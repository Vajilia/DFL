"""Edition 8.15 read-only viewer projection.

This is an isolated contract for a future public website, not a production route.
Only the fields explicitly selected below may cross the public boundary.
No RNG, hidden card state, writes, or mutable reference sharing.
"""
from __future__ import annotations

import copy
from collections.abc import Mapping, Sequence

RULE_VERSION = "DFL-Ed8.15"
TABS = ("Home", "Teams", "Players", "Schedule", "Standings", "Statistics")
LOOK_FIELDS = ("skin_tone", "eye_color", "hair_color", "hair_style", "face_shape", "body_type")

def _record(value, label):
    if not isinstance(value, Mapping):
        raise TypeError(f"{label} must be a mapping")
    return value

def public_character(card, *, season_year):
    """Derive age from birth year; never send attributes, traits or memories."""
    c = _record(card, "character card")
    if not isinstance(season_year, int) or isinstance(season_year, bool):
        raise TypeError("season_year must be an integer")
    birth = c["birth_year"]
    if not isinstance(birth, int) or isinstance(birth, bool):
        raise TypeError("birth_year must be an integer")
    age = season_year - birth
    if not 18 <= age <= 110:
        raise ValueError("character age outside public adult range")
    required = ("id", "name", "role", "position", "height", "weight", "look")
    if any(key not in c for key in required):
        raise ValueError("incomplete public character identity")
    for key in ("id", "name", "role", "position"):
        if not isinstance(c[key], str) or not c[key]:
            raise ValueError(f"{key} must be a nonempty public string")
    for key in ("height", "weight"):
        if isinstance(c[key], bool) or not isinstance(c[key], (int, float)) or not 0 < c[key] < 1000:
            raise ValueError(f"{key} must be a positive public measurement")
    result = {key: copy.deepcopy(c[key]) for key in required}
    look = _record(c["look"], "creation look")
    result["look"] = {}
    for key in LOOK_FIELDS:
        if key in look:
            if not isinstance(look[key], str) or not look[key]:
                raise ValueError(f"creation look field {key} must be a nonempty string")
            result["look"][key] = look[key]
    result["age"] = age
    return result

def public_digest(events, *, since_sequence=0):
    """Return public events after a client's last seen sequence; never mutate history.

    The event log owns global monotonically increasing integer sequences, including
    private events. A skipped private sequence is harmless and discloses no content.
    No viewer acknowledgement is written to canonical simulation state.
    """
    if not isinstance(since_sequence, int) or isinstance(since_sequence, bool) or since_sequence < 0:
        raise ValueError("since_sequence must be a nonnegative integer")
    if not isinstance(events, Sequence) or isinstance(events, (str, bytes)):
        raise TypeError("events must be a sequence")
    result = []
    last = 0
    for item in events:
        event = _record(item, "event")
        seq = event["sequence"]
        if not isinstance(seq, int) or isinstance(seq, bool) or seq <= last:
            raise ValueError("event sequence must be strictly increasing and positive")
        last = seq
        if seq <= since_sequence or event.get("visibility") != "public":
            continue
        keys = ("id", "sequence", "simulated_time", "public_summary")
        if any(key not in event for key in keys):
            raise ValueError("public event lacks its safe display fields")
        for key in ("id", "simulated_time", "public_summary"):
            if not isinstance(event[key], str) or not event[key]:
                raise ValueError(f"public event {key} must be a nonempty string")
        result.append({key: copy.deepcopy(event[key]) for key in keys})
    return result

def public_packet(*, cards, events, season_year, since_sequence=0):
    """Stateless snapshot; the six navigation tabs are fixed by §16."""
    if not isinstance(cards, Sequence) or isinstance(cards, (str, bytes)):
        raise TypeError("cards must be a sequence")
    return {
        "rule_version": RULE_VERSION,
        "tabs": list(TABS),
        "characters": [public_character(c, season_year=season_year) for c in cards],
        "event_digest": public_digest(events, since_sequence=since_sequence),
    }
