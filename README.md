# Learning Agentic AI — Project-First Open-Source Journey

> Building practical, autonomous AI agents completely locally with open-source tools. **$0 API cost. 100% private. No cloud lock-in.**

This repository documents my hands-on journey learning **Agentic AI** from the ground up by building real tools for daily student life rather than just studying theory.

---

## 🗺️ Learning Roadmap & Progress

| Phase | Milestone / Project | Core Concept | Status |
|:---:|---|---|:---:|
| **0** | **Local Environment Setup** | Local LLM inference via Ollama (`llama3.2:3b`) | ✅ Completed |
| **1** | **Project 1: Homework Math & Real-Time Agent** | ReAct loop, tool calling, JSON schemas, semantic routing | ✅ Completed |
| **2** | **Project 2: Persistent Study Session Coach** | Long-term memory, context persistence via disk state | 🔄 In Progress |
| **3** | **Project 3: Course Research & Outline Planner** | Multi-step reasoning & state machines with LangGraph | ⏳ Upcoming |
| **4** | **Project 4: Peer-Review & Debate Room** | Multi-agent coordination & adversary/critic workflows | ⏳ Upcoming |
| **5** | **Project 5: Desktop Notes & Study Assistant** | Grounding agents to local files & standard protocols | ⏳ Upcoming |

---

## 🚀 Phase 1: ReAct Agent & Multi-Tool Calling (Completed)

In this phase, I built an autonomous agent from scratch in Python without heavy wrapper frameworks to understand the core dispatch loop.

### What it does:
The agent takes complex user prompts combining arithmetic and real-time questions (e.g., *"I have 4 classes with 18 students each and 3 classes with 24 students. How many total students are there, and what is the time right now?"*):
1. **Understands Tools Semantically:** Reads the plain-English function descriptions and decides which tools are needed.
2. **Executes Multiple Tools in Parallel:** 
   - `calculate(expression)`: Runs sandboxed mathematical operations safely.
   - `get_current_time()`: Retrieves live system timestamps.
3. **Overcomes RLHF Refusal Reflex:** Uses system-level grounding to ensure the model trusts tool outputs instead of apologizing with standard *"I don't have real-time access"* canned disclaimers.

```
                      [User Prompt]
                            │
                            ▼
                     [Local LLaMA 3.2]
                            │
     ┌──────────────────────┴──────────────────────┐
     ▼                                             ▼
Tool Request: calculate                       Tool Request: get_current_time
     │                                             │
     ▼                                             ▼
Python Sandbox (144)                         datetime.now()
     │                                             │
     └──────────────────────┬──────────────────────┘
                            ▼
              Appended to `messages` notepad
                            │
                            ▼
              [LLaMA Synthesizes Final Answer]
```

### Deep Engineering Insights Uncovered:
* **The LLM is Still Just Predicting Tokens:** Function calling isn't magic code execution inside the model; the model simply predicts a structured JSON string adhering to schemas injected via Ollama's chat template.
* **The `messages` Transcript is Memory:** LLMs have zero internal state. Passing the updated `messages` list back and forth simulates continuous dialogue and tool feedback.
* **Semantic Routing Efficiency:** Large general models can be paired with small, hyper-fast router models to classify intents and dispatch tools with 90% lower latency.

---

## 🛠️ Tech Stack

* **Inference Engine:** [Ollama](https://ollama.com/) (running `llama3.2:3b` locally on CPU/GPU)
* **Language:** Python 3.10+
* **Libraries:** `ollama`, `duckduckgo-search`, `langgraph`, `pydantic`
* **Infrastructure:** 100% offline-capable, Linux-native

---

## 💻 Running the Code

### 1. Prerequisites
Ensure Ollama is installed and running:
```bash
ollama serve
ollama pull llama3.2:3b
```

### 2. Setup Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt  # or: pip install ollama duckduckgo-search langgraph
```

### 3. Run Project 1 (Agent with Tools)
```bash
python student-agent/agent-tools.py
```

---

## 📚 Complete Learning Guide
The comprehensive roadmap and complete code for all 5 phases are available in **[AGENTIC_AI_GUIDE.md](./AGENTIC_AI_GUIDE.md)**.
