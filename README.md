# 🔐 ClawVault

> Encrypted credential manager CLI - Lightweight, secure, and privacy-first

**ClawVault** is a command-line tool for securely storing API keys, tokens, and other credentials locally with AES-256 encryption.

## Features

- 🔐 **AES-256 encryption** via Fernet
- 🔑 **Master password** with PBKDF2 key derivation
- 📋 **Clipboard support** for easy copying
- 🏷️ **Tagging system** for organization
- 🔍 **Search & filter** capabilities
- 💾 **Local-only storage** (no cloud, no tracking)
- 🎨 **Colorized output** for better readability
- ⚡ **Fast and lightweight** - minimal dependencies

## Installation

```bash
# Clone the repository
git clone https://github.com/clawito00/clawvault.git
cd clawvault

# Install
pip install -e .
```

## Quick Start

### Initialize Vault

First time you run any command, ClawVault will create a new encrypted vault:

```bash
clawvault add github --key ghp_xxxxx --tag api
# Enter master password (this creates the vault)
```

### Add Credentials

```bash
# Basic usage
clawvault add openai --key sk-xxxxx

# With tags
clawvault add github --key ghp_xxxxx --tag api --tag development

# With multiple tags
clawvault add stripe --key sk_live_xxxxx --tag payment --tag production --tag api
```

### Get Credentials

```bash
# Display to stdout
clawvault get github

# Copy to clipboard
clawvault get github --copy
```

### List Credentials

```bash
# List all
clawvault list

# Filter by tag
clawvault list --tag api

# Verbose (show tags)
clawvault list --verbose
```

### Search Credentials

```bash
clawvault search git
clawvault search stripe
```

### Update Credentials

```bash
# Update key
clawvault update github --key ghp_newkey

# Update tags (replaces existing)
clawvault update github --tag api --tag production
```

### Delete Credentials

```bash
# With confirmation
clawvault delete github

# Force delete (no confirmation)
clawvault delete github --force
```

### Backup & Restore

```bash
# Export (with optional encryption)
clawvault export backup.json
clawvault export backup.enc --encrypt

# Import
clawvault import backup.json
clawvault import backup.enc --decrypt
```

## Security

### Encryption

- **Algorithm:** Fernet (AES-128-CBC + HMAC)
- **Key Derivation:** PBKDF2 with SHA-256
- **Iterations:** 100,000
- **Salt:** Random 16-byte salt per vault

### Best Practices

- Master password is never stored
- Only encrypted data touches disk
- Secure file permissions (600)
- No plaintext in logs or memory longer than necessary
- All credentials encrypted before storage

### Storage Location

Vault data is stored at:
```
~/.clawvault/vault.json
```

File permissions are automatically set to `600` (owner read/write only).

## CLI Reference

```bash
clawvault add <service> --key <key> [--tag <tag>...]
clawvault get <service> [--copy]
clawvault list [--tag <tag>] [--verbose]
clawvault search <query>
clawvault update <service> [--key <key>] [--tag <tag>...]
clawvault delete <service> [--force]
clawvault export <file> [--encrypt]
clawvault import <file> [--decrypt]
```

## Examples

```bash
# Store API keys
clawvault add openai --key sk-xxxxx --tag ai --tag api
clawvault add anthropic --key sk-ant-xxxxx --tag ai --tag api
clawvault add stripe --key sk_live_xxxxx --tag payment --tag production

# Retrieve keys
clawvault get openai --copy  # Copies to clipboard
clawvault get stripe         # Prints to stdout

# Organization
clawvault list --tag ai      # List all AI-related keys
clawvault search stripe      # Search for "stripe"

# Management
clawvault update openai --key sk-newkey
clawvault delete old-service --force
```

## Development

### Requirements

- Python 3.8+
- `cryptography` library

### Running Tests

```bash
python -m pytest tests/
```

### Building

```bash
python -m build
```

## FAQ

**Q: Is my master password stored anywhere?**
A: No. The master password is used to derive an encryption key, but the password itself is never stored.

**Q: Can I change my master password?**
A: Coming soon in a future update.

**Q: Where is my data stored?**
A: Locally in `~/.clawvault/vault.json`. The file is encrypted and only readable by you.

**Q: Can I sync across devices?**
A: ClawVault is designed for local-only storage. You can manually copy the vault file, but there's no built-in sync.

**Q: Is this suitable for production secrets?**
A: ClawVault is great for development and personal use. For production systems, consider dedicated secret management solutions.

## License

MIT License - see [LICENSE](LICENSE) file

## Contributing

Contributions welcome! Please open an issue or PR.

## Author

Built with ☕ by [clawito00](https://github.com/clawito00)

---

> *"Security is not a product, but a process."* — Bruce Schneier
