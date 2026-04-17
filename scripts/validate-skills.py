#!/usr/bin/env python3
"""Validate skill structure against the rules in CLAUDE.md.

Checks every skills/<name>/SKILL.md for:
  - YAML frontmatter parses
  - `name` matches folder name
  - `description` is a non-empty string
  - total file length <= MAX_LINES

Checks .claude-plugin/marketplace.json for:
  - every listed skill path exists and has a SKILL.md
  - every skills/<name>/ folder is referenced by at least one plugin

Checks README.md for:
  - every skills/<name>/ folder is mentioned somewhere

Exits non-zero when any check fails; prints one finding per line.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
MARKETPLACE = REPO_ROOT / ".claude-plugin" / "marketplace.json"
README = REPO_ROOT / "README.md"
MAX_LINES = 500


@dataclass
class Finding:
    path: Path
    message: str

    def __str__(self) -> str:
        return f"{self.path.relative_to(REPO_ROOT)}: {self.message}"


def split_frontmatter(text: str) -> str | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        return None
    return text[4:end]


def validate_skill(skill_dir: Path) -> list[Finding]:
    findings: list[Finding] = []
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return [Finding(skill_dir, "missing SKILL.md")]

    raw = skill_md.read_text(encoding="utf-8")
    line_count = raw.count("\n") + (0 if raw.endswith("\n") else 1)
    if line_count > MAX_LINES:
        findings.append(
            Finding(skill_md, f"{line_count} lines exceeds limit of {MAX_LINES} (see CLAUDE.md)")
        )

    fm_text = split_frontmatter(raw)
    if fm_text is None:
        findings.append(Finding(skill_md, "missing YAML frontmatter (must start with '---')"))
        return findings

    try:
        fm = yaml.safe_load(fm_text)
    except yaml.YAMLError as e:
        findings.append(Finding(skill_md, f"invalid YAML frontmatter: {e}"))
        return findings

    if not isinstance(fm, dict):
        findings.append(Finding(skill_md, "frontmatter must be a YAML mapping"))
        return findings

    name = fm.get("name")
    if name != skill_dir.name:
        findings.append(
            Finding(skill_md, f"frontmatter name={name!r} does not match folder name {skill_dir.name!r}")
        )

    description = fm.get("description")
    if not isinstance(description, str) or not description.strip():
        findings.append(Finding(skill_md, "frontmatter description must be a non-empty string"))

    return findings


def validate_marketplace(skill_dirs: list[Path]) -> list[Finding]:
    findings: list[Finding] = []
    if not MARKETPLACE.is_file():
        return [Finding(MARKETPLACE, "missing marketplace.json")]

    try:
        data = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [Finding(MARKETPLACE, f"invalid JSON: {e}")]

    referenced: set[str] = set()
    for plugin in data.get("plugins", []):
        for skill_path in plugin.get("skills", []):
            resolved = (REPO_ROOT / skill_path).resolve()
            if not (resolved / "SKILL.md").is_file():
                findings.append(
                    Finding(MARKETPLACE, f"plugin {plugin.get('name')!r} references missing skill {skill_path!r}")
                )
                continue
            try:
                referenced.add(resolved.relative_to(SKILLS_DIR).parts[0])
            except ValueError:
                findings.append(
                    Finding(MARKETPLACE, f"plugin {plugin.get('name')!r} skill path {skill_path!r} is outside skills/")
                )

    for skill_dir in skill_dirs:
        if skill_dir.name not in referenced:
            findings.append(
                Finding(skill_dir, f"skill {skill_dir.name!r} is not referenced by any plugin in marketplace.json")
            )

    return findings


def validate_readme(skill_dirs: list[Path]) -> list[Finding]:
    if not README.is_file():
        return [Finding(README, "missing README.md")]
    text = README.read_text(encoding="utf-8")
    return [
        Finding(README, f"skill {s.name!r} is not mentioned in README.md")
        for s in skill_dirs
        if s.name not in text
    ]


def main() -> int:
    if not SKILLS_DIR.is_dir():
        print(f"no skills/ directory at {SKILLS_DIR}", file=sys.stderr)
        return 2

    skill_dirs = sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir())
    findings: list[Finding] = []
    for s in skill_dirs:
        findings.extend(validate_skill(s))
    findings.extend(validate_marketplace(skill_dirs))
    findings.extend(validate_readme(skill_dirs))

    if findings:
        for f in findings:
            print(f)
        print(f"\n{len(findings)} issue(s) found across {len(skill_dirs)} skill(s)", file=sys.stderr)
        return 1

    print(f"OK: {len(skill_dirs)} skill(s) validated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
