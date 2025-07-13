@echo off
REM GPU Environment Test Script using JARVIS conda environment directly
REM Tests CUDA, cuDNN, and TensorRT availability in JARVIS environment
REM Created for Little_JARVIS project

echo ========================================
echo GPU Environment Test Script (JARVIS Direct)
echo ========================================
echo.

REM Define JARVIS Python path and installation paths
set "JARVIS_PYTHON=C:\Users\73524\.conda\envs\jarvis\python.exe"
set "TENSORRT_ROOT=C:\Users\73524\TensorRT-10.12.0.36.Windows.win10.cuda-12.9\TensorRT-10.12.0.36"
set "CUDNN_ROOT=C:\Users\73524\cudnn-windows-x86_64-8.9.7.29_cuda12-archive"

REM Add to PATH if directories exist
if exist "%TENSORRT_ROOT%\lib" (
    set "PATH=%TENSORRT_ROOT%\lib;%PATH%"
    echo INFO: Added TensorRT lib to PATH
)
if exist "%CUDNN_ROOT%\lib\x64" (
    set "PATH=%CUDNN_ROOT%\lib\x64;%PATH%"
    echo INFO: Added cuDNN lib to PATH
)
echo.

REM Check if JARVIS Python is available
echo [1/6] Checking JARVIS Python availability...
if exist "%JARVIS_PYTHON%" (
    echo OK: JARVIS Python found at %JARVIS_PYTHON%
    "%JARVIS_PYTHON%" --version
) else (
    echo ERROR: JARVIS Python not found at %JARVIS_PYTHON%
    goto :end
)
echo.

REM Check NVIDIA driver
echo [2/6] Checking NVIDIA driver...
nvidia-smi >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: NVIDIA driver not found or nvidia-smi not available
    goto :end
) else (
    echo OK: NVIDIA driver is available
    nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader,nounits
)
echo.

REM Check CUDA installation
echo [3/6] Checking CUDA installation...
nvcc --version >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: CUDA compiler ^(nvcc^) not found in PATH
    echo Checking environment variables...
    if defined CUDA_PATH (
        echo CUDA_PATH is set to: %CUDA_PATH%
    ) else (
        echo ERROR: CUDA_PATH environment variable not set
    )
) else (
    echo OK: CUDA compiler is available
    nvcc --version | findstr "release"
)
echo.

REM Test CUDA with PyTorch in JARVIS environment
echo [4/6] Testing CUDA with PyTorch in JARVIS environment...
echo import sys > temp_cuda_test.py
echo print('Python executable:', sys.executable) >> temp_cuda_test.py
echo print('Python version:', sys.version) >> temp_cuda_test.py
echo try: >> temp_cuda_test.py
echo     import torch >> temp_cuda_test.py
echo     print('PyTorch version:', torch.__version__) >> temp_cuda_test.py
echo     if torch.cuda.is_available(): >> temp_cuda_test.py
echo         print('CUDA is available in PyTorch') >> temp_cuda_test.py
echo         print('CUDA version:', torch.version.cuda) >> temp_cuda_test.py
echo         print('Number of CUDA devices:', torch.cuda.device_count()) >> temp_cuda_test.py
echo         for i in range(torch.cuda.device_count()): >> temp_cuda_test.py
echo             print(f'Device {i}: {torch.cuda.get_device_name(i)}') >> temp_cuda_test.py
echo         # Test a simple CUDA operation >> temp_cuda_test.py
echo         try: >> temp_cuda_test.py
echo             x = torch.tensor([1.0, 2.0, 3.0]).cuda() >> temp_cuda_test.py
echo             y = x * 2 >> temp_cuda_test.py
echo             print('CUDA tensor operation successful:', y.cpu().numpy()) >> temp_cuda_test.py
echo         except Exception as e: >> temp_cuda_test.py
echo             print('CUDA tensor operation failed:', str(e)) >> temp_cuda_test.py
echo     else: >> temp_cuda_test.py
echo         print('ERROR: CUDA is not available in PyTorch') >> temp_cuda_test.py
echo except ImportError as e: >> temp_cuda_test.py
echo     print('WARNING: PyTorch not installed:', str(e)) >> temp_cuda_test.py
echo. >> temp_cuda_test.py
echo try: >> temp_cuda_test.py
echo     import tensorflow as tf >> temp_cuda_test.py
echo     print('TensorFlow version:', tf.__version__) >> temp_cuda_test.py
echo     gpus = tf.config.list_physical_devices('GPU') >> temp_cuda_test.py
echo     if gpus: >> temp_cuda_test.py
echo         print('TensorFlow GPU devices:', len(gpus)) >> temp_cuda_test.py
echo         for gpu in gpus: >> temp_cuda_test.py
echo             print(f'  {gpu}') >> temp_cuda_test.py
echo     else: >> temp_cuda_test.py
echo         print('ERROR: No GPU devices found in TensorFlow') >> temp_cuda_test.py
echo except ImportError: >> temp_cuda_test.py
echo     print('WARNING: TensorFlow not installed') >> temp_cuda_test.py
"%JARVIS_PYTHON%" temp_cuda_test.py 2>nul
del temp_cuda_test.py 2>nul
echo.

REM Test cuDNN
echo [5/6] Testing cuDNN...

REM Check cuDNN installation directory
if exist "%CUDNN_ROOT%" (
    echo OK: cuDNN installation found at %CUDNN_ROOT%
    if exist "%CUDNN_ROOT%\lib\x64\cudnn64_8.lib" (
        echo OK: cuDNN library files found
    ) else (
        echo WARNING: cuDNN library files not found in lib\x64 directory
    )
) else (
    echo WARNING: cuDNN installation directory not found
)

echo try: > temp_cudnn_test.py
echo     import torch >> temp_cudnn_test.py
echo     if torch.cuda.is_available(): >> temp_cudnn_test.py
echo         if torch.backends.cudnn.enabled: >> temp_cudnn_test.py
echo             print('OK: cuDNN is enabled in PyTorch') >> temp_cudnn_test.py
echo             print('cuDNN version:', torch.backends.cudnn.version()) >> temp_cudnn_test.py
echo             # Test cuDNN operation >> temp_cudnn_test.py
echo             try: >> temp_cudnn_test.py
echo                 x = torch.randn(1, 3, 32, 32).cuda() >> temp_cudnn_test.py
echo                 conv = torch.nn.Conv2d(3, 16, 3).cuda() >> temp_cudnn_test.py
echo                 y = conv(x) >> temp_cudnn_test.py
echo                 print('cuDNN convolution operation successful') >> temp_cudnn_test.py
echo             except Exception as e: >> temp_cudnn_test.py
echo                 print('cuDNN operation failed:', str(e)) >> temp_cudnn_test.py
echo         else: >> temp_cudnn_test.py
echo             print('ERROR: cuDNN is not enabled in PyTorch') >> temp_cudnn_test.py
echo     else: >> temp_cudnn_test.py
echo         print('SKIP: CUDA not available, cannot test cuDNN') >> temp_cudnn_test.py
echo except ImportError: >> temp_cudnn_test.py
echo     print('WARNING: PyTorch not installed, cannot test cuDNN') >> temp_cudnn_test.py
echo. >> temp_cudnn_test.py
echo try: >> temp_cudnn_test.py
echo     import tensorflow as tf >> temp_cudnn_test.py
echo     if tf.config.list_physical_devices('GPU'): >> temp_cudnn_test.py
echo         print('OK: TensorFlow GPU support includes cuDNN') >> temp_cudnn_test.py
echo     else: >> temp_cudnn_test.py
echo         print('SKIP: No GPU devices in TensorFlow') >> temp_cudnn_test.py
echo except ImportError: >> temp_cudnn_test.py
echo     print('WARNING: TensorFlow not installed') >> temp_cudnn_test.py
"%JARVIS_PYTHON%" temp_cudnn_test.py 2>nul
del temp_cudnn_test.py 2>nul
echo.

REM Test TensorRT
echo [6/6] Testing TensorRT...

REM Check TensorRT installation directory
if exist "%TENSORRT_ROOT%" (
    echo OK: TensorRT installation found at %TENSORRT_ROOT%
    if exist "%TENSORRT_ROOT%\lib\nvinfer_10.dll" (
        echo OK: TensorRT library files found
    ) else (
        echo WARNING: TensorRT library files not found in lib directory
    )
) else (
    echo WARNING: TensorRT installation directory not found
)

echo import sys > temp_tensorrt_test.py
echo import os >> temp_tensorrt_test.py
echo tensorrt_path = r'%TENSORRT_ROOT%' >> temp_tensorrt_test.py
echo if os.path.exists(tensorrt_path): >> temp_tensorrt_test.py
echo     sys.path.insert(0, os.path.join(tensorrt_path, 'python')) >> temp_tensorrt_test.py
echo     for root, dirs, files in os.walk(os.path.join(tensorrt_path, 'python')): >> temp_tensorrt_test.py
echo         if 'tensorrt' in root: >> temp_tensorrt_test.py
echo             sys.path.insert(0, root) >> temp_tensorrt_test.py
echo try: >> temp_tensorrt_test.py
echo     import tensorrt as trt >> temp_tensorrt_test.py
echo     print('OK: TensorRT is installed') >> temp_tensorrt_test.py
echo     print('TensorRT version:', trt.__version__) >> temp_tensorrt_test.py
echo except ImportError as e: >> temp_tensorrt_test.py
echo     print('WARNING: TensorRT Python package not available:', str(e)) >> temp_tensorrt_test.py
echo. >> temp_tensorrt_test.py
echo try: >> temp_tensorrt_test.py
echo     import torch >> temp_tensorrt_test.py
echo     if hasattr(torch.backends, 'tensorrt'): >> temp_tensorrt_test.py
echo         print('OK: TensorRT backend available in PyTorch') >> temp_tensorrt_test.py
echo     else: >> temp_tensorrt_test.py
echo         print('INFO: TensorRT backend not available in PyTorch') >> temp_tensorrt_test.py
echo except ImportError: >> temp_tensorrt_test.py
echo     print('WARNING: PyTorch not installed') >> temp_tensorrt_test.py
echo. >> temp_tensorrt_test.py
echo try: >> temp_tensorrt_test.py
echo     import tensorflow as tf >> temp_tensorrt_test.py
echo     try: >> temp_tensorrt_test.py
echo         from tensorflow.python.compiler.tensorrt import trt_convert as trt >> temp_tensorrt_test.py
echo         print('OK: TensorRT integration available in TensorFlow') >> temp_tensorrt_test.py
echo     except ImportError: >> temp_tensorrt_test.py
echo         print('INFO: TensorRT integration not available in TensorFlow') >> temp_tensorrt_test.py
echo except ImportError: >> temp_tensorrt_test.py
echo     print('WARNING: TensorFlow not installed') >> temp_tensorrt_test.py
"%JARVIS_PYTHON%" temp_tensorrt_test.py 2>nul
del temp_tensorrt_test.py 2>nul

:end
echo.
echo ========================================
echo GPU Environment Test Completed
echo ========================================
echo.
echo Press any key to exit...
pause >nul
