"""The Chronicle (2026-10-17): the league's weekly story is chosen, written, checked and kept once, apart from the game.

  1  separate from the game: the chronicle code imports nothing of the simulation, and reading a feed leaves every file in it exactly as it was
  2  selection: every finished week and playoff round gets 1-10 entries of 1-5 paragraphs (about 2 on average) under the word cap, and the biggest story is always in
  3  the fact checker holds text to its fact sheet: an invented number, score or name is caught, the true text is not
  4  the template writer always passes its own checker, and the same feed gives the same words
  5  written once: a unit already on disk is never rewritten, even if the feed is replayed; another league's chronicle is refused
  6  the LLM writer is off without a key and a price; when on, bad text is retried once and then replaced by the template, and the monthly budget stops it
  7  an unfinished week or round is not written
  8  the site shows the Chronicle on the home page and on its own page

    python engine/check_chronicle.py
"""
import ast, datetime as dt, hashlib, json, os, shutil, sys, tempfile, threading, functools, http.server

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chronicle as C
import live as L

failures = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else f"  {detail}"))
    if not ok:
        failures.append(name)


def tree_hash(root):
    h = hashlib.sha256()
    for dp, dn, fn in sorted(os.walk(root)):
        dn.sort()
        for f in sorted(fn):
            h.update(os.path.join(dp, f).encode())
            h.update(open(os.path.join(dp, f), "rb").read())
    return h.hexdigest()


def read_all(out):
    d = {}
    for fn in sorted(os.listdir(out)):
        if fn.endswith(".json") and fn[0].isdigit():
            j = json.load(open(os.path.join(out, fn)))
            j.pop("written", None)
            d[fn] = j
    return d


# ---- 1 separate from the game -------------------------------------------------------------------------------------------------------
tree = ast.parse(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "chronicle.py")).read())
imported = set()
for n in ast.walk(tree):
    if isinstance(n, ast.Import):
        imported |= {a.name.split(".")[0] for a in n.names}
    elif isinstance(n, ast.ImportFrom):
        imported.add((n.module or "").split(".")[0])
ok_imports = {"argparse", "csv", "datetime", "hashlib", "json", "os", "random", "re", "sys", "time", "injuries", "urllib"}
check("the chronicle code imports nothing of the simulation (only the standard library and the injury names)", imported <= ok_imports, str(sorted(imported - ok_imports)))
src_live = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "live.py")).read()
check("the live runner does not import the chronicle", "chronicle" not in src_live)

# ---- a finished season to write about ----------------------------------------------------------------------------------------------
EPOCH = int(dt.datetime(2026, 10, 13, 0, 0).timestamp() * 1000)
feed_dir = tempfile.mkdtemp()
run = L.Runner(feed_dir, 7, EPOCH)
s = run.world.advance_to(1)
run.tick(s.final_end + 1000)
L.write_json(os.path.join(feed_dir, "meta.json"), dict(seed=7, epoch_ms=EPOCH))
before = tree_hash(feed_dir)
feed = C.Feed(feed_dir)
out1 = tempfile.mkdtemp()
wrote = C.scan(feed, out1)
check("reading and writing about a feed leaves the feed untouched", tree_hash(feed_dir) == before)
docs = read_all(out1)
check("every one of the 19 weeks and 4 playoff rounds has a write-up", len(docs) == 23 and sum(k.startswith("1_w") for k in docs) == 19, str(sorted(docs)))

# ---- 2 selection ---------------------------------------------------------------------------------------------------------------------
counts = [len(d["entries"]) for d in docs.values()]
check("each unit has 1 to 10 entries", all(1 <= n <= 10 for n in counts), str(counts))
paras = [len(e["paragraphs"]) for d in docs.values() for e in d["entries"]]
check("each entry has 1 to 5 paragraphs", all(1 <= p <= 5 for p in paras), str(sorted(set(paras))))
stories = [len(e["paragraphs"]) for d in docs.values() for e in d["entries"] if e["id"] != "roundup"]
avg = sum(stories) / len(stories)
check("the stories average about two paragraphs (1.5 to 3)", 1.5 <= avg <= 3.0, f"{avg:.2f}")
words = [sum(len(p.split()) for e in d["entries"] if e["id"] != "roundup" for p in e["paragraphs"]) for d in docs.values()]
check("the stories of a unit stay under the word cap", max(words) <= C.WORD_CAP, str(max(words)))
check("each week ends with the short roundup", all(d["entries"][-1]["id"] == "roundup" for k, d in docs.items() if k.startswith("1_w")))
w1 = C.build_unit(feed, 1, "w5")
top = max(w1["games"], key=lambda g: (g["score"], -ord(g["id"][-1])))["score"]
picked = C.select(w1)
check("the highest-scoring game of a week is always among the stories", max(p["score"] for p in picked) == top)
check("an upset (a 0-4 club beating a 3-1 club) outranks a plain result", C.story_score(dict(angles=[dict(t="upset", s=90)]), False) > C.story_score(dict(angles=[]), False))
check("the final is always a story, and says who won the title", "champions" in docs["1_playoff_final.json"]["entries"][0]["headline"] and docs["1_playoff_final.json"]["entries"][0]["score"] >= 90)

# ---- 3 the fact checker ------------------------------------------------------------------------------------------------------------------
fa = C.build_unit(feed, 1, "w5")
pick = C.select(fa)[0]
sheet = C.fact_sheet(feed, fa, pick)
good = C.write_template(sheet)
txt = good["headline"] + "\n" + "\n".join(good["paragraphs"])
check("the true text passes the checker", not C.check_text(txt, sheet), str(C.check_text(txt, sheet)))
wp, lp = max(sheet["hp"], sheet["ap"]), min(sheet["hp"], sheet["ap"])
bad_num = f"{sheet['winner']['name']} won {wp + 7}-{lp}."
check("a wrong score is caught, even when each of its numbers appears elsewhere on the sheet", any(p.startswith("score") for p in C.check_text(bad_num, sheet)))
check("an invented player is caught", any("Zorbak" in p for p in C.check_text("Quarterback Mirelda Zorbak threw for the winners.", sheet)))
check("an invented club is caught", any("Wombats" in p for p in C.check_text("The Wombats were stunned.", sheet)))
check("a spelled-out wrong number is caught", any("number" in p for p in C.check_text("They won by thirty-seven points.", sheet)) or any("number" in p for p in C.check_text("They scored thirty touchdowns.", sheet)))
check("a sentence opener is not mistaken for a name", not C.check_text("Meanwhile, nothing else happened.", sheet))
inj_text = "The " + sheet["home"]["nick"] + " lost a starter."
check("a club's nickname is allowed", not C.check_text(inj_text, sheet))

# ---- 4 template writer: passes its own checker, deterministic ------------------------------------------------------------------
out2 = tempfile.mkdtemp()
C.scan(C.Feed(feed_dir), out2)
check("the same feed gives the same words (twice)", read_all(out1) == read_all(out2))

# ---- 5 written once ------------------------------------------------------------------------------------------------------------------------
fp = os.path.join(out1, "1_w3.json")
doc = json.load(open(fp))
doc["entries"][0]["headline"] = "KEPT AS WRITTEN"
json.dump(doc, open(fp, "w"))
again = C.scan(C.Feed(feed_dir), out1)
check("rescanning writes nothing and keeps the words as they were", again == [] and json.load(open(fp))["entries"][0]["headline"] == "KEPT AS WRITTEN")
other = tempfile.mkdtemp()
shutil.copytree(out1, other, dirs_exist_ok=True)
L.write_json(os.path.join(feed_dir, "meta.json"), dict(seed=8, epoch_ms=EPOCH))
try:
    C.scan(C.Feed(feed_dir), other)
    refused = False
except SystemExit:
    refused = True
check("another league's chronicle is refused rather than mixed", refused)
L.write_json(os.path.join(feed_dir, "meta.json"), dict(seed=7, epoch_ms=EPOCH))
idx = json.load(open(os.path.join(out1, "index.json")))["units"]
check("the index lists every unit in order, oldest first", [(u["year"], u["unit"]) for u in idx][:3] == [(1, "w1"), (1, "w2"), (1, "w3")] and idx[-1]["unit"] == "playoff_final")

# ---- 6 the LLM writer ----------------------------------------------------------------------------------------------------------------
check("the LLM writer is off without a key and a price", not C.LLMWriter(env={}).enabled() and not C.LLMWriter(env={"ANTHROPIC_API_KEY": "k", "DFL_CHRONICLE_MODEL": "m"}).enabled())
env = {"ANTHROPIC_API_KEY": "k", "DFL_CHRONICLE_MODEL": "m", "DFL_PRICE_IN": "3", "DFL_PRICE_OUT": "15"}
calls = []


def fake(reply, tin=1500, tout=300):
    def transport(body):
        calls.append(body)
        return {"content": [{"type": "text", "text": reply}], "usage": {"input_tokens": tin, "output_tokens": tout}}
    return transport


winner = sheet["winner"]["nick"]
n = sheet["paragraphs"]
true_reply = json.dumps(dict(headline=f"{winner} win {wp}-{lp}", paragraphs=[f"The {winner} won {wp}-{lp}."] * n))
bad_reply = json.dumps(dict(headline="Zorbak shines", paragraphs=["Mirelda Zorbak scored 99 points."] * n))
spend_path = os.path.join(tempfile.mkdtemp(), "spend.json")
bud = C.Budget(spend_path, 18.0)
llm = C.LLMWriter(env=env, transport=fake(true_reply))
check("the LLM writer is on with a key, a model and both prices", llm.enabled())
ents, log = C.compose(feed, fa, llm, bud)
check("good LLM text is used, and its cost is counted against the month", log["llm_used"] >= 1 and bud.spent() > 0 and ents[0]["how"] == "llm", str(log))
calls.clear()
llm = C.LLMWriter(env=env, transport=fake(bad_reply))
ents, log = C.compose(feed, fa, llm, C.Budget(os.path.join(tempfile.mkdtemp(), "s.json"), 18.0))
check("invented names and numbers are retried once, then the template is used", len(calls) == 2 * len(C.select(fa)) and log["llm_used"] == 0 and all(e["how"] == "template" for e in ents), f"{len(calls)} {log}")
check("the template that replaced them passes the checker (nothing invented reaches the page)", all("Zorbak" not in " ".join(e["paragraphs"]) for e in ents))
calls.clear()
exhausted = C.Budget(os.path.join(tempfile.mkdtemp(), "s.json"), 0.0)
ents, log = C.compose(feed, fa, C.LLMWriter(env=env, transport=fake(true_reply)), exhausted)
check("with the month's budget spent no call is made and the templates carry on", not calls and all(e["how"] == "template" for e in ents))


def boom(body):
    raise OSError("network down")


ents, log = C.compose(feed, fa, C.LLMWriter(env=env, transport=boom), C.Budget(os.path.join(tempfile.mkdtemp(), "s.json"), 18.0))
check("an API failure falls back to the templates", len(ents) >= 2 and all(e["how"] == "template" for e in ents))
est = C.estimate(feed)
check("--estimate reports the size of a week's prompts", est and est["stories"] >= 1 and est["input_tokens"] > 500 and est["output_tokens"] > 0, str(est))
print("ESTIMATE one week:", est)

# ---- 7 unfinished units are not written ---------------------------------------------------------------------------------------------
part = tempfile.mkdtemp()
shutil.copytree(feed_dir, part, dirs_exist_ok=True)
for fn in os.listdir(os.path.join(part, "g")):
    if fn.startswith("1_r4_"):
        os.remove(os.path.join(part, "g", fn))
        break
po = tempfile.mkdtemp()
C.scan(C.Feed(part), po)
have = sorted(k for k in os.listdir(po) if k.startswith("1_w"))
check("a week with a game file missing, and every later unit, waits", "1_w4.json" not in have and "1_w3.json" in have and "1_playoff_final.json" not in os.listdir(po), str(have))

# ---- 8 the site ----------------------------------------------------------------------------------------------------------------------
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("SKIP the site is not checked here (playwright is not installed)")
    sync_playwright = None
if sync_playwright:
    import build_site
    root = tempfile.mkdtemp()
    build_site.build(os.path.join(root, "index.html"), 7, live=True, rules=5)
    shutil.copytree(feed_dir, os.path.join(root, "live"))
    shutil.copytree(out1, os.path.join(root, "live", "chronicle"))
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(type("Q", (http.server.SimpleHTTPRequestHandler,), {"log_message": lambda *a: None}), directory=root))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{srv.server_address[1]}/index.html"
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        errs = []
        pg = br.new_page(viewport=dict(width=1100, height=900))
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(url)
        pg.wait_for_timeout(3500)
        heads = pg.evaluate("[...document.querySelectorAll('#app h2')].map(h => h.textContent.trim())")
        check("the home page carries a 'From the Chronicle' block", "From the Chronicle" in heads, str(heads))
        pg.evaluate("location.hash='chronicle'")
        pg.wait_for_timeout(1500)
        art = pg.evaluate("document.querySelectorAll('#chr-body article').length")
        check("the Chronicle page shows the latest write-up and lists every week", art >= 1 and pg.evaluate("document.querySelectorAll('#chr-body a[href^=\"#chronicle-\"]').length") >= 20, str(art))
        pg.evaluate("location.hash='chronicle-1_w2'")
        pg.wait_for_timeout(1200)
        check("a week can be opened by its address and shows its stories", "Week 2" in pg.evaluate("document.querySelector('#chr-body h2').textContent") and pg.evaluate("document.querySelectorAll('#chr-body article').length") >= 4)
        tabs = pg.evaluate("[...document.querySelectorAll('#tabs a')].map(a => a.textContent.trim().toUpperCase())")
        check("the Chronicle adds no tab", len(tabs) == 8, str(tabs))
        check("no script error", not errs, str(errs[:2]))
        br.close()
    srv.shutdown()

print()
print("FAILED: " + ", ".join(failures) if failures else "all chronicle checks passed")
sys.exit(1 if failures else 0)
