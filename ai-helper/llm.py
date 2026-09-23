"""封装大模型 API 调用：发请求、取答案、分类处理异常。

main.py 只需要拿到一个 messages 列表，调用 chat() 得到回答文本，
完全不关心 HTTP 细节。以后换模型、加流式输出，都只改这里。
"""
import requests

from config import API_URL, API_KEY, MODEL_NAME, TIMEOUT


def chat(messages: list[dict]) -> str | None:
    """把 messages 发给模型，返回回答文本；失败返回 None。

    返回 None 而不是抛异常，是为了让 main.py 的对话循环能继续：
    一次超时不至于让整个程序崩掉。
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }
    data = {
        "model": MODEL_NAME,
        "messages": messages,
    }

    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=TIMEOUT)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        print("请求失败，状态码：", response.status_code)
        print(response.text)
        return None

    except requests.exceptions.Timeout:
        print("\n[错误] 请求超时，网络太慢了。")
    except requests.exceptions.ConnectionError:
        print("\n[错误] 网络连接失败，请检查网络。")
    except Exception as e:
        print(f"\n[错误] 发生异常：{e}")

    return None