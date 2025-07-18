import json
import logging
from websockets.sync.client import connect
from .poster import MisskeyPoster
from .chat import ChatHandler
from .config import INSTANCE_URL, API_TOKEN, USER_ID, CHANNEL_ID

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('MisskeyChannelIDFinder')

class MisskeyNotificationListener:
    '''服务器监听类'''
    def __init__(self, channel_id: None|str, chat: ChatHandler, poster: MisskeyPoster):
        self.instance_url = INSTANCE_URL.rstrip('/')
        self.api_token = API_TOKEN
        self.user_id = USER_ID
        self.channel_id = channel_id
        self.ws_url = f"wss://{self.instance_url.split('//')[1]}/streaming?i={self.api_token}"
        self.running = False
        self.chat = chat
        self.poster = poster
        self.max_reconnect_attempts = 5 # 最大重连次数
        self.reconnect_delay = 5  # 初始重连延迟
        
    def _handle_message(self, message):
        """处理接收到的消息"""
        try:
            data = json.loads(message)
            if data.get('type') == 'channel':
                body = data.get('body', {})

                if not body.get('body') :
                    return
                
                note = body['body']

                if self.channel_id and str(note.get('channel', {}).get('id')) != self.channel_id:
                    return

                # 处理提及消息，其它消息（如reply）同理
                if body.get('type') == 'mention':
                    if note.get('user', {}).get('id') != self.user_id:
                        self.on_mention(note)
                
        except json.JSONDecodeError:
            logger.error("消息解析失败")
        except KeyError as e:
            logger.error(f"消息格式错误: {e}")

    def on_mention(self, note):
        """当有人@你时调用（可重写）"""
        # 尝试获取用户信息
        user_info = note.get('user', {})
        user = user_info.get('username') if user_info.get('username') else user_info.get('id')
        note_id = note.get('id')

        content = note['text']
        logger.info(f"👤 新提及 来自频道{self.channel_id} 用户[{user}]: {content}")

        result = self.poster.send_note(
            text = f"@{user} "+self.chat.handle_chat(user, content, note_id),
            replyId = note_id,
        )

        note_id = result.get('createdNote', {}).get('id')

        if result:
            logger.info(f"成功回复! Note ID: {note_id}")
            logger.info(f"查看链接: {INSTANCE_URL}/notes/{note_id}")
        else:
            logger.error("回复失败，请检查错误信息")


    def start_listening(self):
        """开始监听消息，支持指定频道"""
        self.running = True
        logger.info(f"开始监听通知 (用户ID: {self.user_id})")
        
        with connect(self.ws_url) as websocket:
            # 必须首先订阅主频道才能接收通知
            main_connect_msg = {
                "type": "connect",
                "body": {
                    "channel": "main",
                    "id": "main"
                }
            }
            websocket.send(json.dumps(main_connect_msg))
            
            # 如果提供了频道ID，则额外订阅该频道
            if self.channel_id:
                channel_connect_msg = {
                    "type": "connect",
                    "body": {
                        "channel": "channel",
                        "id": f"channel_{self.channel_id}",
                        "params": {
                            "channelId": self.channel_id
                        }
                    }
                }
                websocket.send(json.dumps(channel_connect_msg))
                logger.info(f"已订阅频道: {self.channel_id}")
            
            # 持续接收消息
            while self.running:
                try:
                    message = websocket.recv(timeout=10)
                    self._handle_message(message)
                except TimeoutError:
                    # 定期发送心跳包
                    ping_msg = {
                        "type": "ping",
                        "body": {"id": "heartbeat"}
                    }
                    websocket.send(json.dumps(ping_msg))
                except Exception as e:
                    logger.exception(f"连接错误: {e}")
                    if self.max_reconnect_attempts :
                        logger.info(f"将在{self.reconnect_delay}秒后尝试重连....")
                        time.sleep(self.reconnect_delay)
                        self.reconnect_dela += 2
                        self.max_reconnect_attempts -= 1
                        self.start_listening()
                    else :
                        logger.info(f"重连次数达到上限")
                        break

if __name__ == "__main__":
    
    chat = ChatHandler()
    poster = MisskeyPoster(instance_url=INSTANCE_URL, api_token=API_TOKEN,)
    
    # 启动监听
    listener = MisskeyNotificationListener(CHANNEL_ID[0], chat, poster) # 当没有指定channel_id时需用None占位
    
    import time
    reconnect_attempts = 5
    max_reconnect_attempts = 10

    try:
        while max_reconnect_attempts > 1:
            try :
                listener.start_listening() # 指定监听频道，默认主频道。
            except Exception as e:
                logger.error(f"连接错误: {e}; 即将重连...")

            max_reconnect_attempts -= 1
            time.sleep(reconnect_attempts)
            reconnect_attempts += 2
        logger.error(f"达到最大重连次数，程序终止。")
    except KeyboardInterrupt:
        listener.stop()
        logger.info("程序已停止")