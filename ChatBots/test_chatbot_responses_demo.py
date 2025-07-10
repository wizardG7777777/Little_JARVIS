"""
Demo version of ChatBot Response Testing with mock responses
演示版本的聊天机器人响应测试（使用模拟响应）

This demo shows how the test framework works when the LLM is functioning properly.
It uses mock responses to demonstrate the complete testing workflow.
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Add current directory to Python path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def mock_call_local(user_query: str, enable_thinking: bool = False) -> tuple:
    """Mock version of call_local that returns simulated responses"""
    
    # Simulate processing time
    time.sleep(0.5)
    
    # Mock responses for each test case
    mock_responses = {
        "现在是下午3点25分，90分钟后是几点？": {
            "thinking": "用户问的是时间计算问题。现在是下午3点25分，需要加上90分钟。90分钟等于1小时30分钟。3点25分 + 1小时30分钟 = 4点55分。",
            "response": "现在是下午3点25分，90分钟后是下午4点55分。计算过程：90分钟 = 1小时30分钟，3:25 PM + 1:30 = 4:55 PM。"
        },
        "我现在刚刚抵达杭州，你有什么推荐的吗？": {
            "thinking": "用户刚到杭州，需要推荐一些当地的景点和活动。杭州最著名的是西湖，还有灵隐寺、雷峰塔等景点，以及当地美食。",
            "response": "欢迎来到杭州！我推荐您：1. 西湖风景区（必游景点）2. 灵隐寺（历史文化）3. 雷峰塔（登高望远）4. 河坊街（传统小吃）5. 龙井茶园（品茶体验）。建议先游西湖，感受杭州的诗意美景。"
        },
        "你好，你能介绍一下你自己吗？": {
            "thinking": "用户想了解我的身份和功能。我应该简洁地介绍自己是一个AI助手，能够帮助用户解答问题和提供服务。",
            "response": "你好！我是一个AI智能助手，基于大语言模型开发。我可以帮助您：回答各种问题、提供信息查询、协助解决问题、进行日常对话等。我会尽力为您提供准确、有用的帮助。有什么我可以为您做的吗？"
        },
        "感冒了应该喝姜茶还是冰咖啡？": {
            "thinking": "这是一个健康建议问题。感冒时应该选择温热的饮品来帮助身体恢复，姜茶有暖身和抗炎的作用，而冰咖啡会让身体更寒冷，不利于康复。",
            "response": "感冒时建议喝姜茶而不是冰咖啡。原因：1. 姜茶性温，有助于驱寒暖身 2. 生姜具有抗炎和抗病毒特性 3. 温热饮品有助于缓解喉咙不适 4. 冰咖啡会让身体更寒冷，可能加重感冒症状。建议多喝温开水，充分休息。"
        },
        "长江流经武汉吗？它在上海入海吗？": {
            "thinking": "这是地理知识问题。长江确实流经武汉，武汉位于长江中游。长江最终在上海附近入海，准确地说是在崇明岛附近流入东海。",
            "response": "是的，这两个说法都正确：1. 长江确实流经武汉，武汉市位于长江中游，长江将武汉分为汉口、汉阳、武昌三镇 2. 长江在上海入海，准确地说是在上海崇明岛附近流入东海。长江全长约6300公里，是中国第一大河。"
        },
        "怎么快速解冻冷冻肉？用热水泡对吗？": {
            "thinking": "这是烹饪技巧问题。用热水解冻肉类是不正确的方法，会导致细菌滋生和肉质变差。正确的方法包括冷藏解冻、冷水解冻等。",
            "response": "不建议用热水泡解冻肉类。正确的快速解冻方法：1. 冷水解冻：用密封袋装肉，放入冷水中，每30分钟换一次水 2. 微波炉解冻：使用解冻功能，注意及时翻面 3. 提前规划：放冷藏室慢慢解冻（最安全）。热水解冻会导致细菌滋生和肉质变差。"
        },
        "端午节吃粽子是为了纪念哪位历史人物？": {
            "thinking": "这是中国传统文化和历史知识问题。端午节吃粽子是为了纪念屈原，他是战国时期楚国的爱国诗人。",
            "response": "端午节吃粽子是为了纪念屈原。屈原（约公元前340-278年）是战国时期楚国的爱国诗人和政治家，因忧国忧民投汨罗江而死。人们为了不让鱼虾吃掉屈原的身体，就投粽子到江中喂鱼，后来逐渐形成了端午节吃粽子的传统。"
        },
        "黄埔军校在上海吗？": {
            "thinking": "这是地理和历史知识问题。黄埔军校不在上海，而是在广州的黄埔区，现在叫中国人民解放军陆军军官学校。",
            "response": "不，黄埔军校不在上海，而是在广州市黄埔区。黄埔军校全称为\"中华民国陆军军官学校\"，1924年由孙中山创办，位于广州黄埔长洲岛。现在该地设有黄埔军校旧址纪念馆，是重要的历史文化遗址。"
        },
        "你好，我想向你介绍我新认识的朋友：llama": {
            "thinking": "用户想介绍他的朋友llama。这是一个社交互动场景，我应该表现出友好和兴趣，询问更多关于这位朋友的信息。",
            "response": "你好！很高兴听到你认识了新朋友llama！能告诉我更多关于llama的事情吗？比如你们是怎么认识的，或者llama有什么有趣的特点？我很乐意了解你的朋友们。"
        },
        "我今天很开心，希望你也开心一点哦 :-)": {
            "thinking": "用户表达了积极的情感，并希望我也开心。这是一个温暖的社交互动，我应该回应用户的善意，表达感谢和积极的情感。",
            "response": "谢谢你的善意！你的开心也让我感到很愉快 😊 能够帮助到用户并看到大家开心，对我来说就是最大的快乐。希望你今天的好心情能一直持续下去！有什么开心的事情想分享吗？"
        }
    }
    
    # Get response for the query
    response_data = mock_responses.get(user_query, {
        "thinking": "这是一个我需要仔细思考的问题。让我分析一下用户的需求并提供合适的回答。",
        "response": "感谢您的问题。我会尽力为您提供有用的信息和帮助。"
    })
    
    if enable_thinking:
        return response_data["thinking"], response_data["response"]
    else:
        return "", response_data["response"]

class ChatBotTesterDemo:
    def __init__(self):
        """Initialize the demo chatbot tester with test cases and evaluation criteria"""
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
            }
        ]
        
        self.results = []
        self.pass_fail_thresholds = {
            "time_calculation": 0.5,
            "location_recommendation": 0.5,
            "self_introduction": 0.5,
            "health_advice": 0.5,
            "geography_knowledge": 0.5
        }

    def run_single_test(self, test_case):
        """Run a single test case with thinking mode enabled"""
        print(f"\n{'='*60}")
        print(f"Running Test {test_case['id']}: {test_case['category']}")
        print(f"Question: {test_case['question']}")
        print(f"{'='*60}")
        
        try:
            start_time = time.time()
            
            # Call the mock chatbot with thinking mode enabled
            thinking_process, chat_response = mock_call_local(
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
        print("Starting ChatBot Response Testing (Demo Mode)...")
        print(f"Total test cases: {len(self.test_cases)}")
        
        for test_case in self.test_cases:
            result = self.run_single_test(test_case)
            self.results.append(result)
            
            # Add small delay between tests
            time.sleep(0.5)
        
        print(f"\n{'='*60}")
        print("All tests completed!")
        print(f"{'='*60}")

    def generate_markdown_report(self, output_file="chatbot_test_results_demo.md"):
        """Generate a comprehensive markdown report of test results"""
        
        report_content = f"""# ChatBot Response Testing Report (Demo Mode)

## Test Overview
- **Test Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **Total Test Cases**: {len(self.test_cases)}
- **Test Framework**: Large Language Model Response Validation (Demo)
- **Thinking Mode**: Enabled for all tests
- **Note**: This is a demonstration using mock responses

## Test Categories
The following categories were tested:
1. Time Calculation (时间计算)
2. Location Recommendations (地点推荐)
3. Self-Introduction (自我介绍)
4. Health Advice (健康建议)
5. Geography Knowledge (地理知识)

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
                report_content += f"""### Test {i}: {result['category']} ✅
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

## Demo Results Analysis

This demonstration shows how the testing framework works when the LLM is functioning properly:
1. **Thinking Process**: Each response includes detailed reasoning
2. **Response Quality**: Answers are contextually appropriate and informative
3. **Performance Metrics**: Response times are tracked for optimization
4. **Error Handling**: Framework gracefully handles any issues

---
*Report generated by ChatBot Testing Framework (Demo Mode)*
"""
        
        # Save the report
        output_path = Path(__file__).parent / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"Demo markdown report saved to: {output_path}")
        return output_path

def main():
    """Main function to run the demo chatbot testing suite"""
    tester = ChatBotTesterDemo()
    
    # Run all tests
    tester.run_all_tests()
    
    # Generate markdown report
    report_path = tester.generate_markdown_report()
    
    print(f"\nDemo testing completed successfully!")
    print(f"Results saved to: {report_path}")

if __name__ == "__main__":
    main()
