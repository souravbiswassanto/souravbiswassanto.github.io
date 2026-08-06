#!/usr/bin/env python3
"""Render data/profile.json into review/index.html.

This is the *review* page, not the portfolio. It is deliberately plain: its only job is to let
Saurov read everything that was collected in one place and correct it. The real site gets built
from the same profile.json once the content is signed off.

Usage:  python3 build-review.py    (then open review/index.html in a browser)
"""

import html
import json
import pathlib

ROOT = pathlib.Path(__file__).parent
DATA = json.loads((ROOT / "data" / "profile.json").read_text())
OUT = ROOT / "review" / "index.html"


def e(x):
    return html.escape(str(x), quote=True)


def link(url, label=None):
    return f'<a href="{e(url)}">{e(label or url)}</a>'


out = []
w = out.append

SECTIONS = [
    ("identity", "Identity"),
    ("experience", "Profession"),
    ("education", "Education"),
    ("contact", "Contact"),
    ("metrics", "GitHub metrics"),
    ("projects", "Projects"),
    ("cases", "Case studies"),
    ("releases", "Release lifecycle"),
    ("writing", "Writing &amp; speaking"),
    ("skills", "Skills"),
    ("enterprise", "Enterprise impact"),
    ("cp", "Competitive programming"),
    ("photos", "Photos"),
    ("assets", "Assets"),
    ("constraints", "Constraints"),
]

w("""<!doctype html>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex">
<title>Collected portfolio data — Saurov Chandra Biswas</title>
<style>
  :root{--bg:#fff;--fg:#16181d;--mut:#5c6370;--line:#e2e5ea;--acc:#0b5fff;--card:#f7f8fa;
        --warn-bg:#fff8e6;--warn-line:#e6c15c;--warn-fg:#5c4708;--mono:ui-monospace,SFMono-Regular,Menlo,monospace}
  @media (prefers-color-scheme:dark){
    :root{--bg:#0f1115;--fg:#e6e8ec;--mut:#9aa2b1;--line:#262b34;--acc:#7aa2ff;--card:#161a21;
          --warn-bg:#2a2310;--warn-line:#7a6320;--warn-fg:#e8d18a}
  }
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--fg);
       font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
  .wrap{display:grid;grid-template-columns:220px minmax(0,1fr);gap:48px;
        max-width:1200px;margin:0 auto;padding:40px 24px 120px}
  nav{position:sticky;top:40px;align-self:start;font-size:14px}
  nav a{display:block;padding:4px 0;color:var(--mut);text-decoration:none;border:0}
  nav a:hover{color:var(--acc)}
  nav .navhead{font-weight:600;color:var(--fg);margin-bottom:8px}
  a{color:var(--acc);text-decoration:none;border-bottom:1px solid transparent}
  a:hover{border-bottom-color:currentColor}
  h1{font-size:28px;margin:0 0 4px;letter-spacing:-.01em}
  h2{font-size:19px;margin:56px 0 4px;padding-bottom:8px;border-bottom:1px solid var(--line);letter-spacing:-.01em}
  h2:first-of-type{margin-top:24px}
  h3{font-size:16px;margin:28px 0 6px}
  h4{font-size:14px;margin:18px 0 4px;color:var(--mut);text-transform:uppercase;letter-spacing:.05em}
  p{margin:8px 0}
  ul{margin:8px 0;padding-left:20px}
  li{margin:4px 0}
  .lede{color:var(--mut);margin-bottom:24px}
  .kv{display:grid;grid-template-columns:180px minmax(0,1fr);gap:2px 16px;margin:12px 0;font-size:15px}
  .kv dt{color:var(--mut)}
  .kv dd{margin:0}
  code,.mono{font-family:var(--mono);font-size:13px}
  .card{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:16px 20px;margin:14px 0}
  .warn{background:var(--warn-bg);border:1px solid var(--warn-line);color:var(--warn-fg);
        border-radius:8px;padding:14px 18px;margin:14px 0;font-size:14.5px}
  .warn b{color:inherit}
  .stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:16px 0}
  .stat{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:14px}
  .stat .v{font-family:var(--mono);font-size:24px;font-weight:600;letter-spacing:-.02em}
  .stat .l{font-size:13px;margin-top:2px}
  .stat .s{font-size:12px;color:var(--mut);margin-top:2px}
  table{border-collapse:collapse;width:100%;font-size:14px;margin:12px 0}
  th,td{text-align:left;padding:6px 10px 6px 0;border-bottom:1px solid var(--line);vertical-align:top}
  th{color:var(--mut);font-weight:500}
  .tags{margin-top:8px}
  .tag{display:inline-block;font-size:12px;font-family:var(--mono);color:var(--mut);
       border:1px solid var(--line);border-radius:99px;padding:1px 9px;margin:0 4px 4px 0}
  .meta{font-size:13px;color:var(--mut)}
  .quote{border-left:3px solid var(--acc);padding-left:14px;margin:10px 0;font-size:15px}
  @media(max-width:820px){.wrap{grid-template-columns:1fr;gap:0}nav{position:static;margin-bottom:32px}}
</style>
<div class="wrap">
<nav><div class="navhead">Sections</div>""")
for sid, label in SECTIONS:
    w(f'<a href="#{sid}">{label}</a>')
w("</nav>\n<main>")

ident, contact = DATA["identity"], DATA["contact"]
m = DATA["_meta"]

w(f"<h1>{e(ident['name'])} — collected portfolio data</h1>")
w(f'<p class="lede">Everything gathered in the data-collection pass, rendered plainly for review. '
  f'This is <b>not</b> the portfolio design — it exists so you can correct the facts before anything is built. '
  f'Collected {e(m["collected"])}.</p>')

w('<div class="warn"><b>Redaction in force.</b> Your second, part-time role is not named anywhere on this page '
  'or in the planned site — no company name, no job title. Its technical content appears only as unattributed '
  'independent engineering work.</div>')

# ---------------------------------------------------------------- identity
w('<h2 id="identity">Identity</h2>')
w('<dl class="kv">')
for k in ["name", "title", "company", "location", "hometown", "years_experience", "github_created"]:
    if ident.get(k):
        w(f"<dt>{e(k.replace('_',' '))}</dt><dd>{e(ident[k])}</dd>")
w("</dl>")
w(f'<h4>Positioning line <span class="meta">— {e(ident["tagline_status"])}</span></h4>')
w(f'<p class="quote">{e(ident["tagline"])}</p>')
w(f'<h4>Summary <span class="meta">— {e(ident["summary_status"])}</span></h4>')
w(f'<p class="quote">{e(ident["summary"])}</p>')

# ---------------------------------------------------------------- experience (moved to top)
w('<h2 id="experience">Profession</h2>')
for x in DATA["experience"]:
    if x.get("REDACTED"):
        w('<div class="card">')
        w(f'<h3>{e(x["public_label"])} <span class="meta">· {e(x["start"])} – {e(x["end"])}</span></h3>')
        w('<div class="warn"><b>Employer and job title withheld</b> — per your instruction, neither is '
          'recorded for publication. The content below is usable, unattributed.</div>')
        w("<ul>")
        for b in x["usable_content"]:
            w(f"<li>{e(b)}</li>")
        w("</ul>")
        w(f'<p class="meta">Supporting public repo: {link(x["supporting_public_repo"])}</p>')
        w("</div>")
        continue
    w('<div class="card">')
    w(f'<h3>{e(x["display_title"])} · {link(x["company_url"], x["company"])} '
      f'<span class="meta">· {e(x["location"])} · {e(x["start"])} – present</span></h3>')
    w("<h4>Progression</h4><table><tr><th>When</th><th>What</th></tr>")
    for p in x["progression"]:
        w(f'<tr><td class="mono">{e(p["when"])}</td><td>{e(p["what"])}</td></tr>')
    w("</table>")
    w("<h4>Scope</h4><ul>")
    for s in x["scope"]:
        w(f"<li>{e(s)}</li>")
    w("</ul><h4>Achievements</h4><ul>")
    for b in x["bullets"]:
        w(f"<li>{e(b)}</li>")
    w("</ul>")
    for r in x.get("removed_bullets", []):
        w(f'<div class="warn">{e(r)}</div>')
    w("</div>")

# ---------------------------------------------------------------- education (moved to top)
ed = DATA["education"]
w('<h2 id="education">Education</h2>')
w(f'<div class="warn">{e(ed["display_note"])}</div>')
pri = ed["primary"]
w('<div class="card">')
w(f'<h3>{e(pri["degree"])}</h3>')
w('<dl class="kv">')
w(f'<dt>institution</dt><dd>{e(pri["institution"])}, {e(pri["location"])}</dd>')
w(f'<dt>dates</dt><dd>{e(pri["start"])} – {e(pri["end"])}</dd>')
w(f'<dt>CGPA</dt><dd>{e(pri["cgpa"])}</dd>')
w(f'<dt>coursework</dt><dd>{e(" · ".join(pri["coursework"]))}</dd>')
w("</dl></div>")
w("<h4>Earlier academic record</h4><table><tr><th>Level</th><th>Institution</th><th>Result</th><th>Distinction</th></tr>")
for x in ed["earlier"]:
    w(f'<tr><td>{e(x["level"])}</td><td>{e(x["institution"])}<br><span class="meta">{e(x["location"])}</span></td>'
      f'<td class="mono">{e(x["result"] or "—")}</td><td>{e(x["distinction"] or "—")}</td></tr>')
w("</table>")
lead = ed["leadership"]
w(f'<h4>Leadership</h4><p><b>{e(lead["role"])}</b> <span class="meta">· {e(lead["period"])}</span><br>'
  f'{e(lead["detail"])}</p>')

w("<h4>Certifications</h4>")
for c in DATA["certifications"]:
    w('<div class="card">')
    w(f'<h3>{e(c["name"])}</h3><dl class="kv">')
    w(f'<dt>issuer</dt><dd>{e(c["issuer"])}</dd>')
    w(f'<dt>level</dt><dd>{e(c["level"])}</dd>')
    w(f'<dt>score</dt><dd>{e(c["score"])}</dd>')
    w(f'<dt>sections</dt><dd>{e(" · ".join(c["sections"]))}</dd>')
    w(f'<dt>awarded</dt><dd>{e(c["awarded"])}</dd>')
    w(f'<dt>certificate</dt><dd>{link(c["url"], "view PDF")}</dd>')
    w("</dl>")
    w(f'<p class="meta">{e(c["verified"])}</p>')
    w(f'<p><b>Placement:</b> {e(c["placement"])}</p>')
    w("</div>")

# ---------------------------------------------------------------- contact
w('<h2 id="contact">Contact</h2><dl class="kv">')
w(f'<dt>email (personal)</dt><dd>{link("mailto:"+contact["email_personal"], contact["email_personal"])}</dd>')
w(f'<dt>email (work)</dt><dd>{e(contact["email_work"])}</dd>')
w(f'<dt>phone</dt><dd>{e(contact["phone"])} — <b>not published</b></dd>')
w(f'<dt>github</dt><dd>{link(contact["github"])}</dd>')
w(f'<dt>linkedin</dt><dd>{link(contact["linkedin"])}</dd>')
w('<dt>website</dt><dd class="meta">none yet — this is what we are building</dd>')
w("</dl>")
w(f'<div class="warn">{e(contact["phone_note"])}</div>')

# ---------------------------------------------------------------- metrics
g = DATA["github_metrics"]
w('<h2 id="metrics">GitHub metrics</h2>')
w(f'<p class="meta">Queried live from the GitHub API on {e(g["verified_on"])} — every number below is reproducible.</p>')
w('<div class="stats">')
for s in g["headline_stats_for_site"]:
    w(f'<div class="stat"><div class="v">{e(s["value"])}</div><div class="l">{e(s["label"])}</div>'
      f'<div class="s">{e(s["sub"])}</div></div>')
w("</div>")
w("<h4>Output by year</h4><table><tr><th>Year</th><th>PRs authored</th><th>PRs reviewed</th></tr>")
for y in sorted(g["authored_by_year"]):
    w(f'<tr><td>{e(y)}</td><td class="mono">{g["authored_by_year"][y]}</td>'
      f'<td class="mono">{g["reviewed_by_year"][y]}</td></tr>')
w("</table>")
w(f'<p class="meta">Peak: {g["peak_month_authored"]["count"]} PRs authored in '
  f'{e(g["peak_month_authored"]["month"])} ({e(g["peak_month_authored"]["note"])}); '
  f'{g["peak_month_reviewed"]["count"]} reviewed in {e(g["peak_month_reviewed"]["month"])}. '
  f'{g["prs_merged"]} of {g["prs_authored_total"]} authored PRs merged; reviews span '
  f'{g["distinct_authors_reviewed_for"]} distinct authors.</p>')
w("<h4>Top repositories by PRs authored</h4><table><tr><th>Repository</th><th>PRs</th></tr>")
for r in g["top_repos_authored"]:
    w(f'<tr><td class="mono">{e(r["repo"])}</td><td class="mono">{r["prs"]}</td></tr>')
w("</table>")
w("<h4>By organisation</h4><p>")
w(" &nbsp;·&nbsp; ".join(f'<span class="mono">{e(k)}</span> {v}' for k, v in g["authored_by_org"].items()))
w("</p>")

# ---------------------------------------------------------------- projects
w('<h2 id="projects">Projects</h2>')
for p in DATA["flagship_projects"]:
    w('<div class="card">')
    title = e(p["name"])
    if p.get("org"):
        title += f' <span class="meta">· {e(p["org"])}</span>'
    elif p.get("org_note"):
        title += ' <span class="meta">· employer withheld</span>'
    w(f'<h3>{title}</h3>')
    w(f'<p class="meta">{e(p["role"])} · {e(p["period"])}</p>')
    w(f'<p>{e(p["summary"])}</p>')
    if p.get("highlights"):
        w("<ul>")
        for h in p["highlights"]:
            w(f"<li>{e(h)}</li>")
        w("</ul>")
    if p.get("related_writing"):
        w("<h4>Related writing &amp; talks</h4><ul>")
        for rw in p["related_writing"]:
            w(f'<li>{link(rw["url"], rw["title"])} <span class="meta">— {e(rw["date"])} · {e(rw["role"])}</span></li>')
        w("</ul>")
    w('<div class="tags">')
    for t in p.get("stack", []):
        w(f'<span class="tag">{e(t)}</span>')
    w("</div>")
    if p.get("links"):
        w('<p class="meta">' + " · ".join(link(l["url"], l["label"]) for l in p["links"]) + "</p>")
    w("</div>")

# ---------------------------------------------------------------- cases
w('<h2 id="cases">Case studies</h2>')
w('<p class="lede">These are the centrepiece of the site. Each is a real, measured piece of work — check '
  'the facts and the framing carefully, because these are what a hiring manager will actually read.</p>')
for c in DATA["case_studies"]:
    w('<div class="card">')
    w(f'<h3>{e(c["title"])}</h3>')
    if c.get("attribution"):
        w(f'<div class="warn"><b>Attribution:</b> {e(c["attribution"])}</div>')
    if c.get("title_note"):
        w(f'<p class="meta">{e(c["title_note"])}</p>')
    w(f'<p class="quote">{e(c["hook"])}</p>')
    w("<ul>")
    for b in c["body"]:
        w(f"<li>{e(b)}</li>")
    w("</ul>")
    w(f'<p class="meta">Evidence: {e(c["evidence"])}</p>')
    if c.get("related_writing"):
        w("<h4>Published alongside this work</h4><ul>")
        for rw in c["related_writing"]:
            w(f'<li>{link(rw["url"], rw["title"])} <span class="meta">— {e(rw["date"])} · {e(rw["role"])}</span></li>')
        w("</ul>")
    w('<div class="tags">' + "".join(f'<span class="tag">{e(t)}</span>' for t in c["tags"]) + "</div>")
    w("</div>")

# ---------------------------------------------------------------- release lifecycle
rl = DATA["release_lifecycle"]
w('<h2 id="releases">Release lifecycle</h2>')
w(f"<p>{e(rl['summary'])}</p>")
w("<table><tr><th>Release</th><th>Date</th><th>Announcement blog (authored)</th></tr>")
for r in rl["releases"]:
    note = f'<br><span class="meta">{e(r["note"])}</span>' if r.get("note") else ""
    w(f'<tr><td class="mono">{e(r["version"])}</td><td class="mono">{e(r["date"])}</td>'
      f'<td>{link(r["blog"], "Read")}{note}</td></tr>')
w("</table>")
w("<h4>Supporting release engineering</h4><ul>")
for s in rl["supporting_work"]:
    w(f"<li>{e(s)}</li>")
w("</ul>")
w(f'<div class="warn">{e(rl["url_caveat"])}</div>')

# ---------------------------------------------------------------- writing
wr = DATA["writing"]
w('<h2 id="writing">Writing &amp; speaking</h2>')
w("<h4>Featured deep-dives</h4><ul>")
for b in wr["blogs"]:
    if b.get("featured"):
        w(f'<li>{link(b["url"], b["title"])} <span class="meta">— {e(b["date"])}</span></li>')
w("</ul>")
w('<p class="meta">The 9 release-announcement posts now live under '
  '<a href="#releases">Release lifecycle</a>, next to the releases they announce.</p>')
w(f'<div class="warn">{e(wr["blog_count_note"])}</div>')
w("<h4>Documentation authored</h4><ul>")
for d in wr["docs"]:
    w(f"<li>{e(d)}</li>")
w("</ul>")
w(f'<p class="meta">{e(wr["docs_note"])}</p>')
w("<h4>Internal writing</h4><ul>")
for d in wr["internal"]:
    w(f"<li>{e(d)}</li>")
w("</ul>")
w("<h4>Speaking — recordings</h4>")
for s in wr["speaking"]:
    w(f'<div class="card"><b>{e(s["title"])}</b>'
      f'<p class="meta">{e(s["event"])} · {e(s["date"])} · {e(s["channel"])}</p>'
      f'<p>Watch: {link(s["video"])}</p>'
      f'<p class="meta">{e(s["verified"])}</p></div>')

# ---------------------------------------------------------------- skills
w('<h2 id="skills">Skills</h2><dl class="kv">')
for k, v in DATA["skills"].items():
    w(f'<dt>{e(k.replace("_"," "))}</dt><dd>{e(" · ".join(v))}</dd>')
w("</dl>")

# ---------------------------------------------------------------- enterprise
ent = DATA["enterprise_impact"]
w('<h2 id="enterprise">Enterprise impact</h2><dl class="kv">')
w(f'<dt>on-call regions</dt><dd>{e(" · ".join(ent["on_call_regions"]))}</dd>')
w(f'<dt>how customers are described</dt><dd>{e(" · ".join(ent["anonymized_descriptors"]))}</dd>')
w(f'<dt>platforms</dt><dd>{e(" · ".join(ent["platforms"]))}</dd>')
w("</dl>")
w(f'<div class="warn"><b>No customer names.</b> {e(ent["naming_decision"])}</div>')
w("<h4>Representative escalations solved</h4><ul>")
for x in ent["representative_escalations"]:
    w(f"<li>{e(x)}</li>")
w("</ul>")

# ---------------------------------------------------------------- cp
cp = DATA["competitive_programming"]
w('<h2 id="cp">Competitive programming</h2>')
w(f'<div class="warn">{e(cp["positioning_note"])}</div>')
w('<div class="stats">')
w(f'<div class="stat"><div class="v">{cp["totals"]["problems_solved"]}</div><div class="l">problems solved</div>'
  f'<div class="s">across 15 judges</div></div>')
w(f'<div class="stat"><div class="v">{cp["totals"]["contests"]}</div><div class="l">contests entered</div></div>')
w('<div class="stat"><div class="v">11th</div><div class="l">ICPC Dhaka Regional 2021</div>'
  '<div class="s">of 165 teams · Divisional Champion</div></div>')
w('<div class="stat"><div class="v">2064</div><div class="l">CodeChef peak</div>'
  '<div class="s">5-star / Yellow</div></div>')
w("</div>")
w("<h4>Primary profiles</h4><table><tr><th>Platform</th><th>Handle</th><th>Peak</th><th>Solved</th><th>Contests</th></tr>")
for p in cp["profiles"]:
    if not p.get("primary"):
        continue
    w(f'<tr><td>{e(p["platform"])}</td><td>{link(p["url"], p["handle"])}</td>'
      f'<td class="mono">{e(p.get("max_rating","—"))} {e(p.get("rank",""))}</td>'
      f'<td class="mono">{e(p.get("solved","—"))}</td><td class="mono">{e(p.get("contests","—"))}</td></tr>')
w("</table>")
w(f'<p class="meta">{e(cp["profiles_note"])}</p>')
dc = cp["divisional_champion_summary"]
w('<div class="card"><h3>Divisional Champion &times;5</h3>')
w(f'<p class="quote">{e(dc["claim"])}</p>')
w(f'<p>{e(dc["why_it_matters"])}</p><ul>')
for ev in dc["events"]:
    w(f'<li>{e(ev)}</li>')
w("</ul></div>")
w(f'<div class="warn"><b>Certificate links:</b> {e(cp["certificate_caveat"])}</div>')
for heading, key in [("ICPC record", "icpc"), ("Global contests", "global_contests"),
                     ("National contests", "national_contests")]:
    w(f"<h4>{heading}</h4><ul>")
    for x in cp[key]:
        label = f'{x.get("year","")} {x["event"]}'.strip()
        extra = f' <span class="meta">— {e(x["award"])}</span>' if x.get("award") else ""
        proof = []
        if x.get("certificate"):
            proof.append(link(x["certificate"], "certificate"))
        if x.get("official_certificate"):
            proof.append(link(x["official_certificate"], "official certificate"))
        if x.get("standings"):
            proof.append(link(x["standings"], "standings"))
        pr = f' <span class="meta">[{" · ".join(proof)}]</span>' if proof else \
             ' <span class="meta">[no proof link]</span>'
        unc = f'<br><span class="meta">⚠ {e(x["result_uncertain"])}</span>' if x.get("result_uncertain") else ""
        w(f'<li><b>{e(label)}</b> — {e(x["result"])}{extra}{pr}{unc}</li>')
    w("</ul>")
w("<h4>Awards</h4><ul>")
for a in cp["awards"]:
    w(f"<li>{e(a)}</li>")
w("</ul><h4>Problem setting</h4><ul>")
for a in cp["problem_setting"]:
    w(f"<li>{e(a)}</li>")
w("</ul>")

# ---------------------------------------------------------------- photos
ph = DATA["photos"]
w('<h2 id="photos">Photos</h2>')
w(f'<div class="warn"><b>{e(ph["status"])}</b></div>')
w(f'<p>Drop the image files here: <code>{e(ph["directory"])}</code> — any filenames are fine. '
  'Then tell me what each one shows and I will place it where it works hardest.</p>')
w("<h4>Received</h4>")
for r in ph.get("received", []):
    w(f'<div class="card"><b class="mono">{e(r["file"])}</b> '
      f'<span class="meta">· {e(r["dimensions"])} · {e(r["format"])} · slot: {e(r["slot"])}</span>'
      f'<p>{e(r["note"])}</p>'
      f'<p><img src="../assets/photos/{e(r["file"])}" alt="{e(r["file"])}" '
      f'style="max-width:260px;border-radius:8px;border:1px solid var(--line)"></p></div>')
w("<h4>Still wanted</h4><table><tr><th>Slot</th><th>What is wanted</th><th>Status</th></tr>")
for x in ph["wanted"]:
    status = f'<b>have — {e(x["satisfied_by"])}</b>' if x.get("satisfied_by") else \
             ("required" if x["required"] else "optional")
    w(f'<tr><td class="mono">{e(x["slot"])}</td><td>{e(x["need"])}</td><td>{status}</td></tr>')
w("</table>")
found = sorted(p.name for p in (ROOT / "assets" / "photos").glob("*") if p.is_file())
w(f'<p class="meta">Currently in that folder: '
  f'{("<code>" + "</code>, <code>".join(e(f) for f in found) + "</code>") if found else "nothing yet"}.</p>')

# ---------------------------------------------------------------- assets
a = DATA["assets"]
w('<h2 id="assets">Assets</h2><dl class="kv">')
w(f'<dt>CV (1 page)</dt><dd class="mono">{e(a["cv_pdf_one_page"])}</dd>')
w(f'<dt>CV (2 page)</dt><dd class="mono">{e(a["cv_pdf_two_page"])}</dd>')
w(f'<dt>CV source</dt><dd class="mono">{e(a["cv_master_tex"])}</dd>')
w(f'<dt>photo</dt><dd>{e(a["photo"])}</dd>')
w("</dl>")
w("<h4>Diagrams worth drawing</h4><ul>")
for d in a["diagram_opportunities"]:
    w(f"<li>{e(d)}</li>")
w("</ul>")

# ---------------------------------------------------------------- constraints
w('<h2 id="constraints">Constraints &amp; corrections carried forward</h2>')
for c in m["hard_constraints"]:
    w(f'<div class="warn">{e(c)}</div>')
w("<h4>Sources read</h4><ul>")
for s in m["sources"]:
    w(f'<li class="mono">{e(s)}</li>')
w("</ul>")

w("</main></div>")

OUT.write_text("\n".join(out))
print(f"wrote {OUT} ({OUT.stat().st_size:,} bytes)")
