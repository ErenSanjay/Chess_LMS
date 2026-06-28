import base64
import hmac
import json
from datetime import UTC, datetime, timedelta
from hashlib import pbkdf2_hmac, sha256
from secrets import token_urlsafe
from uuid import UUID

from app.core.config import Settings
from app.modules.users.models import User, UserStatus


class InvalidTokenError(ValueError):
    pass


PASSWORD_ITERATIONS = 310_000


def now_utc() -> datetime:
    return datetime.now(UTC)


def normalize_email(email: str) -> str:
    return email.strip().lower()


def hash_password(password: str, settings: Settings) -> str:
    salt = token_urlsafe(24)
    digest = pbkdf2_hmac(
        "sha256",
        f"{password}{settings.password_pepper}".encode("utf-8"),
        salt.encode("utf-8"),
        PASSWORD_ITERATIONS,
    )
    encoded_digest = base64.urlsafe_b64encode(digest).decode("ascii")
    return f"pbkdf2_sha256${PASSWORD_ITERATIONS}${salt}${encoded_digest}"


def verify_password(password: str, password_hash: str, settings: Settings) -> bool:
    try:
        algorithm, iterations_raw, salt, stored_digest = password_hash.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        digest = pbkdf2_hmac(
            "sha256",
            f"{password}{settings.password_pepper}".encode("utf-8"),
            salt.encode("utf-8"),
            int(iterations_raw),
        )
        encoded_digest = base64.urlsafe_b64encode(digest).decode("ascii")
        return hmac.compare_digest(encoded_digest, stored_digest)
    except (ValueError, TypeError):
        return False


def hash_token(token: str, settings: Settings) -> str:
    return sha256(f"{token}{settings.password_pepper}".encode("utf-8")).hexdigest()


def create_access_token(user: User, settings: Settings) -> str:
    issued_at = now_utc()
    expires_at = issued_at + timedelta(seconds=settings.access_token_ttl_seconds)
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role.value,
        "status": user.status.value,
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "iat": int(issued_at.timestamp()),
        "nbf": int(issued_at.timestamp()),
        "exp": int(expires_at.timestamp()),
        "typ": "access",
    }
    return encode_jwt(payload, settings.jwt_private_key)


def decode_access_token(token: str, settings: Settings) -> dict[str, object]:
    payload = decode_jwt(token, settings.jwt_private_key)
    if payload.get("typ") != "access":
        raise InvalidTokenError("Unexpected token type")
    if payload.get("iss") != settings.jwt_issuer:
        raise InvalidTokenError("Invalid issuer")
    if payload.get("aud") != settings.jwt_audience:
        raise InvalidTokenError("Invalid audience")

    current_timestamp = int(now_utc().timestamp())
    expires_at = payload.get("exp")
    not_before = payload.get("nbf")
    if not isinstance(expires_at, int) or expires_at <= current_timestamp:
        raise InvalidTokenError("Token expired")
    if not isinstance(not_before, int) or not_before > current_timestamp:
        raise InvalidTokenError("Token not active yet")

    return payload


def encode_jwt(payload: dict[str, object], secret: str) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    signing_input = ".".join(
        [
            base64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8")),
            base64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8")),
        ]
    )
    signature = hmac.new(
        secret.encode("utf-8"),
        signing_input.encode("ascii"),
        sha256,
    ).digest()
    return f"{signing_input}.{base64url_encode(signature)}"


def decode_jwt(token: str, secret: str) -> dict[str, object]:
    try:
        header_segment, payload_segment, signature_segment = token.split(".")
    except ValueError:
        raise InvalidTokenError("Malformed token") from None

    signing_input = f"{header_segment}.{payload_segment}"
    expected_signature = hmac.new(
        secret.encode("utf-8"),
        signing_input.encode("ascii"),
        sha256,
    ).digest()
    actual_signature = base64url_decode(signature_segment)
    if not hmac.compare_digest(actual_signature, expected_signature):
        raise InvalidTokenError("Invalid signature")

    header = json.loads(base64url_decode(header_segment))
    if header.get("alg") != "HS256":
        raise InvalidTokenError("Unsupported token algorithm")

    payload = json.loads(base64url_decode(payload_segment))
    if not isinstance(payload, dict):
        raise InvalidTokenError("Invalid token payload")
    return payload


def base64url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def base64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(f"{value}{padding}".encode("ascii"))


def ensure_active_user(user: User) -> None:
    if user.status != UserStatus.active:
        raise PermissionError("User account is not active")


def user_id_from_payload(payload: dict[str, object]) -> UUID:
    raw_subject = payload.get("sub")
    if not isinstance(raw_subject, str):
        raise InvalidTokenError("Missing subject")
    return UUID(raw_subject)
