from .config import ChatConfig, ConfigManager, CHANNEL_ID, BASE_DIR
from .connector import MisskeyNotificationListener
from .poster import MisskeyPoster
from .chat import ChatHandler
from typing import Dict, List
import threading
import logging
import time

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('MisskeyChannelBot')

class GroupManager:
    def __init__(self, ID: str):
        self.id = ID
        self.conf = ChatConfig(ID)
        self.chat = ChatHandler(self.conf)
        self.poster = MisskeyPoster()
        self.connector = MisskeyNotificationListener(ID, self.chat, self.poster)

def run():
    """启动监听器的主函数"""

    bucket: Dict[str, GroupManager] = {} # 存储频道管理器的字典
    
    for cid in CHANNEL_ID:
        bucket[cid] = GroupManager(cid)
    
    threads = []
    
    # 启动频道监听线程
    for cid in CHANNEL_ID:
        def run_channel(id=cid):
            reconnect_attempts = 5
            max_reconnect_attempts = 10
            
            try:
                while max_reconnect_attempts > 0:
                    try:
                        bucket[id].connector.start_listening()
                        break
                    except Exception as e:
                        logger.error(f"连接错误: {e}; 将在{reconnect_attempts}秒后尝试重连...")
                        reconnect_attempts += 2
                        max_reconnect_attempts -= 1
                        if max_reconnect_attempts > 0:
                            time.sleep(reconnect_attempts)
                
                if max_reconnect_attempts == 0:
                    logger.error(f"频道 {id} 达到最大重连次数，停止尝试。")
            except KeyboardInterrupt:
                bucket[id].connector.stop()
                logger.info(f"频道 {id} 已停止")
        
        thread = threading.Thread(target=run_channel, daemon=True)
        thread.start()
        threads.append(thread)
        logger.info(f"频道 {cid} 监听线程已启动")
    
    # 主控制循环
    try:
        logger.info("所有频道监听线程已启动，按 Ctrl+C 终止程序...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("接收到终止信号，正在停止所有连接...")
        for cid in CHANNEL_ID:
            if cid in bucket:
                try:
                    bucket[cid].connector.stop()
                except Exception as e:
                    logger.error(f"停止频道 {cid} 时出错: {e}")
        
        # 等待线程结束
        for thread in threads:
            thread.join(timeout=5)
        
        logger.info("程序已完全停止")

if __name__ == "__main__":

    bucket: Dict[str, GroupManager] = {}

    # 创建并启动每个频道的监听线程
    threads = []
    for id in CHANNEL_ID:
        bucket[id] = GroupManager(id)
        
        # 定义线程函数
        def run_channel(id=id):  # 使用默认参数捕获当前id值
            reconnect_attempts = 5  # 重连等待时间
            max_reconnect_attempts = 10  # 最大重连次数
            
            try:
                while max_reconnect_attempts > 0:
                    try:
                        bucket[id].connector.start_listening()  # 指定监听频道
                        break  # 如果连接成功且没有异常，跳出重连循环
                    except Exception as e:
                        logger.error(f"连接错误: {e}; 将在{reconnect_attempts}秒后尝试重连...")
                        reconnect_attempts += 2
                        max_reconnect_attempts -= 1
                        
                        if max_reconnect_attempts > 0:
                            time.sleep(reconnect_attempts)
                            
                if max_reconnect_attempts == 0:
                    logger.error(f"频道 {id} 达到最大重连次数，停止尝试。")
            except KeyboardInterrupt:
                bucket[id].connector.stop()
                logger.info(f"频道 {id} 已停止")
        
        # 创建并启动线程
        thread = threading.Thread(target=run_channel, daemon=True)
        thread.start()
        threads.append(thread)
        logger.info(f"频道 {id} 监听线程已启动")

    # 主线程等待键盘中断
    try:
        logger.info("所有频道监听线程已启动，按 Ctrl+C 终止程序...")
        while True:
            threading.Event().wait(1)  # 保持主线程运行
    except KeyboardInterrupt:
        logger.info("接收到终止信号，正在停止所有连接...")
        # 停止所有连接器
        for id in CHANNEL_ID:
            if id in bucket:
                try:
                    bucket[id].connector.stop()
                except Exception as e:
                    logger.error(f"停止频道 {id} 时出错: {e}")
        
        # 等待所有线程结束（最多5秒）
        for thread in threads:
            thread.join(timeout=5)
        
        logger.info("程序已完全停止")



