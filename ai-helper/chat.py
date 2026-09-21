import requests
import sqlite3
from datetime import datetime
import os
from dotenv import load_dotenv

# 加载 .env 文件里的环境变量
load_dotenv()

# 从环境变量里读取 Key
API_KEY = os.getenv("DEEPSEEK_API_KEY") 

# 1. 连接/创建数据库
conn = sqlite3.connect("chat_history.db")
cursor = conn.cursor()

# 2. 创建表（如果不存在）
cursor.execute('''
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        time TEXT,
        question TEXT,
        answer TEXT
    )
''')
conn.commit()

# 3. 初始化对话历史
messages = [
    {"role": "system", "content": "你是一个有用的AI助手，回答请尽量简洁。"}
]

url = "https://api.deepseek.com/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

print("开始聊天吧！（输入'退出'结束程序）")

# 4. 开启无限循环，实现多轮对话
while True:
    # 获取用户输入
    user_input = input("\n你：")
    
    # 判断是否退出
    if user_input == "退出":
        print("再见！")
        break

    # 5. 把用户的新问题追加到历史列表里
    messages.append({"role": "user", "content": user_input})

    # 6. 准备发送的数据
    data = {
        "model": "deepseek-chat",
        "messages": messages
    }

    # 7. 发送请求（用 try...except 包裹，防止崩溃）
    try:
        # 加上 timeout=30，防止网络卡死一直等
        response = requests.post(url, headers=headers, json=data, timeout=30)

        # 8. 提取回答，保存到数据库并打印
        if response.status_code == 200:
            answer = response.json()["choices"][0]["message"]["content"]
            print("\nAI：")
            print(answer)
            
            # 9. 把 AI 的回答也追加到历史列表里
            messages.append({"role": "assistant", "content": answer})
            
            # 记录当前时间
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 存入数据库
            cursor.execute(
                "INSERT INTO history (time, question, answer) VALUES (?, ?, ?)",
                (current_time, user_input, answer)
            )
            conn.commit()
        else:
            print("请求失败，状态码：", response.status_code)
            print(response.text)
            # 请求失败，把刚才的问题从历史里删掉
            messages.pop()

    # 捕获网络超时错误
    except requests.exceptions.Timeout:
        print("\n[错误] 请求超时，网络太慢了。")
        messages.pop()
    # 捕获网络连接错误（比如断网）
    except requests.exceptions.ConnectionError:
        print("\n[错误] 网络连接失败，请检查网络。")
        messages.pop()
    # 兜底捕获其他所有异常
    except Exception as e:
        print(f"\n[错误] 发生异常：{e}")
        messages.pop()

# 10. 关闭数据库连接
conn.close()