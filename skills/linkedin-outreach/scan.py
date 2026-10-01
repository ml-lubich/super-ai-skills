"""List LinkedIn threads that still need a referral reply.

Needs the linkedin-refer Chrome on CDP 9222 with /messaging/ open, plus `li` and `agent-browser`.
Usage: python3 scan.py [OUT.json] [--referee heupler]
Prints the candidate threads (last message is theirs, no referral yet, not excluded).
The job-vs-sales decision is left to the agent reading the output.
"""
import json, re, subprocess, sys, time

out = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('--') else 'candidates.json'
referee = sys.argv[sys.argv.index('--referee') + 1] if '--referee' in sys.argv else 'heupler'
EXCL = re.compile(r'\b(anduril|mach|echostar|dish)\b|perry barrow|w3sourcing', re.I)

def ab(js):
    return subprocess.run(['agent-browser', '--cdp', '9222', 'eval', js], capture_output=True, text=True).stdout.strip()

def li(*a):
    return json.loads(subprocess.run(['li', *a, '--json'], capture_output=True, text=True).stdout or '{}')

# Load the whole list (LinkedIn loads it lazily as you scroll)
for _ in range(15):
    ab("(()=>{const c=document.querySelector('.msg-conversations-container__conversations-list');c.scrollTop=c.scrollHeight;(c.closest('[class*=scroll]')||c.parentElement).scrollTop=1e9})()")
    time.sleep(2)

cands = {}
for t in li('threads', '--limit', '500')['threads']:
    n = t['name']
    if t['preview'].startswith('You'):
        continue
    ab("(()=>{const a=[...document.querySelectorAll('li.msg-conversation-listitem')].find(e=>e.innerText.includes(%s));a&&(a.querySelector('a')||a).click()})()" % json.dumps(n))
    time.sleep(2.5)
    d = li('read', '--limit', '80')
    txt = "\n".join(d.get('lines', []))
    speakers = re.findall(r'View (.+?)’s profile', txt)
    if n.split()[0] not in txt or not speakers:
        continue                       # click missed; wrong thread
    if referee in txt.lower() or speakers[-1] == 'Misha' or EXCL.search(txt):
        continue
    cands[n] = {'url': d['url'], 'unread': t['unread'], 'text': txt[-2500:]}
    print(('* ' if t['unread'] else '  ') + n, flush=True)
json.dump(cands, open(out, 'w'), indent=1, ensure_ascii=False)
