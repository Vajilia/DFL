"""Role utility: what a player is worth to a club in the role she would play, and what each seat in the league is judged on.

Two small ideas that the GM's roster decisions (gm_roster.py) and every Decision Point share.

1. A player's role on a club. At each position the club's players are ranked by rating: the best ones start (positions.STARTERS), the next few
   are backups who step in when a starter is hurt, and the rest are depth. Her role utility is what she adds to the club in that role, in the
   engine's own points: a player who would start adds (her rating over the weakest starter's) x (1 + 0.4 x starters at the position) + 5; a
   player who would only be a backup or depth is a small cost (her rating less 60), because the club pays her for a seat that does not
   win games. These are exactly the numbers the free-agency rule has always used (offseason._gain now calls utility() here), so the engine
   on the autopilot is unchanged; the GM is shown the same number, as she perceives it, when she chooses.

2. What each seat is judged on. The Diamond Coronation is the first priority of every role (decisions.coronation); under it each role has its
   own yardstick, in plain words, shown at the top of every decision the role makes. The ring of accountability: players answer to coaches,
   coaches and the GM to the CEO, the CEO to the fans.
"""
from __future__ import annotations

from typing import List

from positions import STARTERS

ROLES = ("starter", "backup", "depth")
EMPTY_SLOT = 45.0               # the rating a missing starter counts as (a newcomer at an empty slot always starts)

JUDGED_ON = {
    "owner": "Judged by the fans: the club's record and the Coronation, the fans' trust in your pledges, and a club that stays solvent "
             "(payroll floor of about $90M over four seasons). You hire and fire the GM and the head coach.",
    "gm": "Judged by the CEO: a roster that can win the Coronation inside the cap. You scout, draft, re-sign, sign and trade for role utility "
          "(what each player adds in her role: starter, backup or depth), not for names.",
    "coach": "Judged by the CEO: wins with the roster the GM gave you. You hire and fire the coordinators, approve their schemes and develop the players.",
    "coordinator": "Judged by the head coach: how well your side of the ball plays, in the scheme that fits the roster.",
    "player": "Judged by the coaches: the role you earn, and the pay your rating and years command.",
    "fans": "You are where outside revenue enters: you reward a club that wins and keeps its word, and you stay away from one that does not.",
}


def judged_on(actor_kind: str) -> str:
    return JUDGED_ON.get(actor_kind, "")


def slot_floor(roster, pos: str) -> float:
    """The rating of the weakest starter at a position (what a newcomer has to beat to start)."""
    at = sorted((p.ovr for p in roster if p.pos == pos), reverse=True)
    n = STARTERS[pos]
    return at[n - 1] if len(at) >= n else EMPTY_SLOT


def utility(roster, pos: str, ovr: float) -> float:
    """What a player of this rating adds to the club (the roster as it stands, without her) at her position."""
    n = STARTERS[pos]
    floor = slot_floor(roster, pos)
    if ovr > floor:                                       # she would start
        return (ovr - floor) * (1.0 + 0.4 * n) + 5.0
    return ovr - 60.0                                     # backup or depth: small and negative


def role_of(roster, p) -> str:
    """Her role on the club: starter, backup (the next few at the position) or depth."""
    n = STARTERS[p.pos]
    at: List = sorted((q for q in roster if q.pos == p.pos), key=lambda q: (-q.ovr, q.id))
    i = next((k for k, q in enumerate(at) if q is p), len(at))
    return "starter" if i < n else "backup" if i < n + max(1, (n + 1) // 2) else "depth"


def role_if_signed(roster, pos: str, ovr: float) -> str:
    """The role a newcomer of this rating would have on the club as it stands."""
    n = STARTERS[pos]
    better = sum(1 for q in roster if q.pos == pos and q.ovr >= ovr)
    return "starter" if better < n else "backup" if better < n + max(1, (n + 1) // 2) else "depth"
