import ast
import json
import operator
import os
from pathlib import Path
from openai import OpenAI


def load_skill(path):
    text = Path(path).read_text(encoding="utf-8")

    if not text.startswith("---"):
        return {}, text

    _, frontmatter, body = text.split("---", 2)
    meta = parse_simple_frontmatter(frontmatter)
    return meta, body.strip()


def parse_simple_frontmatter(text):
    meta = {}
    current_list_key = None

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()

        if not stripped:
            continue

        if stripped.startswith("- ") and current_list_key:
            meta[current_list_key].append(stripped[2:])
            continue

        current_list_key = None

        if ":" not in stripped:
            continue

        key, value = stripped.split(":", 1)
        key = key.strip()
        value = value.strip()

        if value:
            meta[key] = value
        else:
            meta[key] = []
            current_list_key = key

    return meta


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


TOOL_REGISTRY = {
    "get_weather": {
        "function": get_weather,
        "schema": {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get fake weather of a location for this demo.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string"},
                    },
                    "required": ["location"],
                },
            },
        },
    },
    "calculate": {
        "function": calculate,
        "schema": {
            "type": "function",
            "function": {
                "name": "calculate",
                "description": "Calculate a simple arithmetic expression.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {"type": "string"},
                    },
                    "required": ["expression"],
                },
            },
        },
    },
    "finish": {
        "function": None,
        "schema": {
            "type": "function",
            "function": {
                "name": "finish",
                "description": "Finish the loop when the final answer is ready.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "final_answer": {"type": "string"},
                    },
                    "required": ["final_answer"],
                },
            },
        },
    },
}


def compile_skill_to_request_parts(skill_path):
    meta, skill_body = load_skill(skill_path)

    tool_names = meta.get("tools", [])
    tools = [TOOL_REGISTRY[name]["schema"] for name in tool_names]

    system_prompt = (
        "You are using the following skill instructions.\n\n"
        f"{skill_body}"
    )

    return {
        "skill_name": meta.get("name", "unknown"),
        "tool_names": tool_names,
        "response_format": meta.get("response_format"),
        "system_prompt": system_prompt,
        "tools": tools,
    }


def call_model(messages, compiled_skill):
    request_body = {
        "model": "deepseek-v4-pro",
        "messages": messages,
        "tools": compiled_skill["tools"],
    }

    print("\nRequest body shape:")
    print(json.dumps({
        "model": request_body["model"],
        "messages": [
            {"role": message["role"], "content": message["content"][:80]}
            for message in request_body["messages"]
        ],
        "tools": [
            tool["function"]["name"]
            for tool in request_body["tools"]
        ],
    }, ensure_ascii=False, indent=2))

    response = client.chat.completions.create(**request_body)
    return response.choices[0].message


def run_tool(tool_call):
    name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)

    tool_fn = TOOL_REGISTRY[name]["function"]
    result = tool_fn(**arguments)

    print(f"Tool: {name}({arguments}) -> {result}")
    return result


def run_agent(user_input, skill_path):
    compiled_skill = compile_skill_to_request_parts(skill_path)

    print("Loaded skill:")
    print(json.dumps({
        "skill_name": compiled_skill["skill_name"],
        "tools_from_skill": compiled_skill["tool_names"],
        "response_format_from_skill": compiled_skill["response_format"],
    }, ensure_ascii=False, indent=2))

    messages = [
        {"role": "system", "content": compiled_skill["system_prompt"]},
        {"role": "user", "content": user_input},
    ]

    while True:
        message = call_model(messages, compiled_skill)
        messages.append(message.model_dump())

        if not message.tool_calls:
            raise RuntimeError("Expected tool_calls. The skill asks the model to call finish.")

        for tool_call in message.tool_calls:
            name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            if name == "finish":
                print(f"Finish: {arguments['final_answer']}")
                return arguments["final_answer"]

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

skill_path = Path(__file__).parent / "skills" / "weather_math" / "SKILL.md"
run_agent("Weather in Hangzhou, and what is 12 * 3 + 4?", skill_path)
