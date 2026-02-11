"""Base analyzer utilities."""

import os
import re
from pathlib import Path
from typing import List, Dict, Any

TEXT_EXTENSIONS = {
    ".py", ".rs", ".go", ".js", ".ts", ".rb", ".sh", ".bash",
    ".yaml", ".yml", ".json", ".toml", ".md", ".txt",
    ".dockerfile", ".mk", ".make", "",
}

SKIP_DIRS = {".git", "node_modules", "vendor", "target", "build", "dist", "__pycache__"}

MAX_FILE_SIZE = 5 * 1024 * 1024


def should_scan_file(path: Path) -> bool:
    try:
        if path.stat().st_size > MAX_FILE_SIZE:
            return False
    except OSError:
        return False
    suffix = path.suffix.lower()
    name = path.name.lower()
    if name in {"makefile", "dockerfile", "containerfile"}:
        return True
    return suffix in TEXT_EXTENSIONS


def walk_repo(repo_path: Path) -> List[Path]:
    files = []
    for root, dirs, filenames in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for filename in filenames:
            filepath = Path(root) / filename
            if should_scan_file(filepath):
                files.append(filepath)
    return files


def grep_file(filepath: Path, patterns: List[re.Pattern]) -> List[Dict[str, Any]]:
    matches = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for line_num, line in enumerate(f, 1):
                for pattern in patterns:
                    if pattern.search(line):
                        matches.append({
                            "file": str(filepath),
                            "line": line_num,
                            "pattern": pattern.pattern,
                            "context": line.strip()[:200],
                        })
    except Exception:
        pass
    return matches


def analyze_repo(repo_path: Path, patterns: List[str]) -> Dict[str, Any]:
    compiled = [re.compile(p, re.IGNORECASE) for p in patterns]
    all_matches = []
    for filepath in walk_repo(repo_path):
        matches = grep_file(filepath, compiled)
        all_matches.extend(matches)
    return {"found": len(all_matches) > 0, "matches": all_matches}


def check_paths_exist(repo_path: Path, paths: List[str]) -> List[Dict[str, Any]]:
    matches = []
    for rel_path in paths:
        full_path = repo_path / rel_path
        if full_path.exists():
            matches.append({
                "file": str(full_path),
                "line": 0,
                "pattern": f"path:{rel_path}",
                "context": f"Path exists: {rel_path}",
            })
    return matches
