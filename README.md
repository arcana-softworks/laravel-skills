# laravel-new-skill

Public Agent Skill that scaffolds a new Laravel app (any official or community starter kit), applies **sensible Laravel source defaults**, then sets up Boost, Wayfinder (when needed), and JS tooling via **vite-plus (`vp`)** when the kit ships it (oxfmt/oxlint/Vitest fallback otherwise).

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
3. **Tooling** — Boost, Wayfinder on Inertia/Vite if missing, **vite-plus `vp`** JS tooling (or oxfmt/oxlint/Vitest fallback), build, PHP tests. Separate commit.

### JS standard

| Concern | npm scripts | With `vite-plus` | Fallback |
|---------|-------------|------------------|----------|
| Format | `format`, `format:check` | `vp fmt`, `vp fmt --check` | `oxfmt` |
| Lint | `lint` | `vp lint` | `oxlint` |
| Types | `types` | `vp check --no-fmt --no-lint` | `oxlint --type-aware --type-check` |
| JS tests | `test:js` | `vp test` | `vitest run` |
| Build | `build` | `vp build` | kit default |

On vite-plus kits, configure `fmt` / `lint` / `test` in `vite.config` (enable `lint.options.typeAware` + `typeCheck`). Do **not** add direct `oxfmt` / `oxlint` / `oxlint-tsgolint` deps or `.oxfmtrc.json` / `.oxlintrc.json`. PHP stays on Pest/PHPUnit via `php artisan test`.

## Layout

```
skills/laravel-new/
  SKILL.md
  scripts/scaffold-app | apply-essentials | setup-tooling | setup-js-tooling
  reference/ESSENTIALS.md          # paste-ready PHP snippets
  reference/stubs/                 # pint, rector, make:action
  reference/js/                    # ox* configs (fallback) + Vitest smoke
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
git add -A && git commit -m "Install Boost, Wayfinder, vite-plus/vp JS tooling, and project tooling"

npm run format:check && npm run lint && npm run types && npm run test:js && npm run build
php artisan test
```

## License

MIT. Upstream Laravel, Boost, Wayfinder, Oxc, and Vite+/Vitest remain under their respective licenses.
