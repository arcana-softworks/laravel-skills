# Essentials → starter-kit source mapping

Patches in this repo translate [nunomaduro/essentials](https://github.com/nunomaduro/essentials) defaults into plain Laravel source changes against [laravel/react-starter-kit](https://github.com/laravel/react-starter-kit). **`nunomaduro/essentials` is never added to `composer.json`.**

Pinned while building the current patch set (see `versions.json`):

| Upstream | Ref |
|----------|-----|
| laravel/react-starter-kit | `dbd4817d2d2936be14bc1ca7c94692fcef20b6b1` |
| nunomaduro/essentials | `v1.2.0` (`c5458ca21a395e592ba7d2ae16ec62632f7c7f3a`) |

## Runtime defaults (`AppServiceProvider`)

| Essentials configurable | Default in package | Source translation |
|-------------------------|--------------------|--------------------|
| `ShouldBeStrict` | enabled | `Model::shouldBeStrict()` |
| `AutomaticallyEagerLoadRelationships` | enabled | `Model::automaticallyEagerLoadRelationships()` |
| `ImmutableDates` | enabled | Already present in the starter kit; kept as `Date::use(CarbonImmutable::class)` |
| `ProhibitDestructiveCommands` | enabled | Already present; kept as `DB::prohibitDestructiveCommands(app()->isProduction())` |
| `ForceScheme` | enabled (production only) | `URL::forceHttps()` when `app()->isProduction()` |
| `AggressivePrefetching` | enabled | `Vite::useAggressivePrefetching()` |
| `SetDefaultPassword` | enabled (skipped during unit tests) | `Password::defaults(...)` with `min(12)`, letters/mixedCase/numbers/symbols, `max(255)`, `uncompromised()` in production; skipped when `runningUnitTests()` |
| `FakeSleep` | enabled during unit tests | `Sleep::fake()` when `runningUnitTests()` |
| `PreventStrayRequests` | enabled during unit tests | `Http::preventStrayRequests()` when `runningUnitTests()` |
| `Unguard` | **disabled** | Not applied (matches package default) |

## Tooling / Artisan extras

| Essentials feature | Source translation |
|--------------------|--------------------|
| `essentials:pint` / `stubs/pint.stub` | Project `pint.json` replaced with the Essentials Pint stub |
| `essentials:rector` / `stubs/rector.stub` | `rector.php` added from the Essentials Rector stub (install `rector/rector` yourself to run it) |
| `make:action` / `stubs/action.stub` | `app/Console/Commands/MakeActionCommand.php` + `stubs/action.stub` |
| Package `phpstan.neon.dist` | Not copied — it targets the package itself. The starter kit’s Larastan `phpstan.neon` is kept |

## Code style follow-through

With Essentials’ Pint rules enabled, the third patch applies the resulting style across the skeleton (`declare(strict_types=1)`, `final` classes, etc.) and corrects `ProfileValidationRules` PHPDoc so Larastan stays green when `User` is `final` (`Rule::unique()` returns `Unique`, which is `Stringable`, not `ValidationRule`).

## Already overlapped by the official starter kit

As of the pinned starter SHA, the upstream kit already configured immutable dates, destructive-command prohibition, and production password defaults. The runtime patch keeps those behaviors and aligns password defaults with Essentials (`max(255)`, skip under unit tests).

## Installable tree

`bin/kit materialize --push` applies this mapping onto the pinned starter and force-pushes orphan branch `kit` (Composer package name from `versions.json` → `kit.composer_name`). That branch is what `laravel new --using=…:dev-kit` consumes. Do not hand-edit it.
