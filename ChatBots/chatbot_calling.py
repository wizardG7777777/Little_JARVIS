from pathlib import Path
from ChatBots.LocalChatBot import LocalChatBot, load_prompt
def call_local(user_query: str, enable_thinking:bool=False) -> tuple:
    model_path = Path(__file__).parent.parent / "models" / "llm" / "Qwen3-1.7B"
    local_llm = LocalChatBot(model_path=str(model_path))
    
    # 获取系统提示
    system_prompt = load_prompt("daily_chat")
    
    # 创建标准消息格式
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_query}
    ]
    
    # 创建配置 - 使用字典而不是 RunnableConfig
    model_config_dict = {"thinking": enable_thinking}
    
    # 直接调用 invoke 方法，传递标准消息格式和字典配置
    result = local_llm.invoke(
        {"messages": messages},  # 使用标准消息格式
        config=model_config_dict
    )
    
    chat_response = result["content"]
    thinking_process = result["thinking"]
    return thinking_process, chat_response
if __name__ == "__main__":
    llm_thinking, llm_response = call_local(user_query="I am currently arrived in HangZhou, can you tell me something about this city?", enable_thinking=True)
    print(f"Thinking process: {llm_thinking}")
    print(f"Chat response: {llm_response}")