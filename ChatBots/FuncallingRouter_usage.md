### 🤖 Assistant



# Function Calling Interface 路由器说明书

## 概述

`function_calling_interface` 是一个动态函数调用路由器，旨在为 LLM 模组提供统一的函数调用接口。该路由器能够根据注册表文件 (`registry.json`) 中的函数信息，动态导入模块并执行函数调用。

## 主要特性

- ✅ 动态函数调用，支持从文件路径或模块名导入
- ✅ 严格的参数类型验证
- ✅ 嵌套函数调用支持（如 `weather.weather_search`）
- ✅ 统一的错误处理机制
- ✅ 函数搜索和发现功能
- ✅ 跨平台路径处理

## 安装和依赖

### 必需依赖
```bash
pip install rapidfuzz
```

### 文件结构
```
项目根目录/
├── RegistryModule/
│   ├── registry.json          # 函数注册表文件
│   └── function_registry.py   # 路由器主文件
└── 其他模块文件...
```

## 核心API

### 1. 主要调用方法

```python
def call_function(self, input_tuple) -> tuple:
    """
    执行函数调用
    
    Args:
        input_tuple: 元组，格式为 (function_name, parameters_dict)
                    function_name: 函数名称字符串
                    parameters_dict: 参数字典，键为参数名，值为参数值
    
    Returns:
        tuple: (success: bool, result: Any)
              success为True表示调用成功，False表示调用失败
              result为函数返回值或错误信息
    """
```

### 2. 辅助方法

```python
def get_available_functions(self) -> List[Dict]:
    """获取所有可用的函数列表"""

def search_functions(self, query: str, limit: int = 5) -> List[Dict]:
    """搜索函数"""
```

## 使用示例

### 基本使用

```python
from function_registry import function_calling_interface

# 创建路由器实例
router = function_calling_interface()

# 调用函数
result = router.call_function((
    "weather.weather_search", 
    {"key_word": "北京", "web_link": "https://weather.com"}
))

if result[0]:  # 调用成功
    print(f"函数执行结果: {result[1]}")
else:  # 调用失败
    print(f"调用失败: {result[1]}")
```

### 无参数函数调用

```python
result = router.call_function(("spotify.play", {}))
```

### 获取可用函数

```python
functions = router.get_available_functions()
for func in functions:
    print(f"模块: {func['module_name']}")
    print(f"函数: {func['function_name']}")
    print(f"参数: {func['parameters']}")
```

### 搜索函数

```python
results = router.search_functions("天气", limit=3)
for result in results:
    print(f"找到函数: {result['full_name']}")
```

## 错误处理机制

⚠️ **重要**: 所有由路由器判断并返回的错误信息都以 `"Router"` 开头，这是为了帮助 LLM 模组识别错误来源。

### 错误类型

| 错误类型 | 返回格式 | 描述 |
|---------|----------|------|
| 输入格式错误 | `(False, "Router: augment error - 具体错误信息")` | 输入不是元组或格式不正确 |
| 函数未找到 | `(False, "Router: funtion {func_name} not found")` | 注册表中找不到指定函数 |
| 参数错误 | `(False, "Router: augment error - 具体错误信息")` | 参数类型、数量或名称错误 |
| 执行错误 | `(False, "Router: execution error - 具体错误信息")` | 函数执行过程中出现异常 |

### 常见错误示例

```python
# 1. 函数未找到
result = router.call_function(("nonexistent_function", {}))
# 返回: (False, "Router: funtion nonexistent_function not found")

# 2. 参数类型错误
result = router.call_function(("weather.weather_search", {"key_word": 123}))
# 返回: (False, "Router: augment error - Parameter 'key_word' should be str, got int")

# 3. 缺少必需参数
result = router.call_function(("weather.weather_search", {"key_word": "北京"}))
# 返回: (False, "Router: augment error - Missing required parameters: web_link")

# 4. 多余参数
result = router.call_function(("spotify.play", {"extra_param": "value"}))
# 返回: (False, "Router: augment error - Unexpected parameters: extra_param")
```

## 支持的参数类型

| 类型字符串 | Python类型 | 示例 |
|-----------|------------|------|
| `"str"` | `str` | `"hello"` |
| `"int"` | `int` | `42` |
| `"float"` | `float` | `3.14` |
| `"bool"` | `bool` | `True` |
| `"list"` | `list` | `[1, 2, 3]` |
| `"dict"` | `dict` | `{"key": "value"}` |
| `"tuple"` | `tuple` | `(1, 2, 3)` |
| `"None"` | `NoneType` | `None` |

## 注册表格式

`registry.json` 文件格式示例：

```json
{
  "modules": [
    {
      "module_name": "weather_module",
      "module_path": "/path/to/weather_module.py",
      "functions": [
        {
          "function_name": "weather.weather_search",
          "parameters": [
            {"name": "key_word", "type": "str"},
            {"name": "web_link", "type": "str"}
          ]
        }
      ]
    }
  ]
}
```

## 高级特性

### 嵌套函数调用

路由器支持嵌套函数调用，如 `weather.weather_search`：

```python
# 注册表中的函数名可以包含点号
"function_name": "weather.weather_search"

# 调用时
result = router.call_function(("weather.weather_search", params))
```

### 动态模块导入

路由器支持两种模块导入方式：

1. **文件路径导入**: `module_path` 以 `.py` 结尾
2. **模块名导入**: `module_path` 为标准模块名

## 最佳实践

### 1. 错误处理

```python
def safe_function_call(router, func_name, params):
    result = router.call_function((func_name, params))
    
    if result[0]:
        return result[1]
    else:
        error_msg = result[1]
        if error_msg.startswith("Router: funtion"):
            # 函数未找到，建议搜索相似函数
            suggestions = router.search_functions(func_name, limit=3)
            print(f"建议的函数: {[s['full_name'] for s in suggestions]}")
        elif error_msg.startswith("Router: augment error"):
            # 参数错误，需要修正参数
            print(f"参数错误: {error_msg}")
        else:
            # 其他错误
            print(f"执行错误: {error_msg}")
        return None
```

### 2. 函数发现

```python
def find_function_info(router, func_name):
    """获取函数的详细信息"""
    functions = router.get_available_functions()
    for func in functions:
        if func['function_name'] == func_name:
            return func
    return None
```

## 注意事项

1. **路径处理**: 确保 `registry.json` 文件存在于正确的路径
2. **类型验证**: 参数类型必须与注册表中声明的类型匹配
3. **错误识别**: 所有路由器错误都以 `"Router"` 开头
4. **模块导入**: 确保被调用的模块在Python路径中或提供正确的文件路径
5. **函数命名**: 支持嵌套函数调用，使用点号分隔

## 故障排除

### 常见问题

1. **函数未找到**
   - 检查 `registry.json` 文件是否存在
   - 确认函数名称拼写正确
   - 使用 `search_functions()` 查找相似函数

2. **参数错误**
   - 检查参数类型是否匹配
   - 确认参数名称正确
   - 使用 `get_available_functions()` 查看函数签名

3. **导入错误**
   - 确认模块路径正确
   - 检查模块是否存在
   - 验证Python路径设置

## 版本兼容性

- Python 3.7+
- 依赖 `rapidfuzz` 库进行模糊搜索
- 支持 Windows 和 Unix-like 系统

