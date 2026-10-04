# 🗺️ Agentic AI: The Project-First Open-Source Roadmap

A zero-cost, hands-on engineering guide to mastering Agentic AI from scratch. Built exclusively with local open-weights models (via Ollama) and Python. No proprietary APIs, no subscriptions, and zero cloud lock-in.

---

## 🛠️ The Open-Source Stack Card

| Layer | Tool | Cost | Why We Use It |
|---|---|---|---|
| **Local LLM Engine** | Ollama (`llama3.2:3b` or `qwen2.5:7b`) | 100% Free & Offline | Runs locally in RAM/VRAM, zero API bills, native tool-calling fine-tuning |
| **Agent Tool Execution** | Pure Python Functions | Free | Zero overhead; transparent understanding of the execution bridge |
| **Long-Term Memory** | Local JSON / SQLite file | Free | Persistent storage across restarts without complex cloud databases |
| **State Machine & Planning** | LangGraph | Free & Open Source | Cyclic graph execution; deterministic control over multi-step workflows |
| **Live Web Search** | `duckduckgo-search` | Free | Real-time fact retrieval with zero API keys or rate limits |
| **Local Workspace** | Python 3.10+ `venv` | Free | Isolated, reproducible development environment |

---

## ⚡ Quick Concept Index

1. **Agent**: An LLM program equipped with tools that can decide *when* and *how* to execute code rather than just generating static text.
2. **Tool Calling (Function Calling)**: A structured protocol where the model predicts a function name and JSON arguments instead of a normal conversational response.
3. **Semantic Routing**: How the LLM reads plain-English `"description"` strings of tools to determine which one matches the user's intent.
4. **`messages` Transcript**: The stateful timeline passed to the LLM on every call, acting as the memory notepad for a stateless model.
5. **RLHF Refusal Reflex**: Pre-trained model reluctance to answer real-time questions (overridden via System Prompts and authoritative tool results).
6. **Context Persistence (Memory)**: Extracting user facts and saving them to disk so they survive script restarts.
7. **Graph State (LangGraph)**: Passing a structured dictionary (State) through defined worker functions (Nodes) connected by logic pathways (Edges).
8. **Multi-Agent Orchestration**: Coordinating multiple specialized LLM personas (e.g., Writer, Critic, Synthesizer) to catch blind spots and refine output.

---

## Phase 0 — Environment Setup

### 1. Install Ollama & Pull the Model
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start the local Ollama background server
ollama serve

# In a new terminal, pull the 3B parameter tool-calling model (~2.0 GB)
ollama pull llama3.2:3b
```

### 2. Set Up the Python Virtual Environment
```bash
mkdir -p student-agent && cd student-agent
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install ollama duckduckgo-search langgraph langchain-core
```

---

## Phase 1 — Project 1: Homework Math & Real-Time Agent
**Core Concept:** *What is an agent? Tool Use & The Dispatch Loop.*

### Why this project?
LLMs are language predictors, not calculators or clocks. By giving the model Python tools for math and real-time clock access, we turn a text-predictor into an autonomous agent that routes tasks to code.

### Complete Runnable Code (`agent-tools.py`)
```python
import json
import ollama
from datetime import datetime

# --- 1. Define Tools (The Agent's "Hands") ---
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression safely."""
    try:
        # Sandboxed eval: Strips all builtins so no system commands can run
        result = eval(expression, {"__builtins__": None}, {})
        return str(result)
    except Exception as e:
        return f"Error: {e}"

def get_current_time() -> str:
    """Returns the current date and time formatted as a string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# --- 2. Tool Schemas (The Agent's "Instruction Manual") ---
tools = [
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Calculate mathematical expressions like '24 * 15' or '(100 / 4) + 12'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "The math expression to evaluate"}
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Get the current date and time right now. Always call this when asked about the time, date, or today.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    }
]

# --- 3. Lookup Map (Connecting Text to Python Functions) ---
available_tools = {
    "calculate": calculate,
    "get_current_time": get_current_time,
}

# --- 4. The Agent Execution Loop ---
def run_agent(prompt: str):
    # System prompt overrides default RLHF refusal reflex
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant with access to real-time tools. When you receive data from tools (such as time or math results), trust that data and use it directly to answer the user."
        },
        {"role": "user", "content": prompt}
    ]

    # Step A: First LLM Call (Decides whether to answer or call tools)
    response = ollama.chat(model="llama3.2:3b", messages=messages, tools=tools)
    messages.append(response["message"])

    # Step B: Check if the model emitted tool calls
    if response["message"].get("tool_calls"):
        for tool_call in response["message"]["tool_calls"]:
            func_name = tool_call["function"]["name"]
            arguments = tool_call["function"]["arguments"]

            print(f"🤖 [Agent Decision]: Needs tool '{func_name}' with args {arguments}")
            tool_output = available_tools[func_name](**arguments)
            print(f"🔧 [Tool Output]: {tool_output}")

            # Step C: Append tool observation to the notepad
            messages.append({
                "role": "tool",
                "content": str(tool_output),
            })

        # Step D: Final LLM Call (Synthesizes final answer using tool observations)
        final_response = ollama.chat(model="llama3.2:3b", messages=messages, tools=tools)
        return final_response["message"]["content"]

    return response["message"]["content"]

if __name__ == "__main__":
    query = "I have 4 classes with 18 students each and 3 classes with 24 students. How many total students are there, and what is the time right now?"
    print(f"User Query: {query}\n")
    answer = run_agent(query)
    print(f"\nFinal Agent Response:\n{answer}")
```

### Key Discoveries from Phase 1
1. **Ollama Chat Template Injection:** When you pass `tools=tools`, Ollama merges your JSON schema into the model's chat template (`ollama show --template llama3.2:3b`).
2. **Semantic Matching:** The model matches questions to tools based purely on the text in the `"description"` fields.
3. **The `messages` Transcript:** LLMs have zero memory; passing the accumulated `messages` list back and forth is what provides continuity.

---

## Phase 2 — Project 2: Persistent Study Coach & Flashcard Memory
**Core Concept:** *Memory & Context Persistence.*

### Why this project?
LLMs are stateless. When you exit a Python process, the conversation disappears. Real personal agents must remember user preferences, exam dates, and weak topics across reboots without requiring paid cloud databases.

### Complete Runnable Code (`study_memory_agent.py`)
```python
import json
import os
import ollama

MEMORY_FILE = "study_memory.json"

def load_memory() -> dict:
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {"weak_topics": [], "session_notes": []}

def save_memory(memory: dict):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

def study_coach_turn(user_input: str):
    memory = load_memory()

    # Dynamic system prompt primed with persistent disk memory
    system_prompt = f"""You are a personal student study coach.
Current student profile:
- Weak topics to reinforce: {', '.join(memory['weak_topics']) if memory['weak_topics'] else 'None recorded yet'}
- Past session takeaways: {'; '.join(memory['session_notes'][-3:]) if memory['session_notes'] else 'First session'}

Respond concisely. If the student struggles with a concept, output:
[WEAK_TOPIC: <topic_name>]
If the student shares an exam date, deadline, or rule to remember, output:
[NOTE: <note_text>]
"""

    response = ollama.chat(
        model="llama3.2:3b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
    )

    content = response["message"]["content"]

    # Extract memory tags and save to disk
    if "[WEAK_TOPIC:" in content:
        topic = content.split("[WEAK_TOPIC:")[1].split("]")[0].strip()
        if topic not in memory["weak_topics"]:
            memory["weak_topics"].append(topic)
            save_memory(memory)
            print(f"💾 [Disk Memory Saved]: Added weak topic -> '{topic}'")

    if "[NOTE:" in content:
        note = content.split("[NOTE:")[1].split("]")[0].strip()
        memory["session_notes"].append(note)
        save_memory(memory)
        print(f"💾 [Disk Memory Saved]: Logged note -> '{note}'")

    clean_display = content.split("[WEAK_TOPIC:")[0].split("[NOTE:")[0].strip()
    return clean_display

if __name__ == "__main__":
    print("🎓 Study Coach active. Type 'exit' to quit.\n")
    while True:
        try:
            user_msg = input("You: ")
            if user_msg.lower() in ("exit", "quit"):
                break
            reply = study_coach_turn(user_msg)
            print(f"\nCoach: {reply}\n")
        except (KeyboardInterrupt, EOFError):
            break
```

---

## Phase 3 — Project 3: Course Research & Outline Planner
**Core Concept:** *Multi-Step Reasoning & Deterministic State Graphs (LangGraph).*

### Why this project?
Asking a single prompt to "research a topic, verify sources, and write an essay outline" results in shallow, hallucinated text. LangGraph breaks complex tasks into an explicit assembly line of nodes sharing a single state.

### Complete Runnable Code (`research_graph.py`)
```python
from typing import TypedDict, List
from duckduckgo_search import DDGS
from langgraph.graph import StateGraph, END
import ollama

# --- 1. State Definition (The Shared Notepad) ---
class AgentState(TypedDict):
    topic: str
    search_queries: List[str]
    raw_research: List[str]
    outline: str

# --- 2. Graph Nodes (The Specialized Workers) ---
def step_plan_queries(state: AgentState) -> AgentState:
    print("🔍 [Step 1]: Generating focused search queries...")
    prompt = f"Provide 2 concise search queries to research: '{state['topic']}'. Output ONLY the queries, one per line."
    res = ollama.chat(model="llama3.2:3b", messages=[{"role": "user", "content": prompt}])
    queries = [q.strip("- ").strip() for q in res["message"]["content"].strip().split("\n") if q.strip()][:2]
    return {"search_queries": queries}

def step_run_research(state: AgentState) -> AgentState:
    print(f"🌐 [Step 2]: Searching web for: {state['search_queries']}")
    findings = []
    ddgs = DDGS()
    for q in state["search_queries"]:
        try:
            results = ddgs.text(q, max_results=2)
            for r in results:
                findings.append(f"Title: {r['title']}\nSnippet: {r['body']}")
        except Exception as e:
            findings.append(f"Search failed for {q}: {e}")
    return {"raw_research": findings}

def step_generate_outline(state: AgentState) -> AgentState:
    print("📝 [Step 3]: Synthesizing research into paper outline...")
    notes = "\n\n".join(state["raw_research"])
    prompt = f"""You are an academic advisor. Using the research notes below, produce an outline for an essay on: '{state['topic']}'.

Research Notes:
{notes}

Include:
1. Thesis statement
2. Key section headings with supporting facts
3. Recommended discussion questions
"""
    res = ollama.chat(model="llama3.2:3b", messages=[{"role": "user", "content": prompt}])
    return {"outline": res["message"]["content"]}

# --- 3. Assemble the Graph Pipeline ---
workflow = StateGraph(AgentState)
workflow.add_node("planner", step_plan_queries)
workflow.add_node("researcher", step_run_research)
workflow.add_node("writer", step_generate_outline)

workflow.set_entry_point("planner")
workflow.add_edge("planner", "researcher")
workflow.add_edge("researcher", "writer")
workflow.add_edge("writer", END)

app = workflow.compile()

if __name__ == "__main__":
    topic = "Impact of renewable microgrids on rural student study habits"
    print(f"Running research pipeline for: {topic}\n")
    final_output = app.invoke({"topic": topic, "search_queries": [], "raw_research": [], "outline": ""})
    print("\n================ FINAL OUTLINE ================\n")
    print(final_output["outline"])
```

---

## Phase 4 — Project 4: The Peer-Review & Debate Room
**Core Concept:** *Multi-Agent Systems & Role Orchestration.*

### Why this project?
A single LLM instance is prone to confirmation bias. When you create two opposing personas (a Proposer and a Skeptic) and have a Synthesizer mediate between them, logical fallacies and weak points are caught automatically.

### Complete Runnable Code (`peer_review_agents.py`)
```python
import ollama

def agent_draft(topic: str) -> str:
    print("👤 [Agent 1 - Proposer]: Writing initial position...")
    prompt = f"Write a 1-paragraph persuasive argument on: '{topic}'."
    res = ollama.chat(model="llama3.2:3b", messages=[{"role": "user", "content": prompt}])
    return res["message"]["content"]

def agent_critique(topic: str, draft: str) -> str:
    print("🧐 [Agent 2 - Skeptic]: Auditing argument for logical fallacies...")
    prompt = f"""You are a strict grading reviewer. Audit this argument on '{topic}'.
Find 2 logical flaws or unproven assumptions. Be concise and direct.

Draft:
{draft}
"""
    res = ollama.chat(model="llama3.2:3b", messages=[{"role": "user", "content": prompt}])
    return res["message"]["content"]

def agent_synthesizer(topic: str, draft: str, critique: str) -> str:
    print("⚖️ [Agent 3 - Synthesizer]: Re-writing bulletproof final version...")
    prompt = f"""Revise the draft to resolve the weaknesses identified by the critique.

Original Topic: {topic}
Original Draft: {draft}
Critique: {critique}

Provide the final strengthened argument:"""
    res = ollama.chat(model="llama3.2:3b", messages=[{"role": "user", "content": prompt}])
    return res["message"]["content"]

def run_peer_review_room(topic: str):
    draft = agent_draft(topic)
    print(f"\n--- Initial Draft ---\n{draft}\n")

    critique = agent_critique(topic, draft)
    print(f"\n--- Skeptic Critique ---\n{critique}\n")

    final_version = agent_synthesizer(topic, draft, critique)
    print(f"\n--- Polished Submission ---\n{final_version}\n")

if __name__ == "__main__":
    run_peer_review_room("University textbooks should be completely replaced by open-source digital wikis.")
```

---

## Phase 5 — Project 5: Local Desktop Notes & Study Assistant
**Core Concept:** *Grounding Agents to Local Files & Directory Standards.*

### Why this project?
Connecting an agent to local folders lets you query and organize your actual personal lecture notes without exposing private files to cloud servers.

### Complete Runnable Code (`notes_agent.py`)
```python
import os
import glob
import ollama

NOTES_DIR = "./my_lecture_notes"
os.makedirs(NOTES_DIR, exist_ok=True)

# Create a sample note if the directory is empty
sample_file = os.path.join(NOTES_DIR, "biology_101.txt")
if not os.path.exists(sample_file):
    with open(sample_file, "w") as f:
        f.write("Mitochondria produce ATP through cellular respiration. Photosynthesis converts sunlight into glucose in chloroplasts.")

def list_notes() -> str:
    """Lists all available study note text files."""
    files = glob.glob(f"{NOTES_DIR}/*.txt")
    return "\n".join([os.path.basename(f) for f in files]) if files else "No notes found."

def read_note(filename: str) -> str:
    """Reads the complete content of a given study note file."""
    filepath = os.path.join(NOTES_DIR, os.path.basename(filename))
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return f.read()
    return f"File '{filename}' does not exist."

tools = [
    {
        "type": "function",
        "function": {
            "name": "list_notes",
            "description": "Get a list of all existing note filenames in the student notes folder.",
            "parameters": {"type": "object", "properties": {}},
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_note",
            "description": "Read the text contents of a note file by name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "e.g., 'biology_101.txt'"}
                },
                "required": ["filename"],
            },
        }
    }
]

tool_dispatcher = {"list_notes": list_notes, "read_note": read_note}

def ask_notes_assistant(user_prompt: str):
    messages = [
        {"role": "system", "content": "You are a local files assistant. Use your tools to read files before answering."},
        {"role": "user", "content": user_prompt}
    ]

    res = ollama.chat(model="llama3.2:3b", messages=messages, tools=tools)
    messages.append(res["message"])

    while res["message"].get("tool_calls"):
        for tool_call in res["message"]["tool_calls"]:
            fname = tool_call["function"]["name"]
            args = tool_call["function"]["arguments"]
            print(f"📂 [File Tool]: Calling {fname}({args})")
            output = tool_dispatcher[fname](**args)

            messages.append({"role": "tool", "content": str(output)})

        res = ollama.chat(model="llama3.2:3b", messages=messages, tools=tools)
        messages.append(res["message"])

    return res["message"]["content"]

if __name__ == "__main__":
    query = "Look at my notes, tell me what files I have, and summarize how mitochondria work."
    print(f"User: {query}\n")
    reply = ask_notes_assistant(query)
    print(f"\nAssistant:\n{reply}")
```
