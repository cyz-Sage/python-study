"""负责知识库加载与提示词（messages）的构造。

把"怎么拼提示词"从业务流程里抽出来，以后要把宠物笔记换成
病历、法律条文、客服话术，改的是这里的模板，不是 main.py。
"""
from config import NOTES_PATH

# 占位符 {knowledge} 在 build_system_prompt 里被替换成知识库内容
SYSTEM_PROMPT_TEMPLATE = (
    "你是一个知识助手。请严格根据以下背景信息回答问题：\n{knowledge}"
)


def load_knowledge() -> str:
    """启动时读一次知识库；找不到就大声警告，而不是静默降级。"""
    if NOTES_PATH.exists():
        knowledge = NOTES_PATH.read_text(encoding="utf-8")
        print(f"[信息] 已加载知识库：{NOTES_PATH}（{len(knowledge)} 个字）")
        return knowledge

    print(f"[警告] 没找到知识库文件：{NOTES_PATH}")
    print("        本次回答没有背景知识，AI 可能会编造内容！")
    return ""


def build_system_prompt(knowledge: str) -> str:
    """把知识库内容填进系统提示词模板。"""
    return SYSTEM_PROMPT_TEMPLATE.format(knowledge=knowledge)


def build_messages(
    system_prompt: str,
    history: list[dict],
    user_input: str,
    max_history: int,
) -> list[dict]:
    """组装一次请求要发的完整 messages。

    history 只存 user 和 assistant 消息（不含 system），
    这里按 max_history 做滑动窗口截断，避免越聊越长。
    """
    recent = history[-max_history:]
    return (
        [{"role": "system", "content": system_prompt}]
        + recent
        + [{"role": "user", "content": user_input}]
    )