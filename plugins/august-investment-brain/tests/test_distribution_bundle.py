from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = json.loads((ROOT / "bundle.json").read_text(encoding="utf-8"))
SKILLS = ROOT / "skills"

forbidden_names = {"builder", "thinker", "writing", "personal-brain", "codex-delegation"}
assert not forbidden_names.intersection(BUNDLE["skills"])
expected_skills = [
    "investment-brain",
    "investment-onboarding",
    "august-analyst",
    "log-decision",
    "brain-feedback",
    "capture-the-book",
]
assert BUNDLE["skills"] == expected_skills, f"unexpected active skill set: {BUNDLE['skills']}"
assert not set(BUNDLE["skills"]).intersection(BUNDLE["retired_skills"]), "active and retired skills overlap"
skill_directories = sorted(path.name for path in SKILLS.iterdir() if (path / "SKILL.md").exists())
assert skill_directories == sorted(expected_skills), f"orphan or missing skill directories: {skill_directories}"

for name in BUNDLE["skills"]:
    folder = SKILLS / name
    skill = folder / "SKILL.md"
    agent = folder / "agents" / "openai.yaml"
    assert skill.exists(), f"missing {skill}"
    assert agent.exists(), f"missing {agent}"
    text = skill.read_text(encoding="utf-8")
    assert re.match(r"^---\nname: [a-z0-9-]+\ndescription:", text), f"invalid frontmatter: {name}"
    if name == "investment-onboarding":
        assert "profile get" in text, "onboarding must authenticate before collecting answers"
    else:
        assert "## First-use gate (required)" in text, f"missing first-use gate: {name}"
        assert "profile get" in text and "investment-onboarding" in text, f"incomplete first-use gate: {name}"

for path in ROOT.rglob("*"):
    if "tests" in path.parts:
        continue
    if not path.is_file() or path.suffix.lower() not in {".md", ".py", ".ps1", ".json", ".yaml"}:
        continue
    text = path.read_text(encoding="utf-8")
    for token in ("CalShannon", "C:\\Users\\", ".brain-env.json", "AZURE_PG_", "SUPABASE_", "mcp__"):
        assert token not in text, f"private/server token {token!r} in {path}"

client = (SKILLS / "investment-brain" / "scripts" / "brain_api.py").read_text(encoding="utf-8")
assert 'config.get("api_key")' not in client and '"api_key":' not in client, "client must not embed an API key"
assert "ONBOARDING_REQUIRED" in client and "_guarded_call" in client, "shared client must enforce onboarding for every route"
assert "onboarding-reset.pending" in client and '"reset"' in client, "client must support a safe redo-onboarding reset"
assert "/profiles/" not in "\n".join(p.read_text(encoding="utf-8") for p in SKILLS.rglob("SKILL.md"))
core_skill = (SKILLS / 'investment-brain' / 'SKILL.md').read_text(encoding='utf-8')
assert 'profile get' in core_skill and 'answer_preferences' in core_skill, 'front door must progressively load the authenticated profile'
assert 'immediately continue with the `investment-onboarding` workflow in the same turn' in core_skill, 'missing/incomplete profiles must enter onboarding automatically'
assert 'Treat a setup-only request' in core_skill and 'Do not show a capability menu' in core_skill, 'first-use requests must ask the first onboarding question instead of showing a menu'
print(f"PASS: portable distribution bundle with {len(BUNDLE['skills'])} skills")
