# Credential Manager CLI - Project Plan

## Overview
Encrypted local credential store with a clean CLI interface. Lightweight, privacy-first, designed for API keys.

## Tech Stack
- **Language:** Python 3.12+
- **Encryption:** `cryptography` library (Fernet symmetric encryption)
- **Storage:** JSON file in `~/.clawvault/`
- **CLI:** `argparse` with subcommands

## Features

### Core
- [x] Add credential (service, key, metadata)
- [x] Get credential (copy to clipboard or display)
- [x] List all services
- [x] Delete credential
- [x] Update credential

### Security
- [x] Master password (PBKDF2 derived key)
- [x] AES-256 encryption via Fernet
- [ ] Auto-lock after timeout
- [x] Secure memory handling (no plaintext in logs)
- [x] Password change capability

### UX
- [x] Colorized output
- [x] Tab completion for service names
- [x] Search/filter credentials
- [x] Export/import (encrypted)
- [x] Backup to file
- [x] Restore from backup

## CLI Design

```bash
clawvault add github --key ghp_xxx --tag api --tag development
clawvault get github          # Display key
clawvault get github --copy   # Copy to clipboard
clawvault list
clawvault list --tag api
clawvault search git
clawvault delete github
clawvault export backup.enc
clawvault import backup.enc
clawvault --help
```

## File Structure

```
clawvault/
├── clawvault/
│   ├── __init__.py
│   ├── cli.py           # Main CLI entry point
│   ├── vault.py         # Encryption/storage logic
│   ├── models.py        # Credential data models
│   └── utils.py         # Helpers (clipboard, colors)
├── completions/
│   ├── clawvault.bash   # Bash completion
│   └── _clawvault       # Zsh completion
├── setup.py
├── README.md
├── LICENSE
└── .gitignore
```

## Storage Format

```json
{
  "version": "1.0",
  "salt": "base64...",
  "credentials": [
    {
      "service": "github",
      "encrypted_key": "base64...",
      "tags": ["api", "development"],
      "created": "2026-02-26T...",
      "updated": "2026-02-26T..."
    }
  ]
}
```

## Implementation Steps

1. **Phase 1: Core functionality** ✅ COMPLETE
   - Set up project structure
   - Implement encryption/decryption
   - Basic CLI commands (add, get, list, delete)
   - Repo: https://github.com/clawito00/clawvault

2. **Phase 2: UX improvements** ✅ COMPLETE
   - Colorized output
   - Clipboard support
   - Search/filter
   - Export/import functionality
   - Basic test suite

3. **Phase 3: Advanced features** ✅ COMPLETE
   - Password change command
   - Backup system (create, list, restore)
   - Backup directory management

4. **Phase 4: Polish** ✅ COMPLETE
   - Tab completion for bash and zsh
   - README updated with completion instructions
   - Ready for PyPI packaging

## Security Considerations

- Master password never stored (derived key only)
- Salt stored in plaintext (standard practice)
- Encryption: Fernet (AES-128-CBC + HMAC)
- Key derivation: PBKDF2 with SHA256, 100k iterations
- No plaintext credentials in memory longer than necessary
- Secure file permissions (600)

## Privacy Rules (per AGENTS.md)

- No infrastructure details in README
- Generic location
- No personal names
- Public repo at: https://github.com/clawito00/clawvault

## Schedule

**Build ONLY when ALL conditions are met:**
1. ✅ Time is between 3 AM and 7 AM (user offline)
2. ✅ No active user requests (truly idle)
3. ✅ Weekly quota < 20%
4. ✅ 5-hour quota < 50%

**If ANY condition fails, skip project work.**

**Estimated time:** 3-4 sessions to complete Phase 1-2
