import time
from tqdm import tqdm
from multiprocessing import Pool, Manager

def process_query(args):
    """
    Process a single query using the generate_fn function with retry logic.
    
    Args:
        args (tuple): Contains all arguments needed for processing a single query.

    Returns:
        tuple: (query_key, result)
    """
    k, query_data, generate_fn, model_path, api_key, client, init_sleep, max_retries, sleep_factor = args
    sleep_time = init_sleep
    query = query_data['question']
    image = query_data["figure_path"]
    curr_retries = 0
    result = None

    while curr_retries < max_retries and result is None:
        try:
            result = generate_fn(image, query, model_path, api_key=api_key, client=client, random_baseline=False)
        except Exception as e:
            print(f"Error: {e}")
            print(f"Error {curr_retries}, sleeping for {sleep_time} seconds...")
            time.sleep(sleep_time)
            curr_retries += 1
            sleep_time *= sleep_factor

    if result is None:
        result = "Error in generating response."
        print(f"Error in generating response for {k}")

    return k, result

def generate_response_remote_wrapper(generate_fn, queries, model_path, api_key, client, init_sleep=1, max_retries=10, sleep_factor=1.6, num_workers=16):
    """
    Wrapper function to handle multiple queries using multiprocessing.

    Args:
        generate_fn (callable): The function to generate a response for a query.
        queries (dict): Dictionary of queries where each key maps to query data.
        model_path (str): Path to the model to be used.
        api_key (str): API key for authentication.
        client (str): Client identifier.
        init_sleep (float): Initial sleep time between retries.
        max_retries (int): Maximum number of retries for each query.
        sleep_factor (float): Factor by which to multiply sleep time after each retry.
        num_workers (int): Number of parallel workers to use.

    Returns:
        None: Updates the `queries` dictionary with responses.
    """
    manager = Manager()
    queries_shared = manager.dict(queries)

    with Pool(processes=num_workers) as pool:
        args = [
            (k, queries_shared[k], generate_fn, model_path, api_key, client, init_sleep, max_retries, sleep_factor)
            for k in queries
        ]

        for k, result in tqdm(pool.imap_unordered(process_query, args), total=len(queries)):
            queries[k]['response'] = result

def get_client_fn(model_path):
    if model_path in ['claude-3-sonnet-20240229', 
                      'claude-3-opus-20240229', 
                      'claude-3-haiku-20240307', 
                      'claude-3-5-sonnet-20240620']:
        from .claude import get_client_model
    # gemini
    elif model_path in ['gemini-1.5-pro-001', 
                        'gemini-1.0-pro-vision-001', 
                        'gemini-1.5-flash-001',
                        'gemini-1.5-pro-exp-0801']:
        from .gemini import get_client_model
    # gpt
    elif model_path in ['gpt-4o-2024-05-13', 
                        'gpt-4o-2024-08-06',
                        'chatgpt-4o-latest',
                        'gpt-4-turbo-2024-04-09', 
                        'gpt-4o-mini-2024-07-18']:
        from .gpt import get_client_model
    # reka
    elif model_path in ['reka-core-20240415', 
                        'reka-flash-20240226', 
                        'reka-core-20240415']:
        from .reka import get_client_model
    # qwen
    elif model_path in ['qwen-vl-max', 
                        'qwen-vl-plus']:
        from .qwen import get_client_model
    # internvl2pro
    elif model_path in ['InternVL2-Pro']:
        from .internvl2pro import get_client_model
    elif model_path in ['SenseChat-5-Vision']:
        from .sensechat_vision import get_client_model
    else:
        raise ValueError(f"Model {model_path} not supported")
    return get_client_model

def get_generate_fn(model_path):
    model_name = model_path.split('/')[-1]
    # cambrian
    if model_name in ['cambrian-34b']:
        from .cambrian import generate_response
    # chartgemma
    elif model_name in ['chartgemma']:
        from .chartgemma import generate_response
    # claude
    elif model_name in ['claude-3-sonnet-20240229',
                        'claude-3-opus-20240229',
                        'claude-3-haiku-20240307',
                        'claude-3-5-sonnet-20240620']:
        from .claude import generate_response
    # deepseekvl
    elif model_name in ['deepseek-vl-7b-chat']:
        from .deepseekvl import generate_response
    # gemini
    elif model_name in ['gemini-1.5-pro-001', 
                        'gemini-1.0-pro-vision-001', 
                        'gemini-1.5-flash-001',
                        'gemini-1.5-pro-exp-0801']:
        from .gemini import generate_response
    # gpt
    elif model_name in ['gpt-4o-2024-05-13', 
                        'gpt-4o-2024-08-06',
                        'chatgpt-4o-latest',
                        'gpt-4-turbo-2024-04-09', 
                        'gpt-4o-mini-2024-07-18']:
        from .gpt import generate_response
    # idefics2
    elif model_name in ['idefics2-8b',
                        'idefics2-8b-chatty',
                        'Idefics3-8B-Llama3']:
        from .idefics import generate_response
    # ixc2
    elif model_name in ['internlm-xcomposer2-4khd-7b',
                        'internlm-xcomposer2-vl-7b']:
        from .ixc2 import generate_response
    # internvl2
    elif model_name in ['InternVL2-26B',
                        'InternVL2-Llama3-76B']:
        from .internvl2 import generate_response
    # internvl15
    elif model_name in ['InternVL-Chat-V1-5']:
        from .internvl15 import generate_response
    # llava16
    elif model_name in ['llava-v1.6-34b-hf',
                        'llava-v1.6-mistral-7b-hf']:
        from .llava16 import generate_response
    # mgm
    elif model_name in ['MGM-34B-HD',
                        'MGM-8B-HD']:
        from .mgm import generate_response
    # minicpm
    elif model_name in ['MiniCPM-Llama3-V-2_5',
                        'MiniCPM-V-2',
                        'MiniCPM-V-2_6']:
        from .minicpm import generate_response
    elif model_name in ['glm-4v-9b']:
        from .glm import generate_response
    # moai
    elif model_name in ['MoAI-7B']:
        from .moai import generate_response
    # paligemma
    elif model_name in ['paligemma-3b-mix-448']:
        from .paligemma import generate_response
    # phi3
    elif model_name in ['Phi-3-vision-128k-instruct']:
        from .phi3 import generate_response
    # qwen
    elif model_name in ['qwen-vl-max',
                        'qwen-vl-plus']:
        from .qwen import generate_response
    # reka
    elif model_name in ['reka-core-20240415',
                        'reka-flash-20240226',
                        'reka-core-20240415']:
        from .reka import generate_response
    # sphinx
    elif model_name in ['SPHINX-v2-1k']:
        from .sphinx2 import generate_response
    # vila
    elif model_name in ['VILA1.5-40b']:
        from .vila15 import generate_response
    # ovis
    elif model_name in ['Ovis1.5-Llama3-8B',
                        'Ovis1.5-Gemma2-9B']:
        from .ovis import generate_response
    # internvl2pro
    elif model_name in ['InternVL2-Pro']:
        from .internvl2pro import generate_response
    elif model_name in ['ChartLlama-13b']:
        from .chartllama import generate_response
    elif model_name in ['TinyChart-3B-768']:
        from .tinychart import generate_response
    elif model_name in ['ChartInstruct-LLama2',
                        'ChartInstruct-FlanT5-XL']:
        from .chartinstruct import generate_response
    elif model_name in ['unichart-chartqa-960']:
        from .unichart import generate_response
    elif model_name in ['ChartAssistant']:
        from .chartast import generate_response
    elif model_name in ['DocOwl1.5-Omni',
                        'DocOwl1.5-Chat',]:
        from .docowl15 import generate_response
    elif model_name in ['ureader-v1']:
        from .ureader import generate_response
    elif model_name in ['TextMonkey',
                        'Monkey-Chat',]:
        from .textmonkey import generate_response
    elif model_name in ['cogagent-vqa-hf']:
        from .cogagent import generate_response
    elif model_name in ['SenseChat-5-Vision']:
        from .sensechat_vision import generate_response
    else:
        raise ValueError(f"Model {model_name} not supported")
    return generate_response
