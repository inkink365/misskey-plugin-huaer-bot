import toml
from pathlib import Path
from typing import Dict, Any
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('MisskeyChannelBot')

class ConfigManager:
    '''配置管理类'''

    @staticmethod
    def load_toml(file_path: Path) -> Dict[str, Any]:
        try:
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    return toml.load(f)
            logger.error(f"TOML 不存在: {file_path}")
            return {}
        except Exception as e:
            logger.error(f"加载 {file_path} 失败: {e}")
            return {}
    
    @staticmethod
    def save_toml(data: Dict[str, Any], file_path: Path):
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                toml.dump(data, f)
        except Exception as e:
            logger.error(f"保存 {file_path} 失败: {e}")

BASE_DIR = Path(__file__).resolve().parent

# 版本信息
MAJOR_VERSION = 1
MINOR_VERSION = 0
PATCH_VERSION = 3
VERSION_SUFFIX = "stable"

# 导入配置文件
cfg = ConfigManager.load_toml(BASE_DIR / "config.toml")

# 解析API配置
MOD = cfg["api"].get("mod", [])
URL = cfg["api"].get("url", "")

HEADERS = cfg["api"].get("headers", {})

COOL = cfg["misskey"].get("cooldown", 0.0)
USER_ID = cfg["misskey"].get("user_id", "")
CHANNEL_ID = cfg["misskey"].get("channel_id", [])
INSTANCE_URL = cfg["misskey"].get("instance_url", "")
API_TOKEN = cfg["misskey"].get("api_token", "")

PERSONALITY = cfg["channels"].get("default_personality", "")
TOKEN = cfg["channels"].get("max_token", 1024)
ROUND = cfg["channels"].get("rd", 6)
MEM = cfg["channels"].get("memory", [])

class ChatConfig:
    '''变量容器类，配置的动态载体'''
    def __init__(self, ID: int):

        self.id = ID # ID : 此配置归属的组的ID

        self.rd : int = cfg[f"{self.id}"].get("rd", ROUND)
        self.mess : list = cfg[f"{self.id}"].get("memory", MEM) 
        self.cooldown : float = cfg[f"{self.id}"].get("cooldown", COOL)
        self.max_token : int = cfg[f"{self.id}"].get("max_token", TOKEN)
        self.current_personality : str= cfg[f"{self.id}"].get("default_personality", PERSONALITY) 
