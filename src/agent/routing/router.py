"""
路由节点模块
"""

from ..core.state import AgentState
from ..core.message_handler import ensure_message_format
from .intent_detector import detect_agent


def router_node(state: AgentState):
    """路由节点：根据用户输入决定使用哪个代理"""
    # 读取但不修改原 state
    messages = ensure_message_format(state.get("messages", []))
    current_agent = state.get("current_agent", "")

    # 没有消息则不路由，直接返回（不改动）
    if not messages:
        return {}

    # 解析最后一条用户输入
    last_message = messages[-1]
    if hasattr(last_message, "content"):
        content = last_message.content
        user_msg = content if isinstance(content, str) else str(content)
    else:
        user_msg = str(last_message)

    # 意图识别
    new_agent = state.get("current_agent") or detect_agent(user_msg, messages)
    
    # 如需 reset，设置重置标记
    if new_agent == "reset":
        return {"current_agent": "reset", "reset_flag": True}

    # 首次或切换，仅更新 current_agent
    if new_agent != current_agent:
        return {"current_agent": new_agent}

    # 无变化
    return {}


def should_use_react_agent(state: AgentState) -> bool:
    """判断是否应该使用ReAct代理"""
    # 检查是否需要重置
    if state.get("reset_flag"):
        # 清理state，只保留最后一条用户消息
        messages = state.get("messages", [])
        if messages:
            # 保留最后一条消息作为新的开始
            last_message = messages[-1]
            # 清理所有状态，只保留最后一条消息
            state.clear()
            state["messages"] = [last_message]
            state["current_agent"] = "reset_flag"
            # 移除重置标记
            if "reset_flag" in state:
                del state["reset_flag"]
        return True
    
    if state.get("current_agent") == "reset":
        return False
    return state.get("current_agent") in ["seek_application_or_menu_agent","asset_center_agent",'knowledge_retrieval']
