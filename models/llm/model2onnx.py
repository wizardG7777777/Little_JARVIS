from transformers.onnx import export, FeaturesManager
from transformers import AutoTokenizer, AutoModel
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
model_name = os.path.join(current_dir, "Qwen3-0.6B")
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)
task = "text-generation"  # 根据模型类型调整
model_kind, model_onnx_config = FeaturesManager.check_supported_model_or_raise(model, feature=task)
onnx_config = model_onnx_config(model.config)
# 导出 ONNX 模型
onnx_path = os.path.join(current_dir, "qwen3_0.6b.onnx")
export(
    preprocessor= tokenizer,              # Hugging Face tokenizer
    model= model,
    config= onnx_config,                  # Hugging Face 模型对象
    output= onnx_path,              # 输出路径
    opset=15,
    legacy=False 
)
