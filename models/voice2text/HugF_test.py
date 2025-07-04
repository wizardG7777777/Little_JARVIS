import os
import glob
import torch
import soundfile as sf
from transformers import WhisperProcessor, WhisperForConditionalGeneration


test_path = "../../TestMaterial/human_speech/output/"
def __folder_path_extract(input_path:str)->list:
    if os.path.isdir(input_path) and os.path.exists(input_path):
        file_path_array = glob.glob(os.path.join(input_path, "*.wav"))
        return file_path_array
    else:
        print("Invalid input path")
        return [] # return empty list if input is not a valid directory, and make sure the function will not break the program

device = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")

audio_array = [sf.read(audio) for audio in __folder_path_extract(test_path)]
print(type(audio_array))
print(type(audio_array[0]))
print(type(audio_array[0][0]))
print(type(audio_array[0][1]))