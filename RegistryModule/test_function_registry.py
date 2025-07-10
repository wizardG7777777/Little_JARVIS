# test_function_registry.py

import unittest
import os
import json
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from function_registry import FunctionRegistry, FunctionType


class TestFunctionRegistry(unittest.TestCase):
    """Unit tests for FunctionRegistry class"""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.test_json_path = os.path.join(self.test_dir, "test_registry.json")
        
        # Create registry instance for testing
        self.registry = FunctionRegistry(verbose=False, json_registry_path=self.test_json_path)
        
        # Define test functions
        def test_static_func(param1: str, param2: int = 10):
            """Test static function"""
            return f"Static: {param1} - {param2}"
        
        def test_plugin_func(keyword: str, limit: int = 5):
            """Test plugin function"""
            return f"Plugin: {keyword} (limit: {limit})"
        
        def test_third_party_func(action: str):
            """Test third-party function"""
            return f"Third-party: {action}"
        
        self.test_static_func = test_static_func
        self.test_plugin_func = test_plugin_func
        self.test_third_party_func = test_third_party_func

    def tearDown(self):
        """Clean up after each test method."""
        # Remove temporary directory and all its contents
        shutil.rmtree(self.test_dir)

    def test_registry_initialization(self):
        """Test registry initialization"""
        self.assertIsInstance(self.registry, FunctionRegistry)
        self.assertEqual(self.registry.json_registry_path, self.test_json_path)
        self.assertIsInstance(self.registry.functions, dict)
        self.assertIsInstance(self.registry.module_info, dict)

    def test_register_static_function(self):
        """Test registering a static function"""
        result = self.registry.register_static(
            name="test_static",
            func=self.test_static_func,
            description="Test static function"
        )
        
        self.assertTrue(result)
        self.assertIn("test_static", self.registry.functions)
        
        func_info = self.registry.functions["test_static"]
        self.assertEqual(func_info["type"], "static")
        self.assertEqual(func_info["description"], "Test static function")
        self.assertEqual(func_info["call_count"], 0)

    def test_register_plugin_function(self):
        """Test registering a plugin function"""
        result = self.registry.register_plugin(
            name="search",
            func=self.test_plugin_func,
            plugin_name="weather",
            description="Weather search plugin"
        )
        
        self.assertTrue(result)
        self.assertIn("weather.search", self.registry.functions)
        
        func_info = self.registry.functions["weather.search"]
        self.assertEqual(func_info["type"], "plugin")
        self.assertEqual(func_info["description"], "Weather search plugin")

    def test_register_third_party_function(self):
        """Test registering a third-party function"""
        result = self.registry.register_third_party(
            name="play",
            func=self.test_third_party_func,
            app_name="spotify",
            description="Spotify music player"
        )
        
        self.assertTrue(result)
        self.assertIn("spotify.play", self.registry.functions)
        
        func_info = self.registry.functions["spotify.play"]
        self.assertEqual(func_info["type"], "third_party")
        self.assertEqual(func_info["description"], "Spotify music player")

    def test_register_duplicate_function_without_override(self):
        """Test registering duplicate function without override flag"""
        # Register function first time
        result1 = self.registry.register_static("duplicate", self.test_static_func)
        self.assertTrue(result1)
        
        # Try to register same name again without override
        result2 = self.registry.register_static("duplicate", self.test_static_func)
        self.assertFalse(result2)

    def test_register_duplicate_function_with_override(self):
        """Test registering duplicate function with override flag"""
        # Register function first time
        result1 = self.registry.register_static("override_test", self.test_static_func)
        self.assertTrue(result1)
        
        # Register same name again with override
        result2 = self.registry.register_static("override_test", self.test_plugin_func, override=True)
        self.assertTrue(result2)

    def test_execute_function(self):
        """Test executing a registered function"""
        # Register a function
        self.registry.register_static("execute_test", self.test_static_func)
        
        # Execute the function
        result = self.registry.execute("execute_test", param1="hello", param2=20)
        
        self.assertEqual(result, "Static: hello - 20")
        
        # Check call count was updated
        func_info = self.registry.functions["execute_test"]
        self.assertEqual(func_info["call_count"], 1)
        self.assertIsNotNone(func_info["last_called"])

    def test_execute_nonexistent_function(self):
        """Test executing a function that doesn't exist"""
        result = self.registry.execute("nonexistent", param1="test")
        self.assertIsNone(result)

    def test_list_functions(self):
        """Test listing all functions"""
        # Register functions of different types
        self.registry.register_static("static_func", self.test_static_func)
        self.registry.register_plugin("plugin_func", self.test_plugin_func, plugin_name="test")
        self.registry.register_third_party("third_func", self.test_third_party_func, app_name="test")
        
        # List all functions
        all_functions = self.registry.list_functions()
        self.assertEqual(len(all_functions), 3)
        
        # List only static functions
        static_functions = self.registry.list_functions(FunctionType.STATIC)
        self.assertEqual(len(static_functions), 1)
        self.assertIn("static_func", static_functions)
        
        # List only plugin functions
        plugin_functions = self.registry.list_functions("plugin")
        self.assertEqual(len(plugin_functions), 1)
        self.assertIn("test.plugin_func", plugin_functions)

    def test_unregister_function(self):
        """Test unregistering a function"""
        # Register a function
        self.registry.register_static("unregister_test", self.test_static_func)
        self.assertIn("unregister_test", self.registry.functions)
        
        # Unregister the function
        result = self.registry.unregister("unregister_test")
        self.assertTrue(result)
        self.assertNotIn("unregister_test", self.registry.functions)

    def test_unregister_nonexistent_function(self):
        """Test unregistering a function that doesn't exist"""
        result = self.registry.unregister("nonexistent")
        self.assertFalse(result)

    def test_save_and_load_json(self):
        """Test saving and loading registry to/from JSON"""
        # Register some functions
        self.registry.register_static("save_test", self.test_static_func, description="Save test function")
        self.registry.register_plugin("load_test", self.test_plugin_func, plugin_name="test", description="Load test function")
        
        # Save to JSON
        save_result = self.registry.save_to_json()
        self.assertTrue(save_result)
        self.assertTrue(os.path.exists(self.test_json_path))
        
        # Verify JSON content
        with open(self.test_json_path, 'r') as f:
            data = json.load(f)
        
        self.assertIn("modules", data)
        self.assertIsInstance(data["modules"], list)
        
        # Create new registry and load from JSON
        new_registry = FunctionRegistry(verbose=False, json_registry_path=self.test_json_path)
        load_result = new_registry.load_from_json(self.test_json_path)
        self.assertTrue(load_result)

    def test_parameter_schema_generation(self):
        """Test automatic parameter schema generation"""
        def typed_function(name: str, age: int, height: float, active: bool, tags: list):
            return f"{name} is {age} years old"
        
        self.registry.register_static("typed_func", typed_function)
        
        func_info = self.registry.functions["typed_func"]
        schema = func_info["parameters"]
        
        self.assertEqual(schema["properties"]["name"]["type"], "string")
        self.assertEqual(schema["properties"]["age"]["type"], "integer")
        self.assertEqual(schema["properties"]["height"]["type"], "number")
        self.assertEqual(schema["properties"]["active"]["type"], "boolean")
        self.assertEqual(schema["properties"]["tags"]["type"], "array")
        
        # All parameters should be required (no defaults)
        self.assertEqual(len(schema["required"]), 5)

    def test_batch_registration(self):
        """Test batch registration of functions"""
        functions_to_register = [
            {
                "name": "batch1",
                "func": self.test_static_func,
                "type": "static",
                "description": "Batch static function"
            },
            {
                "name": "batch2",
                "func": self.test_plugin_func,
                "type": "plugin",
                "plugin_name": "batch_plugin",
                "description": "Batch plugin function"
            },
            {
                "name": "batch3",
                "func": self.test_third_party_func,
                "type": "third_party",
                "app_name": "batch_app",
                "description": "Batch third-party function"
            }
        ]
        
        results = self.registry.register_batch(functions_to_register)
        
        self.assertEqual(len(results), 3)
        self.assertTrue(all(results.values()))
        
        # Verify all functions were registered
        self.assertIn("batch1", self.registry.functions)
        self.assertIn("batch_plugin.batch2", self.registry.functions)
        self.assertIn("batch_app.batch3", self.registry.functions)

    def test_export_function_schema(self):
        """Test exporting function schema"""
        # Register and execute a function to create call history
        self.registry.register_static("schema_test", self.test_static_func)
        self.registry.execute("schema_test", param1="test", param2=42)
        
        # Export schema without call history
        schema = self.registry.export_function_schema(include_call_history=False)
        self.assertIn("functions", schema)
        self.assertIn("modules", schema)
        self.assertIn("schema_test", schema["functions"])
        self.assertNotIn("call_history", schema["functions"]["schema_test"])
        
        # Export schema with call history
        schema_with_history = self.registry.export_function_schema(include_call_history=True)
        self.assertIn("call_history", schema_with_history["functions"]["schema_test"])

    def test_get_function_info(self):
        """Test getting function information"""
        self.registry.register_static("info_test", self.test_static_func, description="Info test")
        
        info = self.registry.get_function_info("info_test")
        self.assertIsNotNone(info)
        self.assertEqual(info["description"], "Info test")
        self.assertEqual(info["type"], "static")
        
        # Test non-existent function
        no_info = self.registry.get_function_info("nonexistent")
        self.assertIsNone(no_info)


if __name__ == "__main__":
    unittest.main()
