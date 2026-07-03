import json
import os
from openai import OpenAI


MEMORY_STORE = {
    "user_profile": {
        "language": "Chinese",
        "coding_background": "Java",
        "learning_goal": "Understand agent harness, tools, workflow, and memory.",
    },
    "preferences": {
        "explanation_style": "Use flow/state first, syntax second.",
        "output_style": "Keep examples small and readable.",
    },
    "unrelated": {
        "favorite_food": "no need to send this for coding questions",
    },
}


def retrieve_memory(user_input):
    selected = {
        "user_profile": MEMORY_STORE["user_profile"],
        "preferences": MEMORY_STORE["preferences"],
    }

    if "food" in user_input.lower():
        selected["unrelated"] = MEMORY_STORE["unrelated"]

    return selected


def build_messages(user_input):
    memory = retrieve_memory(user_input)

    system_prompt = (
        "You are a teaching assistant.\n\n"
        "Relevant memory for this request:\n"
        f"{json.dumps(memory, ensure_ascii=False, indent=2)}\n\n"
        "Use the memory only when it helps answer the current question."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input},
    ]

    print("Memory selected for this request:")
    print(json.dumps(memory, ensure_ascii=False, indent=2))

    return messages


client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)

user_input = "用我容易理解的方式解释一下 LangGraph 的 state。"
messages = build_messages(user_input)

response = client.chat.completions.create(
    model="deepseek-v4-pro",
    messages=messages,
)

print("\nModel answer:")
print(response.choices[0].message.content)
