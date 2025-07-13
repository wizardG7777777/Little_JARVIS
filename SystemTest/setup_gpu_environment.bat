@echo off
REM GPU Environment Setup Script for Windows
REM Sets up TensorRT and cuDNN paths for Little_JARVIS project
REM Created for Little_JARVIS project

echo ========================================
echo GPU Environment Setup Script
echo ========================================
echo.

REM Define paths
set TENSORRT_ROOT=C:\Users\73524\TensorRT-10.12.0.36.Windows.win10.cuda-12.9\TensorRT-10.12.0.36
set CUDNN_ROOT=C:\Users\73524\cudnn-windows-x86_64-8.9.7.29_cuda12-archive

echo [1/4] Checking TensorRT installation...
if exist "%TENSORRT_ROOT%" (
    echo OK: TensorRT directory found at %TENSORRT_ROOT%
    if exist "%TENSORRT_ROOT%\lib" (
        echo OK: TensorRT lib directory found
    ) else (
        echo WARNING: TensorRT lib directory not found
    )
    if exist "%TENSORRT_ROOT%\include" (
        echo OK: TensorRT include directory found
    ) else (
        echo WARNING: TensorRT include directory not found
    )
) else (
    echo ERROR: TensorRT directory not found at %TENSORRT_ROOT%
    goto :end
)
echo.

echo [2/4] Checking cuDNN installation...
if exist "%CUDNN_ROOT%" (
    echo OK: cuDNN directory found at %CUDNN_ROOT%
    if exist "%CUDNN_ROOT%\lib" (
        echo OK: cuDNN lib directory found
    ) else (
        echo WARNING: cuDNN lib directory not found
    )
    if exist "%CUDNN_ROOT%\include" (
        echo OK: cuDNN include directory found
    ) else (
        echo WARNING: cuDNN include directory not found
    )
) else (
    echo ERROR: cuDNN directory not found at %CUDNN_ROOT%
    goto :end
)
echo.

echo [3/4] Setting up environment variables...
REM Add TensorRT to PATH
set PATH=%TENSORRT_ROOT%\lib;%PATH%
echo Added TensorRT lib to PATH: %TENSORRT_ROOT%\lib

REM Add cuDNN to PATH
set PATH=%CUDNN_ROOT%\lib;%PATH%
echo Added cuDNN lib to PATH: %CUDNN_ROOT%\lib

REM Set TensorRT environment variables
set TENSORRT_PATH=%TENSORRT_ROOT%
set TRT_LIB_DIR=%TENSORRT_ROOT%\lib
set TRT_INCLUDE_DIR=%TENSORRT_ROOT%\include

REM Set cuDNN environment variables
set CUDNN_PATH=%CUDNN_ROOT%
set CUDNN_LIB_DIR=%CUDNN_ROOT%\lib
set CUDNN_INCLUDE_DIR=%CUDNN_ROOT%\include

echo Environment variables set successfully.
echo.

echo [4/4] Installing Python packages with correct paths...
echo Installing TensorRT Python package...
if exist "%TENSORRT_ROOT%\python" (
    for /d %%i in ("%TENSORRT_ROOT%\python\*") do (
        if exist "%%i\tensorrt-*.whl" (
            echo Found TensorRT wheel in %%i
            python -m pip install "%%i\tensorrt-*.whl" --force-reinstall
        )
    )
) else (
    echo WARNING: TensorRT Python directory not found, trying pip install
    python -m pip install tensorrt
)

echo.
echo Installing PyTorch with CUDA support...
python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 --force-reinstall

echo.
echo Installing TensorFlow with GPU support...
python -m pip install tensorflow[and-cuda] --force-reinstall

echo.
echo ========================================
echo Environment Setup Completed
echo ========================================
echo.
echo Current environment variables:
echo TENSORRT_PATH=%TENSORRT_PATH%
echo CUDNN_PATH=%CUDNN_PATH%
echo PATH includes TensorRT and cuDNN lib directories
echo.
echo You can now run test_gpu_environment.bat to verify the setup.
echo.

:end
echo Press any key to exit...
pause >nul
