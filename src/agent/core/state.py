"""
状态管理模块
"""

from langgraph.graph import MessagesState
from typing import Optional


class AgentState(MessagesState):
    """代理状态类，继承自MessagesState以支持消息的追加合并"""
    current_agent: str = "fallback"
    reset_flag: Optional[bool] = None
    user_token: Optional[str] = None
    client_token: Optional[str] = None
