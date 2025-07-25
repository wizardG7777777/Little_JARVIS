"""
This method is used for convert multiple types of model into PyTorch supported format.
1. Transformer (from hugging face) into pt
2. onnx into pt
3. tf into pt. Well, unsupported for now.
"""
import os
from pathlib import Path
import torch


def get_device() -> str:
    # Use cuda priority, then mps
    if torch.cuda.is_available():
        print("cuda is detected.")
        return "cuda"
    elif torch.backends.mps.is_available():
        print("MPS accelerator is detected")
        return "mps"
    else:
        print("No acceleration is detected, but program can use CPU at least")
        return "cpu"
def path_available(path: str) -> bool:
    return Path(path).exists()


class ModelConverter:
    def __init__(self):
        self.device = get_device()
        self.supported_type = ["transformers", "onnx", "pytorch", "huggingface", "tensorflow"]
    def __is_pytorch(self, model_path: str) -> bool:
        if not path_available(model_path):
            print("❌ model path not found: {model_path}")
            return False


        return True

    def __is_transformers(self, model_path: str):
        if not path_available(model_path):
            print("❌ model path not found: {model_path}")
            return False
        # 检测模型文件是否是一个文件夹，因为transformers类的模型文件是以文件夹的格式存在的
        if not os.path.isdir(model_path):
            print(f"❌ model path is not a directory, please check your download carefully. An original model which is downloaded from Huggingface should be a directory: {model_path}")
            if Path(model_path).suffix == ".gguf":
                print("⚠️ .gguf is not supported by this method, please download the original model file from Huggingface.")
            return False
        mode_dir = Path(model_path)
        if not (mode_dir / "config.json").exists():
            print(f"❌ config.json not found in model directory, please check your download carefully. An original model which is downloaded from Huggingface should contain config.json: {model_path}")
            return False
        for file in mode_dir.iterdir():
            if file.suffix == ".bin":
                print("The bin file is founded")
                return True
            elif file.suffix == ".safetensors":
                print("The safetensors file is founded")
                return True
        return False
    def __is_onnx(self, model_path: str):
        if not path_available(model_path):
            print("❌ model path not found: {model_path}")
            return False

        return True
    def __is_tensorflow(self, model_path: str) -> bool:
        print("Tensorflow file is not supported yet.")
        return False
    def _convert_transformers(self, model_dir:str):
        pass

    def model_convert(self, model_path:str, original_type:str):
        if original_type.lower() not in self.supported_type:
            print(f"Model type: {model_path} is not supported by this version now")
        elif (original_type == "transformers" or original_type=="huggingface") and self.__is_transformers(model_path):
            print("Converting model from transformer into PyTorch now")
        elif original_type == "onnx" and self.__is_onnx(model_path):
            print("Converting model from onnx into PyTorch now")
        elif original_type == "pytorch" and self.__is_pytorch(model_path):
            print("No need to convert, model is ready for pruning and quantization.")
        elif original_type == "tensorflow" and self.__is_tensorflow(model_path):
            print("Converting model from tensorflow into PyTorch now")
        else:
            print(f"Maybe your model file is not {original_type}, please check your input.")
