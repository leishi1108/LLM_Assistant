# LLM-Assistant: 基于 LangGraph 的智能对话助手

## 🎯 项目概述

LLM-Assistant 是一个基于 LangGraph 框架构建的智能对话助手系统，支持多轮对话、工具调用和智能路由。系统采用模块化设计，能够根据用户意图自动选择合适的 Agent 处理不同类型的请求，特别针对资产管理和知识问答场景进行了优化。

## 🏗️ 技术架构

### 核心框架选型

- **LangGraph**: 主要的状态图管理框架，用于构建复杂的对话流程
- **LangChain**: 提供 Agent 创建和工具集成能力
- **FastMCP**: 微服务通信协议，用于工具服务集成
- **CustomLLM**: 自定义 LLM 接口，支持多种模型服务
- **FastAPI**: Web API 框架，提供 HTTP 和 WebSocket 接口

### 架构组件

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   用户输入      │    │  FastAPI 服务器  │    │  LangGraph      │
│  (HTTP/WS)      │───▶│   (API 网关)     │───▶│  (状态图路由)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │  React Agent    │    │  工具服务       │
                       │  (智能代理)      │───▶│  (MCP/ReAPI)    │
                       └─────────────────┘    └─────────────────┘
```

#### 数据流向
- **水平流向**: 用户输入 → FastAPI → LangGraph
- **垂直流向**: LangGraph → React Agent → 工具服务
- **核心流程**: 请求经过API网关，由LangGraph路由到React Agent，Agent调用工具服务完成处理

#### 详细组件层次

```
┌─────────────────────────────────────────────────────────────────┐
│                        FastAPI 服务器层                        │
├─────────────────────────────────────────────────────────────────┤
│  HTTP API          │  WebSocket API      │  会话管理           │
│  /chat             │  /ws                │  /sessions          │
│  /health           │  流式输出            │  /demo              │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        LangGraph 状态图                        │
├─────────────────────────────────────────────────────────────────┤
│  GraphBuilder      │  AgentState        │  MessageHandler     │
│  - 图构建          │  - 状态管理         │  - 消息格式化       │
│  - 节点连接        │  - 令牌管理         │  - 类型转换         │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        路由决策层                              │
├─────────────────────────────────────────────────────────────────┤
│  IntentDetector    │  RouterNode        │  ShouldUseReact     │
│  - 意图识别        │  - 路由分发         │  - React判断        │
│  - LLM分析         │  - 状态更新         │  - 重置处理         │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      React Agent 执行层                        │
├─────────────────────────────────────────────────────────────────┤
│  create_react_agent (LangGraph内置)                            │
│  ├── LLM 推理引擎                                              │
│  ├── 工具调用机制                                              │
│  ├── 参数收集逻辑                                              │
│  └── 响应生成策略                                              │
│                                                                 │
│  Agent 实现:                                                   │
│  ├── create_seek_application_agent()                           │
│  │   ├── 工具集: tools1 (基础工具)                             │
│  │   ├── 提示词: 参数收集专用                                  │
│  │   └── 功能: 菜单找回、天气查询等                            │
│  │                                                             │
│  ├── create_asset_center_agent(state)                          │
│  │   ├── 工具集: tools2 (资产管理)                             │
│  │   ├── 提示词: 资产操作专用                                  │
│  │   ├── 状态感知: user_token, client_token                    │
│  │   └── 功能: 资产查询、权限分配等                            │
│  │                                                             │
│  └── knowledge_retrieval()                                     │
│      ├── 工具集: tools3 (知识库)                               │
│      ├── 提示词: 问答专用                                      │
│      └── 功能: ReAPI知识检索                                   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        工具集成层                              │
├─────────────────────────────────────────────────────────────────┤
│  MCP 客户端        │  工具注册          │  异步调用           │
│  - MultiServerMCP  │  - 动态发现        │  - asyncio.run()    │
│  - 连接管理        │  - 缓存机制        │  - 超时处理         │
│  - 错误处理        │  - 类型检查        │  - 重试逻辑         │
│                                                                 │
│  工具分类:                                                      │
│  ├── tools1: 基础工具 (天气、菜单等)                            │
│  ├── tools2: 资产管理工具 (查询、分配等)                        │
│  └── tools3: 知识库工具 (ReAPI检索)                            │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        外部服务层                              │
├─────────────────────────────────────────────────────────────────┤
│  MCP 服务器集群    │  ReAPI 服务        │  自定义 LLM         │
│  - 资产管理服务    │  - 知识检索        │  - CustomLLM        │
│  - 基础工具服务    │  - 认证授权        │  - 模型适配         │
│  - SSE 传输        │  - 结果格式化      │  - 配置管理         │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 核心特性

### 1. 智能路由系统
- 基于用户意图的自动 Agent 选择
- 支持多轮对话上下文保持
- 智能参数收集和工具调用
- 支持重置会话功能

### 2. 多 Agent 支持
- **seek_application_or_menu_agent**: 参数收集和工具调用
- **asset_center_agent**: 资产管理操作（查询、分配权限等）
- **knowledge_retrieval**: 知识库问答

### 3. 多工具支持
- **MCP 工具集群**: 通过 MCP 协议集成外部工具服务
- **资产管理工具**: 查询资产状态、分配权限、查询成员等
- **知识库工具**: 基于 ReAPI 的知识检索
- **基础工具**: 天气查询、菜单找回等

### 4. 状态管理
- 基于 MessagesState 的对话历史管理
- 自动消息格式化和序列化
- 支持复杂对话状态持久化
- 支持用户令牌和客户端令牌管理

### 5. Web API 接口
- **HTTP API**: 单次对话接口
- **WebSocket**: 实时流式对话接口
- **会话管理**: 支持多会话并发
- **认证机制**: 基于 Bearer Token 的认证

## 📁 项目结构

```
LLM-Assistant/
├── src/
│   └── agent/
│       ├── api/
│       │   └── server.py          # FastAPI 服务器
│       ├── core/
│       │   ├── state.py           # 状态管理
│       │   ├── graph_builder.py   # 图构建器
│       │   └── message_handler.py # 消息处理
│       ├── execution/
│       │   ├── react_agent.py     # ReAct Agent 实现
│       │   └── agent_runner.py    # Agent 运行器
│       ├── routing/
│       │   ├── intent_detector.py # 意图识别
│       │   └── router.py          # 路由逻辑
│       ├── tools/
│       │   └── mcp_client.py      # MCP 客户端
│       ├── config/
│       │   ├── settings.py        # 配置管理
│       │   └── prompts.py         # 提示词管理
│       ├── llm.py                 # 自定义 LLM 接口
│       └── main.py                # 主入口
├── tests/
│   ├── asset_manage_mcp_server.py # 资产管理 MCP 服务器
│   ├── mcp_server.py              # 基础 MCP 服务器
│   └── integration_tests/         # 集成测试
├── client_examples/               # 客户端示例
├── frontend_examples/             # 前端集成示例
├── README.md                      # 项目文档
└── requirements.txt               # 依赖管理
```

## 🔧 安装和配置

### 环境要求
- Python 3.8+
- 支持异步操作的环境

### 依赖安装
```bash
pip install langgraph langchain fastmcp fastapi uvicorn
```

### 配置说明
1. 在 `src/agent/config/settings.py` 中配置你的 LLM 服务
2. 启动 MCP 工具服务器
3. 配置 MCP 客户端连接信息

## 🎮 使用方法

### 1. 启动 MCP 工具服务
```bash
# 启动资产管理 MCP 服务器
cd tests
python asset_manage_mcp_server.py

# 启动基础 MCP 服务器
python mcp_server.py
```

### 2. 启动 API 服务器
```bash
# 启动 FastAPI 服务器
python src/agent/api/server.py

# 或使用 uvicorn
uvicorn src.agent.api.server:app --host 0.0.0.0 --port 8000
```

### 3. 使用 HTTP API
```bash
# 单次对话
curl -X POST "http://localhost:8000/chat" \
  -H "Authorization: Bearer your_token" \
  -H "Content-Type: application/json" \
  -d '{"message": "查询我的资产状态"}'
```

### 4. 使用 WebSocket API
```javascript
// 连接 WebSocket
const ws = new WebSocket('ws://localhost:8000/ws?token=your_token');

// 发送消息
ws.send(JSON.stringify({
  type: 'chat',
  message: '查询我的资产状态',
  chat_type: 'asset_center_agent'
}));
```

## 🧠 核心组件详解

### create_react_agent 核心机制

`create_react_agent` 是 LangGraph 提供的核心 Agent 创建函数，它实现了 ReAct (Reasoning + Acting) 模式：

#### 核心特性
- **推理与行动循环**: 结合 LLM 推理能力和工具调用
- **自动工具选择**: 根据用户输入智能选择合适的工具
- **参数收集**: 自动收集工具执行所需的参数
- **错误处理**: 内置重试和错误恢复机制

#### 工作流程
```
用户输入 → LLM分析 → 工具选择 → 参数收集 → 工具调用 → 结果处理 → 响应生成
    ↑                                                                    ↓
    └─────────────────── 循环迭代直到完成 ──────────────────────────────┘
```

#### 实现细节
```python
def create_react_agent(llm, tools, prompt):
    """
    创建 ReAct Agent
    
    参数:
    - llm: 语言模型实例
    - tools: 可用工具列表
    - prompt: 系统提示词
    
    返回:
    - 配置好的 Agent 实例
    """
    return create_react_agent(llm, tools, prompt)
```

#### Agent 运行机制

每个 Agent 都通过 `react_router_node` 进行统一调度：

```python
def react_router_node(state: AgentState):
    """Agent 统一调度器"""
    agent_name = state.get("current_agent")
    
    # 根据 agent_name 创建对应的 Agent
    if agent_name == "seek_application_or_menu_agent":
        agent = create_seek_application_agent()
    elif agent_name == "asset_center_agent":
        agent = create_asset_center_agent(state)
    elif agent_name == "knowledge_retrieval":
        agent = knowledge_retrieval()
    
    # 异步调用 Agent
    response = asyncio.run(agent.ainvoke({"messages": messages}))
    
    return response
```

#### 异步处理机制

系统采用异步处理确保工具调用的高效性：

- **异步调用**: 使用 `asyncio.run(agent.ainvoke())` 处理 MCP 工具
- **同步回退**: 异步失败时自动切换到同步调用
- **超时处理**: 内置超时机制防止长时间阻塞
- **错误恢复**: 多层次的错误处理和重试机制

### Agent 类型

#### seek_application_or_menu_agent
- **功能**: 参数收集和工具调用
- **工具**: 基础工具集（天气查询、菜单找回等）
- **工作流程**: 
  1. 分析工具需求
  2. 收集必需参数
  3. 调用相应工具
  4. 返回执行结果

#### asset_center_agent
- **功能**: 资产管理操作
- **工具**: 资产管理工具集
- **支持操作**:
  - 查询资产状态
  - 分配/取消分配资产权限
  - 查询在线产品
  - 查询企业成员
  - 查询资产权限状态
- **特点**: 支持用户友好的参数收集（收集名称而非ID）

#### knowledge_retrieval
- **功能**: 知识库问答
- **工具**: ReAPI 知识检索
- **适用场景**: 用户中心相关问答

### 路由逻辑

#### 意图识别算法
```python
def detect_agent(user_msg, history=None):
    # 基于关键词的模式匹配
    # 历史上下文分析
    # 操作指令识别
    # 返回对应的 Agent 类型
```

#### 路由决策
- **资产管理相关**: 路由到 `asset_center_agent`
- **知识问答相关**: 路由到 `knowledge_retrieval`
- **参数收集相关**: 路由到 `seek_application_or_menu_agent`
- **重置指令**: 清空当前会话

### 状态管理

#### AgentState 结构
```python
class AgentState(MessagesState):
    current_agent: str          # 当前活跃的 Agent
    user_token: Optional[str]   # 用户认证令牌
    client_token: Optional[str] # 客户端认证令牌
```

#### 消息格式
- 支持 HumanMessage、AIMessage、ToolMessage 等
- 自动序列化和反序列化
- 工具调用上下文保持

## 🔌 工具集成

### MCP 工具规范
```python
@mcp.tool()
def tool_name(param1: str, param2: str) -> dict:
    """工具描述"""
    try:
        # 工具逻辑
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

### 工具注册流程
1. MCP 服务器启动时自动注册工具
2. LangGraph 客户端连接并获取工具列表
3. Agent 自动识别可用工具
4. 根据用户需求选择合适的工具调用

### 资产管理工具
- **query_assets_by_status**: 查询资产状态
- **allocate_asset_privileges**: 分配资产权限
- **query_online_products**: 查询在线产品
- **query_enterprise_members**: 查询企业成员
- **query_asset_privilege_status**: 查询资产权限状态

## 📊 性能优化

### 1. 异步处理
- 使用 `asyncio.run()` 处理异步工具调用
- 支持并发工具执行
- WebSocket 支持流式输出

### 2. 内存管理
- 基于 MessagesState 的增量更新
- 避免重复消息存储
- 智能历史记录管理

### 3. 路由优化
- 意图识别缓存
- 历史上下文智能采样
- 快速 Agent 切换

### 4. 会话管理
- 支持多会话并发
- 自动会话清理
- 状态持久化

## 🧪 测试和调试

### 调试信息
系统提供详细的调试日志：
- Agent 调用状态
- 工具注册信息
- 路由决策过程
- 工具调用详情

### 测试工具
```bash
# 运行集成测试
python -m pytest tests/integration_tests/

# 测试多轮对话
python test_multi_turn_history.py

# 测试 API 接口
curl http://localhost:8000/health
```

### 演示页面
访问 `http://localhost:8000/demo` 查看 WebSocket 演示页面

## 🔮 扩展指南

### 添加新工具
1. 在 MCP 服务器中定义新工具
2. 更新 Agent 提示词
3. 重启 MCP 服务器

### 添加新 Agent
1. 在 `react_agent.py` 中定义新的 Agent 函数
2. 在路由逻辑中添加意图识别
3. 更新状态图配置

### 自定义 LLM
1. 继承 CustomLLM 类
2. 实现必要的接口方法
3. 在配置中指定使用

### 添加新 API 端点
1. 在 `server.py` 中添加新的路由
2. 定义请求/响应模型
3. 实现业务逻辑

## 🚨 注意事项

1. **MCP 服务**: 确保 MCP 服务器正常运行
2. **异步兼容**: 注意异步和同步调用的兼容性
3. **状态持久化**: 大型对话可能需要额外的状态管理
4. **错误处理**: 工具调用失败时的回退机制
5. **认证安全**: 生产环境请设置具体的 CORS 域名
6. **参数收集**: 优先收集用户友好的参数（名称而非ID）

## 📝 更新日志

- **v1.0.0**: 基础框架搭建，支持菜单找回工具
- **v1.1.0**: 添加天气查询工具，优化路由逻辑
- **v1.2.0**: 改进状态管理，支持多轮对话
- **v1.3.0**: 添加资产管理 Agent 和工具集成
- **v1.4.0**: 添加 FastAPI 服务器和 WebSocket 支持
- **v1.5.0**: 优化提示词模板，改进参数收集逻辑

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！请确保：
1. 代码符合项目规范
2. 添加必要的测试
3. 更新相关文档

## 📄 许可证

本项目采用 MIT 许可证，详见 LICENSE 文件。

---

**项目维护者**: LLM-Assistant Team  
**最后更新**: 2024年12月