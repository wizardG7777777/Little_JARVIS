import os
import glob
import torch
import time
import soundfile as sf
from transformers import WhisperProcessor, WhisperForConditionalGeneration
from pynvml import nvmlInit, nvmlDeviceGetHandleByIndex, nvmlDeviceGetMemoryInfo


def __folder_path_extract(input_path: str) -> list:
    if os.path.isdir(input_path) and os.path.exists(input_path):
        file_path_array = glob.glob(os.path.join(input_path, "*.wav"))
        file_path_array.sort()  # 保证文件顺序
        return file_path_array
    else:
        print("Invalid input path")
        return []


def get_gpu_memory():
    """获取当前GPU内存使用量(MB)"""
    nvmlInit()
    handle = nvmlDeviceGetHandleByIndex(0)
    info = nvmlDeviceGetMemoryInfo(handle)
    return info.used / (1024 ** 2)  # 转换为MB


def audio_transcription(input_path: str, output_path: str = "./"):
    # 初始化内存监控
    if torch.cuda.is_available():
        initial_mem = get_gpu_memory()
    else:
        process = psutil.Process(os.getpid())
        initial_mem = process.memory_info().rss / (1024 ** 2)  # MB

    # 记录开始时间
    start_time = time.perf_counter()

    device = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")
    model_name = "./whisper-large-v3-turbo"

    # 记录模型加载时间
    load_start = time.perf_counter()
    audio_processor = WhisperProcessor.from_pretrained(model_name)
    audio_model = WhisperForConditionalGeneration.from_pretrained(model_name).to(device)
    load_time = (time.perf_counter() - load_start) * 1000  # ms

    # 获取并排序文件
    file_paths = __folder_path_extract(input_path)
    if not file_paths:
        return

    # 读取音频文件
    audio_start = time.perf_counter()
    audio_array = [sf.read(audio) for audio in file_paths]
    sample_rate = 16000
    audio_data = [a[0] for a in audio_array if a[1] == sample_rate]
    audio_time = (time.perf_counter() - audio_start) * 1000  # ms

    # 特征提取
    feature_start = time.perf_counter()
    inputs = audio_processor(
        audio_data,
        sampling_rate=sample_rate,
        return_tensors="pt",
        return_attention_mask=True,
        padding=True
    )
    input_features = inputs.input_features.to(device)
    attention_mask = inputs.attention_mask.to(device)
    feature_time = (time.perf_counter() - feature_start) * 1000  # ms

    # 推理生成
    generate_start = time.perf_counter()
    predicted_ids = audio_model.generate(
        input_features=input_features,
        attention_mask=attention_mask,
        task="transcribe",
        language="zh",
    )
    generate_time = (time.perf_counter() - generate_start) * 1000  # ms

    # 解码
    decode_start = time.perf_counter()
    texts = audio_processor.batch_decode(predicted_ids, skip_special_tokens=True)
    decode_time = (time.perf_counter() - decode_start) * 1000  # ms

    # 计算总时间和内存消耗
    total_time = (time.perf_counter() - start_time) * 1000  # ms
    if torch.cuda.is_available():
        peak_mem = get_gpu_memory()
        mem_used = peak_mem - initial_mem
    else:
        process = psutil.Process(os.getpid())
        peak_mem = process.memory_info().rss / (1024 ** 2)
        mem_used = peak_mem - initial_mem

    # 打印性能统计
    print("\n===== 性能统计 =====")
    print(f"总处理时间: {total_time:.2f} ms")
    print(f"峰值内存使用: {mem_used:.2f} MB")
    print(f"模型加载时间: {load_time:.2f} ms")
    print(f"音频读取时间: {audio_time:.2f} ms")
    print(f"特征提取时间: {feature_time:.2f} ms")
    print(f"推理生成时间: {generate_time:.2f} ms")
    print(f"解码时间: {decode_time:.2f} ms")
    print(f"处理文件数: {len(file_paths)}")
    print(f"平均每文件时间: {total_time / len(file_paths):.2f} ms")

    # 按顺序输出结果
    print("\n===== 转录结果 =====")
    for i, (path, text) in enumerate(zip(file_paths, texts)):
        print(f"{os.path.basename(path)}: {text}")


if __name__ == "__main__":
    # 安装必要的监控库
    try:
        import psutil
    except ImportError:
        print("安装psutil用于内存监控...")
        import subprocess

        subprocess.run(["pip", "install", "psutil"])
        import psutil

    try:
        import pynvml
    except ImportError:
        print("安装pynvml用于GPU监控...")
        import subprocess

        subprocess.run(["pip", "install", "pynvml"])
        from pynvml import nvmlInit, nvmlDeviceGetHandleByIndex, nvmlDeviceGetMemoryInfo

    audio_transcription("../../TestMaterial/human_speech/output/")
