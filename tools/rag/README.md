# Stampede Management Project Knowledge Index

This directory contains the local CocoIndex-backed project knowledge setup used by OpenCode.

## What Is Indexed

The index covers the Python crowd monitoring application, auth/licensing utilities, Spring Boot WebSocket backend, React
frontend, docs, and examples.

It intentionally excludes virtual environments, generated folders, build outputs, dependency folders, local RAG
setup/data, logs, model binaries, license files, and other sensitive or bulky artifacts.

## Setup

```bash
/opt/homebrew/bin/python3.12 -m venv tools/rag/.venv
tools/rag/.venv/bin/python -m pip install -r tools/rag/requirements.txt
```

CocoIndex is not available for the macOS system Python 3.9 used by `/usr/bin/python3`; use Python 3.12 or newer.

## Build Or Refresh The Index

```bash
tools/rag/.venv/bin/python tools/rag/stampede_project_index.py
```

CocoIndex stores incremental state under `tools/rag/data/cocoindex.lmdb` and the searchable SQLite target at
`tools/rag/data/stampede_project_knowledge.sqlite`.

## Auto Refresh

Local queries and the OpenCode MCP server refresh the index on demand before searching. A refresh runs when the SQLite
target is missing, when an indexed source file is newer than the last successful refresh, or when the refresh marker is
older than `STAMPEDE_RAG_REFRESH_MIN_INTERVAL_SECONDS` so deletions and renames are picked up periodically.

The default OpenCode interval is 300 seconds. Set `STAMPEDE_RAG_AUTO_REFRESH=0` to disable auto-refresh, or change
`STAMPEDE_RAG_REFRESH_MIN_INTERVAL_SECONDS` to tune the periodic refresh cadence.

## Query Locally

```bash
tools/rag/.venv/bin/python tools/rag/query_project_knowledge.py "How does the occupancy pipeline work?"
tools/rag/.venv/bin/python tools/rag/query_project_knowledge.py "Where are dashboard WebSocket messages handled?" --module backend
```

## OpenCode MCP

`.opencode/opencode.json` starts `tools/rag/mcp_project_knowledge.py` as the `stampede_project_knowledge` MCP server and
starts Context7 with `npx -y @upstash/context7-mcp`. Restart OpenCode after config changes.
