# skills

Agent skills for development, by Arcana Softworks. Works with Cursor, Claude Code, Codex and other agents that support the [skills](https://skills.sh) format.

## Install

```bash
# list what's available
npx skills add arcana-softworks/skills --list

# install one skill globally
npx skills add arcana-softworks/skills --skill <skill-name> -g -a cursor -a claude-code -a codex -y

# install everything
npx skills add arcana-softworks/skills --all
```

## Skills

| Skill | Summary |
|-------|---------|
| [`laravel-new`](skills/laravel-new/) | Scaffold a new Laravel app with any starter kit, then apply sensible defaults, tooling, CI and Docker |

Each skill lives in its own directory under `skills/` and is self-contained: a `SKILL.md`, plus any scripts and reference files it needs. Skill-specific docs are in a `README.md` inside the skill's directory.

## Adding a skill

1. Create `skills/<skill-name>/SKILL.md` with `name` and `description` frontmatter.
2. Keep everything the skill needs inside its directory.
3. Add a row to the table above.

## License

MIT. Third-party tools that skills install or reference remain under their own licenses.
