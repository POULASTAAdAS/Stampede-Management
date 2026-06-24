---
name: project-knowledge
description: Use when answering questions about Stampede Management project code knowledge, including Python crowd monitoring, tracking, geometry, licensing/auth, Spring Boot WebSocket backend, React frontend, docs, or local RAG knowledge.
---

# Stampede Management Project Knowledge

Use the `stampede_project_knowledge` MCP server tool `project_knowledge_search` before answering questions about this
project's implementation, especially questions that require connecting code across Python monitoring, backend, frontend,
auth, examples, or docs.

The index covers source and documentation files under the Python application, auth utilities, Spring Boot backend, React
frontend, examples, and docs. It excludes virtual environments, generated output, build artifacts, dependency folders,
logs, model binaries, license files, and local RAG data.

Query examples:

```text
How does the crowd occupancy pipeline work?
Where are WebSocket updates sent from Python?
How does the backend route dashboard messages?
Which frontend component renders occupancy status?
Where is license validation handled?
How is perspective calibration configured?
```

If the MCP tool is unavailable, run the local CLI instead:

```bash
tools/rag/.venv/bin/python tools/rag/query_project_knowledge.py "How does the crowd occupancy pipeline work?"
```
