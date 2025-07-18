import time
import requests
import json
import logging
from .config import INSTANCE_URL, API_TOKEN, CHANNEL_ID

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('MisskeyChannelIDFinder')

class MisskeyPoster:
    '''信息发送类'''
    def __init__(self):
        self.api_token = API_TOKEN
        self.instance_url = INSTANCE_URL.rstrip('/')
        self.api_endpoint = f"{self.instance_url}/api/notes/create"
        self.upload_url = f"{self.instance_url}/api/drive/files/create"

    def send_note(self, text, visibility="public", cw=None, **kwargs):
        """
        发送帖子到 Misskey，带断线重连机制
        :param text: 帖子内容 (支持 Markdown)
        :param visibility: 可见性 (public/home/followers/specified)
        :param cw: 内容警告 (可选)
        :param kwargs: 其他可选参数 (file_ids, poll, etc.)
        :return: API 响应或 None（失败时）
        """
        headers = {'Content-Type': 'application/json'}
        payload = {
            "i": self.api_token,
            "text": text,
            "visibility": visibility,
            **kwargs
        }

        attempt = 0
        retry_delay = 1
        max_retries = 5
        
        # 添加可选的内容警告
        if cw:
            payload["cw"] = cw
        
        # 连接和重试机制
        while attempt < max_retries:
            try:
                response = requests.post(
                    self.api_endpoint,
                    data=json.dumps(payload),
                    headers=headers,
                    timeout=30
                )
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.ConnectionError as e:
                # 连接错误（10054等）
                logger.warning(f"连接错误 (尝试 {attempt+1}): {e}")
                time.sleep(retry_delay)
                attempt += 1
                retry_delay += 2
                
            except requests.exceptions.Timeout:
                logger.warning(f"请求超时 (尝试 {attempt+1})")
                time.sleep(retry_delay)
                attempt += 1
                retry_delay += 2
                
            except requests.exceptions.RequestException as e:
                # 其他请求错误
                logger.error(f"API请求失败: {e}")
                if hasattr(e, 'response') and e.response is not None:
                    logger.error(f"API错误详情: {e.response.text}")
                return None
        
        logger.error(f"发送失败: 重试{max_retries}次后仍失败")
        return None
        
    def upload_file(self, file_path):
        """
        上传文件到 Misskey Drive
        :param file_path: 本地文件路径
        :return: 文件ID (成功) 或 None (失败)
        """
        
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                data = {'i': self.api_token}
                response = requests.post(
                    self.upload_url,
                    data=data,
                    files=files,
                    timeout=30
                )
            response.raise_for_status()
            file_data = response.json()
            return file_data.get('id')
        except Exception as e:
            logger.error(f"文件上传失败: {e}")
            return None

if __name__ == "__main__":
    # 初始化客户端
    channel_poster = MisskeyPoster()

    result = None

    # 示例请不要一起运行！

    '''# 示例一，发送普通帖子 (可添加内容警告 cw="敏感内容提示")
    result = channel_poster.send_note(
        text="hello_world!",
        visibility="public"  # 改为 followers 可限制可见性
    )'''

    '''import os

    # 获取当前脚本所在的目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 示例二，发送带有文件的帖子(需先上传文件，仅支持部分格式文件)
    png_path = os.path.join(script_dir, "misc\mikumikubeam.jpg")
    print(png_path)
    # 上传文件
    file_id = channel_poster.upload_file(png_path)
    result = channel_poster.send_note(
        text="and now, it's the time ... for the moment you've been wait for!",
        fileIds=[file_id]
    )'''

    '''from datetime import datetime, timedelta, timezone

    # 示例三，发送投票
    expires = datetime.now(timezone.utc) + timedelta(hours=24) # 持续24小时
    expires_at = int(expires_at.timestamp() * 1000)

    poll = {
        "choices": ["A.可爱", "B.选A", "C.选B"],
        "multiple": False,  # 是否允许多选
        "expiresAt": expires_at # 过期时间，格式: YYYY-MM-DDTHH:MM:SSZ
    }
    result = channel_poster.send_note(
        text = "评价一下华尔酱",
        poll = poll
    )'''

    '''# 示例四 markdown测试
    md_path = os.path.join(script_dir, "misc\example.md")

    with open(md_path,"r",encoding="utf-8") as f:
        result = channel_poster.send_note(
            text=f.read(),
        )'''
    
    
    '''# 示例五 发送帖子到频道
    result = channel_poster.send_note(
        text="频道消息测试",
        channelId=CHANNEL_ID[0],
        # cw="敏感内容提示"  # 可选的警告标签
    )'''
    
    if result:
        note_id = result.get('createdNote', {}).get('id')
        logger.info(f"成功发送! Note ID: {note_id}")
        logger.info(f"查看链接: {INSTANCE_URL}/notes/{note_id}")
    else:
        logger.error("发送失败，请检查错误信息")
