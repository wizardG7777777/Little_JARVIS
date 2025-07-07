"""
RuleBaseEngine - A rule-based intent classification and risk assessment engine

Chinese to English Term Mapping:
- 高危禁止 -> HIGH_RISK_FORBIDDEN
- 需二次确认 -> REQUIRES_CONFIRMATION
- 直接放行 -> DIRECT_ALLOW

Risk Level Descriptions:
- L1: HIGH_RISK_FORBIDDEN - Maximum risk, operation forbidden
- L2: REQUIRES_CONFIRMATION - High risk, requires secondary confirmation
- L3: REQUIRES_CONFIRMATION - Medium risk, requires secondary confirmation
- L4: DIRECT_ALLOW - Low risk, direct operation allowed
- L5: DIRECT_ALLOW - No risk, direct operation allowed
"""

import json
import re


class RuleEngine:
    def __init__(self, rules_file_path):
        # Load rules from the JSON file
        with open(rules_file_path, 'r', encoding='utf-8') as f:
            self.rules = json.load(f)

        # Initialize the risk level mapping dictionary
        self.risk_level_mapping = {
            "L1": "HIGH_RISK_FORBIDDEN",
            "L2": "REQUIRES_CONFIRMATION",
            "L3": "REQUIRES_CONFIRMATION",
            "L4": "DIRECT_ALLOW",
            "L5": "DIRECT_ALLOW"
        }

    def process_input(self, text):
        """
        Process user input and return a tuple of (intent, action)

        Args:
            text (str): User input text

        Returns:
            tuple: (intent_type, action) or (LLM, "leave to chat_bot") if no match
        """
        # Try to match user input with rules
        intent_result = self.classify_intent(text)

        if intent_result:
            intent_type = intent_result["intent_type"]
            risk_level = intent_result["risk_level"]
            action = self.risk_level_mapping.get(risk_level, "DIRECT_ALLOW")
            return intent_type, action
        else:
            # If no match is found, return for LLM processing
            return "LLM", "leave to chat_bot"

    def classify_intent(self, text):
        """
        Classify user intent based on defined rules

        Args:
            text (str): User input text

        Returns:
            dict: Information about the matched intent or None if no match
        """
        matched_intents = []

        # Check all patterns in intent_classifier
        intent_classifier = self.rules.get("intent_classifier", {})
        for intent_type, patterns in intent_classifier.items():
            for pattern_info in patterns:
                if "pattern" in pattern_info and re.search(pattern_info["pattern"], text):
                    matched_intents.append({
                        "intent_type": intent_type,
                        "priority": pattern_info.get("priority", 10),
                        "risk_level": pattern_info.get("risk_level", "L5"),
                        "type": pattern_info.get("type", "regular")
                    })
                elif "condition" in pattern_info and "length > " in pattern_info["condition"]:
                    length_limit = int(pattern_info["condition"].split("length > ")[1])
                    if len(text) > length_limit:
                        matched_intents.append({
                            "intent_type": intent_type,
                            "priority": pattern_info.get("priority", 10),
                            "risk_level": pattern_info.get("risk_level", "L5"),
                            "type": pattern_info.get("type", "regular")
                        })

        # Check system_function patterns
        system_function = self.rules.get("system_function", {})
        for func_type, patterns in system_function.items():
            for pattern_info in patterns:
                if "pattern" in pattern_info and re.search(pattern_info["pattern"], text):
                    matched_intents.append({
                        "intent_type": f"system_{func_type}",
                        "priority": 3,  # Default priority for system functions
                        "risk_level": pattern_info.get("risk_level", "L5"),
                        "action": pattern_info.get("action", "")
                    })

        # Check dialogue_management patterns
        dialogue_management = self.rules.get("dialogue_management", {})
        for dialogue_type, patterns in dialogue_management.items():
            for pattern_info in patterns:
                if "pattern" in pattern_info and re.search(pattern_info["pattern"], text):
                    matched_intents.append({
                        "intent_type": f"dialogue_{dialogue_type}",
                        "priority": 2,  # High priority for dialogue management
                        "risk_level": pattern_info.get("risk_level", "L5"),
                        "action": pattern_info.get("action", "")
                    })

        # Sort by priority (lower number = higher priority)
        if matched_intents:
            matched_intents.sort(key=lambda x: x.get("priority", 10))
            return matched_intents[0]

        return None

    def update_risk_mapping(self, new_mapping):
        """
        Update the risk level mapping dictionary

        Args:
            new_mapping (dict): New mapping from risk levels to actions
        """
        self.risk_level_mapping.update(new_mapping)


# Example usage
if __name__ == "__main__":
    engine = RuleEngine("Rules.json")

    # Test cases
    test_inputs = [
        "打开空调",
        "查看当前车速",
        "你好，讲个笑话",
        "打开车窗然后调整座椅",
        "请帮我查一下今天的天气",
        "这是一个很长的句子，超过8个字符的复杂命令测试",
        "停止所有操作",
        "请告诉我附近有什么好吃的餐厅"
    ]

    for input_text in test_inputs:
        result = engine.process_input(input_text)
        print(f"Input: {input_text}")
        print(f"Result: {result}\n")

    # Example of updating risk mapping
    engine.update_risk_mapping({
        "L3": "HIGH_RISK_FORBIDDEN",  # Change L3 from "REQUIRES_CONFIRMATION" to "HIGH_RISK_FORBIDDEN"
        "L4": "REQUIRES_CONFIRMATION"  # Change L4 from "DIRECT_ALLOW" to "REQUIRES_CONFIRMATION"
    })

    print("After updating risk mapping:")
    for input_text in test_inputs[:3]:
        result = engine.process_input(input_text)
        print(f"Input: {input_text}")
        print(f"Result: {result}\n")
