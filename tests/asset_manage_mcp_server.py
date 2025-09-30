#!/usr/bin/env python3
"""
MyGlodon Asset Management MCP Server

This MCP server provides access to MyGlodon asset management functionality
through the OpenAssetManageController API endpoints.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
import aiohttp
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel,
    Text,
    Image,
    EmbeddedResourceReference,
    Resource,
    ToolResult,
    Error,
    ErrorCode,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MyGlodonMCPServer:
    def __init__(self):
        self.server = Server("myglodon-asset-management")
        self.base_url = "https://me-test.glodon.com"  # Default MyGlodon API base URL
        self.user_token = None
        self.client_token = None
        
        # Register tools
        self.server.list_tools(self.list_tools)
        self.server.call_tool(self.call_tool)
        
    async def list_tools(self, request: ListToolsRequest) -> ListToolsResult:
        """List available tools for MyGlodon asset management."""
        tools = [
            Tool(
                name="query_assets_by_status",
                description="查询资产状态 - 根据状态查询企业资产信息，支持分页",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "pageNum": {
                            "type": "integer",
                            "description": "页码，默认为1",
                            "default": 1
                        },
                        "pageSize": {
                            "type": "integer", 
                            "description": "每页大小，默认为20",
                            "default": 20
                        },
                        "searchType": {
                            "type": "string",
                            "description": "搜索类型",
                            "enum": ["productUri", "productName", "assetNum", "memberAccount"]
                        },
                        "searchCondition": {
                            "type": "string",
                            "description": "搜索条件"
                        },
                        "assetStatus": {
                            "type": "string",
                            "description": "资产状态",
                            "enum": ["VALID", "EXPIRED", "UNASSIGNED", "ASSIGNED", "BORROWED", "ONLINED", "LOCKED"]
                        }
                    },
                    "required": ["searchType", "searchCondition", "assetStatus"]
                }
            ),

            Tool(
                name="allocate_asset_privileges",
                description="分配/取消分配资产权限 - 为指定资产分配或取消分配权限给成员，返回操作状态。状态包括：NONE(无权限)、SUCCESS(分配成功)、FAILED(分配失败)、OCCUPIED(已分配给其他用户)、NOT_REQUIRED(无需分配)、BORROWED(已被借出)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "assignType": {
                            "type": "string",
                            "description": "分配类型",
                            "enum": ["assign", "unassign"]
                        },
                        "assetPrivileges": {
                            "type": "array",
                            "description": "资产权限列表",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "assetNum": {
                                        "type": "string",
                                        "description": "资产编号"
                                    },
                                    "assetId": {
                                        "type": "string",
                                        "description": "资产ID"
                                    },
                                    "memberId": {
                                        "type": "string",
                                        "description": "成员ID"
                                    }
                                },
                                "required": ["assetNum", "assetId", "memberId"]
                            }
                        }
                    },
                    "required": ["assignType", "assetPrivileges"]
                }
            ),
            Tool(
                name="query_online_products",
                description="查询在线产品 - 查询指定资产的在线云锁产品信息",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "assetId": {
                            "type": "string",
                            "description": "资产ID"
                        }
                    },
                    "required": ["assetId"]
                }
            ),
            Tool(
                name="query_enterprise_members",
                description="查询企业成员 - 获取企业下的成员列表",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            Tool(
                name="query_asset_privilege_status",
                description="查询资产权限状态 - 获取资产的权限分配状态信息",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "assetId": {
                            "type": "string",
                            "description": "资产ID"
                        }
                    },
                    "required": ["assetId"]
                }
            ),
            Tool(
                name="set_user_token",
                description="设置用户令牌 - 设置用于API认证的用户令牌",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "userToken": {
                            "type": "string",
                            "description": "用户认证令牌"
                        }
                    },
                    "required": ["userToken"]
                }
            ),
            Tool(
                name="set_client_token",
                description="设置客户端令牌 - 设置用于API认证的客户端令牌",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "clientToken": {
                            "type": "string",
                            "description": "客户端认证令牌"
                        }
                    },
                    "required": ["clientToken"]
                }
            ),
            Tool(
                name="set_base_url",
                description="设置API基础URL - 设置MyGlodon API的基础URL",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "baseUrl": {
                            "type": "string",
                            "description": "API基础URL，例如: http://localhost:8080"
                        }
                    },
                    "required": ["baseUrl"]
                }
            )
        ]
        return ListToolsResult(tools=tools)
    
    async def call_tool(self, request: CallToolRequest) -> CallToolResult:
        """Execute the requested tool."""
        try:
            if request.name == "query_assets_by_status":
                return await self._query_assets_by_status(request.arguments)
            elif request.name == "allocate_asset_privileges":
                return await self._allocate_asset_privileges(request.arguments)
            elif request.name == "query_online_products":
                return await self._query_online_products(request.arguments)
            elif request.name == "query_enterprise_members":
                return await self._query_enterprise_members(request.arguments)
            elif request.name == "query_asset_privilege_status":
                return await self._query_asset_privilege_status(request.arguments)
            elif request.name == "set_user_token":
                return await self._set_user_token(request.arguments)
            elif request.name == "set_client_token":
                return await self._set_client_token(request.arguments)
            elif request.name == "set_base_url":
                return await self._set_base_url(request.arguments)
            else:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Unknown tool: {request.name}")]
                )
        except Exception as e:
            logger.error(f"Error executing tool {request.name}: {str(e)}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error: {str(e)}")]
            )
    
    async def _query_assets_by_status(self, arguments: Dict[str, Any]) -> CallToolResult:
        """查询资产状态"""
        if not self.user_token:
            return CallToolResult(
                content=[TextContent(type="text", text="Error: User token not set. Please set user token first.")]
            )
        
        url = f"{self.base_url}/v1/assets/manage/asset/status"
        params = {
            "pageNum": arguments.get("pageNum", 1),
            "pageSize": arguments.get("pageSize", 20)
        }
        
        data = {
            "searchType": arguments["searchType"],
            "searchCondition": arguments["searchCondition"],
            "assetStatus": arguments["assetStatus"]
        }
        
        headers = {"userToken": self.user_token, "clientToken": self.client_token, "Content-Type": "application/json"}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, params=params, json=data, headers=headers) as response:
                result = await response.json()
                return CallToolResult(
                    content=[TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
                )
    
    async def _allocate_asset_privileges(self, arguments: Dict[str, Any]) -> CallToolResult:
        """分配资产权限"""
        if not self.user_token:
            return CallToolResult(
                content=[TextContent(type="text", text="Error: User token not set. Please set user token first.")]
            )
        
        assign_type = arguments["assignType"]
        asset_privileges = arguments["assetPrivileges"]
        
        url = f"{self.base_url}/v1/assets/manage/asset/{assign_type}/privileges"
        headers = {"userToken": self.user_token, "clientToken": self.client_token, "Content-Type": "application/json"}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=asset_privileges, headers=headers) as response:
                result = await response.json()
                return CallToolResult(
                    content=[TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
                )
    
    async def _query_online_products(self, arguments: Dict[str, Any]) -> CallToolResult:
        """查询在线产品"""
        if not self.user_token:
            return CallToolResult(
                content=[TextContent(type="text", text="Error: User token not set. Please set user token first.")]
            )
        
        asset_id = arguments["assetId"]
        url = f"{self.base_url}/v1/assets/manage/{asset_id}/products/online"
        headers = {"userToken": self.user_token, "clientToken": self.client_token}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                result = await response.json()
                return CallToolResult(
                    content=[TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
                )
    
    async def _query_enterprise_members(self, arguments: Dict[str, Any]) -> CallToolResult:
        """查询企业成员"""
        if not self.user_token:
            return CallToolResult(
                content=[TextContent(type="text", text="Error: User token not set. Please set user token first.")]
            )
        
        url = f"{self.base_url}/v1/assets/manage/members"
        headers = {"userToken": self.user_token, "clientToken": self.client_token}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                result = await response.json()
                return CallToolResult(
                    content=[TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
                )
    
    async def _query_asset_privilege_status(self, arguments: Dict[str, Any]) -> CallToolResult:
        """查询资产权限状态"""
        if not self.user_token:
            return CallToolResult(
                content=[TextContent(type="text", text="Error: User token not set. Please set user token first.")]
            )
        
        asset_id = arguments["assetId"]
        url = f"{self.base_url}/v1/assets/manage/asset/{asset_id}/privilege/status"
        headers = {"userToken": self.user_token, "clientToken": self.client_token}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                result = await response.json()
                return CallToolResult(
                    content=[TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
                )
    
    async def _set_user_token(self, arguments: Dict[str, Any]) -> CallToolResult:
        """设置用户令牌"""
        self.user_token = arguments["userToken"]
        return CallToolResult(
            content=[TextContent(type="text", text=f"User token set successfully: {self.user_token[:10]}...")]
        )
    
    async def _set_client_token(self, arguments: Dict[str, Any]) -> CallToolResult:
        """设置客户端令牌"""
        self.client_token = arguments["clientToken"]
        return CallToolResult(
            content=[TextContent(type="text", text=f"Client token set successfully: {self.client_token[:10]}...")]
        )
    
    async def _set_base_url(self, arguments: Dict[str, Any]) -> CallToolResult:
        """设置API基础URL"""
        self.base_url = arguments["baseUrl"]
        return CallToolResult(
            content=[TextContent(type="text", text=f"Base URL set successfully: {self.base_url}")]
        )

async def main():
    """Main entry point for the MCP server."""
    server = MyGlodonMCPServer()
    
    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await server.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="myglodon-asset-management",
                server_version="1.0.0",
                capabilities=server.server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None,
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main()) 