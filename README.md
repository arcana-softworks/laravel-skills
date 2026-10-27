# Laravel React starter + Essentials (patch-based)

Start from the **official** [Laravel Inertia React starter kit](https://github.com/laravel/react-starter-kit) and apply [Nuno Maduro’s Essentials](https://github.com/nunomaduro/essentials) recommendations as a **maintained source patch set** — **not** by requiring `nunomaduro/essentials` in Composer.

This repo is the single source of truth for:

1. **Patch-based kit** — `patches/`, `bin/essentials-kit`, scheduled CI sync  
2. **Agent skill** — `skills/laravel-react-essentials/SKILL.md` (uses the same patches/script)

## Pinned upstreams

See [`versions.json`](versions.json). Current patch set built against:

| Project | Ref |
|---------|-----|
| `laravel/react-starter-kit` | `dbd4817d2d2936be14bc1ca7c94692fcef20b6b1` |
| `nunomaduro/essentials` | `v1.2.0` (`c5458ca…`) |

Feature → file mapping: [`docs/ESSENTIALS_MAPPING.md`](docs/ESSENTIALS_MAPPING.md).

## Quick start (one command)

```bash
git clone <this-repo> laravel-react-essentials-kit
cd laravel-react-essentials-kit
./bin/essentials-kit create my-app
cd my-app
composer install --no-interaction --prefer-dist --no-scripts
php artisan package:discover
cp -n .env.example .env && php artisan key:generate --force
mkdir -p database && touch database/database.sqlite && php artisan migrate --force
npm install && npm run build
```

### `laravel new --using=…`

The Laravel installer’s `--using` flag expects a **complete** application tree (Composer package or URL fetched via tiged), not this meta/patch repo.

**Best one-command route today:** `./bin/essentials-kit create my-app`.

**Optional:** publish a `kit` branch that contains only the materialized patched app (CI or `create` output). Then:

```bash
laravel new my-app --using=https://github.com/<you>/<repo>/tree/kit
# or, once on Packagist as a project package:
laravel new my-app --using=vendor/laravel-react-essentials-kit
```

Until that branch/package exists, use `bin/essentials-kit create`.

## CLI reference

```bash
./bin/essentials-kit help
./bin/essentials-kit versions
./bin/essentials-kit fetch                 # clone/update pinned starter into .cache/
./bin/essentials-kit apply --dir <app>     # apply patches/series in order
./bin/essentials-kit sync                  # fetch origin/main, apply, report failures
./bin/essentials-kit check-upstreams       # starter + Essentials moved past pins?
./bin/essentials-kit regenerate --dir <patched-app>
./bin/essentials-kit create my-app
./bin/essentials-kit verify
```

If a patch fails to apply, the tool prints the patch name and `git apply` error so you can fix and regenerate.

### Regenerating patches

1. `./bin/essentials-kit fetch --ref <new-starter-sha>`
2. Apply old patches or edit a working tree until Essentials behavior + Pint/PHPStan are green
3. `./bin/essentials-kit regenerate --dir /path/to/working-tree`
4. Update `versions.json` (starter SHA and/or Essentials tag/commit)
5. Update `docs/ESSENTIALS_MAPPING.md` if Essentials gained/lost configurables
6. `./bin/essentials-kit verify` and run the app’s `pint` / `phpstan` / `php artisan test` / `npm run build`

## What the patches change

Runtime (in `AppServiceProvider`): strict models, automatic eager loading, immutable dates, prohibit destructive commands in production, force HTTPS in production, aggressive Vite prefetching, Essentials-aligned password defaults, `Http::preventStrayRequests()` + `Sleep::fake()` during unit tests.

Tooling: Essentials `pint.json`, `rector.php`, and `php artisan make:action` (+ stub).

Code style: Essentials Pint rules applied across the skeleton (strict types, `final` classes, …).

**Not** applied: `Unguard` (disabled in Essentials by default). **Not** added: `nunomaduro/essentials` package.

## Agent skill (two commits)

Follow [`skills/laravel-react-essentials/SKILL.md`](skills/laravel-react-essentials/SKILL.md). It must:

1. Scaffold the official kit at the pinned SHA → **one commit**
2. Run `./bin/essentials-kit apply --dir <app>` → **exactly one Essentials commit**

## CI sync

[`.github/workflows/sync.yml`](.github/workflows/sync.yml) runs on a weekday schedule, push, and PR:

1. `check-upstreams` (starter `main` + Essentials tags/main vs `versions.json`)
2. Apply patches to the **pinned** starter and to **current** `origin/main` (fails loudly if apply breaks)
3. `composer install`, migrate, `npm run build`, Pint, PHPStan, PHPUnit

Works as GitHub Actions; Origin + Depot can run the same workflow syntax. No secrets are required for public upstream fetches.

## Layout

```
bin/essentials-kit
patches/series
patches/0001-essentials-runtime-defaults.patch
patches/0002-essentials-tooling-and-make-action.patch
patches/0003-essentials-code-style-and-types.patch
versions.json
docs/ESSENTIALS_MAPPING.md
skills/laravel-react-essentials/SKILL.md
.github/workflows/sync.yml
```

## License

Patch tooling and docs: MIT. Upstream Laravel starter kit and Essentials remain under their respective licenses.
