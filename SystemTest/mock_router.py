"""
Mock Router for System Testing
This mock router simulates the IntentRouter functionality without LLM dependencies
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from RuleBaseEngine.RuleBaseEngine import RuleEngine
from typing import Tuple, Dict, Any


class MockRouter:
    """Mock router that simulates IntentRouter without LLM dependencies"""
    
    def __init__(self, rules_path: str = None):
        """
        Initialize the Mock Router with rule engine only
        
        Args:
            rules_path: Path to the Rules.json file
        """
        try:
            # Set default rules path if not provided
            if rules_path is None:
                # Get the parent directory path and construct the rules path
                parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                rules_path = os.path.join(parent_dir, "RuleBaseEngine", "Rules.json")

            # Initialize rule engine
            self.rule_engine = RuleEngine(rules_path)
            
            # Risk level mapping for explanations (matching updated IntentRouter.py)
            self.risk_explanations = {
                "HIGH_RISK_FORBIDDEN": "This operation is classified as high-risk and has been blocked for security reasons.",
                "REQUIRES_CONFIRMATION": "This operation requires additional confirmation due to security policies.",
                "DIRECT_ALLOW": "This operation is approved and can be executed directly."
            }
            
            # Mock function registry for testing
            self.mock_functions = {
                "device_control": ["air_conditioner_control", "window_control", "seat_control"],
                "info_query": ["speed_query", "battery_query", "fuel_query"],
                "system_app_launch": ["navigation_app", "music_app"],
                "system_web_service": ["weather_service", "stock_service"],
                "system_file_access": ["media_player"]
            }
            
        except Exception as e:
            raise Exception(f"Mock Router initialization failed: {str(e)}")
    
    def _mock_function_call(self, intent_type: str, user_input: str) -> Tuple[bool, str]:
        """
        Mock function call that simulates successful execution
        
        Returns:
            Tuple[bool, str]: (success, result_message)
        """
        try:
            # Simulate function selection based on intent type
            if intent_type in self.mock_functions:
                function_name = self.mock_functions[intent_type][0]  # Use first function as default
                return True, f"Mock function '{function_name}' executed successfully for input: '{user_input}'"
            elif intent_type.startswith("system_"):
                # Handle system functions
                system_type = intent_type.replace("system_", "")
                if system_type in self.mock_functions:
                    function_name = self.mock_functions[system_type][0]
                    return True, f"Mock system function '{function_name}' executed successfully"
                else:
                    return True, f"Mock system function executed for {system_type}"
            elif intent_type.startswith("dialogue_"):
                return True, f"Mock dialogue function executed for {intent_type}"
            else:
                return True, f"Mock function executed for intent: {intent_type}"
                
        except Exception as e:
            return False, f"Mock function call failed: {str(e)}"
    
    def _mock_chat_response(self, user_input: str) -> str:
        """Mock chat response for LLM fallback cases"""
        return f"Mock chat response for: '{user_input}'. This would normally be handled by the LLM."
    
    def process_request(self, user_input: str) -> str:
        """
        Main method to process user requests (mock version)
        
        Args:
            user_input: User's text input
            
        Returns:
            str: Response string or error message with "Error: " prefix
        """
        try:
            # Validate input
            if not isinstance(user_input, str):
                return "Error: Input must be a string"
            
            if not user_input.strip():
                return "Error: Empty input provided"
            
            # Pass to rule base engine
            print(f"Processing user input: {user_input}")
            intent_type, action = self.rule_engine.process_input(user_input)
            
            print(f"Rule engine response - Intent: {intent_type}, Action: {action}")
            
            # Check if should leave to LLM (mock response)
            if intent_type == "LLM" and action == "leave to chat_bot":
                print("Routing to mock LLM for chat")
                return self._mock_chat_response(user_input)
            
            # Check risk level
            if action == "HIGH_RISK_FORBIDDEN":
                reason = self.risk_explanations.get(action, "High-risk operation blocked")
                print(f"High-risk operation blocked: {user_input}")
                return f"Operation blocked: {reason}"
            
            # For operations requiring confirmation
            if action == "REQUIRES_CONFIRMATION":
                confirmation_msg = self.risk_explanations.get(action, "Operation requires confirmation")
                print(f"Operation requires confirmation: {user_input}")
                return f"Confirmation required: {confirmation_msg} Please confirm if you want to proceed."
            
            # For approved operations
            if action == "DIRECT_ALLOW":
                # Mock function execution
                success, result = self._mock_function_call(intent_type, user_input)
                
                if success:
                    print(f"Mock function execution successful for intent: {intent_type}")
                    return f"Operation completed successfully. {result}"
                else:
                    print(f"Mock function execution failed for intent: {intent_type}")
                    return f"Error: {result}"
            
            # Unknown action
            return f"Error: Unknown action type: {action}"
            
        except Exception as e:
            error_msg = f"Mock Router processing error: {str(e)}"
            print(error_msg)
            return f"Error: {error_msg}"
    
    def update_risk_mapping(self, new_mapping: Dict[str, str]):
        """Update risk level mapping in rule engine"""
        try:
            self.rule_engine.update_risk_mapping(new_mapping)
            print("Risk mapping updated successfully")
        except Exception as e:
            print(f"Error updating risk mapping: {str(e)}")


# Test the mock router
if __name__ == "__main__":
    try:
        # Initialize mock router
        router = MockRouter()
        
        # Test cases
        test_inputs = [
            "打开空调",
            "查看当前车速", 
            "你好",
            "停止所有操作",
            "讲个笑话"
        ]
        
        print("=== Mock Router Testing ===")
        for test_input in test_inputs:
            print(f"\nInput: {test_input}")
            response = router.process_request(test_input)
            print(f"Response: {response}")
            print("-" * 50)
            
    except Exception as e:
        print(f"Mock Router test failed: {str(e)}")
