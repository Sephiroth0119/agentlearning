import json
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)

messages = [
    {
        "role": "system",
        "content": """
你负责抽取任务信息。必须输出 json。

格式：
{
  "intent": "用户意图",
  "language": "python 或 java 或 unknown",
  "needs_tool": true
}
""",
    },
    {
        "role": "user",
        "content": "我想用 Python 调 DeepSeek API，并让它返回结构化结果。",
    },
]

request_body = {
    "model": "deepseek-v4-pro",
    "messages": messages,
    "response_format": {"type": "json_object"},
}

print("=== 我发送给模型的内容 ===")
print(json.dumps(request_body, ensure_ascii=False, indent=2))

response = client.chat.completions.create(**request_body)

raw_json = response.choices[0].message.content
print("\n=== 模型返回的原始 JSON 字符串 ===")
print(raw_json)

data = json.loads(raw_json)
print("\n=== Python 解析后再格式化成 JSON ===")
print(json.dumps(data, ensure_ascii=False, indent=2))
