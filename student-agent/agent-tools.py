import json
import ollama
from datetime import datetime


# --- 1. Define tools (Agent's "Hands") ---
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression safely."""
    try:
        # Limited builtins for safe local evaluation
        result = eval(expression, {"__builtins__": None}, {})
        return str(result)
    except Exception as e:
        return f"Error: {e}"

def get_current_time():
    """returns the current time"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Tool schema: Informs the model when and how to call the function
tools = [
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Calculate mathematical expressions like '24 * 15' or '(100 / 4) + 12'",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "The math expression to evaluate",
                    }
                },
                "required": ["expression"],
            },
        },

    },

    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Get the current date and time right now. Always call this when asked about the time, date, today, or how many hours left.",
            "parameters": {
                "type": "object",
                "properties": {},  # No parameters needed
            },
        },
    }
]

# Map string name returned by model to actual Python function
available_tools = {
    "calculate": calculate,
    "get_current_time": get_current_time
    }


# --- 2. The Agent Loop (Thought -> Action -> Observation -> Final Answer) ---
def run_agent(prompt: str):
    messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant with access to real-time tools. When you receive data from tools (such as time or math results), trust that data and use it directly to answer the user."
            },
            {"role": "user", "content": prompt}
        ]


    # Step A: Ask model. It either replies with text OR requests a tool call
    response = ollama.chat(model="llama3.2:3b", messages=messages, tools=tools)
    messages.append(response["message"])

    # Step B: Check if the model decided it needs a tool
    if response["message"].get("tool_calls"):
        for tool_call in response["message"]["tool_calls"]:
            func_name = tool_call["function"]["name"]
            arguments = tool_call["function"]["arguments"]

            print(
                f"🤖 [Agent Decision]: Needs tool '{func_name}' with args {arguments}"
            )
            tool_output = available_tools[func_name](**arguments)
            print(f"🔧 [Tool Output]: {tool_output}")

            # Step C: Feed the tool's result back to the model as an observation
            messages.append(
                {
                    "role": "tool",
                    "content": str(tool_output),
                }
            )

        # Step D: Final answer from model using the tool output
        final_response = ollama.chat(model="llama3.2:3b", messages=messages)
        return final_response["message"]["content"]

    return response["message"]["content"]


if __name__ == "__main__":
    query = "I have 4 classes with 18 students each and 3 classes with 24 students. How many total students are there? and what is the time rn"
    print(f"User: {query}\n")
    answer = run_agent(query)
    print(f"\nFinal Agent Response:\n{answer}")
