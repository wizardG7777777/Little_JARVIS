import os
import glob
import sys

import numpy
import torch
import soundfile as sf
import time # for stage1 timing test, can be deleted when stage1 test is done
from transformers import WhisperProcessor, WhisperForConditionalGeneration


def __folder_path_extract(input_path:str)->list:
    if os.path.isdir(input_path) and os.path.exists(input_path):
        file_path_array = glob.glob(os.path.join(input_path, "*.wav"))
        file_path_array.sort() # Make sure files are sorted
        return file_path_array
    else:
        print("Invalid input path")
        return [] # return empty list if input is not a valid directory, and make sure the function will not break the program
def audio_reading (sample_rate:int, file_path:str="../../TestMaterial/human_speech/output/")-> list:
    # Read audio file and return audio data and sample rate
    # If no input parameter is used, use default path
    audio_array = [sf.read(audio) for audio in __folder_path_extract(input_path=file_path)]
    audio_data = []
    for audio in audio_array:
        if audio[1] == sample_rate:
            audio_data.append(audio)
        else:
            # print(f"Audio {audio} is not 16000Hz, please resample it")
            pass
    return audio_data
def audio_from_mic() -> list:
    # This function set up for future, ready for reading from mic, it suppose to return a list which contains audio data

   """
   Explanation:
   for every element in list, they are:
   first element is audio data, which is numpy array
   second element is sample rate, which is int, and should be 16000 by default
   """
   return []
def audio_transcription(input_audio_data:list,
                        voice_model:str="./whisper-base",
                        output_path:str="./")->str:
    # Use cuda priority, then metal, last cpu
    device = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")

    # load model and processor in same directory
    model_name = voice_model
    audio_processor = WhisperProcessor.from_pretrained(model_name)
    audio_model = WhisperForConditionalGeneration.from_pretrained(model_name).to(device)

    """
    audio loading, remember, every element in audio_array is tuple
    tuple[0] is the audio data, which is numpy array, also the raw data need to be processed
    tuple[1] is the sample rate, which is int, and should be 16000, other wise it will lead error
    """

    sample_rate = 16000
    audio_data = [a[0] for a in input_audio_data if a[1] == sample_rate]
    if len(audio_data) == 0:
        print("No audio data, please check the input audio data")
        return ""

    # feature extract and pre-process
    inputs = audio_processor(
        audio_data,
        sampling_rate=sample_rate,
        return_tensors="pt",
        return_attention_mask=True,  # Get attention mask for following process
        padding=True  # Enable it for batch processing
    )
    input_features = inputs.input_features.to(device)
    attention_mask = inputs.attention_mask.to(device)

    # Transcript
    start_time_stamp = time.perf_counter()
    predicted_ids = audio_model.generate(
        input_features=input_features,
        attention_mask=attention_mask,
        task="transcribe",
        language="zh",
    )
    text = audio_processor.batch_decode(predicted_ids, skip_special_tokens=True)
    end_time_stamp = time.perf_counter()
    print(f"Time cost: {(end_time_stamp - start_time_stamp)*1000} ms")

    # print("Here is the result：", text)
    result = ""
    for t in text:
        if t != "" and type(t) is type("Hello"):
            result += t
    return result

class AudioModel:
    def __init__(self, model_path:str):
        # Model initialization, load model from disk into memory, use cuda priority

        # Check if model path exists
        if not os.path.exists(model_path):
            print(f"警告: 模型路径 '{model_path}' 不存在！")
            print("请检查模型路径是否正确，或确保模型文件已下载到指定位置。")
            sys.exit(1)  # 终止程序执行

        # Store model path
        self.model_path = model_path

        # Set device priority: cuda > mps > cpu
        self.device = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")

        # Load model and processor
        try:
            print(f"正在从 '{model_path}' 加载模型...")
            self.processor = WhisperProcessor.from_pretrained(model_path)
            self.model = WhisperForConditionalGeneration.from_pretrained(model_path).to(self.device)
            print(f"模型加载成功，使用设备: {self.device}")
        except Exception as e:
            print(f"警告: 模型加载失败！错误信息: {str(e)}")
            print("请检查模型文件是否完整或格式是否正确。")
            sys.exit(1)  # 终止程序执行

        # model has been loaded successfully
        self.is_ready = True
