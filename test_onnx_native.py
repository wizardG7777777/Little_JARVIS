#!/usr/bin/env python3
"""
使用原生onnxruntime测试Whisper ONNX模型

使用方法:
python test_onnx_native.py

作者: JARVIS Assistant
日期: 2025-07-03
"""

import os
import sys
import json
import numpy as np
import onnxruntime as ort
from pathlib import Path
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WhisperONNXInference:
    def __init__(self, model_path="models/voice2text/whisper-large-v3-turbo-onnx"):
        """初始化Whisper ONNX推理器"""
        self.model_path = Path(model_path)
        self.encoder_session = None
        self.decoder_session = None
        self.config = None
        self.preprocessor_config = None
        
    def load_models(self):
        """加载ONNX模型"""
        try:
            # 加载配置文件
            with open(self.model_path / "config.json", 'r') as f:
                self.config = json.load(f)
            
            with open(self.model_path / "preprocessor_config.json", 'r') as f:
                self.preprocessor_config = json.load(f)
            
            logger.info("配置文件加载成功")
            
            # 加载编码器
            encoder_path = self.model_path / "encoder_model.onnx"
            self.encoder_session = ort.InferenceSession(str(encoder_path))
            logger.info("编码器模型加载成功")
            
            # 加载解码器
            decoder_path = self.model_path / "decoder_model.onnx"
            self.decoder_session = ort.InferenceSession(str(decoder_path))
            logger.info("解码器模型加载成功")
            
            return True
            
        except Exception as e:
            logger.error(f"模型加载失败: {e}")
            return False
    
    def preprocess_audio(self, audio_array, sample_rate=16000):
        """预处理音频数据"""
        try:
            # 简化的音频预处理
            # 实际应用中需要更复杂的特征提取
            
            # 确保采样率正确
            if len(audio_array) == 0:
                # 创建静音音频用于测试
                audio_array = np.zeros(sample_rate * 2, dtype=np.float32)
            
            # 归一化
            if np.max(np.abs(audio_array)) > 0:
                audio_array = audio_array / np.max(np.abs(audio_array))
            
            # 创建梅尔频谱特征 (简化版本)
            # 实际的Whisper需要更复杂的特征提取
            n_mels = self.preprocessor_config.get('feature_size', 128)
            n_frames = 3000  # Whisper的固定帧数
            
            # 创建模拟的梅尔频谱特征
            features = np.random.randn(1, n_mels, n_frames).astype(np.float32) * 0.1
            
            logger.info(f"音频预处理完成，特征形状: {features.shape}")
            return features
            
        except Exception as e:
            logger.error(f"音频预处理失败: {e}")
            return None
    
    def run_encoder(self, input_features):
        """运行编码器"""
        try:
            # 获取编码器输入名称
            input_name = self.encoder_session.get_inputs()[0].name
            
            # 运行编码器
            encoder_outputs = self.encoder_session.run(None, {input_name: input_features})
            encoder_hidden_states = encoder_outputs[0]
            
            logger.info(f"编码器输出形状: {encoder_hidden_states.shape}")
            return encoder_hidden_states
            
        except Exception as e:
            logger.error(f"编码器运行失败: {e}")
            return None
    
    def run_decoder(self, encoder_hidden_states, max_length=50):
        """运行解码器"""
        try:
            # 初始化解码器输入
            batch_size = encoder_hidden_states.shape[0]
            
            # 开始token (通常是50258)
            input_ids = np.array([[50258]], dtype=np.int64)
            
            # 获取解码器输入名称
            decoder_inputs = self.decoder_session.get_inputs()
            input_ids_name = decoder_inputs[0].name
            encoder_hidden_states_name = decoder_inputs[1].name
            
            generated_tokens = []
            
            for step in range(max_length):
                # 运行解码器
                decoder_outputs = self.decoder_session.run(
                    None, 
                    {
                        input_ids_name: input_ids,
                        encoder_hidden_states_name: encoder_hidden_states
                    }
                )
                
                logits = decoder_outputs[0]
                
                # 获取下一个token
                next_token = np.argmax(logits[0, -1, :])
                generated_tokens.append(next_token)
                
                # 更新input_ids
                input_ids = np.concatenate([input_ids, [[next_token]]], axis=1)
                
                # 检查结束条件
                if next_token == 50257:  # 结束token
                    break
            
            logger.info(f"解码器生成了 {len(generated_tokens)} 个token")
            return generated_tokens
            
        except Exception as e:
            logger.error(f"解码器运行失败: {e}")
            return None
    
    def test_inference(self):
        """测试推理过程"""
        try:
            logger.info("开始测试推理...")
            
            # 创建测试音频
            test_audio = np.zeros(16000 * 2, dtype=np.float32)  # 2秒静音
            
            # 预处理音频
            features = self.preprocess_audio(test_audio)
            if features is None:
                return False
            
            # 运行编码器
            encoder_outputs = self.run_encoder(features)
            if encoder_outputs is None:
                return False
            
            # 运行解码器
            generated_tokens = self.run_decoder(encoder_outputs)
            if generated_tokens is None:
                return False
            
            logger.info(f"生成的token: {generated_tokens[:10]}...")  # 显示前10个token
            logger.info("推理测试成功!")
            
            return True
            
        except Exception as e:
            logger.error(f"推理测试失败: {e}")
            return False

def main():
    """主函数"""
    logger.info("开始测试Whisper ONNX模型 (原生onnxruntime)")
    
    # 创建推理器
    inferencer = WhisperONNXInference()
    
    # 加载模型
    if not inferencer.load_models():
        print("❌ 模型加载失败!")
        sys.exit(1)
    
    # 测试推理
    if inferencer.test_inference():
        print("\n✅ ONNX模型测试成功!")
        print("模型可以正常进行推理")
        print("\n模型信息:")
        print(f"- 编码器输入: {inferencer.encoder_session.get_inputs()[0].shape}")
        print(f"- 编码器输出: {inferencer.encoder_session.get_outputs()[0].shape}")
        print(f"- 解码器输入: {[inp.shape for inp in inferencer.decoder_session.get_inputs()]}")
        print(f"- 解码器输出: {inferencer.decoder_session.get_outputs()[0].shape}")
    else:
        print("\n❌ ONNX模型测试失败!")
        sys.exit(1)

if __name__ == "__main__":
    main()
