#!/bin/zsh
# finish-vercel-setup.sh — one command, one tap, everything else automatic.
#
#   ~/.claude/skills/vercel-login-auto/finish-vercel-setup.sh [account-email] [repo ...]
#   ~/.claude/skills/vercel-login-auto/finish-vercel-setup.sh engineering@eriaevents.co ~/dev/eria-website
#
# Works for ANY Vercel account signed in on this machine and ANY projects: the
# account is an argument, the teams are read back from the login, and project
# identity comes from each repo's .vercel/project.json. Nothing is hardcoded.
#
# Order of operations:
#   1. Already authorised? Skip to step 2.
#   2. Open the device page in the Chrome profile whose PRIMARY account matches
#      (never one where it is merely secondary — that is how a personal tool
#      ends up authorised inside a client org), then WAIT while you click
#      "Allow Access". The script does not click it: that approval is the one
#      step whose value is that a person performed it. Everything on either
#      side of it is automated so the click is all you ever do.
#   3. `vgate sync`, VERIFIED against `vgate ls` — a silent sync failure looks
#      identical to success and only surfaces days later as "expired".
#   4. Deploy the given repos (or `sitedeploy all`), then verify.
#
# Never `vercel logout` (destroys the only stored credential) and never
# `vgate switch`/`use` — Vercel auth is global on this machine, so pinning a
# client team makes it the default for every session. Pass --scope instead.
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ACCOUNT="${1:-michaelle.lubich@gmail.com}"
[ $# -gt 0 ] && shift
REPOS=("$@")
WAIT_SECONDS="${WAIT_SECONDS:-300}"

bold() { printf '\033[1m%s\033[0m\n' "$*"; }
ok()   { printf '\033[32m✓\033[0m %s\n' "$*"; }
bad()  { printf '\033[31m✗\033[0m %s\n' "$*"; }
say()  { printf '\033[36m→\033[0m %s\n' "$*"; }
die()  { bad "$*"; exit 1; }

authorised() {
  case "$(vercel whoami 2>&1 | tail -1)" in
    *"Not authorized"*|*Error*) return 1 ;;
    *) return 0 ;;
  esac
}

# ── 1. sign in, if needed ────────────────────────────────────────────────────
if authorised; then
  WHO="$(vercel whoami 2>&1 | tail -1)"
  ok "already signed in as $WHO"
else
  bold "Step 1 — sign the Vercel CLI in as $ACCOUNT"

  PROFILE="$(python3 "$HERE/resolve-chrome-profile.py" "$ACCOUNT" 2>/dev/null)" \
    || die "no Chrome profile has $ACCOUNT as its PRIMARY account. Pass a profile directory instead, or sign Chrome in with it first."
  say "account $ACCOUNT → Chrome profile '$PROFILE'"

  LOG="$(mktemp)"
  ( vercel login >"$LOG" 2>&1 ) &
  LOGIN_PID=$!

  URL=""
  for _ in $(seq 1 30); do
    URL="$(tr -d '\r' <"$LOG" | grep -o 'https://vercel.com/oauth/device?user_code=[A-Z-]*' | head -1)"
    [ -n "$URL" ] && break
    sleep 1
  done
  [ -n "$URL" ] || { kill "$LOGIN_PID" 2>/dev/null; die "vercel login printed no device URL:
$(cat "$LOG")"; }

  open -na "Google Chrome" --args --profile-directory="$PROFILE" "$URL"

  printf '\n'
  bold "   >>> Click \"Allow Access\" in the window that just opened <<<"
  printf '   %s\n' "$URL"
  printf '   Code: \033[1m%s\033[0m\n\n' "${URL##*=}"
  say "If you get a login form instead of an Allow button, sign in to vercel.com"
  say "as $ACCOUNT once in that profile — until then Allow renders DISABLED and"
  say "no amount of retrying gets past it. One-time, per profile."

  # Poll the real condition. The CLI process exiting is not proof of success.
  say "waiting up to ${WAIT_SECONDS}s for the approval…"
  for _ in $(seq 1 "$WAIT_SECONDS"); do
    authorised && break
    kill -0 "$LOGIN_PID" 2>/dev/null || { sleep 2; break; }
    sleep 1
  done
  kill "$LOGIN_PID" 2>/dev/null
  rm -f "$LOG"

  authorised || die "not authorised — the approval never landed. Device codes expire in ~10 minutes: re-run and click promptly, or sign in to vercel.com in '$PROFILE' first."
  WHO="$(vercel whoami 2>&1 | tail -1)"
  ok "signed in as $WHO"
fi

# ── 2. persist it, verified ──────────────────────────────────────────────────
bold "Step 2 — store the credential so it stays switchable"
if command -v vgate >/dev/null; then
  vgate sync >/dev/null 2>&1 || say "vgate sync returned non-zero"
  STORED="$(vgate ls 2>/dev/null | grep -iF "$WHO" | head -1 | tr -s ' ')"
  case "$STORED" in
    *expired*|"") bad "vgate did not store '$WHO' as valid — check: vgate ls" ;;
    *) ok "vgate: $STORED" ;;
  esac
else
  say "vgate not installed — skipping"
fi

TEAMS="$(vercel teams ls 2>/dev/null | sed -n '/^ *id/,$p' | tail -n +2 | awk 'NF')"
[ -n "$TEAMS" ] && { say "teams this login can act on (pass --scope <id>):"; printf '%s\n' "$TEAMS"; }

# ── 3. deploy and verify ─────────────────────────────────────────────────────
bold "Step 3 — deploy and verify"
if [ ${#REPOS[@]} -eq 0 ]; then
  if command -v sitedeploy >/dev/null; then
    say "no repos given → sitedeploy all"
    sitedeploy all && sitedeploy doctor
    exit $?
  fi
  say "nothing to deploy (pass repo paths, or install sitedeploy)"
  exit 0
fi

FAILED=0
for repo in "${REPOS[@]}"; do
  NAME="$(basename "$repo")"
  if [ ! -f "$repo/.vercel/project.json" ]; then
    bad "$NAME: no .vercel/project.json — run 'vercel link' in that repo once"
    FAILED=$((FAILED + 1)); continue
  fi
  SCOPE="$(jq -r '.orgId' "$repo/.vercel/project.json")"
  PROJ="$(jq -r '.projectName' "$repo/.vercel/project.json")"
  say "$PROJ (scope $SCOPE)"
  if ( cd "$repo" && vercel --prod --yes --scope "$SCOPE" ); then
    ok "$PROJ deployed"
  else
    bad "$PROJ failed"; FAILED=$((FAILED + 1))
  fi
done

printf '\n'
if [ "$FAILED" -eq 0 ]; then
  ok "all deploys reported success"
  say "Now confirm production actually serves it — a green build is not a deploy."
  say "sitedeploy doctor, or fetch each URL and grep a string only the new build has."
else
  die "$FAILED deploy(s) failed — read the output above, fix the cause, re-run."
fi
