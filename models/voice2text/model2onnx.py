from transformers.onnx import export, FeaturesManager
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor
import os
import torch
from pathlib import Path

current_dir = os.path.dirname(os.path.abspath(__file__))
model_name = os.path.join(current_dir, "whisper-large-v3-turbo")

print("正在加载模型和处理器...")
# 使用正确的模型类和处理器
processor = AutoProcessor.from_pretrained(model_name)
model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_name,
    torch_dtype=torch.float32,  # 使用float32以避免一些ONNX导出问题
    low_cpu_mem_usage=True
)

print("正在配置ONNX导出...")
# 指定正确的任务特征 - 使用default特征
task = "default"
model_kind, model_onnx_config = FeaturesManager.check_supported_model_or_raise(model, feature=task)
onnx_config = model_onnx_config(model.config)

# 导出 ONNX 模型
onnx_path = Path(current_dir) / "whisperv3-turbo.onnx"
print(f"开始导出ONNX模型到: {onnx_path}")

try:
    export(
        preprocessor=processor,              # Whisper处理器（包含tokenizer和feature_extractor）
        model=model,                         # Whisper模型
        config=onnx_config,                  # ONNX配置
        output=onnx_path,                    # 输出路径
        opset=14                             # 降低ONNX操作集版本以提高兼容性
    )
    print("ONNX模型导出成功！")
except Exception as e:
    print(f"导出过程中出现错误: {e}")
    print("尝试使用更简单的配置...")

    # 如果失败，尝试使用更简单的配置
    try:
        export(
            preprocessor=processor,
            model=model,
            config=onnx_config,
            output=onnx_path,
            opset=11  # 使用更低的操作集版本
        )
        print("使用简化配置导出成功！")
    except Exception as e2:
        print(f"简化配置也失败了: {e2}")
        raise e2
