#!/usr/bin/env python3
"""
启动自定义API服务器
"""

import uvicorn
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("🚀 启动 LLM Assistant 自定义API服务器...")
    print("📡 API地址: http://localhost:8000")
    print("🌐 演示页面: http://localhost:8000/demo")
    print("📚 API文档: http://localhost:8000/docs")
    print("🔌 WebSocket: ws://localhost:8000/ws/{session_id}")
    print("=" * 50)
    
    uvicorn.run(
        "src.agent.api.server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # 开发模式，代码变更自动重载
        log_level="info"
    )
