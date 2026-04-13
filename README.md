# Dolphin Agent

A voice-controlled AI agent that runs entirely on your machine. Speak a command, watch it think, see it act.

---

## Demo

A demo of this project is available [here on YouTube](https://youtu.be/B4mwDj7juHM)

---

## What It Does

Dolphin Agent listens to your voice, understands what you want, and executes real actions on your local filesystem. It remembers what you told it last week. It asks before it overwrites anything. It shows you exactly what it's doing at every step.

No cloud. No subscriptions. No data leaving your machine.

---

## Features

**Voice first, but not voice only.** Speak into your mic, drop an audio file, or just type. All three input modes are available and switchable with a single keypress.

**Real agent, not a classifier.** Compound commands work. "Write a Python file with a retry function, then summarize it" executes both steps without you having to ask twice.

**Human in the loop.** The agent asks for your approval before writing or modifying any file. You see exactly what it wants to write before it touches your filesystem.

**Persistent memory across sessions.** Powered by Mem0. The agent remembers context from previous conversations. You don't have to re-explain your project every time you open the app.

**Full trace visibility.** Every tool call, every decision, every result is visible in a collapsible trace panel for each conversation turn. You always know what the agent did and why.

**Runs locally.** Whisper for transcription. Qwen3 via Ollama for reasoning. Gemma3:1b for summarization. Everything runs on your machine. Falls back to Groq if you don't have a local GPU.

---

## Quickstart

**Prerequisites:** Ollama running locally with `qwen3:4b` and `gemma3:1b` pulled. Python 3.12+. A Mem0 API key from [app.mem0.ai](https://app.mem0.ai).

```bash
git clone https://github.com/yourname/dolphin-agent
cd dolphin-agent
pip install uv
uv sync
cp .env.example .env
# fill in your keys
uv run textual run tui/app.py
```

---

## Controls

| Key | Action |
|-----|--------|
| `1` | Record from microphone |
| `2` | Upload an audio file |
| `3` | Type a prompt |
| `Ctrl+C` | Quit |

---

## What the Agent Can Do

- Create and write files
- Read files (text, markdown, PDF, Word)
- Summarize file contents
- Chain multiple operations in a single command
- Remember context from past sessions via Mem0

All file operations are sandboxed to the `output/` directory. The agent cannot touch anything outside it.

---

## Architecture

Four layers, each independently testable.

```
Voice Input / Text Input
        ↓
   Whisper STT
        ↓
  LangGraph Agent  ←→  Mem0 (long-term memory)
        ↓
   Tool Execution
        ↓
   Textual TUI
```

The agent is a LangGraph StateGraph with two nodes — an agent node that reasons with Qwen3, and a tool node that executes actions. Human-in-the-loop confirmation uses LangGraph's `interrupt()` primitive with `MemorySaver` checkpointing so the graph resumes exactly where it paused.

Read the full architecture breakdown in the [article](#).

---

## Environment Variables

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MAIN_MODEL=qwen3:4b
SUMMARY_MODEL=gemma3:1b
MEM0_API_KEY=your_key_here
MEM0_ORG_ID=your_org_id
MEM0_PROJECT_ID=your_project_id
GROQ_API_KEY=your_groq_key  # optional, fallback only
GROQ_MODEL=llama-3.3-70b-versatile
```

---

## Project Structure

```
dolphin-agent/
├── stt/               # Whisper transcription + mic recording
├── agent/
│   ├── nodes/         # agent_node, tool_node
│   ├── tools/         # read_file, write_to_file, summarize_file
│   ├── graph.py       # LangGraph graph assembly
│   └── state.py       # AgentState
├── tui/               # Textual app
├── scripts/           # Layer test harnesses
└── output/            # All agent file ops land here
```

---

## Built With

- [Whisper](https://github.com/openai/whisper) — speech to text
- [LangGraph](https://langchain-ai.github.io/langgraph/) — agent graph and session memory
- [Mem0](https://mem0.ai) — long-term memory across sessions
- [Ollama](https://ollama.ai) — local model inference
- [Textual](https://textual.textualize.io) — terminal UI

---

*All file operations are sandboxed. The agent cannot write outside the `output/` directory regardless of what it's asked to do.*