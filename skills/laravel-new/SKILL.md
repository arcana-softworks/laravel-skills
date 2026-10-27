---
name: laravel-new
description: >-
  Create a new Laravel application with any official or community starter kit
  (Inertia React default), apply sensible Laravel source defaults in one atomic
  commit, then set up Boost, Wayfinder when needed, JS tooling via vite-plus
  (`vp fmt` / `vp lint` / `vp check` / `vp test` / `vp build`) when present, with
  oxfmt/oxlint/Vitest fallback otherwise, plus vendored anti-slop Oxlint rules
  and a generated app CI workflow. Use when the user asks for a new Laravel app,
  laravel new, or scaffold Laravel.
---

# laravel-new

Create a fresh Laravel app → apply sensible source defaults → Boost / Wayfinder / vite-plus (`vp`) JS tooling + anti-slop + CI.

Install: `npx skills add arcana-softworks/laravel-skills` (optionally `--skill laravel-new -g -a cursor -a claude-code -a codex -y`).

```bash
SKILL_ROOT="…/skills/laravel-new"   # path after install
```

## Plan and confirm (mandatory — do this first)

**Before creating files, installing packages, or editing anything**, present a numbered plan of **every** change you will make, tailored to the chosen kit and package manager. Ask whether to change or remove any steps. Wait for the user’s answer (a plain “go ahead” / “yes” / “lgtm” counts as accept-all). Only then run.

Generate the plan with:

```bash
chmod +x "${SKILL_ROOT}/scripts/"*
"${SKILL_ROOT}/scripts/print-plan" --app <name> --kit react --database sqlite --phpunit
# After edits, re-print with skips, e.g.:
# "${SKILL_ROOT}/scripts/print-plan" --app <name> --kit react --skip boost --skip vitest
```

Or list the same steps yourself using the table below. Include kit, DB, PHP test runner, package manager (lockfile detect / default npm / explicit `--pm`), Boost agents, and the three-commit layout.

### Step ids

| ID | Description |
|----|-------------|
| `scaffold` | Scaffold Laravel app with the chosen starter kit |
| `essentials` | Apply sensible PHP source defaults (strict models, dates, make:action, Pint) |
| `boost` | Install Laravel Boost and configure agents |
| `wayfinder` | Install Wayfinder when Inertia + Vite (skip if already present / non-Inertia) |
| `js-fmt-lint` | Configure oxfmt/oxlint via vite-plus `vp` (or direct ox* fallback) + package scripts |
| `anti-slop` | Vendor [dmmulroy/anti-slop](https://github.com/dmmulroy/anti-slop) Oxlint rules and wire into vp/oxlint config |
| `vitest` | Add Vitest smoke tests, setup file, and `test:js` script |
| `ci` | Write `.github/workflows/ci.yml` (check/dry-run php + js jobs) |
| `commits` | Three-commit layout: scaffold → essentials → tooling |

Honour removals by passing `--skip <id>` (repeatable) to the scripts, e.g.:

```bash
"${SKILL_ROOT}/scripts/setup-tooling" --dir . --skip boost --skip vitest
```

Legacy flags `--skip-boost` / `--skip-wayfinder` still work. Package manager is a **choice** in the plan (not a skippable step): follow the kit lockfile (default npm); pass `--pm` only on explicit user request.

## Ask only what is needed

| Prompt | Default |
|--------|---------|
| App name | required |
| Starter kit | **Inertia React** (`--react`) |
| Database | `sqlite` |
| Tests (PHP) | `phpunit` |
| Boost agents | `cursor,claude_code,codex` |
| JS package manager | **Follow the kit lockfile** (see below); do not ask unless the user brings it up |

Kits: `--react` / `--vue` / `--svelte` / `--livewire` / none / `--using=<package-or-url>`.

### Package manager

Detect from the app lockfile (do not invent a preference):

| Lockfile | Manager |
|----------|---------|
| `package-lock.json` | npm |
| `pnpm-lock.yaml` | pnpm |
| `yarn.lock` | yarn |
| `bun.lockb` / `bun.lock` | bun |
| *(none)* | **npm** (default) |

Use **pnpm** (or yarn/bun) only when the user explicitly asks. Then pass `--pm pnpm` to `setup-tooling` / `setup-js-tooling` / `setup-anti-slop` (swaps conflicting lockfiles and rewrites `composer.json` scripts that call `npm`/`pnpm`/…). Otherwise keep the detected manager and do not swap lockfiles.

## Commit layout (mandatory unless `--skip commits`)

1. **Scaffold** — untouched kit  
2. **Essentials** — sensible PHP defaults only (one atomic commit)  
3. **Tooling** — Boost, Wayfinder (if needed), vite-plus/`vp` (or oxfmt/oxlint/Vitest fallback), anti-slop, app `.github/workflows/ci.yml`, deps, build, tests  

### 1) Scaffold

```bash
chmod +x "${SKILL_ROOT}/scripts/"*
"${SKILL_ROOT}/scripts/scaffold-app" my-app --kit react --database sqlite --phpunit
cd my-app
git init -b main
git add -A
git commit -m "Scaffold Laravel application (official react starter kit)"
```

### 2) Essentials (source defaults)

Paste/apply the snippets in [`reference/ESSENTIALS.md`](reference/ESSENTIALS.md), or run:

```bash
"${SKILL_ROOT}/scripts/apply-essentials" --dir .
vendor/bin/pint --parallel --test
php artisan test
php artisan make:action SkillProbe --no-interaction && rm -f app/Actions/SkillProbeAction.php
git add -A
git commit -m "Apply sensible Laravel defaults (strict models, immutable dates, make:action, Pint)"
```

Key paste targets (see reference for full blocks):

| Where | What |
|-------|------|
| `app/Providers/EssentialsServiceProvider.php` | `Model::shouldBeStrict()`, eager load, `Date::use(CarbonImmutable::class)`, prohibit destructive commands, `URL::forceHttps` in production, `Vite::usePrefetchStrategy('aggressive')`, password defaults, `Http::preventStrayRequests` + `Sleep::fake` in unit tests |
| `bootstrap/providers.php` | Register that provider |
| `app/Console/Commands/MakeActionCommand.php` + `stubs/action.stub` | From `reference/stubs/` |
| `pint.json` / optional `rector.php` | From `reference/stubs/` |

### 3) Tooling (Boost + Wayfinder + JS + anti-slop + CI)

```bash
"${SKILL_ROOT}/scripts/setup-tooling" --dir . --agents cursor,claude_code,codex
# With skips from plan-and-confirm, e.g.:
# "${SKILL_ROOT}/scripts/setup-tooling" --dir . --agents cursor,claude_code,codex --skip boost --skip vitest
# Only if the user explicitly requested pnpm (or yarn/bun):
# "${SKILL_ROOT}/scripts/setup-tooling" --dir . --agents cursor,claude_code,codex --pm pnpm
git add -A
git commit -m "Install Boost, Wayfinder (if needed), vite-plus/vp JS tooling, anti-slop, and project tooling"
```

`setup-tooling` runs, in order (honouring `--skip`): Boost → Wayfinder → `setup-js-tooling` (`js-fmt-lint` / `vitest`) → `setup-anti-slop` → `setup-ci-workflow` → migrate / build / format:check / lint / types / test:js / PHP tests.

JS standard — **prefer vite-plus** on React/Vue/Svelte kits (config in `vite.config` `fmt` / `lint` / `test`; no separate `.oxfmtrc` / `.oxlintrc`, no direct `oxfmt`/`oxlint` deps):

| Concern | Script | vite-plus kits | Fallback (e.g. Livewire) |
|---------|--------|----------------|--------------------------|
| Format | `format` / `format:check` | `vp fmt` / `vp fmt --check` | `oxfmt` / `oxfmt --check` |
| Lint | `lint` | `vp lint` (type-aware via config) | `oxlint` |
| Types | `types` | `vp check --no-fmt --no-lint` | `oxlint --type-aware --type-check` |
| JS tests | `test:js` | `LARAVEL_BYPASS_ENV_CHECK=1 vp test` | `vitest run` (same env prefix if `laravel-vite-plugin` is present) |
| Build | `build` | `vp build` | kit default |

#### anti-slop

Vendored from [dmmulroy/anti-slop](https://github.com/dmmulroy/anti-slop) (no npm package — copy `src/` → `tools/oxlint/anti-slop`). Skill ships a pinned copy under `reference/anti-slop/` (see `UPSTREAM.md`). Install steps (normal package install + config only):

1. Copy plugin → `tools/oxlint/anti-slop/`
2. Pin `@oxlint/plugins@<exact oxlint version>` as a devDependency (match installed oxlint, including vite-plus’s nested copy)
3. Merge `ignorePatterns`, `jsPlugins`, and all generic `rules` into `vite.config` `lint` (and the same ignores into `fmt.ignorePatterns`), or into `.oxlintrc.json` on the oxlint fallback path
4. Enable Effect plugin/rules only when `effect` is a **direct** dependency
5. Run `vp lint --fix` (or `oxlint --fix`) → formatter → lint again; fix owned source or relax specific rules sensibly — do not blanket-disable
6. On Inertia kits, add `// SAFETY:` comments for known starter-kit assertions and apply these **narrow** relaxations (report them in the summary):
   - `anti-slop/no-unsafe-dictionary-type=off` — Inertia `sharedPageProps` / `User` open index signatures
   - `anti-slop/no-runtime-typeof=off` — Inertia `href` string|object unions in kit helpers

**Oddity flagged:** anti-slop’s source imports `@oxlint/plugins` and its install skill installs that package. vite-plus docs prefer `vite-plus/lint/plugins` imports; we follow anti-slop’s instructions and pin `@oxlint/plugins` exactly to the resolved oxlint version. Do not run anti-slop’s unrelated scripts beyond the documented copy + config.

#### Generated app CI

`setup-tooling` also writes **`.github/workflows/ci.yml`** via `setup-ci-workflow` (see `reference/github/ci.yml.example`): parallel `php` and `js` jobs on `push` to `main` and `pull_request`. Check/dry-run only (`pint --test`, PHPStan, Rector `--dry-run` when installed, `php artisan test`, plus present JS scripts including `lint`, which covers anti-slop). Skips missing tools; uses the detected package manager and PHP version from `composer.json`.

### 4) Summarize for the user

App path, kit, commits (or skipped), PHP defaults present, Boost/Wayfinder/JS tooling/anti-slop/CI status, any anti-slop rules relaxed and why, PHP + `test:js` / format / lint / types / build results.

## Rules

- **Always plan-and-confirm before changing anything**; honour `--skip` / user removals.
- Never squash essentials into the scaffold commit (unless `commits` was skipped by the user).
- Prefer skill scripts + `reference/ESSENTIALS.md` snippets over inventing config.
- Keep PHP tests (`php artisan test`) and JS tests (`npm run test:js`) separate.
- Prefer `vp` whenever `vite-plus` is present; only install oxfmt/oxlint/Vitest directly as a fallback.
- Follow the kit package manager from the lockfile (default npm); switch to pnpm/yarn/bun only on explicit user request (`--pm`).
- Generated app CI must stay check/dry-run only (never write or auto-fix).
- anti-slop: vendor + `@oxlint/plugins` pin + config merge only; report oddities; keep lint green by fixing or narrowly relaxing rules.
