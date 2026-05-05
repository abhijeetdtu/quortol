---
title: Building an Agent from Scratch in theindependent
slug: building-an-agent-from-scratch-theindependent
excerpt: A starter write-up of the architecture and maintainability work that shaped theindependent into a durable LangGraph plus Ollama agent.
tags: Agent Engineering, LangGraph, Ollama
published_at: 2026-05-05T09:00:00
updated_at: 2026-05-05T09:00:00
---

# Building an Agent from Scratch in theindependent

This post captures the work done in `C:\Users\abhij\Code\theindependent` to evolve a basic loop into a practical agent system.

## What We Built

- A persistent LangGraph workflow that keeps working until `mark_task_complete`.
- A multi-stage pipeline for planning, searching, reading sources, and synthesis.
- Durable short-term checkpoints and long-term SQLite memory keyed by user.
- Tooling for web search, focused page reading, skill loading, and runtime memory operations.
- Optional human-in-the-loop resume flow with explicit decision checkpoints.

## Maintainability Improvements

- Removed hardcoded credentials and shifted to environment variables.
- Added robust tool-call parsing for both JSON and XML-like fallback formats.
- Introduced per-tool timeout policy and runtime timeout enforcement.
- Refactored complex routing logic and improved targeted exception handling.
- Added architecture, state, and error-recovery documentation for faster onboarding.

## Why It Matters

The biggest gain was reliability under real usage: runs are easier to resume, tool failures are safer, and the system is easier to understand and extend.

## Next Iteration

1. Expand unit coverage for parser, timeout, and discovery utilities.
2. Add stricter type hints and static analysis checks.
3. Continue improving citation and source coverage checks for research outputs.
