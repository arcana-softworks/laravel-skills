#!/usr/bin/env bash
# Shared package-manager helpers for laravel-new skill scripts.
# Source from another script:  source "$(dirname "$0")/lib/package-manager.sh"
#
# Detection (lockfile wins; default npm):
#   package-lock.json      → npm
#   pnpm-lock.yaml         → pnpm
#   yarn.lock              → yarn
#   bun.lockb / bun.lock   → bun
#
# Explicit override: set FORCE_PM=npm|pnpm|yarn|bun before calling
# resolve_package_manager (or pass --pm through the caller).

detect_package_manager_from_lockfile() {
  if [[ -f package-lock.json ]]; then
    echo npm
  elif [[ -f pnpm-lock.yaml ]]; then
    echo pnpm
  elif [[ -f yarn.lock ]]; then
    echo yarn
  elif [[ -f bun.lockb || -f bun.lock ]]; then
    echo bun
  else
    echo npm
  fi
}

# Sets: PM, PM_INSTALL, PM_ADD_DEV, PM_REMOVE, PM_RUN
resolve_package_manager() {
  local forced="${FORCE_PM:-}"
  local detected
  detected="$(detect_package_manager_from_lockfile)"

  if [[ -n "$forced" ]]; then
    case "$forced" in
      npm|pnpm|yarn|bun) PM="$forced" ;;
      *)
        echo "Unknown package manager: ${forced} (use npm|pnpm|yarn|bun)" >&2
        return 1
        ;;
    esac
  else
    PM="$detected"
  fi

  case "$PM" in
    npm)
      PM_INSTALL=(npm install)
      PM_ADD_DEV=(npm install -D)
      PM_REMOVE=(npm uninstall)
      PM_RUN=(npm run)
      ;;
    pnpm)
      PM_INSTALL=(pnpm install)
      PM_ADD_DEV=(pnpm add -D)
      PM_REMOVE=(pnpm remove)
      PM_RUN=(pnpm run)
      ;;
    yarn)
      PM_INSTALL=(yarn install)
      PM_ADD_DEV=(yarn add -D)
      PM_REMOVE=(yarn remove)
      PM_RUN=(yarn)
      ;;
    bun)
      PM_INSTALL=(bun install)
      PM_ADD_DEV=(bun add -d)
      PM_REMOVE=(bun remove)
      PM_RUN=(bun run)
      ;;
  esac

  if [[ -n "$forced" && "$forced" != "$detected" ]]; then
    switch_package_manager_lockfiles "$forced" "$detected"
    rewrite_composer_package_manager_scripts "$forced"
  fi

  export PM
}

# Drop conflicting lockfiles when the user explicitly switches PM.
switch_package_manager_lockfiles() {
  local target="$1"
  local previous="$2"
  echo "Switching package manager ${previous} → ${target} (explicit --pm)" >&2

  case "$target" in
    npm)
      rm -f pnpm-lock.yaml yarn.lock bun.lockb bun.lock
      ;;
    pnpm)
      rm -f package-lock.json yarn.lock bun.lockb bun.lock
      ;;
    yarn)
      rm -f package-lock.json pnpm-lock.yaml bun.lockb bun.lock
      ;;
    bun)
      rm -f package-lock.json pnpm-lock.yaml yarn.lock
      ;;
  esac
}

# Rewrite composer.json scripts that invoke npm/pnpm/yarn/bun.
rewrite_composer_package_manager_scripts() {
  local target="$1"
  [[ -f composer.json ]] || return 0
  python3 - "$target" <<'PY'
import json
import re
import sys

target = sys.argv[1]
path = "composer.json"
data = json.load(open(path, encoding="utf-8"))
scripts = data.get("scripts")
if not isinstance(scripts, dict):
    raise SystemExit(0)

# Map any of the common PM prefixes to the target.
pattern = re.compile(r"\b(npm|pnpm|yarn|bun)( run\b| install\b| ci\b| [\w:-])")

def rewrite_one(val: str) -> str:
    def repl(m: re.Match[str]) -> str:
        rest = m.group(2)
        # yarn has no "run" for some scripts; keep "yarn run" when original had "npm run"
        if target == "yarn" and rest.startswith(" run"):
            return "yarn" + rest
        if target == "yarn" and rest.startswith(" install"):
            return "yarn" + rest
        return target + rest
    return pattern.sub(repl, val)

changed = False

def walk(obj):
    global changed
    if isinstance(obj, list):
        for i, item in enumerate(obj):
            if isinstance(item, str):
                new = rewrite_one(item)
                if new != item:
                    obj[i] = new
                    changed = True
            else:
                walk(item)
    elif isinstance(obj, dict):
        for k, v in list(obj.items()):
            if isinstance(v, str):
                new = rewrite_one(v)
                if new != v:
                    obj[k] = new
                    changed = True
            else:
                walk(v)

walk(scripts)
if changed:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=4)
        fh.write("\n")
    print(f"Updated composer.json scripts to use {target}")
else:
    print("composer.json scripts already match package manager (or have no PM calls)")
PY
}

pm_install() {
  "${PM_INSTALL[@]}" "$@"
}

pm_add_dev() {
  "${PM_ADD_DEV[@]}" "$@"
}

pm_remove() {
  local -a pkgs=("$@")
  [[ ${#pkgs[@]} -eq 0 || -z "${pkgs[0]:-}" ]] && return 0
  "${PM_REMOVE[@]}" "${pkgs[@]}"
}

pm_run() {
  "${PM_RUN[@]}" "$@"
}
