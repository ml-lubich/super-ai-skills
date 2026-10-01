---
name: keychain
description: >
  Retrieve passwords and secrets from macOS Keychain in agent sessions.
  Use this skill whenever you need a stored credential (password, API key, token)
  without hardcoding it into a skill file. Triggers: "get my password for X",
  "retrieve from keychain", "look up credentials for Y", or any task that needs
  a secret stored in the system keychain.
---

# macOS Keychain Skill

All sensitive credentials are stored in macOS Keychain. **Never hardcode passwords
in skill files or agent context.** Always retrieve at runtime using the `security` CLI.

---

## Retrieve a Password

### Internet password (websites / services)

```bash
security find-internet-password -s "<service>" -a "<account>" -w
```

Returns just the plaintext password on stdout.

### Generic password (API keys, tokens)

```bash
security find-generic-password -s "<service>" -a "<account>" -w
```

---

## Known Stored Credentials

| Service       | Account                         | Keychain Label        | Retrieve Command |
|---------------|---------------------------------|-----------------------|------------------|
| LinkedIn      | `michaelle.lubich@gmail.com`    | `LinkedIn - Misha`    | `security find-internet-password -s "linkedin.com" -a "michaelle.lubich@gmail.com" -w` |

> Add more entries here as new credentials are stored.

---

## Store a New Credential

### Internet password

```bash
security add-internet-password \
  -s "<service-domain>" \
  -a "<account/username>" \
  -w "<password>" \
  -l "<human-readable-label>" \
  -U   # -U = update if already exists
```

### Generic password

```bash
security add-generic-password \
  -s "<service-name>" \
  -a "<account>" \
  -w "<secret>" \
  -l "<label>" \
  -U
```

---

## Using Credentials in a Script

Always retrieve inline — do not assign to a shell variable that gets logged:

```bash
# Inline retrieval example (browser automation)
LI_PASS=$(security find-internet-password -s "linkedin.com" -a "michaelle.lubich@gmail.com" -w)
agent-browser fill @e20 "$LI_PASS"
unset LI_PASS
```

Or pass directly:

```bash
agent-browser fill @e20 "$(security find-internet-password -s 'linkedin.com' -a 'michaelle.lubich@gmail.com' -w)"
```

---

## Security Rules

- **Never print passwords to stdout** in chat responses or log files.
- **Never store passwords** in skill files, rules, or YAML configs.
- **Always use `-w` flag** on retrieval to get password-only output (no metadata).
- **Use `-U` flag** on `add-*-password` to upsert without duplicating entries.
