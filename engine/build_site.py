"""Build the read-only website: export the founding league's data (site_export.py) and pour it into site/template.html. One self-contained page.

    python engine/build_site.py [out.html] [seed]
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import site_export

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def build(out: str, seed: int = 7) -> int:
    data = json.dumps(site_export.export(seed), separators=(",", ":")).replace("</", "<\\/")      # safe inside a script tag
    html = open(os.path.join(ROOT, "site", "template.html"), encoding="utf-8").read().replace("__DATA__", data)
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    return len(html)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "site", "index.html")
    print(out, build(out, int(sys.argv[2]) if len(sys.argv) > 2 else 7), "bytes")
