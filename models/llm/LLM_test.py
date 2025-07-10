from llama_cpp import Llama
import langchain
import subprocess
import shutil
# Warning: This program can not output expected result
def test_llama_cpp_functional():

    binary = shutil.which("llama-cli") or shutil.which("llama")
    if not binary:
        print("Neither 'llama-cli' nor 'llama' found in PATH.")
        return False
    else:
        try:
            res = subprocess.run([binary, "--version"],
                                 capture_output=True, text=True, check=True)
            print(res.stdout.strip())
        except subprocess.CalledProcessError as e:
            print(f"Found binary at {binary}, but failed to run it:", e)
            return False
    return True
def llm_analysation(llm_model:str, back_ground:str="", user_query:str=""):
    SamplePrompt = """# 角色 \n 你是一个智能车载语音助手，你应当尽力回答用户的问题: ## 用户的问题 \n"""
    llm = Llama(
        llm_model,
        n_gpu_layers=-1, # For GPU acceleration
        n_ctx=4096 # Define context length
    )
    # print(llm.metadata)
    user_query = SamplePrompt + "\n" + user_query
    user_query.strip()
    out_put = llm(
        user_query,
        max_tokens=2048,
        echo=False,
        temperature=0.7,
        top_p=0.95,
        stop=["<|im_end|>"],
        repeat_penalty=1.3
    )
    return out_put

def handle_stream_response(generator) -> str:
    full_response = ""
    for chunk in generator:
        delta = chunk["choices"][0]["text"]  # 获取增量文本
        print(delta, end='', flush=True)  # 实时打印
        full_response += delta
    return full_response

if __name__ == "__main__":
   if test_llama_cpp_functional():
       print("llama_cpp is functional")

   else:
       print("llama_cpp is not functional")
result = llm_analysation(llm_model="./qwen3-1.7b-q8.gguf", user_query="你好，请介绍你自己")
# print(type(result))
print(result["choices"][0]["text"])