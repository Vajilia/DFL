"""The enrichment agent and the profile page (stage 2 of the character creator).

A prospect row (prospects.py) is a skeleton: position, age, ratings and an origin (college, date of birth, hometown, four college seasons).
When a player is *selected* (drafted in the first two rounds, or whenever anything wants to show her) the richer detail is filled in by a separate agent:
a short paragraph about her, her `bio`, written from the facts on her card. The profile page the website shows is then rendered from the card
(`profile`), so a card stays what it always was: a text document holding everything a decider needs.

The agent is a plug, like the decision drivers: `lg.enricher` is a function `payload dict -> text` (None means no agent). Whatever it says is
checked and may be discarded; the code writer (`code_bio`) always has an answer, so a league never waits on, or depends on, an agent. A bio is
flavour only: it is never read by the engine, nothing in it changes a rating, a price or a result, and no random number comes from the engine's
stream. At most `AGENT_CALLS_PER_YEAR` agent calls are made in a season; everyone beyond that gets the code writer's paragraph (and a card that says so).
"""
from __future__ import annotations

import cards as C
import prospects as PR

AGENT_CALLS_PER_YEAR = 24          # most agent-written bios a season: the first two rounds of the draft, in pick order, until the budget is spent
ENRICH_MAX_PICK = 96               # draftees at this pick or better are written up when they are drafted (rounds 1 and 2); the agent writes them when there is one
BIO_MIN, BIO_MAX = 60, 700         # characters: what a usable paragraph looks like

PATH_PHRASE = {
    "Power-conference star": "a star from the start at a power program",
    "Small-college standout": "the standout at a small program the big schools overlooked",
    "Late bloomer": "a late bloomer who did not look like a pro until her last two seasons",
    "Walk-on turned starter": "a walk-on who earned her scholarship and then her starting job",
    "International pathway": "who came to the game by the international route",
    "Two-sport athlete": "a two-sport athlete who gave up the other sport for this one",
    "Junior-college transfer": "a junior-college transfer who made the most of her second chance",
    "Overlooked recruit": "an overlooked recruit who has played with a chip on her shoulder since",
    "Coach's daughter": "a coach's daughter who grew up in the film room",
    "Came up through the academy system": "a product of the academy system",
}
TRAIT_PHRASE = {
    "Competitor": "a competitor who hates to lose at anything", "Loyalist": "loyal to a fault to whoever gives her a chance",
    "Mercenary": "clear-eyed about the business of the game", "Showman": "never happier than when the lights are on",
    "Quiet Leader": "a quiet leader the locker room listens to", "Hothead": "quick to anger and quicker to forgive",
    "Perfectionist": "a perfectionist who watches film long after the others leave",
    "Free Spirit": "a free spirit who plays loose", "Grinder": "a grinder who outworks everyone around her",
    "Diplomat": "the one who keeps the room together",
}


def _senior(pos: str, row: dict) -> str:
    if pos == "QB":
        return f"threw for {row['yds']:,} yards and {row['td']} touchdowns on {row['cmp']} completions"
    if pos == "RB":
        return f"ran for {row['yds']:,} yards and {row['td']} touchdowns"
    if pos in ("WR", "TE"):
        return f"caught {row['rec']} passes for {row['yds']:,} yards and {row['td']} touchdowns"
    if pos == "OL":
        return f"started {row['starts']} games and gave up {row['sacks_allowed']} sacks"
    if pos == "DL":
        return f"made {row['tkl']} tackles, {row['tfl']} for loss, and {row['sacks']} sacks"
    if pos == "LB":
        return f"made {row['tkl']} tackles with {row['sacks']} sacks and {row['tfl']} tackles for loss"
    if pos in ("CB", "S"):
        return f"made {row['tkl']} tackles with {row['ints']} interceptions and {row['pd']} passes defended"
    if pos == "K":
        return f"made {row['fg_made']} of {row['fg_att']} field goals, the longest from {row['long']} yards"
    return f"punted {row['punts']} times for a {row['avg']}-yard average"


def facts(lg, p) -> dict:
    """Everything a writer may use, and nothing else: no ratings but her tier, nothing about other people."""
    c = p.card
    o = PR.ensure_origin(lg.card_seed, p, c.born_year if c else 0)
    drafted = next((e for e in (c.career if c else []) if e["event"] == "drafted"), None)
    return dict(name=c.name, first=c.first, position=p.pos, age=p.age, born=o["dob"], hometown=o["hometown"], college=o["college"], college_tier=o["tier"],
                background=c.path, personality=c.trait, wants=c.wants, fears=c.fears, level=C.tier_label(p.ovr),
                senior_year=_senior(p.pos, o["stats"][-1]), college_seasons=[dict(o["stats"][i], line=PR.stat_line(p.pos, o["stats"][i])) for i in range(4)],
                draft=None if drafted is None else dict(year=drafted["year"], pick=drafted["pick"], team=lg.by_id[drafted["team"]].name if drafted.get("team") in lg.by_id else None))


def code_bio(lg, p) -> str:
    """The paragraph the code writes: always available, always from the card's own facts, the same every time for the same player."""
    f = facts(lg, p)
    r = C._rng(lg.card_seed, "bio", p.id)
    path = PATH_PHRASE.get(f["background"], "a player with her own road to the pros")
    trait = TRAIT_PHRASE.get(f["personality"], "a player who keeps her own counsel")
    small = f["college_tier"] == 3
    opening = r.choice((f"{f['name']} grew up in {f['hometown']}, {path}.", f"Out of {f['hometown']}, {f['name']} is {path}."))
    college = (f"She played at {f['college']}" + (", a program few scouts pass through, " if small else " ") + f"and as a senior {f['senior_year']}.")
    if f["draft"] is None:
        pro = r.choice(("She came to camp as a free agent and had to earn every rep.", "Nobody drafted her; she signed on and has been proving it ever since."))
    elif f["draft"]["pick"] <= 48:
        pro = f"{f['draft']['team']} took her with pick {f['draft']['pick']} in {f['draft']['year']}, in the first round."
    else:
        pro = f"{f['draft']['team']} drafted her with pick {f['draft']['pick']} in {f['draft']['year']}."
    close = f"Teammates call her {trait}; she wants {f['wants']} and fears {f['fears']}."
    return " ".join((opening, college, pro, close))


def valid(text, f) -> bool:
    """Is this usable as her paragraph? Plain text of a sensible length that is about her (it names her school or her town)."""
    return (isinstance(text, str) and BIO_MIN <= len(text.strip()) <= BIO_MAX and "\n\n" not in text.strip() and "```" not in text
            and (f["college"] in text or f["hometown"] in text or f["name"] in text))


def enrich(lg, p, year: int, use_agent: bool = True) -> str:
    """Give her a bio if she has none: the agent's if there is one, it answers and it passes the check; the code writer's otherwise. Returns how it was written."""
    c = p.card
    if c is None or c.enriched:
        return c.enriched if c else ""
    f = facts(lg, p)
    text, how = None, "code"
    agent = getattr(lg, "enricher", None)
    if use_agent and agent is not None:
        try:
            got = agent(dict(task="bio", year=year, facts=f, instructions="Write one short paragraph (2 to 4 sentences, plain text) about this player for her page. "
                             "Use only these facts. Do not invent statistics, teammates or events."))
        except Exception:
            got = None
        if valid(got, f):
            text, how = got.strip(), "agent"
    c.bio = text if text is not None else code_bio(lg, p)
    c.enriched = how
    return how


def run(lg, year: int) -> dict:
    """The season's enrichment pass (called after the cards are made): the first-two-rounds draftees of this year, best pick first. The agent writes them up
    to the call budget (the code writer does the rest). Everyone else is written when someone asks (profile, ensure_bio): a card is a text document and
    most of the league's players are never looked at."""
    calls = code = 0
    everyone = [p for t in lg.teams for p in list(t.roster) + list(t.practice_squad) + list(t.ir)] + list(lg.free_agents)
    new = sorted((p for p in everyone if p.card is not None and not p.card.enriched and p.draft_year == year and p.draft_pick and p.draft_pick <= ENRICH_MAX_PICK),
                 key=lambda p: p.draft_pick)
    for p in new:
        want = p.draft_pick <= ENRICH_MAX_PICK and calls < AGENT_CALLS_PER_YEAR and getattr(lg, "enricher", None) is not None
        how = enrich(lg, p, year, use_agent=want)
        calls += want
        code += how == "code"
    return dict(drafted=len(new), agent_calls=calls, code_bios=code)


def ensure_bio(lg, p, year: int = 0):
    """Anything that wants to show a player (a profile page, a scene) calls this first: she has a bio afterwards."""
    if p.card is not None and not p.card.enriched:
        enrich(lg, p, year, use_agent=False)


def profile(lg, p, year: int = 0) -> str:
    """Her page: rendered from her card and kept on it. Markdown, so any site can show it."""
    ensure_bio(lg, p, year)
    c, o = p.card, PR.ensure_origin(lg.card_seed, p, p.card.born_year)
    team = lg.by_id[p.team_id].name if p.team_id in lg.by_id else ("retired" if p.retired else "free agent")
    L = [f"# {c.name}", f"**{p.pos} · {team} · age {p.age} · {C.tier_label(p.ovr)}**", "",
         f"Born {c.dob} · {c.hometown} · {o['college']}", "", "## About", c.bio, "", "## College career",
         "| Year | Games | Line |", "|---|---|---|"]
    L += [f"| {s['class_year']} | {s['games']} | {PR.stat_line(p.pos, s)} |" for s in o["stats"]]
    if c.honors:
        L += ["", "## Honors", ", ".join(f"{h.get('title', h.get('honor', 'honor'))} {h.get('year', '')}".strip() for h in c.honors)]
    L += ["", "## Pro career"]
    for e in c.career:
        if e["event"] == "drafted":
            L.append(f"- {e['year']}: drafted, pick {e['pick']}" + (f", {lg.by_id[e['team']].name}" if e.get("team") in lg.by_id else ""))
        elif e["event"] == "retired":
            L.append(f"- {e['year']}: retired at {e['age']}")
        elif e["event"] != "personality_shift":
            L.append(f"- {e['year']}: {e['event']}")
    c.profile = "\n".join(L)
    return c.profile
