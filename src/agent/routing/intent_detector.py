"""
意图识别模块
"""

import re
from typing import List, Optional
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from agent.config.settings import get_llm


def detect_agent(user_msg, history: Optional[List[BaseMessage]] = None) -> str:
    """
    专门针对参数收集场景的意图识别
    返回：'seek_application_or_menu_agent' | 'other_agent' | 'reset'
    """
    # 安全地处理user_msg，确保它是字符串
    if isinstance(user_msg, str):
        user_content_lower = user_msg.lower().strip()
    elif isinstance(user_msg, (list, dict)):
        user_content_lower = str(user_msg).lower().strip()
    else:
        user_content_lower = str(user_msg).lower().strip()

    # 重置意图：最明确的判断
    reset_keywords = ['reset', '重置', '清空', '重新开始', '重新来过', '清空对话', '重新对话']
    if any(keyword in user_content_lower for keyword in reset_keywords):
        return 'reset'

    # ------- 基于 LLM 的意图识别（在不改变上述逻辑的前提下追加） -------
    try:
        llm = get_llm(0.1, 10)
        # 组装对话上下文：强调“最后输入”的权重更高（说明+放在末尾）
        history_text = ""
        if history:
            # 仅选取最近的若干条，避免过长（例如取最近6条）
            recent_messages: List[BaseMessage] = history[-6:]
            formatted_pairs: List[str] = []
            for m in recent_messages:
                role = getattr(m, "type", "user")
                content = getattr(m, "content", "")
                formatted_pairs.append(f"{role}: {content}")
            history_text = "\n".join(formatted_pairs)

        system_prompt = (
            "你是意图识别器。只输出以下标签之一：\n"
            "- asset_center_agent\n"
            "- knowledge_retrieval\n\n"
            "判定规则：\n"
            "1) knowledge_retrieval主问答类， asset_center_agent主资产中心操作类。\n"
            "2) 严格避免输出除上述标签外的任何文字。\n"
            "3) 结合历史对话与用户最后输入进行判断，但最后输入权重更高。\n"
            "4) 当用户明显在找'/账号/用户/组织/岗位/成员/用户中心'等相关问答时，输出 knowledge_retrieval\n"
            "5) 当用户明显在找'资产/分配/产品'等相关操作需求时，输出 asset_center_agent\n"
        )

        user_prompt = (
            (f"历史对话（可参考）：\n{history_text}\n\n" if history_text else "") +
            f"用户最后输入（请优先考虑）：\n{user_content_lower}"
        )

        ai_msg = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)])
        ai_text = (ai_msg.content or "").strip().lower()

        allowed = {"asset_center_agent", "knowledge_retrieval", "reset"}
        if ai_text in allowed:
            # 保持与上述重置判断一致性：若模型给出 reset，这里也遵循
            return ai_text if ai_text != "reset" else "reset"
        return "asset_center_agent"
    except Exception:
        # LLM 异常时兜底：简单关键词判定
        if any(k in user_content_lower for k in ["资产", "应用", "分配", "产品"]):
            return "asset_center_agent"
        return "asset_center_agent"

