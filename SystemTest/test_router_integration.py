"""
System Integration Tests for Router and Rule Engine
Tests the interaction between IntentRouter and RuleBaseEngine components
"""

import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from SystemTest.mock_router import MockRouter
from RuleBaseEngine.RuleBaseEngine import RuleEngine


class TestRouterIntegration(unittest.TestCase):
    """
    Integration tests for Router and Rule Engine interaction
    Uses mock router to avoid LLM dependencies
    """
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Get the parent directory path and construct the rules path
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        rules_path = os.path.join(parent_dir, "RuleBaseEngine", "Rules.json")

        self.mock_router = MockRouter()
        self.rule_engine = RuleEngine(rules_path)
        
        # Test data from test_rulebase_engine.py
        self.device_control_tests = [
            "打开空调",
            "关闭车窗", 
            "调整座椅",
            "启动雨刮",
            "停止大灯"
        ]
        
        self.info_query_tests = [
            "查看当前车速",
            "显示电量",
            "报告油量",
            "当前胎压是多少"
        ]
        
        self.daily_chat_tests = [
            "你好",
            "早上好",
            "谢谢"
        ]
        
        self.system_function_tests = [
            "打开地图",
            "播放周杰伦的歌",
            "今天天气怎么样"
        ]
        
        self.complex_command_tests = [
            "停止所有操作",  # L2 - REQUIRES_CONFIRMATION
            "打开车窗然后关闭"  # L3 - REQUIRES_CONFIRMATION
        ]
    
    def test_device_control_routing(self):
        """Test device control commands routing through the system."""
        print("\n=== Testing Device Control Routing ===")
        
        successful_routes = 0
        total_tests = len(self.device_control_tests)
        
        for test_input in self.device_control_tests:
            # Test rule engine classification
            intent, action = self.rule_engine.process_input(test_input)
            
            # Test router processing
            response = self.mock_router.process_request(test_input)
            
            print(f"Input: '{test_input}' -> Intent: {intent}, Action: {action}")
            print(f"Router Response: {response}")
            
            # Verify expected behavior
            if intent == "device_control" and action == "DIRECT_ALLOW":
                self.assertIn("Operation completed successfully", response)
                successful_routes += 1
            elif action == "REQUIRES_CONFIRMATION":
                self.assertIn("Confirmation required", response)
                successful_routes += 1
            
            print("-" * 50)
        
        accuracy = successful_routes / total_tests
        print(f"Device Control Routing Accuracy: {accuracy:.2%} ({successful_routes}/{total_tests})")
        self.assertGreater(accuracy, 0.5, "Device control routing accuracy should be > 50%")
    
    def test_info_query_routing(self):
        """Test information query commands routing through the system."""
        print("\n=== Testing Info Query Routing ===")
        
        successful_routes = 0
        total_tests = len(self.info_query_tests)
        
        for test_input in self.info_query_tests:
            # Test rule engine classification
            intent, action = self.rule_engine.process_input(test_input)
            
            # Test router processing
            response = self.mock_router.process_request(test_input)
            
            print(f"Input: '{test_input}' -> Intent: {intent}, Action: {action}")
            print(f"Router Response: {response}")
            
            # Verify expected behavior
            if intent == "info_query" and action == "DIRECT_ALLOW":
                self.assertIn("Operation completed successfully", response)
                successful_routes += 1
            elif intent == "LLM":
                self.assertIn("Mock chat response", response)
                successful_routes += 1
            
            print("-" * 50)
        
        accuracy = successful_routes / total_tests
        print(f"Info Query Routing Accuracy: {accuracy:.2%} ({successful_routes}/{total_tests})")
        self.assertGreater(accuracy, 0.5, "Info query routing accuracy should be > 50%")
    
    def test_system_function_routing(self):
        """Test system function commands routing through the system."""
        print("\n=== Testing System Function Routing ===")
        
        successful_routes = 0
        total_tests = len(self.system_function_tests)
        
        for test_input in self.system_function_tests:
            # Test rule engine classification
            intent, action = self.rule_engine.process_input(test_input)
            
            # Test router processing
            response = self.mock_router.process_request(test_input)
            
            print(f"Input: '{test_input}' -> Intent: {intent}, Action: {action}")
            print(f"Router Response: {response}")
            
            # Verify expected behavior
            if intent.startswith("system_") and action == "DIRECT_ALLOW":
                self.assertIn("Operation completed successfully", response)
                successful_routes += 1
            elif action == "REQUIRES_CONFIRMATION":
                self.assertIn("Confirmation required", response)
                successful_routes += 1
            
            print("-" * 50)
        
        accuracy = successful_routes / total_tests
        print(f"System Function Routing Accuracy: {accuracy:.2%} ({successful_routes}/{total_tests})")
        self.assertGreater(accuracy, 0.5, "System function routing accuracy should be > 50%")
    
    def test_risk_level_handling(self):
        """Test risk level handling in router."""
        print("\n=== Testing Risk Level Handling ===")
        
        for test_input in self.complex_command_tests:
            # Test rule engine classification
            intent, action = self.rule_engine.process_input(test_input)
            
            # Test router processing
            response = self.mock_router.process_request(test_input)
            
            print(f"Input: '{test_input}' -> Intent: {intent}, Action: {action}")
            print(f"Router Response: {response}")
            
            # Verify risk handling
            if action == "REQUIRES_CONFIRMATION":
                self.assertIn("Confirmation required", response)
            elif action == "HIGH_RISK_FORBIDDEN":
                self.assertIn("Operation blocked", response)
            
            print("-" * 50)
    
    def test_llm_fallback_routing(self):
        """Test LLM fallback routing for chat inputs."""
        print("\n=== Testing LLM Fallback Routing ===")
        
        for test_input in self.daily_chat_tests:
            # Test rule engine classification
            intent, action = self.rule_engine.process_input(test_input)
            
            # Test router processing
            response = self.mock_router.process_request(test_input)
            
            print(f"Input: '{test_input}' -> Intent: {intent}, Action: {action}")
            print(f"Router Response: {response}")
            
            # Verify LLM fallback or direct chat handling
            if intent == "LLM" and action == "leave to chat_bot":
                self.assertIn("Mock chat response", response)
            elif intent == "daily_chat":
                self.assertIn("Operation completed successfully", response)
            
            print("-" * 50)
    
    def test_input_validation(self):
        """Test input validation in router."""
        print("\n=== Testing Input Validation ===")
        
        # Test empty input
        response = self.mock_router.process_request("")
        self.assertIn("Error: Empty input provided", response)
        print(f"Empty input test: {response}")
        
        # Test non-string input
        response = self.mock_router.process_request(None)
        self.assertIn("Error: Input must be a string", response)
        print(f"Non-string input test: {response}")
        
        print("Input validation tests passed")
    
    def test_overall_integration(self):
        """Test overall system integration with mixed inputs."""
        print("\n=== Testing Overall Integration ===")
        
        mixed_test_cases = [
            ("打开空调", "device_control", "DIRECT_ALLOW"),
            ("查看当前车速", "info_query", "DIRECT_ALLOW"),
            ("你好", "daily_chat", "DIRECT_ALLOW"),
            ("停止所有操作", "complex_command", "REQUIRES_CONFIRMATION")
        ]
        
        successful_integrations = 0
        total_tests = len(mixed_test_cases)
        
        for test_input, expected_intent, expected_action in mixed_test_cases:
            # Test rule engine classification
            intent, action = self.rule_engine.process_input(test_input)
            
            # Test router processing
            response = self.mock_router.process_request(test_input)
            
            print(f"Input: '{test_input}'")
            print(f"Expected: Intent={expected_intent}, Action={expected_action}")
            print(f"Actual: Intent={intent}, Action={action}")
            print(f"Router Response: {response}")
            
            # Check if integration works correctly
            if action == expected_action:
                if action == "DIRECT_ALLOW" and "Operation completed successfully" in response:
                    successful_integrations += 1
                elif action == "REQUIRES_CONFIRMATION" and "Confirmation required" in response:
                    successful_integrations += 1
                elif action == "HIGH_RISK_FORBIDDEN" and "Operation blocked" in response:
                    successful_integrations += 1
            
            print("-" * 50)
        
        accuracy = successful_integrations / total_tests
        print(f"Overall Integration Accuracy: {accuracy:.2%} ({successful_integrations}/{total_tests})")
        self.assertGreater(accuracy, 0.7, "Overall integration accuracy should be > 70%")


if __name__ == "__main__":
    # Run the tests with verbose output
    unittest.main(verbosity=2)
