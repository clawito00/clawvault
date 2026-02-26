#!/usr/bin/env python3
"""Test script for ClawVault basic functionality"""

import sys
import os
import tempfile
import shutil
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from clawvault.vault import Vault
from clawvault.models import Credential, VaultData


def test_vault_creation():
    """Test vault creation and basic operations"""
    print("Testing vault creation...")

    # Create temporary directory for test
    temp_dir = tempfile.mkdtemp()
    vault_path = Path(temp_dir) / "test_vault.json"

    try:
        vault = Vault(vault_path)

        # Test unlock with new vault
        password = "test_password_123"
        assert vault.unlock(password), "Failed to unlock new vault"
        print("✓ Vault created and unlocked")

        # Test adding credential
        vault.add_credential("test_service", "test_key_123", tags=["test", "api"])
        print("✓ Credential added")

        # Test getting credential
        key = vault.get_credential("test_service")
        assert key == "test_key_123", "Retrieved key doesn't match"
        print("✓ Credential retrieved")

        # Test listing credentials
        services = vault.list_credentials()
        assert "test_service" in services, "Service not in list"
        print("✓ Credentials listed")

        # Test search
        results = vault.search_credentials("test")
        assert "test_service" in results, "Search failed"
        print("✓ Search works")

        # Test update
        vault.update_credential("test_service", key="new_key_456")
        new_key = vault.get_credential("test_service")
        assert new_key == "new_key_456", "Update failed"
        print("✓ Credential updated")

        # Test delete
        vault.delete_credential("test_service")
        assert vault.get_credential("test_service") is None, "Delete failed"
        print("✓ Credential deleted")

        print("\n✅ All tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    success = test_vault_creation()
    sys.exit(0 if success else 1)
