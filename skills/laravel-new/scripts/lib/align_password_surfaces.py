#!/usr/bin/env python3
"""Align kit password tests/UI/hashing with NCSC Password::defaults (idempotent)."""
from __future__ import annotations

import re
import sys
from pathlib import Path

PASS_OK_12 = "apple banana"  # 12 chars, all-lowercase passphrase
PASS_SHORT = "shortpwd"  # 8 chars
FACTORY_PLAIN = "password"


def write(path: Path, text: str, root: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(f"Wrote {path.relative_to(root)}")


def main() -> int:
    root = Path(sys.argv[1])
    password_max = int(sys.argv[2])
    stubs = Path(sys.argv[3])

    # --- HASH_DRIVER=argon2id (avoid bcrypt silent 72-byte truncation) ---
    env_example = root / ".env.example"
    if env_example.is_file():
        text = env_example.read_text(encoding="utf-8")
        if re.search(r"(?m)^HASH_DRIVER=", text):
            text = re.sub(r"(?m)^HASH_DRIVER=.*$", "HASH_DRIVER=argon2id", text)
        elif re.search(r"(?m)^BCRYPT_ROUNDS=", text):
            text = re.sub(
                r"(?m)^(BCRYPT_ROUNDS=.*)$",
                r"\1\nHASH_DRIVER=argon2id",
                text,
                count=1,
            )
        else:
            text = text.rstrip() + "\nHASH_DRIVER=argon2id\n"
        if "BCRYPT_LIMIT" not in text:
            text = re.sub(
                r"(?m)^(HASH_DRIVER=argon2id)$",
                r"\1\n"
                r"# BCRYPT_LIMIT=72  # if using bcrypt: fail instead of silently truncating at 72 bytes",
                text,
                count=1,
            )
        env_example.write_text(text, encoding="utf-8")
        print("Updated .env.example HASH_DRIVER=argon2id")

    phpunit = root / "phpunit.xml"
    if phpunit.is_file():
        text = phpunit.read_text(encoding="utf-8")
        if 'name="HASH_DRIVER"' not in text:
            text = text.replace(
                '<env name="BCRYPT_ROUNDS" value="4"/>',
                '<env name="BCRYPT_ROUNDS" value="4"/>\n'
                '        <env name="HASH_DRIVER" value="argon2id"/>',
                1,
            )
            phpunit.write_text(text, encoding="utf-8")
            print("Updated phpunit.xml HASH_DRIVER=argon2id")

    hashing = root / "config" / "hashing.php"
    if not hashing.is_file():
        stub = stubs / "hashing.php"
        if stub.is_file():
            write(hashing, stub.read_text(encoding="utf-8"), root)

    # --- TestCase: fake UncompromisedVerifier ---
    test_case = root / "tests" / "TestCase.php"
    if test_case.is_file() and "UncompromisedVerifier" not in test_case.read_text(encoding="utf-8"):
        desired = """<?php

namespace Tests;

use Illuminate\\Contracts\\Validation\\UncompromisedVerifier;
use Illuminate\\Foundation\\Testing\\TestCase as BaseTestCase;
use Laravel\\Fortify\\Features;

abstract class TestCase extends BaseTestCase
{
    protected function setUp(): void
    {
        parent::setUp();

        // Keep Password::uncompromised() offline and deterministic in tests/CI.
        $this->app->bind(UncompromisedVerifier::class, fn () => new class implements UncompromisedVerifier
        {
            public function verify($data): bool
            {
                return true;
            }
        });
    }

    protected function skipUnlessFortifyHas(string $feature, ?string $message = null): void
    {
        if (! Features::enabled($feature)) {
            $this->markTestSkipped($message ?? "Fortify feature [{$feature}] is not enabled.");
        }
    }
}
"""
        current = test_case.read_text(encoding="utf-8")
        if "skipUnlessFortifyHas" in current:
            write(test_case, desired, root)
        else:
            if "use Illuminate\\Contracts\\Validation\\UncompromisedVerifier;" not in current:
                current = current.replace(
                    "namespace Tests;\n",
                    "namespace Tests;\n\nuse Illuminate\\Contracts\\Validation\\UncompromisedVerifier;\n",
                    1,
                )
            if "protected function setUp(): void" not in current:
                current = current.replace(
                    "abstract class TestCase extends BaseTestCase\n{\n",
                    "abstract class TestCase extends BaseTestCase\n{\n"
                    "    protected function setUp(): void\n"
                    "    {\n"
                    "        parent::setUp();\n\n"
                    "        $this->app->bind(UncompromisedVerifier::class, fn () => new class implements UncompromisedVerifier\n"
                    "        {\n"
                    "            public function verify($data): bool\n"
                    "            {\n"
                    "                return true;\n"
                    "            }\n"
                    "        });\n"
                    "    }\n\n",
                    1,
                )
            write(test_case, current, root)

    # --- Align feature tests that submit new passwords through Password::default() ---
    replacements = [
        (
            "tests/Feature/Auth/RegistrationTest.php",
            r"'password'\s*=>\s*'password'",
            f"'password' => '{PASS_OK_12}'",
        ),
        (
            "tests/Feature/Auth/RegistrationTest.php",
            r"'password_confirmation'\s*=>\s*'password'",
            f"'password_confirmation' => '{PASS_OK_12}'",
        ),
        (
            "tests/Feature/Auth/PasswordResetTest.php",
            r"'password'\s*=>\s*'password'",
            f"'password' => '{PASS_OK_12}'",
        ),
        (
            "tests/Feature/Auth/PasswordResetTest.php",
            r"'password_confirmation'\s*=>\s*'password'",
            f"'password_confirmation' => '{PASS_OK_12}'",
        ),
        (
            "tests/Feature/Auth/PasswordResetTest.php",
            r"'password'\s*=>\s*'newpassword123'",
            f"'password' => '{PASS_OK_12}'",
        ),
        (
            "tests/Feature/Auth/PasswordResetTest.php",
            r"'password_confirmation'\s*=>\s*'newpassword123'",
            f"'password_confirmation' => '{PASS_OK_12}'",
        ),
        (
            "tests/Feature/Settings/SecurityTest.php",
            r"'password'\s*=>\s*'new-password'",
            f"'password' => '{PASS_OK_12}'",
        ),
        (
            "tests/Feature/Settings/SecurityTest.php",
            r"'password_confirmation'\s*=>\s*'new-password'",
            f"'password_confirmation' => '{PASS_OK_12}'",
        ),
        (
            "tests/Feature/Settings/SecurityTest.php",
            r"Hash::check\('new-password'",
            f"Hash::check('{PASS_OK_12}'",
        ),
    ]

    for rel, pattern, repl in replacements:
        path = root / rel
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        new, n = re.subn(pattern, repl, text)
        if n:
            path.write_text(new, encoding="utf-8")
            print(f"Aligned {rel} ({n} replacement(s))")

    # --- Dedicated password-criteria feature test ---
    criteria = root / "tests" / "Feature" / "Auth" / "PasswordCriteriaTest.php"
    if not criteria.is_file():
        write(
            criteria,
            f"""<?php

namespace Tests\\Feature\\Auth;

use App\\Models\\User;
use Illuminate\\Foundation\\Testing\\RefreshDatabase;
use Illuminate\\Support\\Facades\\Hash;
use Illuminate\\Validation\\Rules\\Password;
use Laravel\\Fortify\\Features;
use Tests\\TestCase;

class PasswordCriteriaTest extends TestCase
{{
    use RefreshDatabase;

    public function test_ncsc_password_defaults_are_min_12_max_column_uncompromised_without_composition(): void
    {{
        $rules = Password::defaults()->appliedRules();

        $this->assertSame(12, $rules['min']);
        $this->assertSame({password_max}, $rules['max']);
        $this->assertTrue($rules['uncompromised']);
        $this->assertFalse($rules['mixedCase']);
        $this->assertFalse($rules['letters']);
        $this->assertFalse($rules['numbers']);
        $this->assertFalse($rules['symbols']);
    }}

    public function test_twelve_char_all_lowercase_passphrase_is_accepted(): void
    {{
        $this->skipUnlessFortifyHas(Features::registration());

        $response = $this->post(route('register.store'), [
            'name' => 'Passphrase User',
            'email' => 'passphrase@example.com',
            'password' => '{PASS_OK_12}',
            'password_confirmation' => '{PASS_OK_12}',
        ]);

        $response->assertSessionHasNoErrors();
        $this->assertAuthenticated();
    }}

    public function test_eight_char_password_is_rejected(): void
    {{
        $this->skipUnlessFortifyHas(Features::registration());

        $response = $this->post(route('register.store'), [
            'name' => 'Short User',
            'email' => 'short@example.com',
            'password' => '{PASS_SHORT}',
            'password_confirmation' => '{PASS_SHORT}',
        ]);

        $response->assertSessionHasErrors('password');
        $this->assertGuest();
    }}

    public function test_password_at_column_max_length_is_accepted(): void
    {{
        $this->skipUnlessFortifyHas(Features::registration());

        $password = str_repeat('a', {password_max});

        $response = $this->post(route('register.store'), [
            'name' => 'Max User',
            'email' => 'max@example.com',
            'password' => $password,
            'password_confirmation' => $password,
        ]);

        $response->assertSessionHasNoErrors();
        $this->assertAuthenticated();
    }}

    public function test_password_over_column_max_length_is_rejected(): void
    {{
        $this->skipUnlessFortifyHas(Features::registration());

        $password = str_repeat('a', {password_max + 1});

        $response = $this->post(route('register.store'), [
            'name' => 'Overmax User',
            'email' => 'overmax@example.com',
            'password' => $password,
            'password_confirmation' => $password,
        ]);

        $response->assertSessionHasErrors('password');
        $this->assertGuest();
    }}

    public function test_password_update_accepts_passphrase_without_composition_rules(): void
    {{
        $user = User::factory()->create([
            'password' => Hash::make('{FACTORY_PLAIN}'),
        ]);

        $response = $this
            ->actingAs($user)
            ->put(route('user-password.update'), [
                'current_password' => '{FACTORY_PLAIN}',
                'password' => '{PASS_OK_12}',
                'password_confirmation' => '{PASS_OK_12}',
            ]);

        $response->assertSessionHasNoErrors();
        $this->assertTrue(Hash::check('{PASS_OK_12}', $user->refresh()->password));
    }}
}}
""",
            root,
        )

    # --- Frontend help copy ---
    for rel in (
        "resources/js/pages/settings/security.tsx",
        "resources/js/pages/auth/register.tsx",
        "resources/js/pages/auth/reset-password.tsx",
    ):
        path = root / rel
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        new = text.replace(
            "Ensure your account is using a long, random password to stay secure",
            "Use a long passphrase (for example three random words). No symbol or mixed-case requirements",
        )
        if rel.endswith("register.tsx") or rel.endswith("reset-password.tsx"):
            new = new.replace('placeholder="Password"', 'placeholder="Three random words"')
            new = new.replace('placeholder="Confirm password"', 'placeholder="Confirm passphrase"')
        if new != text:
            path.write_text(new, encoding="utf-8")
            print(f"Updated UI copy in {rel}")

    print(f"PasswordMaxApplied={password_max}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
