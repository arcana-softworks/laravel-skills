# Sensible Laravel defaults (paste snippets)

Kit-agnostic source changes. Apply into the install’s existing **`app/Providers/AppServiceProvider.php`** (`register()` / `boot()`), merging with any kit content already there. Do **not** create an `EssentialsServiceProvider`.

Password policy cites **OWASP Password Storage**, **NIST SP 800-63B-4**, and **NCSC** guidance.

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

// Passwords (OWASP / NIST SP 800-63B-4 / NCSC):
// - min 12: deliberate user choice below NIST's 15-char single-factor SHALL
//   (above ICO's 10; NCSC gives no number)
// - max 255: fixed request/DoS bound (above NIST's ≥64 SHOULD); NOT the users.password
//   column length (that column stores the hash, not the plaintext)
// - no composition rules; uncompromised() = HIBP deny-list (k-anonymity)
// Laravel Password::min/max count Unicode characters via mb_strlen.
Password::defaults(fn (): Password => Password::min(12)->max(255)->uncompromised());

if (app()->runningUnitTests()) {
    Http::preventStrayRequests();
    Sleep::fake();
}
```

If the kit already defines `Password::defaults(...)` (often production-only with `mixedCase` / `numbers` / `symbols`, or an older min/max), **replace** it with the one-liner above.

Promote three-random-words passphrases (and a password manager) in UI copy ([NCSC](https://www.ncsc.gov.uk/collection/top-tips-for-staying-secure-online/three-random-words)).

### Hashing (OWASP first choice: Argon2id)

- Default driver: **`HASH_DRIVER=argon2id`** (OWASP Password Storage Cheat Sheet; bcrypt is legacy-only).
- Explicit costs in `config/hashing.php` / `.env.example`: **memory=65536 KiB, time=4, threads=1** — Laravel’s defaults, which already exceed OWASP’s minimum (m=19456 KiB / t=2 / p=1).
- **`rehash_on_login` => true** so stored bcrypt (or weaker) hashes upgrade via `Hash::needsRehash` on login.
- NIST: verifiers SHALL NOT truncate — argon2id hashes the full input (unlike bcrypt’s 72-byte behaviour).

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
- Cover: 11-char rejected; 12-char all-lowercase accepted; 12-char multibyte accepted; 255 accepted; 256 rejected; hash of `72×a + X` must not verify as `72×a + Y` (no truncation).

## 6. Rector (optional) — project `rector.php`

If missing, copy `reference/stubs/rector.php`. Running Rector requires `rector/rector` separately.

## 7. PHPStan

Keep the kit’s `phpstan.neon` / Larastan setup. Do not invent a package-oriented phpstan config. Run `vendor/bin/phpstan analyse` when present.
