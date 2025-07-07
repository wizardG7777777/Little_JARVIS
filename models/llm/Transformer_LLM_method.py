import time
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig




def phi_test():
    ms_phi = "./Phi-4-mini-instruct"
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

    config_q8 = BitsAndBytesConfig(
        load_in_8bit=True
    )
    config_q4 = BitsAndBytesConfig(
        load_in_4bit=True
    )
    model = AutoModelForCausalLM.from_pretrained(
        ms_phi,
        device_map="cuda",
        torch_dtype="auto",
        trust_remote_code=True
    )

    tokenizer = AutoTokenizer.from_pretrained(ms_phi)

    messages = [
        {"role": "system", "content": "You are a helpful AI assistant."},
        {"role": "user", "content": "Please introduce your self."},
    ]

    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
    )
    """
    There is 2 type of setting for phi series model, 
    1. If you want a relatively deterministic output, set do_sample=False and remove the tempture parameter. 
    2. If you prefer a more random, human-like output, set do_sample=True and specify a reasonably appropriate tempture parameter.
    """
    stable_generation_args = {
        "max_new_tokens": 500,
        "return_full_text": False,
        "do_sample": False,
    }
    unstable_generation_args = {
        "max_new_tokens": 500,
        "return_full_text": False,
        "temperature": 0.6,
        "do_sample": True,
    }
    start_time_stamp = time.perf_counter()
    output = pipe(messages, **unstable_generation_args)
    end_time_stamp = time.perf_counter()
    print(f"Time cost: {(end_time_stamp - start_time_stamp)*1000} ms")
    # print(output[0]['generated_text'])
    return output[0]['generated_text']


def qwen_test(thinking:bool=True) -> dict:
    model_name = "./Qwen3-0.6B"
    # load the tokenizer and the model
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    config_q8 = BitsAndBytesConfig(
        load_in_8bit=True,
        llm_int8_threshold=5.0
    )
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype="auto",
        quantization_config=config_q8,
        device_map="auto"
    )

    # prepare the model input
    prompt = "Give me a short introduction to large language model."
    messages = [
        {"role": "user", "content": prompt}
    ]
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=True  # Switches between thinking and non-thinking modes. Default is True.
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

    # conduct text completion
    start_time = time.perf_counter()
    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=500,
        use_cache=True
    )
    output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist()
    end_time = time.perf_counter()
    print(f"Time cost: {(end_time - start_time)*1000} ms")

    # parsing thinking content
    try:
        # rindex finding 151668 (</think>)
        index = len(output_ids) - output_ids[::-1].index(151668)
    except ValueError:
        index = 0
    if thinking:
        thinking_content = tokenizer.decode(output_ids[:index], skip_special_tokens=True).strip("\n")
    else:
        thinking_content = ""
    content = tokenizer.decode(output_ids[index:], skip_special_tokens=True).strip("\n")

    # print("thinking content:", thinking_content)
    # print("content:", content)
    result = {"thinking": thinking_content, "content": content}
    return result

if __name__ == "__main__":
    # test_output = qwen_test(thinking=False)
    test_output = phi_test()
    print(test_output)