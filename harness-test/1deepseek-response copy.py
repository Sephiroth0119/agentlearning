import json
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)

request_body = {
    "model": "deepseek-v4-pro",
    "messages": [
        {"role": "system", "content": "你是一个简洁的中文助手。"},
        {"role": "user", "content": "用一句话解释什么是 agent harness。"},
    ],
}

print("=== 我发送给模型的内容 ===")
print(json.dumps(request_body, ensure_ascii=False, indent=2))

response = client.chat.completions.create(**request_body)

print("\n=== 模型返回的内容 ===")
print(response.choices[0].message.content)