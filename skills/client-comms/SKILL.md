---
name: client-comms
description: Write client-facing updates (WhatsApp, email, Linear comments) for NON-TECHNICAL clients. Use whenever a message, update, or reply is going to a client rather than to Misha — ERIA (Nikita, Chandni) and every other client. Triggers include "update the client", "message the group", "tell Nikita", "reply to them", "let them know", "comment on the ticket", or any outbound note about shipped work.
---

# Talking to clients

Clients are **non-technical**. They hired Misha to make the problem go away, not to
learn how it was solved. Every message answers one question: *what does this mean
for my business?*

## The rules

1. **Business value only.** What can they now do, sell, or stop worrying about.
2. **Never explain the engineering.** No code, no file names, no commits, no table
   or database names, no test counts, no framework names, no "I refactored/deployed/
   migrated". They do not care and it reads as noise.
3. **Be concise.** Shorter than feels natural. A few lines. Cut every sentence that
   does not change what they do next.
4. **Be humble. Never brag.** State what is working, not how hard it was. No "I built
   a robust system", no victory laps, no adjectives about your own work.
5. **Be positive and responsive.** Acknowledge quickly, confirm what you understood,
   say what happens next. Silence is the thing clients actually hate.
6. **A light touch of competence is fine.** One concrete specific ("I checked every
   enquiry going back through the week") signals rigour without a lecture. One.
   Never a paragraph.
7. **Problems: say the impact, not the cause.** "The email service stopped accepting
   our messages" — not the API error, the DNS records, or the account owner. Then say
   what you are doing and that nothing was lost.
8. **Never promise a date you do not control.** If it depends on someone else, say so
   plainly and without blame.

## Two audiences, never mixed

Every task has two reports. Keep them strictly apart.

| Goes to Misha (private, in chat) | Goes to the client |
|---|---|
| Tooling hiccups: a bridge down, an API error, a failed download, an expired login, a flaky test, a deploy that needed a retry | Nothing about any of it. Ever. |
| What's blocked and exactly why | Only if it needs *their* input: ask for that one thing, plainly ("could you resend the photo from this morning?") |
| Partial progress, caveats, what's left | Only what is finished and live |

Our internal plumbing (WhatsApp bridge, agents, CI, Vercel, Dropbox fetches, MCP)
does not exist as far as the client knows. If a tool broke on our side, the client
never hears it. We fix it, or Misha tells them in his own words if he chooses to.

## Message only when it's true

- Send "done" only after it's verified live on the real site. A message saying
  something is done when it isn't costs more trust than silence does.
- If only part is done, say what is live and leave out the rest. Don't list what's
  missing unless they need to act.
- Hitting "send" to a client is Misha's voice. Match his tone (below) exactly.

## Misha's texting voice (WhatsApp)

When Misha asks for it (e.g. "1–2 lines, all lowercase"), that is the format. No
exceptions: every letter lowercase, no sign-off, no emoji unless he uses them.
- good: `all done - the new conference section and the corporate event pages are live on the site, let me know if you want any tweaks`
- bad: `Hi Nikita! 🎉 I've completed all the requested changes. Unfortunately the WhatsApp bridge failed to download one image…`

## Shape of a good update

> [What changed for them, in one line.]
> [Anything they need to do, or that nothing is needed.]
> [What is next, if anything.]

## Examples

**Bad** — engineering, bragging, too long:
> I've added a new `website_enquiries` table in Supabase with typed columns and wired
> it into the server action, plus a new admin section rendered under Reports. Shipped
> in commit 2740d67 with 3174 tests passing and full validator approval. The Resend
> API is returning a 400 because the domain isn't verified.

**Good** — business value, humble, short:
> Every enquiry from the website is now saved automatically, and you can see all the
> answers in the admin portal. Nothing can slip through anymore.
>
> The email notifications are still down at the provider's end — I'm on it. Nothing
> has been lost in the meantime.

**Bad** — vague and passive:
> Some updates have been made to the system and things should be working better now.

**Good** — specific about *their* outcome:
> Two enquiries came in that never reached your inbox — I've sent them over so you can
> call them today.

## Channel notes

- **WhatsApp**: shortest form. No headers, no bullets unless listing people or items.
  Write like a person texting, not a status report.
- **Linear comments**: 1–3 plain sentences on what it means for them. No hashes, stats,
  or jargon.
- **Email**: same rules, slightly more structure allowed when listing details they need
  to act on (e.g. a lead's contact info).

## Before sending

Read it back and ask: *would a person who has never seen a terminal understand every
word, and know what to do next?* If not, cut and rewrite.
Then check: *does it mention any tool, error, or internal problem?* If yes, remove it
and move it into the private report to Misha. Related: `[[nikita-communication-style]]`
for ERIA's specific voice.
