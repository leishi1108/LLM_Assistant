from typing import Dict, Any, Optional

import httpx
from fastmcp import FastMCP
import requests
import json
from fastmcp.server.auth import AuthProvider, AccessToken

# 鉴权配置
AUTH_API_URL = "https://your-auth-domain.com/api/auth/verify"  # 替换为你的鉴权接口地址
AUTH_TIMEOUT = 30

class CustomTokenVerifier(AuthProvider):
    """自定义Token验证器，通过调用外部鉴权接口验证token"""
    
    def __init__(self, auth_url: str, resource_server_url: str = None, required_scopes: list = None):
        super().__init__(resource_server_url=resource_server_url)
        self.auth_url = auth_url
        self.required_scopes = required_scopes or ["read", "write"]
    
    async def verify_token(self, token: str) -> Optional[AccessToken]:
        """验证token的有效性
        
        Args:
            token: 用户提供的token
            
        Returns:
            AccessToken对象如果验证成功，None如果验证失败
        """
        try:
            # 处理token格式
            auth_token = token if token.startswith("Bearer ") else f"Bearer {token}"
            
            # 构建鉴权请求头
            headers = {
                "Authorization": auth_token,
                "Content-Type": "application/json"
            }
            
            # 发送鉴权请求（使用同步请求，因为这是示例）
            print(f"开始验证token: {token[:20]}...")
            resp = requests.get(self.auth_url, headers=headers, timeout=AUTH_TIMEOUT)
            
            # 检查响应状态
            if resp.status_code == 200:
                result = resp.json()
                print(f"Token验证成功")
                
                # 创建AccessToken对象
                # 这里可以根据你的鉴权接口返回的数据结构来调整
                return AccessToken(
                    token=token,
                    token_type="Bearer",
                    expires_in=3600,  # 默认1小时过期
                    scopes=self.required_scopes,  # 使用配置的权限范围
                    user_id=result.get("user_id", "unknown"),  # 从鉴权结果中获取用户ID
                    client_id=result.get("client_id", "unknown")  # 从鉴权结果中获取客户端ID
                )
            else:
                error_msg = f"Token验证失败，状态码: {resp.status_code}"
                try:
                    error_detail = resp.json()
                    error_msg += f"，错误详情: {error_detail}"
                except:
                    error_msg += f"，响应内容: {resp.text}"
                
                print(f"Token验证失败: {error_msg}")
                return None
                
        except requests.exceptions.RequestException as e:
            error_msg = f"鉴权接口网络异常: {str(e)}"
            print(f"鉴权接口网络异常: {error_msg}")
            return None
        except Exception as e:
            error_msg = f"鉴权过程未知异常: {str(e)}"
            print(f"鉴权过程未知异常: {error_msg}")
            return None
    
    def get_routes(self):
        """获取鉴权路由（默认实现）"""
        return []
    
    def get_resource_metadata_url(self):
        """获取资源元数据URL（默认实现）"""
        return None

def configure_auth(auth_url: str, timeout: int = 30):
    """配置鉴权接口地址和超时时间

    Args:
        auth_url: 鉴权接口的完整URL
        timeout: 请求超时时间（秒）
    """
    global AUTH_API_URL, AUTH_TIMEOUT
    AUTH_API_URL = auth_url
    AUTH_TIMEOUT = timeout
    print(f"鉴权配置已更新: URL={auth_url}, 超时={timeout}秒")

# 创建自定义鉴权提供者
auth_provider = CustomTokenVerifier(
        auth_url="https://auth.company.com/api/verify",        # 外部鉴权服务
    resource_server_url="http://localhost:8081",
    required_scopes=["read", "write"]
)

mcp = FastMCP("asert_center_tool_list", auth=auth_provider)

@mcp.tool()
def asset_allocation_mcp(workspaceCode: str, appCode: str) -> dict:
    """调用接口把包含某个产品的资产分配给一个指定的员工
    
    参数说明：
        workspaceCode：工作空间编码
        appCode: 应用代码
    
    返回格式：
        成功时返回API响应数据，失败时返回错误信息
    """
    try:
        return "2"
            
    except requests.exceptions.RequestException as e:
        error_msg = f"网络请求异常: {str(e)}"
        print(f"网络请求异常: {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "type": "network_error"
        }
    except json.JSONDecodeError as e:
        error_msg = f"响应解析异常: {str(e)}"
        print(f"响应解析异常: {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "type": "parse_error"
        }
    except Exception as e:
        error_msg = f"未知异常: {str(e)}"
        print(f"未知异常: {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "type": "unknown_error"
        }

if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8081)

