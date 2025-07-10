#!/usr/bin/env python3
"""
Simple test runner for ChatBot response validation
简单的聊天机器人响应验证测试运行器

Usage:
    python run_chatbot_tests.py

This script will:
1. Run all chatbot response tests
2. Generate a markdown report
3. Display summary results
"""

import sys
import os
from pathlib import Path

# Add the current directory and parent directory to Python path
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(parent_dir))

try:
    from test_chatbot_responses import ChatBotTester
except ImportError as e:
    print(f"Error importing test module: {e}")
    print("Please ensure test_chatbot_responses.py is in the same directory")
    print(f"Current directory: {current_dir}")
    print(f"Python path: {sys.path[:3]}")
    sys.exit(1)

def main():
    """Main function to run chatbot tests with error handling"""
    print("=" * 60)
    print("ChatBot Response Testing Suite")
    print("=" * 60)
    
    try:
        # Initialize tester
        tester = ChatBotTester()
        
        # Run tests
        print("Starting test execution...")
        tester.run_all_tests()
        
        # Generate report
        print("\nGenerating markdown report...")
        report_path = tester.generate_markdown_report()
        
        # Display summary
        successful_tests = len([r for r in tester.results if "error" not in r])
        total_tests = len(tester.results)
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Failed: {total_tests - successful_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Report Location: {report_path}")
        print("=" * 60)
        
        # Show any errors
        failed_tests = [r for r in tester.results if "error" in r]
        if failed_tests:
            print("\nFAILED TESTS:")
            for test in failed_tests:
                print(f"- Test {test['test_id']} ({test['category']}): {test['error']}")
        
        return 0 if successful_tests == total_tests else 1
        
    except Exception as e:
        print(f"Critical error during test execution: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
