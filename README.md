# arcana-softworks/laravel-skills

Public collection of Laravel-focused Agent Skills for Cursor, Claude Code, Codex, and compatible agents.

Install the collection (or a single skill):

```bash
npx skills add arcana-softworks/laravel-skills
npx skills add arcana-softworks/laravel-skills --list
npx skills add arcana-softworks/laravel-skills --skill laravel-new -g -a cursor -a claude-code -a codex -y
npx skills add arcana-softworks/laravel-skills --all
```

Repo: https://github.com/arcana-softworks/laravel-skills

## Skills

| Skill | Path | Summary |
|-------|------|---------|
| **laravel-new** | [`skills/laravel-new/`](skills/laravel-new/) | Scaffold a Laravel app (any kit; Inertia React default), apply sensible PHP source defaults, then Boost / Wayfinder / vite-plus (`vp`) JS tooling, anti-slop, and app CI |

More skills will land under `skills/` over time. Each skill is self-contained (`SKILL.md`, scripts, reference files).

---

## laravel-new

Scaffolds a new Laravel app (any official or community starter kit), applies **sensible Laravel source defaults**, then sets up Boost, Wayfinder (when needed), JS tooling via **vite-plus (`vp`)** when the kit ships it (oxfmt/oxlint/Vitest fallback otherwise), vendored **[anti-slop](https://github.com/dmmulroy/anti-slop)** Oxlint rules, and a generated app CI workflow.

| Agent | Typical path | Flag |
|-------|--------------|------|
| Cursor | `.cursor/skills/laravel-new` or `.agents/skills/laravel-new` | `-a cursor` |
| Claude Code | `.claude/skills/laravel-new` | `-a claude-code` |
| Codex | `.agents/skills/laravel-new` | `-a codex` |

### Plan and confirm

Before changing anything, the skill presents a numbered plan of all steps (scaffold, essentials, Boost, Wayfinder, vp/ox lint+fmt, anti-slop, Vitest, CI, package manager, commit layout). The user can accept (“go ahead”), edit options, or remove steps by id. Skips are passed through as `--skip <id>` to the scripts.

| Step id | One-line description |
|---------|----------------------|
| `scaffold` | Scaffold Laravel app with the chosen starter kit |
| `essentials` | Apply sensible PHP source defaults |
| `boost` | Install Laravel Boost and configure agents |
| `wayfinder` | Install Wayfinder when Inertia + Vite |
| `js-fmt-lint` | Configure oxfmt/oxlint via `vp` (or ox* fallback) |
| `anti-slop` | Vendor dmmulroy/anti-slop and wire into vp/oxlint |
| `vitest` | Add Vitest smoke tests and `test:js` |
| `ci` | Write `.github/workflows/ci.yml` |
| `commits` | Three-commit layout: scaffold → essentials → tooling |

Helper: `skills/laravel-new/scripts/print-plan --app my-app --kit react`.

### What it does

1. **Scaffold** — `laravel new` (or `composer create-project`). Default kit: Inertia React. Commit 1.
2. **Essentials** — self-contained PHP snippets / `apply-essentials` (strict models, immutable dates, safe console, HTTPS, Vite prefetch, test Http/Sleep nets, `make:action`, Pint). One atomic commit.
3. **Tooling** — Boost, Wayfinder on Inertia/Vite if missing, **vite-plus `vp`** JS tooling (or oxfmt/oxlint/Vitest fallback), **anti-slop**, generated app **`.github/workflows/ci.yml`**, build, PHP tests. Separate commit.

### JS standard

| Concern | npm scripts | With `vite-plus` | Fallback |
|---------|-------------|------------------|----------|
| Format | `format`, `format:check` | `vp fmt`, `vp fmt --check` | `oxfmt` |
| Lint | `lint` | `vp lint` (+ anti-slop jsPlugins) | `oxlint` (+ anti-slop) |
| Types | `types` | `vp check --no-fmt --no-lint` | `oxlint --type-aware --type-check` |
| JS tests | `test:js` | `LARAVEL_BYPASS_ENV_CHECK=1 vp test` | `vitest run` (same env prefix if `laravel-vite-plugin` is present) |
| Build | `build` | `vp build` | kit default |

On vite-plus kits, configure `fmt` / `lint` / `test` in `vite.config` (enable `lint.options.typeAware` + `typeCheck`). Do **not** add direct `oxfmt` / `oxlint` / `oxlint-tsgolint` deps or `.oxfmtrc.json` / `.oxlintrc.json`. PHP stays on Pest/PHPUnit via `php artisan test`.

**anti-slop:** vendored to `tools/oxlint/anti-slop` (skill ships `reference/anti-slop/`), pins `@oxlint/plugins` to the resolved oxlint version, merges ignores / `jsPlugins` / rules into `vite.config` `lint` (and ignores into `fmt`). Effect rules only when `effect` is a direct dependency. CI `lint` job runs the same `npm run lint` / `vp lint` path.

### Package manager

Scripts detect the JS package manager from the lockfile (`package-lock.json` → npm, `pnpm-lock.yaml` → pnpm, `yarn.lock` → yarn, `bun.lockb`/`bun.lock` → bun), defaulting to **npm** when no lockfile exists. Pass `--pm pnpm` (or `yarn`/`bun`) to `setup-tooling` / `setup-js-tooling` / `setup-anti-slop` only when the user explicitly requests that manager — that swaps conflicting lockfiles and rewrites `composer.json` scripts that invoke npm/pnpm/yarn/bun.

### Generated app CI

`setup-ci-workflow` writes `.github/workflows/ci.yml` with parallel **php** and **js** jobs (check/dry-run only). It enables Pint `--test`, PHPStan, Rector `--dry-run`, and PHPUnit/Pest via `php artisan test` when those tools exist, plus whichever of `format:check` / `lint` / `types` / `test:js` / `build` are present as package scripts. Actions use Node-24-compatible majors (`actions/checkout@v5`, `actions/setup-node@v5`, `actions/cache@v5`).

### Layout

```
skills/laravel-new/
  SKILL.md
  scripts/scaffold-app | apply-essentials | setup-tooling | setup-js-tooling
         | setup-anti-slop | setup-ci-workflow | print-plan
  scripts/lib/package-manager.sh   # lockfile PM detect + --pm switch
  scripts/lib/steps.sh             # step ids + --skip parsing
  reference/ESSENTIALS.md          # paste-ready PHP snippets
  reference/stubs/                 # pint, rector, make:action
  reference/js/                    # ox* configs (fallback) + Vitest smoke
  reference/anti-slop/             # vendored dmmulroy/anti-slop plugin copy
  reference/github/ci.yml.example  # shape of generated app CI
```

### Manual usage

```bash
SKILL=./skills/laravel-new
chmod +x "$SKILL/scripts/"*
"$SKILL/scripts/print-plan" --app my-app --kit react   # plan-and-confirm first
"$SKILL/scripts/scaffold-app" my-app --kit react --database sqlite --phpunit
cd my-app && git init -b main && git add -A && git commit -m "Scaffold Laravel application"

"$SKILL/scripts/apply-essentials" --dir .
git add -A && git commit -m "Apply sensible Laravel defaults"

"$SKILL/scripts/setup-tooling" --dir . --agents cursor,claude_code,codex
# or with skips: --skip boost --skip vitest
git add -A && git commit -m "Install Boost, Wayfinder, vite-plus/vp JS tooling, anti-slop, and project tooling"

npm run format:check && npm run lint && npm run types && npm run test:js && npm run build
php artisan test
```

## License

MIT. Upstream Laravel, Boost, Wayfinder, Oxc, Vite+/Vitest, and anti-slop remain under their respective licenses.
