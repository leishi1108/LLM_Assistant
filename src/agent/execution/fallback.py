"""
回退节点模块
"""

from langchain_core.messages import AIMessage
from ..core.state import AgentState


def fallback_node(state: AgentState):
    """回退节点：当不需要特殊代理时使用"""
    state["messages"] =[]
    return {"messages": [AIMessage(content="我是通用助手，请问有什么可以帮助您的？")]}
