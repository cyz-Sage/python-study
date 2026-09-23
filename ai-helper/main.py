"""程序入口：只负责对话循环和打印，不碰具体实现细节。

业务流程一目了然：加载知识库 → 建库连接 → 循环提问 → 存记录。
HTTP 细节看 llm.py，数据库细节看 db.py，配置看 config.py。
"""
from config import MAX_HISTORY
from db import init_db, save_record
from llm import chat
from prompts import build_messages, build_system_prompt, load_knowledge


def main() -> None:
    knowledge = load_knowledge()
    system_prompt = build_system_prompt(knowledge)

    # 只存 user / assistant 消息，system 单独放在 system_prompt 里
    history: list[dict] = []

    conn = init_db()

    print("开始聊天吧！（输入'退出'结束程序）")

    while True:
        user_input = input("\n你：")
        if user_input == "退出":
            print("再见！")
            break

        messages = build_messages(system_prompt, history, user_input, MAX_HISTORY)
        answer = chat(messages)

        if answer is None:
            continue

        print("\nAI：")
        print(answer)

        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": answer})
        save_record(conn, user_input, answer)

    conn.close()


if __name__ == "__main__":
    main()