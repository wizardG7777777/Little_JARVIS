"""
Mock API Calls for System Testing
This module provides mock implementations of all APIs defined in registry.json
Only performs parameter type validation without executing actual logic
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Union


class MockAPIValidator:
    """Mock API class that validates parameter types based on registry.json"""
    
    def __init__(self):
        """Initialize the mock API validator with registry data"""
        self.registry_data = self._load_registry()
        self.function_signatures = self._build_function_signatures()
    
    def _load_registry(self) -> Dict[str, Any]:
        """Load registry.json file"""
        try:
            # Get parent directory and construct registry path
            current_dir = Path(__file__).resolve().parent
            parent_dir = current_dir.parent
            registry_path = parent_dir / "RegistryModule" / "registry.json"
            
            if not registry_path.exists():
                raise FileNotFoundError(f"Registry file not found: {registry_path}")
            
            with open(registry_path, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            raise Exception(f"Failed to load registry: {str(e)}")
    
    def _build_function_signatures(self) -> Dict[str, Dict[str, Any]]:
        """Build function signatures from registry data"""
        signatures = {}
        
        for module in self.registry_data.get('modules', []):
            module_name = module.get('module_name', '')
            
            for function in module.get('functions', []):
                function_name = function.get('function_name', '')
                full_name = f"{module_name}.{function_name}"
                
                signatures[full_name] = {
                    'module_name': module_name,
                    'function_name': function_name,
                    'parameters': function.get('parameters', [])
                }
        
        return signatures
    
    def _validate_parameter_type(self, value: Any, expected_type: str) -> bool:
        """Validate if value matches expected type"""
        type_mapping = {
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
            'list': list,
            'dict': dict,
            'tuple': tuple,
            'None': type(None)
        }
        
        if expected_type not in type_mapping:
            return True  # Unknown type, skip validation
        
        expected_python_type = type_mapping[expected_type]
        
        if expected_type == 'None':
            return value is None
        else:
            return isinstance(value, expected_python_type)
    
    def validate_and_call(self, function_name: str, **kwargs) -> Dict[str, Any]:
        """
        Validate parameters and simulate function call
        
        Args:
            function_name: Full function name (module.function)
            **kwargs: Function parameters
            
        Returns:
            Dict containing validation result and mock response
        """
        if function_name not in self.function_signatures:
            return {
                'success': False,
                'error': f"Function '{function_name}' not found in registry",
                'result': None
            }
        
        signature = self.function_signatures[function_name]
        expected_params = signature['parameters']
        
        # Validate parameters
        validation_errors = []
        
        # Check required parameters
        required_param_names = {param['name'] for param in expected_params}
        provided_param_names = set(kwargs.keys())
        
        # Check for missing parameters
        missing_params = required_param_names - provided_param_names
        if missing_params:
            validation_errors.append(f"Missing required parameters: {', '.join(missing_params)}")
        
        # Check for unexpected parameters
        unexpected_params = provided_param_names - required_param_names
        if unexpected_params:
            validation_errors.append(f"Unexpected parameters: {', '.join(unexpected_params)}")
        
        # Validate parameter types
        for param in expected_params:
            param_name = param['name']
            expected_type = param['type']
            
            if param_name in kwargs:
                provided_value = kwargs[param_name]
                if not self._validate_parameter_type(provided_value, expected_type):
                    validation_errors.append(
                        f"Parameter '{param_name}' should be {expected_type}, "
                        f"got {type(provided_value).__name__}"
                    )
        
        if validation_errors:
            return {
                'success': False,
                'error': '; '.join(validation_errors),
                'result': None
            }
        
        # If validation passes, return mock success response
        return {
            'success': True,
            'error': None,
            'result': f"Mock execution successful for {function_name} with parameters: {kwargs}"
        }


# Create mock API instances for each module in registry.json
class MockBatteryModule:
    """Mock battery module API"""
    
    def __init__(self, validator: MockAPIValidator):
        self.validator = validator
    
    def get_battery_status(self):
        """Mock get_battery_status function"""
        return self.validator.validate_and_call('battery_module.get_battery_status')


class MockClimateModule:
    """Mock climate module API"""
    
    def __init__(self, validator: MockAPIValidator):
        self.validator = validator
    
    def set_cabin_temperature(self, temperature: float, zone: str):
        """Mock set_cabin_temperature function"""
        return self.validator.validate_and_call(
            'climate_module.set_cabin_temperature',
            temperature=temperature,
            zone=zone
        )
    
    def activate_climate_preconditioning(self, enable: bool, target_temp: float, departure_time: str):
        """Mock activate_climate_preconditioning function"""
        return self.validator.validate_and_call(
            'climate_module.activate_climate_preconditioning',
            enable=enable,
            target_temp=target_temp,
            departure_time=departure_time
        )


class MockNavigationModule:
    """Mock navigation module API"""
    
    def __init__(self, validator: MockAPIValidator):
        self.validator = validator
    
    def set_destination(self, location: str, waypoints: list):
        """Mock set_destination function"""
        return self.validator.validate_and_call(
            'navigation_module.set_destination',
            location=location,
            waypoints=waypoints
        )
    
    def find_charging_stations(self, radius_km: int, filter_by: dict):
        """Mock find_charging_stations function"""
        return self.validator.validate_and_call(
            'navigation_module.find_charging_stations',
            radius_km=radius_km,
            filter_by=filter_by
        )


class MockMediaModule:
    """Mock media module API"""
    
    def __init__(self, validator: MockAPIValidator):
        self.validator = validator
    
    def play_media(self, media_type: str, source: str, content_id: str):
        """Mock play_media function"""
        return self.validator.validate_and_call(
            'media_module.play_media',
            media_type=media_type,
            source=source,
            content_id=content_id
        )
    
    def adjust_volume(self, level: int):
        """Mock adjust_volume function"""
        return self.validator.validate_and_call(
            'media_module.adjust_volume',
            level=level
        )


class MockDrivingModule:
    """Mock driving module API"""
    
    def __init__(self, validator: MockAPIValidator):
        self.validator = validator
    
    def get_driving_statistics(self, time_period: str):
        """Mock get_driving_statistics function"""
        return self.validator.validate_and_call(
            'driving_module.get_driving_statistics',
            time_period=time_period
        )
    
    def set_driving_mode(self, mode: str):
        """Mock set_driving_mode function"""
        return self.validator.validate_and_call(
            'driving_module.set_driving_mode',
            mode=mode
        )


class MockAPIFactory:
    """Factory class to create mock API instances"""
    
    def __init__(self):
        self.validator = MockAPIValidator()
        self.battery_module = MockBatteryModule(self.validator)
        self.climate_module = MockClimateModule(self.validator)
        self.navigation_module = MockNavigationModule(self.validator)
        self.media_module = MockMediaModule(self.validator)
        self.driving_module = MockDrivingModule(self.validator)
    
    def get_module(self, module_name: str):
        """Get mock module by name"""
        module_mapping = {
            'battery_module': self.battery_module,
            'climate_module': self.climate_module,
            'navigation_module': self.navigation_module,
            'media_module': self.media_module,
            'driving_module': self.driving_module
        }
        return module_mapping.get(module_name)
    
    def call_function(self, module_name: str, function_name: str, **kwargs):
        """Call mock function by module and function name"""
        module = self.get_module(module_name)
        if module is None:
            return {
                'success': False,
                'error': f"Module '{module_name}' not found",
                'result': None
            }
        
        if not hasattr(module, function_name):
            return {
                'success': False,
                'error': f"Function '{function_name}' not found in module '{module_name}'",
                'result': None
            }
        
        try:
            func = getattr(module, function_name)
            return func(**kwargs)
        except Exception as e:
            return {
                'success': False,
                'error': f"Function call failed: {str(e)}",
                'result': None
            }


# Test the mock API
if __name__ == "__main__":
    print("=== Testing Mock API Calls ===")
    
    factory = MockAPIFactory()
    
    # Test cases
    test_cases = [
        # Valid calls
        ('battery_module', 'get_battery_status', {}),
        ('climate_module', 'set_cabin_temperature', {'temperature': 22.5, 'zone': 'driver'}),
        ('navigation_module', 'set_destination', {'location': '北京', 'waypoints': []}),
        ('media_module', 'adjust_volume', {'level': 50}),
        ('driving_module', 'set_driving_mode', {'mode': 'sport'}),
        
        # Invalid calls (type errors)
        ('climate_module', 'set_cabin_temperature', {'temperature': 'hot', 'zone': 'driver'}),
        ('media_module', 'adjust_volume', {'level': 'loud'}),
        
        # Missing parameters
        ('climate_module', 'set_cabin_temperature', {'temperature': 22.5}),
        
        # Unknown function
        ('battery_module', 'unknown_function', {}),
    ]
    
    for module_name, function_name, params in test_cases:
        print(f"\nTesting: {module_name}.{function_name}({params})")
        result = factory.call_function(module_name, function_name, **params)
        print(f"Success: {result['success']}")
        if result['error']:
            print(f"Error: {result['error']}")
        if result['result']:
            print(f"Result: {result['result']}")
        print("-" * 50)
