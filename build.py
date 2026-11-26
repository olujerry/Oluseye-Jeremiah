#!/usr/bin/env python3
"""
build.py: reads articles.json + projects.json and writes index.html.
Run locally:  python build.py
GitHub Actions runs this on every push and every Monday.

articles.json fields:
  title, url, platform, tags[], excerpt   (required)
  date      "YYYY-MM"  (optional; dated articles sort first, newest on top)
  topics    ["Healthcare AI", ...]  (drives the topic filter + healthcare section)
  featured  <position>  (optional; shows the piece in "Selected writing")
"""
import json, html
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(__file__).parent

# ── Edit your details here ────────────────────────────────────────────────
CONFIG = {
    "name": "Oluseye Jeremiah",
    "full_name": "Oluseye Jeremiah Oluwapelumi",
    "roles": ["AI Engineer", "Technical Writer", "AI in Healthcare"],
    "location": "Lagos, Nigeria · Remote",
    "email": "oluseyejeremiah@gmail.com",
    "linkedin": "",          # e.g. "https://www.linkedin.com/in/your-handle/"; leave "" to hide
    "github": "https://github.com/olujerry",
    "x": "https://x.com/olujerry19",
    "writing_since": 2021,
    "available": True,
    "now": [
        ("Writing", "Agents, RAG and vector search tutorials for Actian, via Hackmamba"),
        ("Building", "MalarAI, offline malaria detection on Android"),
    ],
}
TOPIC_ORDER = ["Healthcare AI", "Agents & RAG", "LLMs & GenAI", "Machine Learning",
               "Data & SQL", "Dev tools & APIs", "Python"]
# ──────────────────────────────────────────────────────────────────────────

articles = json.loads((ROOT / "articles.json").read_text(encoding="utf-8"))
projects = json.loads((ROOT / "projects.json").read_text(encoding="utf-8"))

PLATFORMS = {
    "DataCamp":     {"color": "#2f6fd6", "home": "https://www.datacamp.com/blog"},
    "freeCodeCamp": {"color": "#1f8a4c", "home": "https://www.freecodecamp.org/news/author/oluseye-jeremiah/"},
    "Twilio":       {"color": "#e0313b", "home": "https://www.twilio.com/en-us/blog/authors/author.oluseye-jeremiah"},
    "Strapi":       {"color": "#5b4fe9", "home": "https://strapi.io/user/oluseye-jeremiah"},
    "Hackmamba":    {"color": "#d9631e", "home": "https://dev.to/actiandev"},
    "Dev.to":       {"color": "#7a7a7a", "home": "https://dev.to/oluseyej"},
    "Medium":       {"color": "#8a8a8a", "home": "https://medium.com/@oluseyejeremiah"},
    "Hashnode":     {"color": "#2962ff", "home": "https://oluseyejeremiah.hashnode.dev"},
}
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()

e = html.escape
now = datetime.now(UTC)
year = now.year
updated = now.strftime("%d %B %Y").lstrip("0")
total = len(articles)

def slug(s): return "".join(c for c in s.lower() if c.isalnum())
def color(p): return PLATFORMS.get(p, {}).get("color", "#888")
def fmt_date(d):
    if not d: return ""
    y, m = d.split("-")[:2]
    return f"{MONTHS[int(m) - 1]} {y}"

# newest dated first, then undated in original order
dated = sorted((a for a in articles if a.get("date")), key=lambda a: a["date"], reverse=True)
articles_sorted = dated + [a for a in articles if not a.get("date")]
latest = dated[0] if dated else None

counts = {}
for a in articles: counts[a["platform"]] = counts.get(a["platform"], 0) + 1
platform_order = sorted(counts, key=lambda p: (-counts[p], p))
topic_counts = {t: sum(t in a.get("topics", []) for a in articles) for t in TOPIC_ORDER}

# ── Pieces ────────────────────────────────────────────────────────────────
roles_html = '<span class="sep" aria-hidden="true">/</span>'.join(f"<span>{e(r)}</span>" for r in CONFIG["roles"])

now_rows = "".join(f"<div><dt>{e(k)}</dt><dd>{e(v)}</dd></div>" for k, v in CONFIG["now"])
if latest:
    now_rows += (f'<div><dt>Latest</dt><dd><a href="{e(latest["url"])}" target="_blank" rel="noopener">'
                 f'{e(latest["title"])}</a> <span class="muted">· {fmt_date(latest["date"])}</span></dd></div>')

pub_strip = "".join(
    f'<a href="{e(PLATFORMS.get(p, {}).get("home", "#"))}" target="_blank" rel="noopener">{e(p)}</a>'
    for p in platform_order)

def project_card(pr, i):
    stack = "".join(f"<li>{e(s)}</li>" for s in pr.get("stack", []))
    links = "".join(
        f'<a class="tlink" href="{e(l["url"])}" target="_blank" rel="noopener">{e(l["label"])} <span aria-hidden="true">↗</span></a>'
        for l in pr.get("links", []))
    if i == 0:
        pts = "".join(f"<li>{e(p)}</li>" for p in pr.get("points", []))
        return f"""
      <article class="project project-lead">
        <div>
          <p class="kicker"><span class="idx">0{i + 1}</span>{e(pr.get("kicker", ""))}</p>
          <h3>{e(pr["name"])}</h3>
          <p class="project-sum">{e(pr["summary"])}</p>
        </div>
        <div class="pl-side">
          <ul class="points">{pts}</ul>
          <ul class="stack">{stack}</ul>
          <div class="project-links">{links}</div>
        </div>
      </article>"""
    return f"""
      <article class="project">
        <p class="kicker"><span class="idx">0{i + 1}</span>{e(pr.get("kicker", ""))}</p>
        <h3>{e(pr["name"])}</h3>
        <p class="project-sum">{e(pr["summary"])}</p>
        <ul class="stack">{stack}</ul>
        <div class="project-links">{links}</div>
      </article>"""

projects_html = "".join(project_card(p, i) for i, p in enumerate(projects))

health = [a for a in articles_sorted if "Healthcare AI" in a.get("topics", [])]
health_html = "".join(f"""
        <li><a href="{e(a['url'])}" target="_blank" rel="noopener">
          <span class="h-meta">{e(a['platform'])}{(' · ' + fmt_date(a.get('date'))) if a.get('date') else ''}</span>
          <span class="h-title">{e(a['title'])}</span>
          <span class="arr" aria-hidden="true">↗</span>
        </a></li>""" for a in health)

featured = sorted((a for a in articles if a.get("featured")), key=lambda a: int(a["featured"]))
def feat_card(a, i):
    tags = " · ".join(e(t) for t in a.get("tags", []))
    return f"""
      <a class="feat{' feat-lead' if i == 0 else ''}" href="{e(a['url'])}" target="_blank" rel="noopener">
        <span class="feat-meta"><span class="dot" style="background:{color(a['platform'])}"></span>{e(a['platform'])}<span class="feat-tags">{tags}</span></span>
        <h3>{e(a['title'])}</h3>
        <p>{e(a.get('excerpt', ''))}</p>
        <span class="read">Read <span aria-hidden="true">→</span></span>
      </a>"""
featured_html = "".join(feat_card(a, i) for i, a in enumerate(featured))

topic_btns = f'<button class="chip on" data-t="all" aria-pressed="true">All <span>{total}</span></button>'
for t in TOPIC_ORDER:
    if topic_counts[t]:
        topic_btns += f'<button class="chip" data-t="{slug(t)}" aria-pressed="false">{e(t)} <span>{topic_counts[t]}</span></button>'
plat_opts = '<option value="all">All publications</option>' + "".join(
    f'<option value="{slug(p)}">{e(p)} ({counts[p]})</option>' for p in platform_order)

rows_html = ""
for a in articles_sorted:
    tags = "".join(f"<span>{e(t)}</span>" for t in a.get("tags", []))
    topics = " ".join(slug(t) for t in a.get("topics", []))
    search = e(" ".join([a["title"], a["platform"], a.get("excerpt", ""), " ".join(a.get("tags", [])), " ".join(a.get("topics", []))]).lower())
    rows_html += f"""
      <li><a class="row" data-p="{slug(a['platform'])}" data-t="{topics}" data-s="{search}" href="{e(a['url'])}" target="_blank" rel="noopener">
        <span class="row-main"><span class="row-title">{e(a['title'])}</span><span class="row-plat"><span class="dot" style="background:{color(a['platform'])}"></span>{e(a['platform'])}{(' · ' + fmt_date(a.get('date'))) if a.get('date') else ''}</span></span>
        <span class="row-tags">{tags}</span>
        <span class="arr" aria-hidden="true">↗</span>
      </a></li>"""

contact_links = f'<a class="btn primary" href="mailto:{e(CONFIG["email"])}">Email me</a>'
if CONFIG["linkedin"]:
    contact_links += f'<a class="btn" href="{e(CONFIG["linkedin"])}" target="_blank" rel="noopener">LinkedIn</a>'
contact_links += f'<a class="btn" href="{e(CONFIG["github"])}" target="_blank" rel="noopener">GitHub</a>'
if CONFIG["x"]:
    contact_links += f'<a class="btn" href="{e(CONFIG["x"])}" target="_blank" rel="noopener">X</a>'

badge = '<span class="badge"><span class="pulse"></span>Open to freelance &amp; full-time roles</span>' if CONFIG["available"] else ""

CSS = """
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#f6f4ef;--surface:#fffdf9;--sunk:#efece4;--ink:#16150f;--mid:#47453d;--muted:#7a776b;
  --line:#e2ded3;--line2:#cbc6b6;--accent:#0b6b5d;--accent-2:#c2512b;--accent-ink:#fff;--accent-soft:#dff0eb;
  --serif:'Newsreader',Georgia,serif;--sans:'Inter',system-ui,sans-serif;--mono:'JetBrains Mono',ui-monospace,monospace;
  --ease-out:cubic-bezier(0.23,1,0.32,1);
  color-scheme:light;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --bg:#11120e;--surface:#191a15;--sunk:#0d0e0b;--ink:#eeebe1;--mid:#c3bfb2;--muted:#8d8a7d;
  --line:#2a2b24;--line2:#3b3c33;--accent:#5cc7ae;--accent-2:#eb8a63;--accent-ink:#0b1411;--accent-soft:#182a25;color-scheme:dark}}
:root[data-theme="dark"]{
  --bg:#11120e;--surface:#191a15;--sunk:#0d0e0b;--ink:#eeebe1;--mid:#c3bfb2;--muted:#8d8a7d;
  --line:#2a2b24;--line2:#3b3c33;--accent:#5cc7ae;--accent-2:#eb8a63;--accent-ink:#0b1411;--accent-soft:#182a25;color-scheme:dark}
html{scroll-behavior:smooth;scroll-padding-top:72px}
body{font-family:var(--sans);background:var(--bg);color:var(--ink);font-size:16px;line-height:1.6;-webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility}
a{color:inherit;text-decoration:none}
.wrap{max-width:1120px;margin:0 auto;padding:0 24px}
@media(max-width:520px){.wrap{padding:0 16px}}
:focus-visible{outline:2px solid var(--accent);outline-offset:3px;border-radius:4px}
.muted{color:var(--muted)}
.skip{position:absolute;left:-999px;top:8px;background:var(--ink);color:var(--bg);padding:8px 12px;border-radius:6px;z-index:99}
.skip:focus{left:8px}

/* nav */
.nav{position:sticky;top:0;z-index:30;background:color-mix(in srgb,var(--bg) 86%,transparent);backdrop-filter:saturate(1.4) blur(12px);border-bottom:1px solid var(--line)}
.nav .wrap{display:flex;align-items:center;gap:24px;height:60px}
.logo{font-family:var(--serif);font-size:19px;font-weight:600;letter-spacing:-.01em;display:flex;align-items:center;gap:10px}
.mark{width:26px;height:26px;border-radius:7px;background:var(--ink);color:var(--bg);display:grid;place-items:center;font-family:var(--mono);font-size:11px;font-weight:500;letter-spacing:-.04em}
.nav-links{display:flex;gap:24px;margin-left:auto;font-size:14px;color:var(--mid)}
.nav-links a{transition:color .15s ease}
.theme{background:none;border:1px solid var(--line2);color:var(--mid);width:34px;height:34px;border-radius:50%;cursor:pointer;font-size:15px;display:grid;place-items:center;transition:transform 160ms var(--ease-out),border-color .15s ease}
.theme:active{transform:scale(.94)}
@media(max-width:720px){.nav-links{display:none}.theme{margin-left:auto}}

/* hero */
.hero{padding:80px 0 0}
.hero-grid{display:grid;grid-template-columns:minmax(0,1.45fr) minmax(0,1fr);gap:56px;align-items:end}
@media(max-width:900px){.hero-grid{grid-template-columns:1fr;gap:40px}}
.badge{display:inline-flex;align-items:center;gap:8px;font-size:13px;color:var(--accent);background:var(--accent-soft);padding:6px 12px;border-radius:999px;font-weight:500;margin-bottom:28px}
.pulse{width:7px;height:7px;border-radius:50%;background:var(--accent);animation:pulse 2.4s ease-in-out infinite}
@keyframes pulse{50%{opacity:.3}}
.roles{font-family:var(--mono);font-size:13px;color:var(--mid);display:flex;flex-wrap:wrap;gap:6px 10px;margin-bottom:18px;letter-spacing:.01em}
.roles .sep{color:var(--line2)}
h1{font-family:var(--serif);font-weight:500;font-size:clamp(2.5rem,5.6vw,4.4rem);line-height:1.02;letter-spacing:-.03em}
h1 .name-2{display:block;color:var(--accent);font-style:italic;font-weight:400;font-size:.62em;letter-spacing:-.02em;margin-top:.35em;line-height:1.1}
.who{color:var(--ink);font-weight:500}
.lede{font-size:clamp(1.05rem,1.5vw,1.18rem);color:var(--mid);max-width:54ch;margin-top:26px;line-height:1.65}
.lede strong{color:var(--ink);font-weight:600}
.ctas{display:flex;gap:10px;flex-wrap:wrap;margin-top:30px}
.btn{display:inline-flex;align-items:center;gap:6px;font-size:14.5px;font-weight:500;padding:11px 18px;border-radius:9px;border:1px solid var(--line2);background:var(--surface);transition:transform 160ms var(--ease-out),border-color .15s ease,background-color .15s ease,color .15s ease}
.btn:active{transform:scale(.97)}
.btn.primary{background:var(--ink);color:var(--bg);border-color:var(--ink)}

/* now panel */
.now{background:var(--surface);border:1px solid var(--line);border-radius:14px;overflow:hidden}
.now-head{display:flex;justify-content:space-between;align-items:center;padding:12px 18px;border-bottom:1px solid var(--line);font-family:var(--mono);font-size:11.5px;color:var(--muted);letter-spacing:.06em;text-transform:uppercase;background:var(--sunk)}
.now-head b{display:inline-flex;align-items:center;gap:7px;color:var(--accent);font-weight:500}
.now dl{padding:6px 18px}
.now dl div{display:grid;grid-template-columns:76px 1fr;gap:12px;padding:12px 0;border-bottom:1px dashed var(--line)}
.now dl div:last-child{border-bottom:0}
.now dt{font-family:var(--mono);font-size:11.5px;color:var(--muted);text-transform:uppercase;letter-spacing:.05em;padding-top:2px}
.now dd{font-size:14.5px;color:var(--mid);line-height:1.5}
.now dd a{color:var(--ink);text-decoration:underline;text-decoration-color:var(--line2);text-underline-offset:3px;transition:text-decoration-color .15s ease}
.now-stats{display:grid;grid-template-columns:repeat(3,1fr);border-top:1px solid var(--line)}
.now-stats div{padding:14px 18px;border-left:1px solid var(--line)}
.now-stats div:first-child{border-left:0}
.now-stats b{display:block;font-family:var(--serif);font-weight:500;font-size:1.6rem;line-height:1.1}
.now-stats span{font-size:12px;color:var(--muted)}

.pubs{margin-top:64px;padding:22px 0;border-top:1px solid var(--line);display:flex;flex-wrap:wrap;align-items:baseline;gap:8px 28px}
.pubs-label{font-family:var(--mono);font-size:11.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin-right:4px}
.pubs a{font-family:var(--serif);font-size:clamp(1.05rem,1.8vw,1.3rem);color:var(--mid);transition:color .15s ease}

/* sections */
section{padding:80px 0;border-top:1px solid var(--line)}
.sec-head{display:flex;align-items:end;justify-content:space-between;gap:16px 40px;flex-wrap:wrap;margin-bottom:36px}
.eyebrow{font-family:var(--mono);font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--accent);margin-bottom:10px}
h2{font-family:var(--serif);font-weight:500;font-size:clamp(1.9rem,3.6vw,2.7rem);letter-spacing:-.02em;line-height:1.08}
.sec-note{color:var(--muted);font-size:15px;max-width:42ch}

/* projects */
.projects{display:grid;grid-template-columns:repeat(2,1fr);gap:16px}
.project.project-lead{grid-column:1/-1;display:grid;grid-template-columns:minmax(0,1.3fr) minmax(0,1fr);gap:12px 48px;align-items:start}
.project-lead .pl-side{display:flex;flex-direction:column;gap:16px}
@media(max-width:820px){.project.project-lead{grid-template-columns:1fr}}
.points{list-style:none;display:flex;flex-direction:column;gap:10px}
.points li{display:grid;grid-template-columns:18px 1fr;font-size:15px;color:var(--mid)}
.points li::before{content:'+';font-family:var(--mono);color:var(--accent)}
@media(max-width:820px){.projects{grid-template-columns:1fr}}
.project{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:28px;display:flex;flex-direction:column;gap:12px}
.project.project-lead{background:var(--sunk)}
.project-lead > div:first-child{display:flex;flex-direction:column;gap:12px}
.project-lead h3{font-size:clamp(2rem,3.4vw,2.6rem)}
.project-lead .project-sum{font-size:16.5px}
.kicker{font-family:var(--mono);font-size:11.5px;color:var(--muted);letter-spacing:.04em;text-transform:uppercase;display:flex;gap:10px;align-items:center}
.idx{color:var(--accent)}
.project h3{font-family:var(--serif);font-weight:500;font-size:1.6rem;letter-spacing:-.015em;line-height:1.12}
.project-sum{color:var(--mid);font-size:15px;flex:1}
.stack{list-style:none;display:flex;flex-wrap:wrap;gap:6px}
.stack li{font-family:var(--mono);font-size:11.5px;padding:3px 8px;border-radius:6px;background:var(--bg);border:1px solid var(--line);color:var(--mid)}
.project-links{display:flex;flex-wrap:wrap;gap:18px;padding-top:14px;border-top:1px solid var(--line)}
.tlink{font-size:14px;font-weight:500;color:var(--accent);text-decoration:underline;text-decoration-color:transparent;text-underline-offset:3px;transition:text-decoration-color .15s ease}

/* healthcare */
.health{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.25fr);gap:56px}
@media(max-width:860px){.health{grid-template-columns:1fr;gap:28px}}
.health-copy p:not(.eyebrow){color:var(--mid);font-size:16.5px;margin-top:18px;max-width:46ch}
.health-copy p:not(.eyebrow) strong{color:var(--ink);font-weight:600}
.hlist{list-style:none;border-top:1px solid var(--line)}
.hlist a{display:grid;grid-template-columns:1fr 18px;gap:4px 14px;padding:18px 4px;border-bottom:1px solid var(--line);transition:background-color .15s ease}
.h-meta{font-family:var(--mono);font-size:11.5px;color:var(--muted);grid-column:1}
.h-title{font-family:var(--serif);font-size:1.25rem;line-height:1.3;grid-column:1;transition:color .15s ease}
.hlist .arr{grid-row:1/3;grid-column:2;align-self:center}

/* featured */
.feats{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
@media(max-width:900px){.feats{grid-template-columns:repeat(2,1fr)}}
@media(max-width:600px){.feats{grid-template-columns:1fr}}
.feat{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:24px;display:flex;flex-direction:column;gap:10px;transition:border-color .15s ease,transform 200ms var(--ease-out)}
.feat:active{transform:scale(.99)}
.feat.feat-lead{grid-column:span 2;background:var(--ink);color:var(--bg);border-color:var(--ink)}
.feat.feat-lead p,.feat.feat-lead .feat-meta{color:color-mix(in srgb,var(--bg) 76%,var(--ink))}
.feat.feat-lead p{font-size:16px;max-width:52ch}
.feat.feat-lead h3{font-size:clamp(1.5rem,2.6vw,2rem)}
.feat.feat-lead .read{color:var(--bg)}
@media(max-width:600px){.feat.feat-lead{grid-column:span 1}}
.feat-meta{display:flex;align-items:center;gap:8px;font-size:13px;color:var(--muted);flex-wrap:wrap}
.feat-tags{font-family:var(--mono);font-size:11px}
.feat-tags::before{content:"/";margin-right:8px;opacity:.5}
.dot{width:8px;height:8px;border-radius:50%;display:inline-block;flex-shrink:0}
.feat h3{font-family:var(--serif);font-weight:500;font-size:1.3rem;line-height:1.25;letter-spacing:-.01em}
.feat p{font-size:14.5px;color:var(--mid);flex:1}
.read{font-size:14px;font-weight:500;color:var(--accent);margin-top:6px}

/* archive */
.tools{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:14px}
.search,.select{font:inherit;font-size:15px;padding:11px 14px;border-radius:9px;border:1px solid var(--line2);background:var(--surface);color:var(--ink)}
.search{flex:1 1 280px}
.select{flex:0 0 auto;cursor:pointer}
.search::placeholder{color:var(--muted)}
.chips{display:flex;gap:6px;flex-wrap:wrap}
.chip{font:inherit;font-size:13px;padding:6px 12px;border-radius:999px;border:1px solid var(--line2);background:none;color:var(--mid);cursor:pointer;transition:transform 160ms var(--ease-out),background-color .15s ease,color .15s ease,border-color .15s ease}
.chip:active{transform:scale(.96)}
.chip span{color:var(--muted);font-family:var(--mono);font-size:11px;margin-left:2px}
.chip.on{background:var(--ink);color:var(--bg);border-color:var(--ink)}
.chip.on span{color:color-mix(in srgb,var(--bg) 70%,var(--ink))}
.count{font-size:13px;color:var(--muted);margin:18px 0 6px;font-family:var(--mono)}
.rows{list-style:none;border-top:1px solid var(--line)}
.row{display:grid;grid-template-columns:minmax(0,1fr) auto 18px;gap:20px;align-items:baseline;padding:15px 4px;border-bottom:1px solid var(--line);transition:background-color .12s ease}
.row-main{display:flex;flex-direction:column;gap:3px;min-width:0}
.row-title{font-family:var(--serif);font-size:1.1rem;line-height:1.35;transition:color .15s ease}
.row-plat{display:flex;align-items:center;gap:7px;font-size:12.5px;color:var(--muted)}
.row-tags{display:flex;gap:6px;justify-content:flex-end;flex-wrap:wrap;max-width:260px}
.row-tags span{font-family:var(--mono);font-size:11px;color:var(--muted);white-space:nowrap}
.row-tags span+span::before{content:"· ";opacity:.6}
.arr{color:var(--muted);font-size:13px}
@media(max-width:760px){.row{grid-template-columns:minmax(0,1fr) 18px;gap:2px 12px}.row-main{grid-column:1}.row-tags{display:none}.row .arr{grid-column:2;align-self:center}}
.empty{padding:28px 4px;color:var(--muted);display:none}

/* about */
.about{display:grid;grid-template-columns:1.2fr 1fr;gap:56px}
@media(max-width:820px){.about{grid-template-columns:1fr;gap:32px}}
.about p:not(.eyebrow){color:var(--mid);font-size:16.5px;margin-top:16px;max-width:60ch}
.about p strong{color:var(--ink);font-weight:600}
.offer{list-style:none}
.offer li{padding:18px 0;border-bottom:1px solid var(--line);display:grid;grid-template-columns:34px 1fr;gap:4px 12px}
.offer li:first-child{border-top:1px solid var(--line)}
.offer i{font-style:normal;font-family:var(--mono);font-size:12px;color:var(--accent);grid-row:span 2;padding-top:3px}
.offer b{font-weight:600;font-size:15.5px}
.offer span{color:var(--muted);font-size:14.5px}

/* contact */
.contact{background:var(--ink);color:var(--bg);border-top:0}
.contact .eyebrow{color:color-mix(in srgb,var(--accent) 60%,var(--bg))}
.contact h2{font-size:clamp(2.1rem,5.4vw,3.8rem);max-width:17ch}
.contact p:not(.eyebrow){color:color-mix(in srgb,var(--bg) 74%,var(--ink));margin-top:18px;max-width:52ch;font-size:16.5px}
.contact .btn{background:transparent;color:var(--bg);border-color:color-mix(in srgb,var(--bg) 30%,var(--ink))}
.contact .btn.primary{background:var(--bg);color:var(--ink);border-color:var(--bg)}
footer{padding:24px 0 40px;font-size:13px;color:var(--muted)}
footer .wrap{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap}

/* hover only on devices that really hover */
@media (hover:hover) and (pointer:fine){
  .nav-links a:hover,.pubs a:hover{color:var(--ink)}
  .theme:hover{color:var(--ink);border-color:var(--ink)}
  .btn:hover{border-color:var(--ink)}
  .btn.primary:hover{background:var(--accent);border-color:var(--accent);color:var(--accent-ink)}
  .contact .btn:hover{border-color:var(--bg)}
  .contact .btn.primary:hover{background:var(--accent);border-color:var(--accent);color:var(--accent-ink)}
  .tlink:hover{text-decoration-color:currentColor}
  .now dd a:hover{text-decoration-color:currentColor}
  .feat:hover{border-color:var(--line2);transform:translateY(-2px)}
  .chip:hover{border-color:var(--ink);color:var(--ink)}
  .chip.on:hover{color:var(--bg)}
  .row:hover,.hlist a:hover{background:var(--surface)}
  .row:hover .row-title,.hlist a:hover .h-title{color:var(--accent)}
}

/* one entrance for the hero, nothing else */
@media (prefers-reduced-motion:no-preference){
  .hero-grid > *{animation:rise 520ms var(--ease-out) both}
  .hero-grid > *:nth-child(2){animation-delay:90ms}
  @keyframes rise{from{opacity:0;transform:translateY(8px)}}
}
@media (prefers-reduced-motion:reduce){.pulse{animation:none}html{scroll-behavior:auto}.feat:hover{transform:none}}
"""

JS = """
(function(){
  var root=document.documentElement, btn=document.getElementById('theme');
  try{var t=localStorage.getItem('theme'); if(t) root.setAttribute('data-theme',t);}catch(e){}
  function isDark(){var t=root.getAttribute('data-theme'); return t? t==='dark' : matchMedia('(prefers-color-scheme: dark)').matches;}
  function icon(){btn.textContent=isDark()?'☀':'☾'; btn.setAttribute('aria-label',isDark()?'Switch to light theme':'Switch to dark theme');}
  icon();
  btn.addEventListener('click',function(){var n=isDark()?'light':'dark'; root.setAttribute('data-theme',n); try{localStorage.setItem('theme',n);}catch(e){} icon();});

  var q=document.getElementById('q'), sel=document.getElementById('plat'),
      chips=[].slice.call(document.querySelectorAll('.chip')),
      rows=[].slice.call(document.querySelectorAll('.row')), cnt=document.getElementById('cnt'),
      empty=document.getElementById('empty'), topic='all';
  function apply(){
    var term=q.value.trim().toLowerCase(), p=sel.value, n=0;
    rows.forEach(function(r){
      var ok=(topic==='all'||(' '+r.dataset.t+' ').indexOf(' '+topic+' ')>-1)
           &&(p==='all'||r.dataset.p===p)&&(!term||r.dataset.s.indexOf(term)>-1);
      r.parentNode.style.display=ok?'':'none'; if(ok)n++;
    });
    cnt.textContent=n; empty.style.display=n?'none':'block';
  }
  chips.forEach(function(c){c.addEventListener('click',function(){
    chips.forEach(function(x){x.classList.remove('on');x.setAttribute('aria-pressed','false');});
    c.classList.add('on'); c.setAttribute('aria-pressed','true'); topic=c.dataset.t; apply();
  });});
  q.addEventListener('input',apply); sel.addEventListener('change',apply);
})();
"""

initials = "".join(w[0] for w in CONFIG["name"].split()[:2]).upper()
first, last = CONFIG["name"].split(" ", 1)
years = year - CONFIG["writing_since"]

HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{e(CONFIG['name'])}: AI Engineer and Technical Writer</title>
<meta name="description" content="{e(CONFIG['full_name'])}: AI engineer and technical writer focused on AI in healthcare. {total} published tutorials on LLMs, agents, RAG, ML and data for DataCamp, freeCodeCamp, Twilio, Strapi and more.">
<meta property="og:title" content="{e(CONFIG['name'])}: AI Engineer and Technical Writer">
<meta property="og:description" content="AI engineer and technical writer focused on AI in healthcare. {total} published tutorials.">
<meta property="og:type" content="website">
<meta name="theme-color" content="#f6f4ef" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#11120e" media="(prefers-color-scheme: dark)">
<link rel="icon" type="image/x-icon" href="favicon.ico">
<link rel="icon" type="image/svg+xml" href="favicon.svg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;1,6..72,400;1,6..72,500&display=swap" rel="stylesheet">
<script>try{{var t=localStorage.getItem('theme');if(t)document.documentElement.setAttribute('data-theme',t)}}catch(e){{}}</script>
<style>{CSS}</style>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>

<nav class="nav" aria-label="Main">
  <div class="wrap">
    <a class="logo" href="#top"><span class="mark" aria-hidden="true">{e(initials)}</span>{e(CONFIG['name'])}</a>
    <div class="nav-links">
      <a href="#projects">Projects</a>
      <a href="#healthcare">Healthcare</a>
      <a href="#writing">Writing</a>
      <a href="#about">About</a>
      <a href="#contact">Contact</a>
    </div>
    <button class="theme" id="theme" type="button" aria-label="Toggle theme">☾</button>
  </div>
</nav>

<main id="main">
  <header class="hero" id="top">
    <div class="wrap">
      <div class="hero-grid">
        <div>
          {badge}
          <p class="roles"><span class="who">{e(CONFIG['full_name'])}</span></p>
          <h1>AI engineer &amp;<br>technical writer. <span class="name-2">Building AI for healthcare.</span></h1>
          <p class="lede">I build machine learning systems, from on-device medical imaging to LLM agents, and write the tutorials developers learn from. {total} published pieces on LLMs, agents, RAG, ML and data, each one built on code I actually ran.</p>
          <div class="ctas">
            <a class="btn primary" href="#contact">Work with me</a>
            <a class="btn" href="#projects">See projects</a>
          </div>
        </div>
        <aside class="now" aria-label="What I'm doing now">
          <div class="now-head"><span>Now</span><b><span class="pulse"></span>{now.strftime('%b %Y')}</b></div>
          <dl>{now_rows}</dl>
          <div class="now-stats">
            <div><b>{total}</b><span>articles</span></div>
            <div><b>{len(counts)}</b><span>publications</span></div>
            <div><b>{years}+ yrs</b><span>writing</span></div>
          </div>
        </aside>
      </div>
      <div class="pubs">
        <span class="pubs-label">Published by</span>
        {pub_strip}
      </div>
    </div>
  </header>

  <section id="projects">
    <div class="wrap">
      <div class="sec-head">
        <div><p class="eyebrow">Projects</p><h2>Things I've built</h2></div>
        <p class="sec-note">Each one shipped, with code or a write-up you can check.</p>
      </div>
      <div class="projects">{projects_html}
      </div>
    </div>
  </section>

  <section id="healthcare">
    <div class="wrap health">
      <div class="health-copy">
        <p class="eyebrow">Focus</p>
        <h2>AI in healthcare</h2>
        <p>My MSc research produced <strong>MalarAI</strong>, an on-device model that screens blood smears for malaria where connectivity is unreliable. I'm drawn to the same problem everywhere: making clinical AI accurate, explainable and usable in low-resource settings.</p>
        <p>These are the health-focused builds and tutorials I've published so far.</p>
      </div>
      <ul class="hlist">{health_html}
      </ul>
    </div>
  </section>

  <section id="selected">
    <div class="wrap">
      <div class="sec-head">
        <div><p class="eyebrow">Selected writing</p><h2>Start with these</h2></div>
        <p class="sec-note">Model deep-dives, evaluation, API tutorials and full-stack builds.</p>
      </div>
      <div class="feats">{featured_html}
      </div>
    </div>
  </section>

  <section id="writing">
    <div class="wrap">
      <div class="sec-head">
        <div><p class="eyebrow">Archive</p><h2>All writing</h2></div>
      </div>
      <div class="tools">
        <input class="search" id="q" type="search" placeholder="Search titles, tools or topics, e.g. RAG, SQL, Twilio" aria-label="Search articles">
        <select class="select" id="plat" aria-label="Filter by publication">{plat_opts}</select>
      </div>
      <div class="chips" role="group" aria-label="Filter by topic">{topic_btns}</div>
      <p class="count"><span id="cnt">{total}</span> articles</p>
      <ul class="rows">{rows_html}
      </ul>
      <p class="empty" id="empty">Nothing matches that search. Try a broader term or clear the filters.</p>
    </div>
  </section>

  <section id="about">
    <div class="wrap about">
      <div>
        <p class="eyebrow">About</p>
        <h2>Engineer first, then writer</h2>
        <p>I hold a <strong>BSc in Computer Science</strong> and an <strong>MSc in Data Science</strong> from the University of Ibadan. I build with Python, TensorFlow, LLM APIs and vector databases, and I write for developer audiences at DataCamp, freeCodeCamp, Twilio, Strapi and Hackmamba's clients.</p>
        <p>I was a Microsoft Learn Student Ambassador and a GDSC core team member, I've taught machine learning through Inventors, and I was a freeCodeCamp Top Contributor in 2023.</p>
      </div>
      <div>
        <p class="eyebrow">How I can help</p>
        <ul class="offer">
          <li><i>01</i><b>AI and ML engineering</b><span>Prototypes, evaluation and on-device models, especially for health.</span></li>
          <li><i>02</i><b>Build-along tutorials</b><span>A working project with your SDK or API, plus the step-by-step guide.</span></li>
          <li><i>03</i><b>AI and LLM explainers</b><span>Model launches, benchmarks, RAG and agents, tested hands-on.</span></li>
          <li><i>04</i><b>Docs and guides</b><span>Getting-started guides and integration docs developers actually finish.</span></li>
        </ul>
      </div>
    </div>
  </section>

  <section id="contact" class="contact">
    <div class="wrap">
      <p class="eyebrow">Contact</p>
      <h2>Building something in AI or health tech?</h2>
      <p>I'm open to AI engineering roles, freelance tutorials and technical content for AI, data and developer-tool teams. Tell me what you're working on.</p>
      <div class="ctas">{contact_links}</div>
    </div>
  </section>
</main>

<footer>
  <div class="wrap">
    <span>© {year} {e(CONFIG['full_name'])} · {e(CONFIG['location'])}</span>
    <span>Updated {updated}</span>
  </div>
</footer>

<script>{JS}</script>
</body>
</html>
"""

(ROOT / "index.html").write_text(HTML, encoding="utf-8")
print(f"Built index.html: {total} articles, {len(projects)} projects, {len(featured)} featured, {len(health)} healthcare, {updated}")
