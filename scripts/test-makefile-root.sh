#!/bin/sh
set -eu

require_posix_tool() {
  tool_name=$1
  tool_path=$(command -v "$tool_name" 2>/dev/null || :)
  case "$tool_path" in
    /*) ;;
    *) tool_path= ;;
  esac
  if [ -z "$tool_path" ] || [ ! -x "$tool_path" ] || [ -d "$tool_path" ]; then
    printf '%s\n' "required POSIX tool unavailable: $tool_name" >&2
    exit 1
  fi
  printf '%s\n' "$tool_path"
}

CAT=$(require_posix_tool cat)
CHMOD=$(require_posix_tool chmod)
CP=$(require_posix_tool cp)
ENV=$(require_posix_tool env)
GREP=$(require_posix_tool grep)
MAKE=$(require_posix_tool make)
MKDIR=$(require_posix_tool mkdir)
MKTEMP=$(require_posix_tool mktemp)
RM=$(require_posix_tool rm)
SED=$(require_posix_tool sed)

assert_file_contains() {
  expected=$1
  file=$2
  "$GREP" -Fq "$expected" "$file"
}

SCRIPT_DIR=${0%/*}
[ "$SCRIPT_DIR" != "$0" ] || SCRIPT_DIR=.
ROOT_DIR=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd -P)
if ! "$SED" -n '1,2p' "$ROOT_DIR/tests/test_scrape.py" | "$GREP" -Eiq 'coding[=:][[:space:]]*utf-?8'; then
  printf '%s\n' 'tests/test_scrape.py must declare UTF-8 for Python 2 compilation' >&2
  exit 1
fi
TEMP_ROOT=$("$MKTEMP" -d "${TMPDIR:-/tmp}/scrape-electrical-root-control-XXXXXX")
ATTACKER_ROOT="$TEMP_ROOT/attacker-root"
cleanup() {
  "$RM" -rf "$TEMP_ROOT"
}
trap cleanup EXIT HUP INT TERM
unset MAKEFILES MAKEFILE_LIST MAKEFLAGS MFLAGS MAKEOVERRIDES ROOT PYTHON PYTHONDONTWRITEBYTECODE

CONTROL_DIR="$TEMP_ROOT/control"
CHECKOUT="$TEMP_ROOT/scrape-electrical's [gate] \"quoted\" \`touch SCRAPE_ELECTRICAL_BACKTICK_MARKER\`"
COMMAND_LOG="$TEMP_ROOT/commands.log"
BAD_COMMAND_LOG="$TEMP_ROOT/bad-command.log"
FAKE_SHELL_LOG="$TEMP_ROOT/fake-shell.log"
"$MKDIR" "$CONTROL_DIR" "$CHECKOUT" "$CHECKOUT/scripts" "$CHECKOUT/bin" "$ATTACKER_ROOT"
CONTROL_DIR=$(CDPATH= cd -- "$CONTROL_DIR" && pwd -P)
CHECKOUT=$(CDPATH= cd -- "$CHECKOUT" && pwd -P)
MAKEFILE="$CHECKOUT/Makefile"
"$CP" "$ROOT_DIR/Makefile" "$MAKEFILE"

for command in python2 python3; do
  "$CAT" >"$CHECKOUT/bin/$command" <<'EOF'
#!/bin/sh
printf '%s|%s|%s|%s\n' "$PWD" "$0" "${PYTHONDONTWRITEBYTECODE:-}" "$*" >> "$SCRAPE_ELECTRICAL_COMMAND_LOG"
EOF
  "$CHMOD" +x "$CHECKOUT/bin/$command"
done
"$CAT" >"$CHECKOUT/scripts/test-makefile-root.sh" <<'EOF'
#!/bin/sh
printf '%s|%s|%s|root-test\n' "$PWD" "$0" "${PYTHONDONTWRITEBYTECODE:-}" >> "$SCRAPE_ELECTRICAL_COMMAND_LOG"
EOF
"$CHMOD" +x "$CHECKOUT/scripts/test-makefile-root.sh"
"$CAT" >"$CHECKOUT/scripts/test-root-tool-portability.sh" <<'EOF'
#!/bin/sh
printf '%s|%s|%s|root-tool-portability\n' "$PWD" "$0" "${PYTHONDONTWRITEBYTECODE:-}" >> "$SCRAPE_ELECTRICAL_COMMAND_LOG"
EOF
"$CHMOD" +x "$CHECKOUT/scripts/test-root-tool-portability.sh"

BAD_COMMAND="$TEMP_ROOT/bad-command"
"$CAT" >"$BAD_COMMAND" <<EOF
#!/bin/sh
printf '%s\n' invoked >> '$BAD_COMMAND_LOG'
exit 91
EOF
"$CHMOD" +x "$BAD_COMMAND"

FAKE_SHELL="$TEMP_ROOT/fake-shell"
"$CAT" >"$FAKE_SHELL" <<EOF
#!/bin/sh
printf '%s\n' invoked >> '$FAKE_SHELL_LOG'
exec /bin/sh "\$@"
EOF
"$CHMOD" +x "$FAKE_SHELL"

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
  "$RM" -f "$COMMAND_LOG" "$BAD_COMMAND_LOG" "$FAKE_SHELL_LOG"
  output="$TEMP_ROOT/output"
  set +e
  case "$mode" in
    default)
      (cd "$CONTROL_DIR" && PATH="$CHECKOUT/bin:$PATH" SCRAPE_ELECTRICAL_COMMAND_LOG="$COMMAND_LOG" "$MAKE" --no-print-directory --file "$MAKEFILE" "$target") >"$output" 2>&1 ;;
    command-python3)
      (cd "$CONTROL_DIR" && PATH="$CHECKOUT/bin:$PATH" SCRAPE_ELECTRICAL_COMMAND_LOG="$COMMAND_LOG" "$MAKE" --no-print-directory --file "$MAKEFILE" PYTHON=python3 "$target") >"$output" 2>&1 ;;
    environment-python3)
      (cd "$CONTROL_DIR" && PATH="$CHECKOUT/bin:$PATH" PYTHON=python3 SCRAPE_ELECTRICAL_COMMAND_LOG="$COMMAND_LOG" "$MAKE" --no-print-directory --file "$MAKEFILE" "$target") >"$output" 2>&1 ;;
    command-root)
      (cd "$CONTROL_DIR" && PATH="$CHECKOUT/bin:$PATH" SCRAPE_ELECTRICAL_COMMAND_LOG="$COMMAND_LOG" "$MAKE" --no-print-directory --file "$MAKEFILE" "ROOT=$ATTACKER_ROOT" "$target") >"$output" 2>&1 ;;
    environment-root)
      (cd "$CONTROL_DIR" && PATH="$CHECKOUT/bin:$PATH" ROOT="$ATTACKER_ROOT" SCRAPE_ELECTRICAL_COMMAND_LOG="$COMMAND_LOG" "$MAKE" --no-print-directory --file "$MAKEFILE" "$target") >"$output" 2>&1 ;;
    command-shell)
      (cd "$CONTROL_DIR" && PATH="$CHECKOUT/bin:$PATH" SCRAPE_ELECTRICAL_COMMAND_LOG="$COMMAND_LOG" "$MAKE" --no-print-directory --file "$MAKEFILE" "SHELL=$FAKE_SHELL" "$target") >"$output" 2>&1 ;;
    environment-shell)
      (cd "$CONTROL_DIR" && PATH="$CHECKOUT/bin:$PATH" SHELL="$FAKE_SHELL" SCRAPE_ELECTRICAL_COMMAND_LOG="$COMMAND_LOG" "$MAKE" --no-print-directory --file "$MAKEFILE" "$target") >"$output" 2>&1 ;;
    command-flags)
      (cd "$CONTROL_DIR" && PATH="$CHECKOUT/bin:$PATH" SCRAPE_ELECTRICAL_COMMAND_LOG="$COMMAND_LOG" "$MAKE" --no-print-directory --file "$MAKEFILE" '.SHELLFLAGS=-eu -c' "$target") >"$output" 2>&1 ;;
    environment-flags)
      (cd "$CONTROL_DIR" && "$ENV" '.SHELLFLAGS=-eu -c' PATH="$CHECKOUT/bin:$PATH" SCRAPE_ELECTRICAL_COMMAND_LOG="$COMMAND_LOG" "$MAKE" --no-print-directory --file "$MAKEFILE" "$target") >"$output" 2>&1 ;;
    command-bytecode)
      (cd "$CONTROL_DIR" && PATH="$CHECKOUT/bin:$PATH" SCRAPE_ELECTRICAL_COMMAND_LOG="$COMMAND_LOG" "$MAKE" --no-print-directory --file "$MAKEFILE" PYTHONDONTWRITEBYTECODE=0 "$target") >"$output" 2>&1 ;;
    environment-bytecode)
      (cd "$CONTROL_DIR" && PATH="$CHECKOUT/bin:$PATH" PYTHONDONTWRITEBYTECODE=0 SCRAPE_ELECTRICAL_COMMAND_LOG="$COMMAND_LOG" "$MAKE" --no-print-directory --file "$MAKEFILE" "$target") >"$output" 2>&1 ;;
    *)
      printf '%s\n' "unknown test mode: $mode" >&2
      exit 1 ;;
  esac
  result=$?
  set -e
  if [ "$result" -ne 0 ]; then
    printf '%s\n' "$scenario $target failed" >&2
    "$CAT" "$output" >&2
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
  case "$target" in
    build|check|lint|verify)
      if ! assert_file_contains 'compile(open("tests/test_scrape.py", "rb").read(), "tests/test_scrape.py", "exec")' "$COMMAND_LOG"; then
        printf '%s\n' "$scenario $target skipped the Python 2 test-module compile gate" >&2
        exit 1
      fi
      ;;
  esac
  case "$target" in
    check|root-test|verify)
      if ! assert_file_contains 'root-tool-portability' "$COMMAND_LOG"; then
        printf '%s\n' "$scenario $target skipped the hostile PATH portability gate" >&2
        exit 1
      fi
      ;;
  esac
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

  if (cd "$CONTROL_DIR" && PATH="$CHECKOUT/bin:$PATH" SCRAPE_ELECTRICAL_COMMAND_LOG="$COMMAND_LOG" "$MAKE" --no-print-directory --file "$MAKEFILE" "PYTHON=$BAD_COMMAND" "$target") >"$TEMP_ROOT/invalid-command.out" 2>&1; then exit 1; fi
  assert_file_contains "PYTHON must be exactly python2 or python3" "$TEMP_ROOT/invalid-command.out"
  if (cd "$CONTROL_DIR" && PATH="$CHECKOUT/bin:$PATH" PYTHON="$BAD_COMMAND" SCRAPE_ELECTRICAL_COMMAND_LOG="$COMMAND_LOG" "$MAKE" --no-print-directory --file "$MAKEFILE" "$target") >"$TEMP_ROOT/invalid-environment.out" 2>&1; then exit 1; fi
  assert_file_contains "PYTHON must be exactly python2 or python3" "$TEMP_ROOT/invalid-environment.out"
done

if [ -e "$CONTROL_DIR/SCRAPE_ELECTRICAL_BACKTICK_MARKER" ] || [ -e "$BAD_COMMAND_LOG" ]; then
  printf '%s\n' "checkout path or invalid Python executed a command" >&2
  exit 1
fi

FUNCTION_MARKER="$CONTROL_DIR/SCRAPE_ELECTRICAL_FUNCTION_MARKER"
if (cd "$CONTROL_DIR" && "$MAKE" --no-print-directory --file "$MAKEFILE" 'PYTHON=$(shell touch SCRAPE_ELECTRICAL_FUNCTION_MARKER)' check) >"$TEMP_ROOT/function-command.out" 2>&1; then exit 1; fi
assert_file_contains "PYTHON must be exactly python2 or python3" "$TEMP_ROOT/function-command.out"
if (cd "$CONTROL_DIR" && "$ENV" 'PYTHON=$(shell touch SCRAPE_ELECTRICAL_FUNCTION_MARKER)' "$MAKE" --no-print-directory --file "$MAKEFILE" check) >"$TEMP_ROOT/function-environment.out" 2>&1; then exit 1; fi
assert_file_contains "PYTHON must be exactly python2 or python3" "$TEMP_ROOT/function-environment.out"
[ ! -e "$FUNCTION_MARKER" ]

if (cd "$CONTROL_DIR" && "$MAKE" --no-print-directory --file "$MAKEFILE" MAKEFILE_LIST=/tmp/untrusted check) >"$TEMP_ROOT/command-list.out" 2>&1; then exit 1; fi
assert_file_contains "MAKEFILE_LIST must not be overridden" "$TEMP_ROOT/command-list.out"
if (cd "$CONTROL_DIR" && MAKEFILE_LIST=/tmp/untrusted "$MAKE" --environment-overrides --no-print-directory --file "$MAKEFILE" check) >"$TEMP_ROOT/environment-list.out" 2>&1; then exit 1; fi
assert_file_contains "MAKEFILE_LIST must not be overridden" "$TEMP_ROOT/environment-list.out"
PRELOADED="$TEMP_ROOT/preloaded.mk"
printf '%s\n' 'ROOT := /tmp/preloaded' >"$PRELOADED"
if (cd "$CONTROL_DIR" && MAKEFILES="$PRELOADED" "$MAKE" --no-print-directory --file "$MAKEFILE" check) >"$TEMP_ROOT/preloaded.out" 2>&1; then exit 1; fi
assert_file_contains "MAKEFILES must be empty" "$TEMP_ROOT/preloaded.out"
EARLIER="$TEMP_ROOT/earlier.mk"
printf '%s\n' '# earlier' >"$EARLIER"
if (cd "$CONTROL_DIR" && "$MAKE" --no-print-directory --file "$EARLIER" --file "$MAKEFILE" check) >"$TEMP_ROOT/earlier-multiple.out" 2>&1; then exit 1; fi
assert_file_contains "repository Makefile path could not be resolved" "$TEMP_ROOT/earlier-multiple.out"
LATER="$TEMP_ROOT/later.mk"
LATER_MARKER="$TEMP_ROOT/later-marker"
"$CAT" >"$LATER" <<EOF
build:
	@printf owned > "$LATER_MARKER"
EOF
if (cd "$CONTROL_DIR" && "$MAKE" --no-print-directory --file "$MAKEFILE" --file "$LATER" build) >"$TEMP_ROOT/later-multiple.out" 2>&1; then exit 1; fi
assert_file_contains "repository Makefile must be loaded alone" "$TEMP_ROOT/later-multiple.out"
[ ! -e "$LATER_MARKER" ]
printf '%s\n' "Makefile root tests passed: 77 executed target/authority cases and 21 invalid-runtime, function, file-list, preload, or multi-Makefile rejections"
