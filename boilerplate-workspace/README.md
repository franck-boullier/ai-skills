# Boilerplate Workspace

A Startup folder containing the baseline skills and tools to create an AI Agent friendly workspace.

This boilerplate should work with tools like Claude Cowork and IDE like VS Code, Cursor, Google Antigravity, Amazon Kiro, or any other tool that supports the Skills format.

The main benefit of this boilerplate is that it give your agent MEMORIES and it has several skills that the agent can use to:

- Create document you can use to restart work that is spanning several sessions with your AI Agents
- Use the restart guide to continue where you've left off in a previous session.
- Record lessons learned from your interactions with your AI Agents.
- Document the decisions you need to make, record the reasons why you need to make them, and help you make the decisions.
- Record decisions you have made and the rationale behind them.

## Foundations

This was built on the key principles described in:

- [Why we need explainable AI - Aug 2020](https://medium.com/antlerglobal/5-reasons-why-you-need-explainable-ai-929a64ae66ff).
- [The COOL Framework - Jun 2024](linkedin.com/pulse/introducing-context-outputs-library-cool-framework-ai-franck-boullier-9jb9e).
- [Andrej Karpaty's LLM Knowledge base Concept - apr 2026](https://x.com/karpathy/status/2039805659525644595?s=20).

## Recommendations

- Use the Markdown format when writing documents. This is the format that most LLMs understand best with the mimimum number of tokens spent of converting documents.
- If you need to ingest documents, use the PDF format. PDF to text parser are usually built in most tools that you will use to interact with your LLM of choice.

## Key Principles

- This structure should be LLM-agnostic. It should be able to be used with most LLMs from the major providers (Anthropic, OpenAI, Google, Alibaba-Qwen, Kimi-K2, Moonshot Minimax, Meta Llama, xAI Grok, Mistral, etc...).
- We use the "Progressive Discovery" pattern to save on token cost and improve context retrieval. Each file that have a YAML formatted frontmatter will be discovered more efficiently. Initially, only the frontmatter (what's in this file) is loaded into the context window. The full file is loaded into the context window only when the agent needs to use it.

## Step-by-step Guide

- Create a new folder for your workspace on your local machine.
- Upodate the `AGENTS.md` file to explain the purpose of your workspace.

### Build the Agent Memory

- Open the newly created workspace folder in the tool that you are using (ex:Claude Cowork, VS Code with the Claude Code extension, Cursor, Google Antigravity, Amazon Kiro, etc...)

#### "Old School"

- Enter the following prompt.

```text
using the skill `build-agent-memory` can you help me build the memories files and folder structure for this workspace now please?
Act as a thought partner.
DO NOT GUESS!
Ask questions if you have ANY doubt!
```

#### Using A Shortcut Command

- Run the command `/build-memory` in the tool you are using and follow the instructions.
