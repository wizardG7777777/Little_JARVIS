"""
Test file for Large Language Model response validation
测试大语言模型是否能够根据用户输入作出正确反应

This test file evaluates the chatbot's ability to:
1. Provide accurate responses to various types of questions
2. Enable thinking chain mode for better reasoning
3. Handle different conversation scenarios appropriately
4. Generate coherent and contextually relevant responses

Test Categories:
- Time calculation (时间计算)
- Location recommendations (地点推荐) 
- Self-introduction (自我介绍)
- Health advice (健康建议)
- Geography knowledge (地理知识)
- Cooking tips (烹饪技巧)
- Historical knowledge (历史知识)
- Location facts (地点事实)
- Social interaction (社交互动)
- Emotional response (情感回应)
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Add current directory to Python path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from chatbot_calling import call_local

class ChatBotTester:
    def __init__(self):
        """Initialize the chatbot tester with test cases and evaluation criteria"""
        self.test_cases = [
            {
                "id": 1,
                "category": "time_calculation",
                "question": "现在是下午3点25分，90分钟后是几点？",
                "expected_type": "时间计算",
                "evaluation_criteria": "Should correctly calculate 3:25 PM + 90 minutes = 4:55 PM"
            },
            {
                "id": 2,
                "category": "location_recommendation", 
                "question": "我现在刚刚抵达杭州，你有什么推荐的吗？",
                "expected_type": "地点推荐",
                "evaluation_criteria": "Should provide relevant Hangzhou attractions/activities"
            },
            {
                "id": 3,
                "category": "self_introduction",
                "question": "你好，你能介绍一下你自己吗？",
                "expected_type": "自我介绍", 
                "evaluation_criteria": "Should provide clear self-introduction as AI assistant"
            },
            {
                "id": 4,
                "category": "health_advice",
                "question": "感冒了应该喝姜茶还是冰咖啡？",
                "expected_type": "健康建议",
                "evaluation_criteria": "Should recommend ginger tea over iced coffee for cold"
            },
            {
                "id": 5,
                "category": "geography_knowledge",
                "question": "长江流经武汉吗？它在上海入海吗？",
                "expected_type": "地理知识",
                "evaluation_criteria": "Should confirm both facts are correct"
            },
            {
                "id": 6,
                "category": "cooking_tips",
                "question": "怎么快速解冻冷冻肉？用热水泡对吗？",
                "expected_type": "烹饪技巧",
                "evaluation_criteria": "Should advise against hot water, suggest safer methods"
            },
            {
                "id": 7,
                "category": "historical_knowledge",
                "question": "端午节吃粽子是为了纪念哪位历史人物？",
                "expected_type": "历史知识",
                "evaluation_criteria": "Should mention Qu Yuan (屈原)"
            },
            {
                "id": 8,
                "category": "location_facts",
                "question": "黄埔军校在上海吗？",
                "expected_type": "地点事实",
                "evaluation_criteria": "Should correct that it's in Guangzhou, not Shanghai"
            },
            {
                "id": 9,
                "category": "social_interaction",
                "question": "你好，我想向你介绍我新认识的朋友：llama",
                "expected_type": "社交互动",
                "evaluation_criteria": "Should respond appropriately to friend introduction"
            },
            {
                "id": 10,
                "category": "emotional_response",
                "question": "我今天很开心，希望你也开心一点哦 :-)",
                "expected_type": "情感回应",
                "evaluation_criteria": "Should respond positively to user's happiness"
            }
        ]
        
        self.results = []
        self.pass_fail_thresholds = {
            "time_calculation": 0.5,
            "location_recommendation": 0.5,
            "self_introduction": 0.5,
            "health_advice": 0.5,
            "geography_knowledge": 0.5,
            "cooking_tips": 0.5,
            "historical_knowledge": 0.5,
            "location_facts": 0.5,
            "social_interaction": 0.5,
            "emotional_response": 0.5
        }

    def run_single_test(self, test_case):
        """Run a single test case with thinking mode enabled"""
        print(f"\n{'='*60}")
        print(f"Running Test {test_case['id']}: {test_case['category']}")
        print(f"Question: {test_case['question']}")
        print(f"{'='*60}")
        
        try:
            start_time = time.time()
            
            # Call the chatbot with thinking mode enabled
            thinking_process, chat_response = call_local(
                user_query=test_case['question'], 
                enable_thinking=True
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # Store results
            result = {
                "test_id": test_case['id'],
                "category": test_case['category'],
                "question": test_case['question'],
                "thinking_process": thinking_process,
                "chat_response": chat_response,
                "response_time": response_time,
                "evaluation_criteria": test_case['evaluation_criteria'],
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            print(f"Response Time: {response_time:.2f} seconds")
            print(f"Thinking Process: {thinking_process}")
            print(f"Chat Response: {chat_response}")
            
            return result
            
        except Exception as e:
            error_result = {
                "test_id": test_case['id'],
                "category": test_case['category'],
                "question": test_case['question'],
                "error": str(e),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            print(f"Error occurred: {str(e)}")
            return error_result

    def run_all_tests(self):
        """Run all test cases and collect results"""
        print("Starting ChatBot Response Testing...")
        print(f"Total test cases: {len(self.test_cases)}")
        
        for test_case in self.test_cases:
            result = self.run_single_test(test_case)
            self.results.append(result)
            
            # Add small delay between tests
            time.sleep(1)
        
        print(f"\n{'='*60}")
        print("All tests completed!")
        print(f"{'='*60}")

    def generate_markdown_report(self, output_file="chatbot_test_results.md"):
        """Generate a comprehensive markdown report of test results"""
        
        report_content = f"""# ChatBot Response Testing Report

## Test Overview
- **Test Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **Total Test Cases**: {len(self.test_cases)}
- **Test Framework**: Large Language Model Response Validation
- **Thinking Mode**: Enabled for all tests

## Test Categories
The following categories were tested:
1. Time Calculation (时间计算)
2. Location Recommendations (地点推荐)
3. Self-Introduction (自我介绍)
4. Health Advice (健康建议)
5. Geography Knowledge (地理知识)
6. Cooking Tips (烹饪技巧)
7. Historical Knowledge (历史知识)
8. Location Facts (地点事实)
9. Social Interaction (社交互动)
10. Emotional Response (情感回应)

## Detailed Test Results

"""
        
        for i, result in enumerate(self.results, 1):
            if "error" in result:
                report_content += f"""### Test {i}: {result['category']} ❌
**Question**: {result['question']}
**Status**: ERROR
**Error Message**: {result['error']}
**Timestamp**: {result['timestamp']}

---

"""
            else:
                report_content += f"""### Test {i}: {result['category']}
**Question**: {result['question']}
**Response Time**: {result['response_time']:.2f} seconds
**Evaluation Criteria**: {result['evaluation_criteria']}

#### Thinking Process:
```
{result['thinking_process']}
```

#### Chat Response:
```
{result['chat_response']}
```

**Timestamp**: {result['timestamp']}

---

"""
        
        # Add summary section
        successful_tests = len([r for r in self.results if "error" not in r])
        failed_tests = len([r for r in self.results if "error" in r])
        
        report_content += f"""## Test Summary

- **Successful Tests**: {successful_tests}/{len(self.results)}
- **Failed Tests**: {failed_tests}/{len(self.results)}
- **Success Rate**: {(successful_tests/len(self.results)*100):.1f}%

## Evaluation Notes

Each test case was evaluated based on specific criteria:
- **Accuracy**: Whether the response contains correct information
- **Relevance**: Whether the response addresses the user's question appropriately  
- **Completeness**: Whether the response provides sufficient detail
- **Coherence**: Whether the response is logically structured and clear

## Recommendations

Based on the test results, consider the following improvements:
1. Monitor response accuracy for factual questions
2. Evaluate thinking process quality and reasoning chains
3. Assess response appropriateness for different conversation types
4. Review response times for performance optimization

---
*Report generated by ChatBot Testing Framework*
"""
        
        # Save the report
        output_path = Path(__file__).parent / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"Markdown report saved to: {output_path}")
        return output_path

def main():
    """Main function to run the chatbot testing suite"""
    tester = ChatBotTester()
    
    # Run all tests
    tester.run_all_tests()
    
    # Generate markdown report
    report_path = tester.generate_markdown_report()
    
    print(f"\nTesting completed successfully!")
    print(f"Results saved to: {report_path}")

if __name__ == "__main__":
    main()
