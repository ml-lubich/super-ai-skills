---
name: clickup-admin-browser
description: Do the ClickUp things the API cannot - invite or remove workspace members, and archive tasks in bulk - by driving the ClickUp web UI with agent-browser. Use when the ClickUp MCP has no tool for what is needed (there is no invite/add-member tool and no archive field on update_task), when someone needs ClickUp access, or when duplicates must be archived rather than deleted. Also use when a ClickUp write is rate-limited but the work still has to happen, since the UI does not consume the API quota.
---

# clickup-admin-browser

Two ClickUp jobs have no API path at all:

| Job | Why the API can't | 
|---|---|
| Invite a member | The MCP exposes only `clickup_find_member_by_name`. There is no invite/add tool. |
| Archive a task | `clickup_update_task` has no `archived` field. Only `clickup_delete_task` exists, and delete is irreversible. |

The UI does both, and **it does not spend the REST rate-limit budget** — which matters on the Free plan, where writes cap near 50 per ~24h window (see `clickup-burst-writes-trip-the-limit` memory).

## One-time setup (needs the human once)

ClickUp shows a login wall and no Chrome profile on this machine carries a
session — verified across `Default`, `Profile 1`, `Profile 3`. Store the
credential once:

```bash
agent-browser auth save clickup \
  --url "https://app.clickup.com/login" \
  --username "<the ClickUp account email>" \
  --password-stdin      # paste the password, it is not written to shell history
```

Never put the password on the command line, never echo it, never write it into
a file in the repo. `agent-browser auth list` shows names and URLs only.

After that every run below is hands-free:

```bash
agent-browser auth login clickup
```

If ClickUp uses Google SSO on this account there is no password to save. In that
case say so plainly and hand the task back — do not try to drive an OAuth
consent screen.

## Invite a member

```bash
export AGENT_BROWSER_SESSION=clickup-admin
agent-browser auth login clickup
agent-browser open "https://app.clickup.com/<workspace_id>/settings/team/<workspace_id>/users"
agent-browser wait 4000
agent-browser snapshot -i          # find the Invite control by ref, do not guess selectors
# click Invite, type the email, choose the role, confirm
agent-browser get url               # prove you are not still on /login
```

**Verify with the API, not the screenshot.** After inviting, confirm with
`clickup_find_member_by_name <email>` — a member row rendering in the DOM is not
proof the invite was actually created. `find_member_by_name` returning `null`
means it did not work, whatever the page showed.

ERIA workspace is `90141458888`, ERIA space `90146722683`, main list `901418477402`.

## Archive tasks in bulk

Open the task, use the `...` menu → Archive. For many tasks, use the list view's
multi-select and the bulk action toolbar rather than one task at a time.

**Never archive without checking the task is genuinely a duplicate first.** In
this workspace, identity is the Linear URL in the description, never the task
name — two migration runs wrote two different naming conventions for the same
issue. See `docs/clickup-migration.md` in the Eria-Website repo.

## Cleanup

Close only your own session: `agent-browser close` with your
`AGENT_BROWSER_SESSION` set. Never `agent-browser close --all` — other sessions
share this machine.
