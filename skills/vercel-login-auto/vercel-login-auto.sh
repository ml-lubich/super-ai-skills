#!/usr/bin/env bash
# Complete a `vercel login` device-code flow in a NAMED Chrome profile.
#
#   vercel-login-auto.sh michaelle.lubich@gmail.com
#   vercel-login-auto.sh engineering@eriaevents.co
#   vercel-login-auto.sh "Profile 2"            # directory name also accepted
#
# Why a script and not "just run vercel login": the CLI prints a device URL and
# blocks. Approving it needs a browser that is ALREADY signed into the right
# Vercel account, and on this machine several Chrome profiles are signed into
# different ones — including a client org. Opening the flow in whichever
# profile happens to be frontmost is how a personal tool ends up authorised
# against a client's account, so the profile is a required argument and is
# resolved by primary account, never guessed.
#
# PREREQUISITES (all one-time, all a human decision — see SKILL.md):
#   * Chrome: View > Developer > "Allow JavaScript from Apple Events"
#   * System Settings > Privacy & Security > Automation: allow the calling
#     terminal to control Google Chrome
#   * If run from an agent harness, that harness must permit `osascript`
#
# Never runs `vercel logout`: it destroys the only stored credential, and
# `vgate` can only re-save an ALREADY ACTIVE login, never revive a dead one.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ACCOUNT="${1:-}"
POLL_SECONDS="${VERCEL_LOGIN_TIMEOUT:-180}"

die() { printf '\033[31m✗\033[0m %b\n' "$*" >&2; exit 1; }
say() { printf '\033[36m→\033[0m %s\n' "$*"; }
ok()  { printf '\033[32m✓\033[0m %s\n' "$*"; }

[ -n "$ACCOUNT" ] || die "usage: $(basename "$0") <account-email|profile-directory> [more accounts…]"

# Several accounts = several SEPARATE logins, one after another: each gets its own
# `vercel login` process, its own device code, its own Chrome profile, its own
# approval and its own vgate sync. A code is never reused or shared across
# profiles. Vercel auth is global, so the LAST account listed ends up active.
if [ $# -gt 1 ]; then
  FAILED=""
  for acct in "$@"; do
    printf '\n\033[1m── %s ──\033[0m\n' "$acct"
    "$0" "$acct" || FAILED="$FAILED $acct"
  done
  [ -z "$FAILED" ] || die "login failed for:$FAILED"
  ok "all logins stored in vgate; active now: ${*: -1} (switch with: vgate switch <email>)"
  exit 0
fi
command -v vercel >/dev/null || die "vercel CLI not on PATH"
command -v osascript >/dev/null || die "osascript not available (macOS only)"

# ── 1. resolve the profile ───────────────────────────────────────────────────
if [[ "$ACCOUNT" == *@* ]]; then
  PROFILE="$(python3 "$HERE/resolve-chrome-profile.py" "$ACCOUNT")" || exit 1
  say "account $ACCOUNT -> Chrome profile '$PROFILE'"
else
  PROFILE="$ACCOUNT"
  say "using Chrome profile '$PROFILE' as given"
fi

# ── 2. start the login and capture the device URL ────────────────────────────
# One device code belongs to exactly ONE `vercel login` process. A second login
# started while another is still waiting puts two codes in flight; whichever
# is approved second gets "Could not verify user code" and nothing is stored.
# So: refuse to start on top of a pending login. Kill it (or let it finish)
# first — never share or re-enter a code between processes.
PENDING="$(pgrep -f 'vercel login' 2>/dev/null | tr '\n' ' ')"
if [ -n "$PENDING" ]; then
  die "another 'vercel login' is already waiting for approval (pid $PENDING).\n     Each login needs its own device code and its own approval. Finish or kill that one first:\n       kill $PENDING"
fi
LOG="$(mktemp -t vercel-login)"
vercel login >"$LOG" 2>&1 &
LOGIN_PID=$!
# The CLI prints "Visit https://vercel.com/oauth/device?user_code=XXXX-XXXX".
URL=""
for _ in $(seq 1 30); do
  sleep 1
  URL="$(grep -oE 'https://vercel\.com/oauth/device\?user_code=[A-Z0-9-]+' "$LOG" | head -1)"
  [ -n "$URL" ] && break
done
if [ -z "$URL" ]; then
  kill "$LOGIN_PID" 2>/dev/null
  die "vercel login printed no device URL in 30s:\n$(cat "$LOG")"
fi
ok "device URL: $URL"

# ── 3. open it in THAT profile ───────────────────────────────────────────────
open -na "Google Chrome" --args --profile-directory="$PROFILE" "$URL"
sleep 5

# ── 4. approve it ────────────────────────────────────────────────────────────
# Clicks by VISIBLE LABEL rather than a CSS selector: Vercel ships a hashed,
# frequently-rebuilt class soup, and a selector pinned to it silently stops
# matching after any redeploy — which looks exactly like "the login hung".
APPROVE_JS='
(() => {
  const wanted = ["confirm", "approve", "authorize", "continue", "verify"];
  const els = [...document.querySelectorAll("button, a, input[type=submit]")];
  const hit = els.find(el => {
    const t = ((el.innerText || el.value || "") + " " + (el.getAttribute("aria-label") || ""))
      .trim().toLowerCase();
    return t && wanted.some(w => t === w || t.startsWith(w + " ") || t.includes(w));
  });
  if (!hit) return "NO_BUTTON:" + document.title + "|" + document.body.innerText.slice(0, 200);
  hit.click();
  return "CLICKED:" + (hit.innerText || hit.value || "").trim();
})()
'
# Click only in the tab showing THIS login's code. "front window's active tab" can
# belong to another profile (or an older login's page), which approves the wrong
# account or a dead code.
CODE="${URL##*user_code=}"
RESULT="$(osascript \
  -e 'tell application "Google Chrome"' \
  -e '  repeat with w in windows' \
  -e '    repeat with t in tabs of w' \
  -e "      if URL of t contains \"$CODE\" then return execute t javascript \"$(printf '%s' "$APPROVE_JS" | tr '\n' ' ' | sed 's/"/\\"/g')\"" \
  -e '    end repeat' \
  -e '  end repeat' \
  -e "  return \"NO_TAB:no Chrome tab shows code $CODE\"" \
  -e 'end tell' 2>&1)"

case "$RESULT" in
  CLICKED*) ok "approved in browser (${RESULT#CLICKED:})" ;;
  NO_TAB*) say "${RESULT#NO_TAB:} yet — approve it by hand in profile '$PROFILE' (do NOT paste this code into another profile)" ;;
  NO_BUTTON*)
    # Two very different situations land here, and conflating them cost a day:
    #   (a) a profile already holding a valid session auto-confirmed — fine;
    #   (b) the profile is NOT signed in to vercel.com, so the page renders the
    #       login screen and "Allow Access" exists but is DISABLED. No amount of
    #       retrying or re-wording the click fixes (b): the account has to sign
    #       in to that Chrome profile once, by hand, before any of this works.
    DETAIL="${RESULT#NO_BUTTON:}"
    case "$DETAIL" in
      *"Log in to Vercel"*|*"Continue with Email"*|*"Sign Up"*)
        kill "$LOGIN_PID" 2>/dev/null
        die "Chrome profile '$PROFILE' is not signed in to vercel.com, so 'Allow Access' is disabled.\n     Sign in once as $ACCOUNT in that profile, then re-run this script — one-time per profile." ;;
      *) say "no approve control found — page may have auto-confirmed. Detail: $DETAIL" ;;
    esac ;;
  *)
    say "osascript did not report a click: $RESULT"
    say "If this says 'not allowed', the two Chrome/Automation prerequisites in SKILL.md are not granted yet." ;;
esac

# ── 5. wait for the CLI, then persist and VERIFY ─────────────────────────────
say "waiting up to ${POLL_SECONDS}s for the CLI to complete…"
for _ in $(seq 1 "$POLL_SECONDS"); do
  kill -0 "$LOGIN_PID" 2>/dev/null || break
  sleep 1
done
kill "$LOGIN_PID" 2>/dev/null

# The CLI's own log is the source of truth for "did the code get approved".
# `vercel whoami` can 401 on a perfectly healthy login, so it is NOT used as
# the health check; `vercel teams ls` is (it needs a working token).
if ! grep -q "signed in" "$LOG"; then
  printf '%s\n' "$(cat "$LOG")" >&2
  die "the CLI never reported 'signed in' — the device code was not approved (or was approved for a different, already-consumed code). Nothing was changed."
fi
TEAMS="$(vercel teams ls 2>&1 | grep -E '^\s*✔?\s*[a-z0-9-]+\s+' | awk '{print $NF}' | tr '\n' ' ')"
if [ -z "$TEAMS" ]; then
  die "CLI said signed in, but 'vercel teams ls' returned nothing — token unusable. Nothing was changed."
fi
WHO="$(vercel whoami 2>/dev/null | tail -1)"
[ -n "$WHO" ] || WHO="(whoami 401s — normal; teams: $TEAMS)"
ok "signed in as $WHO"

# ── 6. persist through vgate, and VERIFY it took ─────────────────────────────
# vgate SAVES an active login so it can be switched back to later; it cannot
# create one. Running it after — never instead of — the login is the whole
# point. It is also not optional: without it this login is not switchable, so
# the next session that needs a different account strands this one.
#
# Verified, not fire-and-forget: a silent `vgate sync` that failed looks exactly
# like one that worked, and the failure only surfaces days later as "expired".
if command -v vgate >/dev/null; then
  SYNCED="$(vgate sync 2>&1 | tail -1)"
  case "$ACCOUNT" in
    *@*)
      case "$SYNCED" in
        *"$ACCOUNT"*) ;;
        *) die "login completed, but for the WRONG account: $SYNCED (asked for $ACCOUNT).\n     The device page was approved in a Chrome profile signed in as someone else. Nothing more was changed." ;;
      esac ;;
  esac
  if [ -n "$SYNCED" ]; then
    STORED="$(vgate ls 2>/dev/null | grep -iF "$WHO" | head -1)"
    case "$STORED" in
      *expired*|"") say "vgate sync ran but '$WHO' is not stored as valid — check: vgate ls" ;;
      *) ok "vgate sync verified — $(printf '%s' "$STORED" | tr -s ' ')" ;;
    esac
  else
    say "vgate sync failed (login is still good; it just is not switchable yet)"
  fi
fi

# ── 7. report the teams this account can act on ──────────────────────────────
# Any account, any team, any project: the caller needs to know which `--scope`
# values this login unlocks. Never `vgate switch`/`use` to pin one — Vercel auth
# is global on this machine, so pinning a client team makes it the default for
# every session. Pass `--scope <team>` per command instead.
if TEAMS="$(vercel teams ls 2>/dev/null | sed -n '/^ *id/,$p' | tail -n +2 | awk 'NF' | head -20)"; then
  [ -n "$TEAMS" ] && { say "teams reachable with this login (use: vercel … --scope <id>):"; printf '%s\n' "$TEAMS"; }
fi
rm -f "$LOG"
