"""
图构建器模块
"""

from langgraph.graph import StateGraph
from langgraph.constants import END
from typing import Callable, Any
from .state import AgentState


class GraphBuilder:
    """LangGraph状态图构建器"""
    
    def __init__(self):
        self.builder = StateGraph(AgentState)
        self._setup_nodes()
        self._setup_edges()
    
    def _setup_nodes(self):
        """设置图节点"""
        from ..routing.router import router_node
        from ..execution.agent_runner import react_router_node
        from ..execution.fallback import fallback_node
        
        self.builder.add_node("router", router_node)
        self.builder.add_node("react_agent", react_router_node)
        self.builder.add_node("fallback", fallback_node)
    
    def _setup_edges(self):
        """设置图边和条件路由"""
        from ..routing.router import should_use_react_agent
        
        # 添加条件边
        self.builder.add_conditional_edges(
            "router",
            should_use_react_agent,
            {
                True: "react_agent",
                False: "fallback"
            }
        )
        
        self.builder.add_edge("react_agent", END)
        self.builder.add_edge("fallback", END)
        self.builder.set_entry_point("router")
    
    def compile(self):
        """编译图"""
        return self.builder.compile()
