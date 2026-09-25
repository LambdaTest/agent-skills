#!/bin/sh
# kane-cli ready check (preflight).
#
# Prints, in one call, everything an agent needs to know before it starts a
# kane-cli run. It only reads status. It changes nothing: no sign-in, no
# config write, no install, no network call of its own. It never reads
# credential files. It always exits 0, and problems show up in the text.
#
# Usage: sh preflight.sh [--mobile emulator|simulator] [--grid]
#
# Output is plain text in "## <section>" blocks, always in this order:
#   version       kane-cli --version, or the word "missing"
#   whoami        kane-cli whoami, then exit=<code>
#   balance       kane-cli balance, then exit=<code>
#   settings      kane-cli config show, then exit=<code>
#   agent-config  saved agent preferences, or the word "none"
#   env           ci= ssh= display= os= arch= node=
#   chrome        found=<path> and override=<KANE_CLI_CHROME_PATH>
#   app           port=<n> for each local dev port with a listener
#   tests         count=<n> of *_test.md files within four directory levels
#   mobile        only with --mobile: kane-cli doctor --target <kind>
#   grid          only with --grid: kane-cli plugin doctor remote-execution
# When kane-cli is missing, every command block holds the word "missing".
# whoami, balance and settings run at the same time to keep the check quick.

DEV_PORTS="3000 3001 4200 4321 5173 5174 8000 8080 8888"

mobile_asked=no
mobile=""
grid=no
while [ $# -gt 0 ]; do
  case "$1" in
    --mobile)
      mobile_asked=yes
      case "${2:-}" in
        "" | --*) mobile="" ;;
        *) mobile=$2; shift ;;
      esac
      ;;
    --mobile=*) mobile_asked=yes; mobile=${1#--mobile=} ;;
    --grid) grid=yes ;;
    *) ;;
  esac
  shift
done
case "$mobile" in
  emulator | simulator) mobile_ok=yes ;;
  *) mobile_ok=no ;;
esac

have_cli=no
if command -v kane-cli >/dev/null 2>&1; then have_cli=yes; fi

# Scratch space for the parallel calls. Removed on every way out.
work=$(mktemp -d "${TMPDIR:-/tmp}/kane-preflight.XXXXXX" 2>/dev/null) || work=""
cleanup() {
  if [ -n "$work" ] && [ -d "$work" ]; then rm -rf "$work"; fi
}
trap cleanup EXIT
trap 'exit 1' HUP INT TERM

# start_bg <key> <command...>: run in the background, keep output and code.
start_bg() {
  bg_key=$1
  shift
  ( "$@" >"$work/$bg_key.out" 2>&1 </dev/null; echo $? >"$work/$bg_key.code" ) &
}

# emit_cmd <key> <command...>: print the block body for one kane-cli call.
emit_cmd() {
  emit_key=$1
  shift
  if [ "$have_cli" != yes ]; then
    echo "missing"
    return 0
  fi
  if [ -n "$work" ] && [ -f "$work/$emit_key.code" ]; then
    cat "$work/$emit_key.out"
    # Keep exit= on its own line when the output has no final newline.
    if [ -n "$(tail -c 1 "$work/$emit_key.out")" ]; then echo; fi
    echo "exit=$(cat "$work/$emit_key.code")"
  else
    # No scratch space: run it now instead.
    emit_out=$("$@" 2>&1 </dev/null)
    emit_code=$?
    if [ -n "$emit_out" ]; then printf '%s\n' "$emit_out"; fi
    echo "exit=$emit_code"
  fi
}

if [ -n "$work" ]; then
  if [ "$have_cli" = yes ]; then
    start_bg whoami kane-cli whoami
    start_bg balance kane-cli balance
    start_bg settings kane-cli config show
    if [ "$mobile_ok" = yes ]; then start_bg mobile kane-cli doctor --target "$mobile"; fi
    if [ "$grid" = yes ]; then start_bg grid kane-cli plugin doctor remote-execution; fi
  fi
  # Listening sockets, numeric only (no DNS, no service names) so it stays quick.
  if command -v lsof >/dev/null 2>&1; then
    lsof -nP -iTCP:"$(echo "$DEV_PORTS" | tr ' ' ',')" -sTCP:LISTEN -Fn >"$work/ports.raw" 2>/dev/null </dev/null &
  elif command -v ss >/dev/null 2>&1; then
    ss -ltn >"$work/ports.raw" 2>/dev/null </dev/null &
  elif command -v netstat >/dev/null 2>&1; then
    ( netstat -an 2>/dev/null </dev/null | grep -i listen >"$work/ports.raw" ) &
  fi
fi

echo "## version"
if [ "$have_cli" = yes ]; then
  version=$(kane-cli --version 2>/dev/null </dev/null)
  if [ -z "$version" ]; then version=$(kane-cli --version 2>&1 </dev/null); fi
  printf '%s\n' "$version"
else
  echo "missing"
fi

wait

echo "## whoami"
emit_cmd whoami kane-cli whoami

echo "## balance"
emit_cmd balance kane-cli balance

echo "## settings"
emit_cmd settings kane-cli config show

echo "## agent-config"
agent_config="$HOME/.testmuai/kaneai/agent-config/config.json"
if [ -f "$agent_config" ] && [ -r "$agent_config" ]; then
  cat "$agent_config"
  if [ -n "$(tail -c 1 "$agent_config")" ]; then echo; fi
else
  echo "none"
fi

echo "## env"
os_name=$(uname -s 2>/dev/null)
if [ -n "${SSH_CONNECTION:-}" ] || [ -n "${SSH_TTY:-}" ]; then ssh_session=yes; else ssh_session=no; fi
case "$os_name" in
  # macOS always has a screen. So does Windows under Git Bash, MSYS or Cygwin.
  Darwin | MINGW* | MSYS* | CYGWIN*)
    if [ "$ssh_session" = yes ]; then display=no; else display=yes; fi
    ;;
  *)
    if [ -n "${DISPLAY:-}" ] || [ -n "${WAYLAND_DISPLAY:-}" ]; then display=yes; else display=no; fi
    ;;
esac
echo "ci=${CI:-}"
echo "ssh=$ssh_session"
echo "display=$display"
echo "os=$os_name"
echo "arch=$(uname -m 2>/dev/null)"
echo "node=$(node --version 2>/dev/null </dev/null)"

echo "## chrome"
chrome_found=""
for candidate in \
  "${KANE_CLI_CHROME_PATH:-}" \
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  "/usr/bin/google-chrome" \
  "/usr/bin/google-chrome-stable" \
  "$(command -v google-chrome 2>/dev/null)" \
  "/c/Program Files/Google/Chrome/Application/chrome.exe" \
  "/c/Program Files (x86)/Google/Chrome/Application/chrome.exe" \
  "${LOCALAPPDATA:-}/Google/Chrome/Application/chrome.exe"; do
  if [ -n "$candidate" ] && [ -f "$candidate" ]; then
    chrome_found=$candidate
    break
  fi
done
echo "found=$chrome_found"
echo "override=${KANE_CLI_CHROME_PATH:-}"

echo "## app"
if [ -n "$work" ] && [ -s "$work/ports.raw" ]; then
  for port in $DEV_PORTS; do
    # The local address ends in :<port> (lsof, ss, Windows netstat) or
    # .<port> (BSD netstat). A listener's remote side never carries a port.
    if grep -E "[:.]$port([[:space:]]|\$)" "$work/ports.raw" >/dev/null 2>&1; then
      echo "port=$port"
    fi
  done
fi

echo "## tests"
test_count=$(find . -maxdepth 4 \( -name node_modules -o -name .git \) -prune -o -type f -name '*_test.md' -print 2>/dev/null | wc -l | tr -d ' ')
echo "count=${test_count:-0}"

if [ "$mobile_asked" = yes ]; then
  echo "## mobile"
  if [ "$mobile_ok" = yes ]; then
    emit_cmd mobile kane-cli doctor --target "$mobile"
  else
    echo "invalid target"
  fi
fi

if [ "$grid" = yes ]; then
  echo "## grid"
  emit_cmd grid kane-cli plugin doctor remote-execution
fi

exit 0
