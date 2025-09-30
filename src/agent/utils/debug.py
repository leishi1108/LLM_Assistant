"""
调试模块 - 日志记录和调试信息
"""

import logging
from typing import Any, Dict
from datetime import datetime


def setup_logging(level: int = logging.INFO) -> None:
    """设置日志记录 - 异步安全版本"""
    # 只使用 StreamHandler 避免阻塞调用
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )


def setup_file_logging(log_file: str = 'agent.log') -> None:
    """设置文件日志记录 - 仅在需要时使用"""
    try:
        # 使用相对路径避免阻塞调用
        import os
        log_path = os.path.join(os.getcwd(), log_file)
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        
        # 获取根日志记录器并添加文件处理器
        root_logger = logging.getLogger()
        root_logger.addHandler(file_handler)
        
    except Exception as e:
        # 如果文件日志设置失败，只使用控制台日志
        print(f"文件日志设置失败: {e}")


def log_debug_info(title: str, data: Any, level: str = "INFO") -> None:
    """记录调试信息"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if level.upper() == "DEBUG":
        print(f"[{timestamp}] 🔍 {title}")
    elif level.upper() == "INFO":
        print(f"[{timestamp}] ℹ️  {title}")
    elif level.upper() == "WARNING":
        print(f"[{timestamp}] ⚠️  {title}")
    elif level.upper() == "ERROR":
        print(f"[{timestamp}] ❌ {title}")
    else:
        print(f"[{timestamp}] {title}")
    
    if isinstance(data, dict):
        for key, value in data.items():
            print(f"  {key}: {value}")
    elif isinstance(data, list):
        for i, item in enumerate(data):
            print(f"  [{i}]: {item}")
    else:
        print(f"  {data}")
    
    print()  # 空行分隔


def log_agent_call(agent_name: str, input_data: Dict, response: Any) -> None:
    """记录代理调用信息"""
    log_debug_info(
        f"调用代理: {agent_name}",
        {
            "输入": input_data,
            "响应类型": type(response).__name__,
            "响应键": list(response.keys()) if isinstance(response, dict) else "N/A"
        },
        "INFO"
    )


def log_tool_call(tool_name: str, parameters: Dict, result: Any) -> None:
    """记录工具调用信息"""
    log_debug_info(
        f"工具调用: {tool_name}",
        {
            "参数": parameters,
            "结果类型": type(result).__name__,
            "结果": result
        },
        "INFO"
    )
