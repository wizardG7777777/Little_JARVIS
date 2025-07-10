# ChatBot Response Testing Suite

## Overview
This testing suite evaluates the Large Language Model's ability to provide accurate and appropriate responses to various types of user inputs. The tests are designed to validate the chatbot's performance across different conversation scenarios with thinking chain mode enabled.

## Files Description

### Core Test Files
- **`test_chatbot_responses.py`** - Main testing framework with comprehensive test cases
- **`run_chatbot_tests.py`** - Simple test runner script for easy execution
- **`chatbot_calling.py`** - Template file containing the `call_local` function (dependency)

### Generated Output
- **`chatbot_test_results.md`** - Detailed markdown report with test results (generated after running tests)

## Test Categories

The test suite covers 10 different conversation scenarios:

1. **Time Calculation (时间计算)** - Mathematical time computation
2. **Location Recommendations (地点推荐)** - Travel and location advice
3. **Self-Introduction (自我介绍)** - AI assistant self-description
4. **Health Advice (健康建议)** - Medical and wellness guidance
5. **Geography Knowledge (地理知识)** - Geographical facts and information
6. **Cooking Tips (烹饪技巧)** - Food preparation and cooking advice
7. **Historical Knowledge (历史知识)** - Historical facts and cultural knowledge
8. **Location Facts (地点事实)** - Specific location-based factual information
9. **Social Interaction (社交互动)** - Social conversation and interaction
10. **Emotional Response (情感回应)** - Emotional intelligence and empathy

## Test Questions

The following questions are used in the test suite:

1. 现在是下午3点25分，90分钟后是几点？
2. 我现在刚刚抵达杭州，你有什么推荐的吗？
3. 你好，你能介绍一下你自己吗？
4. 感冒了应该喝姜茶还是冰咖啡？
5. 长江流经武汉吗？它在上海入海吗？
6. 怎么快速解冻冷冻肉？用热水泡对吗？
7. 端午节吃粽子是为了纪念哪位历史人物？
8. 黄埔军校在上海吗？
9. 你好，我想向你介绍我新认识的朋友：llama
10. 我今天很开心，希望你也开心一点哦 :-)

## Usage Instructions

### Prerequisites
- Python 3.7+
- Required dependencies from the main project
- Access to the local LLM model (Qwen3-1.7B)
- Properly configured `chatbot_calling.py` module

### Running Tests

#### Method 1: Using the Test Runner (Recommended)
```bash
cd ChatBots
python run_chatbot_tests.py
```

#### Method 2: Direct Execution
```bash
cd ChatBots
python test_chatbot_responses.py
```

#### Method 3: Import and Use in Python
```python
from test_chatbot_responses import ChatBotTester

# Initialize tester
tester = ChatBotTester()

# Run all tests
tester.run_all_tests()

# Generate markdown report
report_path = tester.generate_markdown_report()
```

## Output Format

### Console Output
The test suite provides real-time feedback during execution:
- Test progress indicators
- Individual test results
- Thinking process output
- Response time measurements
- Summary statistics

### Markdown Report
A comprehensive markdown report is generated containing:
- Test overview and metadata
- Detailed results for each test case
- Thinking process chains
- Chat responses
- Performance metrics
- Evaluation criteria
- Summary statistics and recommendations

## Evaluation Criteria

Each test case is evaluated based on:
- **Accuracy**: Correctness of factual information
- **Relevance**: Appropriateness to the user's question
- **Completeness**: Sufficient detail in the response
- **Coherence**: Logical structure and clarity

## Configuration

### Pass/Fail Thresholds
The test suite uses configurable thresholds for each category (default: 0.5):
```python
self.pass_fail_thresholds = {
    "time_calculation": 0.5,
    "location_recommendation": 0.5,
    # ... other categories
}
```

### Customization Options
- Modify test questions in the `test_cases` list
- Adjust evaluation criteria
- Change output file names
- Configure response time limits
- Add new test categories

## Troubleshooting

### Common Issues
1. **Import Errors**: Ensure all dependencies are properly installed
2. **Model Path Issues**: Verify the LLM model path in `chatbot_calling.py`
3. **Permission Errors**: Check file write permissions for report generation
4. **Memory Issues**: Monitor system resources during model loading

### Error Handling
The test suite includes comprehensive error handling:
- Individual test failures don't stop the entire suite
- Detailed error messages in both console and report
- Graceful degradation for missing dependencies

## Integration with CI/CD

The test suite can be integrated into continuous integration pipelines:
```bash
# Example CI command
python run_chatbot_tests.py && echo "Tests passed" || echo "Tests failed"
```

## Contributing

To add new test cases:
1. Add entries to the `test_cases` list in `ChatBotTester.__init__()`
2. Define appropriate evaluation criteria
3. Update the pass/fail thresholds if needed
4. Test the new cases locally before committing

## License

This testing suite follows the same license as the main Little_JARVIS project.
