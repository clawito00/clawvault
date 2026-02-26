"""Main CLI entry point"""

import argparse
import sys
from typing import List

from .vault import Vault
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

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Execute command
    args.func(args)


if __name__ == "__main__":
    main()
