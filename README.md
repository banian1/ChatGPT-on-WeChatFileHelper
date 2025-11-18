# ChatGPT on WeChatFileHelper

一个基于 Selenium 和阿里云通义千问的微信网页版自动化 AI 助手，支持文本和图片输入，自动生成 PDF 格式的回复。

## 功能特性

✨ **核心功能**
- 🤖 集成阿里云通义千问 API（qwen3-max/qwen3-vl-plus 模型）
- 📝 支持文本消息处理
- 🖼️ 支持图片识别和分析
- 📄 自动生成 Markdown 和 PDF 格式回复
- 🔄 自动去重，避免重复处理相同消息


## 环境要求

```bash
Python 3.8+
```

## 依赖安装

```bash
pip install selenium openai pypandoc
```

### 额外要求

- **Chrome 浏览器** 和对应版本的 [ChromeDriver](https://chromedriver.chromium.org/)
- **Pandoc**：用于 Markdown 转 PDF
- **xelatex**：用于 PDF 中文支持

## 配置

### 1. 设置环境变量

```bash
# Windows (cmd)
set DASHSCOPE_API_KEY=your_api_key_here

# Windows (PowerShell)
$env:DASHSCOPE_API_KEY="your_api_key_here"

# Linux/macOS
export DASHSCOPE_API_KEY=your_api_key_here
```

获取 API Key：访问 [阿里云通义千问](https://dashscope.aliyuncs.com/)

### 2. 项目结构

```
chatgptonwechat/
├── auto.py              # 主程序：微信消息监听和转发
├── requestai.py         # AI 请求和处理模块
├── message.py           # 消息类定义
├── README.md            # 项目说明
├── markdown/            # Markdown 输出目录（自动创建）
└── pdf/                 # PDF 输出目录（自动创建）
```

## 使用方法

### 快速开始

```bash
python auto.py
```

程序启动后：
1. 浏览器会打开微信网页版 (https://szfilehelper.weixin.qq.com/)
2. **在 20 秒内扫描二维码登录**
3. 页面加载完成后，向文件助手发送消息
4. AI 自动处理并生成 PDF 回复

### 工作流程

```
用户消息 (文本/图片)
    ↓
[auto.py] 检测并获取消息
    ↓
[requestai.py] 调用 AI 处理
    ↓
生成 Markdown 文件
    ↓
转换为 PDF
    ↓
自动发送 PDF 文件到微信
```

### PDF 转换参数

编辑 `requestai.py` 中的 `convert_md_to_pdf()` 函数：

```python
extra_args = [
    '--pdf-engine=xelatex',           # PDF 引擎
    '--variable', 'CJKmainfont=SimSun',  # 中文字体
    '--variable', 'geometry:margin=1in', # 页边距
]
```
## 更新日志

### v1.0 (当前版本)
- ✅ 基础文本和图片处理
- ✅ PDF 自动生成
- ✅ 消息去重
- ✅ 完整日志记录



## 许可证

MIT License

