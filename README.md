# Laravel React starter + Essentials (patch-based)

Start from the **official** [Laravel Inertia React starter kit](https://github.com/laravel/react-starter-kit) and apply [Nuno Maduro’s Essentials](https://github.com/nunomaduro/essentials) recommendations as a **maintained source patch set** — **not** by requiring `nunomaduro/essentials` in Composer.

This repo is the single source of truth for:

1. **Patches + tooling** — `patches/`, `bin/kit`, scheduled CI sync  
2. **Materialized installable kit** — orphan branch `kit` (generated only; never hand-edited) for `laravel new --using=…`  
3. **Agent skill** — `skills/laravel-react-essentials/SKILL.md` (uses the same patches/`bin/kit`)

## Pinned upstreams

See [`versions.json`](versions.json). Current patch set built against:

| Project | Ref |
|---------|-----|
| `laravel/react-starter-kit` | `dbd4817d2d2936be14bc1ca7c94692fcef20b6b1` |
| `nunomaduro/essentials` | `v1.2.0` (`c5458ca…`) |
| Materialized Composer package | `local/laravel-react-kit` on branch `kit` → version `dev-kit` |

Feature → file mapping: [`docs/ESSENTIALS_MAPPING.md`](docs/ESSENTIALS_MAPPING.md).

## How `laravel new --using` works

From `laravel/installer` v5:

| `--using` value | Installer behaviour |
|-----------------|---------------------|
| **No `://` in the string** (Packagist / Composer package) | `composer create-project {using} "{dir}" --stability=dev` |
| **Contains `://`** (and not a first-party `laravel/*` kit) | `npx tiged@latest {using} "{dir}" && composer install` |

`tiged` only understands **GitHub / GitLab / Bitbucket / Sourcehut / Hugging Face**. It does **not** speak Cursor Origin. For Origin-hosted (or other private) remotes, use the **Composer package** form below.

Branch `kit` on this repo is an **orphan full-app tree** produced by `bin/kit materialize --push` from `patches/` + the pinned upstream. Patches remain the source of truth; never edit `kit` by hand.

### Exact command (Composer / Packagist-style)

Default package name (change in `versions.json` → `kit.composer_name` before publishing):

```bash
laravel new my-app --using=local/laravel-react-kit:dev-kit
```

That resolves Composer version `dev-kit` → git branch `kit`.

#### A) Public Packagist (best for others)

1. Set `kit.composer_name` to your Packagist name and rematerialize (`bin/kit materialize --push`).
2. Submit the package on [Packagist](https://packagist.org) with the VCS URL; ensure Packagist tracks branch `kit` (or tags cut from it).
3. Consumers run:

```bash
laravel new my-app --using=your-vendor/your-package:dev-kit
```

No extra Composer config once Packagist is public.

#### B) Public GitHub mirror (tiged URL form)

Mirror/push this repo (or only branch `kit`) to GitHub, then:

```bash
laravel new my-app --using=https://github.com/OWNER/REPO/tree/kit
# tiged also accepts: OWNER/REPO#kit
```

#### C) Private Cursor Origin (or other private Git)

`tiged` cannot fetch Origin. Configure Composer to see the VCS repo, then use the package form:

```bash
# Once per machine (use a token that can read the repo)
composer config repositories.laravel-react-kit vcs https://origin.cursor.com/git/OWNER/REPO.git

# Auth — pick what your forge supports, e.g. HTTP basic or a URL with a token:
composer config http-basic.origin.cursor.com x-access-token YOUR_TOKEN
# or: git credential / insteadOf / netrc

laravel new my-app --using=local/laravel-react-kit:dev-kit
```

If the repo is only on Origin and never published to Packagist/GitHub, **every consumer** needs that `repositories` (+ auth) config. Publishing to Packagist or a public GitHub `kit` branch removes that requirement.

### Chisel / `install:features`

The official starter runs `install:features` from Composer / installer hooks. The Laravel installer sets `LARAVEL_INSTALLER_DEFER_HOOKS=1` during `create-project`, then runs deferred hooks afterward (so Chisel is not half-applied mid-install). Prefer **`laravel new --using=…`** over raw `composer install` when you want that behaviour. Materialize **does not** run Composer or Chisel; it only writes the source tree.

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
./bin/kit materialize --push   # build + force-push orphan branch kit
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

## Agent skill (two commits)

Follow [`skills/laravel-react-essentials/SKILL.md`](skills/laravel-react-essentials/SKILL.md). Prefer `laravel new --using=…` when the `kit` branch is available; otherwise scaffold + `bin/kit apply` with exactly two commits.

## CI sync

[`.github/workflows/sync.yml`](.github/workflows/sync.yml) on schedule / push to `main`:

1. `check-upstreams`
2. Apply patches to pinned starter and current upstream `main`
3. Pint / PHPStan / PHPUnit / `npm run build`
4. `bin/kit materialize --push` (refreshes orphan `kit` branch)

Needs `contents: write` (or equivalent) to push `kit`. No app secrets are stored in the repo.

## Layout

```
bin/kit
patches/series
patches/0001-….patch …
versions.json
docs/ESSENTIALS_MAPPING.md
skills/laravel-react-essentials/SKILL.md
.github/workflows/sync.yml
# branch kit  → generated full app only (not present on main)
```

## License

Patch tooling and docs: MIT. Upstream Laravel starter kit and Essentials remain under their respective licenses.
