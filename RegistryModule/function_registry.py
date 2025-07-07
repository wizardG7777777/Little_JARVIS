# function_registry.py

import inspect
import json
import logging
import os
import datetime
from typing import Callable, Dict, Any, Optional, List, Union
from enum import Enum


class FunctionType(Enum):
    STATIC = "static"
    PLUGIN = "plugin"
    THIRD_PARTY = "third_party"


class FunctionRegistry:
    """
    A registry for managing function calls from natural language commands.
    Supports static functions, plugin functions, and third-party API integration.
    Can record API calls to a JSON file for documentation and monitoring.
    """

    def __init__(self, verbose: bool = False, json_registry_path: str = "registry.json"):
        self.functions = {}
        self.verbose = verbose
        self.logger = self._setup_logger()
        self.json_registry_path = json_registry_path
        self.module_info = {}  # Track module paths and information
        self._load_registry_if_exists()

    def _setup_logger(self):
        """Set up a logger for the registry"""
        logger = logging.getLogger("FunctionRegistry")
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO if self.verbose else logging.WARNING)
        return logger

    def _load_registry_if_exists(self):
        """Load existing registry from JSON file if it exists"""
        if os.path.exists(self.json_registry_path):
            try:
                self.load_from_json(self.json_registry_path)
                self.logger.info(f"Loaded existing registry from {self.json_registry_path}")
            except Exception as e:
                self.logger.warning(f"Failed to load registry: {str(e)}")

    def register(self,
                 name: str,
                 func: Callable,
                 parameter_schema: Optional[Dict] = None,
                 function_type: FunctionType = FunctionType.STATIC,
                 description: str = "",
                 override: bool = False,
                 module_path: str = None) -> bool:
        """
        Register a function with the registry.

        Args:
            name: Unique identifier for the function
            func: The callable function to register
            parameter_schema: JSON schema describing the function parameters
            function_type: Type of function (static, plugin, third-party)
            description: Human-readable description of what the function does
            override: Whether to override an existing function with the same name
            module_path: Path to the module containing the function (for JSON tracking)

        Returns:
            bool: True if registration was successful, False otherwise
        """
        try:
            # Check if function already exists
            if name in self.functions and not override:
                return self._handle_error(
                    f"Function '{name}' already exists. Use override=True to replace it.",
                    show_example=True
                )

            # Validate the function is callable
            if not callable(func):
                return self._handle_error(
                    f"Provided object for '{name}' is not callable.",
                    show_example=True
                )

            # Auto-generate parameter schema if none provided
            if parameter_schema is None:
                parameter_schema = self._generate_parameter_schema(func)

            # Get module path if not provided
            if module_path is None:
                try:
                    module_path = inspect.getmodule(func).__file__
                except (AttributeError, TypeError):
                    module_path = "unknown_module_path"

            # Extract module name from path
            module_name = os.path.basename(module_path).replace(".py", "") if module_path else "unknown_module"

            # Register the function
            self.functions[name] = {
                "function": func,
                "parameters": parameter_schema,
                "type": function_type.value,
                "description": description,
                "module_path": module_path,
                "module_name": module_name,
                "call_count": 0,
                "last_called": None
            }

            # Update module info for JSON tracking
            if module_name not in self.module_info:
                self.module_info[module_name] = {
                    "module_path": module_path,
                    "functions": {}
                }

            # Store parameter info in format matching Registration.json
            param_info = []
            for param_name, param_details in parameter_schema.get("properties", {}).items():
                param_type = param_details.get("type", "string")
                # Convert JSON schema types to Python types
                type_mapping = {
                    "string": "str",
                    "integer": "int",
                    "number": "float",
                    "boolean": "bool",
                    "array": "list",
                    "object": "dict"
                }
                py_type = type_mapping.get(param_type, param_type)
                param_info.append({"name": param_name, "type": py_type})

            self.module_info[module_name]["functions"][name] = {
                "function_name": name,
                "parameters": param_info
            }

            self.logger.info(f"Successfully registered {function_type.value} function: {name}")

            # Save updated registry to JSON
            self.save_to_json()

            return True

        except Exception as e:
            return self._handle_error(f"Error registering function '{name}': {str(e)}")

    def register_static(self,
                        name: str,
                        func: Callable,
                        parameter_schema: Optional[Dict] = None,
                        description: str = "",
                        override: bool = False,
                        module_path: str = None) -> bool:
        """Register a static function that's part of the core application."""
        return self.register(
            name=name,
            func=func,
            parameter_schema=parameter_schema,
            function_type=FunctionType.STATIC,
            description=description,
            override=override,
            module_path=module_path
        )

    def register_plugin(self,
                        name: str,
                        func: Callable,
                        parameter_schema: Optional[Dict] = None,
                        description: str = "",
                        plugin_name: str = "",
                        override: bool = False,
                        module_path: str = None) -> bool:
        """Register a function from a plugin."""
        full_name = f"{plugin_name}.{name}" if plugin_name else name
        return self.register(
            name=full_name,
            func=func,
            parameter_schema=parameter_schema,
            function_type=FunctionType.PLUGIN,
            description=description,
            override=override,
            module_path=module_path
        )

    def register_third_party(self,
                             name: str,
                             func: Callable,
                             parameter_schema: Optional[Dict] = None,
                             description: str = "",
                             app_name: str = "",
                             override: bool = False,
                             module_path: str = None) -> bool:
        """Register a function from a third-party application."""
        full_name = f"{app_name}.{name}" if app_name else name
        return self.register(
            name=full_name,
            func=func,
            parameter_schema=parameter_schema,
            function_type=FunctionType.THIRD_PARTY,
            description=description,
            override=override,
            module_path=module_path
        )

    def register_batch(self, functions: List[Dict]) -> Dict[str, bool]:
        """
        Register multiple functions at once.

        Args:
            functions: List of dictionaries containing function registration info

        Returns:
            Dictionary mapping function names to registration success/failure
        """
        results = {}
        for func_info in functions:
            name = func_info.get("name")
            if not name:
                self._handle_error("Missing function name in batch registration")
                continue

            # Create a copy of func_info without the 'type' key for method calls
            func_info_copy = func_info.copy()
            func_type = func_info_copy.pop("type", "static")

            if func_type == "static" or func_type == FunctionType.STATIC:
                success = self.register_static(**func_info_copy)
            elif func_type == "plugin" or func_type == FunctionType.PLUGIN:
                success = self.register_plugin(**func_info_copy)
            elif func_type == "third_party" or func_type == FunctionType.THIRD_PARTY:
                success = self.register_third_party(**func_info_copy)
            else:
                success = False
                self._handle_error(f"Unknown function type: {func_type}")

            results[name] = success

        return results

    def execute(self, function_name: str, **kwargs) -> Any:
        """
        Execute a registered function with the provided parameters and record the call.

        Args:
            function_name: Name of the function to execute
            **kwargs: Parameters to pass to the function

        Returns:
            The result of the function execution
        """
        if function_name not in self.functions:
            self._handle_error(f"Function '{function_name}' not found in registry.")
            return None

        try:
            # Update call statistics
            self.functions[function_name]["call_count"] += 1
            self.functions[function_name]["last_called"] = datetime.datetime.now().isoformat()

            # Record this API call
            self._record_api_call(function_name, kwargs)

            # Execute the function
            func = self.functions[function_name]["function"]
            result = func(**kwargs)

            # Save updated registry to JSON after successful execution
            self.save_to_json()

            return result
        except Exception as e:
            self._handle_error(f"Error executing function '{function_name}': {str(e)}")
            return None

    def _record_api_call(self, function_name: str, parameters: Dict[str, Any]) -> None:
        """
        Record an API call for tracking purposes.

        Args:
            function_name: Name of the called function
            parameters: Parameters passed to the function
        """
        function_info = self.functions.get(function_name)
        if not function_info:
            return

        # Store API call record
        if "call_history" not in function_info:
            function_info["call_history"] = []

        # Limit history to 10 most recent calls to avoid excessive storage
        if len(function_info["call_history"]) >= 10:
            function_info["call_history"].pop(0)

        function_info["call_history"].append({
            "timestamp": datetime.datetime.now().isoformat(),
            "parameters": parameters
        })

    def get_function_info(self, function_name: str) -> Optional[Dict]:
        """
        Get information about a registered function.

        Args:
            function_name: Name of the function

        Returns:
            Dictionary with function information or None if not found
        """
        return self.functions.get(function_name)

    def list_functions(self, function_type: Optional[Union[FunctionType, str]] = None) -> Dict[str, Dict]:
        """
        List all registered functions, optionally filtered by type.

        Args:
            function_type: Type of functions to list (None for all)

        Returns:
            Dictionary of function information
        """
        if function_type is None:
            return {name: {k: v for k, v in info.items() if k != 'function'}
                    for name, info in self.functions.items()}

        # Handle string type for convenience
        if isinstance(function_type, str):
            type_value = function_type
        else:
            type_value = function_type.value

        return {
            name: {k: v for k, v in info.items() if k != 'function'}
            for name, info in self.functions.items()
            if info["type"] == type_value
        }

    def unregister(self, function_name: str) -> bool:
        """
        Remove a function from the registry.

        Args:
            function_name: Name of the function to remove

        Returns:
            True if successful, False otherwise
        """
        if function_name not in self.functions:
            return self._handle_error(f"Cannot unregister: Function '{function_name}' not found.")

        # Remove from module info
        function_info = self.functions[function_name]
        module_name = function_info.get("module_name")
        if module_name in self.module_info and function_name in self.module_info[module_name]["functions"]:
            del self.module_info[module_name]["functions"][function_name]

            # Remove module if it has no functions
            if not self.module_info[module_name]["functions"]:
                del self.module_info[module_name]

        # Remove from functions dict
        del self.functions[function_name]

        # Save updated registry to JSON
        self.save_to_json()

        self.logger.info(f"Unregistered function: {function_name}")
        return True

    def _generate_parameter_schema(self, func: Callable) -> Dict:
        """
        Automatically generate a parameter schema from function signature.

        Args:
            func: The function to analyze

        Returns:
            Parameter schema dictionary
        """
        sig = inspect.signature(func)
        schema = {
            "type": "object",
            "properties": {},
            "required": []
        }

        for param_name, param in sig.parameters.items():
            # Skip self parameter for methods
            if param_name == "self":
                continue

            param_type = "string"  # Default type
            if param.annotation != inspect.Parameter.empty:
                if param.annotation == int:
                    param_type = "integer"
                elif param.annotation == float:
                    param_type = "number"
                elif param.annotation == bool:
                    param_type = "boolean"
                elif param.annotation == list or param.annotation == List:
                    param_type = "array"
                elif param.annotation == dict or param.annotation == Dict:
                    param_type = "object"

            schema["properties"][param_name] = {"type": param_type}

            # Add to required parameters if no default value
            if param.default == inspect.Parameter.empty:
                schema["required"].append(param_name)

        return schema

    def save_to_json(self, filepath: str = None) -> bool:
        """
        Save the registry to a JSON file.

        Args:
            filepath: Path to the JSON file (uses default if None)

        Returns:
            True if successful, False otherwise
        """
        try:
            if filepath is None:
                filepath = self.json_registry_path

            # Convert registry to JSON-compatible format
            registry_data = {
                "modules": []
            }

            for module_name, module_data in self.module_info.items():
                module_entry = {
                    "module_name": module_name,
                    "module_path": module_data["module_path"],
                    "functions": []
                }

                for func_name, func_data in module_data["functions"].items():
                    module_entry["functions"].append(func_data)

                registry_data["modules"].append(module_entry)

            # Write to file with pretty formatting
            with open(filepath, 'w') as f:
                json.dump(registry_data, f, indent=2)

            self.logger.info(f"Registry saved to {filepath}")
            return True

        except Exception as e:
            self.logger.error(f"Error saving registry to JSON: {str(e)}")
            return False

    def load_from_json(self, filepath: str) -> bool:
        """
        Load registry information from a JSON file.
        Note: This only loads metadata, not the actual function implementations.

        Args:
            filepath: Path to the JSON file

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filepath, 'r') as f:
                registry_data = json.load(f)

            self.module_info = {}

            for module in registry_data.get("modules", []):
                module_name = module.get("module_name")
                module_path = module.get("module_path")

                if not module_name:
                    continue

                self.module_info[module_name] = {
                    "module_path": module_path,
                    "functions": {}
                }

                for func_data in module.get("functions", []):
                    func_name = func_data.get("function_name")
                    if func_name:
                        self.module_info[module_name]["functions"][func_name] = func_data

            self.logger.info(f"Loaded registry information from {filepath}")
            return True

        except Exception as e:
            self.logger.error(f"Error loading registry from JSON: {str(e)}")
            return False

    def export_function_schema(self, include_call_history: bool = False) -> Dict:
        """
        Export the registry as a schema for documentation or API integration.

        Args:
            include_call_history: Whether to include function call history

        Returns:
            Dictionary containing registry schema
        """
        schema = {
            "functions": {},
            "modules": {}
        }

        # Add function information
        for name, info in self.functions.items():
            function_schema = {
                "type": info["type"],
                "description": info["description"],
                "parameters": info["parameters"],
                "module_name": info.get("module_name", "unknown"),
                "call_count": info.get("call_count", 0),
                "last_called": info.get("last_called")
            }

            if include_call_history and "call_history" in info:
                function_schema["call_history"] = info["call_history"]

            schema["functions"][name] = function_schema

        # Add module information
        schema["modules"] = self.module_info

        return schema

    def _handle_error(self, message: str, show_example: bool = False) -> bool:
        """
        Handle errors by logging the message and optionally showing usage examples.

        Args:
            message: Error message
            show_example: Whether to show usage examples

        Returns:
            False to indicate failure
        """
        self.logger.error(message)

        if show_example:
            print("\nCorrect usage examples:")
            print("-----------------------")
            print("# Register a static function:")
            print(
                'registry.register_static("windows_open", windows_open, {"type": "object", "properties": {"height": {"type": "number"}}})')
            print("\n# Register a plugin function:")
            print('registry.register_plugin("weather_search", weather_search, plugin_name="weather")')
            print("\n# Register a third-party function:")
            print('registry.register_third_party("play_music", play_music, app_name="spotify")')
            print("\n# Export registry to JSON:")
            print('registry.save_to_json("api_registry.json")')

        return False


# Example usage
if __name__ == "__main__":
    # Create a registry
    registry = FunctionRegistry(verbose=True, json_registry_path="Registration.json")

    # Example functions
    def windows_operation(window_obj: str, height: float):
        print(f"Operating window {window_obj} to height {height}")
        return {"status": "success", "new_height": height}

    def weather_search(key_word: str, web_link: str = None):
        print(f"Searching weather for {key_word}" + (f" using {web_link}" if web_link else ""))
        return {"weather": "sunny", "temperature": "25°C"}

    def spotify():
        print("Opening Spotify")
        return {"status": "opened"}

    # Register functions
    registry.register_static(
        "windows_operation",
        windows_operation,
        parameter_schema={
            "type": "object",
            "properties": {
                "window_obj": {"type": "string", "description": "Window identifier"},
                "height": {"type": "number", "description": "Window height percentage"}
            },
            "required": ["window_obj", "height"]
        },
        description="Control a vehicle window"
    )

    registry.register_plugin(
        "weather_search",
        weather_search,
        plugin_name="weather",
        description="Search for weather information"
    )

    registry.register_third_party(
        "play",
        spotify,
        app_name="spotify",
        description="Open Spotify music player"
    )

    # Execute functions
    print("\nExecuting functions:")
    registry.execute("windows_operation", window_obj="driver", height=75)
    registry.execute("weather.weather_search", key_word="New York")
    registry.execute("spotify.play")

    # List all registered functions
    print("\nAll registered functions:")
    for name, info in registry.list_functions().items():
        print(f"- {name} ({info['type']}): {info['description']}")

    # Export registry to JSON file
    registry.save_to_json("updated_registry.json")

    print("\nRegistry JSON file has been saved. Example of usage history:")
    function_schema = registry.export_function_schema(include_call_history=True)
    for func_name, func_info in function_schema["functions"].items():
        print(f"\n{func_name}:")
        print(f"  Call count: {func_info['call_count']}")
        print(f"  Last called: {func_info['last_called']}")
        if "call_history" in func_info:
            print("  Recent calls:")
            for call in func_info["call_history"]:
                print(f"    - {call['timestamp']}: {call['parameters']}")
