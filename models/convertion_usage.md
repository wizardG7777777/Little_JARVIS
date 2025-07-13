# convert2onnx.py 使用说明

## 概述

`convert2onnx.py` 是一个功能强大的深度学习模型优化工具，专门用于对大型语言模型进行剪枝、量化和ONNX格式转换。该工具支持多种优化技术，能够显著减少模型大小并提高推理效率。

## 功能特性

### 🎯 **核心功能**
- **模型剪枝**: 使用L1非结构化剪枝减少模型参数
- **动态量化**: INT8量化压缩模型大小
- **LoRA微调**: 低秩适应技术优化模型
- **ONNX导出**: 跨平台模型格式转换

### 🚨 **警告与提醒**
- **平台兼容性**: 目前导出的模型文件仅在安装了英伟达显卡的设备上经过测试

### 📊 **预期优化目标**
- 模型大小减少: 30-50%
- 推理速度提升: 20-40%
- 内存使用降低: >30%
- 精度损失: <10%

## 环境要求

### 🔧 **系统要求**
- Python 3.8+
- Windows/Linux
- 内存: 8GB+ 
- 存储: 模型大小的3倍空间

### 📦 **依赖库**
```bash
# 核心依赖
pip install torch transformers
pip install peft optimum
pip install onnx onnxruntime
pip install numpy pyyaml

# 可选依赖（用于完整功能）
pip install datasets
pip install accelerate
```

## 快速开始

### 1. 基础使用

```bash
# 基本命令
python convert2onnx.py --model_path llm/Qwen3-0.6B --config_path purning_config.yaml

# 指定自定义配置
python convert2onnx.py --model_path /path/to/model --config_path /path/to/config.yaml
```

## 配置文件说明

### 📝 **purning_config.yaml 详解**

```yaml
# 剪枝配置
pruning:
  sparsity_function: "PolynomialDecay"  # 稀疏度衰减函数
  init_sparsity: 0.05                  # 初始稀疏度 (5%)
  final_sparsity: 0.5                  # 最终稀疏度 (50%)
  start_step: 5000                     # 开始步数
  end_step: 15000                      # 结束步数
  update_frequency: 200                # 更新频率

# 量化配置
quantization:
  bits: 8                              # 量化位数
  quantization_type: "INT8"            # 量化类型
  compute_type_nvidia: "float16"       # NVIDIA GPU计算类型
  compute_type_universal: "float16"    # 通用计算类型
  double_quantization: true            # 双重量化
  group_size: 64                       # 组大小
  fallback_group_sizes: [32, 16, 8]    # 备选组大小

# LoRA配置
lora:
  rank: [16, 32]                       # 秩参数
  alpha: 32                            # Alpha参数
  learning_rate: 1e-5                  # 学习率
  batch_size: 2                        # 批大小
  epochs: 3                            # 训练轮次
  target_modules: ["q_proj", "k_proj", "v_proj", "o_proj"]  # 目标模块

# 数据集配置（可选）
dataset:
  zh_wiki_path: "/path/to/dataset"     # 中文维基百科数据集路径
```

### ⚙️ **参数调优建议**

#### 内存受限环境
```yaml
lora:
  batch_size: 1        # 减少批大小
  epochs: 2            # 减少训练轮次

quantization:
  group_size: 32       # 使用较小的组大小
```

#### 高性能环境
```yaml
lora:
  batch_size: 4        # 增加批大小
  epochs: 5            # 增加训练轮次

pruning:
  final_sparsity: 0.6  # 更高的稀疏度
```

## 使用示例

### 📋 **示例1: 基础模型优化**

```bash
# 1. 准备配置文件
cp purning_config.yaml my_config.yaml

# 2. 运行优化
python convert2onnx_fixed.py \
  --model_path llm/Qwen3-0.6B \
  --config_path my_config.yaml

# 3. 查看结果
ls llm/Qwen3-0.6B/converted_model/
```

### 📋 **示例2: 自定义优化参数**

```yaml
# custom_config.yaml
pruning:
  final_sparsity: 0.3  # 较低的稀疏度保持更高精度

quantization:
  group_size: 128      # 较大的组大小

lora:
  batch_size: 1        # 适应小内存环境
```

```bash
python convert2onnx_fixed.py \
  --model_path your_model_path \
  --config_path custom_config.yaml
```

### 📋 **示例3: 仅剪枝不量化**

修改配置文件或代码，跳过量化步骤：

```python
# 在代码中注释掉量化步骤
# success, msg = self._quantize_model()
```

## 输出文件说明

### 📁 **输出目录结构**

```
model_path/converted_model/
├── optimized_model.pth          # 优化后的模型权重
├── model.onnx                   # ONNX格式模型（如果成功导出）
├── tokenizer/                   # 分词器文件
│   ├── tokenizer_config.json
│   ├── tokenizer.json
│   └── special_tokens_map.json
└── model_optimized.onnx         # Jetson优化版本（如果生成）
```

### 📊 **日志文件**

```
model_conversion.log             # 详细的转换日志
```

## 故障排除

### ❗ **常见问题**

#### 1. 内存不足
```
错误: CUDA out of memory
解决: 减少batch_size或使用CPU模式
```

#### 2. ONNX导出失败
```
错误: quantized::linear_dynamic not supported
解决: 跳过量化步骤，先导出基础模型
```

#### 3. 依赖库缺失
```
错误: ModuleNotFoundError: No module named 'peft'
解决: pip install peft
```

### 🔧 **解决方案**

#### 内存优化
```yaml
# 在配置文件中调整
lora:
  batch_size: 1
  
quantization:
  group_size: 32
```

#### ONNX兼容性
```bash
# 使用修复版本
python convert2onnx_fixed.py --model_path model --config_path config.yaml
```

## 性能优化建议

### 🚀 **最佳实践**

#### 1. 分步骤优化
```bash
# 步骤1: 剪枝
python convert2onnx_fixed.py --model_path model --config_path config_pruning.yaml

# 步骤2: 量化
python convert2onnx_fixed.py --model_path model --config_path config_quantization.yaml

# 步骤3: ONNX导出（使用未量化版本）
```

#### 2. 参数调优策略
- **保守策略**: final_sparsity=0.3, 适合精度敏感应用
- **平衡策略**: final_sparsity=0.5, 推荐的默认设置
- **激进策略**: final_sparsity=0.7, 最大压缩率

#### 3. 硬件适配
```yaml
# GPU环境
lora:
  batch_size: 4

# CPU环境  
lora:
  batch_size: 1
  
quantization:
  group_size: 32
```

## 高级用法

### 🔬 **自定义剪枝策略**

```python
# 修改PyTorchPruner类
class CustomPruner(PyTorchPruner):
    def prune_model(self):
        # 自定义剪枝逻辑
        pass
```

### 🔬 **批量处理**

```bash
# 批量处理多个模型
for model in model_list; do
    python convert2onnx_fixed.py --model_path $model --config_path config.yaml
done
```

## 版本说明

### 📝 **版本对比**

| 版本 | 状态 | 说明 |
|------|------|------|
| convert2onnx.py | ⚠️ 原版 | 包含一些兼容性问题 |
| convert2onnx_fixed.py | ✅ 推荐 | 修复了所有已知问题 |
| convert2onnx_clean.py | ✅ 简化版 | 移除了复杂依赖 |

### 🎯 **推荐使用**

- **生产环境**: `convert2onnx_fixed.py`
- **开发测试**: `convert2onnx_clean.py`
- **学习研究**: `convert2onnx.py`

## 技术支持

### 📞 **获取帮助**

1. **查看日志**: `model_conversion.log`
2. **检查配置**: 验证YAML语法
3. **环境检查**: 确认依赖库版本
4. **内存监控**: 使用系统监控工具

### 🐛 **报告问题**

提供以下信息：
- 错误日志
- 配置文件
- 系统环境
- 模型信息

---

## 总结

`convert2onnx.py` 是一个功能全面的模型优化工具，通过合理配置和使用，可以显著提升模型的部署效率。建议从简单配置开始，逐步调优参数以获得最佳效果。
