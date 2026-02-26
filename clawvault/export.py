"""Export and import functionality"""

import os
import json
import base64
from pathlib import Path
from typing import Optional
from datetime import datetime

from .vault import Vault


class VaultExporter:
    """Handle vault export and import"""

    @staticmethod
    def export_vault(vault: Vault, output_path: Path, export_password: Optional[str] = None) -> None:
        """Export vault to encrypted file"""
        if not vault._fernet:
            raise RuntimeError("Vault is locked")

        # Prepare export data
        export_data = {
            "version": "1.0",
            "exported": datetime.now().isoformat(),
            "credentials": vault._data.credentials
        }

        # Encrypt export with export password (if provided)
        if export_password:
            from cryptography.fernet import Fernet
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
            from cryptography.hazmat.backends import default_backend

            salt = os.urandom(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )
            key = base64.urlsafe_b64encode(kdf.derive(export_password.encode()))
            fernet = Fernet(key)

            # Encrypt the export data
            json_data = json.dumps(export_data)
            encrypted = fernet.encrypt(json_data.encode())

            # Save with salt
            final_data = {
                "encrypted": base64.urlsafe_b64encode(encrypted).decode(),
                "salt": base64.urlsafe_b64encode(salt).decode()
            }

            with open(output_path, 'w') as f:
                json.dump(final_data, f)
        else:
            # No encryption (already encrypted in vault)
            with open(output_path, 'w') as f:
                json.dump(export_data, f, indent=2)

        # Set secure permissions
        os.chmod(output_path, 0o600)

    @staticmethod
    def import_vault(vault: Vault, input_path: Path, import_password: Optional[str] = None) -> int:
        """Import vault from encrypted file. Returns number of credentials imported."""
        if not vault._fernet:
            raise RuntimeError("Vault is locked")

        with open(input_path, 'r') as f:
            data = json.load(f)

        # Check if file is encrypted with export password
        if "encrypted" in data and import_password:
            from cryptography.fernet import Fernet
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
            from cryptography.hazmat.backends import default_backend

            # Decrypt with import password
            salt = base64.urlsafe_b64decode(data["salt"].encode())
            encrypted = base64.urlsafe_b64decode(data["encrypted"].encode())

            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )
            key = base64.urlsafe_b64encode(kdf.derive(import_password.encode()))
            fernet = Fernet(key)

            decrypted = fernet.decrypt(encrypted)
            data = json.loads(decrypted.decode())

        # Import credentials
        imported_count = 0
        for cred in data.get("credentials", []):
            try:
                # Check if service already exists
                service = cred["service"]
                if vault.get_credential_meta(service):
                    # Skip existing
                    continue

                # Add credential
                vault._data.credentials.append(cred)
                imported_count += 1
            except Exception:
                continue

        if imported_count > 0:
            vault._save_vault()

        return imported_count
