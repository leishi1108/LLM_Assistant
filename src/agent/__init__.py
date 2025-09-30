"""
LLM-Assistant: 基于 LangGraph 的智能对话助手
"""

from .core import AgentState, GraphBuilder, ensure_message_format
from .routing import detect_agent, router_node, should_use_react_agent
from .execution import create_seek_application_agent, react_router_node, fallback_node
from .tools import get_tools, get_tool1_mcp_client, get_tool2_mcp_client
from .config import get_llm, get_mcp_config, get_system_prompt

__version__ = "1.0.0"
__author__ = "LLM-Assistant Team"

__all__ = [
    "AgentState",
    "GraphBuilder", 
    "ensure_message_format",
    "detect_agent",
    "router_node",
    "should_use_react_agent",
    "create_seek_application_agent",
    "react_router_node",
    "fallback_node",
    "get_tools",
    "get_tool1_mcp_client",
    "get_tool2_mcp_client",
    "get_llm",
    "get_mcp_config",
    "get_system_prompt"
]
