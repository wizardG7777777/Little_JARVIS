# Function Registry User Manual

## Table of Contents
- [Introduction](#introduction)
- [Installation](#installation)
- [Basic Usage](#basic-usage)
- [Registering Functions](#registering-functions)
  - [Static Functions](#static-functions)
  - [Plugin Functions](#plugin-functions)
  - [Third-Party Functions](#third-party-functions)
  - [Batch Registration](#batch-registration)
- [Executing Functions](#executing-functions)
- [Managing the Registry](#managing-the-registry)
  - [Listing Functions](#listing-functions)
  - [Getting Function Information](#getting-function-information)
  - [Unregistering Functions](#unregistering-functions)
- [JSON Registry](#json-registry)
  - [Saving Registry to JSON](#saving-registry-to-json)
  - [Loading Registry from JSON](#loading-registry-from-json)
- [Advanced Features](#advanced-features)
  - [Auto-generating Parameter Schemas](#auto-generating-parameter-schemas)
  - [Call History and Statistics](#call-history-and-statistics)
  - [Exporting Function Schema](#exporting-function-schema)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

## Introduction

The Function Registry is a Python utility that helps manage function calls from natural language commands. It supports:

- Registration of static, plugin, and third-party functions
- Parameter validation through JSON schemas
- Call history tracking and statistics
- JSON export and import capabilities

This tool is particularly useful for applications with natural language interfaces, chatbots, and AI assistants.

## Installation

No installation is required beyond the standard Python library. Simply include `function_registry.py` in your project.

```python
from function_registry import FunctionRegistry, FunctionType
```

## Basic Usage

Initialize a new registry:

```python
# Create a registry with verbose logging and custom JSON path
registry = FunctionRegistry(verbose=True, json_registry_path="my_registry.json")

# Create a simple registry with default settings
registry = FunctionRegistry()
```

## Registering Functions

### Static Functions

Static functions are part of your core application:

```python
def my_function(param1: str, param2: int = 0):
    return f"Processed {param1} with value {param2}"

# Register with auto-generated parameter schema
registry.register_static(
    name="my_function",
    func=my_function,
    description="Process data with parameters"
)

# Register with custom parameter schema
registry.register_static(
    name="my_function", 
    func=my_function,
    parameter_schema={
        "type": "object",
        "properties": {
            "param1": {"type": "string", "description": "First parameter"},
            "param2": {"type": "integer", "description": "Optional second parameter"}
        },
        "required": ["param1"]
    },
    description="Process data with parameters"
)
```

### Plugin Functions

Plugin functions extend your application's functionality:

```python
def weather_search(location: str, days: int = 5):
    # Implementation
    return {"forecast": f"Weather for {location} for {days} days"}

registry.register_plugin(
    name="search",
    func=weather_search,
    plugin_name="weather",
    description="Search for weather information"
)
# Registered as "weather.search"
```

### Third-Party Functions

Third-party functions integrate external applications:

```python
def play_music(song_name: str, artist: str = None):
    # Implementation to play music
    return {"status": "playing", "song": song_name}

registry.register_third_party(
    name="play",
    func=play_music,
    app_name="spotify",
    description="Play music on Spotify"
)
# Registered as "spotify.play"
```

### Batch Registration

Register multiple functions at once:

```python
registry.register_batch([
    {
        "name": "function1",
        "func": my_function1,
        "type": "static",
        "description": "First function"
    },
    {
        "name": "function2",
        "func": my_function2,
        "type": "plugin",
        "plugin_name": "tools",
        "description": "Second function"
    }
])
```

## Executing Functions

Execute a registered function by name:

```python
# Execute a static function
result = registry.execute("my_function", param1="hello", param2=42)

# Execute a plugin function
result = registry.execute("weather.search", location="New York")

# Execute a third-party function
result = registry.execute("spotify.play", song_name="Bohemian Rhapsody")
```

## Managing the Registry

### Listing Functions

List all registered functions or filter by type:

```python
# List all functions
all_functions = registry.list_functions()

# List only static functions
static_functions = registry.list_functions(FunctionType.STATIC)

# List by type as string
plugin_functions = registry.list_functions("plugin")
```

### Getting Function Information

Get details about a specific function:

```python
function_info = registry.get_function_info("my_function")
```

### Unregistering Functions

Remove a function from the registry:

```python
registry.unregister("my_function")
```

## JSON Registry

### Saving Registry to JSON

Save the registry to a JSON file:

```python
# Save to default path (specified during initialization)
registry.save_to_json()

# Save to a custom path
registry.save_to_json("custom_registry.json")
```

### Loading Registry from JSON

Load registry metadata from a JSON file:

```python
registry.load_from_json("my_registry.json")
```

## Advanced Features

### Auto-generating Parameter Schemas

The registry can automatically generate parameter schemas from function signatures:

```python
def example_func(name: str, age: int, is_active: bool = True, data: dict = None):
    pass

# The registry will analyze the signature and create an appropriate schema
registry.register_static("example_func", example_func)
```

### Call History and Statistics

Track function call statistics:

```python
# Execute a function multiple times
registry.execute("my_function", param1="test")
registry.execute("my_function", param1="another_test", param2=10)

# Get function info with statistics
func_info = registry.get_function_info("my_function")
print(f"Call count: {func_info['call_count']}")
print(f"Last called: {func_info['last_called']}")
print(f"Call history: {func_info.get('call_history', [])}")
```

### Exporting Function Schema

Export the registry as a schema for documentation:

```python
# Export basic schema
schema = registry.export_function_schema()

# Export with call history
detailed_schema = registry.export_function_schema(include_call_history=True)
```

## Examples

Here's a complete example:

```python
from function_registry import FunctionRegistry

# Create registry
registry = FunctionRegistry(verbose=True)

# Define functions
def greet(name: str, formal: bool = False):
    if formal:
        return f"Good day, {name}."
    return f"Hello, {name}!"

def calculate_area(length: float, width: float):
    return length * width

# Register functions
registry.register_static("greet", greet, description="Greet a person")
registry.register_static("calculate_area", calculate_area, 
                       description="Calculate rectangle area")

# Execute functions
print(registry.execute("greet", name="Alice"))
print(registry.execute("greet", name="Mr. Smith", formal=True))
print(registry.execute("calculate_area", length=5.2, width=3.0))

# List all functions
print("\nRegistered Functions:")
for name, info in registry.list_functions().items():
    print(f"- {name}: {info['description']}")

# Save registry
registry.save_to_json("functions.json")
```

## Troubleshooting

Common issues and solutions:

| Issue | Solution |
|-------|----------|
| Function already exists | Use `override=True` when registering |
| Function not found | Check for typos in function name |
| Parameter type mismatch | Ensure parameters match the schema types |
| JSON registry not saving | Check file permissions and path |

For more assistance, enable verbose mode when creating the registry:

```python
registry = FunctionRegistry(verbose=True)
```

This will provide detailed logging information about registry operations.

---

**Note**: This manual covers the FunctionRegistry class as defined in `function_registry.py`. For additional features or custom implementations, please refer to the source code.