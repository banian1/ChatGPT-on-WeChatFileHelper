from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
from message import *
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import requestai
import os
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 设置浏览器选项
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)  # 全局等待对象

LAST_MESSAGE_HASH = None  # 用于检测消息变化

def send(message):
    """发送消息"""
    try:
        sendbox = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, 'chat-panel__input-container'))
        )
        if message.msg_type == MessageType.TEXT:
            sendbox.send_keys(message.content)
            sendbox.send_keys(Keys.ENTER)
            logger.info(f"发送文本消息: {message.content[:50]}")
        
        elif message.msg_type == MessageType.FILE:
            attach_btn = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, 'file-input'))
            )
            pdf_path = os.path.abspath(message.content)
            attach_btn.send_keys(pdf_path)
            logger.info(f"发送文件: {pdf_path}")
    except TimeoutException:
        logger.error("等待发送框超时")
        raise

def get_last_message():
    """获取最后一条消息"""
    try:
        # 等待消息元素出现
        messages = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.msg-item.mine[item]"))
        )
        
        if not messages:
            return Message(MessageType.TEXT, "")
        
        last_msg = messages[-1]
        
        # 尝试获取文本消息
        try:
            msg_text = last_msg.find_element(By.CLASS_NAME, 'msg-text').text
            return Message(MessageType.TEXT, msg_text)
        except NoSuchElementException:
            pass
        
        # 尝试获取图片消息
        try:
            last_msg.find_element(By.CLASS_NAME, 'msg-image')
            download_link = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.icon.icon__download"))
            )
            download_link.click()
            
            # 等待图片下载
            time.sleep(2)
            downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
            jpg_files = [
                os.path.join(downloads_folder, f) 
                for f in os.listdir(downloads_folder) 
                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))
            ]
            
            if jpg_files:
                jpg_files.sort(key=lambda f: os.path.getmtime(f), reverse=True)
                return Message(MessageType.IMAGE, jpg_files[0])
        except NoSuchElementException:
            pass
        
        return Message(MessageType.FILE, "")
    
    except TimeoutException:
        logger.debug("等待消息超时，继续检查")
        return Message(MessageType.TEXT, "")

def has_new_message(current_msg: Message) -> bool:
    """判断是否有新消息（避免重复处理）"""
    global LAST_MESSAGE_HASH
    
    current_hash = hash((current_msg.msg_type, current_msg.content))
    
    if current_hash == LAST_MESSAGE_HASH:
        return False
    
    LAST_MESSAGE_HASH = current_hash
    return True

def wait_for_page_ready(timeout=20):
    """等待页面完全加载"""
    try:
        wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, 'chat-panel__input-container'))
        )
        logger.info("页面加载完成")
    except TimeoutException:
        logger.error("页面加载超时")
        raise

def main():
    try:
        # 打开微信网页版
        driver.get("https://szfilehelper.weixin.qq.com/")
        logger.info("请在20秒内扫描二维码登录微信网页版...")
        
        # 等待用户扫描二维码
        time.sleep(20)
        
        # 等待页面就绪
        wait_for_page_ready()
        
        # 主循环：监听消息
        while True:
            try:
                question_new = get_last_message()
                
                # 检查是否为新消息且不是bot回复
                if (question_new.msg_type in [MessageType.TEXT, MessageType.IMAGE] and
                    question_new.content and
                    has_new_message(question_new) and
                    'bot' not in question_new.content):
                    
                    logger.info(f"收到新消息: {question_new.msg_type}")
                    pdf_reply = requestai.handle_question(question_new)
                    send(pdf_reply)
                
                # 用事件监听代替 sleep
                # 等待新消息出现（检测DOM变化）
                try:
                    WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div.msg-item.mine[item]"))
                    )
                except TimeoutException:
                    # 5秒内无新消息，继续轮询
                    pass
                
            except Exception as e:
                logger.error(f"处理消息出错: {e}")
                time.sleep(2)

    except Exception as e:
        logger.error(f"发生错误: {e}")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    main()