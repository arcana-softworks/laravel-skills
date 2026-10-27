---
name: laravel-new
description: >-
  Create a new Laravel application with any official or community starter kit
  (Inertia React default), apply Nuno Maduro Essentials as source-level changes
  (not the composer package) in one atomic commit, then set up Laravel Boost and
  Wayfinder when appropriate. Use when the user asks for a new Laravel app,
  laravel new, scaffold Laravel, or wants Essentials defaults without
  nunomaduro/essentials.
---

# laravel-new

Create a fresh Laravel app, apply Essentials as **source**, then add Boost / Wayfinder tooling. Never `composer require nunomaduro/essentials`.

Install this skill: `npx skills add arcana-softworks/laravel-new-skill` (optionally `--skill laravel-new -g -a cursor -a claude-code -a codex -y`).

Skill root (this directory): use `${SKILL_ROOT}` below as the installed skill path (e.g. `.agents/skills/laravel-new` or `.cursor/skills/laravel-new`).

```bash
SKILL_ROOT="$(dirname "$(dirname "$0")")"  # when running a script from scripts/
# or absolute path to this skill directory after install
```

## When the user asks

Triggers include: “new Laravel app”, “scaffold Laravel”, “laravel new”, “Laravel with Essentials”, “Inertia React app”, etc.

## Ask only what is needed

Collect (or infer from the request), then proceed with defaults:

| Prompt | Default |
|--------|---------|
| App name | required (ask if missing) |
| Starter kit | **Inertia React** (`--react`) |
| Database | `sqlite` |
| Test framework | `phpunit` |
| Auth extras | none (`--workos` / `--teams` / `--no-authentication` only if requested) |
| Agents for Boost | `cursor,claude_code,codex` (or whatever the user names) |

### Kit choices (Laravel installer)

| User intent | Flag / value |
|-------------|--------------|
| React + Inertia (default) | `--react` |
| Vue + Inertia | `--vue` |
| Svelte + Inertia | `--svelte` |
| Livewire | `--livewire` |
| No starter kit | omit kit flags → plain `laravel/laravel` via fallback, or installer without kit flags |
| Community / custom | `--using=<packagist/name-or-https-url>` |

Installer also supports `--livewire-class-components`, `--workos`, `--teams`, `--no-authentication`, `--pest` / `--phpunit`, `--npm` / `--no-node`, `--boost` / `--no-boost`. Prefer this skill’s Boost step over the installer’s `--boost` so Boost lands in the tooling commit.

## Procedure (mandatory commit layout)

Work in a clean parent directory. Prefer the helper scripts shipped with this skill; they are idempotent where noted.

### 1) Scaffold (commit 1 — untouched kit)

```bash
chmod +x "${SKILL_ROOT}/scripts/"*
"${SKILL_ROOT}/scripts/scaffold-app" my-app --kit react --database sqlite --phpunit
cd my-app
# If the directory is not already a git repo:
git init -b main
git add -A
git commit -m "Scaffold Laravel application (official react starter kit)"
```

Adjust the commit message to name the kit actually used (`vue`, `livewire`, `using:vendor/package`, etc.).

Fallback if `laravel` is not on `PATH`: `scaffold-app` uses `composer create-project` for Packagist kit names (not URL-shaped `--using` values).

### 2) Essentials as source (commit 2 — one atomic commit)

```bash
# Optional but recommended: review live Essentials docs first
# https://raw.githubusercontent.com/nunomaduro/essentials/main/README.md

"${SKILL_ROOT}/scripts/apply-essentials" --dir .
# Verify behaviours / quality gates when present:
vendor/bin/pint --parallel --test 2>/dev/null || true
vendor/bin/phpstan analyse 2>/dev/null || true
php artisan test 2>/dev/null || true
php artisan make:action SkillProbe --no-interaction && rm -f app/Actions/SkillProbeAction.php

git add -A
git commit -m "Apply Nuno Maduro Essentials recommendations as source (not nunomaduro/essentials)"
```

Confirm `composer.json` does **not** list `nunomaduro/essentials`.

If `apply-essentials` warns about new upstream headings, read the Essentials README and extend the provider / stubs before committing.

Reference: [`reference/ESSENTIALS.md`](reference/ESSENTIALS.md).

### 3) Tooling: Boost + Wayfinder + deps (commit 3+)

```bash
"${SKILL_ROOT}/scripts/setup-tooling" --dir . --agents cursor,claude_code,codex
git add -A
git commit -m "Install Laravel Boost, Wayfinder (if needed), and project tooling"
```

- **Boost:** `composer require --dev laravel/boost`, write `boost.json` with agents, then `php artisan boost:install --no-interaction`.
- **Wayfinder:** if the kit already has `laravel/wayfinder`, leave it. Otherwise, on Inertia + Vite stacks, install `laravel/wayfinder` + `@laravel/vite-plugin-wayfinder` and wire `vite.config.*`.
- Also: `composer install`, `npm install`, `key:generate`, sqlite migrate, `npm run build`, `php artisan test`.

Keep Essentials changes out of this commit.

### 4) Final summary to the user

Report:

1. App path and kit used  
2. Commit layout (scaffold → Essentials → tooling)  
3. Essentials behaviours present; package **not** required  
4. Boost agents configured; Wayfinder status  
5. Test / Pint / PHPStan results  

## Rules

- **Never** `composer require nunomaduro/essentials`.
- **Never** squash Essentials into the scaffold commit.
- Prefer scripts under `scripts/` over re-implementing patch hunks.
- Kits differ — do not assume React-only file paths; the Essentials provider approach is kit-agnostic.
- Re-fetch Essentials docs when applying so new defaults are not missed silently.
