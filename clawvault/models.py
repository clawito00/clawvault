"""Data models for credentials"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import json


@dataclass
class Credential:
    """Represents a stored credential"""
    service: str
    encrypted_key: str
    tags: List[str] = field(default_factory=list)
    created: str = field(default_factory=lambda: datetime.now().isoformat())
    updated: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "service": self.service,
            "encrypted_key": self.encrypted_key,
            "tags": self.tags,
            "created": self.created,
            "updated": self.updated,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Credential":
        """Create from dictionary"""
        return cls(
            service=data["service"],
            encrypted_key=data["encrypted_key"],
            tags=data.get("tags", []),
            created=data.get("created", datetime.now().isoformat()),
            updated=data.get("updated", datetime.now().isoformat()),
            metadata=data.get("metadata", {})
        )


@dataclass
class VaultData:
    """Represents the entire vault structure"""
    version: str = "1.0"
    salt: str = ""
    credentials: List[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "version": self.version,
            "salt": self.salt,
            "credentials": self.credentials
        }

    @classmethod
    def from_dict(cls, data: dict) -> "VaultData":
        """Create from dictionary"""
        return cls(
            version=data.get("version", "1.0"),
            salt=data.get("salt", ""),
            credentials=data.get("credentials", [])
        )
