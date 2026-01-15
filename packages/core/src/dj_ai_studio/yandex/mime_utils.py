"""MIME type detection utilities."""

from enum import Enum


class MimeType(Enum):
    """Supported image MIME types."""

    JPEG = "image/jpeg"
    PNG = "image/png"


MAGIC_BYTES: tuple[tuple[MimeType, bytes], ...] = (
    (MimeType.JPEG, bytes((0xFF, 0xD8, 0xFF))),
    (MimeType.PNG, bytes((0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A))),
)


def guess_mime_type(data: bytes) -> MimeType | None:
    """Guess MIME type from image data magic bytes.

    Args:
        data: Image binary data

    Returns:
        MimeType if recognized, None otherwise
    """
    for mime_type, magic_bytes in MAGIC_BYTES:
        if data.startswith(magic_bytes):
            return mime_type
    return None
