from __future__ import annotations

import os
import pathlib
import re
import sqlite3
import subprocess
import sys
import time
from dataclasses import dataclass

import numpy as np
from cocoindex.ops.sentence_transformers import SentenceTransformerEmbedder

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[2]
DATA_DIR = pathlib.Path(os.environ.get("STAMPEDE_RAG_DATA_DIR", PROJECT_ROOT / "tools" / "rag" / "data"))
SQLITE_PATH = pathlib.Path(os.environ.get("STAMPEDE_RAG_DB", DATA_DIR / "stampede_project_knowledge.sqlite"))
EMBEDDING_MODEL = os.environ.get("STAMPEDE_RAG_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
INDEX_SCRIPT_PATH = PROJECT_ROOT / "tools" / "rag" / "stampede_project_index.py"
REFRESH_STAMP_PATH = pathlib.Path(os.environ.get("STAMPEDE_RAG_REFRESH_STAMP", DATA_DIR / "auto_refresh.stamp"))
REFRESH_LOCK_PATH = pathlib.Path(os.environ.get("STAMPEDE_RAG_REFRESH_LOCK", DATA_DIR / "auto_refresh.lock"))
REFRESH_MIN_INTERVAL_SECONDS = int(os.environ.get("STAMPEDE_RAG_REFRESH_MIN_INTERVAL_SECONDS", "300"))
REFRESH_TIMEOUT_SECONDS = int(os.environ.get("STAMPEDE_RAG_REFRESH_TIMEOUT_SECONDS", "600"))
REFRESH_LOCK_WAIT_SECONDS = int(os.environ.get("STAMPEDE_RAG_REFRESH_LOCK_WAIT_SECONDS", "60"))

SOURCE_ROOTS: tuple[str, ...] = (".", "auth", "backend", "frontend", "docs", "examples")
INCLUDED_FILE_SUFFIXES = (
    ".py",
    ".kt",
    ".kts",
    ".java",
    ".js",
    ".jsx",
    ".css",
    ".html",
    ".json",
    ".properties",
    ".md",
    ".txt",
    ".ps1",
    ".bat",
)
EXCLUDED_DIR_NAMES = {
    ".git",
    ".idea",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    "build",
    "dist",
    ".gradle",
    ".kotlin",
    "node_modules",
    "data",
    "CrowdMonitor_Package_Windows",
}
EXCLUDED_FILE_NAMES = {"license.dat"}
EXCLUDED_FILE_SUFFIXES = (".dat", ".log", ".pt", ".png", ".zip", ".exe")

_embedder: SentenceTransformerEmbedder | None = None


@dataclass
class SearchResult:
    score: float
    module: str
    path: str
    start_line: int
    end_line: int
    language: str
    text: str


def _get_embedder() -> SentenceTransformerEmbedder:
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformerEmbedder(EMBEDDING_MODEL)
    return _embedder


def _auto_refresh_enabled() -> bool:
    value = os.environ.get("STAMPEDE_RAG_AUTO_REFRESH", "1").strip().lower()
    return value not in {"0", "false", "no", "off"}


def _is_indexed_source_file(path: pathlib.Path) -> bool:
    if path.name in EXCLUDED_FILE_NAMES or path.name.endswith(EXCLUDED_FILE_SUFFIXES):
        return False
    if not path.name.endswith(INCLUDED_FILE_SUFFIXES):
        return False

    try:
        relative_parts = path.relative_to(PROJECT_ROOT).parts
    except ValueError:
        relative_parts = path.parts

    if relative_parts[:2] == ("tools", "rag"):
        return False

    return not any(part.startswith(".") or part in EXCLUDED_DIR_NAMES for part in relative_parts)


def _latest_source_mtime_ns() -> int:
    latest = 0
    for source_root in SOURCE_ROOTS:
        root = PROJECT_ROOT / source_root
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or not _is_indexed_source_file(path):
                continue
            try:
                latest = max(latest, path.stat().st_mtime_ns)
            except FileNotFoundError:
                continue
    return latest


def _last_refresh_mtime_ns() -> int:
    latest = 0
    for path in (REFRESH_STAMP_PATH, SQLITE_PATH):
        try:
            latest = max(latest, path.stat().st_mtime_ns)
        except FileNotFoundError:
            continue
    return latest


def _needs_index_refresh() -> bool:
    if not SQLITE_PATH.exists():
        return True

    last_refresh_ns = _last_refresh_mtime_ns()
    if _latest_source_mtime_ns() > last_refresh_ns:
        return True

    if REFRESH_MIN_INTERVAL_SECONDS <= 0:
        return False

    return time.time_ns() - last_refresh_ns > REFRESH_MIN_INTERVAL_SECONDS * 1_000_000_000


def _acquire_refresh_lock() -> int | None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    deadline = time.monotonic() + REFRESH_LOCK_WAIT_SECONDS
    while True:
        try:
            fd = os.open(REFRESH_LOCK_PATH, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode("utf-8"))
            return fd
        except FileExistsError:
            try:
                lock_age_seconds = time.time() - REFRESH_LOCK_PATH.stat().st_mtime
                if lock_age_seconds > REFRESH_TIMEOUT_SECONDS:
                    REFRESH_LOCK_PATH.unlink(missing_ok=True)
                    continue
            except FileNotFoundError:
                continue

            if time.monotonic() >= deadline:
                return None
            time.sleep(0.25)


def _release_refresh_lock(fd: int | None) -> None:
    if fd is not None:
        os.close(fd)
    REFRESH_LOCK_PATH.unlink(missing_ok=True)


def _run_index_refresh() -> None:
    fd = _acquire_refresh_lock()
    if fd is None:
        return

    try:
        result = subprocess.run(
            [sys.executable, str(INDEX_SCRIPT_PATH)],
            cwd=PROJECT_ROOT,
            env=os.environ.copy(),
            capture_output=True,
            text=True,
            timeout=REFRESH_TIMEOUT_SECONDS,
            check=False,
        )
        if result.returncode != 0:
            details = (result.stderr or result.stdout).strip()
            raise RuntimeError(f"CocoIndex refresh failed with exit code {result.returncode}: {details}")
        REFRESH_STAMP_PATH.write_text(str(time.time_ns()), encoding="utf-8")
    finally:
        _release_refresh_lock(fd)


def _ensure_index_fresh() -> None:
    if not _auto_refresh_enabled() or not _needs_index_refresh():
        return

    try:
        _run_index_refresh()
    except Exception:
        if not SQLITE_PATH.exists():
            raise


def _decode_embedding(value: object) -> np.ndarray:
    if isinstance(value, memoryview):
        value = value.tobytes()
    if isinstance(value, bytes):
        return np.frombuffer(value, dtype=np.float32)
    if isinstance(value, str):
        return np.fromstring(value.strip("[]"), sep=",", dtype=np.float32)
    raise TypeError(f"Unsupported embedding storage type: {type(value).__name__}")


def _keyword_terms(query: str) -> list[str]:
    return [term for term in re.findall(r"[a-zA-Z0-9_]{3,}", query.lower()) if term]


def _keyword_bonus(query_terms: list[str], path: str, module: str, text: str) -> float:
    haystack = f"{module}\n{path}\n{text}".lower()
    matches = sum(1 for term in query_terms if term in haystack)
    return min(matches * 0.035, 0.35)


async def search_project_knowledge(query: str, module: str | None = None, limit: int = 8) -> list[SearchResult]:
    _ensure_index_fresh()

    if not SQLITE_PATH.exists():
        raise FileNotFoundError(
            f"Knowledge index not found at {SQLITE_PATH}. Run `tools/rag/.venv/bin/python tools/rag/stampede_project_index.py` first."
        )

    clean_query = query.strip()
    if not clean_query:
        return []

    limit = max(1, min(limit, 25))
    query_embedding = await _get_embedder().embed(clean_query)
    query_embedding = np.asarray(query_embedding, dtype=np.float32)
    query_norm = float(np.linalg.norm(query_embedding)) or 1.0
    query_terms = _keyword_terms(clean_query)

    sql = "SELECT module, path, language, start_line, end_line, text, embedding FROM project_knowledge_chunks"
    params: list[str] = []
    if module:
        module_filter = module.strip().strip("/")
        sql += " WHERE module LIKE ? OR path LIKE ?"
        params.extend([f"%{module_filter}%", f"{module_filter}/%"])

    results: list[SearchResult] = []
    with sqlite3.connect(SQLITE_PATH) as conn:
        for row in conn.execute(sql, params):
            row_module, path, language, start_line, end_line, text, embedding_blob = row
            embedding = _decode_embedding(embedding_blob)
            embedding_norm = float(np.linalg.norm(embedding)) or 1.0
            vector_score = float(np.dot(query_embedding, embedding) / (query_norm * embedding_norm))
            score = vector_score + _keyword_bonus(query_terms, path, row_module, text)
            results.append(
                SearchResult(
                    score=score,
                    module=row_module,
                    path=path,
                    start_line=start_line,
                    end_line=end_line,
                    language=language,
                    text=text,
                )
            )

    results.sort(key=lambda item: item.score, reverse=True)
    return results[:limit]


def format_results(query: str, results: list[SearchResult]) -> str:
    if not results:
        return f"No Stampede project knowledge results found for: {query}"

    lines = [f"Stampede project knowledge results for: {query}", ""]
    for index, result in enumerate(results, start=1):
        location = f"{result.path}:{result.start_line}-{result.end_line}"
        snippet = result.text.strip()
        if len(snippet) > 1_500:
            snippet = snippet[:1_500].rstrip() + "..."
        lines.extend(
            [
                f"{index}. score={result.score:.3f} module={result.module} `{location}` language={result.language}",
                "```",
                snippet,
                "```",
                "",
            ]
        )
    return "\n".join(lines).rstrip()
