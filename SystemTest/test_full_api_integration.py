"""
Full API Integration Tests
Tests the complete flow: User Input -> IntentRouter -> RuleBaseEngine -> IntentRouter -> LocalChatBot -> FunctionCalling_router -> API

This test avoids modifying RuleBaseEngine and LocalChatBot internal logic by using mock components where needed.
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from RuleBaseEngine.RuleBaseEngine import RuleEngine
from ChatBots.FunctionCalling_router import function_calling_interface
from SystemTest.mock_api_calls import MockAPIFactory


class MockLocalChatBot:
    """Mock LocalChatBot that simulates the interface without requiring actual model"""
    
    def __init__(self):
        self.function_router = function_calling_interface()
    
    def invoke(self, data_input, config=None):
        """Mock invoke method"""
        return {
            "thinking": "Mock thinking process",
            "content": f"Mock response for: {data_input}"
        }
    
    def function_call_with_router(self, user_query: str) -> str:
        """
        Simulate function calling through router
        This method bridges LocalChatBot to FunctionCalling_router
        """
        try:
            # Use the router to handle function calling
            success, result = self.function_router.route_function_call(user_query)
            
            if success:
                return f"Function executed successfully: {result}"
            else:
                return f"Function execution failed: {result}"
                
        except Exception as e:
            return f"Function calling error: {str(e)}"


class MockIntentRouter:
    """Mock IntentRouter that integrates with real RuleBaseEngine and mock LocalChatBot"""
    
    def __init__(self, rules_path: str = None):
        """Initialize with real RuleBaseEngine and mock LocalChatBot"""
        try:
            # Set default rules path if not provided
            if rules_path is None:
                parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                rules_path = os.path.join(parent_dir, "RuleBaseEngine", "Rules.json")
            
            # Initialize real rule engine
            self.rule_engine = RuleEngine(rules_path)
            
            # Initialize mock local chatbot
            self.local_llm = MockLocalChatBot()
            
            # Risk level mapping
            self.risk_explanations = {
                "HIGH_RISK_FORBIDDEN": "This operation is classified as high-risk and has been blocked for security reasons.",
                "REQUIRES_CONFIRMATION": "This operation requires additional confirmation due to security policies.",
                "DIRECT_ALLOW": "This operation is approved and can be executed directly."
            }
            
        except Exception as e:
            raise Exception(f"Mock Router initialization failed: {str(e)}")
    
    def process_request(self, user_input: str) -> str:
        """
        Process user request through the complete pipeline
        User Input -> RuleBaseEngine -> LocalChatBot -> FunctionCalling_router -> API
        """
        try:
            # Validate input
            if not isinstance(user_input, str):
                return "Error: Input must be a string"
            
            if not user_input.strip():
                return "Error: Empty input provided"
            
            # Step 1: Pass to rule base engine
            print(f"Step 1 - Processing user input: {user_input}")
            intent_type, action = self.rule_engine.process_input(user_input)
            print(f"Step 1 - Rule engine response - Intent: {intent_type}, Action: {action}")
            
            # Step 2: Handle based on action
            if intent_type == "LLM" and action == "leave to chat_bot":
                print("Step 2 - Routing to LocalChatBot for chat")
                llm_response = self.local_llm.invoke(user_input)
                return llm_response["content"]
            
            # Check risk level
            if action == "HIGH_RISK_FORBIDDEN":
                reason = self.risk_explanations.get(action, "High-risk operation blocked")
                print(f"Step 2 - High-risk operation blocked: {user_input}")
                return f"Operation blocked: {reason}"
            
            # For operations requiring confirmation
            if action == "REQUIRES_CONFIRMATION":
                confirmation_msg = self.risk_explanations.get(action, "Operation requires confirmation")
                print(f"Step 2 - Operation requires confirmation: {user_input}")
                return f"Confirmation required: {confirmation_msg} Please confirm if you want to proceed."
            
            # For approved operations
            if action == "DIRECT_ALLOW":
                print(f"Step 2 - Operation approved, routing to function calling")
                
                # Step 3: Route to LocalChatBot -> FunctionCalling_router -> API
                function_result = self.local_llm.function_call_with_router(user_input)
                print(f"Step 3 - Function calling result: {function_result}")
                
                return function_result
            
            # Unknown action
            return f"Error: Unknown action type: {action}"
            
        except Exception as e:
            error_msg = f"Router processing error: {str(e)}"
            print(error_msg)
            return f"Error: {error_msg}"


class TestFullAPIIntegration(unittest.TestCase):
    """Test the complete API integration flow"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_router = MockIntentRouter()
        self.mock_api_factory = MockAPIFactory()
        
        # Test cases covering different intent types
        self.test_cases = [
            # Device control tests
            {
                'input': '设置温度到22度',
                'expected_intent': 'device_control',
                'expected_action': 'DIRECT_ALLOW',
                'description': 'Temperature control'
            },
            {
                'input': '调节音量到50',
                'expected_intent': 'device_control', 
                'expected_action': 'DIRECT_ALLOW',
                'description': 'Volume control'
            },
            
            # Info query tests
            {
                'input': '查看电池状态',
                'expected_intent': 'info_query',
                'expected_action': 'DIRECT_ALLOW',
                'description': 'Battery status query'
            },
            {
                'input': '显示驾驶统计',
                'expected_intent': 'info_query',
                'expected_action': 'DIRECT_ALLOW',
                'description': 'Driving statistics query'
            },
            
            # System function tests
            {
                'input': '导航到北京',
                'expected_intent': 'system_app_launch',
                'expected_action': 'DIRECT_ALLOW',
                'description': 'Navigation function'
            },
            {
                'input': '播放音乐',
                'expected_intent': 'system_file_access',
                'expected_action': 'DIRECT_ALLOW',
                'description': 'Media playback'
            },
            
            # Risk level tests
            {
                'input': '停止所有操作',
                'expected_intent': 'complex_command',
                'expected_action': 'REQUIRES_CONFIRMATION',
                'description': 'High-risk operation requiring confirmation'
            },
            
            # Chat fallback tests
            {
                'input': '你好，今天天气怎么样？',
                'expected_intent': 'LLM',
                'expected_action': 'leave to chat_bot',
                'description': 'Chat fallback'
            }
        ]
    
    def test_rule_engine_classification(self):
        """Test rule engine classification accuracy"""
        print("\n=== Testing Rule Engine Classification ===")
        
        successful_classifications = 0
        total_tests = len(self.test_cases)
        
        for test_case in self.test_cases:
            user_input = test_case['input']
            expected_action = test_case['expected_action']
            
            # Test rule engine classification
            intent, action = self.mock_router.rule_engine.process_input(user_input)
            
            print(f"Input: '{user_input}'")
            print(f"Expected Action: {expected_action}, Actual Action: {action}")
            print(f"Intent: {intent}")
            
            # Check if action matches expected (allowing for some flexibility)
            if action == expected_action:
                successful_classifications += 1
                print("✓ Classification correct")
            else:
                print("✗ Classification mismatch")
            
            print("-" * 50)
        
        accuracy = successful_classifications / total_tests
        print(f"Rule Engine Classification Accuracy: {accuracy:.2%} ({successful_classifications}/{total_tests})")
        self.assertGreater(accuracy, 0.5, "Rule engine classification accuracy should be > 50%")
    
    def test_function_calling_router(self):
        """Test function calling router functionality"""
        print("\n=== Testing Function Calling Router ===")
        
        # Test function router directly
        function_router = function_calling_interface()
        
        test_queries = [
            "设置温度到25度",
            "调节音量到60", 
            "查看电池状态",
            "导航到上海",
            "播放音乐"
        ]
        
        successful_routes = 0
        total_tests = len(test_queries)
        
        for query in test_queries:
            print(f"Testing query: '{query}'")
            
            try:
                success, result = function_router.route_function_call(query)
                print(f"Success: {success}")
                print(f"Result: {result}")
                
                if success:
                    successful_routes += 1
                    print("✓ Function routing successful")
                else:
                    print("✗ Function routing failed")
                    
            except Exception as e:
                print(f"✗ Function routing error: {str(e)}")
            
            print("-" * 50)
        
        accuracy = successful_routes / total_tests
        print(f"Function Calling Router Accuracy: {accuracy:.2%} ({successful_routes}/{total_tests})")
        self.assertGreater(accuracy, 0.3, "Function calling router accuracy should be > 30%")
    
    def test_full_integration_flow(self):
        """Test the complete integration flow"""
        print("\n=== Testing Full Integration Flow ===")
        
        successful_integrations = 0
        total_tests = len(self.test_cases)
        
        for test_case in self.test_cases:
            user_input = test_case['input']
            description = test_case['description']
            
            print(f"Testing: {description}")
            print(f"Input: '{user_input}'")
            
            try:
                # Process through complete pipeline
                response = self.mock_router.process_request(user_input)
                print(f"Final Response: {response}")
                
                # Check if response is reasonable (not an error)
                if not response.startswith("Error:"):
                    successful_integrations += 1
                    print("✓ Integration successful")
                else:
                    print("✗ Integration failed")
                    
            except Exception as e:
                print(f"✗ Integration error: {str(e)}")
            
            print("-" * 50)
        
        accuracy = successful_integrations / total_tests
        print(f"Full Integration Accuracy: {accuracy:.2%} ({successful_integrations}/{total_tests})")
        self.assertGreater(accuracy, 0.6, "Full integration accuracy should be > 60%")
    
    def test_mock_api_validation(self):
        """Test mock API parameter validation"""
        print("\n=== Testing Mock API Validation ===")
        
        # Test valid API calls
        valid_calls = [
            ('battery_module', 'get_battery_status', {}),
            ('climate_module', 'set_cabin_temperature', {'temperature': 22.5, 'zone': 'driver'}),
            ('media_module', 'adjust_volume', {'level': 50}),
        ]
        
        # Test invalid API calls
        invalid_calls = [
            ('climate_module', 'set_cabin_temperature', {'temperature': 'hot', 'zone': 'driver'}),
            ('media_module', 'adjust_volume', {'level': 'loud'}),
            ('climate_module', 'set_cabin_temperature', {'temperature': 22.5}),  # Missing parameter
        ]
        
        # Test valid calls
        valid_successes = 0
        for module_name, function_name, params in valid_calls:
            result = self.mock_api_factory.call_function(module_name, function_name, **params)
            if result['success']:
                valid_successes += 1
                print(f"✓ Valid call succeeded: {module_name}.{function_name}")
            else:
                print(f"✗ Valid call failed: {module_name}.{function_name} - {result['error']}")
        
        # Test invalid calls
        invalid_failures = 0
        for module_name, function_name, params in invalid_calls:
            result = self.mock_api_factory.call_function(module_name, function_name, **params)
            if not result['success']:
                invalid_failures += 1
                print(f"✓ Invalid call correctly rejected: {module_name}.{function_name}")
            else:
                print(f"✗ Invalid call incorrectly accepted: {module_name}.{function_name}")
        
        print(f"Valid calls success rate: {valid_successes}/{len(valid_calls)}")
        print(f"Invalid calls rejection rate: {invalid_failures}/{len(invalid_calls)}")
        
        self.assertEqual(valid_successes, len(valid_calls), "All valid calls should succeed")
        self.assertEqual(invalid_failures, len(invalid_calls), "All invalid calls should be rejected")
    
    def test_error_handling(self):
        """Test error handling throughout the pipeline"""
        print("\n=== Testing Error Handling ===")
        
        error_test_cases = [
            ("", "Empty input"),
            (None, "None input"),
            ("未知的复杂指令", "Unknown command"),
        ]
        
        for test_input, description in error_test_cases:
            print(f"Testing: {description}")
            
            try:
                if test_input is None:
                    # Test None input handling
                    response = self.mock_router.process_request(test_input)
                else:
                    response = self.mock_router.process_request(test_input)
                
                print(f"Response: {response}")
                
                # Error cases should return error messages or handle gracefully
                if test_input == "" or test_input is None:
                    self.assertTrue(response.startswith("Error:"), "Should return error for invalid input")
                    print("✓ Error correctly handled")
                else:
                    print("✓ Response generated (may be error or fallback)")
                    
            except Exception as e:
                print(f"Exception: {str(e)}")
                print("✗ Unhandled exception occurred")
            
            print("-" * 50)


if __name__ == "__main__":
    # Run the tests with verbose output
    unittest.main(verbosity=2)
