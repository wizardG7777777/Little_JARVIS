# API 注册程序使用说明

## 概述
`FunctionRegistry` 是一个强大的 API 注册管理工具，用于统一注册和管理不同来源的 API 函数（静态函数、插件函数、第三方 API）。主要功能包括：
- 统一注册管理三类 API：静态函数、插件函数、第三方 API
- 自动生成函数参数模式（JSON Schema）
- 记录 API 调用历史和执行统计
- 支持注册表持久化（JSON 文件）
- 提供完整的 API 文档导出功能

## 快速开始

### 安装依赖
```python
pip install typing_extensions
```

### 初始化注册表
```python
from function_registry import FunctionRegistry, FunctionType

# 创建注册表实例
registry = FunctionRegistry(
    verbose=True,              # 启用详细日志
    json_registry_path="my_registry.json"  # 注册表保存路径
)
```

---

## 核心功能使用指南

### 1. 注册 API 函数

#### 1.1 注册静态函数（核心应用函数）
```python
def my_function(param1: str, param2: int):
    return {"result": param1 * param2}

registry.register_static(
    name="my_function",        # 唯一函数标识
    func=my_function,          # 函数对象
    description="示例静态函数",  # 功能描述
    override=False             # 是否覆盖同名函数
)
```

#### 1.2 注册插件函数
```python
registry.register_plugin(
    name="data_processing",    # 函数名
    func=data_processor,       # 函数对象
    plugin_name="analytics",   # 插件名称
    description="数据分析插件"
)
# 完整函数名: analytics.data_processing
```

#### 1.3 注册第三方 API
```python
registry.register_third_party(
    name="payment",            # API 名称
    func=payment_api,          # API 调用函数
    app_name="stripe",         # 第三方应用名
    description="支付接口"
)
# 完整函数名: stripe.payment
```

#### 1.4 批量注册
```python
functions = [
    {
        "type": "static",
        "name": "func1",
        "func": function1,
        "description": "功能1"
    },
    {
        "type": "plugin",
        "name": "tool",
        "func": plugin_tool,
        "plugin_name": "utils",
        "description": "工具函数"
    }
]

results = registry.register_batch(functions)
```

### 2. 执行 API 函数
```python
# 执行已注册的函数
result = registry.execute(
    function_name="stripe.payment",  # 完整函数名
    amount=100.00,                  # 命名参数
    currency="USD"
)

print(f"执行结果: {result}")
```

### 3. 管理注册表

#### 3.1 获取函数信息
```python
info = registry.get_function_info("analytics.data_processing")
print(f"函数描述: {info['description']}")
print(f"参数模式: {info['parameters']}")
```

#### 3.2 列出所有函数
```python
# 列出所有函数
all_functions = registry.list_functions()

# 按类型筛选
plugin_functions = registry.list_functions(FunctionType.PLUGIN)
third_party_functions = registry.list_functions("third_party")  # 支持字符串类型
```

#### 3.3 注销函数
```python
success = registry.unregister("obsolete.function")
if success:
    print("函数注销成功")
```

### 4. 持久化操作

#### 4.1 保存注册表到 JSON
```python
registry.save_to_json()  # 使用初始化路径
registry.save_to_json("backup.json")  # 自定义路径
```

#### 4.2 从 JSON 加载注册表
```python
registry.load_from_json("backup.json")  # 只加载元数据，不包含函数实现
```

### 5. 导出 API 文档
```python
# 导出基本模式
schema = registry.export_function_schema()

# 包含调用历史
full_schema = registry.export_function_schema(include_call_history=True)

# 保存为文档
with open("api_documentation.json", "w") as f:
    json.dump(full_schema, f, indent=2)
```

---

## 高级功能

### 自定义参数模式
```python
registry.register_static(
    name="advanced_api",
    func=my_api,
    parameter_schema={
        "type": "object",
        "properties": {
            "input": {"type": "string", "maxLength": 100},
            "options": {
                "type": "array",
                "items": {"type": "string"}
            }
        },
        "required": ["input"]
    }
)
```

### 自动参数推断
当不提供 `parameter_schema` 时，系统会自动从函数签名生成：
```python
def auto_params(name: str, age: int, active: bool = True):
    pass

# 自动生成参数模式：
# {
#   "type": "object",
#   "properties": {
#       "name": {"type": "string"},
#       "age": {"type": "integer"},
#       "active": {"type": "boolean"}
#   },
#   "required": ["name", "age"]
# }
```

---

## 使用示例
```python
# 创建注册表
registry = FunctionRegistry(verbose=True)

# 注册车辆控制API
registry.register_static(
    name="window_control",
    func=control_window,
    description="控制车窗开合"
)

# 注册天气插件
registry.register_plugin(
    name="get_forecast",
    func=weather_plugin,
    plugin_name="weather",
    description="获取天气预报"
)

# 执行API
registry.execute("window_control", position="driver", action="open")
registry.execute("weather.get_forecast", location="Beijing")

# 导出文档
with open("api_docs.json", "w") as f:
    json.dump(registry.export_function_schema(), f, indent=2)
```

---

## 注意事项
1. **函数命名规范**：
   - 静态函数：直接使用功能名 (`window_control`)
   - 插件函数：`<插件名>.<功能名>` (`weather.get_forecast`)
   - 第三方API：`<应用名>.<功能名>` (`stripe.payment`)

2. **参数传递**：
   - 必须使用命名参数方式调用 `execute()`
   - 参数名称需完全匹配注册时的定义

3. **错误处理**：
   - 注册失败会返回 `False` 并输出详细错误日志
   - 执行失败会返回 `None` 并记录错误

4. **性能考虑**：
   - 调用历史默认保留最近10次调用
   - 大量注册建议使用 `register_batch()`

5. **安全提示**：
   - 加载 JSON 注册表时不执行函数验证
   - 生产环境应禁用 `verbose` 模式

通过此注册表，您可以统一管理系统中的所有 API 接口，实现高效的路由调用和全面的使用监控。