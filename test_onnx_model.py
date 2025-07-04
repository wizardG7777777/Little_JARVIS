#!/usr/bin/env python3
"""
测试转换后的Whisper ONNX模型

使用方法:
python test_onnx_model.py

作者: JARVIS Assistant
日期: 2025-07-03
"""

import os
import sys
import torch
import logging
import numpy as np
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_onnx_model():
    """测试ONNX模型"""
    try:
        from optimum.onnxruntime import ORTModelForSpeechSeq2Seq
        from transformers import AutoProcessor
        
        model_path = "models/voice2text/whisper-large-v3-turbo-onnx"
        
        logger.info("加载ONNX模型...")
        
        # 加载ONNX模型和处理器
        model = ORTModelForSpeechSeq2Seq.from_pretrained(model_path)
        processor = AutoProcessor.from_pretrained(model_path)
        
        logger.info("ONNX模型加载成功!")
        
        # 创建一个简单的测试音频（静音）
        logger.info("创建测试音频数据...")
        sample_rate = 16000
        duration = 2  # 2秒
        test_audio = np.zeros(sample_rate * duration, dtype=np.float32)
        
        # 处理音频
        logger.info("处理音频数据...")
        inputs = processor(
            test_audio,
            sampling_rate=sample_rate,
            return_tensors="pt"
        )
        
        # 进行推理
        logger.info("执行模型推理...")
        with torch.no_grad():
            generated_ids = model.generate(**inputs, max_new_tokens=50)
        
        # 解码结果
        transcription = processor.batch_decode(generated_ids, skip_special_tokens=True)
        
        logger.info(f"转录结果: {transcription}")
        logger.info("ONNX模型测试成功!")
        
        return True
        
    except Exception as e:
        logger.error(f"ONNX模型测试失败: {e}")
        return False

def main():
    """主函数"""
    logger.info("开始测试Whisper ONNX模型")
    
    if test_onnx_model():
        print("\n✅ ONNX模型测试成功!")
        print("模型可以正常进行语音识别推理")
    else:
        print("\n❌ ONNX模型测试失败!")
        print("请检查模型文件是否完整")
        sys.exit(1)

if __name__ == "__main__":
    main()
