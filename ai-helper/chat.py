import os
import sqlite3
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv

# ==================== 0. 路径锚定 ====================
# __file__ 是"当前这个脚本文件自己"的路径
# .parent  就是它所在的文件夹，也就是 ...\ai-helper
BASE_DIR = Path(__file__).parent
ROOT_DIR = BASE_DIR.parent                      # 项目根目录 ...\study

NOTES_PATH = BASE_DIR / "notes.txt"             # 知识库文件
DB_PATH = BASE_DIR / "chat_history.db"          # 数据库文件

# 从项目根目录读取 .env（API Key 存在这里）
load_dotenv(ROOT_DIR / ".env")
API_KEY = os.getenv("DEEPSEEK_API_KEY")

# 每次请求最多带多少条历史给模型（一问一答 = 2 条，所以 20 条 = 10 轮）
MAX_HISTORY = 20

# ==================== 1. 连接/创建数据库 ====================
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        time TEXT,
        question TEXT,
        answer TEXT
    )
''')
conn.commit()

# ==================== 2. 启动时读一次知识库 ====================
if NOTES_PATH.exists():
    knowledge = NOTES_PATH.read_text(encoding="utf-8")
    print(f"[信息] 已加载知识库：{NOTES_PATH}（{len(knowledge)} 个字）")
else:
    print(f"[警告] 没找到知识库文件：{NOTES_PATH}")
    print("        本次回答没有背景知识，AI 可能会编造内容！")
    knowledge = ""

# ==================== 3. 初始化对话历史 ====================
messages = [
    {"role": "system", "content": "你是一个有用的AI助手。"}
]

url = "https://api.deepseek.com/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

print("开始聊天吧！（输入'退出'结束程序）")

# ==================== 4. 无限循环 ====================
while True:
    user_input = input("\n你：")
    if user_input == "退出":
        print("再见！")
        break

    # 只带最近 MAX_HISTORY 条历史给模型，避免越聊越贵、最后超出模型上限
    # messages[0] 是最初的 system，这里已经不用了，所以跳过
    recent_history = messages[1:][-MAX_HISTORY:]

    current_messages = [
        {"role": "system", "content": f"你是一个知识助手。请严格根据以下背景信息回答问题：\n{knowledge}"}
    ] + recent_history + [{"role": "user", "content": user_input}]

    data = {
        "model": "deepseek-chat",
        "messages": current_messages
    }

    # 异常处理
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            answer = response.json()["choices"][0]["message"]["content"]
            print("\nAI：")
            print(answer)

            # 记录对话历史到内存和数据库
            messages.append({"role": "user", "content": user_input})
            messages.append({"role": "assistant", "content": answer})

            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                "INSERT INTO history (time, question, answer) VALUES (?, ?, ?)",
                (current_time, user_input, answer)
            )
            conn.commit()
        else:
            print("请求失败，状态码：", response.status_code)
            print(response.text)

    except requests.exceptions.Timeout:
        print("\n[错误] 请求超时，网络太慢了。")
    except requests.exceptions.ConnectionError:
        print("\n[错误] 网络连接失败，请检查网络。")
    except Exception as e:
        print(f"\n[错误] 发生异常：{e}")

conn.close()