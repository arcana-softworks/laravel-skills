# laravel-new-skill

Public Agent Skill that scaffolds a new Laravel app (any official or community starter kit), applies [Nuno Maduro’s Essentials](https://github.com/nunomaduro/essentials) as **plain source changes** (never `composer require nunomaduro/essentials`), then sets up Laravel Boost and Wayfinder when appropriate.

## Install

```bash
npx skills add arcana-softworks/laravel-new-skill
```

That discovers `skills/laravel-new/SKILL.md` and installs the skill for your coding agents. Useful variants:

```bash
# List skills in this repo
npx skills add arcana-softworks/laravel-new-skill --list

# Install only this skill, globally, for specific agents
npx skills add arcana-softworks/laravel-new-skill --skill laravel-new -g -a cursor -a claude-code -a codex -y

# All agents, non-interactive
npx skills add arcana-softworks/laravel-new-skill --all
```

### Cursor / Claude Code / Codex

| Agent | Typical project path after `npx skills add` | Notes |
|-------|-----------------------------------------------|--------|
| **Cursor** | `.cursor/skills/laravel-new` or shared `.agents/skills/laravel-new` | Also works with `-a cursor` |
| **Claude Code** | `.claude/skills/laravel-new` | `-a claude-code` |
| **Codex** | `.agents/skills/laravel-new` | `-a codex` |

Use `-g` to install into your user-level skills directory instead of the current project. After install, ask the agent for a “new Laravel app” (or similar); it should load **laravel-new**.

Equivalent with GitHub CLI (if you prefer):

```bash
gh skill install arcana-softworks/laravel-new-skill laravel-new --agent cursor
```

## What the skill does

1. **Scaffold** with `laravel new` (falls back to `composer create-project`) — default kit **Inertia React**; also Vue, Svelte, Livewire, none, or any `--using=` package/URL. Commit 1 = untouched scaffold.
2. **Apply Essentials as source** via `scripts/apply-essentials` (dedicated provider + `make:action` + Pint/Rector stubs). Re-checks the live Essentials README so new recommendations are not missed silently. Commit 2 = one atomic Essentials commit.
3. **Tooling** via `scripts/setup-tooling`: Laravel Boost (`boost:install --no-interaction`), Wayfinder when the stack is Inertia/Vite and it is not already present, composer/npm install, key, sqlite migrate, build, tests. Separate commit(s) after Essentials.

## Layout

```
skills/laravel-new/
  SKILL.md                 # agent instructions
  scripts/
    scaffold-app           # laravel new / composer create-project
    apply-essentials       # idempotent Essentials source translation
    setup-tooling          # Boost, Wayfinder, deps, build, test
  reference/
    ESSENTIALS.md          # feature → source mapping
    stubs/                 # pint, rector, make:action, action.stub
```

## Manual script usage

```bash
git clone https://github.com/arcana-softworks/laravel-new-skill.git
SKILL=./laravel-new-skill/skills/laravel-new
chmod +x "$SKILL/scripts/"*

"$SKILL/scripts/scaffold-app" my-app --kit react --database sqlite --phpunit
cd my-app && git init -b main && git add -A && git commit -m "Scaffold Laravel application"

"$SKILL/scripts/apply-essentials" --dir .
git add -A && git commit -m "Apply Nuno Maduro Essentials recommendations as source (not nunomaduro/essentials)"

"$SKILL/scripts/setup-tooling" --dir . --agents cursor,claude_code,codex
git add -A && git commit -m "Install Laravel Boost, Wayfinder (if needed), and project tooling"
```

## License

MIT. Upstream Laravel, Essentials, Boost, and Wayfinder remain under their respective licenses.
