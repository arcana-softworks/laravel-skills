---
name: laravel-react-essentials
description: >-
  Create a fresh Laravel Inertia React app from the official laravel/react-starter-kit
  and apply Nuno Maduro Essentials recommendations as source patches (not the composer
  package), ending with exactly two commits: scaffold, then Essentials. Use whenever
  the user wants a new Laravel React starter with Essentials defaults, nunomaduro/essentials
  without requiring the package, or this repo's patch-based kit.
---

# Laravel React + Essentials (patch-based)

Install a **fresh** app from the official [laravel/react-starter-kit](https://github.com/laravel/react-starter-kit), then apply this repository’s Essentials **source patches**. Do **not** add `nunomaduro/essentials` to Composer.

Shared source of truth (do not copy patch contents into the skill or the app by hand):

| Path | Role |
|------|------|
| `bin/essentials-kit` | Fetch upstream, apply/regenerate patches, create apps |
| `patches/` + `patches/series` | Ordered Essentials patch set |
| `versions.json` | Pinned starter-kit + Essentials refs |
| `docs/ESSENTIALS_MAPPING.md` | Feature → source mapping |

## Preconditions

- PHP 8.3+, Composer, Node 22+, npm, git, rsync, python3
- This kit repo available locally (clone or path). Set `KIT_ROOT` to it.

## End state (required)

In the **new app** git repository, history must be exactly:

1. **Commit 1 — scaffold:** official React starter kit only (pinned SHA from `versions.json`)
2. **Commit 2 — Essentials:** patches applied via `bin/essentials-kit apply` (one atomic commit)

Clear messages, for example:

- `Scaffold Laravel official React starter kit (laravel/react-starter-kit@<sha>)`
- `Apply Nuno Maduro Essentials recommendations as source patches (not nunomaduro/essentials)`

## Procedure

Replace `KIT_ROOT` with the path to this repository and `APP_NAME` with the app directory name. Prefer a scratch directory outside the kit repo.

```bash
set -euo pipefail
KIT_ROOT="/path/to/this-kit-repo"
APP_NAME="my-app"
APP_PARENT="${PWD}"
APP_DIR="${APP_PARENT}/${APP_NAME}"

chmod +x "${KIT_ROOT}/bin/essentials-kit"
PINNED_SHA="$(python3 -c 'import json;print(json.load(open("'"${KIT_ROOT}"'/versions.json"))["starter_kit"]["ref"])')"

# --- Commit 1: official starter only ---
rm -rf "${APP_DIR}"
git clone https://github.com/laravel/react-starter-kit.git "${APP_DIR}"
cd "${APP_DIR}"
git checkout --force "${PINNED_SHA}"
# Replace upstream history with a single scaffold commit
rm -rf .git
git init -b main
git add -A
git -c user.email="${GIT_AUTHOR_EMAIL:-agent@localhost}" \
    -c user.name="${GIT_AUTHOR_NAME:-agent}" \
    commit -m "Scaffold Laravel official React starter kit (laravel/react-starter-kit@${PINNED_SHA})"

# --- Commit 2: Essentials patches (shared patch set) ---
"${KIT_ROOT}/bin/essentials-kit" apply --dir "${APP_DIR}"
git add -A
git -c user.email="${GIT_AUTHOR_EMAIL:-agent@localhost}" \
    -c user.name="${GIT_AUTHOR_NAME:-agent}" \
    commit -m "Apply Nuno Maduro Essentials recommendations as source patches (not nunomaduro/essentials)"

test "$(git rev-list --count HEAD)" -eq 2
git log --oneline
```

### Bootstrap the app (after the two commits)

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

Note: the upstream kit’s Composer `post-update-cmd` may run `php artisan install:features` (Chisel). Using `--no-scripts` keeps the tree aligned with the patched official kit for verification. For a product app you may run feature installation afterward; Essentials changes live mainly in `AppServiceProvider`, Pint/Rector config, and `make:action`.

## One-command alternative (no two-commit history)

If the user only wants a tree (not the two-commit layout):

```bash
"${KIT_ROOT}/bin/essentials-kit" create "${APP_NAME}"
```

## Rules

- **Never** `composer require nunomaduro/essentials`.
- **Never** paste or re-implement patch hunks in the skill; always call `bin/essentials-kit apply`.
- If apply fails, stop and report the failing patch name + `git apply` error. Do not hand-edit around conflicts unless asked; prefer fixing patches via `bin/essentials-kit regenerate --dir ...` in the kit repo.
- Do not invent extra Essentials features beyond `docs/ESSENTIALS_MAPPING.md` / the patch set.

## Quick behavior checks (optional)

After bootstrapping:

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
