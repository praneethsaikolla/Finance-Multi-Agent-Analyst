import requests
import os

key = "7a46e861aefb09a313086db4b7caaf31"
url = "https://api.bytez.com/models/v2/openai/v1/chat/completions"

models = [
    "meta-llama/Meta-Llama-3-8B-Instruct",
    "meta-llama/Meta-Llama-3.1-8B-Instruct",
    "meta-llama/Llama-2-7b-chat-hf",
    "meta-llama/Llama-3-8b-chat-hf",
    "Qwen/Qwen2.5-7B-Instruct",
    "Qwen/Qwen1.5-7B-Chat",
    "Qwen/Qwen3-4B",
    "mistralai/Mistral-7B-Instruct-v0.2",
    "mistralai/Mistral-7B-Instruct-v0.3",
    "google/gemma-7b-it",
    "gpt-4o",
    "gpt-3.5-turbo"
]

for model in models:
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "hi"}]
    }
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            print(f"SUCCESS: {model}")
            break
        else:
            print(f"Failed {model}: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error {model}: {e}")
