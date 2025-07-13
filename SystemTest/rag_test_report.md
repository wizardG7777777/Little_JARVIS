# RAG.py Function Test Report

Generated: 2025-07-11 00:48:14

## Test Overview

- Total Tests: 6
- Successful Tests: 0
- Failed Tests: 0
- Error Tests: 6
- Success Rate: 0.0%

## Error Tests

### test_01_rag_initialization (__main__.TestRAGFunctionality.test_01_rag_initialization)
```
Traceback (most recent call last):
  File "C:\Users\73524\Documents\PythonPrograms\Little_JARVIS\SystemTest\test_rag_functionality.py", line 114, in test_01_rag_initialization
    print("\n=== 测试RAG类初始化 ===")
    ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\73524\AppData\Local\Programs\Python\Python313\Lib\encodings\cp1252.py", line 19, in encode
    return codecs.charmap_encode(input,self.errors,encoding_table)[0]
           ~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
UnicodeEncodeError: 'charmap' codec can't encode characters in position 6-7: character maps to <undefined>

```

### test_02_markdown_splitting (__main__.TestRAGFunctionality.test_02_markdown_splitting)
```
Traceback (most recent call last):
  File "C:\Users\73524\Documents\PythonPrograms\Little_JARVIS\SystemTest\test_rag_functionality.py", line 165, in test_02_markdown_splitting
    print("\n=== 测试Markdown文件切分 ===")
    ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\73524\AppData\Local\Programs\Python\Python313\Lib\encodings\cp1252.py", line 19, in encode
    return codecs.charmap_encode(input,self.errors,encoding_table)[0]
           ~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
UnicodeEncodeError: 'charmap' codec can't encode characters in position 6-7: character maps to <undefined>

```

### test_03_add_functionality (__main__.TestRAGFunctionality.test_03_add_functionality)
```
Traceback (most recent call last):
  File "C:\Users\73524\Documents\PythonPrograms\Little_JARVIS\SystemTest\test_rag_functionality.py", line 215, in test_03_add_functionality
    print("\n=== 测试向量数据库添加功能 ===")
    ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\73524\AppData\Local\Programs\Python\Python313\Lib\encodings\cp1252.py", line 19, in encode
    return codecs.charmap_encode(input,self.errors,encoding_table)[0]
           ~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
UnicodeEncodeError: 'charmap' codec can't encode characters in position 6-16: character maps to <undefined>

```

### test_04_retrieve_functionality (__main__.TestRAGFunctionality.test_04_retrieve_functionality)
```
Traceback (most recent call last):
  File "C:\Users\73524\Documents\PythonPrograms\Little_JARVIS\SystemTest\test_rag_functionality.py", line 275, in test_04_retrieve_functionality
    print("\n=== 测试向量数据库检索功能 ===")
    ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\73524\AppData\Local\Programs\Python\Python313\Lib\encodings\cp1252.py", line 19, in encode
    return codecs.charmap_encode(input,self.errors,encoding_table)[0]
           ~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
UnicodeEncodeError: 'charmap' codec can't encode characters in position 6-16: character maps to <undefined>

```

### test_05_integration_workflow (__main__.TestRAGFunctionality.test_05_integration_workflow)
```
Traceback (most recent call last):
  File "C:\Users\73524\Documents\PythonPrograms\Little_JARVIS\SystemTest\test_rag_functionality.py", line 367, in test_05_integration_workflow
    print("\n=== 测试完整RAG工作流程 ===")
    ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\73524\AppData\Local\Programs\Python\Python313\Lib\encodings\cp1252.py", line 19, in encode
    return codecs.charmap_encode(input,self.errors,encoding_table)[0]
           ~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
UnicodeEncodeError: 'charmap' codec can't encode characters in position 6-9: character maps to <undefined>

```

### test_06_error_handling (__main__.TestRAGFunctionality.test_06_error_handling)
```
Traceback (most recent call last):
  File "C:\Users\73524\Documents\PythonPrograms\Little_JARVIS\SystemTest\test_rag_functionality.py", line 439, in test_06_error_handling
    print("\n=== 测试错误处理 ===")
    ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\73524\AppData\Local\Programs\Python\Python313\Lib\encodings\cp1252.py", line 19, in encode
    return codecs.charmap_encode(input,self.errors,encoding_table)[0]
           ~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
UnicodeEncodeError: 'charmap' codec can't encode characters in position 6-11: character maps to <undefined>

```

## Test Conclusion

❌ Some tests failed, need to check RAG.py implementation
