"""Utility functions for CLI"""

import os
import sys
import subprocess
from typing import Optional


class Colors:
    """ANSI color codes"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def print_error(message: str) -> None:
    """Print error message in red"""
    print(f"{Colors.RED}✗ Error: {message}{Colors.END}", file=sys.stderr)


def print_success(message: str) -> None:
    """Print success message in green"""
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")


def print_info(message: str) -> None:
    """Print info message in blue"""
    print(f"{Colors.BLUE}ℹ {message}{Colors.END}")


def print_warning(message: str) -> None:
    """Print warning message in yellow"""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")


def copy_to_clipboard(text: str) -> bool:
    """Copy text to system clipboard"""
    try:
        # Try pbcopy (macOS)
        subprocess.run(['pbcopy'], input=text.encode(), check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        try:
            # Try xclip (Linux)
            subprocess.run(['xclip', '-selection', 'clipboard'],
                         input=text.encode(), check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            try:
                # Try xsel (Linux)
                subprocess.run(['xsel', '--clipboard', '--input'],
                             input=text.encode(), check=True)
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                return False


def get_password(prompt: str = "Master password: ") -> str:
    """Get password from environment variable or user input.
    
    Checks CLAWVAULT_PASSWORD env var first, then falls back to interactive input.
    Using the env var is less secure (visible in process list) but enables
    non-interactive usage (scripts, cron, etc.).
    """
    # Check environment variable first
    env_password = os.environ.get("CLAWVAULT_PASSWORD")
    if env_password:
        return env_password
    
    # Fall back to interactive input
    try:
        import getpass
        return getpass.getpass(prompt)
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        sys.exit(1)
