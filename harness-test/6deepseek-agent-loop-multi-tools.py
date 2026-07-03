import ast
import json
import operator
import os
from openai import OpenAI


def get_weather(location):
    return f"{location}: 24 C, light rain"


def calculate(expression):
    operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.USub: operator.neg,
    }

    def eval_node(node):
        if isinstance(node, ast.Expression):
            return eval_node(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in operators:
            return operators[type(node.op)](eval_node(node.left), eval_node(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in operators:
            return operators[type(node.op)](eval_node(node.operand))
        raise ValueError(f"Unsupported expression: {expression}")

    tree = ast.parse(expression, mode="eval")
    return str(eval_node(tree))


def call_model(messages):
    response = client.chat.completions.create(
        model="deepseek-v4-pro",
        messages=messages,
        tools=tools,
    )
    return response.choices[0].message


def run_tool(tool_call):
    name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)

    print(f"Model wants tool: {name}")
    print(f"Arguments: {json.dumps(arguments, ensure_ascii=False)}")

    if name == "get_weather":
        result = get_weather(**arguments)
    elif name == "calculate":
        result = calculate(**arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")

    print(f"Tool result: {result}")
    return result


def run_agent(user_input):
    messages = [
        {
            "role": "system",
            "content": (
                "You are a tool-using agent. You must use tools to complete the task. "
                "Use get_weather for weather, calculate for math, and finish when you "
                "have enough information to answer the user. Do not answer directly in "
                "plain assistant content; call finish with the final answer."
            ),
        },
        {"role": "user", "content": user_input},
    ]

    print(f"User: {user_input}")

    round_index = 1
    while True:
        print(f"\n--- Round {round_index} ---")
        round_index += 1

        message = call_model(messages)
        messages.append(message.model_dump())

        if not message.tool_calls:
            raise RuntimeError("Model returned no tool_calls, but this harness expects finish().")

        for tool_call in message.tool_calls:
            name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            if name == "finish":
                final_answer = arguments["final_answer"]
                print("Model wants tool: finish")
                print(f"Final answer: {final_answer}")
                return final_answer

            tool_result = run_tool(tool_call)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": tool_result,
            })


client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get fake weather of a location for this demo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. Hangzhou, Zhejiang",
                    }
                },
                "required": ["location"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Calculate a simple arithmetic expression.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Simple math expression, e.g. 12 * 3 + 4",
                    }
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "finish",
            "description": "Finish the agent loop when the final answer is ready.",
            "parameters": {
                "type": "object",
                "properties": {
                    "final_answer": {
                        "type": "string",
                        "description": "The final answer to show to the user.",
                    }
                },
                "required": ["final_answer"],
            },
        },
    },
]

run_agent("How's the weather in Hangzhou, Zhejiang? Also calculate 12 * 3 + 4.")
