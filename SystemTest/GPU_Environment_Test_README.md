# GPU环境测试脚本说明

## 概述
本文件夹包含用于测试CUDA、cuDNN和TensorRT可用性的脚本，适用于Windows和Linux系统。

## 文件说明

### Windows批处理文件
- **文件名**: `test_gpu_environment.bat`
- **用途**: 在Windows系统上测试GPU环境（使用系统Python）
- **运行方式**: 双击文件或在命令行中执行 `test_gpu_environment.bat`

- **文件名**: `test_gpu_environment_jarvis_direct.bat`
- **用途**: 在Windows系统上测试GPU环境（使用JARVIS conda环境）
- **运行方式**: 双击文件或在命令行中执行 `test_gpu_environment_jarvis_direct.bat`
- **推荐**: 这是推荐的测试脚本，因为它直接使用JARVIS环境

### 环境配置脚本
- **文件名**: `setup_gpu_environment.bat`
- **用途**: 设置TensorRT和cuDNN环境变量和路径
- **运行方式**: 以管理员权限运行

- **文件名**: `install_gpu_packages_jarvis.bat`
- **用途**: 在JARVIS环境中安装GPU相关的Python包
- **运行方式**: 双击文件或在命令行中执行

### Linux Shell脚本
- **文件名**: `test_gpu_environment.sh`
- **用途**: 在Linux系统上测试GPU环境
- **运行方式**: 在终端中执行 `./test_gpu_environment.sh`
- **注意**: 需要先添加执行权限 `chmod +x test_gpu_environment.sh`

## 测试内容

两个脚本都会执行以下6项测试：

1. **Python可用性检查**
   - 验证Python是否正确安装并可访问
   - 显示Python版本信息

2. **NVIDIA驱动检查**
   - 使用`nvidia-smi`命令检查NVIDIA驱动
   - 显示GPU型号、驱动版本和显存信息

3. **CUDA安装检查**
   - 检查CUDA编译器(nvcc)是否可用
   - 显示CUDA版本信息
   - 检查CUDA环境变量设置

4. **CUDA Python支持测试**
   - 测试PyTorch中的CUDA支持
   - 测试TensorFlow中的GPU支持
   - 显示可用的GPU设备信息

5. **cuDNN测试**
   - 检查PyTorch中的cuDNN支持
   - 检查TensorFlow中的cuDNN集成
   - 显示cuDNN版本信息

6. **TensorRT测试**
   - 检查TensorRT是否安装
   - 测试PyTorch中的TensorRT后端
   - 测试TensorFlow中的TensorRT集成

## 输出解释

### 状态标识
- **OK**: 功能正常可用
- **WARNING**: 功能不可用但不影响其他测试
- **ERROR**: 严重错误，可能影响后续测试
- **INFO**: 信息性消息
- **SKIP**: 由于前置条件不满足而跳过的测试

### 常见问题及解决方案

#### CUDA不可用
- **现象**: "CUDA is not available in PyTorch"
- **原因**: 安装的是CPU版本的PyTorch
- **解决**: 安装GPU版本的PyTorch
  ```bash
  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
  ```

#### TensorFlow未安装
- **现象**: "TensorFlow not installed"
- **解决**: 安装TensorFlow GPU版本
  ```bash
  pip install tensorflow[and-cuda]
  ```

#### TensorRT未安装
- **现象**: "TensorRT not installed"
- **解决**: 安装TensorRT
  ```bash
  pip install tensorrt
  ```

## 系统要求

### 硬件要求
- NVIDIA GPU (支持CUDA的显卡)
- 足够的显存 (建议4GB以上)

### 软件要求
- Python 3.7+
- NVIDIA驱动程序
- CUDA Toolkit
- 相应的深度学习框架 (PyTorch/TensorFlow)

## 注意事项

1. **权限要求**: Linux系统需要执行权限
2. **网络连接**: 某些测试可能需要网络连接来验证库的可用性
3. **临时文件**: Windows批处理文件会创建临时Python文件，测试完成后会自动删除
4. **兼容性**: 脚本兼容Python 3.7+版本

## 故障排除

如果测试失败，请检查：
1. NVIDIA驱动是否正确安装
2. CUDA版本是否与深度学习框架兼容
3. Python环境是否正确配置
4. 是否有足够的系统权限

## 成功配置示例

基于用户的实际环境配置，以下是成功的测试结果：

### 环境信息
- **操作系统**: Windows 11
- **GPU**: NVIDIA GeForce RTX 4060 (8GB显存)
- **NVIDIA驱动**: 576.02
- **CUDA**: 12.6
- **Python环境**: JARVIS conda环境 (Python 3.12.9)
- **PyTorch**: 2.7.1+cu126 (CUDA 12.6版本)
- **TensorRT**: 10.12.0.36
- **cuDNN**: 8.9.7.29

### 安装路径
- **TensorRT**: `C:\Users\73524\TensorRT-10.12.0.36.Windows.win10.cuda-12.9\TensorRT-10.12.0.36`
- **cuDNN**: `C:\Users\73524\cudnn-windows-x86_64-8.9.7.29_cuda12-archive`
- **JARVIS环境**: `C:\Users\73524\.conda\envs\jarvis`

### 测试结果
✅ **CUDA**: 可用，版本12.6
✅ **PyTorch CUDA支持**: 可用，能够执行CUDA张量操作
✅ **cuDNN**: 可用，版本90701，能够执行卷积操作
✅ **TensorRT**: 可用，版本10.12.0.36
❌ **TensorFlow**: 未安装（可选）

## 更新日志

- 2025-07-12: 初始版本，支持CUDA、cuDNN、TensorRT测试
- 2025-07-12: 添加JARVIS环境直接测试脚本，修复路径检测问题，验证成功配置
