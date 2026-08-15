"""Password and compact HS256 JWT utilities with no global mutable state."""

import base64
import hashlib
import hmac
import json
import os
import time
from typing import Any

from fastapi import HTTPException, status


def hash_password(password: str) -> str:
    if len(password) < 12:
        raise ValueError("Password must contain at least 12 characters.")
    salt = os.urandom(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
    return "scrypt$16384$8$1$" + base64.urlsafe_b64encode(salt + digest).decode()


def verify_password(password: str, encoded: str) -> bool:
    try:
        _, n, r, p, value = encoded.split("$", 5)
        raw = base64.urlsafe_b64decode(value)
        salt, digest = raw[:16], raw[16:]
        actual = hashlib.scrypt(password.encode(), salt=salt, n=int(n), r=int(r), p=int(p))
        return hmac.compare_digest(actual, digest)
    except (ValueError, TypeError):
        return False


def _enc(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode()


def _dec(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def create_access_token(subject: str, org: str, role: str, secret: str, minutes: int) -> str:
    header = _enc(b'{"alg":"HS256","typ":"JWT"}')
    payload = _enc(
        json.dumps(
            {"sub": subject, "org": org, "role": role, "exp": int(time.time()) + minutes * 60},
            separators=(",", ":"),
        ).encode()
    )
    signature = _enc(
        hmac.new(secret.encode(), f"{header}.{payload}".encode(), hashlib.sha256).digest()
    )
    return f"{header}.{payload}.{signature}"


def decode_access_token(token: str, secret: str) -> dict[str, Any]:
    try:
        header, payload, signature = token.split(".")
        expected = _enc(
            hmac.new(secret.encode(), f"{header}.{payload}".encode(), hashlib.sha256).digest()
        )
        claims = json.loads(_dec(payload))
        if (
            not hmac.compare_digest(signature, expected)
            or not isinstance(claims.get("exp"), int)
            or claims["exp"] < time.time()
        ):
            raise ValueError
        return dict(claims)
    except (ValueError, TypeError, json.JSONDecodeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token"
        ) from None
