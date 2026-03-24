# Unhosted Web Skills

Agent skills repository for unhosted web application development, hosted on skills.sh.

## Structure

Each skill lives in `skills/<skill-name>/` with a required `SKILL.md` file.
Optional subdirectories: `references/`, `scripts/`, `assets/`.

## SKILL.md Requirements

- YAML frontmatter: `name` (must match folder name) and `description` are required
- Optional: `license`, `compatibility`, `metadata`
- Keep under 500 lines; split into `references/` if longer
- Include practical examples, not just API docs

## Adding a New Skill

1. Create `skills/<skill-name>/SKILL.md`
2. Add the skill path to `.claude-plugin/marketplace.json` under the appropriate plugin
3. Update the skills table in `README.md`
