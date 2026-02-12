"""gittuf analyzer - source repository protection."""

from pathlib import Path
from typing import Dict, Any
from .base import analyze_repo, check_paths_exist
import subprocess

PATTERNS = [
    r"\bgittuf\b",
]

INDICATOR_PATHS = [".gittuf"]


def analyze(repo_path: Path) -> Dict[str, Any]:
    result = analyze_repo(repo_path, PATTERNS)
    result["matches"].extend(check_paths_exist(repo_path, INDICATOR_PATHS))
    
    # Check .git/refs/gittuf
    git_gittuf = repo_path / ".git" / "refs" / "gittuf"
    if git_gittuf.exists():
        result["matches"].append({
            "file": str(git_gittuf),
            "line": 0,
            "pattern": "refs/gittuf",
            "context": "gittuf refs in .git",
        })
    # Also check via git show-ref (catches packed refs)
    try:
        git_result = subprocess.run(
            ["git", "show-ref"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        if "refs/gittuf" in git_result.stdout:
            result["matches"].append({
                "file": str(repo_path / ".git"),
                "line": 0,
                "pattern": "refs/gittuf",
                "context": "gittuf refs found via git show-ref",
            })
    except Exception:
        pass
    
    result["found"] = len(result["matches"]) > 0
    return result
