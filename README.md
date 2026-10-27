# laravel-new-skill

Public Agent Skill that scaffolds a new Laravel app (any official or community starter kit), applies **sensible Laravel source defaults**, then sets up Boost, Wayfinder (when needed), and JS tooling (**oxfmt**, **oxlint** type-aware, **Jest**).

## Install

```bash
npx skills add arcana-softworks/laravel-new-skill
```

```bash
npx skills add arcana-softworks/laravel-new-skill --list
npx skills add arcana-softworks/laravel-new-skill --skill laravel-new -g -a cursor -a claude-code -a codex -y
npx skills add arcana-softworks/laravel-new-skill --all
```

| Agent | Typical path | Flag |
|-------|--------------|------|
| Cursor | `.cursor/skills/laravel-new` or `.agents/skills/laravel-new` | `-a cursor` |
| Claude Code | `.claude/skills/laravel-new` | `-a claude-code` |
| Codex | `.agents/skills/laravel-new` | `-a codex` |

## What the skill does

1. **Scaffold** — `laravel new` (or `composer create-project`). Default kit: Inertia React. Commit 1.
2. **Essentials** — self-contained PHP snippets / `apply-essentials` (strict models, immutable dates, safe console, HTTPS, Vite prefetch, test Http/Sleep nets, `make:action`, Pint). One atomic commit.
3. **Tooling** — Boost, Wayfinder on Inertia/Vite if missing, **oxfmt** + **oxlint** (+ **oxlint-tsgolint**), **Jest** (`test:js`), build, PHP tests. Separate commit.

### JS standard

| Concern | Tool | npm scripts |
|---------|------|-------------|
| Format | oxfmt | `format`, `format:check` |
| Lint + TS | oxlint (type-aware / type-check via oxlint-tsgolint) | `lint`, `types` |
| JS tests | Jest (+ `@swc/jest`, jsdom; React Testing Library) | `test:js` |

Replaces Prettier/ESLint configs and `vp check` / `tsc --noEmit` script aliases. Does **not** use Vitest as the app test runner. PHP stays on Pest/PHPUnit via `php artisan test`.

## Layout

```
skills/laravel-new/
  SKILL.md
  scripts/scaffold-app | apply-essentials | setup-tooling | setup-js-tooling
  reference/ESSENTIALS.md          # paste-ready PHP snippets
  reference/stubs/                 # pint, rector, make:action
  reference/js/                    # .oxfmtrc.json, .oxlintrc.json, Jest smoke
```

## Manual usage

```bash
SKILL=./skills/laravel-new
chmod +x "$SKILL/scripts/"*
"$SKILL/scripts/scaffold-app" my-app --kit react --database sqlite --phpunit
cd my-app && git init -b main && git add -A && git commit -m "Scaffold Laravel application"

"$SKILL/scripts/apply-essentials" --dir .
git add -A && git commit -m "Apply sensible Laravel defaults"

"$SKILL/scripts/setup-tooling" --dir . --agents cursor,claude_code,codex
git add -A && git commit -m "Install Boost, Wayfinder, oxfmt/oxlint/Jest, and project tooling"

npm run format:check && npm run lint && npm run types && npm run test:js && npm run build
php artisan test
```

## License

MIT. Upstream Laravel, Boost, Wayfinder, and Oxc tools remain under their respective licenses.
