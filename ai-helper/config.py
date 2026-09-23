"""集中管理路径、密钥与常量，其余模块从这里 import。

拆出这个文件的意义：以后要改模型名、超时时间、历史条数，
只动这一处，不用在其它代码里翻箱倒柜。
"""
import os
from pathlib import Path

from dotenv import load_dotenv

# ==================== 路径锚定 ====================
# __file__ 是"当前这个脚本文件自己"的路径
# .parent  就是它所在的文件夹，也就是 ...\ai-helper
BASE_DIR = Path(__file__).parent
ROOT_DIR = BASE_DIR.parent                      # 项目根目录 ...\study

NOTES_PATH = BASE_DIR / "notes.txt"             # 知识库文件
DB_PATH = BASE_DIR / "chat_history.db"          # 数据库文件

# 从项目根目录读取 .env（API Key 存在这里）
load_dotenv(ROOT_DIR / ".env")
API_KEY = os.getenv("DEEPSEEK_API_KEY")

# ==================== API 相关常量 ====================
API_URL = "https://api.deepseek.com/chat/completions"
MODEL_NAME = "deepseek-chat"
TIMEOUT = 30                                     # 请求超时（秒）

# ==================== 对话相关常量 ====================
# 每次请求最多带多少条历史给模型（一问一答 = 2 条，所以 20 条 = 10 轮）
MAX_HISTORY = 20