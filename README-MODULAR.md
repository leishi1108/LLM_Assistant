# LLM-Assistant: 模块化架构设计

## 概述

本项目已经重构为清晰的模块化架构，遵循SOLID原则和最佳实践，使代码更加可维护、可测试和可扩展。

## 架构概览

```
src/agent/
├── __init__.py              # 主模块初始化
├── main.py                  # 主程序入口
├── core/                    # 核心模块
│   ├── __init__.py
│   ├── state.py            # 状态管理
│   ├── graph_builder.py    # 图构建器
│   └── message_handler.py  # 消息处理
├── routing/                 # 路由模块
│   ├── __init__.py
│   ├── intent_detector.py  # 意图识别
│   └── router.py           # 路由节点
├── execution/               # 执行模块
│   ├── __init__.py
│   ├── react_agent.py      # ReAct代理
│   ├── agent_runner.py     # 代理运行器
│   └── fallback.py         # 回退节点
├── tools/                   # 工具集成模块
│   ├── __init__.py
│   ├── mcp_client.py       # MCP客户端
│   └── tool_registry.py    # 工具注册表
├── config/                  # 配置模块
│   ├── __init__.py
│   ├── settings.py         # 设置管理
│   └── prompts.py          # 提示词管理
└── utils/                   # 工具模块
    ├── __init__.py
    ├── debug.py            # 调试工具
    └── validators.py       # 验证工具
```

## 模块说明

### 1. 核心模块 (`core/`)

#### `state.py`
- 定义 `AgentState` 类，继承自 `MessagesState`
- 支持消息的追加合并和状态管理
- 包含 `current_agent` 和 `reset_flag` 字段

#### `graph_builder.py`
- 封装 `StateGraph` 构建逻辑
- 自动设置节点、边和条件路由
- 提供 `compile()` 方法生成最终图

#### `message_handler.py`
- 提供 `ensure_message_format()` 函数
- 处理各种消息类型的格式转换
- 支持 `ToolMessage`、`AIMessage` 等

### 2. 路由模块 (`routing/`)

#### `intent_detector.py`
- 实现混合意图识别策略
- 规则基础 + LLM基础的识别方法
- 支持参数收集、重置、闲聊等意图

#### `router.py`
- 实现路由节点逻辑
- 根据意图决定使用哪个代理
- 支持状态转换和重置功能

### 3. 执行模块 (`execution/`)

#### `react_agent.py`
- 创建 ReAct 代理实例
- 管理代理配置和提示词
- 集成工具和LLM

#### `agent_runner.py`
- 执行代理调用逻辑
- 处理异步/同步调用
- 管理消息增量和错误处理

#### `fallback.py`
- 提供回退节点功能
- 处理无法路由的请求

### 4. 工具集成模块 (`tools/`)

#### `mcp_client.py`
- 管理 MCP 客户端连接
- 实现工具发现和注册
- 提供连接管理和错误处理

#### `tool_registry.py`
- 工具注册表管理
- 工具验证和元数据管理
- 支持工具的动态注册

### 5. 配置模块 (`config/`)

#### `settings.py`
- 集中管理配置参数
- LLM 和 MCP 服务器配置
- 环境变量和默认值

#### `prompts.py`
- 系统提示词模板管理
- 支持动态提示词生成
- 提示词版本管理

### 6. 工具模块 (`utils/`)

#### `debug.py`
- 日志记录和调试信息
- 性能监控和错误追踪
- 格式化的调试输出

#### `validators.py`
- 参数和格式验证
- 工具参数验证
- 工作空间选择验证

## 设计原则

### 1. 单一职责原则 (SRP)
- 每个模块只负责一个特定功能
- 清晰的职责边界和接口

### 2. 开闭原则 (OCP)
- 对扩展开放，对修改封闭
- 通过接口和抽象支持新功能

### 3. 依赖倒置原则 (DIP)
- 高层模块不依赖低层模块
- 通过抽象接口解耦

### 4. 接口隔离原则 (ISP)
- 客户端不依赖不需要的接口
- 最小化接口依赖

## 使用方法

### 1. 基本使用

```python
from agent import create_graph

# 创建图实例
graph = create_graph()

# 使用图处理请求
result = graph.invoke({
    "messages": [HumanMessage(content="帮我创建应用")]
})
```

### 2. 扩展新功能

#### 添加新的代理类型
```python
# 在 execution/ 目录下创建新文件
# 在 routing/ 中添加新的意图识别
# 在 config/ 中添加相关配置
```

#### 添加新的工具
```python
# 在 tools/ 目录下创建新文件
# 在 mcp_client.py 中注册新工具
# 在 prompts.py 中添加工具说明
```

### 3. 配置管理

```python
from agent.config import get_llm, get_mcp_config

# 获取LLM配置
llm = get_llm()

# 获取MCP配置
mcp_config = get_mcp_config()
```

## 测试

运行测试验证架构：

```bash
# 激活虚拟环境
source venv1/bin/activate

# 运行测试
python test_modular_architecture.py
```

## 优势

### 1. 可维护性
- 代码分散到不同模块，易于定位和修改
- 清晰的依赖关系，减少耦合

### 2. 可测试性
- 模块独立，便于单元测试
- 清晰的接口，易于模拟和验证

### 3. 可扩展性
- 新功能可以独立添加新模块
- 插件化架构，支持动态扩展

### 4. 团队协作
- 不同开发者可以并行开发不同模块
- 清晰的模块边界，减少冲突

### 5. 代码复用
- 通用功能抽象到工具模块
- 配置和提示词集中管理

## 迁移指南

### 从单体架构迁移

1. **保持接口兼容**
   - 主入口 `graph` 保持不变
   - 外部调用方式无需修改

2. **逐步迁移**
   - 可以先迁移部分模块
   - 保持向后兼容性

3. **测试验证**
   - 运行测试确保功能正常
   - 验证性能和稳定性

## 未来规划

### 1. 插件系统
- 支持动态加载模块
- 配置驱动的功能开关

### 2. 性能优化
- 异步处理优化
- 缓存和连接池管理

### 3. 监控和日志
- 结构化日志
- 性能指标收集

### 4. 配置管理
- 环境配置分离
- 动态配置更新

## 总结

模块化架构重构成功实现了以下目标：

✅ **代码组织清晰** - 功能按模块分类，职责明确  
✅ **依赖关系清晰** - 模块间依赖明确，易于理解  
✅ **扩展性增强** - 新功能可以独立添加  
✅ **可维护性提升** - 代码分散，易于维护  
✅ **团队协作友好** - 并行开发，减少冲突  
✅ **测试覆盖完整** - 模块独立，易于测试  

这种架构设计为项目的长期发展奠定了坚实的基础，使代码更加专业、可维护和可扩展。
