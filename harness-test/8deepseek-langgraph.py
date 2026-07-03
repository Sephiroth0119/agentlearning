import ast
import json
import operator
import os
from typing import Any, TypedDict

from langgraph.graph import END, StateGraph
from openai import OpenAI


class AgentState(TypedDict):
    messages: list[dict[str, Any]]
    final_answer: str | None
    round_index: int


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


def agent_node(state: AgentState):
    print(f"\n--- Round {state['round_index']} / agent node ---")

    message = call_model(state["messages"])
    messages = state["messages"] + [message.model_dump()]

    if not message.tool_calls:
        raise RuntimeError("Model returned no tool_calls. This graph expects finish().")

    return {
        "messages": messages,
        "final_answer": state["final_answer"],
        "round_index": state["round_index"],
    }


def tools_node(state: AgentState):
    print("--- tools node ---")

    messages = list(state["messages"])
    assistant_message = messages[-1]
    final_answer = state["final_answer"]

    for tool_call in assistant_message["tool_calls"]:
        tool_id = tool_call["id"]
        name = tool_call["function"]["name"]
        arguments = json.loads(tool_call["function"]["arguments"])

        print(f"Model wants tool: {name}")
        print(f"Arguments: {json.dumps(arguments, ensure_ascii=False)}")

        if name == "finish":
            final_answer = arguments["final_answer"]
            print(f"Final answer: {final_answer}")
            continue

        if name == "get_weather":
            result = get_weather(**arguments)
        elif name == "calculate":
            result = calculate(**arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")

        print(f"Tool result: {result}")
        messages.append({
            "role": "tool",
            "tool_call_id": tool_id,
            "content": result,
        })

    return {
        "messages": messages,
        "final_answer": final_answer,
        "round_index": state["round_index"] + 1,
    }


def route_after_tools(state: AgentState):
    if state["final_answer"]:
        return END
    return "agent"


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("agent", agent_node)
    graph.add_node("tools", tools_node)

    graph.set_entry_point("agent")
    graph.add_edge("agent", "tools")
    graph.add_conditional_edges("tools", route_after_tools)

    return graph.compile()


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

user_input = "How's the weather in Hangzhou, Zhejiang? Also calculate 12 * 3 + 4."
print(f"User: {user_input}")

initial_state = {
    "messages": [
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
    ],
    "final_answer": None,
    "round_index": 1,
}

app = build_graph()
final_state = app.invoke(initial_state)

print("\n=== Graph finished ===")
print(final_state["final_answer"])
