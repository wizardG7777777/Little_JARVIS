# Little_JARVIS

一个模块化的语音助手系统，能够响应并执行用户的语音指令。

## 概述

Little_JARVIS 是一个综合性的 AI 助手框架，具有以下特性：
- **语音转文字转换** 使用 Whisper 模型
- **大语言模型推理** 使用 Qwen3 和 Phi-4 模型
- **文字转语音转换**（开发中）
- **基于规则的意图分类** 用于安全和风险评估
- **函数调用和路由** 具有可扩展的注册系统
- **RAG（检索增强生成）** 提高准确性

## 工作原理

Little_JARVIS 通过多阶段管道处理语音命令：

```
语音输入 → Whisper (STT) → 规则引擎 → 意图路由器 → 动作执行 → 响应
                            ↓              ↓
                         [风险评估]    [LLM/RAG/函数]
```

### 核心组件

#### 1. 语音转文字模块（Whisper）
- **输入**：音频数据（numpy.ndarray）及采样率
- **输出**：转录文本（字符串）
- 将用户语音命令转换为文本进行处理

#### 2. 基于规则的引擎
- **用途**：分类用户意图并评估风险等级
- **风险等级**：L1-L5 映射到动作：
  - L1：高危禁止
  - L2-L3：需要确认
  - L4-L5：允许直接执行
- **意图类型**：
  - 设备控制（例如："打开空调"）
  - 信息查询（例如："查看当前车速"）
  - 日常聊天（例如："讲个笑话"）
  - 复杂命令
  - 系统操作
- **返回值**：(intent_type, action) 元组

#### 3. 函数注册系统
- **用途**：统一管理所有系统函数的 API
- **函数类型**：
  - 静态函数：核心应用函数
  - 插件函数：扩展功能（例如：`weather.get_forecast`）
  - 第三方 API：外部服务（例如：`stripe.payment`）
- **特性**：
  - 自动生成参数的 JSON Schema
  - 跟踪执行历史和统计信息
  - 支持批量注册
  - 持久化注册表（JSON）

#### 4. RAG 模块
- **用途**：减少幻觉并提高准确性
- **组件**：
  - Markdown 文件语义块切分器
  - 向量数据库（ChromaDB）存储
  - Qwen3-Embedding-0.6B 用于嵌入
- **函数**：
  - `split_markdown_semantic()`：将文档切分为语义块
  - `add()`：向量化并存储文本到数据库
  - `retrieve()`：为查询找到最相关的内容

#### 5. 语言模型集成
- **模型**：Qwen3 系列（0.6B、1.7B、4B）、Phi-4-mini-instruct
- **后端**：PyTorch、VLLM、llama.cpp
- **特性**：
  - 思维链模式用于复杂推理
  - 批处理
  - 流式支持

### 处理流程

1. **语音输入**：用户说出命令
2. **语音识别**：Whisper 将音频转换为文本
3. **意图分类**：规则引擎确定意图和风险等级
4. **路由决策**：
   - 高风险 → 阻止并说明
   - 需要确认 → 要求用户确认
   - 安全操作 → 路由到适当的处理程序：
     - 已知函数 → 函数注册表
     - 知识查询 → RAG 模块
     - 通用查询 → LLM
5. **执行**：选定的组件处理请求
6. **响应生成**：结果转换为语音（TTS - 开发中）

## 架构

系统遵循模块化架构，具有明确的关注点分离：

1. **语音处理管道**：使用 Whisper 将语音转换为文本
2. **语言模型集成**：使用多个 LLM 后端处理文本（PyTorch、VLLM、llama.cpp）
3. **意图分类与路由**：分类用户意图并路由到适当的处理程序
4. **函数注册系统**：动态注册和执行函数
5. **RAG 模块**：使用 ChromaDB 对知识库进行语义搜索

## 安装

```bash
pip install -r requirements_onnx.txt
```

## 使用方法

### 运行测试
```bash
# 测试聊天机器人功能
cd ChatBots && python run_chatbot_tests.py

# 测试完整系统集成
cd SystemTest && python test_full_api_integration.py

# 测试 RAG 功能
cd SystemTest && python run_rag_tests.py
```

### 使用示例

```python
# 初始化组件
from rule_engine import RuleEngine
from function_registry import FunctionRegistry
from rag import RAG

# 处理语音命令
engine = RuleEngine("Rules.json")
registry = FunctionRegistry(verbose=True)
rag = RAG()

# 示例流程
user_input = "打开空调"  # 来自 Whisper STT
intent, action = engine.process_input(user_input)

if intent == "LLM":
    # 路由到 LLM 处理通用查询
    response = chat_bot.process(user_input)
elif action == "直接放行":
    # 通过函数注册表执行
    result = registry.execute("window_control", action="open")
elif action == "需二次确认":
    # 要求用户确认
    confirm = ask_confirmation(user_input)
```

## 项目状态

**注意：该项目目前正在积极开发中，尚未完成。**

### 即将推出的功能（下周）

1. **管道实现**：完成 STT（语音转文字）、LLM 和 TTS（文字转语音）组件的统一管道集成
2. **优化方法**：实现模型的 8 位量化以减少内存使用并提高性能
3. **模型管理**：从硬编码的模型配置过渡到基于 JSON 的模型管理系统

## 技术栈

- **Python** 作为主要语言
- **PyTorch** 用于深度学习
- **Transformers**（Hugging Face）用于 LLM 管理
- **ChromaDB** 用于向量数据库（RAG）
- **ONNX Runtime** 用于模型优化
- **Whisper** 用于语音转文字
- **Qwen3** 和 **Phi-4** 模型用于语言理解

## 许可证

[许可证信息待添加]