#!/usr/bin/env sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && /bin/pwd -P)
TEMP_ROOT=$(mktemp -d "${TMPDIR:-/tmp}/scrape-electrical-root-control-XXXXXX")
ATTACKER_ROOT="$TEMP_ROOT/attacker-root"
trap 'rm -rf "$TEMP_ROOT"' EXIT HUP INT TERM
unset MAKEFILES MAKEFILE_LIST MAKEFLAGS MFLAGS MAKEOVERRIDES ROOT PYTHON PYTHONDONTWRITEBYTECODE

CONTROL_DIR="$TEMP_ROOT/control"
CHECKOUT="$TEMP_ROOT/scrape-electrical's [gate] \"quoted\" \`touch SCRAPE_ELECTRICAL_BACKTICK_MARKER\`"
COMMAND_LOG="$TEMP_ROOT/commands.log"
BAD_COMMAND_LOG="$TEMP_ROOT/bad-command.log"
FAKE_SHELL_LOG="$TEMP_ROOT/fake-shell.log"
mkdir "$CONTROL_DIR" "$CHECKOUT" "$CHECKOUT/scripts" "$CHECKOUT/bin" "$ATTACKER_ROOT"
CONTROL_DIR=$(CDPATH= cd -- "$CONTROL_DIR" && /bin/pwd -P)
CHECKOUT=$(CDPATH= cd -- "$CHECKOUT" && /bin/pwd -P)
MAKEFILE="$CHECKOUT/Makefile"
cp "$ROOT_DIR/Makefile" "$MAKEFILE"

for command in python2 python3; do
  cat >"$CHECKOUT/bin/$command" <<'EOF'
#!/bin/sh
printf '%s|%s|%s|%s\n' "$PWD" "$0" "${PYTHONDONTWRITEBYTECODE:-}" "$*" >> "$SCRAPE_ELECTRICAL_COMMAND_LOG"
EOF
  chmod +x "$CHECKOUT/bin/$command"
done
cat >"$CHECKOUT/scripts/test-makefile-root.sh" <<'EOF'
#!/bin/sh
printf '%s|%s|%s|root-test\n' "$PWD" "$0" "${PYTHONDONTWRITEBYTECODE:-}" >> "$SCRAPE_ELECTRICAL_COMMAND_LOG"
EOF
chmod +x "$CHECKOUT/scripts/test-makefile-root.sh"

BAD_COMMAND="$TEMP_ROOT/bad-command"
cat >"$BAD_COMMAND" <<EOF
#!/bin/sh
printf '%s\n' invoked >> '$BAD_COMMAND_LOG'
exit 91
EOF
chmod +x "$BAD_COMMAND"

FAKE_SHELL="$TEMP_ROOT/fake-shell"
cat >"$FAKE_SHELL" <<EOF
#!/bin/sh
printf '%s\n' invoked >> '$FAKE_SHELL_LOG'
exec /bin/sh "\$@"
EOF
chmod +x "$FAKE_SHELL"

assert_commands_stayed_in_checkout() {
  scenario=$1
  target=$2
  if [ ! -s "$COMMAND_LOG" ]; then
    printf '%s\n' "$scenario $target executed no quality command" >&2
    exit 1
  fi
  while IFS= read -r command; do
    case "$command" in
      "$CONTROL_DIR|"*"$CHECKOUT"*"|1|"*) ;;
      "$CHECKOUT|"*"|1|"*) ;;
      *)
        printf '%s\n' "$scenario $target escaped the checkout or enabled bytecode: $command" >&2
        exit 1
        ;;
    esac
  done <"$COMMAND_LOG"
}

run_case() {
  scenario=$1
  target=$2
  mode=$3
  rm -f "$COMMAND_LOG" "$BAD_COMMAND_LOG" "$FAKE_SHELL_LOG"
  output="$TEMP_ROOT/output"
  set +e
  case "$mode" in
    default)
      (cd "$CONTROL_DIR" && PATH="$CHECKOUT/bin:$PATH" SCRAPE_ELECTRICAL_COMMAND_LOG="$COMMAND_LOG" /usr/bin/make --no-print-directory --file "$MAKEFILE" "$target") >"$output" 2>&1 ;;
    command-python3)
      (cd "$CONTROL_DIR" && PATH="$CHECKOUT/bin:$PATH" SCRAPE_ELECTRICAL_COMMAND_LOG="$COMMAND_LOG" /usr/bin/make --no-print-directory --file "$MAKEFILE" PYTHON=python3 "$target") >"$output" 2>&1 ;;
    environment-python3)
      (cd "$CONTROL_DIR" && PATH="$CHECKOUT/bin:$PATH" PYTHON=python3 SCRAPE_ELECTRICAL_COMMAND_LOG="$COMMAND_LOG" /usr/bin/make --no-print-directory --file "$MAKEFILE" "$target") >"$output" 2>&1 ;;
    command-root)
      (cd "$CONTROL_DIR" && PATH="$CHECKOUT/bin:$PATH" SCRAPE_ELECTRICAL_COMMAND_LOG="$COMMAND_LOG" /usr/bin/make --no-print-directory --file "$MAKEFILE" "ROOT=$ATTACKER_ROOT" "$target") >"$output" 2>&1 ;;
    environment-root)
      (cd "$CONTROL_DIR" && PATH="$CHECKOUT/bin:$PATH" ROOT="$ATTACKER_ROOT" SCRAPE_ELECTRICAL_COMMAND_LOG="$COMMAND_LOG" /usr/bin/make --no-print-directory --file "$MAKEFILE" "$target") >"$output" 2>&1 ;;
    command-shell)
      (cd "$CONTROL_DIR" && PATH="$CHECKOUT/bin:$PATH" SCRAPE_ELECTRICAL_COMMAND_LOG="$COMMAND_LOG" /usr/bin/make --no-print-directory --file "$MAKEFILE" "SHELL=$FAKE_SHELL" "$target") >"$output" 2>&1 ;;
    environment-shell)
      (cd "$CONTROL_DIR" && PATH="$CHECKOUT/bin:$PATH" SHELL="$FAKE_SHELL" SCRAPE_ELECTRICAL_COMMAND_LOG="$COMMAND_LOG" /usr/bin/make --no-print-directory --file "$MAKEFILE" "$target") >"$output" 2>&1 ;;
    command-flags)
      (cd "$CONTROL_DIR" && PATH="$CHECKOUT/bin:$PATH" SCRAPE_ELECTRICAL_COMMAND_LOG="$COMMAND_LOG" /usr/bin/make --no-print-directory --file "$MAKEFILE" '.SHELLFLAGS=-eu -c' "$target") >"$output" 2>&1 ;;
    environment-flags)
      (cd "$CONTROL_DIR" && env '.SHELLFLAGS=-eu -c' PATH="$CHECKOUT/bin:$PATH" SCRAPE_ELECTRICAL_COMMAND_LOG="$COMMAND_LOG" /usr/bin/make --no-print-directory --file "$MAKEFILE" "$target") >"$output" 2>&1 ;;
    command-bytecode)
      (cd "$CONTROL_DIR" && PATH="$CHECKOUT/bin:$PATH" SCRAPE_ELECTRICAL_COMMAND_LOG="$COMMAND_LOG" /usr/bin/make --no-print-directory --file "$MAKEFILE" PYTHONDONTWRITEBYTECODE=0 "$target") >"$output" 2>&1 ;;
    environment-bytecode)
      (cd "$CONTROL_DIR" && PATH="$CHECKOUT/bin:$PATH" PYTHONDONTWRITEBYTECODE=0 SCRAPE_ELECTRICAL_COMMAND_LOG="$COMMAND_LOG" /usr/bin/make --no-print-directory --file "$MAKEFILE" "$target") >"$output" 2>&1 ;;
    *)
      printf '%s\n' "unknown test mode: $mode" >&2
      exit 1 ;;
  esac
  result=$?
  set -e
  if [ "$result" -ne 0 ]; then
    printf '%s\n' "$scenario $target failed" >&2
    cat "$output" >&2
    exit 1
  fi
  assert_commands_stayed_in_checkout "$scenario" "$target"
  if [ -e "$BAD_COMMAND_LOG" ]; then
    printf '%s\n' "$scenario $target executed an invalid Python command" >&2
    exit 1
  fi
  if [ -e "$FAKE_SHELL_LOG" ]; then
    printf '%s\n' "$scenario $target executed caller-controlled shell" >&2
    exit 1
  fi
}

for target in build check contract-test lint root-test test verify; do
  run_case default "$target" default
  run_case command-python3 "$target" command-python3
  run_case environment-python3 "$target" environment-python3
  run_case command-root "$target" command-root
  run_case environment-root "$target" environment-root
  run_case command-shell "$target" command-shell
  run_case environment-shell "$target" environment-shell
  run_case command-flags "$target" command-flags
  run_case environment-flags "$target" environment-flags
  run_case command-bytecode "$target" command-bytecode
  run_case environment-bytecode "$target" environment-bytecode

  if (cd "$CONTROL_DIR" && PATH="$CHECKOUT/bin:$PATH" SCRAPE_ELECTRICAL_COMMAND_LOG="$COMMAND_LOG" /usr/bin/make --no-print-directory --file "$MAKEFILE" "PYTHON=$BAD_COMMAND" "$target") >"$TEMP_ROOT/invalid-command.out" 2>&1; then exit 1; fi
  grep -Fq "PYTHON must be exactly python2 or python3" "$TEMP_ROOT/invalid-command.out"
  if (cd "$CONTROL_DIR" && PATH="$CHECKOUT/bin:$PATH" PYTHON="$BAD_COMMAND" SCRAPE_ELECTRICAL_COMMAND_LOG="$COMMAND_LOG" /usr/bin/make --no-print-directory --file "$MAKEFILE" "$target") >"$TEMP_ROOT/invalid-environment.out" 2>&1; then exit 1; fi
  grep -Fq "PYTHON must be exactly python2 or python3" "$TEMP_ROOT/invalid-environment.out"
done

if [ -e "$CONTROL_DIR/SCRAPE_ELECTRICAL_BACKTICK_MARKER" ] || [ -e "$BAD_COMMAND_LOG" ]; then
  printf '%s\n' "checkout path or invalid Python executed a command" >&2
  exit 1
fi

FUNCTION_MARKER="$CONTROL_DIR/SCRAPE_ELECTRICAL_FUNCTION_MARKER"
if (cd "$CONTROL_DIR" && /usr/bin/make --no-print-directory --file "$MAKEFILE" 'PYTHON=$(shell touch SCRAPE_ELECTRICAL_FUNCTION_MARKER)' check) >"$TEMP_ROOT/function-command.out" 2>&1; then exit 1; fi
grep -Fq "PYTHON must be exactly python2 or python3" "$TEMP_ROOT/function-command.out"
if (cd "$CONTROL_DIR" && env 'PYTHON=$(shell touch SCRAPE_ELECTRICAL_FUNCTION_MARKER)' /usr/bin/make --no-print-directory --file "$MAKEFILE" check) >"$TEMP_ROOT/function-environment.out" 2>&1; then exit 1; fi
grep -Fq "PYTHON must be exactly python2 or python3" "$TEMP_ROOT/function-environment.out"
[ ! -e "$FUNCTION_MARKER" ]

if (cd "$CONTROL_DIR" && /usr/bin/make --no-print-directory --file "$MAKEFILE" MAKEFILE_LIST=/tmp/untrusted check) >"$TEMP_ROOT/command-list.out" 2>&1; then exit 1; fi
grep -Fq "MAKEFILE_LIST must not be overridden" "$TEMP_ROOT/command-list.out"
if (cd "$CONTROL_DIR" && MAKEFILE_LIST=/tmp/untrusted /usr/bin/make --environment-overrides --no-print-directory --file "$MAKEFILE" check) >"$TEMP_ROOT/environment-list.out" 2>&1; then exit 1; fi
grep -Fq "MAKEFILE_LIST must not be overridden" "$TEMP_ROOT/environment-list.out"
PRELOADED="$TEMP_ROOT/preloaded.mk"
printf '%s\n' 'ROOT := /tmp/preloaded' >"$PRELOADED"
if (cd "$CONTROL_DIR" && MAKEFILES="$PRELOADED" /usr/bin/make --no-print-directory --file "$MAKEFILE" check) >"$TEMP_ROOT/preloaded.out" 2>&1; then exit 1; fi
grep -Fq "MAKEFILES must be empty" "$TEMP_ROOT/preloaded.out"
EARLIER="$TEMP_ROOT/earlier.mk"
printf '%s\n' '# earlier' >"$EARLIER"
if (cd "$CONTROL_DIR" && /usr/bin/make --no-print-directory --file "$EARLIER" --file "$MAKEFILE" check) >"$TEMP_ROOT/multiple.out" 2>&1; then exit 1; fi
grep -Fq "repository Makefile path could not be resolved" "$TEMP_ROOT/multiple.out"
printf '%s\n' "Makefile root tests passed: 77 executed target/authority cases and 20 invalid-runtime, function, file-list, preload, or multi-Makefile rejections"
