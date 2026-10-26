"""Build the read-only website: export the founding league's data (site_export.py) and pour it into site/template.html (with the animated field, site/stage.js, written into it). One self-contained page.

    python engine/build_site.py [out.html] [seed]
    python engine/build_site.py --live [out.html] [seed]     the live page: no results of the autopilot season, only the founding rosters

The live page learns everything that happens from the feed the live runner writes (engine/live.py), so the data poured into it holds no game, standing, seed or champion.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import site_export

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def spoiler_free(d: dict) -> dict:
    """Remove every result of the autopilot season from the exported data."""
    d["live"] = True
    d["box"] = {}
    d["games"], d["ambassador"], d["playoffs"] = [], [], []
    d["seeds"], d["division_ranks"], d["champion"] = {}, {}, None
    for c in d["clubs"]:
        c["record"] = dict(w=0, l=0, t=0, pf=0, pa=0, exit="", div_rank=0)
        c.pop("ambassador", None)
    return d


def build(out: str, seed: int = 7, live: bool = False, rules: int = 1) -> int:
    d = site_export.export(seed, rules)
    data = json.dumps(spoiler_free(d) if live else d, separators=(",", ":")).replace("</", "<\\/")      # safe inside a script tag
    stage = open(os.path.join(ROOT, "site", "stage.js"), encoding="utf-8").read()
    stage3d = open(os.path.join(ROOT, "site", "stage3d.js"), encoding="utf-8").read()
    html = open(os.path.join(ROOT, "site", "template.html"), encoding="utf-8").read().replace("__STAGE__", stage).replace("__STAGE3D__", stage3d).replace("__DATA__", data)
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    return len(html)


def build_ed815_preview(out: str) -> int:
    """Opt-in canonical founding preview; never call the legacy simulated export."""
    import ed815_site_preview
    from pathlib import Path
    target = Path(out)
    if target.exists():
        raise FileExistsError(f"preview output already exists: {target}")
    html = ed815_site_preview.render_html(
        ed815_site_preview.SOURCE.read_text(encoding="utf-8")
    )
    with target.open("x", encoding="utf-8") as file:
        file.write(html)
    return len(html)


if __name__ == "__main__":
    if "--ed815-preview" in sys.argv:
        args = [a for a in sys.argv[1:] if a != "--ed815-preview"]
        if len(args) != 1 or "--live" in args:
            raise SystemExit("Usage: build_site.py --ed815-preview <new-output.html>")
        print(args[0], build_ed815_preview(args[0]), "bytes; preview only")
        raise SystemExit(0)
    args = [a for a in sys.argv[1:] if a != "--live"]
    out = args[0] if args else os.path.join(ROOT, "site", "index.html")
    print(out, build(out, int(args[1]) if len(args) > 1 else 7, "--live" in sys.argv), "bytes")
