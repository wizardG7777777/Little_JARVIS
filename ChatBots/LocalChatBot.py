"""
Here is a unified interface for all the chatbot models with the following framework:
A. transormers only
B. llama_cpp + transformers
C. TensorRT + transformers
"""
import os
import torch
from abc import ABC
from typing import Dict, Any, Optional, List, Union
from langchain_core.prompt_values import ChatPromptValue
from pathlib import Path
from langchain.schema.runnable import Runnable
from transformers import AutoTokenizer, AutoModelForCausalLM

def load_prompt(user_intent: str) -> str:
    # Find the project root directory
    def find_project_root(current_path, project_names=None):
        if project_names is None:
            project_names = ["Little_JARVIS", "your_actual_project_name"]
            
        current = Path(current_path)
        # 先检查当前目录是否包含特定文件/目录，这是更可靠的方法
        if (current / "ExtendMaterial" / "Prompts").exists():
            return current
            
        # 然后检查目录名
        if current.name in project_names:
            return current
            
        # 向上递归
        parent = current.parent
        if parent == current:  # Reached root without finding project
            # 如果到达根目录仍未找到，返回当前文件的父目录作为后备方案
            return Path(__file__).resolve().parent.parent
        return find_project_root(parent, project_names)

    try:
        # Get current file's directory and find project root
        current_file = Path(__file__).resolve()
        current_dir = current_file.parent
        project_root = find_project_root(current_dir)
        
        if project_root is None:
            print("Warning: Could not find project root directory")
            # 使用默认提示作为后备方案
            return "You are a helpful AI assistant"
            
        # 打印调试信息
        print(f"Project root: {project_root}")
        
        # Define paths relative to project root
        prompts_dir = project_root / "ExtendMaterial" / "Prompts"
        print(f"Prompts directory: {prompts_dir}")
        print(f"Prompts directory exists: {prompts_dir.exists()}")
        
        # 检查目录内容
        if prompts_dir.exists():
            print(f"Directory contents: {[f.name for f in prompts_dir.iterdir()]}")

        intent_types = {
            "device_control": "",
            "info_query": "",
            "daily_chat": prompts_dir / "DailyChat.md",
            # ...其他意图类型...
        }

        prompt_path = intent_types.get(user_intent, prompts_dir / "DailyChat.md")
        print(f"Selected prompt path: {prompt_path}")
        print(f"File exists: {prompt_path.is_file() if isinstance(prompt_path, Path) else False}")

        # Check if the value is a file path or a direct string
        if isinstance(prompt_path, Path) and prompt_path.is_file():
            try:
                prompt = prompt_path.read_text(encoding="utf-8")
                print(f"Successfully read prompt file: {len(prompt)} characters")
            except UnicodeDecodeError:
                # 尝试不同的编码
                prompt = prompt_path.read_text(encoding="latin-1")
                print("Used latin-1 encoding as fallback")
        else:
            prompt = str(prompt_path)  # Use the string directly
            print("Using path as string directly")
            
        return prompt
        
    except FileNotFoundError as e:
        print(f"Warning: File not found: {str(e)}")
        print("In this scenario, system will use the default prompt.")
        return "You are a helpful AI assistant"
    except PermissionError as e:
        print(f"Warning: Permission error: {str(e)}")
        print("In this scenario, system will use the default prompt.")
        return "You are a helpful AI assistant"
    except Exception as e:
        print(f"Warning: Unexpected error: {type(e).__name__}: {str(e)}")
        print("In this scenario, system will use the default prompt.")
        return "You are a helpful AI assistant"


class LocalChatBot(Runnable):
    def __init__(self, model_path:str):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model path not found: {model_path}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.thinking = False
        self.device = "cuda" # Not support mps or cpu on prototype, gonna to support this in next version
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype="auto",
            device_map=self.device
        )
    def _process_input(self, input_data: Union[str, Dict, List], enable_thinking:bool=False):
        # Standard format of input process, make this function can handle multiple format of input
        # Support ChatPromptValue for now
        try:

            if isinstance(input_data, ChatPromptValue):
                messages = input_data.to_messages()
            elif isinstance(input_data, str):
                messages = [{"role": "user", "content": input_data}]
            elif isinstance(input_data, dict):
                if "messages" in input_data:
                    messages = input_data["messages"]
                else:
                    messages = [{"role": "user", "content": str(input_data)}]
            elif isinstance(input_data, list):
                messages = input_data
            else:
                try:
                    messages = [{"role": "user", "content": str(input_data)}]
                except:
                    raise ValueError(f"Unsupported input type: {type(input_data)}")
        except ImportError:
            # Keep the original Python type support
            if isinstance(input_data, str):
                messages = [{"role": "user", "content": input_data}]
            elif isinstance(input_data, dict):
                if "messages" in input_data:
                    messages = input_data["messages"]
                else:
                    messages = [{"role": "user", "content": str(input_data)}]
            elif isinstance(input_data, list):
                messages = input_data
            else:
                raise ValueError(f"Unsupported input type: {type(input_data)}")

        # Now it is time to convert the user input into query
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=enable_thinking
        )
        return text
    def _parse_output(self, output_ids, input_length):
        """Parse model output to extract thinking and content."""
        # Get only the newly generated tokens
        new_tokens = output_ids[0][input_length:].tolist()

        # Parse thinking content if enabled
        try:
            # Look for </think> token, cause think chain will be covered with <think> in qwen series model
            index = len(new_tokens) - new_tokens[::-1].index(151668)
        except ValueError:
            index = 0

        if self.thinking:
            thinking = self.tokenizer.decode(new_tokens[:index], skip_special_tokens=True).strip("\n")
        else:
            thinking = ""

        content = self.tokenizer.decode(new_tokens[index:], skip_special_tokens=True).strip("\n")

        return thinking, content
    def invoke(
        self,
        data_input: Any,  # noqa: A002
        config: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        config = config or {} # Make this function work even there is no augment passed from calling
        thinking = config.get("thinking", False)
        max_tokens = config.get("max_tokens", 512) # Ofcourse we don't need too much tokens for output
        uquery = self._process_input(data_input, thinking)
        model_inputs = self.tokenizer([uquery], return_tensors="pt").to(self.model.device)
        with torch.no_grad():
            generated_ids = self.model.generate(
                **model_inputs,
                max_new_tokens=max_tokens,
                use_cache=True
            )
        output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist()
        try:
            index = len(output_ids) - output_ids[::-1].index(151668) # 151668 is the token id for </think>
        except ValueError: # If thinking module is not enabled, use this to handle the error
            index = 0
        thinking_content = self.tokenizer.decode(output_ids[:index], skip_special_tokens=True).strip("\n")
        content = self.tokenizer.decode(output_ids[index:], skip_special_tokens=True).strip("\n")
        result = {"thinking": thinking_content, "content": content}
        return result

    def batch(self, inputs: List[Any], config: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Process multiple inputs in batch mode for improved efficiency.

        Args:
            inputs: List of input data (strings, dicts, or lists)
            config: Optional configuration dictionary with batch-specific settings

        Returns:
            List of dictionaries containing thinking and content for each input
        """
        if not inputs:
            return []

        # Validate inputs is a list
        if not isinstance(inputs, list):
            raise ValueError("Inputs must be a list")

        config = config or {}
        thinking = config.get("thinking", False)
        max_tokens = config.get("max_tokens", 512)
        batch_size = config.get("batch_size", len(inputs))  # Process all at once by default

        # Ensure batch_size is reasonable
        batch_size = max(1, min(batch_size, len(inputs)))

        results = []

        # Process inputs in batches to manage memory usage
        for i in range(0, len(inputs), batch_size):
            batch_inputs = inputs[i:i + batch_size]
            batch_results = []

            try:
                # Process each input in the current batch using list comprehension
                processed_texts = [
                    self._process_input(input_data, thinking)
                    for input_data in batch_inputs
                ]

                # Tokenize all inputs in the batch
                model_inputs = self.tokenizer(
                    processed_texts,
                    return_tensors="pt",
                    padding=True,
                    truncation=True,
                    max_length=2048  # Add explicit max_length to prevent warnings
                ).to(self.model.device)

                # Ensure pad_token_id is set properly
                if self.tokenizer.pad_token_id is None:
                    self.tokenizer.pad_token_id = self.tokenizer.eos_token_id

                # Generate responses for the entire batch
                with torch.no_grad():
                    generated_ids = self.model.generate(
                        input_ids=model_inputs.input_ids,
                        attention_mask=model_inputs.attention_mask,
                        max_new_tokens=max_tokens,
                        use_cache=True,
                        pad_token_id=self.tokenizer.pad_token_id,
                        do_sample=False,  # Use greedy decoding for consistency
                        eos_token_id=self.tokenizer.eos_token_id
                    )

                # Process outputs for each item in the batch
                for j, input_data in enumerate(batch_inputs):
                    try:
                        # Get the actual input length for this specific sequence (excluding padding)
                        attention_mask = model_inputs.attention_mask[j]
                        input_length = attention_mask.sum().item()  # Count non-padded tokens
                        output_ids = generated_ids[j]

                        # Extract only the newly generated tokens
                        new_tokens = output_ids[input_length:].tolist()

                        # Parse thinking content if enabled
                        thinking_index = 0
                        try:
                            # Look for </think> token (151668 for Qwen models)
                            thinking_index = len(new_tokens) - new_tokens[::-1].index(151668)
                        except ValueError:
                            thinking_index = 0

                        if thinking:
                            thinking_content = self.tokenizer.decode(
                                new_tokens[:thinking_index], skip_special_tokens=True
                            ).strip()
                        else:
                            thinking_content = ""

                        content = self.tokenizer.decode(
                            new_tokens[thinking_index:], skip_special_tokens=True
                        ).strip()

                        batch_results.append({
                            "thinking": thinking_content,
                            "content": content
                        })

                    except Exception as e:
                        # Handle individual item processing errors
                        batch_results.append({
                            "thinking": "",
                            "content": f"Item processing error: {str(e)}"
                        })

            except Exception as e:
                # Handle batch-level errors gracefully - create error responses for the batch
                error_message = f"Batch processing error: {str(e)}"
                batch_results = [
                    {
                        "thinking": "",
                        "content": error_message
                    }
                    for _ in batch_inputs
                ]

            results.extend(batch_results)

        return results

    def stream(
        self,
        data_input: Any,  # noqa: A002
        config: Optional[Dict[str, Any]] = None,
        **kwargs: Optional[Any],
    ) -> Any:
        result = self.invoke(data_input, config, **kwargs)
        if result["thinking"]:
            yield {"thinking": result["thinking"], "content": ""}
        yield {"thinking": "", "content": result["content"]}
