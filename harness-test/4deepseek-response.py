import json
import os
from openai import OpenAI


def print_json(title, value):
    print(f"\n=== {title} ===")
    print(json.dumps(value, ensure_ascii=False, indent=2))


def send_messages(messages):
    request_body = {
        "model": "deepseek-v4-pro",
        "messages": messages,
        "tools": tools,
    }
    print_json("发送给模型的 request_body", request_body)

    response = client.chat.completions.create(**request_body)
    message = response.choices[0].message
    print_json("模型返回的 assistant message", message.model_dump())
    return message


client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather of a location, the user should supply a location first.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    }
                },
                "required": ["location"],
            },
        },
    },
]

messages = [{"role": "user", "content": "How's the weather in Hangzhou, Zhejiang?"}]

# 第一次调用：模型不会真的查天气，它只会决定要不要调用工具。
message = send_messages(messages)

tool = message.tool_calls[0]
assistant_message = message.model_dump()
messages.append(assistant_message)

tool_arguments = json.loads(tool.function.arguments)
print_json("模型想调用的工具参数", tool_arguments)

# 这里是假装我们自己的 get_weather 工具查到了结果。
tool_result_message = {
    "role": "tool",
    "tool_call_id": tool.id,
    "content": "24°C",
}
messages.append(tool_result_message)
print_json("工具执行结果 message", tool_result_message)

# 第二次调用：把工具结果发回模型，让模型组织成自然语言。
message = send_messages(messages)

print("\n=== 最终给用户看的回答 ===")
print(message.content)
