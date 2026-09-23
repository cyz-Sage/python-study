"""封装 SQLite 操作：建表与保存对话记录。

以后换成 MySQL 或换个表结构，只改这个文件，main.py 一行都不动。
"""
import sqlite3
from datetime import datetime

from config import DB_PATH


def init_db() -> sqlite3.Connection:
    """建立数据库连接并确保 history 表存在，返回连接对象。"""
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
    return conn


def save_record(conn: sqlite3.Connection, question: str, answer: str) -> None:
    """把一轮问答写入 history 表。"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO history (time, question, answer) VALUES (?, ?, ?)",
        (current_time, question, answer)
    )
    conn.commit()