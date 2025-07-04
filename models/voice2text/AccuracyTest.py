# Please change the model_file_path to your own model path, base on Unix style
model_file_path="./whisperv3-turbo.onnx"
test_material_folder_base = "../../TestMaterial/human_speech/output"
import os
import soundfile
import onnxruntime as ort
import numpy as np
def audio_load(audio_path):
    audio, sample_rate = soundfile.read(audio_path)
    if sample_rate != 16000:
        return None, sample_rate
    else:
        return audio, sample_rate

whisper_model = ort.InferenceSession(model_file_path)
single_file = os.path.join(test_material_folder_base, "test01_whisper.wav")
audio, _ = audio_load(single_file)

input_name = whisper_model.get_inputs()[0].name
print(type(input_name))


