from openai import OpenAI
from message import *
import pypandoc
import base64
import os
import logging
import re

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 常量配置
API_KEY = os.getenv("DASHSCOPE_API_KEY")
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
MATH_PROMPT = ("- 行内公式用 \\(...\\) 包裹，如 \\(\\mathbf{E}\\)。\n"
               "- 块级公式用 \\[...\\] 包裹，独占一行。\n"
               "- 禁止使用 $、$$ 或其他公式语法。\n"
               "- 确保 LaTeX 语法正确。")


def get_openai_client():
    """创建OpenAI客户端"""
    if not API_KEY:
        raise ValueError("DASHSCOPE_API_KEY 环境变量未设置")
    return OpenAI(api_key=API_KEY, base_url=BASE_URL)

def getfilename(answer: str) -> str:
    """生成文件名"""
    if not answer:
        raise ValueError("答案内容为空")
    
    try:
        client = get_openai_client()
        completion = client.chat.completions.create(
            model="qwen3-max",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "请为以下内容生成一个简短的文件名，不要包含任何特殊字符：" + answer},
            ],
            stream=False
        )
        filename = completion.choices[0].message.content.strip()
        # 清除特殊字符
        filename = re.sub(r'[\\/:*?"<>|]', '', filename)
        return filename if filename else "output"
    except Exception as e:
        logger.error(f"生成文件名失败: {e}")
        raise

def request_ai(question: Message) -> str:
    """请求AI处理问题"""
    try:
        client = get_openai_client()
        text = "".join(i for i in context)
        text.join(MATH_PROMPT)
        if question.msg_type == MessageType.IMAGE or question.msg_type == MessageType.TEXT:
            content = []
            if question.msg_type == MessageType.IMAGE:
                imgbase = _img2base64(question.content)
                content.append(
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{imgbase}"
                        }
                    }
                )
            content.append({"type": "text", "text": text})
            
            completion = client.chat.completions.create(
                model="qwen3-vl-plus",
                stream=False,
                extra_body={
                    'enable_thinking': True,
                    "thinking_budget": 21920
                },
                messages=[
                    {
                        "role": "user",
                        "content": content,
                    }
                ]
            )
            return completion.choices[0].message.content
        
        else:
            raise ValueError(f"未知的消息类型: {question.msg_type}")
    
    except Exception as e:
        logger.error(f"AI请求失败: {e}")
        raise

def _img2base64(file_path: str) -> str:
    """将图片转换为base64"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"图片文件不存在: {file_path}")
    
    try:
        with open(file_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    except Exception as e:
        logger.error(f"图片转换失败: {e}")
        raise

def convert_md_to_pdf(md_file: str, pdf_file: str, extra_args: list = None):
    """将Markdown文件转换为PDF"""
    if not os.path.exists(md_file):
        raise FileNotFoundError(f"Markdown文件不存在: {md_file}")
    
    if extra_args is None:
        extra_args = [
            '--pdf-engine=xelatex',
            '--variable', 'CJKmainfont=SimSun',
            "--variable", "mainfont=Times New Roman",
            '--variable', 'fontfamily=times',
            '--variable', 'geometry:margin=1in',
        ]
    
    try:
        pypandoc.convert_file(
            md_file, 'pdf',
            format="markdown+tex_math_dollars+tex_math_single_backslash",
            outputfile=pdf_file,
            extra_args=extra_args
        )
        logger.info(f"PDF已生成: {pdf_file}")
    except Exception as e:
        logger.error(f"PDF转换失败: {e}")
        raise

def _ensure_directories():
    """确保必要目录存在"""
    for directory in ['markdown', 'pdf']:
        os.makedirs(directory, exist_ok=True)

def handle_question(question: Message) -> Message:
    """处理问题的主函数"""
    _ensure_directories()
    
    try:
        answer = request_ai(question)
        if not answer:
            raise ValueError("AI返回空答案")
        
        filename = getfilename(answer)
        # 规范化公式语法
        answer = re.sub(r'\$\s*(.*?)\s*\$', r'$\1$', answer)
        
        md_file = os.path.join('markdown', f'{filename}.md')
        pdf_file = os.path.join('pdf', f'{filename}.pdf')

        context.append(answer)
        limit_context_size(context, max_size=5)

        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(answer)
        
        convert_md_to_pdf(md_file, pdf_file)
        logger.info(f"问题处理完成: {filename}")
        
        return Message(MessageType.FILE, pdf_file)
    
    except Exception as e:
        logger.error(f"处理问题失败: {e}")
        raise

if __name__ == "__main__":
    pass
