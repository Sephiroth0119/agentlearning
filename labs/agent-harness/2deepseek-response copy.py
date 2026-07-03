import json
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)

# Round 1
request_body = {
    "model": "deepseek-v4-pro",
    "messages": [
        {"role": "user", "content": "What's the highest mountain in the world?"}
    ],
}

print("=== r1 我发送给模型的内容 ===")
print(json.dumps(request_body, ensure_ascii=False, indent=2))

response = client.chat.completions.create(**request_body)

print("\n=== r1 模型返回的内容 ===")
print(response.choices[0].message.content)

assistant_message = response.choices[0].message

request_body["messages"].append({
    "role": "assistant",
    "content": assistant_message.content,
})
print(f"Messages Round 1: {request_body['messages']}")

# Round 2
request_body["messages"].append({"role": "user", "content": "What is the second?"})

print("\n=== r2 我发送给模型的内容 ===")
print(json.dumps(request_body, ensure_ascii=False, indent=2))

response = client.chat.completions.create(**request_body)

print("\n=== r2 模型返回的内容 ===")
print(response.choices[0].message.content)
