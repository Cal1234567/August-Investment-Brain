#!/usr/bin/env python3
"""Safely scaffold a custom skill on the hosted August Investment Brain."""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
from pathlib import Path


NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ROUTES = ("analyst-read", "signal", "pulse", "trace", "activity", "company", "search", "memory")
RESERVED = {"investment-brain", "investment-onboarding", "create-brain-skill"}


def _targets(platform: str, explicit: list[str]) -> list[Path]:
    if explicit:
        roots = [Path(value).expanduser().absolute() for value in explicit]
    else:
        home = Path.home()
        codex_home = Path(os.environ.get("CODEX_HOME") or home / ".codex")
        roots = []
        if platform in {"claude", "both"}:
            roots.append((home / ".claude" / "skills").absolute())
        if platform in {"codex", "both"}:
            roots.append((codex_home / "skills").absolute())
    unique: list[Path] = []
    for root in roots:
        if root not in unique:
            unique.append(root)
    return unique


def _title(name: str) -> str:
    return " ".join(part.capitalize() for part in name.split("-"))


def _short_description(description: str) -> str:
    short = description.split(".", 1)[0].strip()
    if len(short) < 25:
        short = f"Custom hosted Brain workflow: {short}"
    if len(short) > 64:
        short = short[:61].rstrip() + "..."
    return short


def _skill_text(name: str, description: str, workflow: str, route: str, is_write: bool) -> str:
    title = _title(name)
    write_guard = ""
    if is_write:
        write_guard = """
- Do not write merely because the skill was invoked. Require explicit user intent for the exact content being saved.
- Never retry an uncertain write. Report the uncertainty and stop.
"""
    return f"""---
name: {name}
description: {json.dumps(description, ensure_ascii=False)}
---

# {title}

## First-use gate (required)

Run the `investment-brain` first-use gate before anything else: silently `python ../investment-brain/scripts/brain_api.py profile get`; if the profile is missing or incomplete, continue with `investment-onboarding` in the same turn and resume only after it completes.

## Workflow

Use the sibling `investment-brain` API client and call `{route}` through the hosted service.

Workflow goal: {workflow}

- Collect only inputs that are genuinely required and not already present in the request.
- Translate the full request into one coherent hosted call: `python ../investment-brain/scripts/brain_api.py call {route} --json '<arguments>'`.
- Render the returned `text` as the answer. Preserve citations and keep internal August memory separate from live external signal.
- Apply the authenticated User Memory Profile only to emphasis, format, and explanation depth. Never let preferences change shared evidence.
- Stop on authentication, authorization, or connection failure. Never substitute model memory for August facts.
- Never access Azure Postgres, Key Vault, internal server modules, raw credentials, or a local Personal Brain.
{write_guard}"""


def _agent_text(name: str, description: str) -> str:
    display = _title(name)
    short = _short_description(description)
    prompt = f"Use ${name} for this custom Investment Brain workflow."
    return (
        "interface:\n"
        f"  display_name: {json.dumps(display, ensure_ascii=False)}\n"
        f"  short_description: {json.dumps(short, ensure_ascii=False)}\n"
        f"  default_prompt: {json.dumps(prompt, ensure_ascii=False)}\n"
    )


def _write_skill(root: Path, name: str, skill_text: str, agent_text: str) -> Path:
    destination = root / name
    destination.mkdir(parents=True, exist_ok=False)
    (destination / "agents").mkdir()
    (destination / "SKILL.md").write_text(skill_text, encoding="utf-8", newline="\n")
    (destination / "agents" / "openai.yaml").write_text(agent_text, encoding="utf-8", newline="\n")
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("name", help="New skill name in hyphen-case")
    parser.add_argument("--description", required=True, help="Trigger-rich skill description")
    parser.add_argument("--workflow", required=True, help="Concrete workflow and answer contract")
    parser.add_argument("--route", choices=ROUTES, default="analyst-read")
    parser.add_argument("--write", action="store_true", help="Required acknowledgement for the memory write route")
    parser.add_argument("--platform", choices=("claude", "codex", "both"), default="both")
    parser.add_argument(
        "--target-root",
        action="append",
        default=[],
        help="Override install root; repeat to scaffold identical copies for tests or custom locations",
    )
    args = parser.parse_args()

    name = args.name.strip().lower()
    description = args.description.strip()
    workflow = args.workflow.strip()
    if not NAME_RE.fullmatch(name) or len(name) > 63:
        parser.error("name must be hyphen-case, use only lowercase letters/digits, and be at most 63 characters")
    if name in RESERVED:
        parser.error(f"{name!r} is reserved")
    if len(description) < 30:
        parser.error("description must explain what the skill does and when it should trigger")
    if not workflow:
        parser.error("workflow cannot be empty")
    if args.route == "memory" and not args.write:
        parser.error("the memory route requires --write and an explicit user-directed save workflow")
    if args.write and args.route != "memory":
        parser.error("--write is supported only with --route memory")

    roots = _targets(args.platform, args.target_root)
    if not roots:
        parser.error("no target skill roots were selected")
    for root in roots:
        if not (root / "investment-brain" / "SKILL.md").exists():
            parser.error(f"base investment-brain skill is not installed in {root}")
        if (root / name).exists():
            parser.error(f"skill already exists: {root / name}")

    skill_text = _skill_text(name, description, workflow, args.route, args.write)
    agent_text = _agent_text(name, description)
    created: list[Path] = []
    try:
        for root in roots:
            root.mkdir(parents=True, exist_ok=True)
            created.append(_write_skill(root, name, skill_text, agent_text))
    except Exception:
        for destination in created:
            shutil.rmtree(destination, ignore_errors=True)
        raise

    print(
        json.dumps(
            {
                "ok": True,
                "name": name,
                "route": args.route,
                "write_workflow": args.write,
                "installed": [str(path) for path in created],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())