"""
设置模块 - 配置管理
"""

from agent.llm import CustomLLM
from typing import Dict, Any


def get_llm(temperature, max_tokens) -> CustomLLM:
    """获取LLM实例"""
    return CustomLLM(
        api_url="https://copilot.glodon.com/api/cvforce/aishop/v1/chat/completions",
        # api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTc2NDQ0ODQsInJvIjoidXNlciIsInRlbiI6Inl3cHRicHRqY2Z3YiIsInVpZCI6IjEwMDE1MjEifQ.r8y3Uw9Mdmz8mPRSUed3yxly30V0YjU9UbjdD9Ye86c",
        api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTc4NDI3NTcsInJvIjoidXNlciIsInRlbiI6Inl3cHRicHRqY2Z3YiIsInVpZCI6IjEwMDE1MjEifQ.zx_ofGhbiS-2zYCCBg0y0MkSoLPsHOTijCpaeWMR-iQ",
        model_name="A26lwykwnz2pq",
        temperature=temperature,  # 确定性输出
        max_tokens=max_tokens  # 减少token消耗
    )


def get_mcp_config() -> Dict[str, Any]:
    """获取MCP配置"""
    return {
        "tool_list": {
            "url": "http://127.0.0.1:8000/mcp",
            "transport": "streamable_http"
        }
    }

