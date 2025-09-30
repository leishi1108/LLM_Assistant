"""
FastAPI服务器 - 提供自定义对话接口
"""

from fastapi import FastAPI, Header, HTTPException, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import json
import uuid
from datetime import datetime

from ..main import create_graph
from ..core.state import AgentState
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage


# 请求/响应模型
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: str
    status: str = "success"
    error: Optional[str] = None

class SessionInfo(BaseModel):
    session_id: str
    created_at: str
    message_count: int
    last_activity: str

# 全局变量
app = FastAPI(title="LLM Assistant API", version="1.0.0")
graph = None
active_sessions: Dict[str, Dict[str, Any]] = {}
websocket_connections: Dict[str, WebSocket] = {}

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境请设置具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化LangGraph"""
    global graph
    try:
        graph = create_graph()
        print("✅ LangGraph 初始化成功")
    except Exception as e:
        print(f"❌ LangGraph 初始化失败: {e}")
        raise

@app.get("/")
async def root():
    """根路径 - 返回API信息"""
    return {
        "message": "LLM Assistant API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "chat": "/chat",
            "websocket": "/ws",
            "sessions": "/sessions",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "graph_loaded": graph is not None,
        "active_sessions": len(active_sessions)
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, authorization: Optional[str] = Header(None)):
    """单次对话接口"""
    # if not graph:
    #     raise HTTPException(status_code=500, detail="LangGraph not initialized")
    
    try:
        # 生成或使用现有会话ID
        session_id = request.session_id or str(uuid.uuid4())
        if not authorization:
            raise HTTPException(status_code=401, detail="Authorization header missing")

        # 通常 token 格式为 "Bearer <token>"
        token = None  # 去掉 "Bearer " 前缀
        if authorization.startswith("Bearer "):
            token = authorization[7:]  # 去掉 "Bearer " 前缀
        if token is None:
            raise HTTPException(status_code=500, detail="token is null")
        # 获取或创建会话状态
        if session_id not in active_sessions:
            active_sessions[session_id] = {
                "messages": [],
                "created_at": datetime.now().isoformat(),
                "message_count": 0
            }

        session = active_sessions[session_id]

        # 构建消息
        user_message = HumanMessage(content=request.message)
        session["messages"].append(user_message)
        client_token = "cn-95354332-333f-460b-9a20-e869c4ca56b8"
        # 构建状态
        state = AgentState(
            messages=session["messages"],
            current_agent="asset_center_agent" , # 默认agent
            user_token = token,
            client_token = client_token
        )

        # 调用LangGraph
        result = await asyncio.get_event_loop().run_in_executor(
            None, graph.invoke, state
        )

        # 更新会话状态
        if "messages" in result:
            session["messages"].extend(result["messages"])

        session["message_count"] += 1
        session["last_activity"] = datetime.now().isoformat()
        session["client_token"] = result.get("client_token")

        # 获取AI响应
        ai_response = ""
        if result.get("messages"):
            # 反向遍历，找到最后一个AIMessage就停止
            for msg in reversed(result["messages"]):
                if isinstance(msg, AIMessage):
                    ai_response = msg.content
                    break  # 找到最后一个就退出循环

        if not ai_response:
            ai_response = "抱歉，我无法处理您的请求。"

        return ChatResponse(
            response=ai_response,
            session_id=session_id,
            timestamp=datetime.now().isoformat(),
            status="success"
        )
        
    except Exception as e:
        return ChatResponse(
            response="",
            session_id=request.session_id or str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(),
            status="error",
            error=str(e)
        )

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: Optional[str] = Query(default=None)):
    """WebSocket实时对话接口 - 流式输出"""
    await websocket.accept()

    # 生成会话ID
    session_id = str(uuid.uuid4())
    websocket_connections[session_id] = websocket
    
    # Token 验证
    if token is None:
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": "缺少认证token",
            "timestamp": datetime.now().isoformat()
        }))
        await websocket.close()
        return

    try:
        # 初始化会话
        active_sessions[session_id] = {
            "messages": [],
            "created_at": datetime.now().isoformat(),
            "message_count": 0,
            "user_token": token
        }
        
        # 发送欢迎消息
        await websocket.send_text(json.dumps({
            "type": "welcome",
            "message": "连接成功！可以开始对话了。",
            "session_id": session_id
        }))
        
        while True:
            # 接收消息
            data = await websocket.receive_text()
            message_data = json.loads(data)
            chat_type = message_data.get("chat_type")

            if chat_type == "reset":
                # 重置会话 - 保留user_token和client_token
                if session_id in active_sessions:
                    current_token = active_sessions[session_id].get("user_token")
                    current_client_token = active_sessions[session_id].get("client_token")
                    active_sessions[session_id] = {
                        "messages": [],
                        "created_at": datetime.now().isoformat(),
                        "message_count": 0,
                        "user_token": current_token,
                        "client_token": current_client_token
                    }
                await websocket.send_text(json.dumps({
                    "type": "reset_complete",
                    "message": "会话已重置",
                    "timestamp": datetime.now().isoformat()
                }))
            else:
                user_message = message_data.get("message", "")

                # 处理对话
                session = active_sessions[session_id]
                session["messages"].append(HumanMessage(content=user_message))

                # 构建状态
                state = AgentState(
                    messages=session["messages"],
                    current_agent=chat_type,
                    user_token=session.get("user_token", token),
                    client_token=session.get("client_token")
                )

                # 发送开始处理信号
                await websocket.send_text(json.dumps({
                    "type": "processing_start",
                    "current_agent": "asset_center_agent",
                    "timestamp": datetime.now().isoformat()
                }))

                try:
                    # 调用LangGraph
                    result = await asyncio.get_event_loop().run_in_executor(
                        None, graph.invoke, state
                    )

                    # 更新会话状态
                    if "messages" in result:
                        session["messages"].extend(result["messages"])

                    session["message_count"] += 1
                    session["last_activity"] = datetime.now().isoformat()
                    session["client_token"] = result.get("client_token")

                    # 流式发送AI响应
                    ai_response = ""
                    if result.get("messages"):
                        # 反向遍历，找到最后一个AIMessage
                        for msg in reversed(result["messages"]):
                            if isinstance(msg, AIMessage):
                                ai_response = msg.content
                                break

                    if not ai_response:
                        ai_response = "抱歉，我无法处理您的请求。"

                    # 模拟流式输出 - 按字符发送
                    chunk_size = 10  # 每次发送10个字符
                    for i in range(0, len(ai_response), chunk_size):
                        chunk = ai_response[i:i + chunk_size]
                        await websocket.send_text(json.dumps({
                            "type": "response_chunk",
                            "chunk": chunk,
                            "is_final": i + chunk_size >= len(ai_response),
                            "timestamp": datetime.now().isoformat()
                        }))
                        # 添加小延迟模拟流式效果
                        await asyncio.sleep(0.05)

                    # 发送完成信号
                    await websocket.send_text(json.dumps({
                        "type": "response_complete",
                        "full_response": ai_response,
                        "timestamp": datetime.now().isoformat()
                    }))

                except Exception as e:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": f"处理消息时出错: {str(e)}",
                        "timestamp": datetime.now().isoformat()
                    }))

                
    except WebSocketDisconnect:
        # 清理连接
        if session_id in websocket_connections:
            del websocket_connections[session_id]
    except Exception as e:
        try:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": f"WebSocket连接出错: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }))
        except:
            pass  # 连接可能已断开

@app.get("/sessions", response_model=List[SessionInfo])
async def get_sessions():
    """获取所有会话信息"""
    sessions = []
    for session_id, session_data in active_sessions.items():
        sessions.append(SessionInfo(
            session_id=session_id,
            created_at=session_data["created_at"],
            message_count=session_data["message_count"],
            last_activity=session_data["last_activity"]
        ))
    return sessions

@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """删除指定会话"""
    if session_id in active_sessions:
        del active_sessions[session_id]
        return {"message": f"会话 {session_id} 已删除"}
    else:
        raise HTTPException(status_code=404, detail="会话不存在")

@app.get("/demo")
async def demo_page():
    """演示页面"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>LLM Assistant Demo</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .chat-container { max-width: 800px; margin: 0 auto; }
            .message { margin: 10px 0; padding: 10px; border-radius: 5px; }
            .user { background-color: #e3f2fd; text-align: right; }
            .ai { background-color: #f3e5f5; }
            .input-area { margin-top: 20px; }
            input[type="text"] { width: 70%; padding: 10px; }
            button { padding: 10px 20px; margin-left: 10px; }
            .status { color: #666; font-size: 12px; }
        </style>
    </head>
    <body>
        <div class="chat-container">
            <h1>LLM Assistant Demo</h1>
            <div id="chat-messages"></div>
            <div class="input-area">
                <input type="text" id="message-input" placeholder="输入您的消息...">
                <button onclick="sendMessage()">发送</button>
                <button onclick="clearChat()">清空</button>
                <button onclick="resetSession()">重置会话</button>
            </div>
            <div class="status" id="status">准备就绪</div>
        </div>

        <script>
            let sessionId = null;
            let ws = null;
            let currentAiMessage = null;
            
            function addMessage(content, isUser = false) {
                const chatMessages = document.getElementById('chat-messages');
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${isUser ? 'user' : 'ai'}`;
                messageDiv.textContent = content;
                chatMessages.appendChild(messageDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
                return messageDiv;
            }
            
            function updateStatus(message) {
                document.getElementById('status').textContent = message;
            }
            
            function connectWebSocket() {
                if (ws && ws.readyState === WebSocket.OPEN) {
                    return;
                }
                
                const token = 'demo_token_123'; // 演示用token
                ws = new WebSocket(`ws://localhost:8000/ws?token=${encodeURIComponent(token)}`);
                
                ws.onopen = function() {
                    updateStatus('WebSocket连接已建立');
                };
                
                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    
                    switch(data.type) {
                        case 'welcome':
                            sessionId = data.session_id; // 从服务器获取session_id
                            updateStatus('连接成功，可以开始对话');
                            break;
                            
                        case 'processing_start':
                            updateStatus(`正在处理... (检测到: ${data.detected_agent})`);
                            currentAiMessage = addMessage('', false);
                            break;
                            
                        case 'response_chunk':
                            if (currentAiMessage) {
                                currentAiMessage.textContent += data.chunk;
                                document.getElementById('chat-messages').scrollTop = document.getElementById('chat-messages').scrollHeight;
                            }
                            break;
                            
                        case 'response_complete':
                            currentAiMessage = null;
                            updateStatus('响应完成');
                            break;
                            
                        case 'error':
                            addMessage('错误: ' + data.message, false);
                            updateStatus('发生错误');
                            break;
                            
                        case 'reset_complete':
                            updateStatus('会话已重置');
                            break;
                            
                        case 'pong':
                            // 心跳响应
                            break;
                    }
                };
                
                ws.onclose = function() {
                    updateStatus('WebSocket连接已断开');
                    ws = null;
                };
                
                ws.onerror = function(error) {
                    updateStatus('WebSocket连接错误');
                    console.error('WebSocket error:', error);
                };
            }
            
            function generateSessionId() {
                return 'session_' + Math.random().toString(36).substr(2, 9);
            }
            
            function sendMessage() {
                const input = document.getElementById('message-input');
                const message = input.value.trim();
                if (!message) return;
                
                if (!ws || ws.readyState !== WebSocket.OPEN) {
                    connectWebSocket();
                    setTimeout(() => sendMessage(), 1000);
                    return;
                }
                
                addMessage(message, true);
                input.value = '';
                
                // 发送消息到WebSocket
                ws.send(JSON.stringify({
                    type: 'chat',
                    message: message
                }));
            }
            
            function clearChat() {
                document.getElementById('chat-messages').innerHTML = '';
                currentAiMessage = null;
                updateStatus('聊天已清空');
                
                if (ws) {
                    ws.close();
                    ws = null;
                }
            }
            
            function resetSession() {
                if (ws && ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify({
                        type: 'reset'
                    }));
                }
            }
            
            // 页面加载时连接WebSocket
            window.onload = function() {
                connectWebSocket();
            };
            
            // 回车发送消息
            document.getElementById('message-input').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
            
            // 定期发送心跳
            setInterval(function() {
                if (ws && ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify({type: 'ping'}));
                }
            }, 30000);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
