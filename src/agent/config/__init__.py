"""
配置模块 - 设置和提示词管理
"""

from .settings import get_llm, get_mcp_config
from .prompts import get_system_prompt

__all__ = ["get_llm", "get_mcp_config", "get_system_prompt"]
