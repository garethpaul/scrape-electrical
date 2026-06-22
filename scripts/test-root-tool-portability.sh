#!/bin/sh
set -eu

SCRIPT_DIR=${0%/*}
[ "$SCRIPT_DIR" != "$0" ] || SCRIPT_DIR=.
ROOT_DIR=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd -P)
ROOT_CHECK="$ROOT_DIR/scripts/test-makefile-root.sh"
TEMP_ROOT=$(mktemp -d "${TMPDIR:-/tmp}/scrape-electrical-tool-portability-XXXXXX")
trap 'rm -rf "$TEMP_ROOT"' EXIT HUP INT TERM

resolve_external() {
  command_name=$1
  command_path=$(command -v "$command_name" 2>/dev/null || :)
  case "$command_path" in
    /*) printf '%s\n' "$command_path"; return ;;
  esac

  old_ifs=$IFS
  IFS=:
  for directory in $PATH; do
    [ -n "$directory" ] || directory=.
    if [ -x "$directory/$command_name" ] && [ ! -d "$directory/$command_name" ]; then
      (CDPATH= cd -- "$directory" && printf '%s/%s\n' "$(pwd -P)" "$command_name")
      IFS=$old_ifs
      return
    fi
  done
  IFS=$old_ifs
  printf '%s\n' "host test prerequisite unavailable: $command_name" >&2
  exit 1
}

PORTABLE_BIN="$TEMP_ROOT/portable-bin"
MISSING_GREP_BIN="$TEMP_ROOT/missing-grep-bin"
TOOL_LOG="$TEMP_ROOT/tools.log"
mkdir "$PORTABLE_BIN" "$MISSING_GREP_BIN"

for command_name in cat chmod cp env grep make mkdir mktemp rm sed; do
  command_path=$(resolve_external "$command_name")
  cat >"$PORTABLE_BIN/$command_name" <<EOF
#!/bin/sh
printf '%s\n' '$command_name' >> '$TOOL_LOG'
exec '$command_path' "\$@"
EOF
  chmod +x "$PORTABLE_BIN/$command_name"
  if [ "$command_name" != grep ]; then
    cp "$PORTABLE_BIN/$command_name" "$MISSING_GREP_BIN/$command_name"
  fi
done

if awk '/\/(usr\/bin\/(sed|grep|make)|bin\/pwd)([^[:alnum:]_]|$)/ { found = 1 } END { exit found ? 0 : 1 }' "$ROOT_CHECK"; then
  printf '%s\n' 'root checker must not depend on macOS absolute tool paths' >&2
  exit 1
fi

PATH="$PORTABLE_BIN" /bin/sh "$ROOT_CHECK" >"$TEMP_ROOT/portable.out" 2>&1
for command_name in grep make mktemp sed; do
  if ! awk -v expected="$command_name" '$0 == expected { found = 1 } END { exit found ? 0 : 1 }' "$TOOL_LOG"; then
    printf '%s\n' "portable PATH did not exercise discovered $command_name" >&2
    exit 1
  fi
done

if PATH="$MISSING_GREP_BIN" /bin/sh "$ROOT_CHECK" >"$TEMP_ROOT/missing-grep.out" 2>&1; then
  printf '%s\n' 'root checker accepted an environment without required grep' >&2
  exit 1
fi
if ! awk 'index($0, "required POSIX tool unavailable: grep") { found = 1 } END { exit found ? 0 : 1 }' "$TEMP_ROOT/missing-grep.out"; then
  printf '%s\n' 'root checker did not fail closed with the missing grep diagnostic' >&2
  cat "$TEMP_ROOT/missing-grep.out" >&2
  exit 1
fi

printf '%s\n' 'Root-tool portability tests passed: hostile PATH and missing-tool rejection'
