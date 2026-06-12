#!/usr/bin/env python3
"""
Generate a fresh UUID v7 (time-ordered, RFC 9562).

UUID v7 layout (128 bits, big-endian):

    | 48 bits unix_ts_ms | 4 bits version (=7) | 12 bits rand_a |
    | 2 bits variant (=0b10) | 62 bits rand_b |

Why v7 (and not v4): v7 UUIDs are sortable by creation time, which lines
up cleanly with the date-prefixed filename convention used elsewhere in
this skill. A casual sort on doc-id matches a casual sort on filename.

Why a standalone implementation: Python's stdlib `uuid.uuid7()` was only
added in 3.13. This script targets 3.8+ so it runs anywhere the rest of
the workspace tooling runs.

Usage:
    python generate_uuid_v7.py            # print one UUID v7 to stdout
    python generate_uuid_v7.py --count 5  # print five (one per line)

The script writes nothing to disk and reads nothing. Its only side-effect
is stdout. Capture stdout in the calling skill to use the UUID in front
matter:

    uuid=$(python scripts/generate_uuid_v7.py)
"""

from __future__ import annotations

import argparse
import os
import sys
import time


def generate_uuid_v7() -> str:
    """Return one fresh UUID v7 as a canonical 36-char string."""
    # 48 bits of unix time in milliseconds.
    ts_ms = time.time_ns() // 1_000_000
    ts_bytes = ts_ms.to_bytes(6, "big")

    # 10 bytes of cryptographically-random fill for the remaining bits.
    rand = os.urandom(10)

    # Assemble the 16-byte UUID, then fix the version and variant bits.
    raw = bytearray(ts_bytes + rand)

    # Bits 48-51 are the version. Set to 0b0111 (=7).
    raw[6] = (raw[6] & 0x0F) | 0x70

    # Bits 64-65 are the variant. Set to 0b10 (RFC 4122 / 9562 variant).
    raw[8] = (raw[8] & 0x3F) | 0x80

    hex_str = raw.hex()
    return f"{hex_str[0:8]}-{hex_str[8:12]}-{hex_str[12:16]}-{hex_str[16:20]}-{hex_str[20:32]}"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate one or more UUID v7 values (RFC 9562, time-ordered).",
    )
    parser.add_argument(
        "--count",
        "-n",
        type=int,
        default=1,
        help="How many UUIDs to print (one per line). Default: 1.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    if args.count < 1:
        print("--count must be at least 1", file=sys.stderr)
        return 2
    for _ in range(args.count):
        print(generate_uuid_v7())
    return 0


if __name__ == "__main__":
    sys.exit(main())
