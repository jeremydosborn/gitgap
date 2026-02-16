#!/usr/bin/env python3
"""
tufcheck - Supply chain security mechanism scanner with anonymous research survey.

Scans repositories for signs of:
- gittuf (source protection)
- in-toto (build attestation)
- SBOM (software bill of materials)
- TUF (secure distribution)

Optionally collects anonymous, encrypted survey responses to measure
the gap between public repo visibility and internal implementation.

Usage:
    tufcheck scan /path/to/repo
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from core import gittuf, intoto, sbom, tuf
from survey import collect, bundle, submit

def check_repo_freshness(repo_path: Path) -> dict:
    """Check if local clone is up to date with remote."""
    try:
        subprocess.run(
            ["git", "fetch", "--dry-run"],
            cwd=repo_path,
            capture_output=True,
            timeout=10
        )
        
        local = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_path,
            capture_output=True,
            text=True
        ).stdout.strip()
        
        remote = subprocess.run(
            ["git", "rev-parse", "@{u}"],
            cwd=repo_path,
            capture_output=True,
            text=True
        ).stdout.strip()
        
        if local != remote:
            return {"fresh": False, "local": local[:8], "remote": remote[:8]}
        return {"fresh": True}
        
    except Exception:
        return {"fresh": None, "reason": "Could not check"}

def scan_repo(repo_path: str) -> dict:
    repo_path = Path(repo_path).resolve()
    
    if not repo_path.exists():
        print(f"Error: {repo_path} does not exist", file=sys.stderr)
        sys.exit(1)
    
    scanner_dir = Path(__file__).parent.resolve()
    if repo_path == scanner_dir:
        print(f"Error: Cannot scan the scanner itself", file=sys.stderr)
        sys.exit(1)
    
    project_name = repo_path.name
    
    results = {
        "project": project_name,
        "gittuf": gittuf.analyze(repo_path),
        "intoto": intoto.analyze(repo_path),
        "sbom": sbom.analyze(repo_path),
        "tuf": tuf.analyze(repo_path),
    }
    
    results["summary"] = {
        "gittuf": results["gittuf"]["found"],
        "intoto": results["intoto"]["found"],
        "sbom": results["sbom"]["found"],
        "tuf": results["tuf"]["found"],
        "scan_score": sum([
            results["gittuf"]["found"],
            results["intoto"]["found"],
            results["sbom"]["found"],
            results["tuf"]["found"],
        ]),
        "max_score": 4
    }
    
    return results


def print_results(results: dict):
    print("\n" + "=" * 60)
    print(f"TUFCHECK RESULTS: {results['project']}")
    print("=" * 60)
    
    for check in ["gittuf", "intoto", "sbom", "tuf"]:
        data = results[check]
        status = "✓ FOUND" if data["found"] else "✗ NOT FOUND"
        print(f"\n{check.upper()}: {status}")
        
        if data["found"]:
            if data["matches"]:
                print(f"  Matches ({len(data['matches'])} total):")
                for m in data["matches"][:3]:
                    rel_path = m["file"].split(results["project"])[-1]
                    print(f"    - {rel_path}:{m['line']}")
                    print(f"      {m['context'][:60]}...")
                if len(data["matches"]) > 3:
                    print(f"    ... and {len(data['matches']) - 3} more")
    
    print("\n" + "-" * 60)
    s = results["summary"]
    print(f"SCAN SCORE: {s['scan_score']}/{s['max_score']}")
    print(f"  gittuf:  {'Yes' if s['gittuf'] else 'No'}")
    print(f"  in-toto: {'Yes' if s['intoto'] else 'No'}")
    print(f"  SBOM:    {'Yes' if s['sbom'] else 'No'}")
    print(f"  TUF:     {'Yes' if s['tuf'] else 'No'}")
    print()


def save_results(results: dict) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = Path(__file__).parent / "results" / timestamp
    results_dir.mkdir(parents=True, exist_ok=True)
    output_path = results_dir / f"{results['project']}.json"
    
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    
    return output_path


def prompt_survey() -> bool:
    print("\n" + "=" * 60)
    print("ANONYMOUS RESEARCH SURVEY")
    print("=" * 60)
    print("""
This scan is part of research on supply chain security adoption.

You can help by answering ONE anonymous question about how your
internal implementation compares to what's publicly visible.

Your response:
  - Contains NO identifying information
  - No repo name, no hash, no category, no timestamp
  - Is encrypted client-side before transmission
  - Cannot be linked back to you or this repository
""")
    
    response = input("Participate in research survey? [y/N]: ").strip().lower()
    return response in ('y', 'yes')


def run_survey():
    score = collect.ask_question()
    
    if score is None:
        print("\nSurvey skipped.")
        return
    
    payload = {"v": 1, "internal_score": score}
    
    print("\nPreparing submission...")
    encrypted_shares = bundle.prepare_submission(payload)
    
    print(f"  ✓ Payload encrypted with research public key")
    print(f"  ✓ Split into {len(encrypted_shares)} shares (Shamir 2-of-3)")
    print(f"  ✓ Padded to fixed size (no length fingerprinting)")
    
    submit.submit_shares(encrypted_shares)


def main():
    parser = argparse.ArgumentParser(
        description="Scan repository for supply chain security mechanisms"
    )
    parser.add_argument("repo", help="Path to repository")
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress output")
    
    args = parser.parse_args()
    
    results = scan_repo(args.repo)
    output_path = save_results(results)
    
    if not args.quiet:
        print_results(results)
        print(f"Results saved to: {output_path}")
        
        if prompt_survey():
            run_survey()


if __name__ == "__main__":
    main()