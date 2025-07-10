import unittest
import sys
import os

# Add the current directory to the path so we can import RuleBaseEngine
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from RuleBaseEngine import RuleEngine

device_control_tests = [
    "打开空调",
    "关闭车窗",
    "调整座椅",
    "启动雨刮",
    "停止大灯",
    "升高天窗",
    "降低氛围灯亮度",
    "打开后备箱",
    "调整空调温度到26度",
    "把座椅加热设为高档",
    "关闭座椅加热功能",
    "车窗打开一半"
]

info_query_tests = [
    "查看当前车速",
    "显示电量",
    "报告油量",
    "当前胎压是多少",
    "剩余续航里程",
    "车内温度多少",
    "现在时间",
    "显示已行驶里程",
    "电量还有多少",
    "剩余油量查询"
]

daily_chat_tests = [
    "你好",
    "早上好",
    "谢谢",
    "再见",
    "讲个笑话",
    "和我聊天吧",
    "我们对话一下"
]

system_function_tests = [
    # App Launch
    "导航到最近的加油站",
    "打开地图",
    "导我到附近的商场",
    "播放周杰伦的歌",
    "暂停音乐",
    "下一首",
    "上一曲",

    # File Access
    "播放本地音乐",
    "打开U盘里的视频",
    "播放SD卡中的照片",

    # Web Service
    "今天天气怎么样",
    "查询明天气象情况",
    "查看阿里巴巴股票",
    "今日股价行情"
]

dialogue_management_tests = [
    # Context Rules
    "刚才说到哪了",
    "之前的操作再做一次",
    "上面提到的事情",
    "继续刚才的话题",

    # Termination Rules
    "退出对话",
    "结束当前会话",
    "关闭对话"
]

denied_operations_tests = [
    # Denied Devices
    "调整方向盘",
    "踩刹车",
    "松开油门",
    "换档位",
    "拉手刹",

    # Denied Sensors
    "查看倒车雷达",
    "显示行车记录仪"
]

mixed_tests = [
    # Combined intents
    "打开空调，查询当前温度",
    "导航到家，同时播放音乐",
    "车速多少，然后调整空调温度",

    # Edge cases
    "空调",  # Just a device name without action
    "打开",  # Just an action without device
    "这是一个完全无法匹配任何规则的随机输入句子",
    "$$%^&*",  # Special characters
    "",  # Empty string
    "把方向盘往左打30度",  # Denied device with specific value
    "123456789"  # Just numbers
]

risk_level_tests = [
    # Tests targeting specific risk levels
    "停止所有操作",  # L2
    "打开车窗然后关闭",  # L3 complex command
    "调整空调温度",  # L4
    "查看当前车速",  # L5

    # Tests for entity values
    "把空调温度调到25度",
    "调整座椅到高档",
    "车窗打开半开"
]


class TestRuleBaseEngine(unittest.TestCase):
    """
    Comprehensive unit tests for RuleBaseEngine
    Tests accuracy of intent classification and risk assessment
    """

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.engine = RuleEngine("Rules.json")

        # Pass criteria dictionary - stores minimum accuracy threshold for each test
        # All values initially set to 0.5 (50%) as requested
        self.pass_criteria = {
            "device_control": 0.5,
            "info_query": 0.5,
            "daily_chat": 0.5,
            "system_function": 0.5,
            "dialogue_management": 0.5,
            "risk_level_assessment": 0.5,
            "edge_cases": 0.5,
            "mixed_commands": 0.5,
            "overall_accuracy": 0.5,
            "risk_mapping_update": 1.0  # This should always pass (100%)
        }

        # Expected results for accuracy calculation
        self.expected_results = {
            # Device control tests - should be classified as device_control with L4 risk
            "device_control": {
                "inputs": device_control_tests,
                "expected_intent": "device_control",
                "expected_action": "DIRECT_ALLOW"
            },

            # Info query tests - should be classified as info_query with L5 risk
            "info_query": {
                "inputs": info_query_tests,
                "expected_intent": "info_query",
                "expected_action": "DIRECT_ALLOW"
            },

            # Daily chat tests - should be classified as daily_chat with L5 risk
            "daily_chat": {
                "inputs": daily_chat_tests,
                "expected_intent": "daily_chat",
                "expected_action": "DIRECT_ALLOW"
            },

            # System function tests - should be classified as system_* with various risks
            "system_function": {
                "inputs": system_function_tests,
                "expected_intent_prefix": "system_",
                "expected_actions": ["DIRECT_ALLOW", "DIRECT_ALLOW"]  # Most should be L4/L5
            },

            # Dialogue management tests
            "dialogue_management": {
                "inputs": dialogue_management_tests,
                "expected_intent_prefix": "dialogue_",
                "expected_action": "DIRECT_ALLOW"
            },

            # Denied operations - should be classified but with high risk
            "denied_operations": {
                "inputs": denied_operations_tests,
                "expected_intent": "LLM",  # Should not match patterns, go to LLM
                "expected_action": "leave to chat_bot"
            }
        }

    def check_pass_criteria(self, test_name, accuracy):
        """
        Check if a test passes based on the pass criteria dictionary.

        Args:
            test_name (str): Name of the test (key in pass_criteria dictionary)
            accuracy (float): Achieved accuracy (0.0 to 1.0)

        Returns:
            bool: True if test passes, False otherwise
        """
        threshold = self.pass_criteria.get(test_name, 0.5)  # Default to 50% if not found
        return accuracy >= threshold

    def print_test_result(self, test_name, accuracy, correct, total):
        """
        Print formatted test results with pass/fail status.

        Args:
            test_name (str): Name of the test
            accuracy (float): Achieved accuracy (0.0 to 1.0)
            correct (int): Number of correct predictions
            total (int): Total number of test cases
        """
        threshold = self.pass_criteria.get(test_name, 0.5)
        status = "PASS" if self.check_pass_criteria(test_name, accuracy) else "FAIL"

        print(f"{test_name.replace('_', ' ').title()} Accuracy: {accuracy:.2%} ({correct}/{total})")
        print(f"Threshold: {threshold:.1%} | Status: {status}")
        print("-" * 50)

    def test_device_control_classification(self):
        """Test device control intent classification accuracy."""
        correct_predictions = 0
        total_tests = len(device_control_tests)

        for test_input in device_control_tests:
            result = self.engine.process_input(test_input)
            intent, action = result

            # Check if intent is correctly classified as device_control
            if intent == "device_control" and action == "DIRECT_ALLOW":
                correct_predictions += 1

            print(f"Device Control - Input: '{test_input}' -> Intent: {intent}, Action: {action}")

        accuracy = correct_predictions / total_tests
        self.print_test_result("device_control", accuracy, correct_predictions, total_tests)

        # Assert accuracy meets pass criteria
        assert self.check_pass_criteria("device_control", accuracy), \
            f"Device control accuracy {accuracy:.2%} is below {self.pass_criteria['device_control']:.1%} threshold"

    def test_info_query_classification(self):
        """Test information query intent classification accuracy."""
        correct_predictions = 0
        total_tests = len(info_query_tests)

        for test_input in info_query_tests:
            result = self.engine.process_input(test_input)
            intent, action = result

            # Check if intent is correctly classified as info_query
            if intent == "info_query" and action == "DIRECT_ALLOW":
                correct_predictions += 1

            print(f"Info Query - Input: '{test_input}' -> Intent: {intent}, Action: {action}")

        accuracy = correct_predictions / total_tests
        self.print_test_result("info_query", accuracy, correct_predictions, total_tests)

        # Assert accuracy meets pass criteria
        assert self.check_pass_criteria("info_query", accuracy), \
            f"Info query accuracy {accuracy:.2%} is below {self.pass_criteria['info_query']:.1%} threshold"
    def test_daily_chat_classification(self):
        """Test daily chat intent classification accuracy."""
        correct_predictions = 0
        total_tests = len(daily_chat_tests)

        for test_input in daily_chat_tests:
            result = self.engine.process_input(test_input)
            intent, action = result

            # Check if intent is correctly classified as daily_chat
            if intent == "daily_chat" and action == "DIRECT_ALLOW":
                correct_predictions += 1

            print(f"Daily Chat - Input: '{test_input}' -> Intent: {intent}, Action: {action}")

        accuracy = correct_predictions / total_tests
        self.print_test_result("daily_chat", accuracy, correct_predictions, total_tests)

        # Assert accuracy meets pass criteria
        assert self.check_pass_criteria("daily_chat", accuracy), \
            f"Daily chat accuracy {accuracy:.2%} is below {self.pass_criteria['daily_chat']:.1%} threshold"

    def test_system_function_classification(self):
        """Test system function intent classification accuracy."""
        correct_predictions = 0
        total_tests = len(system_function_tests)

        for test_input in system_function_tests:
            result = self.engine.process_input(test_input)
            intent, action = result

            # Check if intent starts with "system_" (system function classification)
            if intent.startswith("system_") and action in ["DIRECT_ALLOW"]:
                correct_predictions += 1

            print(f"System Function - Input: '{test_input}' -> Intent: {intent}, Action: {action}")

        accuracy = correct_predictions / total_tests
        self.print_test_result("system_function", accuracy, correct_predictions, total_tests)

        # Assert accuracy meets pass criteria
        assert self.check_pass_criteria("system_function", accuracy), \
            f"System function accuracy {accuracy:.2%} is below {self.pass_criteria['system_function']:.1%} threshold"

    def test_dialogue_management_classification(self):
        """Test dialogue management intent classification accuracy."""
        correct_predictions = 0
        total_tests = len(dialogue_management_tests)

        for test_input in dialogue_management_tests:
            result = self.engine.process_input(test_input)
            intent, action = result

            # Check if intent starts with "dialogue_"
            if intent.startswith("dialogue_") and action == "DIRECT_ALLOW":
                correct_predictions += 1

            print(f"Dialogue Management - Input: '{test_input}' -> Intent: {intent}, Action: {action}")

        accuracy = correct_predictions / total_tests
        self.print_test_result("dialogue_management", accuracy, correct_predictions, total_tests)

        # Assert accuracy meets pass criteria
        assert self.check_pass_criteria("dialogue_management", accuracy), \
            f"Dialogue management accuracy {accuracy:.2%} is below {self.pass_criteria['dialogue_management']:.1%} threshold"

    def test_risk_level_assessment(self):
        """Test risk level assessment for different types of commands."""
        risk_test_cases = [
            ("停止所有操作", "complex_command", "REQUIRES_CONFIRMATION"),  # L2
            ("打开车窗然后关闭", "complex_command", "REQUIRES_CONFIRMATION"),  # L3
            ("调整空调温度", "device_control", "DIRECT_ALLOW"),  # L4
            ("查看当前车速", "info_query", "DIRECT_ALLOW"),  # L5
        ]

        correct_predictions = 0
        total_tests = len(risk_test_cases)

        for test_input, expected_intent, expected_action in risk_test_cases:
            result = self.engine.process_input(test_input)
            intent, action = result

            # Check if both intent and action match expectations
            if intent == expected_intent and action == expected_action:
                correct_predictions += 1

            print(f"Risk Assessment - Input: '{test_input}' -> Intent: {intent}, Action: {action} (Expected: {expected_intent}, {expected_action})")

        accuracy = correct_predictions / total_tests
        self.print_test_result("risk_level_assessment", accuracy, correct_predictions, total_tests)

        # Assert accuracy meets pass criteria
        assert self.check_pass_criteria("risk_level_assessment", accuracy), \
            f"Risk assessment accuracy {accuracy:.2%} is below {self.pass_criteria['risk_level_assessment']:.1%} threshold"

    def test_edge_cases(self):
        """Test edge cases and mixed inputs."""
        edge_cases = [
            ("", "LLM", "leave to chat_bot"),  # Empty string
            ("空调", "LLM", "leave to chat_bot"),  # Just device name
            ("打开", "LLM", "leave to chat_bot"),  # Just action
            ("$$%^&*", "LLM", "leave to chat_bot"),  # Special characters
            ("123456789", "LLM", "leave to chat_bot"),  # Just numbers
        ]

        correct_predictions = 0
        total_tests = len(edge_cases)

        for test_input, expected_intent, expected_action in edge_cases:
            result = self.engine.process_input(test_input)
            intent, action = result

            if intent == expected_intent and action == expected_action:
                correct_predictions += 1

            print(f"Edge Case - Input: '{test_input}' -> Intent: {intent}, Action: {action}")

        accuracy = correct_predictions / total_tests
        self.print_test_result("edge_cases", accuracy, correct_predictions, total_tests)

        # Assert accuracy meets pass criteria
        assert self.check_pass_criteria("edge_cases", accuracy), \
            f"Edge cases accuracy {accuracy:.2%} is below {self.pass_criteria['edge_cases']:.1%} threshold"

    def test_mixed_commands(self):
        """Test mixed and complex commands."""
        mixed_cases = [
            ("打开空调，查询当前温度", "complex_command", "REQUIRES_CONFIRMATION"),  # Complex command with 然后
            ("导航到家，同时播放音乐", "complex_command", "REQUIRES_CONFIRMATION"),  # Complex command with 同时
            ("这是一个完全无法匹配任何规则的随机输入句子", "complex_command", "REQUIRES_CONFIRMATION"),  # Long sentence > 8 chars
        ]

        correct_predictions = 0
        total_tests = len(mixed_cases)

        for test_input, expected_intent, expected_action in mixed_cases:
            result = self.engine.process_input(test_input)
            intent, action = result

            # For mixed commands, we expect either the expected result or LLM fallback
            if (intent == expected_intent and action == expected_action) or (intent == "LLM" and action == "leave to chat_bot"):
                correct_predictions += 1

            print(f"Mixed Command - Input: '{test_input}' -> Intent: {intent}, Action: {action}")

        accuracy = correct_predictions / total_tests
        self.print_test_result("mixed_commands", accuracy, correct_predictions, total_tests)

        # Assert accuracy meets pass criteria
        assert self.check_pass_criteria("mixed_commands", accuracy), \
            f"Mixed commands accuracy {accuracy:.2%} is below {self.pass_criteria['mixed_commands']:.1%} threshold"

    def test_overall_accuracy(self):
        """Test overall system accuracy across all test categories."""
        all_test_cases = []

        # Add all test cases with expected results
        for test_input in device_control_tests:
            all_test_cases.append((test_input, "device_control", "DIRECT_ALLOW"))

        for test_input in info_query_tests:
            all_test_cases.append((test_input, "info_query", "DIRECT_ALLOW"))

        for test_input in daily_chat_tests:
            all_test_cases.append((test_input, "daily_chat", "DIRECT_ALLOW"))

        # For system functions, we expect system_* prefix
        for test_input in system_function_tests:
            all_test_cases.append((test_input, "system_", "DIRECT_ALLOW"))  # Prefix match

        # For dialogue management, we expect dialogue_* prefix
        for test_input in dialogue_management_tests:
            all_test_cases.append((test_input, "dialogue_", "DIRECT_ALLOW"))  # Prefix match

        correct_predictions = 0
        total_tests = len(all_test_cases)

        for test_input, expected_intent, expected_action in all_test_cases:
            result = self.engine.process_input(test_input)
            intent, action = result

            # Check if prediction matches expectation
            if expected_intent.endswith("_"):  # Prefix match
                if intent.startswith(expected_intent) and action == expected_action:
                    correct_predictions += 1
            else:  # Exact match
                if intent == expected_intent and action == expected_action:
                    correct_predictions += 1

        accuracy = correct_predictions / total_tests
        print(f"\n=== OVERALL SYSTEM ACCURACY ===")
        print(f"Total Test Cases: {total_tests}")
        print(f"Correct Predictions: {correct_predictions}")
        print(f"Overall Accuracy: {accuracy:.2%}")
        threshold = self.pass_criteria.get("overall_accuracy", 0.5)
        status = "PASS" if self.check_pass_criteria("overall_accuracy", accuracy) else "FAIL"
        print(f"Threshold: {threshold:.1%} | Status: {status}")
        print(f"=== END OVERALL RESULTS ===\n")

        # Assert overall accuracy meets pass criteria
        assert self.check_pass_criteria("overall_accuracy", accuracy), \
            f"Overall system accuracy {accuracy:.2%} is below {self.pass_criteria['overall_accuracy']:.1%} threshold"

    def test_risk_mapping_update(self):
        """Test the risk mapping update functionality."""
        # Test original mapping
        result = self.engine.process_input("调整空调温度")
        original_intent, original_action = result

        # Update risk mapping
        self.engine.update_risk_mapping({
            "L4": "REQUIRES_CONFIRMATION"  # Change L4 from DIRECT_ALLOW to REQUIRES_CONFIRMATION
        })

        # Test updated mapping
        result = self.engine.process_input("调整空调温度")
        updated_intent, updated_action = result

        # Verify the mapping was updated
        assert original_action == "DIRECT_ALLOW", f"Original action should be DIRECT_ALLOW, got {original_action}"
        assert updated_action == "REQUIRES_CONFIRMATION", f"Updated action should be REQUIRES_CONFIRMATION, got {updated_action}"

        print(f"Risk Mapping Update Test - Original: {original_action}, Updated: {updated_action}")

    def display_pass_criteria(self):
        """Display all pass criteria thresholds."""
        print("\n=== PASS CRITERIA THRESHOLDS ===")
        for test_name, threshold in self.pass_criteria.items():
            print(f"{test_name.replace('_', ' ').title()}: {threshold:.1%}")
        print("=== END PASS CRITERIA ===\n")


if __name__ == "__main__":
    # Run the tests
    unittest.main(verbosity=2)
