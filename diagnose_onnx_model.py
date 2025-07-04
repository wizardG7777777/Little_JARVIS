#!/usr/bin/env python3
"""
诊断ONNX模型问题

使用方法:
python diagnose_onnx_model.py

作者: JARVIS Assistant
日期: 2025-07-03
"""

import os
import sys
import traceback
from pathlib import Path

def diagnose_onnx_model():
    """诊断ONNX模型问题"""
    model_path = Path("models/voice2text/whisper-large-v3-turbo-onnx")
    
    print("=== ONNX模型诊断报告 ===\n")
    
    # 1. 检查文件结构
    print("1. 检查文件结构:")
    if model_path.exists():
        print(f"✅ 模型目录存在: {model_path}")
        files = list(model_path.iterdir())
        for file in sorted(files):
            size_mb = file.stat().st_size / (1024 * 1024) if file.is_file() else 0
            print(f"   - {file.name}: {size_mb:.2f} MB")
    else:
        print(f"❌ 模型目录不存在: {model_path}")
        return False
    
    print()
    
    # 2. 检查ONNX文件
    print("2. 检查ONNX文件:")
    onnx_files = list(model_path.glob("*.onnx"))
    if onnx_files:
        print(f"✅ 找到 {len(onnx_files)} 个ONNX文件:")
        for onnx_file in onnx_files:
            print(f"   - {onnx_file.name}")
    else:
        print("❌ 未找到ONNX文件")
        return False
    
    print()
    
    # 3. 尝试使用onnxruntime直接加载
    print("3. 使用onnxruntime直接加载:")
    try:
        import onnxruntime as ort
        
        for onnx_file in onnx_files:
            try:
                session = ort.InferenceSession(str(onnx_file))
                inputs = session.get_inputs()
                outputs = session.get_outputs()
                
                print(f"✅ {onnx_file.name} 加载成功")
                print(f"   输入: {len(inputs)} 个")
                for i, inp in enumerate(inputs):
                    print(f"     {i}: {inp.name} - {inp.shape} - {inp.type}")
                print(f"   输出: {len(outputs)} 个")
                for i, out in enumerate(outputs):
                    print(f"     {i}: {out.name} - {out.shape} - {out.type}")
                print()
                
            except Exception as e:
                print(f"❌ {onnx_file.name} 加载失败: {e}")
                
    except ImportError:
        print("❌ onnxruntime 未安装")
    
    print()
    
    # 4. 尝试使用optimum加载
    print("4. 使用optimum加载:")
    try:
        from optimum.onnxruntime import ORTModelForSpeechSeq2Seq
        from transformers import AutoProcessor
        
        try:
            print("尝试加载模型...")
            model = ORTModelForSpeechSeq2Seq.from_pretrained(str(model_path))
            print("✅ optimum模型加载成功")
            
            print("尝试加载处理器...")
            processor = AutoProcessor.from_pretrained(str(model_path))
            print("✅ 处理器加载成功")
            
        except Exception as e:
            print(f"❌ optimum加载失败: {e}")
            print("详细错误信息:")
            traceback.print_exc()
            
    except ImportError as e:
        print(f"❌ optimum 导入失败: {e}")
    
    print()
    
    # 5. 检查配置文件
    print("5. 检查配置文件:")
    config_files = ["config.json", "preprocessor_config.json", "tokenizer_config.json"]
    for config_file in config_files:
        config_path = model_path / config_file
        if config_path.exists():
            print(f"✅ {config_file} 存在")
            try:
                import json
                with open(config_path, 'r') as f:
                    config = json.load(f)
                print(f"   内容预览: {list(config.keys())[:5]}...")
            except Exception as e:
                print(f"   ⚠️  读取失败: {e}")
        else:
            print(f"❌ {config_file} 缺失")
    
    print("\n=== 诊断完成 ===")
    return True

def main():
    """主函数"""
    try:
        diagnose_onnx_model()
    except Exception as e:
        print(f"诊断过程出错: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
