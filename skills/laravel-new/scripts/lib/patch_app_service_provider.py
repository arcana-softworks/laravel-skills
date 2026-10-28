#!/usr/bin/env python3
"""Merge laravel-new essentials into AppServiceProvider.php (idempotent)."""
from __future__ import annotations

import re
import sys
from pathlib import Path

# NIST SP 800-63B-4: single-factor passwords SHALL be ≥15 characters.
# Max 255 is a fixed request/DoS bound (above NIST's ≥64 SHOULD); NOT the
# users.password column length (that column stores the hash).
PASSWORD_MIN = 15
PASSWORD_MAX = 255

NCSC_PASSWORD = (
    "Password::defaults(fn (): Password => "
    f"Password::min({PASSWORD_MIN})->max({PASSWORD_MAX})->uncompromised());"
)


def main() -> int:
    path = Path(sys.argv[1])
    text = path.read_text(encoding="utf-8")
    original = text

    required_uses = [
        "Carbon\\CarbonImmutable",
        "Illuminate\\Database\\Eloquent\\Model",
        "Illuminate\\Support\\Facades\\Date",
        "Illuminate\\Support\\Facades\\DB",
        "Illuminate\\Support\\Facades\\Http",
        "Illuminate\\Support\\Facades\\URL",
        "Illuminate\\Support\\Facades\\Vite",
        "Illuminate\\Support\\ServiceProvider",
        "Illuminate\\Support\\Sleep",
        "Illuminate\\Validation\\Rules\\Password",
    ]

    def has_use(src: str, fqcn: str) -> bool:
        return re.search(rf"(?m)^use\s+{re.escape(fqcn)}\s*(?:as\s+\w+\s*)?;", src) is not None

    def ensure_uses(src: str) -> str:
        missing = [u for u in required_uses if not has_use(src, u)]
        if not missing:
            return src
        use_lines = [f"use {u};" for u in missing]
        uses = list(re.finditer(r"(?m)^use\s+[^;]+;", src))
        if uses:
            insert_at = uses[-1].end()
            return src[:insert_at] + "\n" + "\n".join(use_lines) + src[insert_at:]
        ns = re.search(r"(?m)^namespace\s+[^;]+;", src)
        if ns:
            return src[: ns.end()] + "\n\n" + "\n".join(use_lines) + src[ns.end() :]
        m = re.search(r"(?s)^<\?php(?:\s*declare\s*\([^)]+\)\s*;)?", src)
        insert_at = m.end() if m else 0
        return src[:insert_at] + "\n\n" + "\n".join(use_lines) + "\n" + src[insert_at:]

    def password_defaults_is_target(src: str) -> bool:
        patterns = [
            rf"Password::defaults\s*\(\s*fn\s*\([^)]*\)\s*:\s*\??Password\s*=>\s*"
            rf"Password::min\s*\(\s*{PASSWORD_MIN}\s*\)\s*->max\s*\(\s*{PASSWORD_MAX}\s*\)\s*"
            rf"->uncompromised\s*\(\s*\)\s*\)\s*;",
            rf"Password::defaults\s*\(\s*fn\s*\([^)]*\)\s*=>\s*"
            rf"Password::min\s*\(\s*{PASSWORD_MIN}\s*\)\s*->max\s*\(\s*{PASSWORD_MAX}\s*\)\s*"
            rf"->uncompromised\s*\(\s*\)\s*\)\s*;",
        ]
        for pat in patterns:
            m = re.search(pat, src, flags=re.S)
            if not m:
                continue
            if re.search(r"mixedCase\s*\(|->numbers\s*\(|->symbols\s*\(|->letters\s*\(", m.group(0)):
                return False
            return True
        return False

    def replace_password_defaults(src: str) -> str:
        m = re.search(r"Password::defaults\s*\(", src)
        if not m:
            return src
        start = m.start()
        i = m.end() - 1
        depth = 0
        while i < len(src):
            if src[i] == "(":
                depth += 1
            elif src[i] == ")":
                depth -= 1
                if depth == 0:
                    end = i + 1
                    while end < len(src) and src[end] in " \t":
                        end += 1
                    if end < len(src) and src[end] == ";":
                        end += 1
                    return src[:start] + NCSC_PASSWORD + src[end:]
            i += 1
        return src

    def find_method_body(src: str, name: str) -> tuple[int, int, str] | None:
        m = re.search(
            rf"(?ms)^(?P<indent>[ \t]*)public function {re.escape(name)}\s*\([^)]*\)\s*(?::\s*\w+\s*)?\{{",
            src,
        )
        if not m:
            return None
        i = m.end()
        depth = 1
        while i < len(src):
            ch = src[i]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return (m.end(), i, m.group("indent") + "        ")
            i += 1
        return None

    def insert_into_boot(src: str, snippets: list[str]) -> str:
        if not snippets:
            return src
        found = find_method_body(src, "boot")
        if not found:
            raise SystemExit("Could not find public function boot() in AppServiceProvider.php")
        body_start, body_end, indent = found
        body = src[body_start:body_end]
        stripped = body.strip()
        if stripped in ("", "//", "//\n"):
            new_body = "\n" + "\n\n".join(f"{indent}{s}" for s in snippets) + "\n" + indent[:4]
            return src[:body_start] + new_body + src[body_end:]
        addition = "\n\n" + "\n\n".join(f"{indent}{s}" for s in snippets) + "\n" + indent[:4]
        return src[:body_start] + body.rstrip() + addition + src[body_end:]

    boot_snippets: list[tuple[str, str]] = [
        (r"Model::shouldBeStrict\s*\(", "Model::shouldBeStrict();"),
        (
            r"Model::automaticallyEagerLoadRelationships\s*\(",
            "Model::automaticallyEagerLoadRelationships();",
        ),
        (r"Date::use\s*\(\s*CarbonImmutable::class\s*\)", "Date::use(CarbonImmutable::class);"),
        (
            r"DB::prohibitDestructiveCommands\s*\(",
            "DB::prohibitDestructiveCommands(app()->isProduction());",
        ),
        (
            r"URL::forceHttps\s*\(",
            "if (app()->isProduction()) {\n            URL::forceHttps();\n        }",
        ),
        (r"Vite::usePrefetchStrategy\s*\(", "Vite::usePrefetchStrategy('aggressive');"),
        (
            r"Http::preventStrayRequests\s*\(",
            "if (app()->runningUnitTests()) {\n"
            "            Http::preventStrayRequests();\n"
            "            Sleep::fake();\n"
            "        }",
        ),
    ]

    if find_method_body(text, "register") is None:
        raise SystemExit("Could not find public function register() in AppServiceProvider.php")

    text = ensure_uses(text)

    if re.search(r"Password::defaults\s*\(", text):
        if not password_defaults_is_target(text):
            text = replace_password_defaults(text)

    to_add: list[str] = []
    for probe, code in boot_snippets:
        if re.search(probe, text):
            continue
        to_add.append(code)

    if not re.search(r"Password::defaults\s*\(", text):
        to_add.append(NCSC_PASSWORD)

    if to_add:
        text = insert_into_boot(text, to_add)

    if not password_defaults_is_target(text) and re.search(r"Password::defaults\s*\(", text):
        text = replace_password_defaults(text)

    if text != original:
        path.write_text(text, encoding="utf-8")
        print("AppServiceProvider updated")
    else:
        print("AppServiceProvider already has essentials")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
