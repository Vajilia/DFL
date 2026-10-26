"""Edition 8.15 standings and playoff qualification, isolated from the legacy runner.

Source: docs/DFL_Design_Document_Ed8.15.md §3.
No input-order-dependent randomness, no head-to-head/restart, and no half-win ties.
All inputs are plain records: clubs {id: {division, conference}} and games
{home, away, home_score, away_score}. Only completed regular-season games.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
from typing import Iterable, Mapping


@dataclass
class Record:
    wins: int = 0
    losses: int = 0
    div_wins: int = 0
    div_losses: int = 0
    conf_wins: int = 0
    conf_losses: int = 0
    points_for: int = 0
    points_against: int = 0
    opponents: list = field(default_factory=list)
    beaten: list = field(default_factory=list)
    games_played: int = 0

    @property
    def win_pct(self) -> float:
        return self.wins / (self.wins + self.losses) if self.wins + self.losses else 0.0

    @property
    def div_pct(self) -> float:
        return self.div_wins / (self.div_wins + self.div_losses) if self.div_wins + self.div_losses else 0.0

    @property
    def conf_pct(self) -> float:
        return self.conf_wins / (self.conf_wins + self.conf_losses) if self.conf_wins + self.conf_losses else 0.0

    @property
    def differential(self) -> int:
        return self.points_for - self.points_against


def build_records(clubs: Mapping, games: Iterable[Mapping]) -> dict:
    """Ties affect points and games played, but no standings records or opponents."""
    out = {club: Record() for club in clubs}
    seen = set()
    for game in games:
        home, away = game["home"], game["away"]
        if home not in clubs or away not in clubs or home == away:
            raise ValueError("invalid opponents")
        hs, aas = game["home_score"], game["away_score"]
        if not isinstance(hs, int) or not isinstance(aas, int) or min(hs, aas) < 0:
            raise ValueError("scores must be nonnegative integers")
        key = game.get("id")
        if key is not None:
            if key in seen:
                raise ValueError("duplicate game id")
            seen.add(key)
        rh, ra = out[home], out[away]
        rh.games_played += 1
        ra.games_played += 1
        rh.points_for += hs
        rh.points_against += aas
        ra.points_for += aas
        ra.points_against += hs
        if hs == aas:
            continue
        winner, loser = (home, away) if hs > aas else (away, home)
        rw, rl = out[winner], out[loser]
        rw.wins += 1
        rl.losses += 1
        rw.beaten.append(loser)
        rw.opponents.append(loser)
        rl.opponents.append(winner)
        if clubs[home]["division"] == clubs[away]["division"]:
            rw.div_wins += 1
            rl.div_losses += 1
        if clubs[home]["conference"] == clubs[away]["conference"]:
            rw.conf_wins += 1
            rl.conf_losses += 1
    return out


def opponent_pct(ids: Iterable, records: Mapping) -> float:
    w = sum(records[club].wins for club in ids)
    l = sum(records[club].losses for club in ids)
    return w / (w + l) if w + l else 0.0


def _draw(seed: int | str, scope: str, club) -> int:
    payload = f"{seed}|{scope}|{club}".encode("utf-8")
    return int.from_bytes(hashlib.sha256(payload).digest(), "big")


def ranking(club_ids: Iterable, clubs: Mapping, records: Mapping, seed: int | str, scope: str) -> list:
    """One lexicographic cascade, no head-to-head and no iterative restart.

    Context eligibility is determined by the *entire* group tied after
    overall wins and overall win percentage, not by pairwise comparisons.
    This avoids non-transitive sort comparators.
    """
    ids = list(club_ids)
    if len(set(ids)) != len(ids) or any(c not in clubs or c not in records for c in ids):
        raise ValueError("unknown or duplicate club")
    groups = {}
    for cid in ids:
        rec = records[cid]
        key = (rec.wins, rec.win_pct)
        groups.setdefault(key, []).append(cid)
    result = []
    for primary in sorted(groups, reverse=True):
        tied = groups[primary]
        same_div = len({(clubs[c]["conference"], clubs[c]["division"]) for c in tied}) == 1
        same_conf = len({clubs[c]["conference"] for c in tied}) == 1
        def rank_key(cid):
            r = records[cid]
            return (
                r.div_wins if same_div else 0,
                r.div_pct if same_div else 0,
                r.conf_wins if same_conf else 0,
                r.conf_pct if same_conf else 0,
                opponent_pct(r.opponents, records),
                r.differential,
                opponent_pct(r.beaten, records),
                _draw(seed, scope, cid),
            )
        result.extend(sorted(tied, key=rank_key, reverse=True))
    return result


def division_orders(clubs: Mapping, records: Mapping, seed: int | str) -> dict:
    groups = {}
    for cid, info in clubs.items():
        groups.setdefault((info["conference"], info["division"]), []).append(cid)
    return {k: ranking(ids, clubs, records, seed, f"division:{k[0]}:{k[1]}") for k, ids in groups.items()}


def playoff_seeds(clubs: Mapping, records: Mapping, seed: int | str) -> dict:
    """4 division champions and 3 other clubs per conference; no fifth-place wild cards."""
    divisions = division_orders(clubs, records, seed)
    result = {}
    for conference in sorted({info["conference"] for info in clubs.values()}):
        divisions_here = [ids for (c, _), ids in divisions.items() if c == conference]
        if len(divisions_here) != 4 or any(len(ids) != 5 for ids in divisions_here):
            raise ValueError("expected four five-club active divisions per conference")
        winners = [ids[0] for ids in divisions_here]
        excluded = {ids[-1] for ids in divisions_here}
        available = [cid for cid, info in clubs.items()
                     if info["conference"] == conference and cid not in winners and cid not in excluded]
        if len(available) < 3:
            raise ValueError("insufficient wild card candidates")
        top_four = ranking(winners, clubs, records, seed, f"playoff:{conference}:division")
        wildcards = ranking(available, clubs, records, seed, f"playoff:{conference}:wildcard")[:3]
        result[conference] = top_four + wildcards
    return result


def next_season_division_seeds(clubs: Mapping, records: Mapping, ambassadors: Mapping, seed: int | str) -> dict:
    """Each division's last-place active club is next ambassador; old ambassador returns seed 5."""
    out = {}
    for division, ordered in division_orders(clubs, records, seed).items():
        if len(ordered) != 5 or division not in ambassadors:
            raise ValueError("expected five active clubs and one returning ambassador per division")
        out[division] = {"next_seeds": ordered[:4] + [ambassadors[division]],
                         "next_ambassador": ordered[4]}
    return out
