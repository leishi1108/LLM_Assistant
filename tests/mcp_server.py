from typing import Dict, Any, Optional

import httpx
from fastmcp import FastMCP
import requests
import json

mcp = FastMCP("tool_list")

@mcp.tool()
def seek_application_or_menu_mcp(domain: str, orgId: str, productCode: str, appCode: str,
                             menuAuthCode: str, appType: str, token: str) -> dict:
    """调用接口排查菜单丢失的原因
    指定给某人指定某个资产，去做分配
    参数说明：
        domain: 域名，
        orgId: 组织ID，
        productCode: 产品代码
        appCode: 应用代码
        menuAuthCode: 菜单权限代码
        appType: 子应用类型，0-> web端，1->移动端
        token: 项管平台获取的认证token
    
    返回格式：
        成功时返回API响应数据，失败时返回错误信息
    """
    try:
        # 处理域名格式
        domain = domain if domain.startswith("http") else 'https://' + domain
        url = domain + "/api/workbench/v4/problem-solving-tool/seek--application-or-menu"
        
        # 构建请求参数
        params = {
            "orgId": orgId,
            "productCode": productCode,
            "appCode": appCode,
            "menuAuthCode": menuAuthCode,
            "appType": appType
        }
        
        print(f"开始调用接口: {url}")
        print(f"请求参数: {params}")
        
        # 处理token格式
        token = token if token.startswith("bearer") else 'Bearer ' + token
        headers = {"Authorization": token}
        
        # 发送请求
        resp = requests.get(url, params=params, headers=headers, timeout=30)
        
        # 检查响应状态
        if resp.status_code == 200:
            result = resp.json()
            print(f"接口调用成功: {result}")
            return {
                "success": True,
                "data": result,
                "message": "接口调用成功"
            }
        else:
            error_msg = f"接口调用失败，状态码: {resp.status_code}"
            try:
                error_detail = resp.json()
                error_msg += f"，错误详情: {error_detail}"
            except:
                error_msg += f"，响应内容: {resp.text}"
            
            print(f"接口调用失败: {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "status_code": resp.status_code
            }
            
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

@mcp.tool()
def get_weather_mcp(city: str, region: str) -> dict:
    """获取指定城市和地区的天气信息
    
    参数说明：
        city: 城市名称
        region: 地区名称
    
    返回格式：
        成功时返回天气信息，失败时返回错误信息
    """
    try:
        print(f"获取天气信息: 城市={city}, 地区={region}")
        
        # 模拟天气数据（固定返回）
        weather_data = {
            "city": city,
            "region": region,
            "weather": "晴转多云",
            "temperature": "18°C",
            "humidity": "65%",
            "wind": "东南风3级",
            "date": "今天"
        }
        
        print(f"天气信息获取成功: {weather_data}")
        return {
            "success": True,
            "data": weather_data,
            "message": f"今天{city}{region}晴转多云"
        }
        
    except Exception as e:
        error_msg = f"获取天气信息失败: {str(e)}"
        print(f"获取天气信息异常: {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "type": "weather_error"
        }

@mcp.tool()
def get_orgs_by_user_mcp(org_id: str) -> Dict[str, Any]:
    """获取组织下所有工作空间列表信息

    参数说明：
        org_id: 组织ID

    返回格式：
        成功时返回组织列表中name，code，失败时返回错误信息
    """
    try:

        module_code: str = "open.my-component",
        print(f"获取组织列表: org_id={org_id}, module_code={module_code}")

        # 构建请求头
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN',
            'authorization': f'bearer 38d4b610-a7d5-4a86-b704-d037d77d044d',
            'priority': 'u=1, i',
            'sec-ch-ua': '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
            'x-module-code': 'open.my-component',
            'x-org-id': org_id,
            'x-product-code': 'open'
        }

        # 发送请求
        url = "https://aecloud-open-test.glodon.com/api/org-permission/v4/orgs/list-by-userId"
        # 发送请求
        resp = requests.get(url, headers=headers, timeout=30)
        # 检查响应状态
        if resp.status_code == 200:
            result = resp.json()
            # 提取指定字段
            fields = ["name", "code"]
            extracted_data = []
            for item in result:
                extracted_item = {}
                for field in fields:
                    if field in item:
                        extracted_item[field] = item[field]
                    else:
                        extracted_item[field] = None  # 如果字段不存在，设为None
                extracted_data.append(extracted_item)
            print(f"接口调用成功: {result}")
            return {
                "success": True,
                "data": extracted_data,
                "message": "接口调用成功"
            }
        else:
            error_msg = f"接口调用失败，状态码: {resp.status_code}"
            try:
                error_detail = resp.json()
                error_msg += f"，错误详情: {error_detail}"
            except:
                error_msg += f"，响应内容: {resp.text}"

            print(f"接口调用失败: {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "status_code": resp.status_code
            }

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
    mcp.run(transport="sse",port =8001)  # host/port 默认即可

