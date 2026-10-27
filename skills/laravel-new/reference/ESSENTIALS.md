# Sensible Laravel defaults (paste snippets)

Kit-agnostic source changes. Prefer registering a dedicated provider so you do not depend on a particular `AppServiceProvider` shape. Or paste the boot body into an existing provider’s `boot()`.

## 1. Service provider — `app/Providers/EssentialsServiceProvider.php`

Create this file, then register it (step 2).

```php
<?php

declare(strict_types=1);

namespace App\Providers;

use Carbon\CarbonImmutable;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Support\Facades\Date;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\URL;
use Illuminate\Support\Facades\Vite;
use Illuminate\Support\ServiceProvider;
use Illuminate\Support\Sleep;
use Illuminate\Validation\Rules\Password;

final class EssentialsServiceProvider extends ServiceProvider
{
    public function register(): void
    {
        //
    }

    public function boot(): void
    {
        Model::shouldBeStrict();
        Model::automaticallyEagerLoadRelationships();

        Date::use(CarbonImmutable::class);

        DB::prohibitDestructiveCommands(app()->isProduction());

        if (app()->isProduction()) {
            URL::forceHttps();
        }

        Vite::usePrefetchStrategy('aggressive');

        if (! app()->runningUnitTests()) {
            Password::defaults(fn (): ?Password => app()->isProduction()
                ? Password::min(12)
                    ->letters()
                    ->mixedCase()
                    ->numbers()
                    ->symbols()
                    ->max(255)
                    ->uncompromised()
                : null);
        }

        if (app()->runningUnitTests()) {
            Http::preventStrayRequests();
            Sleep::fake();
        }
    }
}
```

## 2. Register the provider — `bootstrap/providers.php`

Add next to `AppServiceProvider`:

```php
App\Providers\EssentialsServiceProvider::class,
```

(Laravel 10 `config/app.php` providers array works the same if that is what the kit uses.)

## 3. `make:action` — copy stubs from this skill

| Copy from skill | Into app |
|-----------------|----------|
| `reference/stubs/MakeActionCommand.php` | `app/Console/Commands/MakeActionCommand.php` |
| `reference/stubs/action.stub` | `stubs/action.stub` |

Auto-discovered on Laravel 11+. Smoke: `php artisan make:action Probe --no-interaction` then delete the generated file.

## 4. Pint — project `pint.json`

Replace (or create) with `reference/stubs/pint.json`. Then run `vendor/bin/pint --parallel` so style lands in the same commit.

If `app/Concerns/ProfileValidationRules.php` exists and Larastan complains after `User` becomes `final`, widen the `emailRules()` PHPDoc to `@return array<int, Unique|string>` and `use Illuminate\Validation\Rules\Unique`.

## 5. Rector (optional) — project `rector.php`

If missing, copy `reference/stubs/rector.php`. Running Rector requires `rector/rector` separately.

## 6. PHPStan

Keep the kit’s `phpstan.neon` / Larastan setup. Do not invent a package-oriented phpstan config. Run `vendor/bin/phpstan analyse` when present.
