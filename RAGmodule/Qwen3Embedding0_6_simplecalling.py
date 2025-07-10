#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Qwen3-Embedding-0.6B 简化调用接口
包含所有测试需要用到的方法，提供简单易用的API
"""

import os
import sys
import time
import torch
import torch.nn.functional as F
from typing import List, Union, Optional, Tuple, Dict, Any
from transformers import AutoTokenizer, AutoModel
import numpy as np

# 尝试导入sentence_transformers，如果没有则使用transformers
try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False
    print("Warning: sentence-transformers not available, using transformers only")


class Qwen3Embedding0_6_SimpleAPI:
    """
    Qwen3-Embedding-0.6B 简化API类
    提供所有测试需要的方法，支持多种使用方式
    """
    
    def __init__(self, 
                 model_path: str = "./Qwen3-Embedding-0.6B",
                 use_sentence_transformers: bool = None,
                 device: Optional[str] = None,
                 max_length: int = 8192):
        """
        初始化嵌入模型
        
        Args:
            model_path: 模型路径
            use_sentence_transformers: 是否使用sentence_transformers库，None为自动选择
            device: 设备类型 ('cpu', 'cuda', 'auto')
            max_length: 最大序列长度
        """
        self.model_path = model_path
        self.max_length = max_length
        
        # 自动选择使用哪个库
        if use_sentence_transformers is None:
            self.use_sentence_transformers = HAS_SENTENCE_TRANSFORMERS
        else:
            self.use_sentence_transformers = use_sentence_transformers and HAS_SENTENCE_TRANSFORMERS
        
        # 设备选择
        if device is None or device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
            
        self.model = None
        self.tokenizer = None
        self.is_loaded = False
        
        # 自动加载模型
        self.load_model()
    
    def load_model(self) -> bool:
        """
        加载模型
        
        Returns:
            bool: 是否加载成功
        """
        try:
            if self.use_sentence_transformers:
                print(f"Loading model with sentence_transformers on {self.device}")
                self.model = SentenceTransformer(
                    self.model_path,
                    device=self.device
                )
            else:
                print(f"Loading model with transformers on {self.device}")
                self.tokenizer = AutoTokenizer.from_pretrained(
                    self.model_path, 
                    padding_side='left'
                )
                self.model = AutoModel.from_pretrained(self.model_path)
                self.model.to(self.device)
                self.model.eval()
            
            self.is_loaded = True
            print("✓ Model loaded successfully")
            return True
            
        except Exception as e:
            print(f"✗ Model loading failed: {str(e)}")
            self.is_loaded = False
            return False
    
    def check_model_loaded(self):
        """检查模型是否已加载"""
        if not self.is_loaded:
            raise RuntimeError("Model not loaded. Please call load_model() first.")
    
    def _last_token_pool(self, last_hidden_states: torch.Tensor, 
                        attention_mask: torch.Tensor) -> torch.Tensor:
        """
        最后一个token池化（用于transformers方式）
        """
        left_padding = (attention_mask[:, -1].sum() == attention_mask.shape[0])
        if left_padding:
            return last_hidden_states[:, -1]
        else:
            sequence_lengths = attention_mask.sum(dim=1) - 1
            batch_size = last_hidden_states.shape[0]
            return last_hidden_states[torch.arange(batch_size, device=last_hidden_states.device), sequence_lengths]
    
    def encode_text(self, 
                   texts: Union[str, List[str]], 
                   normalize: bool = True,
                   prompt_name: Optional[str] = None) -> np.ndarray:
        """
        编码文本为嵌入向量
        
        Args:
            texts: 输入文本或文本列表
            normalize: 是否归一化嵌入向量
            prompt_name: 提示名称（仅用于sentence_transformers）
            
        Returns:
            嵌入向量数组
        """
        self.check_model_loaded()
        
        if isinstance(texts, str):
            texts = [texts]
        
        if not texts:
            raise ValueError("Input texts cannot be empty")
        
        try:
            if self.use_sentence_transformers:
                embeddings = self.model.encode(
                    texts, 
                    normalize_embeddings=normalize,
                    prompt_name=prompt_name
                )
                return embeddings
            else:
                # 使用transformers方式
                batch_dict = self.tokenizer(
                    texts,
                    padding=True,
                    truncation=True,
                    max_length=self.max_length,
                    return_tensors="pt",
                )
                batch_dict = {k: v.to(self.device) for k, v in batch_dict.items()}
                
                with torch.no_grad():
                    outputs = self.model(**batch_dict)
                    embeddings = self._last_token_pool(
                        outputs.last_hidden_state, 
                        batch_dict['attention_mask']
                    )
                    
                    if normalize:
                        embeddings = F.normalize(embeddings, p=2, dim=1)
                    
                    return embeddings.cpu().numpy()
                    
        except Exception as e:
            raise RuntimeError(f"Text encoding failed: {str(e)}")
    
    def calculate_similarity(self, 
                           embeddings1: np.ndarray, 
                           embeddings2: np.ndarray) -> np.ndarray:
        """
        计算嵌入向量之间的余弦相似度
        
        Args:
            embeddings1: 第一组嵌入向量
            embeddings2: 第二组嵌入向量
            
        Returns:
            相似度矩阵
        """
        if self.use_sentence_transformers and hasattr(self.model, 'similarity'):
            return self.model.similarity(embeddings1, embeddings2).numpy()
        else:
            # 手动计算余弦相似度
            embeddings1 = torch.tensor(embeddings1)
            embeddings2 = torch.tensor(embeddings2)
            return (embeddings1 @ embeddings2.T).numpy()
    
    def get_embedding_dimension(self) -> int:
        """
        获取嵌入向量维度
        
        Returns:
            嵌入向量维度
        """
        self.check_model_loaded()
        
        if self.use_sentence_transformers:
            return self.model.get_sentence_embedding_dimension()
        else:
            # 通过编码一个简单文本来获取维度
            test_embedding = self.encode_text("test")
            return test_embedding.shape[1]
    
    def benchmark_performance(self, 
                            test_text: str = "This is a performance test text", 
                            num_runs: int = 10) -> Dict[str, float]:
        """
        性能基准测试
        
        Args:
            test_text: 测试文本
            num_runs: 运行次数
            
        Returns:
            性能统计字典
        """
        self.check_model_loaded()
        
        times = []
        for _ in range(num_runs):
            start_time = time.perf_counter()
            self.encode_text(test_text)
            end_time = time.perf_counter()
            times.append((end_time - start_time) * 1000)
        
        return {
            "avg_time_ms": np.mean(times),
            "std_time_ms": np.std(times),
            "min_time_ms": np.min(times),
            "max_time_ms": np.max(times),
            "num_runs": num_runs
        }
    
    def test_basic_functionality(self) -> Dict[str, Any]:
        """
        测试基本功能
        
        Returns:
            测试结果字典
        """
        results = {
            "model_loaded": False,
            "single_text_encoding": False,
            "batch_text_encoding": False,
            "embedding_dimension": None,
            "similarity_calculation": False,
            "performance": None,
            "errors": []
        }
        
        try:
            # 测试模型加载
            results["model_loaded"] = self.is_loaded
            
            # 测试单文本编码
            try:
                embedding = self.encode_text("Test text")
                results["single_text_encoding"] = True
                results["embedding_dimension"] = embedding.shape[1]
            except Exception as e:
                results["errors"].append(f"Single text encoding failed: {e}")
            
            # 测试批量编码
            try:
                embeddings = self.encode_text(["Text 1", "Text 2", "Text 3"])
                results["batch_text_encoding"] = embeddings.shape[0] == 3
            except Exception as e:
                results["errors"].append(f"Batch text encoding failed: {e}")
            
            # 测试相似度计算
            try:
                text1_emb = self.encode_text("Hello world")
                text2_emb = self.encode_text("Hello world")
                similarity = self.calculate_similarity(text1_emb, text2_emb)
                results["similarity_calculation"] = similarity[0, 0] > 0.9  # 相同文本应该高度相似
            except Exception as e:
                results["errors"].append(f"Similarity calculation failed: {e}")
            
            # 测试性能
            try:
                results["performance"] = self.benchmark_performance(num_runs=3)
            except Exception as e:
                results["errors"].append(f"Performance test failed: {e}")
                
        except Exception as e:
            results["errors"].append(f"General test failed: {e}")
        
        return results
    
    def test_edge_cases(self) -> Dict[str, Any]:
        """
        测试边界条件
        
        Returns:
            测试结果字典
        """
        results = {
            "empty_input_handled": False,
            "short_text_handled": False,
            "long_text_handled": False,
            "errors": []
        }
        
        try:
            # 测试空输入
            try:
                self.encode_text([])
                results["errors"].append("Empty input should raise exception")
            except ValueError:
                results["empty_input_handled"] = True
            except Exception as e:
                results["errors"].append(f"Unexpected error for empty input: {e}")
            
            # 测试极短文本
            try:
                short_embedding = self.encode_text("a")
                results["short_text_handled"] = short_embedding.shape[1] > 0
            except Exception as e:
                results["errors"].append(f"Short text handling failed: {e}")
            
            # 测试长文本
            try:
                long_text = "This is a very long text. " * 1000
                long_embedding = self.encode_text(long_text)
                results["long_text_handled"] = long_embedding.shape[1] > 0
            except Exception as e:
                results["errors"].append(f"Long text handling failed: {e}")
                
        except Exception as e:
            results["errors"].append(f"Edge case test failed: {e}")
        
        return results
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """
        运行综合测试
        
        Returns:
            完整测试结果
        """
        print("=" * 60)
        print("Qwen3-Embedding-0.6B Comprehensive Test")
        print("=" * 60)
        
        # 基本功能测试
        print("\n1. Testing basic functionality...")
        basic_results = self.test_basic_functionality()
        
        # 边界条件测试
        print("2. Testing edge cases...")
        edge_results = self.test_edge_cases()
        
        # 汇总结果
        all_results = {
            "basic_functionality": basic_results,
            "edge_cases": edge_results,
            "summary": {
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "pass_rate": 0.0
            }
        }
        
        # 计算通过率
        tests = [
            basic_results["model_loaded"],
            basic_results["single_text_encoding"],
            basic_results["batch_text_encoding"],
            basic_results["similarity_calculation"],
            edge_results["empty_input_handled"],
            edge_results["short_text_handled"],
            edge_results["long_text_handled"]
        ]
        
        total_tests = len(tests)
        passed_tests = sum(tests)
        pass_rate = (passed_tests / total_tests) * 100
        
        all_results["summary"]["total_tests"] = total_tests
        all_results["summary"]["passed_tests"] = passed_tests
        all_results["summary"]["failed_tests"] = total_tests - passed_tests
        all_results["summary"]["pass_rate"] = pass_rate
        
        # 打印结果
        print(f"\n3. Test Summary:")
        print(f"   Total tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {total_tests - passed_tests}")
        print(f"   Pass rate: {pass_rate:.1f}%")
        
        if pass_rate >= 90:
            print("   Status: 🎉 Excellent!")
        elif pass_rate >= 70:
            print("   Status: ✅ Good!")
        elif pass_rate >= 50:
            print("   Status: ⚠️ Fair")
        else:
            print("   Status: ❌ Poor")
        
        print("=" * 60)
        
        return all_results
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        获取模型信息
        
        Returns:
            模型信息字典
        """
        info = {
            "model_path": self.model_path,
            "device": self.device,
            "max_length": self.max_length,
            "use_sentence_transformers": self.use_sentence_transformers,
            "is_loaded": self.is_loaded,
            "embedding_dimension": None,
            "library_used": "sentence_transformers" if self.use_sentence_transformers else "transformers"
        }
        
        if self.is_loaded:
            try:
                info["embedding_dimension"] = self.get_embedding_dimension()
            except:
                info["embedding_dimension"] = "Unknown"
        
        return info


# 便捷函数
def quick_test(model_path: str = "./Qwen3-Embedding-0.6B") -> Dict[str, Any]:
    """
    快速测试函数
    
    Args:
        model_path: 模型路径
        
    Returns:
        测试结果
    """
    api = Qwen3Embedding0_6_SimpleAPI(model_path=model_path)
    return api.run_comprehensive_test()


def quick_encode(texts: Union[str, List[str]], 
                model_path: str = "./Qwen3-Embedding-0.6B") -> np.ndarray:
    """
    快速编码函数
    
    Args:
        texts: 要编码的文本
        model_path: 模型路径
        
    Returns:
        嵌入向量
    """
    api = Qwen3Embedding0_6_SimpleAPI(model_path=model_path)
    return api.encode_text(texts)


if __name__ == "__main__":
    # 运行测试示例
    print("Running Qwen3-Embedding-0.6B Simple API Test...")
    results = quick_test()
    
    # 显示模型信息
    api = Qwen3Embedding0_6_SimpleAPI()
    info = api.get_model_info()
    print(f"\nModel Info: {info}")
