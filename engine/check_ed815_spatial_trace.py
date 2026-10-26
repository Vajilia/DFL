"""Spatial trace contract: 22 identities, 0.05 s steps, lossless bytes."""
import copy

import ed815_spatial_trace as T

players = [{"id": f"{side}-{i}", "side": side, "x": 12.0 + i,
            "y": 3.0 + i, "intent": "block-left" if side == "home" else "cover"}
           for side in ("home", "away") for i in range(11)]
frames = [{"tick": t,
           "players": [{**p, "x": p["x"] + t / 10.0} for p in players],
           "ball": {"x": 20.0 + t, "y": 23.4, "z": 0.9,
                    "holder": "home-0" if t == 0 else None},
           "decisive_events": ["snap"] if t == 0 else ["pass-release"] if t == 2 else []}
          for t in range(3)]
bundle = T.pack(frames)
assert T.unpack(bundle) == frames
assert T.pack(copy.deepcopy(frames)) == bundle
assert bundle["frames"] == 3

def must_reject(changed):
    try:
        T.pack(changed)
    except ValueError:
        return
    raise AssertionError("invalid spatial trace accepted")

for name, edit in (
    ("gap", lambda a: a[1].update(tick=5)),
    ("missing-player", lambda a: a[0]["players"].pop()),
    ("duplicate-id", lambda a: a[0]["players"][0].update(id="away-0")),
    ("wrong-team", lambda a: a[0]["players"][0].update(side="away")),
    ("nonfinite", lambda a: a[0]["ball"].update(z=float("nan"))),
    ("unknown-holder", lambda a: a[1]["ball"].update(holder="unknown")),
    ("missing-intent", lambda a: a[0]["players"][0].pop("intent")),
    ("live-swap", lambda a: a[1]["players"][0].update(id="other-player")),
    ("invalid-event", lambda a: a[1].update(decisive_events=[{}])),
):
    altered = copy.deepcopy(frames)
    edit(altered)
    must_reject(altered)

corrupted = dict(bundle, sha256="0"*64)
try:
    T.unpack(corrupted)
except ValueError:
    pass
else:
    raise AssertionError("tampered checksum accepted")
truncated = dict(bundle, data=bundle["data"][:-1])
try:
    T.unpack(truncated)
except ValueError:
    pass
else:
    raise AssertionError("truncated trace accepted")
extra = dict(bundle, data=bundle["data"] + b"extra")
try:
    T.unpack(extra)
except ValueError:
    pass
else:
    raise AssertionError("trailing payload accepted")
print("OK: 22-player 0.05s lossless spatial trace contract, malformed input rejected")
