"""Lossless Edition 8.15 22-player *trace contract*, not a physics engine.

One tick is exactly 0.05 seconds. This module verifies and compresses
observations supplied by a future spatial simulator; it never generates
player motion, play outcomes, statistics, or football scores.
"""
from __future__ import annotations

import hashlib
import json
import math
import zlib

RULE_VERSION = "DFL-Ed8.15"
TICK_SECONDS = 0.05
MAX_FRAMES = 3600
MAX_BYTES = 16 * 1024 * 1024


def _real(v):
    return type(v) in (int, float) and math.isfinite(v)


def validate(frames):
    if not isinstance(frames, list) or not frames or len(frames) > MAX_FRAMES:
        raise ValueError("play trace must have 1..3600 tick frames")
    previous_ids = None
    for i, frame in enumerate(frames):
        if not isinstance(frame, dict) or frame.get("tick") != i or type(frame.get("tick")) is not int:
            raise ValueError("trace tick must be consecutive integer 0.05s step")
        players = frame.get("players")
        if not isinstance(players, list) or len(players) != 22:
            raise ValueError("exactly 22 on-field players required per tick")
        seen, side_counts = set(), {"home": 0, "away": 0}
        for p in players:
            if not isinstance(p, dict) or not isinstance(p.get("id"), str) or not p["id"]:
                raise ValueError("invalid permanent player identity")
            if p["id"] in seen or p.get("side") not in side_counts:
                raise ValueError("duplicate player or invalid side")
            if any(not _real(p.get(axis)) for axis in ("x", "y")):
                raise ValueError("invalid player position")
            if not isinstance(p.get("intent"), str):
                raise ValueError("intent reference must be a string")
            seen.add(p["id"])
            side_counts[p["side"]] += 1
        if set(side_counts.values()) != {11}:
            raise ValueError("11 players required per side")
        if previous_ids is not None and previous_ids != seen:
            raise ValueError("in-play substitution unsupported; split trace at dead ball")
        previous_ids = seen
        ball = frame.get("ball")
        if not isinstance(ball, dict) or any(not _real(ball.get(k)) for k in ("x", "y", "z")):
            raise ValueError("ball position required on every tick")
        if ball.get("holder") is not None and ball["holder"] not in seen:
            raise ValueError("ball holder not on field")
        events = frame.get("decisive_events")
        if not isinstance(events, list) or any(not isinstance(e, str) or not e for e in events):
            raise ValueError("decisive events must be text identifiers")
    return True


def pack(frames):
    """Canonical compact bytes, SHA256 over raw trace, lossless zlib container."""
    validate(frames)
    raw = json.dumps({"rule_version": RULE_VERSION, "tick_seconds": TICK_SECONDS,
                      "frames": frames}, sort_keys=True, separators=(",", ":"),
                     ensure_ascii=False, allow_nan=False).encode("utf-8")
    if len(raw) > MAX_BYTES:
        raise ValueError("trace exceeds per-play size limit")
    return {"codec": "zlib-ed815-trace-v1", "sha256": hashlib.sha256(raw).hexdigest(),
            "data": zlib.compress(raw, level=9), "frames": len(frames)}


def unpack(bundle):
    if not isinstance(bundle, dict) or bundle.get("codec") != "zlib-ed815-trace-v1":
        raise ValueError("unknown trace codec")
    compressed = bundle.get("data")
    if not isinstance(compressed, bytes):
        raise ValueError("compressed trace must be bytes")
    dec = zlib.decompressobj()
    try:
        raw = dec.decompress(compressed, MAX_BYTES + 1)
        if len(raw) > MAX_BYTES or dec.unconsumed_tail or not dec.eof or dec.unused_data:
            raise ValueError("truncated or oversized trace")
        raw += dec.flush()
        if len(raw) > MAX_BYTES:
            raise ValueError("oversized trace")
        if hashlib.sha256(raw).hexdigest() != bundle.get("sha256"):
            raise ValueError("trace checksum mismatch")
        payload = json.loads(raw.decode("utf-8"))
    except (zlib.error, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid compressed trace") from exc
    if (payload.get("rule_version") != RULE_VERSION
            or payload.get("tick_seconds") != TICK_SECONDS):
        raise ValueError("wrong trace rules/timestep")
    frames = payload.get("frames")
    validate(frames)
    if len(frames) != bundle.get("frames"):
        raise ValueError("trace frame count mismatch")
    return frames
