"""SBOM analyzer - software bill of materials."""

from pathlib import Path
from typing import Dict, Any
from .base import analyze_repo, check_paths_exist

# Generation tools (not just format mentions)
PATTERNS = [
    r"\bsbom\b",
    r"\bsyft\b",
    r"\bsbomtool\b",
    r"cyclonedx",
    r"\bspdx\b",
]

INDICATOR_PATHS = ["sbom", "sbom.json"]


def analyze(repo_path: Path) -> Dict[str, Any]:
    result = analyze_repo(repo_path, PATTERNS)
    result["matches"].extend(check_paths_exist(repo_path, INDICATOR_PATHS))
    
    # Look for SBOM files
    sbom_files = []
    for pattern in ["*sbom*.json", "*cyclonedx*.json", "*spdx*.json"]:
        sbom_files.extend(list(repo_path.rglob(pattern))[:5])
    
    for sf in sbom_files:
        result["matches"].append({
            "file": str(sf),
            "line": 0,
            "pattern": "sbom_file",
            "context": f"SBOM file: {sf.name}",
        })
    
    result["found"] = len(result["matches"]) > 0
        
    result["completeness"] = None
    if result["found"]:
        generates = any(
            "sbomtool" in m["context"].lower() or 
            "syft" in m["context"].lower() or
            "generate" in m["context"].lower()
            for m in result["matches"]
        )
        publishes = any(
            "upload" in m["context"].lower() or
            "publish" in m["context"].lower() or
            "s3" in m["context"].lower() or
            "registry" in m["context"].lower()
            for m in result["matches"]
        )
        result["completeness"] = {
            "generates": generates,
            "stores_in_repo": len(sbom_files) > 0,
            "publishes_external": publishes,
        }

    return result
