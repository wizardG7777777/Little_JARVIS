"""
RAG.py Functionality Test Program (English Version)
Tests all functions in RAG.py RagUniversal class to ensure they work correctly

Test Coverage:
1. RagUniversal class initialization
2. split_markdown_semantic method
3. add method
4. retrieve method
5. Complete RAG workflow integration test
"""

import unittest
import sys
import os
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from RAGmodule.RAG import RagUniversal


class TestRAGFunctionality(unittest.TestCase):
    """RAG functionality test class"""
    
    def setUp(self):
        """Set up test environment"""
        # Create temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.test_markdown_file = os.path.join(self.test_dir, "test.md")
        
        # Create test markdown file
        self.create_test_markdown_file()
        
        # Initialize RAG instance
        try:
            self.rag = RagUniversal()
            self.rag_initialized = True
        except Exception as e:
            print(f"Warning: RAG initialization failed: {e}")
            self.rag_initialized = False
        
        # Test threshold configuration
        self.test_thresholds = {
            'initialization_success': 0.8,
            'markdown_split_accuracy': 0.7,
            'add_function_success': 0.5,
            'retrieve_function_success': 0.7,
            'integration_success': 0.5
        }
    
    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def create_test_markdown_file(self):
        """Create test markdown file"""
        markdown_content = """# Test Document Title

This is an introduction paragraph for the test document.

## Chapter 1

This is the content of chapter 1. Contains some basic information.

### Section 1.1

This is the content of a subsection.

- List item 1
- List item 2
- List item 3

## Chapter 2

This is the content of chapter 2.

```python
# This is a code block
def hello_world():
    print("Hello, World!")
    return True
```

### Section 2.1

This is another subsection.

> This is a quote block
> Contains important information

## Chapter 3

Content of the last chapter.

1. Ordered list item 1
2. Ordered list item 2
3. Ordered list item 3

Final paragraph.
"""
        
        with open(self.test_markdown_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
    
    def test_01_rag_initialization(self):
        """Test RAG class initialization"""
        print("\n=== Testing RAG Class Initialization ===")
        
        test_cases = [
            {
                'description': 'Default initialization',
                'embedding_model': None,
                'should_succeed': True
            },
            {
                'description': 'Custom embedding_model',
                'embedding_model': 'custom_model',
                'should_succeed': True
            }
        ]
        
        successful_inits = 0
        total_tests = len(test_cases)
        
        for test_case in test_cases:
            print(f"Testing: {test_case['description']}")
            
            try:
                if test_case['embedding_model']:
                    rag_instance = RagUniversal(embedding_model=test_case['embedding_model'])
                else:
                    rag_instance = RagUniversal()
                
                # Check key attributes
                self.assertTrue(hasattr(rag_instance, 'client'), "Should have client attribute")
                self.assertTrue(hasattr(rag_instance, 'collection'), "Should have collection attribute")
                self.assertTrue(hasattr(rag_instance, 'embedding'), "Should have embedding attribute")
                
                successful_inits += 1
                print("✓ Initialization successful")
                
            except Exception as e:
                if test_case['should_succeed']:
                    print(f"✗ Initialization failed: {str(e)}")
                else:
                    print(f"✓ Expected failure: {str(e)}")
                    successful_inits += 1
            
            print("-" * 50)
        
        accuracy = successful_inits / total_tests
        print(f"RAG initialization success rate: {accuracy:.2%} ({successful_inits}/{total_tests})")
        self.assertGreater(accuracy, self.test_thresholds['initialization_success'], 
                          f"RAG initialization success rate should be > {self.test_thresholds['initialization_success']:.0%}")
    
    def test_02_markdown_splitting(self):
        """Test markdown file splitting functionality"""
        print("\n=== Testing Markdown File Splitting ===")
        
        if not self.rag_initialized:
            self.skipTest("RAG not successfully initialized, skipping this test")
        
        try:
            # Test normal file splitting
            blocks = self.rag.split_markdown_semantic(self.test_markdown_file)
            
            print(f"Split result: {len(blocks)} semantic blocks")
            
            # Verify split results
            self.assertIsInstance(blocks, list, "Result should be a list")
            self.assertGreater(len(blocks), 0, "Should have at least one semantic block")
            
            # Check if expected content is included
            all_content = ' '.join(blocks)
            expected_elements = [
                'Test Document Title',
                'Chapter 1',
                'Chapter 2', 
                'Chapter 3',
                'def hello_world',
                'List item 1'
            ]
            
            found_elements = 0
            for element in expected_elements:
                if element in all_content:
                    found_elements += 1
                    print(f"✓ Found expected element: {element}")
                else:
                    print(f"✗ Missing expected element: {element}")
            
            accuracy = found_elements / len(expected_elements)
            print(f"Content completeness: {accuracy:.2%} ({found_elements}/{len(expected_elements)})")
            
            # Show first 3 blocks
            print("\nFirst 3 semantic blocks:")
            for i, block in enumerate(blocks[:3]):
                print(f"Block {i+1}: {block[:100]}...")
            
            self.assertGreater(accuracy, self.test_thresholds['markdown_split_accuracy'],
                              f"Markdown split accuracy should be > {self.test_thresholds['markdown_split_accuracy']:.0%}")
            
        except Exception as e:
            self.fail(f"Markdown splitting test failed: {str(e)}")
    
    def test_03_add_functionality(self):
        """Test vector database add functionality"""
        print("\n=== Testing Vector Database Add Functionality ===")
        
        if not self.rag_initialized:
            self.skipTest("RAG not successfully initialized, skipping this test")
        
        test_cases = [
            {
                'description': 'Add single document',
                'documents': ['This is a test document'],
                'collection_name': 'Default',
                'metadata': {'source': 'test', 'id': '1'}
            },
            {
                'description': 'Add multiple documents',
                'documents': ['Document 1', 'Document 2', 'Document 3'],
                'collection_name': 'Default',
                'metadata': {'source': 'test', 'batch': 'multi'}
            },
            {
                'description': 'Add document with detailed metadata',
                'documents': ['Document with metadata'],
                'collection_name': 'Default',
                'metadata': {'source': 'test', 'type': 'example', 'category': 'detailed'}
            },
            {
                'description': 'Add to non-existent collection (should fallback to Default)',
                'documents': ['Test document'],
                'collection_name': 'NonExistentCollection',
                'metadata': {'source': 'test', 'fallback': 'true'}
            }
        ]
        
        successful_adds = 0
        total_tests = len(test_cases)
        
        for test_case in test_cases:
            print(f"Testing: {test_case['description']}")
            
            try:
                self.rag.add(
                    documents_text=test_case['documents'],
                    collection_name=test_case['collection_name'],
                    meta_datas=test_case['metadata']
                )
                
                successful_adds += 1
                print("✓ Add successful")
                
            except Exception as e:
                print(f"✗ Add failed: {str(e)}")
            
            print("-" * 50)
        
        accuracy = successful_adds / total_tests
        print(f"Add functionality success rate: {accuracy:.2%} ({successful_adds}/{total_tests})")
        self.assertGreater(accuracy, self.test_thresholds['add_function_success'],
                          f"Add functionality success rate should be > {self.test_thresholds['add_function_success']:.0%}")
    
    def test_04_retrieve_functionality(self):
        """Test vector database retrieve functionality"""
        print("\n=== Testing Vector Database Retrieve Functionality ===")
        
        if not self.rag_initialized:
            self.skipTest("RAG not successfully initialized, skipping this test")
        
        # First add some test data
        test_documents = [
            "Artificial intelligence is a branch of computer science",
            "Machine learning is a subfield of artificial intelligence",
            "Deep learning uses neural networks for learning",
            "Natural language processing handles human language",
            "Computer vision processes images and videos"
        ]
        
        try:
            # Add test data
            self.rag.add(
                documents_text=test_documents,
                collection_name="Default",
                meta_datas=[{'id': i, 'topic': 'AI'} for i in range(len(test_documents))]
            )
            print("✓ Test data added successfully")
        except Exception as e:
            print(f"✗ Test data addition failed: {str(e)}")
            self.skipTest("Cannot add test data, skipping retrieve test")
        
        test_cases = [
            {
                'description': 'Basic retrieve test',
                'query': 'What is artificial intelligence',
                'collection_name': 'Default',
                'n_results': 3
            },
            {
                'description': 'Retrieve more results',
                'query': 'machine learning',
                'collection_name': 'Default',
                'n_results': 5
            },
            {
                'description': 'Retrieve single result',
                'query': 'deep learning',
                'collection_name': 'Default',
                'n_results': 1
            },
            {
                'description': 'Retrieve from non-existent collection',
                'query': 'test query',
                'collection_name': 'NonExistentCollection',
                'n_results': 3
            }
        ]
        
        successful_retrieves = 0
        total_tests = len(test_cases)
        
        for test_case in test_cases:
            print(f"Testing: {test_case['description']}")
            print(f"Query: '{test_case['query']}'")
            
            try:
                results = self.rag.retrieve(
                    collection_name=test_case['collection_name'],
                    query=test_case['query'],
                    n_results=test_case['n_results']
                )
                
                # Verify result format
                self.assertIsInstance(results, list, "Retrieve results should be a list")
                
                if len(results) > 0:
                    print(f"✓ Retrieve successful, returned {len(results[0])} results")
                    # Show first 2 results
                    for i, result in enumerate(results[0][:2]):
                        print(f"  Result {i+1}: {result[:50]}...")
                else:
                    print("✓ Retrieve successful, but no results returned")
                
                successful_retrieves += 1
                
            except Exception as e:
                print(f"✗ Retrieve failed: {str(e)}")
            
            print("-" * 50)
        
        accuracy = successful_retrieves / total_tests
        print(f"Retrieve functionality success rate: {accuracy:.2%} ({successful_retrieves}/{total_tests})")
        self.assertGreater(accuracy, self.test_thresholds['retrieve_function_success'],
                          f"Retrieve functionality success rate should be > {self.test_thresholds['retrieve_function_success']:.0%}")

    def test_05_integration_workflow(self):
        """Test complete RAG workflow"""
        print("\n=== Testing Complete RAG Workflow ===")

        if not self.rag_initialized:
            self.skipTest("RAG not successfully initialized, skipping this test")

        workflow_steps = []

        try:
            # Step 1: Split markdown file
            print("Step 1: Split markdown file")
            blocks = self.rag.split_markdown_semantic(self.test_markdown_file)
            self.assertGreater(len(blocks), 0, "Should split at least one block")
            workflow_steps.append("markdown_split")
            print(f"✓ Successfully split into {len(blocks)} semantic blocks")

            # Step 2: Add to vector database
            print("\nStep 2: Add to vector database")
            self.rag.add(
                documents_text=blocks,
                collection_name="Default",
                meta_datas={'source': 'test_markdown', 'type': 'integration_test'}
            )
            workflow_steps.append("add_to_db")
            print("✓ Successfully added to vector database")

            # Step 3: Execute retrieval queries
            print("\nStep 3: Execute retrieval queries")
            test_queries = [
                "test document",
                "chapter 1",
                "code block",
                "list item"
            ]

            successful_queries = 0
            for query in test_queries:
                try:
                    results = self.rag.retrieve(
                        collection_name="Default",
                        query=query,
                        n_results=2
                    )

                    if results and len(results[0]) > 0:
                        successful_queries += 1
                        print(f"✓ Query '{query}' successful, found {len(results[0])} results")
                    else:
                        print(f"✗ Query '{query}' no results")

                except Exception as e:
                    print(f"✗ Query '{query}' failed: {str(e)}")

            if successful_queries > 0:
                workflow_steps.append("retrieve_success")
                print(f"✓ Retrieval test completed, success rate: {successful_queries}/{len(test_queries)}")

        except Exception as e:
            print(f"✗ Workflow failed: {str(e)}")

        # Calculate integration test success rate
        expected_steps = ["markdown_split", "add_to_db", "retrieve_success"]
        completed_steps = len([step for step in expected_steps if step in workflow_steps])
        accuracy = completed_steps / len(expected_steps)

        print(f"\nComplete workflow success rate: {accuracy:.2%} ({completed_steps}/{len(expected_steps)})")
        print(f"Completed steps: {workflow_steps}")

        self.assertGreater(accuracy, self.test_thresholds['integration_success'],
                          f"Integration test success rate should be > {self.test_thresholds['integration_success']:.0%}")

    def test_06_error_handling(self):
        """Test error handling"""
        print("\n=== Testing Error Handling ===")

        if not self.rag_initialized:
            self.skipTest("RAG not successfully initialized, skipping this test")

        error_test_cases = [
            {
                'description': 'Split non-existent file',
                'test_type': 'split_nonexistent_file',
                'should_raise_exception': True
            },
            {
                'description': 'Add empty document list',
                'test_type': 'add_empty_documents',
                'should_raise_exception': False
            },
            {
                'description': 'Retrieve empty query',
                'test_type': 'retrieve_empty_query',
                'should_raise_exception': False
            }
        ]

        handled_errors = 0
        total_tests = len(error_test_cases)

        for test_case in error_test_cases:
            print(f"Testing: {test_case['description']}")

            try:
                if test_case['test_type'] == 'split_nonexistent_file':
                    self.rag.split_markdown_semantic('/nonexistent/file.md')
                elif test_case['test_type'] == 'add_empty_documents':
                    self.rag.add(documents_text=[], collection_name="Default")
                elif test_case['test_type'] == 'retrieve_empty_query':
                    self.rag.retrieve(collection_name="Default", query="")

                if test_case['should_raise_exception']:
                    print("✗ Should raise exception but didn't")
                else:
                    print("✓ Correctly handled edge case")
                    handled_errors += 1

            except Exception as e:
                if test_case['should_raise_exception']:
                    print(f"✓ Correctly raised exception: {type(e).__name__}")
                    handled_errors += 1
                else:
                    print(f"✗ Unexpected exception: {str(e)}")

            print("-" * 50)

        accuracy = handled_errors / total_tests
        print(f"Error handling accuracy: {accuracy:.2%} ({handled_errors}/{total_tests})")


if __name__ == "__main__":
    # Run tests and generate report
    print("=" * 60)
    print("RAG.py Function Test Program")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestRAGFunctionality)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Generate test report
    report_file = os.path.join(os.path.dirname(__file__), "rag_test_report_en.md")
    
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# RAG.py Function Test Report\n\n")
            f.write(f"Generated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("## Test Overview\n\n")
            f.write(f"- Total Tests: {result.testsRun}\n")
            f.write(f"- Successful Tests: {result.testsRun - len(result.failures) - len(result.errors)}\n")
            f.write(f"- Failed Tests: {len(result.failures)}\n")
            f.write(f"- Error Tests: {len(result.errors)}\n")
            f.write(f"- Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%\n\n")
            
            if result.failures:
                f.write("## Failed Tests\n\n")
                for test, traceback in result.failures:
                    f.write(f"### {test}\n")
                    f.write(f"```\n{traceback}\n```\n\n")
            
            if result.errors:
                f.write("## Error Tests\n\n")
                for test, traceback in result.errors:
                    f.write(f"### {test}\n")
                    f.write(f"```\n{traceback}\n```\n\n")
            
            f.write("## Test Conclusion\n\n")
            if result.wasSuccessful():
                f.write("✅ All tests passed, RAG.py functions normally\n")
            else:
                f.write("❌ Some tests failed, need to check RAG.py implementation\n")
        
        print(f"\nTest report generated: {report_file}")
        
    except Exception as e:
        print(f"Error generating test report: {e}")
    
    print("\n" + "=" * 60)
    print("Test completed")
