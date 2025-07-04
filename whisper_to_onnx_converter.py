#!/usr/bin/env python3
"""
Whisper Large V3 Turbo to ONNX Converter
将whisper-large-v3-turbo模型转换为ONNX格式

使用方法:
python whisper_to_onnx_converter.py

作者: JARVIS Assistant
日期: 2025-07-03
"""

import os
import sys
import torch
import logging
from pathlib import Path
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor
from optimum.onnxruntime import ORTModelForSpeechSeq2Seq
from optimum.exporters.onnx import main_export

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('whisper_conversion.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class WhisperONNXConverter:
    def __init__(self, model_path="./models/voice2text/whisper-large-v3-turbo", 
                 output_path="./models/voice2text/whisper-large-v3-turbo-onnx"):
        """
        初始化转换器
        
        Args:
            model_path (str): 源模型路径
            output_path (str): ONNX模型输出路径
        """
        self.model_path = Path(model_path)
        self.output_path = Path(output_path)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        
        logger.info(f"使用设备: {self.device}")
        logger.info(f"数据类型: {self.torch_dtype}")
        
    def check_dependencies(self):
        """检查必要的依赖包"""
        try:
            import optimum
            import onnx
            import onnxruntime
            logger.info("所有必要依赖包已安装")
            return True
        except ImportError as e:
            logger.error(f"缺少依赖包: {e}")
            logger.error("请运行: pip install -r requirements_onnx.txt")
            return False
    
    def verify_model_files(self):
        """验证模型文件是否存在"""
        required_files = [
            "config.json",
            "model.safetensors",
            "tokenizer.json",
            "preprocessor_config.json"
        ]
        
        missing_files = []
        for file in required_files:
            if not (self.model_path / file).exists():
                missing_files.append(file)
        
        if missing_files:
            logger.error(f"缺少模型文件: {missing_files}")
            return False
        
        logger.info("模型文件验证通过")
        return True
    
    def load_model(self):
        """加载Whisper模型"""
        try:
            logger.info("正在加载Whisper模型...")
            
            # 加载模型
            self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
                str(self.model_path),
                torch_dtype=self.torch_dtype,
                low_cpu_mem_usage=True,
                use_safetensors=True
            )
            
            # 加载处理器
            self.processor = AutoProcessor.from_pretrained(str(self.model_path))
            
            logger.info("模型加载成功")
            return True
            
        except Exception as e:
            logger.error(f"模型加载失败: {e}")
            return False
    
    def convert_to_onnx(self):
        """转换模型到ONNX格式"""
        try:
            logger.info("开始转换到ONNX格式...")
            
            # 创建输出目录
            self.output_path.mkdir(parents=True, exist_ok=True)
            
            # 使用optimum进行转换
            logger.info("使用Optimum进行ONNX转换...")
            
            # 方法1: 使用ORTModelForSpeechSeq2Seq.from_pretrained进行转换
            try:
                ort_model = ORTModelForSpeechSeq2Seq.from_pretrained(
                    str(self.model_path),
                    export=True,
                    use_cache=False
                )
                
                # 保存ONNX模型
                ort_model.save_pretrained(str(self.output_path))
                
                # 同时保存处理器
                self.processor.save_pretrained(str(self.output_path))
                
                logger.info(f"ONNX模型已保存到: {self.output_path}")
                return True
                
            except Exception as e:
                logger.warning(f"方法1转换失败: {e}")
                logger.info("尝试方法2...")
                
                # 方法2: 使用main_export函数
                main_export(
                    model_name_or_path=str(self.model_path),
                    output=str(self.output_path),
                    task="automatic-speech-recognition",
                    device=self.device,
                    fp16=self.torch_dtype == torch.float16
                )
                
                logger.info(f"ONNX模型已保存到: {self.output_path}")
                return True
                
        except Exception as e:
            logger.error(f"ONNX转换失败: {e}")
            return False
    
    def verify_onnx_model(self):
        """验证转换后的ONNX模型"""
        try:
            logger.info("验证ONNX模型...")
            
            # 检查ONNX文件是否存在
            onnx_files = list(self.output_path.glob("*.onnx"))
            if not onnx_files:
                logger.error("未找到ONNX文件")
                return False
            
            # 尝试加载ONNX模型
            ort_model = ORTModelForSpeechSeq2Seq.from_pretrained(str(self.output_path))
            processor = AutoProcessor.from_pretrained(str(self.output_path))
            
            logger.info("ONNX模型验证成功")
            
            # 显示模型信息
            for onnx_file in onnx_files:
                size_mb = onnx_file.stat().st_size / (1024 * 1024)
                logger.info(f"ONNX文件: {onnx_file.name}, 大小: {size_mb:.2f} MB")
            
            return True
            
        except Exception as e:
            logger.error(f"ONNX模型验证失败: {e}")
            return False
    
    def run_conversion(self):
        """执行完整的转换流程"""
        logger.info("开始Whisper模型ONNX转换流程")
        
        # 检查依赖
        if not self.check_dependencies():
            return False
        
        # 验证模型文件
        if not self.verify_model_files():
            return False
        
        # 加载模型
        if not self.load_model():
            return False
        
        # 转换到ONNX
        if not self.convert_to_onnx():
            return False
        
        # 验证ONNX模型
        if not self.verify_onnx_model():
            return False
        
        logger.info("Whisper模型ONNX转换完成!")
        logger.info(f"转换后的模型保存在: {self.output_path}")
        
        return True

def main():
    """主函数"""
    try:
        # 创建转换器实例
        converter = WhisperONNXConverter()
        
        # 执行转换
        success = converter.run_conversion()
        
        if success:
            print("\n✅ 转换成功完成!")
            print(f"ONNX模型保存位置: {converter.output_path}")
            print("\n可以使用以下代码测试ONNX模型:")
            print("```python")
            print("from optimum.onnxruntime import ORTModelForSpeechSeq2Seq")
            print("from transformers import AutoProcessor")
            print(f"model = ORTModelForSpeechSeq2Seq.from_pretrained('{converter.output_path}')")
            print(f"processor = AutoProcessor.from_pretrained('{converter.output_path}')")
            print("```")
        else:
            print("\n❌ 转换失败!")
            print("请查看日志文件 whisper_conversion.log 获取详细错误信息")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("用户中断转换过程")
        sys.exit(1)
    except Exception as e:
        logger.error(f"转换过程中发生未预期错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
