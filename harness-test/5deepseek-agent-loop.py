import json
import os
from openai import OpenAI


def print_json(title, value):
    print(f"\n=== {title} ===")
    print(json.dumps(value, ensure_ascii=False, indent=2))


def get_weather(location):
    return f"{location}: 24°C, light rain"


def run_tool(tool_call):
    name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)

    print_json("模型想调用的工具", {
        "id": tool_call.id,
        "name": name,
        "arguments": arguments,
    })

    if name == "get_weather":
        return get_weather(**arguments)

    return f"Unknown tool: {name}"


def call_model(messages):
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


def run_agent(user_input, max_rounds=5):
    messages = [{"role": "user", "content": user_input}]

    for round_index in range(max_rounds):
        print(f"\n\n######## Round {round_index + 1} ########")
        message = call_model(messages)
        messages.append(message.model_dump())

        if not message.tool_calls:
            print("\n=== 最终给用户看的回答 ===")
            print(message.content)
            return message.content

        for tool_call in message.tool_calls:
            tool_result = run_tool(tool_call)
            tool_result_message = {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": tool_result,
            }
            print_json("工具执行结果 message", tool_result_message)
            messages.append(tool_result_message)

    raise RuntimeError("Agent loop reached max_rounds without final answer")


client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather of a location.",
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

run_agent("How's the weather in Hangzhou, Zhejiang?")
