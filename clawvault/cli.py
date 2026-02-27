"""Main CLI entry point"""

import argparse
import sys
from typing import List

from .vault import Vault
from .export import VaultExporter
from .utils import (
    print_error, print_success, print_info, print_warning,
    copy_to_clipboard, get_password
)


def cmd_add(args):
    """Add a new credential"""
    vault = Vault()

    # Get master password
    password = get_password()
    if not vault.unlock(password):
        print_error("Failed to unlock vault. Wrong password?")
        sys.exit(1)

    try:
        vault.add_credential(
            service=args.service,
            key=args.key,
            tags=args.tag or [],
            metadata={}
        )
        print_success(f"Credential '{args.service}' added successfully")
    except ValueError as e:
        print_error(str(e))
        sys.exit(1)


def cmd_get(args):
    """Get a credential"""
    vault = Vault()

    # Get master password
    password = get_password()
    if not vault.unlock(password):
        print_error("Failed to unlock vault. Wrong password?")
        sys.exit(1)

    key = vault.get_credential(args.service)
    if not key:
        print_error(f"Service '{args.service}' not found")
        sys.exit(1)

    if args.copy:
        if copy_to_clipboard(key):
            print_success(f"Copied '{args.service}' to clipboard")
        else:
            print_warning("Could not copy to clipboard. Displaying instead:")
            print(key)
    else:
        print(key)


def cmd_list(args):
    """List all credentials"""
    vault = Vault()

    # Get master password
    password = get_password()
    if not vault.unlock(password):
        print_error("Failed to unlock vault. Wrong password?")
        sys.exit(1)

    services = vault.list_credentials(tag=args.tag)

    if not services:
        if args.tag:
            print_info(f"No credentials found with tag '{args.tag}'")
        else:
            print_info("No credentials stored yet")
        return

    print_info(f"Found {len(services)} credential(s):")
    for service in services:
        if args.verbose:
            meta = vault.get_credential_meta(service)
            tags_str = ", ".join(meta["tags"]) if meta["tags"] else "none"
            print(f"  • {service} [tags: {tags_str}]")
        else:
            print(f"  • {service}")


def cmd_search(args):
    """Search credentials"""
    vault = Vault()

    # Get master password
    password = get_password()
    if not vault.unlock(password):
        print_error("Failed to unlock vault. Wrong password?")
        sys.exit(1)

    services = vault.search_credentials(args.query)

    if not services:
        print_info(f"No credentials found matching '{args.query}'")
        return

    print_info(f"Found {len(services)} credential(s):")
    for service in services:
        print(f"  • {service}")


def cmd_delete(args):
    """Delete a credential"""
    vault = Vault()

    # Get master password
    password = get_password()
    if not vault.unlock(password):
        print_error("Failed to unlock vault. Wrong password?")
        sys.exit(1)

    # Confirm deletion
    if not args.force:
        response = input(f"Delete credential '{args.service}'? [y/N]: ")
        if response.lower() != 'y':
            print_info("Cancelled")
            return

    try:
        vault.delete_credential(args.service)
        print_success(f"Credential '{args.service}' deleted")
    except ValueError as e:
        print_error(str(e))
        sys.exit(1)


def cmd_update(args):
    """Update a credential"""
    vault = Vault()

    # Get master password
    password = get_password()
    if not vault.unlock(password):
        print_error("Failed to unlock vault. Wrong password?")
        sys.exit(1)

    try:
        vault.update_credential(
            service=args.service,
            key=args.key,
            tags=args.tag
        )
        print_success(f"Credential '{args.service}' updated")
    except ValueError as e:
        print_error(str(e))
        sys.exit(1)


def cmd_export(args):
    """Export vault to file"""
    vault = Vault()

    # Get master password
    password = get_password()
    if not vault.unlock(password):
        print_error("Failed to unlock vault. Wrong password?")
        sys.exit(1)

    # Get export password (optional)
    export_password = None
    if args.encrypt:
        export_password = get_password("Export password (leave empty for no encryption): ")
        if not export_password:
            print_info("Exporting without additional encryption")

    try:
        from pathlib import Path
        output_path = Path(args.output)
        VaultExporter.export_vault(vault, output_path, export_password)
        print_success(f"Exported {len(vault._data.credentials)} credentials to {args.output}")
    except Exception as e:
        print_error(f"Export failed: {e}")
        sys.exit(1)


def cmd_import(args):
    """Import vault from file"""
    vault = Vault()

    # Get master password
    password = get_password()
    if not vault.unlock(password):
        print_error("Failed to unlock vault. Wrong password?")
        sys.exit(1)

    # Get import password (if needed)
    import_password = None
    if args.decrypt:
        import_password = get_password("Import password: ")

    try:
        from pathlib import Path
        input_path = Path(args.input)
        count = VaultExporter.import_vault(vault, input_path, import_password)
        print_success(f"Imported {count} credentials from {args.input}")
    except Exception as e:
        print_error(f"Import failed: {e}")
        sys.exit(1)


def cmd_passwd(args):
    """Change master password"""
    vault = Vault()

    # Get current password
    old_password = get_password("Current master password: ")
    if not vault.unlock(old_password):
        print_error("Failed to unlock vault. Wrong password?")
        sys.exit(1)

    # Get new password
    new_password = get_password("New master password: ")
    confirm_password = get_password("Confirm new password: ")

    if new_password != confirm_password:
        print_error("Passwords do not match")
        sys.exit(1)

    if len(new_password) < 8:
        print_error("Password must be at least 8 characters")
        sys.exit(1)

    # Change password
    if vault.change_password(old_password, new_password):
        print_success("Master password changed successfully")
    else:
        print_error("Failed to change password")
        sys.exit(1)


def cmd_backup(args):
    """Create a vault backup"""
    vault = Vault()

    # Verify password before backup
    password = get_password()
    if not vault.unlock(password):
        print_error("Failed to unlock vault. Wrong password?")
        sys.exit(1)

    try:
        backup_path = vault.create_backup()
        print_success(f"Backup created: {backup_path}")
        print_info(f"Credentials backed up: {vault.get_credential_count()}")
    except Exception as e:
        print_error(f"Backup failed: {e}")
        sys.exit(1)


def cmd_backups(args):
    """List available backups"""
    vault = Vault()
    backups = vault.list_backups()

    if not backups:
        print_info("No backups found")
        return

    print_info(f"Found {len(backups)} backup(s):")
    for backup in backups:
        size_kb = backup["size"] / 1024
        print(f"  • {backup['name']} ({size_kb:.1f} KB) - {backup['created']}")


def cmd_restore(args):
    """Restore vault from backup"""
    from pathlib import Path

    vault = Vault()
    backup_path = Path(args.backup)

    password = get_password("Master password for backup: ")

    try:
        if vault.restore_backup(backup_path, password):
            print_success(f"Restored vault from {backup_path}")
            print_info(f"Credentials restored: {vault.get_credential_count()}")
        else:
            print_error("Failed to restore backup. Wrong password?")
            sys.exit(1)
    except Exception as e:
        print_error(f"Restore failed: {e}")
        sys.exit(1)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="🔐 ClawVault - Encrypted credential manager",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new credential")
    add_parser.add_argument("service", help="Service name")
    add_parser.add_argument("--key", "-k", required=True, help="API key/credential")
    add_parser.add_argument("--tag", "-t", action="append", help="Tags (can be used multiple times)")
    add_parser.set_defaults(func=cmd_add)

    # Get command
    get_parser = subparsers.add_parser("get", help="Get a credential")
    get_parser.add_argument("service", help="Service name")
    get_parser.add_argument("--copy", "-c", action="store_true", help="Copy to clipboard")
    get_parser.set_defaults(func=cmd_get)

    # List command
    list_parser = subparsers.add_parser("list", help="List all credentials")
    list_parser.add_argument("--tag", "-t", help="Filter by tag")
    list_parser.add_argument("--verbose", "-v", action="store_true", help="Show details")
    list_parser.set_defaults(func=cmd_list)

    # Search command
    search_parser = subparsers.add_parser("search", help="Search credentials")
    search_parser.add_argument("query", help="Search query")
    search_parser.set_defaults(func=cmd_search)

    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a credential")
    delete_parser.add_argument("service", help="Service name")
    delete_parser.add_argument("--force", "-f", action="store_true", help="Skip confirmation")
    delete_parser.set_defaults(func=cmd_delete)

    # Update command
    update_parser = subparsers.add_parser("update", help="Update a credential")
    update_parser.add_argument("service", help="Service name")
    update_parser.add_argument("--key", "-k", help="New API key/credential")
    update_parser.add_argument("--tag", "-t", action="append", help="New tags (replaces existing)")
    update_parser.set_defaults(func=cmd_update)

    # Export command
    export_parser = subparsers.add_parser("export", help="Export vault to file")
    export_parser.add_argument("output", help="Output file path")
    export_parser.add_argument("--encrypt", "-e", action="store_true", help="Encrypt export with password")
    export_parser.set_defaults(func=cmd_export)

    # Import command
    import_parser = subparsers.add_parser("import", help="Import vault from file")
    import_parser.add_argument("input", help="Input file path")
    import_parser.add_argument("--decrypt", "-d", action="store_true", help="Decrypt import with password")
    import_parser.set_defaults(func=cmd_import)

    # Password change command
    passwd_parser = subparsers.add_parser("passwd", help="Change master password")
    passwd_parser.set_defaults(func=cmd_passwd)

    # Backup command
    backup_parser = subparsers.add_parser("backup", help="Create a vault backup")
    backup_parser.set_defaults(func=cmd_backup)

    # List backups command
    backups_parser = subparsers.add_parser("backups", help="List available backups")
    backups_parser.set_defaults(func=cmd_backups)

    # Restore command
    restore_parser = subparsers.add_parser("restore", help="Restore vault from backup")
    restore_parser.add_argument("backup", help="Backup file path")
    restore_parser.set_defaults(func=cmd_restore)

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Execute command
    args.func(args)


if __name__ == "__main__":
    main()
