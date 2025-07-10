# ChatBots 模块使用说明

## 概述

ChatBots 模块是 Little_JARVIS 项目的核心对话组件，提供了统一的聊天机器人接口，支持本地大语言模型推理、云端API调用和函数调用路由等功能。

## 模块结构

```
ChatBots/
├── LocalChatBot.py          # 本地聊天机器人核心类
├── CloudChatBot.py          # 云端聊天机器人接口
├── FunctionCalling_router.py # 函数调用路由器
├── chatbot_calling.py       # 调用模板和示例
├── qwen_runnable.py         # Qwen模型运行器
├── test_chatbot_responses.py # 聊天机器人测试框架
├── run_chatbot_tests.py     # 测试运行器
└── 使用说明.md              # 本文档
```

## 核心功能

### 1. LocalChatBot - 本地大语言模型

#### 基本使用

```python
from ChatBots.LocalChatBot import LocalChatBot, load_prompt
from pathlib import Path

# 初始化模型
model_path = Path("models/llm/Qwen3-1.7B")
chatbot = LocalChatBot(model_path=str(model_path))

# 单次对话
response = chatbot.invoke("你好，请介绍一下你自己")
print(f"回复: {response['content']}")
print(f"思考过程: {response['thinking']}")
```

#### 启用思维链模式

```python
# 创建配置，启用思维链
config = {"thinking": True, "max_tokens": 512}

# 标准消息格式
messages = [
    {"role": "system", "content": "你是一个有用的AI助手"},
    {"role": "user", "content": "现在是下午3点25分，90分钟后是几点？"}
]

# 调用模型
result = chatbot.invoke({"messages": messages}, config=config)
print(f"思考过程: {result['thinking']}")
print(f"最终回答: {result['content']}")
```

#### 批量处理

```python
# 准备多个输入
inputs = [
    "今天天气怎么样？",
    "推荐一些杭州的景点",
    "如何制作红烧肉？"
]

# 批量处理配置
batch_config = {
    "thinking": True,
    "max_tokens": 256,
    "batch_size": 2  # 每批处理2个输入
}

# 执行批量处理
results = chatbot.batch(inputs, config=batch_config)

for i, result in enumerate(results):
    print(f"问题 {i+1}: {inputs[i]}")
    print(f"回答: {result['content']}")
    print(f"思考: {result['thinking']}")
    print("-" * 50)
```

#### 流式输出

```python
# 流式生成回复
for chunk in chatbot.stream("请详细介绍人工智能的发展历史"):
    if chunk["thinking"]:
        print(f"思考中: {chunk['thinking']}")
    if chunk["content"]:
        print(f"回复: {chunk['content']}")
```

### 2. 系统提示词管理

#### 加载预设提示词

```python
from ChatBots.LocalChatBot import load_prompt

# 加载日常对话提示词
daily_prompt = load_prompt("daily_chat")
print(f"系统提示词: {daily_prompt}")

# 支持的提示词类型
prompt_types = [
    "device_control",      # 设备控制
    "info_query",         # 信息查询
    "daily_chat",         # 日常对话
    "complex_command",    # 复杂指令
    "system_app_launch",  # 应用启动
    "system_file_access", # 文件访问
    "system_web_service", # 网络服务
]
```

### 3. 便捷调用函数

#### 使用 chatbot_calling.py

```python
from chatbot_calling import call_local

# 简单调用（不启用思维链）
thinking, response = call_local("你好，今天天气如何？")
print(f"回复: {response}")

# 启用思维链模式
thinking, response = call_local(
    user_query="感冒了应该喝姜茶还是冰咖啡？", 
    enable_thinking=True
)
print(f"思考过程: {thinking}")
print(f"建议: {response}")
```

## 配置参数说明

### LocalChatBot 配置选项

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `thinking` | bool | False | 是否启用思维链模式 |
| `max_tokens` | int | 512 | 最大生成token数量 |
| `batch_size` | int | 输入长度 | 批处理时每批的大小 |

### 模型初始化参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `model_path` | str | 模型文件路径（必需） |
| `device` | str | 计算设备（默认：cuda） |

## 测试框架使用

### 运行完整测试

```bash
# 进入ChatBots目录
cd ChatBots

# 运行所有测试
python run_chatbot_tests.py

# 或直接运行测试文件
python test_chatbot_responses.py
```

### 自定义测试

```python
from test_chatbot_responses import ChatBotTester

# 创建测试器
tester = ChatBotTester()

# 添加自定义测试用例
custom_test = {
    "id": 11,
    "category": "custom_test",
    "question": "你的自定义问题",
    "expected_type": "自定义类型",
    "evaluation_criteria": "评估标准"
}

tester.test_cases.append(custom_test)

# 运行测试
tester.run_all_tests()
tester.generate_markdown_report("custom_test_results.md")
```

## 错误处理和故障排除

### 常见问题

#### 1. 模型加载失败
```python
# 检查模型路径
import os
model_path = "models/llm/Qwen3-1.7B"
if not os.path.exists(model_path):
    print(f"模型路径不存在: {model_path}")
```

#### 2. CUDA内存不足
```python
# 使用较小的批处理大小
config = {"batch_size": 1, "max_tokens": 256}
results = chatbot.batch(inputs, config=config)
```

#### 3. 依赖库缺失
```bash
# 安装必需的依赖
pip install torch transformers accelerate
```

### 错误代码说明

| 错误类型 | 原因 | 解决方案 |
|----------|------|----------|
| `FileNotFoundError` | 模型路径不存在 | 检查并修正模型路径 |
| `CUDA out of memory` | GPU内存不足 | 减少batch_size或max_tokens |
| `ImportError` | 缺少依赖库 | 安装相应的Python包 |

## 性能优化建议

### 1. 批处理优化
- 对于多个相似长度的输入，使用批处理可以显著提高效率
- 根据GPU内存调整 `batch_size` 参数
- 较长的输入建议使用较小的批处理大小

### 2. 内存管理
- 定期清理不需要的变量
- 使用 `torch.no_grad()` 上下文管理器
- 避免在循环中重复加载模型

### 3. 推理加速
- 使用量化模型减少内存占用
- 启用 `use_cache=True` 加速生成
- 考虑使用 TensorRT 进行推理优化

## 集成示例

### 与规则引擎集成

```python
from RuleBaseEngine.RuleBaseEngine import RuleEngine
from ChatBots.LocalChatBot import LocalChatBot

# 初始化组件
rule_engine = RuleEngine("Rules.json")
chatbot = LocalChatBot("models/llm/Qwen3-1.7B")

def process_user_input(user_input):
    # 先通过规则引擎处理
    intent, action = rule_engine.process_input(user_input)
    
    if intent == "LLM":
        # 交给聊天机器人处理
        result = chatbot.invoke(user_input, {"thinking": True})
        return result["content"]
    else:
        # 执行规则引擎的动作
        return f"执行动作: {action}"
```

### 与函数调用集成

```python
from ChatBots.FunctionCalling_router import FunctionRouter

# 创建函数路由器
router = FunctionRouter()

def enhanced_chat(user_input):
    # 检查是否需要函数调用
    if router.needs_function_call(user_input):
        return router.execute_function(user_input)
    else:
        # 普通对话
        return chatbot.invoke(user_input)["content"]
```

## 最佳实践

1. **模型预热**: 首次使用时进行一次简单推理以预热模型
2. **配置管理**: 将常用配置保存为预设，避免重复设置
3. **日志记录**: 记录重要的对话和错误信息用于调试
4. **资源监控**: 监控GPU内存和CPU使用情况
5. **版本控制**: 记录模型版本和配置变更

## 更新日志

- **v1.0**: 初始版本，支持基本对话功能
- **v1.1**: 添加思维链模式支持
- **v1.2**: 实现批处理功能
- **v1.3**: 完善错误处理和测试框架

## 技术支持

如遇到问题，请检查：
1. 模型文件是否完整
2. 依赖库版本是否兼容
3. 系统资源是否充足
4. 配置参数是否正确

更多技术细节请参考源代码注释和测试用例。

# Update
## 任务
不修改LocalChatBot.py的调用逻辑的前提下，完成以下任务
### 修复batch
在不使用新的库的前提下，修复batch函数中存在的错误和警告，建议使用列表承载user query 
### API 路由
在FunctionCalling_router.py中实现一个方法，要求按照registry.json中的内容执行函数调用
### 模拟函数调用
在SystemTest文件夹内编写一个假API调用类，要求仅编写和registry.json内部所有的方法同名的API，其内部不执行任何逻辑，仅判断传入参数的类型是否合规
### API调用逻辑及测试
用户输入 -> IntentRouter -> RuleBaseEngine -> IntentRouter -> LocalChatBot -> FunctionCalling_router -> API
请在SystemTest内部使用unit test编写一个测试文件，完成用户输入到API调用的测试，要求尽量不修改RuleBaseEngine和LocalChatBot内部的逻辑