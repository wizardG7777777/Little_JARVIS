"""
This program implements both function router and function calling interface
English translation of Chinese terms:
- 加载 = load
- 函数 = function
- 返回 = return
- 错误 = error
- 文件 = file
- 项目根目录 = project root directory
- 解析错误 = parsing error
"""
import json
from pathlib import Path
import os
import importlib.util
import sys
from typing import List, Dict, Any, Optional

# Try to import rapidfuzz, use fallback if not available
try:
    from rapidfuzz import fuzz, process
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    RAPIDFUZZ_AVAILABLE = False
    # Simple fallback for basic string matching
    class SimpleFuzz:
        @staticmethod
        def WRatio(a, b):
            # Simple similarity based on common characters
            if not a or not b:
                return 0
            a_lower = a.lower()
            b_lower = b.lower()
            if a_lower == b_lower:
                return 100
            # Count common characters
            common = sum(1 for char in a_lower if char in b_lower)
            return int((common / max(len(a_lower), len(b_lower))) * 100)

    class SimpleProcess:
        @staticmethod
        def extract(query, choices, scorer=None, limit=5):
            # Simple extraction without rapidfuzz
            results = []
            for i, choice in enumerate(choices):
                score = SimpleFuzz.WRatio(query, choice)
                results.append((choice, score, i))
            # Sort by score descending
            results.sort(key=lambda x: x[1], reverse=True)
            return results[:limit]

    fuzz = SimpleFuzz()
    process = SimpleProcess()

def load_registry_json() -> bool:
    """
    Load the RegistryModule/registry.json file located in the project root directory

    Returns:
        bool: Returns True if successfully loaded and parsed JSON, otherwise False
    """
    try:
        # Get current script path and calculate project root directory (two levels up)
        current_script = Path(__file__).resolve()
        project_root = current_script.parent.parent

        # Try multiple possible registry file names
        possible_files = [
            "RegistryModule/registry.json",
            "RegistryModule/updated_registry.json",
            "RegistryModule/Registration.json"
        ]

        json_path = None
        for file_name in possible_files:
            test_path = project_root / file_name
            if test_path.exists():
                json_path = test_path
                break

        if json_path is None:
            print(f"Error: No registry JSON file found in {project_root}/RegistryModule/")
            print(f"Project root directory: {project_root}")
            print(f"Root directory contents: {[f.name for f in project_root.iterdir()]}")
            return False

        # Try to load and parse JSON
        json.loads(json_path.read_text(encoding='utf-8'))
        return True

    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Error location: line {e.lineno}, column {e.colno}")
        print(f"Problem content: {e.doc[e.pos - 30:e.pos + 30] if e.doc else 'no content'}")
        return False

    except Exception as e:
        print(f"Unexpected error loading JSON: {type(e).__name__} - {e}")
        print(f"File path: {json_path}")
        return False


class FunctionRegistry:
    def __init__(self):
        self.registry_data = None
        self.function_index = []  # 存储所有函数的索引信息
        self.load_registry()

    def load_registry(self):
        """Load registry file with cross-platform path support"""
        # Get current script path and calculate project root directory
        current_script = Path(__file__).resolve()
        project_root = current_script.parent.parent

        # Try multiple possible registry file names
        possible_files = [
            "RegistryModule/registry.json",
            "RegistryModule/updated_registry.json",
            "RegistryModule/Registration.json"
        ]

        registry_path = None
        for file_name in possible_files:
            test_path = project_root / file_name
            if test_path.exists():
                registry_path = test_path
                break

        if registry_path is None:
            raise FileNotFoundError(f"Registry file not found in {project_root}/RegistryModule/")

        try:
            with open(registry_path, 'r', encoding='utf-8') as f:
                self.registry_data = json.load(f)
            self._build_function_index()
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format in registry file")

    def _build_function_index(self):
        """Build function index for easy querying"""
        self.function_index = []

        if not self.registry_data or 'modules' not in self.registry_data:
            return

        for module in self.registry_data['modules']:
            module_name = module.get('module_name', '')
            module_path = module.get('module_path', '')

            for function in module.get('functions', []):
                function_info = {
                    'module_name': module_name,
                    'module_path': module_path,
                    'function_name': function.get('function_name', ''),
                    'parameters': function.get('parameters', []),
                    'search_text': f"{module_name}.{function.get('function_name', '')}"  # Text for searching
                }
                self.function_index.append(function_info)

    def semantic_search(self, query: str, limit: int = 1, threshold: float = 60.0) -> List[Dict[str, Any]]:
        """
        Use RapidFuzz for approximate semantic search

        Args:
            query (str): User input query string
            limit (int): Limit on number of results returned, default is 1
            threshold (float): Matching threshold, results below this value will be filtered, default is 60.0

        Returns:
            List[Dict[str, Any]]: List of matching function calls, sorted by similarity
        """
        if not self.function_index:
            return []

        # Prepare search target list
        search_targets = []
        for idx, func_info in enumerate(self.function_index):
            # Create multiple search targets to improve matching accuracy
            targets = [
                (func_info['function_name'], idx),  # Function name
                (func_info['search_text'], idx),  # Module name.function name
                (func_info['module_name'], idx)  # Module name
            ]
            search_targets.extend(targets)

        # Use RapidFuzz for fuzzy matching
        matches = process.extract(
            query,
            [target[0] for target in search_targets],
            scorer=fuzz.WRatio,  # Use weighted ratio algorithm
            limit=limit * 3  # Get more results for deduplication
        )

        # Process matching results
        result_dict = {}
        for match_text, score, match_idx in matches:
            if score < threshold:
                continue

            # Get original function index
            original_idx = search_targets[match_idx][1]
            func_info = self.function_index[original_idx]

            # Use function's unique identifier as key for deduplication
            func_key = f"{func_info['module_name']}.{func_info['function_name']}"

            if func_key not in result_dict or result_dict[func_key]['score'] < score:
                result_dict[func_key] = {
                    'score': score,
                    'function_info': self._format_function_result(func_info)
                }

        # Sort by score and return specified number of results
        sorted_results = sorted(result_dict.values(), key=lambda x: x['score'], reverse=True)
        return [item['function_info'] for item in sorted_results[:limit]]

    def _format_function_result(self, func_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format function result, only return content helpful for LLM parsing

        Args:
            func_info (Dict[str, Any]): Original function information

        Returns:
            Dict[str, Any]: Formatted function information
        """
        return {
            'module_name': func_info['module_name'],
            'function_name': func_info['function_name'],
            'parameters': func_info['parameters'],
            'full_name': f"{func_info['module_name']}.{func_info['function_name']}"
        }

    def get_all_functions(self) -> List[Dict[str, Any]]:
        """Get all registered functions"""
        return [self._format_function_result(func_info) for func_info in self.function_index]

    def get_function_by_name(self, full_name: str) -> Optional[Dict[str, Any]]:
        """Get function information by complete function name"""
        for func_info in self.function_index:
            if func_info['search_text'] == full_name or func_info['function_name'] == full_name:
                # Return the full function info, not just the formatted result
                return func_info
        return None

class function_calling_interface:
    def __init__(self):
        load_registry_json()
        self.registry = FunctionRegistry()
        self.type_mapping = {
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
            'list': list,
            'dict': dict,
            'tuple': tuple,
            'None': type(None)
        }

    def call_function(self, input_tuple):
        """
        Execute function call

        Args:
            input_tuple: Tuple in format (function_name, parameters_dict)
                        function_name: Function name string
                        parameters_dict: Parameter dictionary, keys are parameter names, values are parameter values

        Returns:
            tuple: (success: bool, result: Any)
                  success=True indicates successful call, False indicates failed call
                  result is function return value or error message
        """
        try:
            # Validate input format
            if not isinstance(input_tuple, tuple) or len(input_tuple) != 2:
                return (False, "Router: augment error - Input must be a tuple of (function_name, parameters_dict)")

            function_name, params_dict = input_tuple

            if not isinstance(function_name, str):
                return (False, "Router: augment error - Function name must be a string")

            if not isinstance(params_dict, dict):
                return (False, "Router: augment error - Parameters must be a dictionary")

            # Find function in registry
            func_info = self.registry.get_function_by_name(function_name)
            if func_info is None:
                return (False, f"Router: funtion {function_name} not found")

            # Validate parameters
            validation_result = self._validate_parameters(func_info, params_dict)
            if not validation_result[0]:
                return validation_result

            # Dynamically import module and call function
            try:
                result = self._execute_function(func_info, params_dict)
                return (True, result)
            except Exception as e:
                return (False, f"Router: execution error - {str(e)}")

        except Exception as e:
            return (False, f"Router: augment error - {str(e)}")

    def _validate_parameters(self, func_info, params_dict):
        """
        Validate function parameters

        Args:
            func_info: Function information dictionary
            params_dict: Input parameter dictionary

        Returns:
            tuple: (success: bool, error_message: str or None)
        """
        try:
            expected_params = func_info.get('parameters', [])

            # Get required and provided parameter names
            required_param_names = {param['name'] for param in expected_params}
            provided_param_names = set(params_dict.keys())

            # Check for missing required parameters
            missing_params = required_param_names - provided_param_names
            if missing_params:
                return (False, f"Router: augment error - Missing required parameters: {', '.join(missing_params)}")

            # Check for unexpected parameters
            unexpected_params = provided_param_names - required_param_names
            if unexpected_params:
                return (False, f"Router: augment error - Unexpected parameters: {', '.join(unexpected_params)}")

            # Validate parameter types
            for param in expected_params:
                param_name = param['name']
                expected_type = param['type']

                if param_name in params_dict:
                    provided_value = params_dict[param_name]

                    # Get expected Python type
                    if expected_type in self.type_mapping:
                        expected_python_type = self.type_mapping[expected_type]

                        # Special handling for None type
                        if expected_type == 'None' and provided_value is not None:
                            return (False, f"Router: augment error - Parameter '{param_name}' should be None, got {type(provided_value).__name__}")
                        elif expected_type != 'None' and not isinstance(provided_value, expected_python_type):
                            return (False, f"Router: augment error - Parameter '{param_name}' should be {expected_type}, got {type(provided_value).__name__}")
                    else:
                        # Unknown type, skip validation
                        pass

            return (True, None)

        except Exception as e:
            return (False, f"Router: augment error - Parameter validation failed: {str(e)}")

    def _execute_function(self, func_info, params_dict):
        """
        Execute function call

        Args:
            func_info: Function information dictionary
            params_dict: Parameter dictionary

        Returns:
            Any: Function execution result
        """
        module_path = func_info['module_path']
        module_name = func_info['module_name']
        function_name = func_info['function_name']

        # Handle nested function calls (like weather.weather_search)
        if '.' in function_name:
            # This is a nested call, needs special handling
            parts = function_name.split('.')
            actual_function_name = parts[-1]
            sub_module_path = '.'.join(parts[:-1])
        else:
            actual_function_name = function_name
            sub_module_path = None

        try:
            # Dynamically import module
            if module_path.endswith('.py'):
                # Import from file path
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                if spec is None:
                    raise ImportError(f"Could not load module spec from {module_path}")

                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)
            else:
                # Import from module name
                module = importlib.import_module(module_name)

            # Get function object
            if sub_module_path:
                # Handle nested calls
                target_obj = module
                for part in sub_module_path.split('.'):
                    target_obj = getattr(target_obj, part)
                func_obj = getattr(target_obj, actual_function_name)
            else:
                func_obj = getattr(module, actual_function_name)

            # Call function
            if params_dict:
                return func_obj(**params_dict)
            else:
                return func_obj()

        except ImportError as e:
            raise Exception(f"Could not import module {module_name}: {str(e)}")
        except AttributeError as e:
            raise Exception(f"Function {function_name} not found in module {module_name}: {str(e)}")
        except TypeError as e:
            raise Exception(f"Function call failed due to parameter mismatch: {str(e)}")
        except Exception as e:
            raise Exception(f"Function execution failed: {str(e)}")

    def get_available_functions(self):
        """
        Get all available function list

        Returns:
            List[Dict]: List of available functions
        """
        return self.registry.get_all_functions()

    def search_functions(self, query, limit=5):
        """
        Search functions

        Args:
            query: Search query string
            limit: Limit on number of results returned

        Returns:
            List[Dict]: List of matching functions
        """
        return self.registry.semantic_search(query, limit=limit)