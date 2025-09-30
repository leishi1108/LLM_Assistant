from typing import Dict, Any, Optional
import httpx
from fastmcp import FastMCP
from fastmcp.server.auth import JWTVerifier, StaticTokenVerifier, AuthProvider, AccessToken
import requests
import json

# 方式1: 使用JWT验证器（如果你的鉴权接口返回JWT token）
jwt_auth = JWTVerifier(
    resource_server_url="http://localhost:8081",
    required_scopes=["read", "write"]
)

# 方式2: 使用静态Token验证器（用于测试或简单场景）
static_auth = StaticTokenVerifier(
    resource_server_url="http://localhost:8081",
    required_scopes=["read", "write"]
)

# 方式3: 自定义Token验证器（推荐用于你的场景）
class CustomTokenVerifier(AuthProvider):
    """自定义Token验证器，通过调用外部鉴权接口验证token"""
    
    def __init__(self, auth_url: str, resource_server_url: str = None, required_scopes: list = None):
        super().__init__(resource_server_url=resource_server_url)
        self.auth_url = auth_url
        self.required_scopes = required_scopes or ["read", "write"]
    
    async def verify_token(self, token: str) -> Optional[AccessToken]:
        """验证token的有效性"""
        try:
            # 处理token格式
            auth_token = token if token.startswith("Bearer ") else f"Bearer {token}"
            
            # 构建鉴权请求头
            headers = {
                "Authorization": auth_token,
                "Content-Type": "application/json"
            }
            
            # 发送鉴权请求
            print(f"开始验证token: {token[:20]}...")
            resp = requests.get(self.auth_url, headers=headers, timeout=30)
            
            if resp.status_code == 200:
                result = resp.json()
                print("Token验证成功")
                
                # 返回AccessToken对象
                return AccessToken(
                    token=token,
                    token_type="Bearer",
                    expires_in=3600,
                    scopes=self.required_scopes,
                    user_id=result.get("user_id", "unknown"),
                    client_id=result.get("client_id", "unknown")
                )
            else:
                print(f"Token验证失败: {resp.status_code}")
                return None
                
        except Exception as e:
            print(f"鉴权异常: {e}")
            return None
    
    def get_routes(self):
        """获取鉴权路由（默认实现）"""
        return []
    
    def get_resource_metadata_url(self):
        """获取资源元数据URL（默认实现）"""
        return None

# 创建自定义鉴权提供者
custom_auth = CustomTokenVerifier(
    auth_url="https://your-auth-domain.com/api/auth/verify",
    resource_server_url="http://localhost:8081",
    required_scopes=["read", "write"]
)

# 选择一种鉴权方式（推荐使用自定义鉴权）
# auth_provider = jwt_auth          # JWT验证
# auth_provider = static_auth       # 静态Token验证
auth_provider = custom_auth         # 自定义鉴权（推荐）

# 创建MCP实例
mcp = FastMCP(
    "asert_center_tool_list",
    auth=auth_provider,
    instructions="这是一个资产分配工具，需要有效的认证token才能使用"
)

@mcp.tool()
def asset_allocation_mcp(workspaceCode: str, appCode: str) -> dict:
    """调用接口把包含某个产品的资产分配给一个指定的员工
    
    参数说明：
        workspaceCode：工作空间编码
        appCode: 应用代码
    
    返回格式：
        成功时返回API响应数据，失败时返回错误信息
    
    注意：此工具需要有效的认证token，token应该在请求头中提供
    """
    try:
        return "2"
        # 你的业务逻辑代码...
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "type": "unknown_error"
        }

if __name__ == "__main__":
    print("启动MCP服务器，已启用内置鉴权功能...")
    print("注意：所有工具调用都需要在请求头中提供有效的Authorization token")
    
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8081)
