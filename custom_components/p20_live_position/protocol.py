"""Decode the P20 dynamic-path response without opening another LAN session."""

from __future__ import annotations

import base64
import struct
from typing import Any


def dynamic_data_params(diff: dict[str, Any]) -> dict[str, Any]:
    """Build the official-app path request from the latest dynamic-map nonce."""
    path_nonce = diff.get("diff", {}).get("3", {}).get("nonce")
    if path_nonce is None:
        path_nonce = diff.get("nonce")
    if path_nonce is None:
        raise ValueError("dynamic path nonce is missing")
    return {
        "nonce": path_nonce,
        "start": 0,
        "len": 0,
        "data_id": 3,
        "type": 0,
        "data": {"paths": [], "robot": {}, "pathArgs": []},
    }


def decode_position(
    response: dict[str, Any], calibration: dict[str, float]
) -> dict[str, float | int]:
    """Extract the type-8 robot record from a get_dynamic_data response."""
    encoded = response.get("data")
    if not isinstance(encoded, str):
        raise ValueError("dynamic path payload is missing")
    data = base64.b64decode(encoded)
    offset = 0
    while offset + 8 <= len(data):
        record_type, header_length, payload_length = struct.unpack_from(
            "<HHI", data, offset
        )
        record_length = header_length + payload_length
        if (
            header_length < 8
            or record_length <= 8
            or offset + record_length > len(data)
        ):
            break
        if record_type == 8 and payload_length >= 12:
            raw_x, raw_y, angle = struct.unpack_from(
                "<iii", data, offset + header_length
            )
            lan_x = raw_x / 50
            lan_y = raw_y / 50
            return {
                "lan_x": round(lan_x, 2),
                "lan_y": round(lan_y, 2),
                "angle": angle,
                "left_percent": round(
                    calibration["left_x"] * lan_x
                    + calibration["left_y"] * lan_y
                    + calibration["left_offset"],
                    4,
                ),
                "top_percent": round(
                    calibration["top_x"] * lan_x
                    + calibration["top_y"] * lan_y
                    + calibration["top_offset"],
                    4,
                ),
            }
        offset += record_length
    raise ValueError("robot position record is missing")
