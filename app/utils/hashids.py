from hashids import Hashids
from app.core.config import get_settings


def encode_identifier(value: str) -> str:
    settings = get_settings()
    hasher = Hashids(salt=settings.hashids_salt, min_length=12)
    return hasher.encode_hex(value)
