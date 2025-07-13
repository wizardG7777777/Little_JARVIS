from typing import Any, Dict
import time
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from langchain_core.runnables import Runnable, RunnableConfig

class QwenRunnable(Runnable):
    """
    Runnable wrapper for local Qwen3-1.7B inference with optional Chain-of-Thought.
    """
    def __init__(self,
                 model_name: str = "./Qwen3-1.7B",
                 load_8bit: bool = True,
                 llm_int8_threshold: float = 5.0,
                 max_new_tokens: int = 500):
        super().__init__(config=RunnableConfig())
        # Load tokenizer and model once
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        quant_config = BitsAndBytesConfig(
            load_in_8bit=load_8bit,
            llm_int8_threshold=llm_int8_threshold
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            quantization_config=quant_config,
            device_map="auto",
            trust_remote_code=True
        )
        self.max_new_tokens = max_new_tokens

    def invoke(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        inputs:
          - prompt: str (user input)
          - thinking: bool (whether to retain CoT tokens, default False)
        returns:
          - thinking: str
          - content: str
        """
        prompt_text: str = inputs.get("prompt", "")
        thinking_flag: bool = inputs.get("thinking", False)

        # Build chat template
        messages = [{"role": "user", "content": prompt_text}]
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=thinking_flag
        )
        # Encode inputs
        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)

        # Generate
        start = time.perf_counter()
        outputs = self.model.generate(
            **model_inputs,
            max_new_tokens=self.max_new_tokens,
            use_cache=True
        )
        gen_ids = outputs[0][len(model_inputs.input_ids[0]):].tolist()
        elapsed_ms = (time.perf_counter() - start) * 1000
        print(f"Qwen inference time: {elapsed_ms:.1f} ms")

        # Split thinking and content
        thinking_content, content = "", ""
        if thinking_flag:
            try:
                # 151668 token id corresponds to </think>
                idx = len(gen_ids) - gen_ids[::-1].index(151668)
            except ValueError:
                idx = 0
            thinking_content = self.tokenizer.decode(gen_ids[:idx], skip_special_tokens=True).strip("\n")
            content = self.tokenizer.decode(gen_ids[idx:], skip_special_tokens=True).strip("\n")
        else:
            content = self.tokenizer.decode(gen_ids, skip_special_tokens=True).strip("\n")

        return {"thinking": thinking_content, "content": content}

    async def astream(self, inputs: Dict[str, Any]):
        # Optionally implement streaming if needed
        raise NotImplementedError("Streaming not implemented for QwenRunnable")
