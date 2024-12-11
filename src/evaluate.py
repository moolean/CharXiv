import argparse, json
from openai import OpenAI
from tqdm import tqdm
import os
from openai import AzureOpenAI
import httpx
def random_get_proxy(file, idx):
    fr = open(file, 'r', encoding='utf-8')
    data = json.load(fr)
    proxys = []
    for key, value in data.items():
        proxys += value
    fr.close()
    # print(len(proxys), idx%len(proxys))
    return proxys[idx%len(proxys)]
def test_net():
    '''net test part; gpt do not need this'''
    import httpx

    http_c = httpx.Client()
    current_proxies = http_c.get('http://httpbin.org/ip')
    print(current_proxies.json())
    response = http_c.get('https://ipinfo.io')
    ip_region = response.json()
    print(ip_region)
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_name', type=str, required=True)
    parser.add_argument('--split', type=str, required=True)
    parser.add_argument('--mode', type=str, required=True)
    parser.add_argument('--gen_prefix', type=str, default='gen-')
    parser.add_argument('--api_key', type=str, required=True)
    args = parser.parse_args()
    test_net()
    api_idx = 225 #43 #我们为每个账户规定了一个唯一的编号，如果没有获取到编号，及时联系负责人获取
    proxy_file = '/mnt/afs/user/yaotiankuo/1API1/socks_241107_ids_5_r280.json'

    proxy_url = random_get_proxy(proxy_file, api_idx)
    # proxy_url = 'socks5://10.140.90.11:10200'
    print(proxy_url)
    proxies = {
    "http://": f"{proxy_url}",
    "https://": f"{proxy_url}",
    }
    http_c = httpx.Client(proxies=proxies)
    client = AzureOpenAI(
                    api_key = args.api_key,  
                    api_version = "2024-08-01-preview",
                    azure_endpoint ="https://duomotai.openai.azure.com/",
                    http_client=http_c
                    )
    args.input_file = f"data/{args.mode}_{args.split}.json"
    args.resp_file = f"results/{args.gen_prefix}{args.model_name}-{args.mode}_{args.split}.json"
    args.output_file = args.resp_file.replace(args.gen_prefix, "scores-")
    print(f"Output file: {args.output_file}")

    data, response = json.load(open(args.input_file)), json.load(open(args.resp_file))
    mode = 'descriptive' if 'descriptive' in args.resp_file.split('-')[-1] else 'reasoning'

    if mode == 'descriptive':
        from descriptive_utils import preprocess_descriptive_grading_queries, build_descriptive_grading_queries, \
                postprocess_descriptive_grading_queries, get_descriptive_result_gpt
        # group the responses based on the template id instead of figure id
        groups = preprocess_descriptive_grading_queries(data, response)
        # batched evaluation based on number of questions per query (nq_per_query)
        queries = build_descriptive_grading_queries(groups)
        combined_queries = []
        for query in tqdm(queries):
            result = get_descriptive_result_gpt(client, query['grading_query'], len(query['resp_keys']))
            # query contains resp_keys, grading_query, extract_answer and score
            combined_queries.append({**query, **result})
        queries = combined_queries
        # flatten the queries and only keep the necessary fields
        queries = postprocess_descriptive_grading_queries(queries)
    
    elif mode == 'reasoning':
        from reasoning_utils import build_reasoning_grading_queries, get_reasoning_result_gpt
        # dict of figure_id -> {figure_id, grading_query}
        queries = build_reasoning_grading_queries(data, response) 
        for figure_id, query in tqdm(queries.items()):
            ext, scr = get_reasoning_result_gpt(client, query['grading_query'])
            queries[figure_id]['extracted_answer'] = ext
            queries[figure_id]['score'] = scr
            queries[figure_id].pop('grading_query')
    else: raise ValueError("Mode not supported")

    # output the scores
    with open(args.output_file, "w") as f:
        json.dump(queries, f, indent=4)
