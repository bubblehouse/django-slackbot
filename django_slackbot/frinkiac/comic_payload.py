"""Encode the binary "comic payload" frinkiac/morbotron's /comic/img expects.

Both sites recently removed the old ``/meme/{episode}/{timestamp}.jpg?b64lines=<text>``
endpoint (it now returns 410). The replacement is a server-rendered comic
endpoint:

    GET https://frinkiac.com/comic/img?b=<urlsafe_base64(payload)>

where ``payload`` is a versioned little-endian binary structure carrying one
or more "panels", each with its own episode/timestamp and a list of text
overlays. The wire format below was reverse-engineered from the public SPA
bundle at /platform/build.min.js (the encoder is the ``rn(panels)`` function
there); the field meanings come from validation error names embedded in the
same bundle (``OVERLAY_COUNT_TOO_LARGE``, ``EPISODE_LEN_OUT_OF_RANGE`` etc.).

For a single captioned screenshot we just encode a one-panel comic. The
default font/size/alignment are left to the server.

Wire format (kind = 2, "comic"):

    u8   version            = 1
    u8   kind               = 2
    u8   panel_count        (1..4)
    for each panel:
        u8       episode_len  (1..16)
        bytes    episode (UTF-8)
        u32 LE   timestamp
        u8       overlay_count (0..32)
        for each overlay:
            u8     flags          (bitmask, see FLAG_* below)
            i16 LE x * 10          (-32768..32767)
            i16 LE y * 10
            u8     text_len_short OR sentinel 255 followed by u16 LE text_len
            bytes  text (UTF-8, <=1024 bytes)
            if flags & FLAG_COLOR : u8 r, u8 g, u8 b, u8 a
            if flags & FLAG_FONT  : u8 font_enum, OR sentinel 255 then u8 name_len + name bytes
            if flags & FLAG_SIZE  : u8 size
            if flags & FLAG_ALIGN : u8 align (0=center, 1=left, 2=right)
            if flags & FLAG_TIMING: i16 LE start, i16 LE end

Maximum encoded length is 65536 bytes.
"""

from __future__ import annotations

import base64
import struct
from typing import Iterable, Sequence

FONT_TABLE = {"akbar": 0, "impact": 1, "comicneue": 2, "pacifico": 3, "jost": 4, "fr": 5}
ALIGN_TABLE = {"c": 0, "": 0, None: 0, "l": 1, "r": 2}

FLAG_COLOR = 1
FLAG_FONT = 2
FLAG_SIZE = 4
FLAG_ALIGN = 8
FLAG_ALL_CAPS = 16
FLAG_TIMING = 32

TEXT_LEN_SHORT_SENTINEL = 255
FONT_CUSTOM_SENTINEL = 255
TEXT_MAX_BYTES = 1024
OVERLAY_MAX = 32
PANEL_MAX = 4
EPISODE_LEN_MAX = 16
PAYLOAD_MAX = 65536

DEFAULT_COLOR = (255, 255, 255, 255)


def _encode_overlay(
    buf: bytearray,
    *,
    text: str,
    text_align: str = "c",
    x: float = 0.0,
    y: float = 0.0,
    size: int = 0,
    color: tuple[int, int, int, int] | None = None,
    font: str | None = None,
    all_caps: bool = False,
    start: int = 0,
    end: int = 0,
) -> None:
    text_bytes = text.encode("utf-8")
    if len(text_bytes) > TEXT_MAX_BYTES:
        raise ValueError(f"overlay text is {len(text_bytes)} bytes; max {TEXT_MAX_BYTES}")

    if text_align not in ALIGN_TABLE:
        raise ValueError(f"unknown text_align: {text_align!r}")
    align_value = ALIGN_TABLE[text_align]

    x_int = round(x * 10)
    y_int = round(y * 10)
    for label, v in (("x", x_int), ("y", y_int), ("start", start), ("end", end)):
        if not -32768 <= v <= 32767:
            raise ValueError(f"{label} out of int16 range: {v}")
    if not 0 <= size <= 255:
        raise ValueError(f"size out of range: {size}")

    color = tuple(color) if color else DEFAULT_COLOR

    has_color = color != DEFAULT_COLOR
    has_font = bool(font)
    has_size = size != 0
    has_align = align_value != 0
    has_timing = start != 0 or end != 0

    flags = 0
    if has_color:
        flags |= FLAG_COLOR
    if has_font:
        flags |= FLAG_FONT
    if has_size:
        flags |= FLAG_SIZE
    if has_align:
        flags |= FLAG_ALIGN
    if all_caps:
        flags |= FLAG_ALL_CAPS
    if has_timing:
        flags |= FLAG_TIMING

    buf.append(flags & 0xFF)
    buf.extend(struct.pack("<hh", x_int, y_int))

    if len(text_bytes) < TEXT_LEN_SHORT_SENTINEL:
        buf.append(len(text_bytes))
    else:
        buf.append(TEXT_LEN_SHORT_SENTINEL)
        buf.extend(struct.pack("<H", len(text_bytes)))
    buf.extend(text_bytes)

    if has_color:
        buf.extend([c & 0xFF for c in color])
    if has_font:
        if font in FONT_TABLE:
            buf.append(FONT_TABLE[font])
        else:
            name_bytes = font.encode("utf-8")
            if len(name_bytes) > 255:
                raise ValueError(f"font name is {len(name_bytes)} bytes; max 255")
            buf.append(FONT_CUSTOM_SENTINEL)
            buf.append(len(name_bytes))
            buf.extend(name_bytes)
    if has_size:
        buf.append(size)
    if has_align:
        buf.append(align_value)
    if has_timing:
        buf.extend(struct.pack("<hh", start, end))


def encode_comic(panels: Sequence[dict]) -> bytes:
    """Encode a list of 1..4 panels into the kind=2 binary comic payload."""
    if not 1 <= len(panels) <= PANEL_MAX:
        raise ValueError(f"need 1..{PANEL_MAX} panels; got {len(panels)}")

    buf = bytearray()
    buf.append(1)
    buf.append(2)
    buf.append(len(panels))

    for panel in panels:
        episode_bytes = panel["episode"].encode("utf-8")
        if not 1 <= len(episode_bytes) <= EPISODE_LEN_MAX:
            raise ValueError(f"episode is {len(episode_bytes)} bytes; range 1..{EPISODE_LEN_MAX}")
        buf.append(len(episode_bytes))
        buf.extend(episode_bytes)
        buf.extend(struct.pack("<I", int(panel["timestamp"]) & 0xFFFFFFFF))

        overlays: Iterable[dict] = panel.get("overlays", [])
        overlays = list(overlays)
        if len(overlays) > OVERLAY_MAX:
            raise ValueError(f"too many overlays ({len(overlays)}); max {OVERLAY_MAX}")
        buf.append(len(overlays))
        for overlay in overlays:
            _encode_overlay(buf, **overlay)

    if len(buf) > PAYLOAD_MAX:
        raise ValueError(f"encoded payload is {len(buf)} bytes; max {PAYLOAD_MAX}")
    return bytes(buf)


def urlsafe_b64(payload: bytes) -> str:
    return base64.urlsafe_b64encode(payload).rstrip(b"=").decode("ascii")


def build_meme_url(site_url: str, episode: str, timestamp: int, text: str) -> str:
    """Build a /comic/img URL that renders a single screenshot with one caption overlay.

    The overlay defaults mirror what the frinkiac SPA's comicmaker uses for a
    fresh subtitle: text anchored at (50%, 97%) — i.e. horizontally centered
    near the bottom of the frame — with the "akbar" caption font.
    """
    overlay = {"text": text, "x": 50.0, "y": 97.0, "text_align": "c", "font": "akbar"}
    payload = encode_comic([{"episode": episode, "timestamp": timestamp, "overlays": [overlay]}])
    return f"{site_url.rstrip('/')}/comic/img?b={urlsafe_b64(payload)}"
