@echo off
REM Install GPU packages in JARVIS conda environment
REM Created for Little_JARVIS project

echo ========================================
echo Installing GPU Packages in JARVIS Environment
echo ========================================
echo.

REM Try to activate JARVIS conda environment
echo [1/5] Activating JARVIS conda environment...
call conda activate JARVIS
if %errorlevel% neq 0 (
    echo ERROR: Could not activate JARVIS conda environment
    echo Please make sure conda is installed and JARVIS environment exists
    goto :end
) else (
    echo OK: JARVIS environment activated
)
echo.

REM Check current PyTorch version
echo [2/5] Checking current PyTorch installation...
python -c "import torch; print('Current PyTorch version:', torch.__version__); print('CUDA available:', torch.cuda.is_available())" 2>nul
if %errorlevel% neq 0 (
    echo WARNING: PyTorch not installed or import failed
)
echo.

REM Install PyTorch with CUDA support
echo [3/5] Installing PyTorch with CUDA 12.1 support...
echo This may take several minutes...
conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia -y
if %errorlevel% neq 0 (
    echo ERROR: Failed to install PyTorch with conda, trying pip
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
)
echo.

REM Install TensorFlow with GPU support
echo [4/5] Installing TensorFlow with GPU support...
pip install tensorflow[and-cuda]
echo.

REM Try to install TensorRT Python package
echo [5/5] Installing TensorRT Python package...
set "TENSORRT_ROOT=C:\Users\73524\TensorRT-10.12.0.36.Windows.win10.cuda-12.9\TensorRT-10.12.0.36"

REM First try to find and install TensorRT wheel files
if exist "%TENSORRT_ROOT%\python" (
    echo Searching for TensorRT wheel files...
    for /r "%TENSORRT_ROOT%\python" %%f in (tensorrt-*.whl) do (
        echo Found TensorRT wheel: %%f
        pip install "%%f" --force-reinstall
        goto :tensorrt_installed
    )
    echo WARNING: No TensorRT wheel files found in %TENSORRT_ROOT%\python
) else (
    echo WARNING: TensorRT Python directory not found
)

REM Try pip install as fallback
echo Trying to install TensorRT via pip...
pip install tensorrt

:tensorrt_installed
echo.

REM Verify installations
echo ========================================
echo Verifying GPU Package Installations
echo ========================================
echo.

echo Testing PyTorch CUDA support...
python -c "
import torch
print('PyTorch version:', torch.__version__)
print('CUDA available:', torch.cuda.is_available())
if torch.cuda.is_available():
    print('CUDA version:', torch.version.cuda)
    print('Number of CUDA devices:', torch.cuda.device_count())
    for i in range(torch.cuda.device_count()):
        print(f'Device {i}: {torch.cuda.get_device_name(i)}')
else:
    print('CUDA is not available in PyTorch')
"
echo.

echo Testing TensorFlow GPU support...
python -c "
try:
    import tensorflow as tf
    print('TensorFlow version:', tf.__version__)
    gpus = tf.config.list_physical_devices('GPU')
    if gpus:
        print('TensorFlow GPU devices:', len(gpus))
        for gpu in gpus:
            print(f'  {gpu}')
    else:
        print('No GPU devices found in TensorFlow')
except ImportError:
    print('TensorFlow not installed')
"
echo.

echo Testing TensorRT...
python -c "
try:
    import tensorrt as trt
    print('TensorRT version:', trt.__version__)
except ImportError:
    print('TensorRT Python package not available')
"

echo.
echo ========================================
echo Installation Completed
echo ========================================
echo.
echo You can now run test_gpu_environment.bat to verify the setup.
echo.

:end
echo Press any key to exit...
pause >nul
