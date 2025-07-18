import time
import requests
import logging
from typing import List
from .config import ChatConfig, URL, MOD, HEADERS, INSTANCE_URL, ROUND, USER_ID

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('MisskeyChannelBot')

class ChatHandler:
    '''对话响应类'''
    def __init__(self, conf: ChatConfig):
        self.conf = conf
        self.cooldown_until = 0 # 辅助冷却功能
        self.cooldown = conf.cooldown # 实现冷却功能

    # 辅助函数
    def _manage_memory(self, lst: List) -> List:
        """管理记忆上下文"""
        while len(lst) > self.conf.rd:
            del lst[0]
        return lst

    def _check_api_limit(self) -> bool:
        """检查API调用限制"""
        if time.time() < self.cooldown_until:
            remaining = self.cooldown_until-time.time()
            return True,f"冷却中，剩余时间：{remaining:.0f}秒"
        return False,None

    def _process_response(self, data: dict) -> dict:
        """处理API响应"""
        result = {
            "response": "",
        }
        
        assistant_content = data['choices'][0]['message']['content'].strip()
        result["response"] = assistant_content
        
        return result

    # LLM调用函数
    def _call_api(self, memo: List):
        payload = {
            "model": MOD,
            "messages": [{
                "role": "system",
                "content": self.conf.current_personality
            }] + memo,
            "max_tokens": self.conf.max_token,
        }

        try:
            response = requests.post(
                url=URL,
                json=payload,
                headers=HEADERS,
                timeout=60
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"API请求失败: {e}")
            return None
        
    def _get_conversation_chain(self, note_id, bot_user_id = USER_ID, length = ROUND):
        '''消息链获取函数，用于构建记忆'''
        # 1. 构建 API 请求
        instance_url = INSTANCE_URL.rstrip('/')
        api_url = f"{instance_url}/api/notes/conversation"
        payload = {"noteId": note_id}
        headers = {"Content-Type": "application/json"}
        
        # 2. 发送同步请求
        try:
            response = requests.post(api_url, json=payload, headers=headers)
            response.raise_for_status()  # 检查HTTP错误
            data = response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API请求失败: {e}")
            return []
        
        # 3. 提取并处理消息
        notes = data
        
        # 应用长度限制（取最近的N条）
        if length is not None and length > 0:
            notes = notes[0:length]  # 取最近length条
        
        # 4. 格式化为llm请求格式
        formatted_chain = []
        for note in reversed(notes):
            is_bot = note.get("userId") == bot_user_id
            content = note.get("text", "")
            user_info = note.get('user', {})
            
            # 添加用户ID前缀（非机器人消息）
            if not is_bot:
                user = user_info.get('username') if user_info.get('username') else user_info.get('id')
                content = f"用户[{user}]: {content}"
            
            formatted_chain.append({
                "role": "assistant" if is_bot else "user",
                "content": content
            })
        
        return formatted_chain
        
    def handle_chat(self, name, input, note_id: str) -> str:
        """处理对话请求"""

        # API调用限制检查
        boolean, string = self._check_api_limit()
        if boolean : logger.info(string)

        # 生成整个记忆
        mem: List = self.conf.mess + self._get_conversation_chain(note_id) + [{ "role": "user", "content": f"用户[{name}]: {input}"}]

        # 执行API请求
        reconnect = 3 #请求失败重连次数

        while reconnect:
            response = self._call_api(self._manage_memory(mem))# 记忆管理
            if response :
                break
            else : 
                logger.info("请求失败，尝试重连...")
                reconnect -= 1
                time.sleep(1)
        
        # 处理响应
        result = self._process_response(response)
        
        # 更新API调用时间
        self.cooldown_until = time.time() + self.cooldown
        
        return result["response"]

if __name__ == "__main__":
    chat1 = ChatHandler()
    print(chat1.handle_chat("你是谁？"))