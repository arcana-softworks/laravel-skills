# Sensible Laravel defaults (paste snippets)

Kit-agnostic source changes. Apply into the install’s existing **`app/Providers/AppServiceProvider.php`** (`register()` / `boot()`), merging with any kit content already there. Do **not** create an `EssentialsServiceProvider`.

## 1. `AppServiceProvider` — imports + `boot()` body

Ensure these `use` imports (skip any already present):

```php
use Carbon\CarbonImmutable;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Support\Facades\Date;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\URL;
use Illuminate\Support\Facades\Vite;
use Illuminate\Support\Sleep;
use Illuminate\Validation\Rules\Password;
```

In `boot()` (append alongside kit helpers such as `configureDefaults()`; do not duplicate statements already present elsewhere in the class):

```php
Model::shouldBeStrict();
Model::automaticallyEagerLoadRelationships();

Date::use(CarbonImmutable::class);

DB::prohibitDestructiveCommands(app()->isProduction());

if (app()->isProduction()) {
    URL::forceHttps();
}

Vite::usePrefetchStrategy('aggressive');

Password::defaults(fn (): Password => Password::min(12)->max(255)->uncompromised());

if (app()->runningUnitTests()) {
    Http::preventStrayRequests();
    Sleep::fake();
}
```

If the kit already defines `Password::defaults(...)` (often production-only with `mixedCase` / `numbers` / `symbols`, or an older min/max), **replace** it with the one-liner above.

Promote three-random-words passphrases (and a password manager) in UI copy.

### Hashing

- Default driver: **`HASH_DRIVER=argon2id`**.
- Explicit costs in `config/hashing.php` / `.env.example`: **memory=65536 KiB, time=4, threads=1**.
- **`rehash_on_login` => true** so stored bcrypt (or weaker) hashes upgrade via `Hash::needsRehash` on login.

## 2. Do not register a separate essentials provider

Leave `bootstrap/providers.php` alone (aside from removing any legacy `EssentialsServiceProvider` entry).

## 3. `make:action` — copy stubs from this skill

| Copy from skill | Into app |
|-----------------|----------|
| `reference/stubs/MakeActionCommand.php` | `app/Console/Commands/MakeActionCommand.php` |
| `reference/stubs/action.stub` | `stubs/action.stub` |

Auto-discovered on Laravel 11+. Smoke: `php artisan make:action Probe --no-interaction` then delete the generated file.

## 4. Pint — project `pint.json`

Replace (or create) with `reference/stubs/pint.json`. Then run `vendor/bin/pint --parallel` so style lands in the same commit.

If `app/Concerns/ProfileValidationRules.php` exists and Larastan complains after `User` becomes `final`, widen the `emailRules()` PHPDoc to `@return array<int, Unique|string>` and `use Illuminate\Validation\Rules\Unique`.

## 5. Password tests (offline)

- Fake `UncompromisedVerifier` in `tests/TestCase.php` so kit registration / reset / update tests stay offline and deterministic with `Password::uncompromised()`.
- Align registration / reset / password-update fixtures to ≥12-character passphrases.

## 6. Rector (optional) — project `rector.php`

If missing, copy `reference/stubs/rector.php`. Running Rector requires `rector/rector` separately.

## 7. PHPStan

Keep the kit’s `phpstan.neon` / Larastan setup. Do not invent a package-oriented phpstan config. Run `vendor/bin/phpstan analyse` when present.
