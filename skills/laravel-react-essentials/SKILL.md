---
name: laravel-react-essentials
description: >-
  Create a fresh Laravel Inertia React app from the official laravel/react-starter-kit
  with Nuno Maduro Essentials recommendations as source patches (not the composer
  package). Prefer laravel new --using against this repo's generated kit branch; otherwise
  apply patches via bin/kit and leave exactly two commits (scaffold, then patches).
---

# Laravel React + Essentials (patch-based)

Do **not** add `nunomaduro/essentials` to Composer.

Shared source of truth:

| Path | Role |
|------|------|
| `bin/kit` | Fetch upstream, apply/regenerate patches, materialize `kit` branch, create apps |
| `patches/` + `patches/series` | Ordered patch set |
| `versions.json` | Pinned starter-kit + Essentials refs + `kit.composer_name` / `kit.branch` |
| `docs/ESSENTIALS_MAPPING.md` | Feature → source mapping |
| Branch `kit` | Generated full-app tree for `laravel new --using` (never hand-edit) |

## Preferred: `laravel new --using`

Public GitHub kit branch (tiged under the hood):

```bash
laravel new my-app --using=https://github.com/arcana-softworks/laravel-react#kit
# shorthand: arcana-softworks/laravel-react#kit
# Do not use /tree/kit — tiged treats that as a subdirectory, not a branch.
```

Alternative from a clone of this repo:

```bash
./bin/kit create my-app
```

Optional later: Packagist after you publish `kit.composer_name` from `versions.json` (`laravel new my-app --using=your-vendor/your-package:dev-kit`).

After `laravel new`, verify with Pint / PHPStan / `php artisan test` / `npm run build` as needed. Confirm Essentials behaviours (strict models, immutable dates, etc.) and that `composer.json` does **not** require `nunomaduro/essentials`.

## Fallback: two-commit patch apply

Use when the `kit` branch is unavailable. Prefer a scratch directory outside the kit repo.

```bash
set -euo pipefail
KIT_ROOT="/path/to/this-kit-repo"
APP_NAME="my-app"
APP_PARENT="${PWD}"
APP_DIR="${APP_PARENT}/${APP_NAME}"

chmod +x "${KIT_ROOT}/bin/kit"
PINNED_SHA="$(python3 -c 'import json;print(json.load(open("'"${KIT_ROOT}"'/versions.json"))["starter_kit"]["ref"])')"

# --- Commit 1: official starter only ---
rm -rf "${APP_DIR}"
git clone https://github.com/laravel/react-starter-kit.git "${APP_DIR}"
cd "${APP_DIR}"
git checkout --force "${PINNED_SHA}"
rm -rf .git
git init -b main
git add -A
git -c user.email="${GIT_AUTHOR_EMAIL:-agent@localhost}" \
    -c user.name="${GIT_AUTHOR_NAME:-agent}" \
    commit -m "Scaffold Laravel official React starter kit (laravel/react-starter-kit@${PINNED_SHA})"

# --- Commit 2: patches (shared patch set) ---
"${KIT_ROOT}/bin/kit" apply --dir "${APP_DIR}"
git add -A
git -c user.email="${GIT_AUTHOR_EMAIL:-agent@localhost}" \
    -c user.name="${GIT_AUTHOR_NAME:-agent}" \
    commit -m "Apply Nuno Maduro Essentials recommendations as source patches (not nunomaduro/essentials)"

test "$(git rev-list --count HEAD)" -eq 2
git log --oneline
```

### Bootstrap after the two commits

```bash
cd "${APP_DIR}"
composer install --no-interaction --prefer-dist --no-scripts
php artisan package:discover --ansi
cp -n .env.example .env || true
php artisan key:generate --force
mkdir -p database && touch database/database.sqlite
php artisan migrate --force
npm install && npm run build
vendor/bin/pint --parallel --test
vendor/bin/phpstan analyse
php artisan test
```

`--no-scripts` avoids Chisel/`install:features` mutating the tree mid-bootstrap. Prefer `laravel new --using=…` when you want the installer’s deferred Chisel hooks.

## One-command tree (no two-commit history)

```bash
"${KIT_ROOT}/bin/kit" create "${APP_NAME}"
```

## Rules

- **Never** `composer require nunomaduro/essentials`.
- **Never** paste or re-implement patch hunks; always call `bin/kit apply` or `laravel new --using=…` against the materialized `kit` branch.
- **Never** hand-edit branch `kit`; regenerate with `bin/kit materialize --push`.
- If apply fails, stop and report the failing patch + `git apply` error; fix via `bin/kit regenerate --dir ...`.
- Do not invent features beyond `docs/ESSENTIALS_MAPPING.md` / the patch set.

## Quick behaviour checks (optional)

```bash
php artisan tinker --execute '
$id = App\Models\User::factory()->create()->id;
$u = App\Models\User::query()->findOrFail($id);
try { $u->totally_missing_attr; echo "strict FAIL\n"; }
catch (Throwable $e) { echo "strict OK\n"; }
echo get_class(Illuminate\Support\Facades\Date::now()), "\n";
'
php artisan make:action SkillProbe --no-interaction
test -f app/Actions/SkillProbeAction.php
rm app/Actions/SkillProbeAction.php
```
