# 通过 Python 重新下载模型，如果任意模型不可用，则将Qwen3-Embedding-0.6B切换为指定的模型就好了
from huggingface_hub import snapshot_download
snapshot_download(repo_id="Qwen/Qwen3-Embedding-0.6B", local_dir="./Qwen3-Embedding-0.6B")