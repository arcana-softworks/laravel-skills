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

// NCSC-aligned passwords: min length, deny-list breached passwords, no composition
// rules, max = users.password column length (system capability — usually 255).
// Min 12: NCSC gives no number; ICO says no less than 10; we choose 12.
Password::defaults(fn (): Password => Password::min(12)->max(255)->uncompromised());

if (app()->runningUnitTests()) {
    Http::preventStrayRequests();
    Sleep::fake();
}
```

If the kit already defines `Password::defaults(...)` (often production-only with `mixedCase` / `numbers` / `symbols`), **replace** it with the NCSC one-liner above. Derive `max(N)` from the users migration (`$table->string('password')` → 255, or an explicit length).

Prefer three-random-words passphrases in UI copy ([NCSC](https://www.ncsc.gov.uk/collection/top-tips-for-staying-secure-online/three-random-words)).

### Hashing (long passphrases)

Bcrypt silently truncates past **72 bytes**. laravel-new sets **`HASH_DRIVER=argon2id`** (`.env.example`, `phpunit.xml`, and publishes `config/hashing.php` when missing). If you switch back to bcrypt, set `BCRYPT_LIMIT=72` so over-long values fail closed instead of truncating.

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

- Fake `UncompromisedVerifier` in `tests/TestCase.php` so `Password::uncompromised()` does not call HaveIBeenPwned in CI.
- Align registration / reset / password-update fixtures to ≥12-character passphrases.
- Cover: 12-char all-lowercase accepted; 8-char rejected; column-max accepted; column-max+1 rejected.

## 6. Rector (optional) — project `rector.php`

If missing, copy `reference/stubs/rector.php`. Running Rector requires `rector/rector` separately.

## 7. PHPStan

Keep the kit’s `phpstan.neon` / Larastan setup. Do not invent a package-oriented phpstan config. Run `vendor/bin/phpstan analyse` when present.
