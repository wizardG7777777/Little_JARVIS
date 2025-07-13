#!/bin/bash
# GPU Environment Test Script for Linux
# Tests CUDA, cuDNN, and TensorRT availability
# Created for Little_JARVIS project

echo "========================================"
echo "GPU Environment Test Script"
echo "========================================"
echo

# Check if Python is available
echo "[1/6] Checking Python availability..."
if command -v python3 &> /dev/null; then
    echo "OK: Python3 is available"
    python3 --version
elif command -v python &> /dev/null; then
    echo "OK: Python is available"
    python --version
    PYTHON_CMD="python"
else
    echo "ERROR: Python is not installed or not in PATH"
    exit 1
fi

# Set Python command
if [ -z "$PYTHON_CMD" ]; then
    PYTHON_CMD="python3"
fi
echo

# Check NVIDIA driver
echo "[2/6] Checking NVIDIA driver..."
if command -v nvidia-smi &> /dev/null; then
    echo "OK: NVIDIA driver is available"
    nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader,nounits
else
    echo "ERROR: NVIDIA driver not found or nvidia-smi not available"
    exit 1
fi
echo

# Check CUDA installation
echo "[3/6] Checking CUDA installation..."
if command -v nvcc &> /dev/null; then
    echo "OK: CUDA compiler is available"
    nvcc --version | grep "release"
else
    echo "WARNING: CUDA compiler (nvcc) not found in PATH"
    echo "Checking common CUDA installation paths..."
    if [ -d "/usr/local/cuda" ]; then
        echo "CUDA found at: /usr/local/cuda"
        if [ -f "/usr/local/cuda/bin/nvcc" ]; then
            echo "nvcc found at: /usr/local/cuda/bin/nvcc"
            /usr/local/cuda/bin/nvcc --version | grep "release"
        fi
    else
        echo "ERROR: CUDA installation not found"
    fi
fi
echo

# Test CUDA with Python
echo "[4/6] Testing CUDA with Python..."
$PYTHON_CMD -c "
import sys
try:
    import torch
    print('PyTorch version:', torch.__version__)
    if torch.cuda.is_available():
        print('CUDA is available in PyTorch')
        print('CUDA version:', torch.version.cuda)
        print('Number of CUDA devices:', torch.cuda.device_count())
        for i in range(torch.cuda.device_count()):
            print(f'Device {i}: {torch.cuda.get_device_name(i)}')
    else:
        print('ERROR: CUDA is not available in PyTorch')
except ImportError:
    print('WARNING: PyTorch not installed')

try:
    import tensorflow as tf
    print('TensorFlow version:', tf.__version__)
    gpus = tf.config.list_physical_devices('GPU')
    if gpus:
        print('TensorFlow GPU devices:', len(gpus))
        for gpu in gpus:
            print(f'  {gpu}')
    else:
        print('ERROR: No GPU devices found in TensorFlow')
except ImportError:
    print('WARNING: TensorFlow not installed')
" 2>/dev/null
echo

# Test cuDNN
echo "[5/6] Testing cuDNN..."
$PYTHON_CMD -c "
try:
    import torch
    if torch.cuda.is_available():
        if torch.backends.cudnn.enabled:
            print('OK: cuDNN is enabled in PyTorch')
            print('cuDNN version:', torch.backends.cudnn.version())
        else:
            print('ERROR: cuDNN is not enabled in PyTorch')
    else:
        print('SKIP: CUDA not available, cannot test cuDNN')
except ImportError:
    print('WARNING: PyTorch not installed, cannot test cuDNN')

try:
    import tensorflow as tf
    if tf.config.list_physical_devices('GPU'):
        print('OK: TensorFlow GPU support includes cuDNN')
    else:
        print('SKIP: No GPU devices in TensorFlow')
except ImportError:
    print('WARNING: TensorFlow not installed')
" 2>/dev/null
echo

# Test TensorRT
echo "[6/6] Testing TensorRT..."
$PYTHON_CMD -c "
try:
    import tensorrt as trt
    print('OK: TensorRT is installed')
    print('TensorRT version:', trt.__version__)
except ImportError:
    print('WARNING: TensorRT not installed')

try:
    import torch
    if hasattr(torch.backends, 'tensorrt'):
        print('OK: TensorRT backend available in PyTorch')
    else:
        print('INFO: TensorRT backend not available in PyTorch')
except ImportError:
    print('WARNING: PyTorch not installed')

try:
    import tensorflow as tf
    try:
        from tensorflow.python.compiler.tensorrt import trt_convert as trt
        print('OK: TensorRT integration available in TensorFlow')
    except ImportError:
        print('INFO: TensorRT integration not available in TensorFlow')
except ImportError:
    print('WARNING: TensorFlow not installed')
" 2>/dev/null

echo
echo "========================================"
echo "GPU Environment Test Completed"
echo "========================================"
echo
