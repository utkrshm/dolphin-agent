# Voice Controlled AI Agent

## Model Decisions

- Qwen3.5 4B as main orchestration agent, because Qwen3 excels at tool calling and reasoning, which is what I needed for this task. This model series is currently SOTA open-source model in this size range.
- Gemma3 1B as a summarization agent, to elaborately summarize the files the main agent has been asked to summarize (so as to not pollute the token usage of the orchestration agent too much). Gemma3 series was considered state-of-the-art for textual understanding tasks, such as summarization, back when they were released. I also wanted to optimize for low latency when it came to this agent, because essentially two tool calls are being used in the summarization task.
