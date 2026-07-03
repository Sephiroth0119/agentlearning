![AgentLearning README hero](assets/readme-hero.png)

# AgentLearning

Personal workspace for agent learning, reusable skills, technical notes, and ERP agent experiments.

This repository is not a single product repo. It is split by work boundary:

- reusable skills live in `skills/`
- throwaway or learning experiments live in `labs/`
- longer-running agent projects live in `projects/`
- scheduled or accumulated technical notes live in `knowledge/`

The current agent harness examples use DeepSeek's OpenAI-compatible API and gradually add concepts:

- direct model calls
- multi-round `messages`
- JSON output
- tool calling
- agent loops
- multi-tool `finish` flow
- markdown skill loading
- LangGraph workflow
- simple memory injection

## Layout

```text
assets/                         Images and shared media
knowledge/scheduled-tech-notes/ Scheduled technical learning notes
labs/agent-harness/             Python examples for model/tool/harness experiments
projects/erp-kchz-agent/        ERP kchz agent development records and experiments
skills/sjh-style/               Personal style skill draft and references
```

## Setup

Install the Python packages used by the examples:

```powershell
pip install openai langgraph
```

Set your DeepSeek API key before running API examples:

```powershell
$env:DEEPSEEK_API_KEY="your-token"
```

Do not commit `.env` files or API tokens.

## Suggested Next Step

The next practical direction is to build a small CLI learning assistant agent:

```text
User input
  -> LangGraph agent node
  -> knowledge tools: search_notes / read_note / save_note / finish
  -> simple text memory first
  -> embedding and rerank later
```

For ERP work, keep `projects/erp-kchz-agent/` as the boundary. Put rough notes in `notes/`, durable decisions in `decisions/`, and runnable probes or mock experiments in `experiments/`.
