# Project Framework
## 语音助手模型
* 音频=>文字：Whisper
* 文字推理：Qwen30B-A3B
* 文字=>语音：
## 核心框架
### 大语言模型推理
* PyTorch only
* VLLM + PyTorch
* Llama.cpp + llama-cpp-python
### 语音转文字模块
* 目的：识别用户输入的语音指令
* 实现方案：Whisper
* 模块输入：用户语音，Python:list，其中一级元素为音频数据
    * arr\[0\]: 音频数据，numpy.ndarray
    * arr\[1\]: 采样率，int
* 模块输出：转录结果，Python:str
### RAG 专业知识模块
* 目的：降低大模型回答的幻觉，提升准确度
### 互联网搜索模块
* 目的：突破本地模型知识限制，获取互联网上的最新消息
### 上下文管理模块
* 目的：使得大模型能根据对话背景作出符合人类直觉的回答
### MCP调用模块
* 目的：使得大模型能够根据用户指令调用外部功能
## 具体实现