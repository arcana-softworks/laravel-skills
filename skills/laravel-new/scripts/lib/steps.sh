#!/usr/bin/env bash
# Shared laravel-new step ids, descriptions, and --skip parsing.
# Source from another script after SCRIPT_DIR is set.
#
# Canonical step ids (see SKILL.md "Plan and confirm"):
#   scaffold | essentials | boost | wayfinder | js-fmt-lint | anti-slop |
#   vitest | ci | docker | commits
#
# Usage after source:
#   parse_skip_args "$@"   # consumes --skip <id> / --skip-<id>; leaves rest in STEPS_REMAINING_ARGS
#   step_enabled <id>      # exit 0 if enabled
#   require_known_step <id>

# Ordered list of skippable step ids.
LARAVEL_NEW_STEPS=(
  scaffold
  essentials
  boost
  wayfinder
  js-fmt-lint
  anti-slop
  vitest
  ci
  docker
  commits
)

laravel_new_step_description() {
  case "$1" in
    scaffold) echo "Scaffold Laravel app with the chosen starter kit" ;;
    essentials) echo "Apply sensible PHP source defaults into AppServiceProvider (strict models, NIST/OWASP/NCSC passwords, dates, make:action, Pint)" ;;
    boost) echo "Install Laravel Boost and configure agents" ;;
    wayfinder) echo "Install Wayfinder when Inertia + Vite (skip if already present / non-Inertia)" ;;
    js-fmt-lint) echo "Configure oxfmt/oxlint via vite-plus vp (or direct ox* fallback) + package scripts" ;;
    anti-slop) echo "Fetch latest dmmulroy/anti-slop into the app and wire into vp/oxlint config" ;;
    vitest) echo "Add Vitest smoke tests, setup file, and test:js script" ;;
    ci) echo "Write .github/workflows/ci.yml (check/dry-run php + js jobs)" ;;
    docker) echo "Add ServerSideUp PHP Docker image (Dockerfile, compose, queue/scheduler)" ;;
    commits) echo "Commit layout: scaffold → essentials → tooling → docker (if enabled)" ;;
    *) echo "Unknown step: $1" ;;
  esac
}

# Associative array of skipped steps (bash 4+).
declare -A LARAVEL_NEW_SKIPPED=()

is_known_step() {
  local id="$1"
  local s
  for s in "${LARAVEL_NEW_STEPS[@]}"; do
    [[ "$s" == "$id" ]] && return 0
  done
  return 1
}

require_known_step() {
  local id="$1"
  if ! is_known_step "$id"; then
    echo "Unknown step id: ${id}" >&2
    echo "Known: ${LARAVEL_NEW_STEPS[*]}" >&2
    return 1
  fi
}

mark_step_skipped() {
  local id="$1"
  require_known_step "$id" || return 1
  LARAVEL_NEW_SKIPPED["$id"]=1
}

step_enabled() {
  local id="$1"
  [[ -z "${LARAVEL_NEW_SKIPPED[$id]:-}" ]]
}

# Parse argv for --skip <id>, --skip=<id>, and legacy --skip-<id>.
# Sets STEPS_REMAINING_ARGS to the unconsumed arguments.
parse_skip_args() {
  STEPS_REMAINING_ARGS=()
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --skip)
        [[ $# -ge 2 ]] || { echo "--skip requires a step id" >&2; return 1; }
        mark_step_skipped "$2" || return 1
        shift 2
        ;;
      --skip=*)
        mark_step_skipped "${1#--skip=}" || return 1
        shift
        ;;
      --skip-scaffold) mark_step_skipped scaffold; shift ;;
      --skip-essentials) mark_step_skipped essentials; shift ;;
      --skip-boost) mark_step_skipped boost; shift ;;
      --skip-wayfinder) mark_step_skipped wayfinder; shift ;;
      --skip-js-fmt-lint|--skip-js-tooling) mark_step_skipped js-fmt-lint; shift ;;
      --skip-anti-slop) mark_step_skipped anti-slop; shift ;;
      --skip-vitest) mark_step_skipped vitest; shift ;;
      --skip-ci) mark_step_skipped ci; shift ;;
      --skip-docker) mark_step_skipped docker; shift ;;
      --skip-commits) mark_step_skipped commits; shift ;;
      *)
        STEPS_REMAINING_ARGS+=("$1")
        shift
        ;;
    esac
  done
}

list_enabled_steps() {
  local s
  for s in "${LARAVEL_NEW_STEPS[@]}"; do
    step_enabled "$s" && printf '%s\n' "$s"
  done
}

list_skipped_steps() {
  local s
  for s in "${LARAVEL_NEW_STEPS[@]}"; do
    step_enabled "$s" || printf '%s\n' "$s"
  done
}
