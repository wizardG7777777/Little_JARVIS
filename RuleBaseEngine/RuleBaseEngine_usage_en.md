# Rule Engine 使用说明

## 1. 概述

Rule Engine 是一个基于规则的用户意图识别引擎，可根据预定义的规则文件（Rules.json）解析用户输入，判断用户意图并返回相应的处理建议。该引擎设计为一个独立的Python模块，可以集成到更大的系统中作为意图路由的决策组件。

## 2. 初始化与调用方式

### 2.1 初始化引擎

```python
from rule_engine import RuleEngine

# 初始化引擎，传入规则文件路径
engine = RuleEngine("path/to/Rules.json")
```

### 2.2 基本调用方式

```python
# 处理用户输入
result = engine.process_input("打开空调")
intent, action = result  # 解构返回的元组
```

### 2.3 风险等级映射更新

引擎维护了一个风险等级（L1-L5）到具体操作的映射字典，可以在运行时更新：

```python
# 更新风险等级映射
engine.update_risk_mapping({
    "L3": "高危禁止",  # 将L3从"需二次确认"改为"高危禁止"
    "L4": "需二次确认"  # 将L4从"直接放行"改为"需二次确认"
})
```

## 3. 接受的输入

### 3.1 输入类型

引擎只接受**字符串**作为输入，代表用户的原始请求文本。

```python
engine.process_input("查看当前车速")
```

### 3.2 输入示例

以下是不同类型的有效输入示例：

- 设备控制类：
  ```
  "打开空调"
  "关闭车窗"
  "调整座椅到高档"
  ```

- 信息查询类：
  ```
  "查看当前车速"
  "显示电量"
  "剩余续航多少"
  ```

- 日常对话类：
  ```
  "你好"
  "讲个笑话"
  ```

- 复杂命令类：
  ```
  "打开空调然后调低温度"
  "停止所有操作"
  ```

## 4. 返回值格式及意义

### 4.1 返回值格式

引擎的`process_input`方法返回一个**二元组**：

```python
(intent_type, action)
```

### 4.2 返回值详解

#### 4.2.1 第一个元素：`intent_type`

`intent_type`是一个字符串，表示引擎识别出的用户意图类型，可能的值包括：

- `"device_control"`：设备控制意图
- `"info_query"`：信息查询意图
- `"daily_chat"`：日常对话意图
- `"complex_command"`：复杂命令意图
- `"system_app_launch"`：应用启动意图
- `"system_file_access"`：文件访问意图
- `"system_web_service"`：网络服务意图
- `"dialogue_context_rules"`：对话上下文管理
- `"dialogue_termination_rules"`：对话终止指令
- `"LLM"`：无法识别的意图，需交由LLM处理

#### 4.2.2 第二个元素：`action`

`action`是一个字符串，表示基于风险等级应采取的具体操作，可能的值包括：

- `"高危禁止"`：表示该操作风险极高，系统应拒绝执行
- `"需二次确认"`：表示该操作需要用户进一步确认后才能执行
- `"直接放行"`：表示该操作风险较低，系统可以直接执行
- `"leave to chat_bot"`：特殊值，仅当`intent_type`为`"LLM"`时出现，表示该请求应交由聊天机器人处理

### 4.3 特殊返回值

当引擎无法识别用户意图时，会返回特殊的元组：

```python
("LLM", "leave to chat_bot")
```

这表示当前用户请求无法通过规则引擎处理，需要路由给大语言模型（LLM）进行处理。

## 5. 使用示例

### 5.1 基本使用流程

```python
from rule_engine import RuleEngine

# 初始化引擎
engine = RuleEngine("Rules.json")

# 处理用户输入
user_input = "打开空调"
intent, action = engine.process_input(user_input)

# 根据返回结果进行路由
if intent == "LLM":
    # 交由LLM处理
    chat_bot_response = call_llm_api(user_input)
    print(chat_bot_response)
else:
    # 根据识别的意图和操作建议处理
    if action == "直接放行":
        execute_command(intent, user_input)
    elif action == "需二次确认":
        confirmation = ask_user_confirmation(intent, user_input)
        if confirmation:
            execute_command(intent, user_input)
    elif action == "高危禁止":
        show_warning(intent, user_input)
```

### 5.2 完整路由示例

```python
def process_user_request(user_input):
    # 使用规则引擎处理输入
    intent, action = engine.process_input(user_input)
    
    # 路由逻辑
    if intent == "LLM":
        return process_with_llm(user_input)
    else:
        return process_with_rule_based_system(intent, action, user_input)

def process_with_rule_based_system(intent, action, user_input):
    if action == "高危禁止":
        return {
            "response_type": "warning",
            "message": f"无法执行该操作，因为它属于高风险类别：{user_input}"
        }
    elif action == "需二次确认":
        return {
            "response_type": "confirmation",
            "intent": intent,
            "original_input": user_input,
            "message": f"请确认是否要执行：{user_input}"
        }
    elif action == "直接放行":
        result = execute_intent(intent, user_input)
        return {
            "response_type": "success",
            "result": result,
            "message": f"已执行操作：{user_input}"
        }

def process_with_llm(user_input):
    llm_response = call_llm_api(user_input)
    return {
        "response_type": "llm",
        "message": llm_response
    }
```

## 6. 风险等级映射

引擎默认的风险等级映射如下：

| 风险等级 | 操作建议 |
|---------|---------|
| L1      | 高危禁止 |
| L2      | 需二次确认 |
| L3      | 需二次确认 |
| L4      | 直接放行 |
| L5      | 直接放行 |

可以使用`update_risk_mapping`方法根据实际需求调整此映射。

## 7. 注意事项

1. 确保Rules.json文件格式正确，否则引擎初始化可能失败
2. 处理复杂意图时，引擎会根据优先级（priority）选择最匹配的规则
3. 风险等级映射可以在运行时动态调整，适应不同场景的安全需求
4. 当无法识别用户意图时，应将请求路由给LLM处理，以提供更好的用户体验

---

通过以上使用说明，您应该能够顺利集成和使用规则引擎来处理用户请求，实现基于规则的意图识别和风险评估功能。