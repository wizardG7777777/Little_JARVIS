# Qwen3-Embedding-0.6B 词嵌入模型测试使用说明

## 测试结果概览

✅ **测试状态**: 所有测试通过 (8/8, 100%)  
✅ **模型状态**: 工作正常  
✅ **性能表现**: 优秀 (平均推理时间: ~138ms)

## 已创建的文件

### 1. 核心模块
- **`RAG.py`**: Qwen3嵌入模型封装类，提供统一的API接口
- **`simple_test.py`**: 简化测试脚本，验证模型基本功能
- **`test_qwen3_embedding.py`**: 完整的单元测试套件
- **`run_tests.py`**: 自动化测试运行脚本

### 2. 文档
- **`README_测试说明.md`**: 详细的测试说明文档
- **`使用说明.md`**: 本文件，快速使用指南

## 快速开始

### 运行简化测试（推荐）
```bash
cd RAGmodule
python simple_test.py
```

### 运行完整测试套件
```bash
cd RAGmodule
python run_tests.py
```

### 直接使用模型
```python
from RAG import Qwen3EmbeddingModel

# 初始化模型
model = Qwen3EmbeddingModel(
    model_path="./Qwen3-Embedding-0.6B",
    use_sentence_transformers=False,  # 使用transformers库
    device="cpu"  # 或 "cuda" 如果有GPU
)

# 编码单个文本
text = "这是一个测试文本"
embedding = model.encode(text)
print(f"嵌入向量形状: {embedding.shape}")  # (1, 1024)

# 批量编码
texts = ["文本1", "文本2", "文本3"]
embeddings = model.encode(texts)
print(f"批量嵌入形状: {embeddings.shape}")  # (3, 1024)

# 计算相似度
similarity = model.similarity(embeddings[0:1], embeddings[1:2])
print(f"相似度: {similarity[0,0]:.3f}")
```

## 测试覆盖的功能

### ✅ 已验证功能
1. **模型加载**: 使用transformers库成功加载模型
2. **文本编码**: 单个和批量文本编码正常
3. **嵌入维度**: 正确输出1024维向量
4. **相似度计算**: 相似文本相似度高，不同文本相似度低
5. **性能表现**: CPU推理时间约138ms，性能良好
6. **边界处理**: 正确处理空输入、短文本、长文本
7. **错误处理**: 适当的异常处理机制

### 📊 性能指标
- **嵌入维度**: 1024
- **平均推理时间**: 138.2ms (±1.7ms) on CPU
- **相似文本相似度**: 0.936
- **不同文本相似度**: 0.587
- **测试通过率**: 100%

## 依赖要求

### 必需依赖 ✅
- `torch` - PyTorch深度学习框架
- `transformers` - Hugging Face模型库
- `numpy` - 数值计算库

### 可选依赖 ⚠️
- `sentence-transformers` - 简化的句子嵌入库（未安装，但不影响核心功能）

## 模型特性

### 支持的功能
- **多语言支持**: 支持100+种语言
- **长文本处理**: 最大序列长度32K
- **灵活维度**: 支持32-1024维度输出
- **指令感知**: 支持自定义指令提示

### 技术规格
- **模型大小**: 0.6B参数
- **架构**: 基于Qwen3-0.6B-Base
- **嵌入维度**: 1024
- **上下文长度**: 32K tokens

## 使用建议

### 1. 性能优化
```python
# 使用GPU加速（如果可用）
model = Qwen3EmbeddingModel(device="cuda")

# 批量处理提高效率
texts = ["文本1", "文本2", "文本3"]
embeddings = model.encode(texts)  # 比逐个处理更高效
```

### 2. 相似度搜索
```python
# 构建文档库
documents = ["文档1", "文档2", "文档3"]
doc_embeddings = model.encode(documents)

# 查询
query = "查询文本"
query_embedding = model.encode(query)

# 计算相似度
similarities = model.similarity(query_embedding, doc_embeddings)
best_match = np.argmax(similarities)
print(f"最相似文档: {documents[best_match]}")
```

### 3. 文本聚类
```python
# 编码文本集合
texts = ["文本1", "文本2", "文本3", "文本4"]
embeddings = model.encode(texts)

# 计算相似度矩阵
similarity_matrix = model.similarity(embeddings, embeddings)
print("相似度矩阵:")
print(similarity_matrix)
```

## 故障排除

### 常见问题

1. **模型加载失败**
   - 确保模型文件完整
   - 检查路径是否正确
   - 验证依赖是否安装

2. **内存不足**
   - 使用CPU模式: `device="cpu"`
   - 减少批处理大小
   - 关闭其他程序释放内存

3. **推理速度慢**
   - 使用GPU: `device="cuda"`
   - 批量处理多个文本
   - 考虑模型量化

### 检查命令
```bash
# 检查Python版本
python --version

# 检查依赖
python -c "import torch, transformers, numpy; print('Dependencies OK')"

# 快速测试
python -c "from RAG import Qwen3EmbeddingModel; print('Import OK')"
```

## 下一步建议

### 1. 集成到项目
- 将RAG.py集成到您的项目中
- 根据需求调整配置参数
- 添加项目特定的测试用例

### 2. 功能扩展
- 添加向量数据库支持
- 实现文档检索功能
- 集成到聊天机器人系统

### 3. 性能优化
- 考虑安装sentence-transformers库
- 使用GPU加速
- 实现模型缓存机制

## 联系支持

如果遇到问题，请提供：
1. 错误信息的完整输出
2. Python和依赖版本信息
3. 系统配置（CPU/GPU/内存）
4. 具体的使用场景

---

**总结**: Qwen3-Embedding-0.6B模型已成功通过所有测试，可以正常使用。模型性能优秀，支持多种文本嵌入任务。
