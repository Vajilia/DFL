"""Step 6c/6d: who owns the draft picks, who holds a player's rights, and how a restricted free agent changes clubs.

Three things live here, and they are saved together in their own SQLite tables (store.py, format 3):

  PICKS     the ledger of ordinary draft picks for the coming draft and the three after it. A pick keeps four separate facts: its original club,
            its current owner, its slot once the draft order is known, and whether a pending offer has it reserved or a player has been selected
            with it. The draft follows the current owner; it never changes the slot or the rookie price, which belong to the slot.
  RIGHTS    a qualifying tender (exclusive-rights below 3 accrued seasons, restricted at exactly 3, and any expiring player of an exiled club)
            creates rights for the club. An unqualified player has no rights and goes to the market. UFAs cannot be tendered.
  OFFERS    a restricted free agent's tender can be answered by another club's binding, funded offer. Funded means the cap room is there and is held
            back while the offer is open; compensation is a pick the offering club owns in the tender's round or an earlier one, held back too.
            The prior club has five days to match every represented term. A match releases both holds. If it does not match, the player and the
            compensation change hands together or not at all.

TAGS      one franchise (non-exclusive or exclusive) or transition tag a club a year on an expiring unrestricted player. The tag price is a table lookup
            (the top-7 or top-15 average at her position, 120% of her last cap number, escalating if the same club tags her again), and the tag is a
            one-year guaranteed contract. A non-exclusive franchise tag and a transition tag take offers like a restricted tender; the franchise
            tag carries two first-round picks as compensation, the transition tag none. An exclusive franchise takes no offers.

What this slice does not do (recorded in the rulebook rows): NFL incentives and special contract clauses, competing offer sheets for one player,
unsigned-rights carryover, full trades, compensatory awards. `transfer_pick` is the one door a trade will use for picks.

    "Days" are the league's offseason calendar: an offer made on day d can be matched through day d + 5; at day d + 6 it is committed.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Tuple

import economy as EC
import rules as R
from positions import STARTERS

HORIZON = 3                                  # NFL: picks can be traded for the coming draft and up to three drafts ahead (draft.trading row)
LEVELS = ("first", "second", "original", "refusal")
MATCH_TOLERANCE = 0.20                       # MODEL: the prior club matches an offer up to this far above the player's market price
TAG_MATCH_TOLERANCE = 0.40                   # MODEL: a club matches further above market for a player it franchised or transitioned
TAG_TYPES = ("franchise", "exclusive", "transition")
TAG_KIND = {"franchise": "franchise", "exclusive": "franchise_x", "transition": "transition"}
FRANCHISE_PICKS = 2                          # NFL: a franchise-tagged player carries two first-round picks as compensation
FRANCHISE_KINDS = ("franchise", "franchise_x")
OFFERABLE = ("restricted", "franchise", "transition")     # the rights that take another club's offer sheet
TAG_MAX_STREAK = 3                           # NFL: the same player may be tagged at most three times in a row by her club
COMP_BASE = 100                              # a compensatory pick's "original" is COMP_BASE + its place in the round, never a club id (clubs are 0..47)
PICK_RECORD_YEARS = 1                        # MODEL: finished drafts older than this many years are dropped from the ledger


class MovementError(ValueError):
    """A movement request that is not legal. Nothing has changed when this is raised."""


@dataclass
class Pick:
    year: int                                # the draft year (the offseason after that season)
    rnd: int                                 # 1..7
    original: int                            # the club the pick belonged to when the ledger was made; its place in the order comes from this club
    owner: int                               # the club that makes the selection
    slot: Optional[int] = None               # overall slot 1..336 once the order is set
    reserved_by: Optional[int] = None        # id of the pending offer that holds it as compensation
    selected: Optional[int] = None           # id of the player taken with it

    @property
    def key(self) -> Tuple[int, int, int]:
        return (self.year, self.rnd, self.original)


@dataclass
class Right:
    year: int
    player_id: int
    club: int
    kind: str                                # "exclusive" (rights), "restricted", "franchise", "franchise_x" (exclusive franchise) or "transition"
    level: str                               # "exclusive" or one of LEVELS for tenders; the tag type for tags
    price: float                             # the one-year tender
    comp_round: Optional[int]                # the round of compensation an offer must carry (None: none)
    status: str                              # "tendered" (window open), "kept", "matched", "transferred"


@dataclass
class Offer:
    id: int
    year: int
    player_id: int
    offering: int
    original: int
    salary: float                            # yearly cap number, every represented term below must be matched
    years: int
    share: float                             # signing-bonus share
    guarantee_years: int
    pick: Optional[Tuple[int, int, int]]     # key of the compensation pick, None when the tender carries none
    day: int
    deadline: int
    status: str                              # "pending", "matched", "transferred", "void" (lapsed: could no longer be completed)
    extra: List[Tuple[int, int, int]] = field(default_factory=list)      # keys of further compensation picks (a franchise tag carries two)

    @property
    def keys(self) -> List[Tuple[int, int, int]]:
        return ([self.pick] if self.pick else []) + list(self.extra)


class Movement:
    def __init__(self):
        self.picks: Dict[Tuple[int, int, int], Pick] = {}
        self.rights: Dict[Tuple[int, int], Right] = {}          # (year, player_id)
        self.offers: Dict[int, Offer] = {}
        self.events: List[dict] = []
        self.day = 0
        self.next_offer = 1

    # ---- the ledger of picks ---------------------------------------------------------------------------------------------------------------
    def ensure_picks(self, lg, year: int):
        """The ledger holds this draft and the next three; finished drafts older than a year are dropped. Existing picks are never touched."""
        for y in range(year, year + HORIZON + 1):
            for rnd in range(1, R.DRAFT_ROUNDS + 1):
                for t in lg.teams:
                    self.picks.setdefault((y, rnd, t.id), Pick(y, rnd, t.id, t.id))
        for k in [k for k in self.picks if k[0] < year - PICK_RECORD_YEARS]:
            del self.picks[k]

    def begin_year(self, lg, year: int, pick_of: Dict[int, int]):
        """The offseason after season `year` opens: the ledger is extended, the day is zero, and each pick of this draft gets its slot."""
        self.day = 0
        self.ensure_picks(lg, year)
        for k, pk in self.picks.items():
            if k[0] == year:
                if pk.original >= COMP_BASE:               # a compensatory pick comes after the round's 48 regular picks and is paid the round's last rung
                    pk.slot = pk.rnd * R.DRAFT_PICKS_PER_ROUND
                else:
                    pk.slot = (pk.rnd - 1) * R.DRAFT_PICKS_PER_ROUND + pick_of[pk.original]
        for k in [k for k, r in self.rights.items() if k[0] < year - (TAG_MAX_STREAK if r.kind in FRANCHISE_KINDS else 1)]:
            del self.rights[k]

    def owned(self, year: int, club: int) -> List[Pick]:
        return sorted((p for p in self.picks.values() if p.year == year and p.owner == club), key=lambda p: (p.rnd, p.original))

    def comp_picks(self, year: int, rnd: int) -> List[Pick]:
        """The compensatory picks of a round, in the order they are made (best value first)."""
        return sorted((p for p in self.picks.values() if p.year == year and p.rnd == rnd and p.original >= COMP_BASE), key=lambda p: p.original)

    def slots_owned(self, year: int, club: int) -> List[int]:
        return [p.slot for p in self.owned(year, club) if p.slot is not None and p.selected is None]

    def transfer_pick(self, lg, key, new_owner: int, reason: str = "trade"):
        """Change a pick's owner. The one door for picks (offers use it, trades will). Reserved and used picks do not move."""
        pk = self.picks.get(key)
        if pk is None:
            raise MovementError(f"no such pick {key}")
        if new_owner not in lg.by_id:
            raise MovementError(f"no such club {new_owner}")
        if pk.selected is not None:
            raise MovementError(f"pick {key} has been used")
        if pk.reserved_by is not None:
            raise MovementError(f"pick {key} is held for offer {pk.reserved_by}")
        if pk.owner == new_owner:
            raise MovementError(f"club {new_owner} already owns pick {key}")
        self._event("pick_transfer", year=key[0], round=key[1], original=key[2], from_club=pk.owner, to_club=new_owner, reason=reason)
        pk.owner = new_owner

    def check_free(self, key):
        """Raise unless the pick can be used right now (checked before a player is made for it)."""
        pk = self.picks[key]
        if pk.reserved_by is not None:
            raise MovementError(f"pick {key} is held for offer {pk.reserved_by}")
        if pk.selected is not None:
            raise MovementError(f"pick {key} has been used")

    def select(self, key, player_id: int):
        self.check_free(key)
        self.picks[key].selected = player_id

    def undrafted(self, year: int) -> List[Pick]:
        return [p for p in self.picks.values() if p.year == year and p.selected is None]

    # ---- rights ----------------------------------------------------------------------------------------------------------------------------
    def tender(self, lg, p, level: str, year: int, exiled: bool = False) -> Right:
        """Create the club's rights in an expiring player and give her the one-year tender contract. Illegal levels raise before anything changes."""
        import service
        club = lg.by_id.get(p.team_id)
        if club is None or p not in club.roster:
            raise MovementError("only a player on a club's squad can be tendered")
        if (year, p.id) in self.rights:
            raise MovementError("already tendered this year")
        if p.years_left > 0:
            raise MovementError("her contract has not run out")
        cls = service.expiry_class(p, exiled=exiled)
        if cls == "unrestricted":
            raise MovementError("an unrestricted free agent cannot be tendered")
        if cls == "exclusive_rights":
            if level != "exclusive":
                raise MovementError("exclusive-rights players take only the exclusive tender")
            kind = "exclusive"
        else:
            if level not in LEVELS:
                raise MovementError(f"a restricted free agent takes one of {LEVELS}")
            kind = "restricted"
        comp = None
        if level == "first":
            comp = 1
        elif level == "second":
            comp = 2
        elif level == "original":
            if p.draft_pick is None:
                raise MovementError("an original-round tender needs a drafted player")
            comp = (p.draft_pick - 1) // R.DRAFT_PICKS_PER_ROUND + 1
        prior_base = max(0.0, p.salary - p.bonus)
        price = EC.tender_price(level, prior_base, p.credited_seasons)
        if exiled and service.expiry_class(p) == "unrestricted":
            # A veteran held only by the exile rule is tendered at her market price: the rights are the club's first refusal, not a discount
            # (a DFL adaptation; without it exile would hand a returning club cheap veterans, which the fair-competitiveness bands rule out)
            price = max(price, min(EC.MAX_SALARY, EC.market_salary(p.pos, p.ovr, p.credited_seasons)))
        EC.clear_contract(p)
        EC.sign(p, price, 1, share=0.0, guarantee_years=0)           # the tender is a one-year contract with no bonus and nothing guaranteed
        right = Right(year, p.id, club.id, kind, level, p.salary, comp, "tendered" if kind == "restricted" else "kept")
        self.rights[(year, p.id)] = right
        self._event("tender", year=year, player=p.id, club=club.id, level=level, price=right.price, comp_round=comp)
        return right

    # ---- tags ------------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def tag_table(lg, min_years_left: int = 1) -> Dict[str, List[float]]:
        """Cap numbers of players under contract past this offseason's expirations, by position, highest first. `min_years_left` is 1 once contracts have
        run down and 2 before they have (so the same players count either way)."""
        table: Dict[str, List[float]] = {}
        for t in lg.teams:
            for p in list(t.roster) + list(t.ir):
                if p.years_left >= min_years_left:
                    table.setdefault(p.pos, []).append(p.salary)
        for v in table.values():
            v.sort(reverse=True)
        return table

    def tag_of(self, year: int, club: int) -> Optional["Right"]:
        """The tag a club has used this year, if any."""
        for r in self.rights.values():
            if r.year == year and r.club == club and r.kind in FRANCHISE_KINDS + ("transition",):
                return r
        return None

    def tag_streak(self, year: int, club: int, player_id: int) -> int:
        """How many years in a row, up to the one before `year`, this club has franchise-tagged her."""
        n = 0
        while True:
            r = self.rights.get((year - 1 - n, player_id))
            if r is None or r.club != club or r.kind not in FRANCHISE_KINDS:
                return n
            n += 1

    def tag_price(self, p, tag_type: str, year: int, club: int, table: Dict[str, List[float]]) -> float:
        """The one-year price. Franchise (either kind): the average of the top 7 cap numbers at her position or 120% of her last cap number, whichever is more;
        her club's second consecutive tag is at least 120% of the first, its third at least 144% of the second and at least the quarterback number and 120% of the
        position number. A transition tag: the average of the top 15 or 120% of her last cap number. Never above the maximum contract."""
        if tag_type not in TAG_TYPES:
            raise MovementError(f"unknown tag {tag_type!r}")
        n = EC.TRANSITION_TAG_TOP_N if tag_type == "transition" else EC.FRANCHISE_TAG_TOP_N
        top = table.get(p.pos, [])[:n]
        avg = sum(top) / len(top) if top else 0.0
        price = max(avg, EC.TAG_PRIOR_FACTOR * p.salary)
        if tag_type != "transition":
            streak = self.tag_streak(year, club, p.id)
            if streak >= TAG_MAX_STREAK:
                raise MovementError("a club may tag the same player at most three years in a row")
            if streak >= 1:
                prev = self.rights[(year - 1, p.id)].price
                price = max(price, EC.TAG_PRIOR_FACTOR * prev)
            if streak >= 2:
                qb_top = table.get("QB", [])[:EC.FRANCHISE_TAG_TOP_N]
                qb = sum(qb_top) / len(qb_top) if qb_top else 0.0
                price = max(price, EC.TAG_THIRD_FACTOR * prev, qb, EC.TAG_PRIOR_FACTOR * avg)
        return round(min(EC.MAX_SALARY, price), 2)

    def tag(self, lg, p, tag_type: str, year: int, exiled: bool = False, table: Optional[Dict[str, List[float]]] = None) -> "Right":
        """A club tags an expiring unrestricted player: one tag a club a year, a one-year guaranteed contract at the tag price. Illegal tags raise before anything
        changes. An exiled club may tag. A franchise tag takes offers with two first-round picks as compensation; a transition tag takes offers with none; an
        exclusive franchise takes none."""
        import service
        club = lg.by_id.get(p.team_id)
        if club is None or p not in club.roster:
            raise MovementError("only a player on a club's 53 can be tagged")
        if p.years_left > 0:
            raise MovementError("her contract has not run out")
        if (year, p.id) in self.rights:
            raise MovementError("already tendered or tagged this year")
        if service.expiry_class(p) != "unrestricted":
            raise MovementError("only an unrestricted player takes a tag; the others take a tender")
        if self.tag_of(year, club.id) is not None:
            raise MovementError("a club has one tag a year")
        price = self.tag_price(p, tag_type, year, club.id, table if table is not None else self.tag_table(lg))
        EC.clear_contract(p)
        EC.sign(p, price, 1, share=0.0, guarantee_years=1)            # the tag is signed as a one-year contract and is guaranteed once signed
        kind = TAG_KIND[tag_type]
        comp = 1 if tag_type == "franchise" else None
        right = Right(year, p.id, club.id, kind, tag_type, p.salary, comp, "kept" if tag_type == "exclusive" else "tendered")
        self.rights[(year, p.id)] = right
        self._event("tag", year=year, player=p.id, club=club.id, type=tag_type, price=right.price)
        return right

    # ---- cap and pick reservations ---------------------------------------------------------------------------------------------------------
    def reserved_cap(self, club: int) -> float:
        return round(sum(o.salary for o in self.offers.values() if o.status == "pending" and o.offering == club), 4)

    def room(self, lg, club: int) -> float:
        """What the club could add for one more player: its limit less its offseason count (one open place filled), less what its open offers hold."""
        t = lg.by_id[club]
        return round(EC.limit(t) - EC.offseason_over(t, extra_slots=1) - self.reserved_cap(club), 4)

    def compensation_pick(self, year: int, offering: int, comp_round: Optional[int]) -> Optional[Pick]:
        """Own-or-better: a pick the club owns in the tender round, else the nearest earlier round. None when the tender carries no compensation."""
        if comp_round is None:
            return None
        for rnd in range(comp_round, 0, -1):
            held = [p for p in self.owned(year, offering) if p.rnd == rnd and p.reserved_by is None and p.selected is None]
            if held:
                return held[0]
        raise MovementError(f"club {offering} owns no available pick in round {comp_round} or better")

    def compensation_picks(self, year: int, offering: int, right: "Right") -> List[Pick]:
        """Every pick an offer for this right must carry. A restricted tender: one, own-or-better. A franchise tag: two first-round picks, the offering club's
        earliest (this draft's, then the next draft's). A transition tag: none."""
        if right.comp_round is None:
            return []
        if right.kind != "franchise":
            return [self.compensation_pick(year, offering, right.comp_round)]
        firsts = [p for y in range(year, year + HORIZON + 1) for p in self.owned(y, offering)
                  if p.rnd == 1 and p.reserved_by is None and p.selected is None]
        if len(firsts) < FRANCHISE_PICKS:
            raise MovementError(f"club {offering} does not own two first-round picks to put up for a franchise-tagged player")
        return firsts[:FRANCHISE_PICKS]

    # ---- offers ----------------------------------------------------------------------------------------------------------------------------
    def make_offer(self, lg, offering: int, player_id: int, salary: float, years: int, year: int,
                   share: Optional[float] = None, guarantee_years: int = 1) -> Offer:
        """A binding, funded offer to a restricted free agent whose tender window is open. Everything is checked before anything is reserved."""
        right = self.rights.get((year, player_id))
        if right is None or right.kind not in OFFERABLE or right.status != "tendered":
            raise MovementError("no open tender that takes an offer for that player")
        if offering == right.club:
            raise MovementError("a club cannot make an offer sheet to its own player")
        if offering not in lg.by_id:
            raise MovementError(f"no such club {offering}")
        if any(o.status == "pending" and o.player_id == player_id for o in self.offers.values()):
            raise MovementError("competing offer sheets are not supported: one offer at a time")
        if years < 1 or years > EC.CONTRACT_YEARS_MAX:
            raise MovementError("contract length out of range")
        if guarantee_years < 0 or guarantee_years > years:
            raise MovementError("guaranteed years must be between zero and the length of the contract")
        salary = round(salary, 2)
        if salary < right.price:
            raise MovementError("an offer cannot be below the tender")
        if salary > EC.MAX_SALARY:
            raise MovementError("above the maximum contract")
        if share is not None and not 0.0 <= share <= 1.0:
            raise MovementError("bonus share must be between zero and one")
        if self.room(lg, offering) + 1e-9 < salary:
            raise MovementError("the offer is not funded: the cap room is not there")
        pks = self.compensation_picks(year, offering, right)
        # all checks passed: reserve
        o = Offer(self.next_offer, year, player_id, offering, right.club, salary, int(years),
                  -1.0 if share is None else float(share), int(guarantee_years), pks[0].key if pks else None, self.day, self.day + R.RFA_MATCH_DAYS, "pending",
                  [p.key for p in pks[1:]])
        self.next_offer += 1
        self.offers[o.id] = o
        for pk in pks:
            pk.reserved_by = o.id
        self._event("offer", offer=o.id, year=year, player=player_id, offering=offering, original=right.club, salary=salary, years=o.years,
                    pick=list(o.pick) if o.pick else None, picks=[list(k) for k in o.keys], deadline=o.deadline)
        return o

    def _terms(self, o: Offer, p):
        """The contract the offer represents. A share of -1 means 'the league default for a veteran contract'."""
        return dict(salary=o.salary, years=o.years, share=None if o.share < 0 else o.share, guarantee_years=o.guarantee_years)

    def _player(self, lg, pid: int, club: int):
        t = lg.by_id[club]
        for p in t.roster:
            if p.id == pid:
                return p
        return None

    def match(self, lg, offer_id: int):
        """The prior club matches every represented term. It needs the cap room for the difference. Raises with nothing changed otherwise."""
        o = self.offers.get(offer_id)
        if o is None or o.status != "pending":
            raise MovementError("no pending offer")
        if self.day > o.deadline:
            raise MovementError("the matching period is over")
        p = self._player(lg, o.player_id, o.original)
        right = self.rights[(o.year, o.player_id)]
        if p is None or right.status != "tendered":
            raise MovementError("the player is no longer on the tender")
        t = lg.by_id[o.original]
        # room for the difference between the tender she holds and the terms of the offer
        spare = EC.limit(t) - EC.offseason_over(t) - self.reserved_cap(o.original)
        if spare + 1e-9 < o.salary - p.salary:
            raise MovementError("the prior club cannot fit the offer under its cap")
        # commit the match
        EC.clear_contract(p)
        terms = self._terms(o, p)
        EC.sign(p, terms["salary"], terms["years"], share=terms["share"], guarantee_years=terms["guarantee_years"])
        self._release(o, "matched")
        right.status = "matched"
        self._event("match", offer=o.id, year=o.year, player=o.player_id, club=o.original)

    def _release(self, o: Offer, status: str):
        o.status = status
        for key in o.keys:
            pk = self.picks[key]
            if pk.reserved_by == o.id:
                pk.reserved_by = None

    def commit(self, lg, offer_id: int):
        """Not matched: the player joins the offering club on the offer's terms and the compensation pick goes to the prior club, both or neither.
        Everything is validated first; if anything is wrong this raises and no state has changed."""
        o = self.offers.get(offer_id)
        if o is None or o.status != "pending":
            raise MovementError("no pending offer")
        right = self.rights.get((o.year, o.player_id))
        orig, off = lg.by_id[o.original], lg.by_id[o.offering]
        p = self._player(lg, o.player_id, o.original)
        if p is None or right is None or right.status != "tendered":
            raise MovementError("the player is no longer on the tender")
        held = []
        for key in o.keys:
            pk = self.picks.get(key)
            if pk is None or pk.reserved_by != o.id or pk.owner != o.offering or pk.selected is not None:
                raise MovementError("the compensation pick is no longer held for this offer")
            held.append(pk)
        # the offering club's room, counting the hold as its own money (the player is added in the place the hold was kept for)
        if EC.limit(off) - EC.offseason_over(off, extra_slots=1) - (self.reserved_cap(o.offering) - o.salary) + 1e-9 < o.salary:
            raise MovementError("the offering club can no longer fund the offer")
        # -- no failure past this line
        orig.roster.remove(p)
        EC.clear_contract(p)
        terms = self._terms(o, p)
        EC.sign(p, terms["salary"], terms["years"], share=terms["share"], guarantee_years=terms["guarantee_years"])
        p.team_id, p.fa_years = off.id, 0
        off.roster.append(p)
        for pk in held:
            pk.owner = o.original
        self._release(o, "transferred")
        right.status = "transferred"
        self._event("transfer", offer=o.id, year=o.year, player=o.player_id, from_club=o.original, to_club=o.offering,
                    pick=list(o.pick) if o.pick else None, picks=[list(k) for k in o.keys])

    def pass_on(self, lg, offer_id: int):
        """The prior club declines to match: committed at once."""
        self.commit(lg, offer_id)

    def advance(self, lg, days: int = 1):
        """Time passes. Offers whose matching period is over are committed in the order they were made."""
        if days < 0:
            raise MovementError("time does not run backwards")
        self.day += days
        for o in sorted((o for o in self.offers.values() if o.status == "pending" and self.day > o.deadline), key=lambda o: o.id):
            try:
                self.commit(lg, o.id)
            except MovementError as e:            # an offer that can no longer be completed lapses: both holds are released, the tender stands
                self.void(o.id, str(e))

    def void(self, offer_id: int, reason: str = "withdrawn"):
        """An open offer ends without a transfer: the cap hold and the pick hold are released and the player stays on her tender."""
        o = self.offers.get(offer_id)
        if o is None or o.status != "pending":
            raise MovementError("no pending offer")
        self._release(o, "void")
        self._event("void", offer=o.id, year=o.year, player=o.player_id, offering=o.offering, reason=reason)

    def close_window(self, year: int):
        """The tender window ends: rights still on the tender are kept by the club (she plays on the tender contract)."""
        if any(o.status == "pending" and o.year == year for o in self.offers.values()):
            raise MovementError("offers are still pending")
        for r in self.rights.values():
            if r.year == year and r.status == "tendered":
                r.status = "kept"

    def check_ready_for_draft(self, year: int):
        if any(o.status == "pending" for o in self.offers.values()):
            raise MovementError("the draft cannot start with offers pending")
        for pk in self.picks.values():
            if pk.year == year and pk.reserved_by is not None:
                raise MovementError(f"pick {pk.key} is still reserved")

    def _event(self, kind: str, **kw):
        self.events.append(dict(seq=len(self.events), day=self.day, kind=kind, **kw))

    # ---- the autopilot's side of the market (the Decision Point version will call the same doors) --------------------------------------------
    @staticmethod
    def choose_level(p, cls: str, market: float, prior_base: float, reach: float = 1.5) -> str:
        """The tender a club offers: the highest one whose price the player's market value covers. When no tender fits she is "extend": the club
        negotiates with her at the market like a free agent (the usual re-signing dice), either because she is worth less than the lowest tender
        or because she is worth more than `reach` times the tender (a club keeps a star by signing her at the market, not by paying a tender
        far below her worth). A MODEL rule of the autopilot (roster_model.tender_reach)."""
        if cls == "exclusive_rights":
            return "exclusive" if market >= EC.tender_price("exclusive", prior_base, p.credited_seasons) else "extend"
        for level in LEVELS:
            if level == "original" and p.draft_pick is None:
                continue
            price = EC.tender_price(level, prior_base)
            if market >= price:
                return level if market <= reach * price else "extend"
        return "extend"

    def run_market(self, lg, rng, rm, year: int, log: dict):
        """The restricted market, once a year, before the draft: a few clubs send offers; the prior clubs match or not; five days pass; whatever
        stands is committed. Rare, as in the NFL (rm.rfa_offer_prob)."""
        import rosters as RS
        rights = [r for r in self.rights.values() if r.year == year and r.kind in OFFERABLE and r.status == "tendered"]
        by_id = {}
        for t in lg.teams:
            for p in t.roster:
                by_id[p.id] = p
        rights.sort(key=lambda r: (-by_id[r.player_id].ovr, r.player_id))
        busy = set()
        for r in rights:
            p = by_id[r.player_id]
            market = EC.market_salary(p.pos, p.ovr, p.credited_seasons)
            tagged = r.kind != "restricted"
            if market < (1.0 if tagged else 1.25) * r.price:
                continue
            if rng.random() >= (rm.tag_offer_prob if tagged else rm.rfa_offer_prob):
                continue
            premium = 1.0 + rng.uniform(0.05, 0.40)
            salary = round(min(EC.MAX_SALARY, max(r.price, market * premium)), 2)
            best, best_gain = None, 0.0
            for t in lg.teams:
                if t.id == r.club or t.id in busy:
                    continue
                at = sorted((q.ovr for q in t.roster if q.pos == p.pos), reverse=True)
                floor = at[STARTERS[p.pos] - 1] if len(at) >= STARTERS[p.pos] else 45.0
                gain = p.ovr - floor
                if gain <= best_gain:
                    continue
                if self.room(lg, t.id) + 1e-9 < salary:
                    continue
                try:
                    self.compensation_picks(year, t.id, r)
                except MovementError:
                    continue
                best, best_gain = t, gain
            if best is None:
                continue
            try:
                self.make_offer(lg, best.id, p.id, salary, EC.contract_years(p), year)
            except MovementError:
                continue
            busy.add(best.id)
            log["offers"] = log.get("offers", 0) + 1
        self.advance(lg, 3)
        for o in sorted((o for o in self.offers.values() if o.status == "pending"), key=lambda o: o.id):
            p = by_id[o.player_id]
            market = EC.market_salary(p.pos, p.ovr, p.credited_seasons)
            tol = TAG_MATCH_TOLERANCE if self.rights[(o.year, o.player_id)].kind != "restricted" else MATCH_TOLERANCE
            if o.salary <= market * (1.0 + tol):
                try:
                    self.match(lg, o.id)
                    log["matched"] = log.get("matched", 0) + 1
                except MovementError:
                    pass
        self.advance(lg, R.RFA_MATCH_DAYS + 1 - 3)
        log["transferred"] = log.get("transferred", 0) + sum(1 for o in self.offers.values() if o.year == year and o.status == "transferred")
        self.close_window(year)


# ---- saving: the movement tables --------------------------------------------------------------------------------------------------------------
SCHEMA = """
CREATE TABLE IF NOT EXISTS movement_state(key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE IF NOT EXISTS movement_picks(year INTEGER, rnd INTEGER, original INTEGER, owner INTEGER, slot INTEGER, reserved_by INTEGER, selected INTEGER,
    PRIMARY KEY(year, rnd, original));
CREATE TABLE IF NOT EXISTS movement_rights(year INTEGER, player_id INTEGER, club INTEGER, kind TEXT, level TEXT, price REAL, comp_round INTEGER, status TEXT,
    PRIMARY KEY(year, player_id));
CREATE TABLE IF NOT EXISTS movement_offers(id INTEGER PRIMARY KEY, year INTEGER, player_id INTEGER, offering INTEGER, original INTEGER, salary REAL, years INTEGER,
    share REAL, guarantee_years INTEGER, pick_year INTEGER, pick_rnd INTEGER, pick_original INTEGER, day INTEGER, deadline INTEGER, status TEXT);
CREATE TABLE IF NOT EXISTS movement_offer_extra(offer_id INTEGER, seq INTEGER, year INTEGER, rnd INTEGER, original INTEGER, PRIMARY KEY(offer_id, seq));
CREATE TABLE IF NOT EXISTS movement_events(seq INTEGER PRIMARY KEY, day INTEGER, kind TEXT, json TEXT);
"""


def write(db: sqlite3.Connection, mv: Movement):
    """Replace the movement tables with this ledger. The caller commits."""
    import json                                  # the tables are created with the rest of the schema (store.SCHEMA), so this stays inside one transaction
    for tbl in ("movement_state", "movement_picks", "movement_rights", "movement_offers", "movement_offer_extra", "movement_events"):
        db.execute(f"DELETE FROM {tbl}")
    db.executemany("INSERT INTO movement_state VALUES(?,?)", [("day", str(mv.day)), ("next_offer", str(mv.next_offer))])
    db.executemany("INSERT INTO movement_picks VALUES(?,?,?,?,?,?,?)",
                   [(p.year, p.rnd, p.original, p.owner, p.slot, p.reserved_by, p.selected) for _, p in sorted(mv.picks.items())])
    db.executemany("INSERT INTO movement_rights VALUES(?,?,?,?,?,?,?,?)",
                   [(r.year, r.player_id, r.club, r.kind, r.level, r.price, r.comp_round, r.status) for _, r in sorted(mv.rights.items())])
    db.executemany("INSERT INTO movement_offers VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                   [(o.id, o.year, o.player_id, o.offering, o.original, o.salary, o.years, o.share, o.guarantee_years,
                     o.pick[0] if o.pick else None, o.pick[1] if o.pick else None, o.pick[2] if o.pick else None, o.day, o.deadline, o.status)
                    for _, o in sorted(mv.offers.items())])
    db.executemany("INSERT INTO movement_offer_extra VALUES(?,?,?,?,?)",
                   [(o.id, i, k[0], k[1], k[2]) for _, o in sorted(mv.offers.items()) for i, k in enumerate(o.extra)])
    db.executemany("INSERT INTO movement_events VALUES(?,?,?,?)", [(e["seq"], e["day"], e["kind"], json.dumps(e, sort_keys=True)) for e in mv.events])


def read(db: sqlite3.Connection) -> Movement:
    """Rebuild the ledger from the movement tables. A file with no such tables (a version-2 save) gives an empty ledger, which means every pick
    belongs to its original club: exactly what a version-2 league had."""
    import json
    mv = Movement()
    have = {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    if "movement_state" not in have:
        return mv
    st = dict(db.execute("SELECT key, value FROM movement_state"))
    if not st:                                    # tables made by a save that did not finish (a version-2 file mid-upgrade): no ledger yet
        return mv
    mv.day, mv.next_offer = int(st["day"]), int(st["next_offer"])
    for y, rnd, orig, owner, slot, res, sel in db.execute("SELECT year, rnd, original, owner, slot, reserved_by, selected FROM movement_picks"):
        mv.picks[(y, rnd, orig)] = Pick(y, rnd, orig, owner, slot, res, sel)
    for row in db.execute("SELECT year, player_id, club, kind, level, price, comp_round, status FROM movement_rights"):
        mv.rights[(row[0], row[1])] = Right(*row)
    for (i, y, pid, off, orig, sal, yrs, sh, gy, py, pr, po, day, dl, status) in db.execute(
            "SELECT id, year, player_id, offering, original, salary, years, share, guarantee_years, pick_year, pick_rnd, pick_original, day, deadline, status "
            "FROM movement_offers"):
        mv.offers[i] = Offer(i, y, pid, off, orig, sal, yrs, sh, gy, (py, pr, po) if py is not None else None, day, dl, status)
    if "movement_offer_extra" in have:
        for oid, _, y, rnd, orig in db.execute("SELECT offer_id, seq, year, rnd, original FROM movement_offer_extra ORDER BY offer_id, seq"):
            mv.offers[oid].extra.append((y, rnd, orig))
    mv.events = [json.loads(j) for (j,) in db.execute("SELECT json FROM movement_events ORDER BY seq")]
    return mv


def dump(mv: Movement) -> str:
    """The ledger as canonical text, for comparing two leagues."""
    import json
    return json.dumps(dict(day=mv.day, next_offer=mv.next_offer,
                           picks=[asdict(p) for _, p in sorted(mv.picks.items())],
                           rights=[asdict(r) for _, r in sorted(mv.rights.items())],
                           offers=[asdict(o) for _, o in sorted(mv.offers.items())],
                           events=mv.events), sort_keys=True)
