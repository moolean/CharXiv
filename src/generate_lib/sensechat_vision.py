import requests

def get_client_model(model_path, api_key):
    assert api_key is not None, "API key is required for using GPT"
    assert model_path is not None, "Model name is required for using GPT"
    model = model_path
    client = None
    return client, model

def image_to_base64(image_path):
    import base64
    with open(image_path, 'rb') as image_file:
        encoded_string = base64.b64encode(image_file.read())
        return encoded_string.decode('utf-8')
    
def generate_response(image_path, query, model, media_type="image/jpeg", api_key=None, client=None, random_baseline=False):

    url = 'https://api.sensenova.cn/v1/llm/chat-completions'
    
    content = [{
        'image_base64': image_to_base64(image_path),
        'image_file_id': '',
        'image_url': '',
        'text': '',
        'text': '',
        'type': 'image_base64'
    }]

    content.append({
        'image_base64': '',
        'image_file_id': '',
        'image_url': '',
        'text': query,
        'type': 'text'
    })

    message = [{'content': content, 'role': 'user'}]

    data = {
        'messages': message,
        # 'max_new_tokens': max_new_tokens, # 
        'temperature':0,
        "top_k": 0, 
        "top_p": 0.99, 
        'repetition_penalty':1.05,
        'model': model, # "SenseChat-5-Vision"
        'stream': False,
    }
    headers = {
        'Content-type': 'application/json',
        'Authorization': 'Bearer ' + api_key
    }
    response = requests.post(
        url,
        headers=headers,
        json=data,
    )
    try:
        assert response.status_code == 200
        response = response.json()['data']['choices'][0]['message'].strip()
        return response
    except Exception as err:
        return response.json()['error']['message']


