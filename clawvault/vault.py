"""Vault encryption and storage logic"""

import os
import json
import base64
from pathlib import Path
from datetime import datetime
from typing import Optional, List
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

from .models import Credential, VaultData


class Vault:
    """Encrypted credential vault"""

    def __init__(self, vault_path: Optional[Path] = None):
        """Initialize vault with optional custom path"""
        self.vault_path = vault_path or Path.home() / ".clawvault" / "vault.json"
        self.vault_path.parent.mkdir(parents=True, exist_ok=True)
        self._fernet: Optional[Fernet] = None
        self._data: Optional[VaultData] = None

    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """Derive encryption key from password using PBKDF2"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key

    def _load_vault(self) -> VaultData:
        """Load vault data from disk"""
        if not self.vault_path.exists():
            return VaultData()

        try:
            with open(self.vault_path, 'r') as f:
                data = json.load(f)
            return VaultData.from_dict(data)
        except Exception:
            return VaultData()

    def _save_vault(self) -> None:
        """Save vault data to disk"""
        with open(self.vault_path, 'w') as f:
            json.dump(self._data.to_dict(), f, indent=2)

        # Set secure permissions
        os.chmod(self.vault_path, 0o600)

    def unlock(self, password: str) -> bool:
        """Unlock vault with master password"""
        self._data = self._load_vault()

        # Generate salt if new vault
        if not self._data.salt:
            salt = os.urandom(16)
            self._data.salt = base64.urlsafe_b64encode(salt).decode()
            self._save_vault()
        else:
            salt = base64.urlsafe_b64decode(self._data.salt.encode())

        # Derive key
        key = self._derive_key(password, salt)
        self._fernet = Fernet(key)

        # Test decryption if vault has credentials
        if self._data.credentials:
            try:
                # Try to decrypt first credential to verify password
                cred = self._data.credentials[0]
                self._fernet.decrypt(cred["encrypted_key"].encode())
                return True
            except Exception:
                self._fernet = None
                return False

        return True

    def add_credential(self, service: str, key: str, tags: Optional[List[str]] = None,
                       metadata: Optional[dict] = None) -> None:
        """Add a new credential"""
        if not self._fernet:
            raise RuntimeError("Vault is locked")

        # Check if service already exists
        for cred in self._data.credentials:
            if cred["service"] == service:
                raise ValueError(f"Service '{service}' already exists")

        # Encrypt key
        encrypted_key = self._fernet.encrypt(key.encode()).decode()

        # Create credential
        credential = Credential(
            service=service,
            encrypted_key=encrypted_key,
            tags=tags or [],
            metadata=metadata or {}
        )

        self._data.credentials.append(credential.to_dict())
        self._save_vault()

    def get_credential(self, service: str) -> Optional[str]:
        """Get decrypted credential key"""
        if not self._fernet:
            raise RuntimeError("Vault is locked")

        for cred in self._data.credentials:
            if cred["service"] == service:
                return self._fernet.decrypt(cred["encrypted_key"].encode()).decode()

        return None

    def get_credential_meta(self, service: str) -> Optional[dict]:
        """Get credential metadata (without decrypting key)"""
        for cred in self._data.credentials:
            if cred["service"] == service:
                return {
                    "service": cred["service"],
                    "tags": cred.get("tags", []),
                    "created": cred.get("created"),
                    "updated": cred.get("updated"),
                    "metadata": cred.get("metadata", {})
                }
        return None

    def list_credentials(self, tag: Optional[str] = None) -> List[str]:
        """List all service names, optionally filtered by tag"""
        services = []
        for cred in self._data.credentials:
            if tag:
                if tag in cred.get("tags", []):
                    services.append(cred["service"])
            else:
                services.append(cred["service"])
        return sorted(services)

    def update_credential(self, service: str, key: Optional[str] = None,
                          tags: Optional[List[str]] = None,
                          metadata: Optional[dict] = None) -> None:
        """Update an existing credential"""
        if not self._fernet:
            raise RuntimeError("Vault is locked")

        for i, cred in enumerate(self._data.credentials):
            if cred["service"] == service:
                if key:
                    cred["encrypted_key"] = self._fernet.encrypt(key.encode()).decode()
                if tags is not None:
                    cred["tags"] = tags
                if metadata is not None:
                    cred["metadata"] = metadata
                cred["updated"] = datetime.now().isoformat()
                self._data.credentials[i] = cred
                self._save_vault()
                return

        raise ValueError(f"Service '{service}' not found")

    def delete_credential(self, service: str) -> None:
        """Delete a credential"""
        for i, cred in enumerate(self._data.credentials):
            if cred["service"] == service:
                del self._data.credentials[i]
                self._save_vault()
                return

        raise ValueError(f"Service '{service}' not found")

    def search_credentials(self, query: str) -> List[str]:
        """Search credentials by service name"""
        query_lower = query.lower()
        return [
            cred["service"]
            for cred in self._data.credentials
            if query_lower in cred["service"].lower()
        ]

    def change_password(self, old_password: str, new_password: str) -> bool:
        """Change the master password by re-encrypting all credentials"""
        if not self._fernet:
            raise RuntimeError("Vault is locked")

        # Verify old password by trying to decrypt all credentials
        decrypted_keys = []
        for cred in self._data.credentials:
            try:
                key = self._fernet.decrypt(cred["encrypted_key"].encode()).decode()
                decrypted_keys.append((cred, key))
            except Exception:
                return False

        # Generate new salt and derive new key
        new_salt = os.urandom(16)
        new_salt_b64 = base64.urlsafe_b64encode(new_salt).decode()
        new_key = self._derive_key(new_password, new_salt)
        new_fernet = Fernet(new_key)

        # Re-encrypt all credentials with new key
        for cred, key in decrypted_keys:
            cred["encrypted_key"] = new_fernet.encrypt(key.encode()).decode()

        # Update salt and save
        self._data.salt = new_salt_b64
        self._fernet = new_fernet
        self._save_vault()

        return True

    def get_credential_count(self) -> int:
        """Get total number of credentials"""
        return len(self._data.credentials)

    def create_backup(self, backup_dir: Optional[Path] = None) -> Path:
        """Create a timestamped backup of the vault"""
        import shutil

        backup_dir = backup_dir or (self.vault_path.parent / "backups")
        backup_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"vault_backup_{timestamp}.json"

        shutil.copy2(self.vault_path, backup_path)
        os.chmod(backup_path, 0o600)

        return backup_path

    def list_backups(self, backup_dir: Optional[Path] = None) -> List[dict]:
        """List all available backups"""
        backup_dir = backup_dir or (self.vault_path.parent / "backups")

        if not backup_dir.exists():
            return []

        backups = []
        for backup_file in sorted(backup_dir.glob("vault_backup_*.json"), reverse=True):
            stat = backup_file.stat()
            backups.append({
                "path": str(backup_file),
                "name": backup_file.name,
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_mtime).isoformat()
            })

        return backups

    def restore_backup(self, backup_path: Path, password: str) -> bool:
        """Restore vault from a backup file"""
        import shutil

        if not backup_path.exists():
            raise ValueError(f"Backup file not found: {backup_path}")

        # Create a temporary vault to verify the backup
        temp_path = self.vault_path.with_suffix(".tmp")
        shutil.copy2(backup_path, temp_path)

        # Try to unlock with the temp path
        temp_vault = Vault(vault_path=temp_path)
        if not temp_vault.unlock(password):
            temp_path.unlink()
            return False

        # Backup is valid, replace current vault
        shutil.move(temp_path, self.vault_path)

        # Reload the vault
        self._data = self._load_vault()
        self.unlock(password)

        return True
