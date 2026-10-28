#!/usr/bin/env python3
"""Align kit password tests/UI/hashing with NIST/OWASP/NCSC Password::defaults."""
from __future__ import annotations

import re
import sys
from pathlib import Path

# Shared constants (must match patch_app_service_provider.py).
PASSWORD_MIN = 12
PASSWORD_MAX = 255

# 12-char all-lowercase passphrase (spaces count as characters).
PASS_OK_12 = "apple banana"
PASS_SHORT_11 = "apple banan"
FACTORY_PLAIN = "password"


def write(path: Path, text: str, root: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(f"Wrote {path.relative_to(root)}")


def main() -> int:
    root = Path(sys.argv[1])
    stubs = Path(sys.argv[2])

    # --- HASH_DRIVER=argon2id + explicit OWASP-meeting Argon costs ---
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

        # Explicit Argon2id costs (Laravel defaults already ≥ OWASP min).
        for key, value in (
            ("ARGON_MEMORY", "65536"),
            ("ARGON_TIME", "4"),
            ("ARGON_THREADS", "1"),
        ):
            if re.search(rf"(?m)^{key}=", text):
                text = re.sub(rf"(?m)^{key}=.*$", f"{key}={value}", text)
            else:
                text = re.sub(
                    r"(?m)^(HASH_DRIVER=argon2id)$",
                    rf"\1\n{key}={value}",
                    text,
                    count=1,
                )

        # Drop prior BCRYPT_LIMIT comment/workarounds from essentials if present.
        text = re.sub(r"(?m)^# BCRYPT_LIMIT=.*\n?", "", text)
        text = re.sub(r"(?m)^BCRYPT_LIMIT=.*\n?", "", text)

        env_example.write_text(text, encoding="utf-8")
        print("Updated .env.example HASH_DRIVER=argon2id + Argon costs")

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
        # Testing can use lower Argon cost for speed while keeping argon2id.
        if 'name="ARGON_MEMORY"' not in text:
            text = text.replace(
                '<env name="HASH_DRIVER" value="argon2id"/>',
                '<env name="HASH_DRIVER" value="argon2id"/>\n'
                '        <env name="ARGON_MEMORY" value="65536"/>\n'
                '        <env name="ARGON_TIME" value="2"/>\n'
                '        <env name="ARGON_THREADS" value="1"/>',
                1,
            )
        phpunit.write_text(text, encoding="utf-8")
        print("Updated phpunit.xml HASH_DRIVER / Argon envs")

    hashing = root / "config" / "hashing.php"
    stub = stubs / "hashing.php"
    if stub.is_file():
        # Always refresh published hashing.php from the skill stub so costs stay explicit.
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
    # Prefer replacing prior essentials passphrase ("apple banana") and kit shorts.
    replacements = [
        (
            "tests/Feature/Auth/RegistrationTest.php",
            r"'password'\s*=>\s*'(?:password|apple banana|three word pass)'",
            f"'password' => '{PASS_OK_12}'",
        ),
        (
            "tests/Feature/Auth/RegistrationTest.php",
            r"'password_confirmation'\s*=>\s*'(?:password|apple banana|three word pass)'",
            f"'password_confirmation' => '{PASS_OK_12}'",
        ),
        (
            "tests/Feature/Auth/PasswordResetTest.php",
            r"'password'\s*=>\s*'(?:password|newpassword123|apple banana|three word pass)'",
            f"'password' => '{PASS_OK_12}'",
        ),
        (
            "tests/Feature/Auth/PasswordResetTest.php",
            r"'password_confirmation'\s*=>\s*'(?:password|newpassword123|apple banana|three word pass)'",
            f"'password_confirmation' => '{PASS_OK_12}'",
        ),
        (
            "tests/Feature/Settings/SecurityTest.php",
            r"'password'\s*=>\s*'(?:new-password|apple banana|three word pass)'",
            f"'password' => '{PASS_OK_12}'",
        ),
        (
            "tests/Feature/Settings/SecurityTest.php",
            r"'password_confirmation'\s*=>\s*'(?:new-password|apple banana|three word pass)'",
            f"'password_confirmation' => '{PASS_OK_12}'",
        ),
        (
            "tests/Feature/Settings/SecurityTest.php",
            r"Hash::check\('(?:new-password|apple banana|three word pass)'",
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

    # --- Dedicated password-criteria feature test (always refresh for policy updates) ---
    criteria = root / "tests" / "Feature" / "Auth" / "PasswordCriteriaTest.php"
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

    public function test_password_defaults_are_min_12_max_255_uncompromised_without_composition(): void
    {{
        $rules = Password::defaults()->appliedRules();

        $this->assertSame({PASSWORD_MIN}, $rules['min']);
        $this->assertSame({PASSWORD_MAX}, $rules['max']);
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

    public function test_eleven_char_password_is_rejected(): void
    {{
        $this->skipUnlessFortifyHas(Features::registration());

        $response = $this->post(route('register.store'), [
            'name' => 'Short User',
            'email' => 'short@example.com',
            'password' => '{PASS_SHORT_11}',
            'password_confirmation' => '{PASS_SHORT_11}',
        ]);

        $response->assertSessionHasErrors('password');
        $this->assertGuest();
    }}

    public function test_twelve_character_multibyte_password_is_accepted(): void
    {{
        $this->skipUnlessFortifyHas(Features::registration());

        // 12 Unicode code points (accented letters); Password::min uses mb_strlen.
        $password = str_repeat('é', {PASSWORD_MIN});
        $this->assertSame({PASSWORD_MIN}, mb_strlen($password));

        $response = $this->post(route('register.store'), [
            'name' => 'Unicode User',
            'email' => 'unicode@example.com',
            'password' => $password,
            'password_confirmation' => $password,
        ]);

        $response->assertSessionHasNoErrors();
        $this->assertAuthenticated();
    }}

    public function test_password_at_max_length_is_accepted(): void
    {{
        $this->skipUnlessFortifyHas(Features::registration());

        $password = str_repeat('a', {PASSWORD_MAX});

        $response = $this->post(route('register.store'), [
            'name' => 'Max User',
            'email' => 'max@example.com',
            'password' => $password,
            'password_confirmation' => $password,
        ]);

        $response->assertSessionHasNoErrors();
        $this->assertAuthenticated();
    }}

    public function test_password_over_max_length_is_rejected(): void
    {{
        $this->skipUnlessFortifyHas(Features::registration());

        $password = str_repeat('a', {PASSWORD_MAX + 1});

        $response = $this->post(route('register.store'), [
            'name' => 'Overmax User',
            'email' => 'overmax@example.com',
            'password' => $password,
            'password_confirmation' => $password,
        ]);

        $response->assertSessionHasErrors('password');
        $this->assertGuest();
    }}

    public function test_hash_driver_does_not_truncate_past_seventy_two_bytes(): void
    {{
        $prefix = str_repeat('a', 72);
        $passwordA = $prefix.'X';
        $passwordB = $prefix.'Y';

        $this->assertSame('argon2id', config('hashing.driver'));
        $this->assertNotSame($passwordA, $passwordB);
        $this->assertGreaterThan(72, strlen($passwordA));

        $hash = Hash::make($passwordA);

        $this->assertTrue(Hash::check($passwordA, $hash));
        $this->assertFalse(Hash::check($passwordB, $hash));
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
        new = text
        new = new.replace(
            "Ensure your account is using a long, random password to stay secure",
            "Use a long passphrase (for example three random words) or a password manager. No symbol or mixed-case requirements",
        )
        new = new.replace(
            "Use a long passphrase (for example three random words). No symbol or mixed-case requirements",
            "Use a long passphrase (for example three random words) or a password manager. No symbol or mixed-case requirements",
        )
        if rel.endswith("register.tsx") or rel.endswith("reset-password.tsx"):
            new = new.replace('placeholder="Password"', 'placeholder="Three random words"')
            new = new.replace('placeholder="Confirm password"', 'placeholder="Confirm passphrase"')
        if new != text:
            path.write_text(new, encoding="utf-8")
            print(f"Updated UI copy in {rel}")

    print(f"PasswordPolicy=min{PASSWORD_MIN}_max{PASSWORD_MAX}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
