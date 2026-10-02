"""Follow up once on Joe referrals that got no reply.

Run with imail's python: PY=~/.local/share/uv/tools/imail-mcp/bin/python

  $PY followup.py scan [--min-days 3] > fu.json
      Email-ledger entries referred >= min-days ago, with no inbound reply since and no
      follow-up already sent (ledger 'followup' field or an earlier follow-up in Sent Mail).
  $PY followup.py send fu.json
      One short note per entry in the original thread, cc Joe, resume attached; stamps the
      ledger 'followup' date per send so a re-run never double-sends.
"""
import datetime
import json
import re
import sys

from imail import mail

import refer

A = refer.FROM
FMT = re.compile(r"(\w+), (\w+) (\d+), (\d{4}) at")


def day(s: str) -> datetime.date:
    m = FMT.search(s)
    return datetime.datetime.strptime(f"{m[2]} {m[3]} {m[4]}", "%B %d %Y").date()


def sent_followups() -> set[str]:
    out = mail.run_as(f'''tell application "Mail"
set out to ""
set mb to mailbox "[Gmail]/Sent Mail" of account "{A}"
repeat with i from 1 to 300
 try
  set m to message i of mb
  if content of m contains "follow up on my note about" or content of m contains "following up on my note" then
   repeat with x in to recipients of m
    set out to out & address of x & linefeed
   end repeat
  end if
 end try
end repeat
return out
end tell''')
    return {a.strip().lower() for a in out.splitlines() if a.strip()}


def scan(min_days: int) -> None:
    led, today = refer.ledger(), datetime.date.today()
    already = sent_followups()
    inbox = mail.list_messages(account=A, limit=900)
    out = []
    for e in led:
        if e.get("channel", "email") != "email" or e.get("followup") or e["email"].lower() in already:
            continue
        sent = datetime.date.fromisoformat(e["date"])
        if (today - sent).days < min_days:
            continue
        replies = [m["subject"] for m in inbox
                   if refer.addr(m["sender"]) == e["email"].lower() and day(m["date"]) > sent
                   and re.match(r"(re|fw|fwd):", m["subject"], re.I)]
        if replies:
            continue
        out.append({**e, "days": (today - sent).days})
    print(json.dumps(out, indent=1))


def body(e: dict) -> str:
    first = re.sub(r"[^a-z]", "", e["name"].split()[0].lower()) or "there"
    role = f" for the {e['role'].lower()} role" if e.get("role") else ""
    return (f"hi {first}, following up on my note about joe heupler{role}. "
            f"he's a us citizen and berkeley grad with production ai agent, python and data platform work, "
            f"and he'd be a great person to talk to. he's cc'd, so please reach him directly at {refer.JOE}."
            f"\n\nresume attached again, more at josephheupler.com.\n\nmisha")


def send(path: str) -> None:
    led = refer.ledger()
    for e in json.load(open(path)):
        row = next(x for x in led if x["email"].lower() == e["email"].lower())
        if row.get("followup"):
            print("SKIP already followed up", e["email"]); continue
        try:
            mail.send_message(to=e["email"], subject=(f"Re: referral for your {e['role'].lower()} role" if e.get("role") else "Re: referral for Joe Heupler"), body=body(e),
                              from_addr=refer.FROM, cc=refer.JOE, attachments=[refer.RESUME], is_markdown=False)
        except Exception as err:  # report loudly, keep going
            print("FAIL", e["email"], err); continue
        row["followup"] = str(datetime.date.today())
        refer.LEDGER.write_text(json.dumps(led, indent=1))
        print("SENT", e["email"])


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["scan"]:
        scan(int(a[a.index("--min-days") + 1]) if "--min-days" in a else 3)
    elif a[:1] == ["send"] and len(a) == 2:
        send(a[1])
    else:
        sys.exit(__doc__)
