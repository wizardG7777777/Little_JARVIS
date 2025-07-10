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
        def wratio(a, b):
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
                score = SimpleFuzz.wratio(query, choice)
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
        if RAPIDFUZZ_AVAILABLE:
            matches = process.extract(
                query,
                [target[0] for target in search_targets],
                scorer=fuzz.WRatio,  # Use weighted ratio algorithm
                limit=limit * 3  # Get more results for deduplication
            )
        else:
            # Use simple fallback matching
            matches = process.extract(
                query,
                [target[0] for target in search_targets],
                scorer=fuzz.wratio,  # Use simple ratio algorithm
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

    def route_function_call(self, user_query: str) -> tuple:
        """
        Route function call based on registry.json content

        Args:
            user_query: User input query string

        Returns:
            tuple: (success: bool, result: Any)
                  success=True indicates successful routing and execution
                  result is function return value or error message
        """
        try:
            # First try with lower threshold for better matching
            matching_functions = self.registry.semantic_search(user_query, limit=1, threshold=30.0)

            if not matching_functions:
                # Try keyword-based matching as fallback
                best_match = self._keyword_based_matching(user_query)
                if not best_match:
                    return (False, f"Router: No matching function found for query: '{user_query}'")
            else:
                best_match = matching_functions[0]

            function_name = best_match['full_name']

            # Extract parameters from user query
            parameters = self._extract_parameters_from_query(user_query, best_match)

            # Call the function using the existing call_function method
            return self.call_function((function_name, parameters))

        except Exception as e:
            return (False, f"Router: routing error - {str(e)}")

    def _keyword_based_matching(self, user_query: str) -> dict:
        """
        Fallback keyword-based matching when fuzzy search fails

        Args:
            user_query: User input query

        Returns:
            dict: Best matching function info or None
        """
        query_lower = user_query.lower()

        # Define keyword mappings for better matching
        keyword_mappings = {
            '温度': 'climate_module.set_cabin_temperature',
            '空调': 'climate_module.activate_climate_preconditioning',
            '音量': 'media_module.adjust_volume',
            '播放': 'media_module.play_media',
            '导航': 'navigation_module.set_destination',
            '充电': 'navigation_module.find_charging_stations',
            '电池': 'battery_module.get_battery_status',
            '驾驶': 'driving_module.get_driving_statistics',
            '模式': 'driving_module.set_driving_mode'
        }

        # Find best keyword match
        for keyword, function_name in keyword_mappings.items():
            if keyword in query_lower:
                # Get function info from registry
                func_info = self.registry.get_function_by_name(function_name)
                if func_info:
                    return self.registry._format_function_result(func_info)

        return None

    def _extract_parameters_from_query(self, user_query: str, function_info: dict) -> dict:
        """
        Extract parameters from user query based on function requirements
        This is a simplified implementation - in practice would use LLM or NLP

        Args:
            user_query: User input query
            function_info: Function information from registry

        Returns:
            dict: Extracted parameters
        """
        parameters = {}
        expected_params = function_info.get('parameters', [])

        # Simple parameter extraction based on function type
        function_name = function_info.get('function_name', '')

        try:
            if 'temperature' in function_name.lower():
                # Extract temperature value
                import re
                temp_match = re.search(r'(\d+(?:\.\d+)?)', user_query)
                if temp_match:
                    for param in expected_params:
                        if param['name'] == 'temperature' or param['name'] == 'target_temp':
                            parameters[param['name']] = float(temp_match.group(1))
                        elif param['name'] == 'zone':
                            parameters[param['name']] = "driver"  # Default zone
                        elif param['name'] == 'enable':
                            parameters[param['name']] = True
                        elif param['name'] == 'departure_time':
                            parameters[param['name']] = "08:00"  # Default time

            elif 'volume' in function_name.lower():
                # Extract volume level
                import re
                vol_match = re.search(r'(\d+)', user_query)
                if vol_match:
                    for param in expected_params:
                        if param['name'] == 'level':
                            parameters[param['name']] = int(vol_match.group(1))

            elif 'destination' in function_name.lower():
                # Extract location
                for param in expected_params:
                    if param['name'] == 'location':
                        # Simple extraction - take text after common keywords
                        import re
                        location_match = re.search(r'(?:到|去|导航到|前往)\s*([^，。！？\s]+)', user_query)
                        if location_match:
                            parameters[param['name']] = location_match.group(1)
                        else:
                            parameters[param['name']] = "目的地"  # Default
                    elif param['name'] == 'waypoints':
                        parameters[param['name']] = []  # Empty waypoints

            elif 'charging' in function_name.lower():
                # Extract radius and filter
                for param in expected_params:
                    if param['name'] == 'radius_km':
                        import re
                        radius_match = re.search(r'(\d+)\s*(?:公里|km)', user_query)
                        parameters[param['name']] = int(radius_match.group(1)) if radius_match else 10
                    elif param['name'] == 'filter_by':
                        parameters[param['name']] = {"type": "fast_charging"}  # Default filter

            elif 'media' in function_name.lower() or 'play' in function_name.lower():
                # Extract media parameters
                for param in expected_params:
                    if param['name'] == 'media_type':
                        if '音乐' in user_query or '歌' in user_query:
                            parameters[param['name']] = "music"
                        else:
                            parameters[param['name']] = "audio"
                    elif param['name'] == 'source':
                        parameters[param['name']] = "local"
                    elif param['name'] == 'content_id':
                        parameters[param['name']] = "default_content"

            elif 'driving' in function_name.lower():
                # Extract driving parameters
                for param in expected_params:
                    if param['name'] == 'time_period':
                        if '今天' in user_query:
                            parameters[param['name']] = "today"
                        elif '本周' in user_query:
                            parameters[param['name']] = "week"
                        else:
                            parameters[param['name']] = "today"
                    elif param['name'] == 'mode':
                        if '运动' in user_query or 'sport' in user_query.lower():
                            parameters[param['name']] = "sport"
                        elif '经济' in user_query or 'eco' in user_query.lower():
                            parameters[param['name']] = "eco"
                        else:
                            parameters[param['name']] = "normal"

            # Fill in any missing required parameters with defaults
            for param in expected_params:
                if param['name'] not in parameters:
                    param_type = param.get('type', 'str')
                    if param_type == 'str':
                        parameters[param['name']] = "default_value"
                    elif param_type == 'int':
                        parameters[param['name']] = 0
                    elif param_type == 'float':
                        parameters[param['name']] = 0.0
                    elif param_type == 'bool':
                        parameters[param['name']] = True
                    elif param_type == 'list':
                        parameters[param['name']] = []
                    elif param_type == 'dict':
                        parameters[param['name']] = {}

        except Exception as e:
            # If parameter extraction fails, provide defaults
            for param in expected_params:
                if param['name'] not in parameters:
                    param_type = param.get('type', 'str')
                    if param_type == 'str':
                        parameters[param['name']] = "default_value"
                    elif param_type == 'int':
                        parameters[param['name']] = 0
                    elif param_type == 'float':
                        parameters[param['name']] = 0.0
                    elif param_type == 'bool':
                        parameters[param['name']] = True
                    elif param_type == 'list':
                        parameters[param['name']] = []
                    elif param_type == 'dict':
                        parameters[param['name']] = {}

        return parameters