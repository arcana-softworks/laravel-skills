# Laravel React starter + Essentials (patch-based)

Start from the **official** [Laravel Inertia React starter kit](https://github.com/laravel/react-starter-kit) and apply [Nuno Maduro’s Essentials](https://github.com/nunomaduro/essentials) recommendations as a **maintained source patch set** — **not** by requiring `nunomaduro/essentials` in Composer.

## Create an app

```bash
laravel new my-app --using=https://github.com/arcana-softworks/laravel-react
```

The Laravel installer uses [tiged](https://github.com/tiged/tiged) under the hood for URL-shaped `--using` values (`npx tiged@latest … && composer install`). That clones the repo **default branch** (`main`), which is the generated full app.

Alternative (from a clone of the **`develop`** source branch):

```bash
git clone -b develop https://github.com/arcana-softworks/laravel-react.git
cd laravel-react
./bin/kit create my-app
```

Optional future route: publish to [Packagist](https://packagist.org) (set `kit.composer_name` in `versions.json`, rematerialize, then `laravel new my-app --using=your-vendor/your-package:dev-main`).

## Branch layout

| Branch | Role |
|--------|------|
| **`main`** (default) | Generated installable Laravel + React app. **Never hand-edit.** Produced by `bin/kit materialize --push`. |
| **`develop`** | Source of truth: `patches/`, `bin/kit`, `versions.json`, docs, skills, CI. |

You are reading the maintainer README on **`develop`**. The GitHub home page (`main`) shows the generated app’s upstream starter README — switch to the `develop` branch for this document and the agent skill.

## Pinned upstreams

See [`versions.json`](versions.json). Current patch set built against:

| Project | Ref |
|---------|-----|
| `laravel/react-starter-kit` | `dbd4817d2d2936be14bc1ca7c94692fcef20b6b1` |
| `nunomaduro/essentials` | `v1.2.0` (`c5458ca…`) |
| Materialized app branch | `main` (default / tiged HEAD) |

Feature → file mapping: [`docs/ESSENTIALS_MAPPING.md`](docs/ESSENTIALS_MAPPING.md).

This repo is the single source of truth for:

1. **Patches + tooling** — `patches/`, `bin/kit`, CI sync on `develop`
2. **Materialized installable app** — default branch `main` (generated only) for `laravel new --using=…`
3. **Agent skill** — `skills/laravel-react-essentials/SKILL.md`

## How `laravel new --using` works

From `laravel/installer` v5:

| `--using` value | Installer behaviour |
|-----------------|---------------------|
| **Contains `://`** (and not a first-party `laravel/*` kit) | `npx tiged@latest {using} "{dir}" && composer install` |
| **No `://`** (Packagist / Composer package) | `composer create-project {using} "{dir}" --stability=dev` |

No branch suffix is required: tiged clones the default branch. Patches remain the source of truth on `develop`; never edit `main` by hand.

### Chisel / `install:features`

The official starter runs `install:features` from Composer / installer hooks. The Laravel installer sets `LARAVEL_INSTALLER_DEFER_HOOKS=1` during `create-project`, then runs deferred hooks afterward. Prefer **`laravel new --using=…`** over raw `composer install` when you want that behaviour. Materialize **does not** run Composer or Chisel; it only writes the source tree.

## Local one-command (without the installer)

```bash
./bin/kit create my-app
cd my-app
composer install --no-interaction --prefer-dist --no-scripts
php artisan package:discover
cp -n .env.example .env && php artisan key:generate --force
mkdir -p database && touch database/database.sqlite && php artisan migrate --force
npm install && npm run build
```

## CLI reference

```bash
./bin/kit help
./bin/kit versions
./bin/kit fetch
./bin/kit apply --dir <app>
./bin/kit sync
./bin/kit check-upstreams
./bin/kit regenerate --dir <patched-app>
./bin/kit materialize          # build .cache/materialized
./bin/kit materialize --push   # build + force-push generated branch main
./bin/kit create my-app
./bin/kit verify
```

### Regenerating patches

1. `./bin/kit fetch --ref <new-starter-sha>`
2. Fix/apply until Pint / PHPStan / tests are green
3. `./bin/kit regenerate --dir /path/to/working-tree`
4. Update `versions.json` + `docs/ESSENTIALS_MAPPING.md` if needed
5. `./bin/kit verify` then `./bin/kit materialize --push`

## What the patches change

Runtime (in `AppServiceProvider`): strict models, automatic eager loading, immutable dates, prohibit destructive commands in production, force HTTPS in production, aggressive Vite prefetching, Essentials-aligned password defaults, `Http::preventStrayRequests()` + `Sleep::fake()` during unit tests.

Tooling: Essentials `pint.json`, `rector.php`, and `php artisan make:action` (+ stub).

Code style: Essentials Pint rules across the skeleton.

**Not** applied: `Unguard` (disabled in Essentials by default). **Not** added: `nunomaduro/essentials` package.

## Agent skill

Follow [`skills/laravel-react-essentials/SKILL.md`](skills/laravel-react-essentials/SKILL.md). Prefer `laravel new --using=…` against default `main`; otherwise scaffold + `bin/kit apply` with exactly two commits.

## CI sync

| Workflow | Lives on | Triggers |
|----------|----------|----------|
| [`.github/workflows/sync.yml`](.github/workflows/sync.yml) | `develop` | push / PR to `develop`, `workflow_dispatch`, and `workflow_call` |
| `upstream-sync-schedule.yml` (injected) | generated `main` | weekday `schedule` + `workflow_dispatch` only |

The schedule file must sit on the **default branch** (GitHub only runs cron there). Materialize injects a thin dispatcher that calls the reusable `sync.yml` on `develop`, gated to `arcana-softworks/laravel-react`, and marks it `export-ignore` so tiged tarballs omit it when GitHub honors export-ignore. Pushing regenerated `main` does not re-run the develop workflow (no `on.push` for `main`).

Needs `contents: write` to force-push `main`. No app secrets are stored in this public repo.

## Layout (`develop`)

```
bin/kit
patches/series
patches/0001-….patch …
versions.json
templates/upstream-sync-schedule.yml
docs/ESSENTIALS_MAPPING.md
skills/laravel-react-essentials/SKILL.md
.github/workflows/sync.yml
# branch main → generated full app only (not present on develop)
```

## License

Patch tooling and docs: MIT. Upstream Laravel starter kit and Essentials remain under their respective licenses.
