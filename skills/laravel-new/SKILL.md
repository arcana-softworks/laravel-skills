---
name: laravel-new
description: >-
  Create a new Laravel application with any official or community starter kit
  (Inertia React default), apply sensible Laravel source defaults in one atomic
  commit, then set up Boost, Wayfinder when needed, and JS tooling via vite-plus
  (`vp fmt` / `vp lint` / `vp check` / `vp test` / `vp build`) when present, with
  oxfmt/oxlint/Vitest fallback otherwise. Use when the user asks for a new
  Laravel app, laravel new, or scaffold Laravel.
---

# laravel-new

Create a fresh Laravel app → apply sensible source defaults → Boost / Wayfinder / vite-plus (`vp`) JS tooling.

Install: `npx skills add arcana-softworks/laravel-new-skill` (optionally `--skill laravel-new -g -a cursor -a claude-code -a codex -y`).

```bash
SKILL_ROOT="…/skills/laravel-new"   # path after install
```

## Ask only what is needed

| Prompt | Default |
|--------|---------|
| App name | required |
| Starter kit | **Inertia React** (`--react`) |
| Database | `sqlite` |
| Tests (PHP) | `phpunit` |
| Boost agents | `cursor,claude_code,codex` |

Kits: `--react` / `--vue` / `--svelte` / `--livewire` / none / `--using=<package-or-url>`.

## Commit layout (mandatory)

1. **Scaffold** — untouched kit  
2. **Essentials** — sensible PHP defaults only (one atomic commit)  
3. **Tooling** — Boost, Wayfinder (if needed), vite-plus/`vp` (or oxfmt/oxlint/Vitest fallback), deps, build, tests  

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

### 3) Tooling (Boost + Wayfinder + JS)

```bash
"${SKILL_ROOT}/scripts/setup-tooling" --dir . --agents cursor,claude_code,codex
git add -A
git commit -m "Install Boost, Wayfinder (if needed), vite-plus/vp JS tooling, and project tooling"
```

JS standard — **prefer vite-plus** on React/Vue/Svelte kits (config in `vite.config` `fmt` / `lint` / `test`; no separate `.oxfmtrc` / `.oxlintrc`, no direct `oxfmt`/`oxlint` deps):

| Concern | Script | vite-plus kits | Fallback (e.g. Livewire) |
|---------|--------|----------------|--------------------------|
| Format | `format` / `format:check` | `vp fmt` / `vp fmt --check` | `oxfmt` / `oxfmt --check` |
| Lint | `lint` | `vp lint` (type-aware via config) | `oxlint` |
| Types | `types` | `vp check --no-fmt --no-lint` | `oxlint --type-aware --type-check` |
| JS tests | `test:js` | `vp test` | `vitest run` |
| Build | `build` | `vp build` | kit default |

### 4) Summarize for the user

App path, kit, three commits, PHP defaults present, Boost/Wayfinder/JS tooling status, PHP + `test:js` / format / lint / types / build results.

## Rules

- Never squash essentials into the scaffold commit.
- Prefer skill scripts + `reference/ESSENTIALS.md` snippets over inventing config.
- Keep PHP tests (`php artisan test`) and JS tests (`npm run test:js`) separate.
- Prefer `vp` whenever `vite-plus` is present; only install oxfmt/oxlint/Vitest directly as a fallback.
