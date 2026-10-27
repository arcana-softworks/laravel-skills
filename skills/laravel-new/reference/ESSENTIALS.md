# Essentials → source translations

This skill applies [nunomaduro/essentials](https://github.com/nunomaduro/essentials) **defaults as plain Laravel source**. The Composer package is **never** required.

Before applying, agents should fetch the live package README (and optionally `config/essentials.php`) to notice new features:

- https://raw.githubusercontent.com/nunomaduro/essentials/main/README.md
- https://raw.githubusercontent.com/nunomaduro/essentials/main/config/essentials.php

`scripts/apply-essentials` does this check automatically unless `--skip-fetch` is passed.

## Runtime (via `App\Providers\EssentialsServiceProvider`)

| Essentials feature | Default in package | Source translation |
|--------------------|--------------------|--------------------|
| `ShouldBeStrict` | enabled | `Model::shouldBeStrict()` |
| `AutomaticallyEagerLoadRelationships` | enabled | `Model::automaticallyEagerLoadRelationships()` |
| `ImmutableDates` | enabled | `Date::use(CarbonImmutable::class)` |
| `ProhibitDestructiveCommands` | enabled | `DB::prohibitDestructiveCommands(app()->isProduction())` |
| `ForceScheme` | enabled (production) | `URL::forceHttps()` when production |
| `AggressivePrefetching` | enabled | `Vite::useAggressivePrefetching()` |
| `SetDefaultPassword` | enabled (skipped in unit tests) | `Password::defaults(...)` with Essentials rules; skipped when `runningUnitTests()` |
| `FakeSleep` | enabled in unit tests | `Sleep::fake()` when `runningUnitTests()` |
| `PreventStrayRequests` | enabled in unit tests | `Http::preventStrayRequests()` when `runningUnitTests()` |
| `Unguard` | **disabled** | Not applied |

The provider is registered in `bootstrap/providers.php` (Laravel 11+). This avoids depending on a particular starter kit’s `AppServiceProvider` shape.

## Tooling

| Feature | Source translation |
|---------|-------------------|
| `make:action` | `app/Console/Commands/MakeActionCommand.php` + `stubs/action.stub` |
| `essentials:pint` | project `pint.json` from Essentials stub |
| `essentials:rector` | `rector.php` from Essentials stub if missing |

## Why not the Composer package?

Requiring `nunomaduro/essentials` couples the app to package boot order and config publish steps. Inlining the defaults keeps the scaffold auditable as a normal commit and works the same across official and community kits.
