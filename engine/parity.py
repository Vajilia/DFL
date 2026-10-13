"""Parity profiles: how much the league regulates salaries and protects its weakest clubs. A profile is chosen when a league is created (meta.json "parity")
and applied before the league is opened, every time the runner starts, so a restart plays the same rules.

  tight  the rules as written: cap, floor, bank, Equalization Fund, the league pays half an exiled club's payroll, the exiled clubs hold the lottery picks.
  none   no salary or fairness regulation: no cap, no floor, no maximum contract, no staff pay limits; nothing is paid to an exiled club; no lottery
         (the exiled clubs draft by record like everyone else). The structure of the league (divisions, exile of the fifth-placed clubs, the draft) stays.

A league with no "parity" in its meta.json is "tight", which changes nothing."""
from __future__ import annotations

import economy as EC

PROFILES = {
    "tight": dict(economy={}, options={}),
    "none": dict(economy=dict(REGULATED=False, FLOOR_FRAC=0.0, ABSORPTION=0.0, MAX_SALARY=1.0e6, STAFF_CONTRACT_MAX_PCT=1.0e3, STAFF_PAYROLL_MAX_PCT=1.0e3),
                 options=dict(lottery_pool="none", returner_slot="by_record")),
}
NAMES = tuple(PROFILES)
_original = {k: getattr(EC, k) for p in PROFILES.values() for k in p["economy"]}      # the shipped numbers, so a profile can be switched back (tests)
_current = "tight"


def apply(name: str = "tight") -> str:
    """Set the economy's dials for the profile and remember the Options it needs. Call it before the league is opened."""
    global _current
    if name not in PROFILES:
        raise ValueError(f"unknown parity profile {name!r} (one of {', '.join(NAMES)})")
    for k, v in _original.items():
        setattr(EC, k, v)
    for k, v in PROFILES[name]["economy"].items():
        setattr(EC, k, v)
    _current = name
    return name


def current() -> str:
    return _current


def options() -> dict:
    """Keyword arguments for season.Options under the current profile (empty for tight)."""
    return dict(PROFILES[_current]["options"])
