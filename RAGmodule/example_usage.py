#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Qwen3-Embedding-0.6B 使用示例
演示如何使用简化调用接口进行各种文本嵌入任务
"""

import numpy as np
from Qwen3Embedding0_6_simplecalling import Qwen3Embedding0_6_SimpleAPI, quick_test, quick_encode


def example_basic_usage():
    """基本使用示例"""
    print("=" * 60)
    print("示例1: 基本使用")
    print("=" * 60)
    
    # 初始化API
    api = Qwen3Embedding0_6_SimpleAPI()
    
    # 编码单个文本
    text = "人工智能是计算机科学的一个分支"
    embedding = api.encode_text(text)
    print(f"单文本编码结果: {embedding.shape}")
    
    # 编码多个文本
    texts = [
        "人工智能是计算机科学的一个分支",
        "机器学习是人工智能的核心技术",
        "深度学习是机器学习的重要方法",
        "今天天气很好，适合出门散步"
    ]
    embeddings = api.encode_text(texts)
    print(f"批量编码结果: {embeddings.shape}")
    
    # 计算相似度矩阵
    similarity_matrix = api.calculate_similarity(embeddings, embeddings)
    print(f"相似度矩阵形状: {similarity_matrix.shape}")
    print("相似度矩阵:")
    for i, text in enumerate(texts):
        print(f"{i}: {text[:20]}...")
        for j in range(len(texts)):
            print(f"  与文本{j}相似度: {similarity_matrix[i,j]:.3f}")
    print()


def example_similarity_search():
    """相似度搜索示例"""
    print("=" * 60)
    print("示例2: 相似度搜索")
    print("=" * 60)
    
    api = Qwen3Embedding0_6_SimpleAPI()
    
    # 文档库
    documents = [
        "Python是一种高级编程语言",
        "Java是面向对象的编程语言", 
        "机器学习算法可以从数据中学习",
        "深度学习使用神经网络进行训练",
        "自然语言处理是AI的重要应用",
        "计算机视觉处理图像和视频",
        "今天的天气非常晴朗",
        "我喜欢在公园里散步"
    ]
    
    # 查询
    query = "编程语言相关的内容"
    
    # 编码
    query_embedding = api.encode_text(query)
    doc_embeddings = api.encode_text(documents)
    
    # 计算相似度
    similarities = api.calculate_similarity(query_embedding, doc_embeddings)
    
    # 排序并显示结果
    results = [(i, documents[i], similarities[0,i]) for i in range(len(documents))]
    results.sort(key=lambda x: x[2], reverse=True)
    
    print(f"查询: {query}")
    print("最相似的文档:")
    for i, (idx, doc, score) in enumerate(results[:3]):
        print(f"{i+1}. [{score:.3f}] {doc}")
    print()


def example_multilingual():
    """多语言支持示例"""
    print("=" * 60)
    print("示例3: 多语言支持")
    print("=" * 60)
    
    api = Qwen3Embedding0_6_SimpleAPI()
    
    # 多语言文本
    multilingual_texts = [
        "Hello, how are you?",  # 英语
        "你好，你好吗？",        # 中文
        "こんにちは、元気ですか？",  # 日语
        "Bonjour, comment allez-vous?",  # 法语
        "Hola, ¿cómo estás?",  # 西班牙语
    ]
    
    languages = ["English", "Chinese", "Japanese", "French", "Spanish"]
    
    # 编码
    embeddings = api.encode_text(multilingual_texts)
    print(f"多语言编码结果: {embeddings.shape}")
    
    # 计算语言间相似度
    similarities = api.calculate_similarity(embeddings, embeddings)
    
    print("语言间相似度:")
    for i, lang1 in enumerate(languages):
        for j, lang2 in enumerate(languages):
            if i <= j:
                print(f"{lang1} - {lang2}: {similarities[i,j]:.3f}")
    print()


def example_performance_test():
    """性能测试示例"""
    print("=" * 60)
    print("示例4: 性能测试")
    print("=" * 60)
    
    api = Qwen3Embedding0_6_SimpleAPI()
    
    # 不同长度的文本
    test_texts = [
        "短文本",
        "这是一个中等长度的测试文本，包含了一些常见的词汇。",
        "这是一个较长的测试文本，包含了更多的词汇和更复杂的句子结构。它用于测试模型在处理长文本时的性能表现，包括推理时间和内存使用情况。",
        "这是一个非常长的测试文本。" * 50  # 重复50次
    ]
    
    text_types = ["短文本", "中等文本", "长文本", "超长文本"]
    
    for i, (text, text_type) in enumerate(zip(test_texts, text_types)):
        print(f"测试 {text_type} (长度: {len(text)} 字符)")
        
        # 性能测试
        perf_results = api.benchmark_performance(test_text=text, num_runs=3)
        
        print(f"  平均时间: {perf_results['avg_time_ms']:.1f}ms")
        print(f"  标准差: {perf_results['std_time_ms']:.1f}ms")
        print(f"  最小时间: {perf_results['min_time_ms']:.1f}ms")
        print(f"  最大时间: {perf_results['max_time_ms']:.1f}ms")
        print()


def example_quick_functions():
    """快速函数示例"""
    print("=" * 60)
    print("示例5: 快速函数")
    print("=" * 60)
    
    # 快速测试
    print("运行快速测试...")
    test_results = quick_test()
    print(f"测试通过率: {test_results['summary']['pass_rate']:.1f}%")
    print()
    
    # 快速编码
    print("快速编码示例:")
    texts = ["快速编码测试1", "快速编码测试2"]
    embeddings = quick_encode(texts)
    print(f"快速编码结果: {embeddings.shape}")
    print()


def example_error_handling():
    """错误处理示例"""
    print("=" * 60)
    print("示例6: 错误处理")
    print("=" * 60)
    
    api = Qwen3Embedding0_6_SimpleAPI()
    
    # 测试空输入
    try:
        api.encode_text([])
        print("错误：应该抛出异常")
    except ValueError as e:
        print(f"✓ 正确处理空输入: {e}")
    
    # 测试None输入
    try:
        api.encode_text(None)
        print("错误：应该抛出异常")
    except Exception as e:
        print(f"✓ 正确处理None输入: {type(e).__name__}")
    
    print()


def main():
    """主函数"""
    print("Qwen3-Embedding-0.6B 使用示例")
    print("=" * 60)
    
    try:
        # 运行所有示例
        example_basic_usage()
        example_similarity_search()
        example_multilingual()
        example_performance_test()
        example_quick_functions()
        example_error_handling()
        
        print("=" * 60)
        print("所有示例运行完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"运行示例时发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
