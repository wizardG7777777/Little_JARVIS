import os
import logging
from llama_cpp import Llama
from langchain.llms.base import LLM
from typing import Any, List, Mapping, Optional

def load_prompt(file_path: str) -> str:
    """
    Load a prompt from a file path.

    Args:
        file_path: String path to the prompt file

    Returns:
        The prompt content as a string or empty string if errors occur
    """
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        return ""

    file = None
    try:
        # Open the file
        file = open(file_path, 'r', encoding='utf-8')

        # Read the file content
        content = file.read()

        return content
    except Exception as e:
        print(f"Error reading file '{file_path}': {str(e)}")
        return ""
    finally:
        # Ensure file is closed in the final stage
        if file is not None:
            file.close()


# 自定义LLM类，适配langchain
class LlamaCppLLM(LLM):
    def __init__(self, model_file_path:str, context_length:int=4096, gpu_layers:int=-1,**kwargs):
        super().__init__(**kwargs)
        self.model = Llama(
            model_file_path,
            n_gpu_layers=-1,
            n_ctx=4096
        )
    @property
    def _llm_type(self) -> str:
        return self.model.metadata
    def _call(
            self,
            user_query:str,
            max_token:int,
            echo:bool=False,
            temperature:float=0.7,
            top_p:float=0.95,
            stop:list[str]=["\n","###"],
            prompt_file_path:str="./sample.txt"
    ) -> str:
        user_prompt = load_prompt(prompt_file_path) + user_query

        response = self.model(
        user_prompt,
        max_tokens=4096,
        echo=False,
        temperature=0.7,
        top_p=0.95,
        stop=["\n","###"],
        repeat_penalty=1.2
    )
        return response["choices"][0]["text"]

    def get_num_tokens(self, text: str) -> int:
        """
        Calculate the number of tokens in the given text.

        Args:
            text: The input text to tokenize

        Returns:
            Number of tokens in the text
        """
        try:
            # Some llama-cpp-python versions might need encoding, some might not
            # Try both approaches
            try:
                tokens = self.model.tokenize(text.encode("utf-8"))
            except (AttributeError, TypeError):
                # If encoding causes issues, try without encoding
                tokens = self.model.tokenize(text)

            return len(tokens)
        except Exception as e:
            logging.warning(f"Token counting failed: {e}")
            # Fallback to a rough estimation (4 chars ≈ 1 token for many models)
            return len(text) // 4

    def get_token_ids(self, text: str) -> list:
        """
        Get the token IDs for the given text.

        Args:
            text: The input text to tokenize

        Returns:
            List of token IDs
        """
        try:
            # Try with encoding first
            try:
                return self.model.tokenize(text.encode("utf-8"))
            except (AttributeError, TypeError):
                # If that fails, try without encoding
                return self.model.tokenize(text)
        except Exception as e:
            logging.warning(f"Tokenization failed: {e}")
            return []  # Return empty list on failure

# class ChatBot:
#     def __init__(self, model_file_path:str):
#         self.model =