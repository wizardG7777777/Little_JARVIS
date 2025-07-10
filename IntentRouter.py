import json
import os
import sys
from typing import Tuple, Dict, Any


class Router:
    def __init__(self, rules_path: str = "Rules.json", registration_path: str = None):
        """
        Initialize the Router with rule engine and function registry

        Args:
            rules_path: Path to the Rules.json file
            registration_path: Path to RegistrationTemplate.json file (auto-detected if None)
        """
        try:
            # Import required modules
            from RuleBaseEngine.RuleBaseEngine import RuleEngine
            from ChatBots.LocalChatBot import LocalChatBot

            # Initialize rule engine
            self.rule_engine = RuleEngine(rules_path)

            # Initialize local LLM
            self.local_llm = LocalChatBot()

            # Load function registry
            if registration_path is None:
                registration_path = self._get_registration_path()

            self.function_registry = self._load_function_registry(registration_path)

            # Risk level mapping for explanations (updated to match RuleBaseEngine.py)
            self.risk_explanations = {
                "HIGH_RISK_FORBIDDEN": "This operation is classified as high-risk and has been blocked for security reasons.",
                "REQUIRES_CONFIRMATION": "This operation requires additional confirmation due to security policies.",
                "DIRECT_ALLOW": "This operation is approved and can be executed directly."
            }

        except Exception as e:
            raise Exception(f"Router initialization failed: {str(e)}")

    def _get_registration_path(self) -> str:
        """Auto-detect RegistrationTemplate.json path based on OS"""
        if os.name == 'nt':  # Windows
            return "\\RegistryModule\\RegistrationTemplate.json"
        else:  # Unix-like systems
            return "/RegistryModule/RegistrationTemplate.json"

    def _load_function_registry(self, registration_path: str) -> Dict[str, Any]:
        """Load function registry from JSON file"""
        try:
            # Handle both absolute and relative paths
            if not os.path.isabs(registration_path):
                registration_path = os.path.join(os.getcwd(), registration_path.lstrip('/\\'))

            with open(registration_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise Exception(f"Registration file not found: {registration_path}")
        except json.JSONDecodeError:
            raise Exception(f"Invalid JSON format in registration file: {registration_path}")

    def _function_exists(self, function_name: str) -> bool:
        """Check if function exists in registry"""
        for module in self.function_registry.get("modules", []):
            for function in module.get("functions", []):
                if function.get("function_name") == function_name:
                    return True
        return False

    def _extract_function_name(self, intent_type: str, user_input: str) -> str:
        """Extract function name from intent type and user input"""
        try:
            # Use LLM to extract function name based on intent
            function_name = self.local_llm.intent_phrase(user_input)
            return function_name if function_name else ""
        except Exception as e:
            print(f"Error extracting function name: {str(e)}")
            return ""

    def _call_function(self, user_query: str, function_name: str) -> Tuple[bool, str]:
        """
        Call function and return success status and result

        Returns:
            Tuple[bool, str]: (success, result_or_error_message)
        """
        try:
            if not function_name:
                return False, "No function name provided"

            # Check if function exists in registry
            if self._function_exists(function_name):
                result = self.local_llm.function_call(user_query, function_name)
                return True, result
            else:
                # Try unknown function call
                result = self.local_llm.unknown_function_call(user_query, function_name)
                return True, result

        except Exception as e:
            return False, f"Function call failed: {str(e)}"

    def _generate_response(self, intent_type: str, function_name: str,
                           success: bool, result: str, user_input: str) -> str:
        """Generate appropriate response based on function execution result"""
        if success:
            if function_name:
                return f"Function '{function_name}' executed successfully. Result: {result}"
            else:
                return f"Operation completed successfully. Result: {result}"
        else:
            if function_name:
                return f"Function '{function_name}' execution failed. Error: {result}"
            else:
                return f"Operation failed. Error: {result}"

    def process_request(self, user_input: str) -> str:
        """
        Main method to process user requests

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

            # Check if should leave to LLM
            if intent_type == "LLM" and action == "leave to chat_bot":
                print("Routing to local LLM for chat")
                try:
                    llm_response = self.local_llm.chat(user_input)
                    return llm_response
                except Exception as e:
                    return f"Error: LLM processing failed: {str(e)}"

            # Check risk level (updated to match RuleBaseEngine.py)
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
                # Extract function name
                function_name = self._extract_function_name(intent_type, user_input)
                print(f"Extracted function name: {function_name}")

                # Call function
                success, result = self._call_function(user_input, function_name)

                if success:
                    print(f"Function execution successful: {function_name}")
                    return self._generate_response(intent_type, function_name, True, result, user_input)
                else:
                    print(f"Function execution failed: {function_name}")
                    return f"Error: {result}"

            # Unknown action
            return f"Error: Unknown action type: {action}"

        except Exception as e:
            error_msg = f"Router processing error: {str(e)}"
            print(error_msg)
            return f"Error: {error_msg}"

    def update_risk_mapping(self, new_mapping: Dict[str, str]):
        """Update risk level mapping in rule engine"""
        try:
            self.rule_engine.update_risk_mapping(new_mapping)
            print("Risk mapping updated successfully")
        except Exception as e:
            print(f"Error updating risk mapping: {str(e)}")


# Example usage and testing
if __name__ == "__main__":
    try:
        # Initialize router
        router = Router()

        # Test cases
        test_inputs = [
            "打开空调",
            "查看当前车速",
            "你好",
            "停止所有操作",
            "讲个笑话"
        ]

        print("=== Router Testing ===")
        for test_input in test_inputs:
            print(f"\nInput: {test_input}")
            response = router.process_request(test_input)
            print(f"Response: {response}")
            print("-" * 50)

    except Exception as e:
        print(f"Router test failed: {str(e)}")