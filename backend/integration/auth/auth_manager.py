from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
import time


@dataclass
class UserIdentity:
    user_id: str
    username: str
    is_authenticated: bool
    scopes: list[str] = field(default_factory=list)  # e.g. ["read", "write", "share"]
    created_at: float = field(default_factory=time.time)


@dataclass
class OwnershipRecord:
    build_id: str
    owner_id: str
    created_at: float


@dataclass
class AccessDecision:
    allowed: bool
    reason: str


class AuthManager:
    def __init__(self):
        self._identities: dict[str, UserIdentity] = {}
        self._ownership: dict[str, OwnershipRecord] = {}  # build_id -> record
        self._api_keys: dict[str, str] = {}  # api_key_hash -> user_id

    def register_user(
        self,
        user_id: str,
        username: str,
        scopes: list[str] | None = None,
    ) -> UserIdentity:
        identity = UserIdentity(
            user_id, username, True, scopes or ["read", "write", "share"]
        )
        self._identities[user_id] = identity
        return identity

    def get_user(self, user_id: str) -> UserIdentity | None:
        return self._identities.get(user_id)

    def register_api_key(self, user_id: str, api_key: str) -> str:
        # Store hash of api_key; return the key hash
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        self._api_keys[key_hash] = user_id
        return key_hash

    def authenticate_api_key(self, api_key: str) -> UserIdentity | None:
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        user_id = self._api_keys.get(key_hash)
        return self._identities.get(user_id) if user_id else None

    def claim_ownership(self, build_id: str, user_id: str) -> OwnershipRecord:
        record = OwnershipRecord(build_id, user_id, time.time())
        self._ownership[build_id] = record
        return record

    def get_owner(self, build_id: str) -> str | None:
        rec = self._ownership.get(build_id)
        return rec.owner_id if rec else None

    def check_access(self, user_id: str, build_id: str, action: str) -> AccessDecision:
        # action: "read", "write", "delete", "share"
        identity = self._identities.get(user_id)
        if not identity or not identity.is_authenticated:
            return AccessDecision(False, "user not authenticated")
        if action not in identity.scopes:
            return AccessDecision(False, f"missing scope: {action}")
        owner = self.get_owner(build_id)
        if action in ("write", "delete") and owner and owner != user_id:
            return AccessDecision(False, "not build owner")
        return AccessDecision(True, "allowed")

    def revoke_user(self, user_id: str) -> bool:
        if user_id in self._identities:
            self._identities[user_id].is_authenticated = False
            return True
        return False
