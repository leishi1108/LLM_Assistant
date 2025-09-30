"""
MCP客户端模块
"""

import asyncio

from langchain_core.tools import tool
from langchain_mcp_adapters.client import MultiServerMCPClient
from typing import List, Optional


# 全局MCP客户端实例
_mcp_client: Optional[MultiServerMCPClient] = None
_tools_cache: Optional[List] = None


def get_tool1_mcp_client() -> MultiServerMCPClient:
    """获取MCP客户端实例（单例模式）"""
    global _mcp_client
    
    if _mcp_client is None:
        print("=== MCP 客户端配置 ===")
        print("正在连接到 MCP 服务器...")
        
        try:
            _mcp_client = MultiServerMCPClient({
                "tool_list": {
                    "url": "http://127.0.0.1:8001/sse",
                    "transport": "sse"
                }
            })
            print("MCP 客户端创建成功")
        except Exception as e:
            print(f"MCP 连接失败: {e}")
            import traceback
            traceback.print_exc()
            # 创建空的工具列表作为后备
            _mcp_client = None
            print("MCP 客户端创建失败")
    
    return _mcp_client


def get_tool2_mcp_client() -> MultiServerMCPClient:
    """获取MCP客户端实例（单例模式）"""
    global _mcp_client

    if _mcp_client is None:
        print("=== MCP 客户端配置 ===")
        print("正在连接到 MCP 服务器...")

        try:
            _mcp_client = MultiServerMCPClient({
                "myglodon-asset-management": {
                    "url": "http://192.168.0.239:8000/sse",
                    "transport": "sse"
                }
            })
            print("MCP 客户端创建成功")
        except Exception as e:
            print(f"MCP 连接失败: {e}")
            import traceback
            traceback.print_exc()
            # 创建空的工具列表作为后备
            _mcp_client = None
            print("MCP 客户端创建失败")

    return _mcp_client

@tool
def knowledge_retrieval(content: str) -> dict:
    """调用 Glodon 知识检索 API，根据用户输入内容检索知识库。"""
    import requests

    print("=== ReAPI 知识库工具配置 ===")
    print("正在加载 ReAPI 知识库工具...")
    
    try:
        """调用Glodon知识检索API"""
        url = "https://copilot.glodon.com/api/cvforce/chat/v1/knowledge/retrieval"
        headers = {
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTc3NDk0NDMsInJvIjoidXNlciIsInRlbiI6Inl3cHRicHRqY2Z3YiIsInVpZCI6IjEwMDE1MjEifQ.0CbbbXuo-mS2BIFWyS8g_csvtBCcKixU9cyeDMwtG-M",
            "Content-Type": "application/json",
        }
        payload = {
            "knowledges": ["9d91ce0f-bf09-434e-b29c-cb09f17ca533"],
            "content": content,
            "top_k": 3,
            "score": 0.3,
            "rerank_mode": 0,
            "return_source_data": 0,
            "mode":0
        }
        resp = requests.post(url, headers=headers, json=payload)
        return resp.json()
        
    except Exception as e:
        print(f"ReAPI 知识库工具创建失败: {e}")
        import traceback
        traceback.print_exc()
        return []
def get_tools(tool: str) -> List:
    """获取工具列表（带缓存）"""
    global _tools_cache
    
    # if _tools_cache is None:
    if tool == "tools1":
        client = get_tool1_mcp_client()
        if client is None:
            _tools_cache = []
            return _tools_cache

        try:
            # 测试连接
            print("正在获取工具列表...")
            _tools_cache = asyncio.run(get_tools_with_timeout(client, timeout=5))
            print(f"成功获取 {len(_tools_cache)} 个工具")
        except Exception as e:
            print(f"获取工具失败: {e}")
            import traceback
            traceback.print_exc()
            _tools_cache = []
            print("使用空工具列表作为后备")

    elif tool == "tools2":
        client = get_tool2_mcp_client()
        if client is None:
            _tools_cache = []
            return _tools_cache

        try:
            print("正在获取工具列表...")
            _tools_cache = asyncio.run(get_tools_with_timeout(client, timeout=15))
            print(f"成功获取 {len(_tools_cache)} 个工具")
        except Exception as e:
            print(f"获取工具失败: {e}")
            import traceback
            traceback.print_exc()
            _tools_cache = []
            print("使用空工具列表作为后备")

    elif tool == "tools3":
        # ReAPI知识库工具直接返回，不需要MCP客户端
        _tools_cache = [knowledge_retrieval]
        print(f"成功获取 {len(_tools_cache)} 个ReAPI知识库工具")

    else:
        print(f"未知的工具类型: {tool}")
        _tools_cache = []
        return _tools_cache

    # 调试：检查工具是否正确注册
    if _tools_cache:
        print(f"=== 工具注册调试 ===")
        print(f"获取到的工具数量: {len(_tools_cache)}")
        for i, tool_obj in enumerate(_tools_cache):
            print(f"工具 {i+1}: {tool_obj.name}")
            print(f"  描述: {tool_obj.description}")
            print(f"  参数: {tool_obj.args_schema}")
            print(f"  工具类型: {type(tool_obj)}")
            # 检查工具是否有调用方法
            if hasattr(tool_obj, 'invoke'):
                print(f"  有 invoke 方法: 是")
            if hasattr(tool_obj, 'run'):
                print(f"  有 run 方法: 是")
            if hasattr(tool_obj, 'call'):
                print(f"  有 call 方法: 是")
        print("=== 工具注册调试结束 ===")
    
    return _tools_cache

async def get_tools_with_timeout(client: MultiServerMCPClient, timeout: float = 5.0):
    try:
        # 等待 get_tools 协程，超时会抛出 TimeoutError
        return await asyncio.wait_for(client.get_tools(), timeout=timeout)
    except asyncio.TimeoutError:
        print(f"MultiServerMCPClient.get_tools 超时（{timeout} 秒）")
        # 可以返回空字典或者你希望的默认值
        return {}

def clear_tools_cache():
    """清除工具缓存（用于重新加载工具）"""
    global _tools_cache
    _tools_cache = None
