from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).absolute().parents[1]
SCRIPT = ROOT / "skills" / "create-brain-skill" / "scripts" / "scaffold_brain_skill.py"


def make_root(parent: Path, name: str) -> Path:
    root = parent / name
    base = root / "investment-brain"
    base.mkdir(parents=True)
    (base / "SKILL.md").write_text("---\nname: investment-brain\ndescription: test\n---\n", encoding="utf-8")
    return root


with tempfile.TemporaryDirectory(dir=ROOT) as temporary:
    temp = Path(temporary)
    claude = make_root(temp, "claude-skills")
    codex = make_root(temp, "codex-skills")
    command = [
        sys.executable,
        str(SCRIPT),
        "portfolio-concentration-check",
        "--description",
        "Check portfolio concentration against August memory. Use for overlap, clustering, or exposure review.",
        "--workflow",
        "Identify supported shared exposures, cite the evidence, and end with the top concentration questions.",
        "--route",
        "analyst-read",
        "--target-root",
        str(claude),
        "--target-root",
        str(codex),
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    assert '"ok": true' in result.stdout.lower()

    for root in (claude, codex):
        skill = root / "portfolio-concentration-check" / "SKILL.md"
        agent = root / "portfolio-concentration-check" / "agents" / "openai.yaml"
        assert skill.exists() and agent.exists()
        text = skill.read_text(encoding="utf-8")
        assert "## First-use gate (required)" in text
        assert "profile get" in text and "investment-onboarding" in text
        assert "call analyst-read" in text
        assert "Azure Postgres" in text and "Never access" in text
        assert "$portfolio-concentration-check" in agent.read_text(encoding="utf-8")

    duplicate = subprocess.run(command, capture_output=True, text=True)
    assert duplicate.returncode != 0 and "already exists" in duplicate.stderr

    write_root = make_root(temp, "write-skills")
    unsafe_write = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "save-investment-decision",
            "--description",
            "Save a user-approved investment decision to the hosted Brain when explicitly requested.",
            "--workflow",
            "Save only the exact decision the user approved.",
            "--route",
            "memory",
            "--target-root",
            str(write_root),
        ],
        capture_output=True,
        text=True,
    )
    assert unsafe_write.returncode != 0 and "requires --write" in unsafe_write.stderr

    safe_write = subprocess.run(unsafe_write.args + ["--write"], capture_output=True, text=True, check=True)
    write_text = (write_root / "save-investment-decision" / "SKILL.md").read_text(encoding="utf-8")
    assert '"write_workflow": true' in safe_write.stdout.lower()
    assert "Require explicit user intent" in write_text
    assert "Never retry an uncertain write" in write_text

print("PASS: custom Brain skills scaffold safely for Claude and Codex")