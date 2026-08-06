#!/usr/bin/env python3
"""Build the portfolio site from data/profile.json.

    python3 build.py            # -> site/
    python3 build.py --serve    # build, then serve on :8000

No dependencies beyond the standard library, except Pillow for image derivatives
(optional - the build falls back to copying the original if Pillow is absent).

Fields in profile.json whose names encode *guidance* rather than content - _meta,
*_note, *_caveat, *_status, *_decision, attribution, publication_rule, removed_bullets,
verified, result_uncertain - are review scaffolding and are never emitted. A guard at
the end of the build fails hard if any redacted string reaches the output.
"""

import argparse
import html
import json
import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "src"
OUT = ROOT / "site"
DATA = json.loads((ROOT / "data" / "profile.json").read_text())

SITE_URL = "https://souravbiswassanto.github.io"

# --------------------------------------------------------------------------- guard
# Nothing in this list may appear anywhere in the built output. See README.
FORBIDDEN = [
    "FlowGen", "flowgenx", "Runtime Deployment",
    "Nokia", "Orange Telecom", "GreenHouse", "Coredge", "VNPAY", "SoftBank", "ace-cloud",
    "Staff Software Engineer",
    "1841-978367", "1841978367", "8801881178367",
    "open source", "open-source",
    "Jackpot", "Hangman", "Object Finder", "Boimela", "The Reviver",
]

# --------------------------------------------------------------------------- helpers


def e(x):
    return html.escape(str(x), quote=True)


def slug(case_id):
    return case_id[3:] if case_id.startswith("cs-") else case_id


ICONS = {
    "github": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 .5a12 12 0 0 0-3.79 23.4c.6.1.82-.26.82-.58v-2.2c-3.34.72-4.04-1.6-4.04-1.6-.55-1.4-1.34-1.77-1.34-1.77-1.1-.75.08-.73.08-.73 1.2.09 1.84 1.24 1.84 1.24 1.07 1.84 2.81 1.31 3.5 1 .1-.78.42-1.31.76-1.61-2.67-.3-5.47-1.34-5.47-5.96 0-1.32.47-2.4 1.24-3.24-.13-.3-.54-1.53.12-3.18 0 0 1.01-.32 3.3 1.24a11.5 11.5 0 0 1 6.01 0c2.29-1.56 3.3-1.24 3.3-1.24.66 1.65.25 2.88.12 3.18.77.84 1.23 1.92 1.23 3.24 0 4.63-2.8 5.65-5.48 5.95.43.37.81 1.1.81 2.22v3.29c0 .32.21.69.83.57A12 12 0 0 0 12 .5Z"/></svg>',
    "linkedin": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M20.45 20.45h-3.55v-5.57c0-1.33-.02-3.04-1.85-3.04-1.85 0-2.14 1.45-2.14 2.94v5.67H9.35V9h3.41v1.56h.05a3.74 3.74 0 0 1 3.37-1.85c3.6 0 4.27 2.37 4.27 5.46v6.28ZM5.34 7.43a2.06 2.06 0 1 1 0-4.12 2.06 2.06 0 0 1 0 4.12ZM7.12 20.45H3.55V9h3.57v11.45ZM22.22 0H1.77C.79 0 0 .77 0 1.72v20.56C0 23.23.79 24 1.77 24h20.45c.98 0 1.78-.77 1.78-1.72V1.72C24 .77 23.2 0 22.22 0Z"/></svg>',
    "mail": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m2 7 10 6 10-6"/></svg>',
    "doc": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z"/><path d="M14 2v6h6"/></svg>',
    "arrow": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
    "search": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>',
    "sun": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>',
    "play": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><rect x="2" y="4" width="20" height="16" rx="3"/><path d="m10 9 5 3-5 3z" fill="currentColor"/></svg>',
}


def diagram(name, caption):
    svg = (SRC / "diagrams" / f"{name}.svg").read_text()
    svg = re.sub(r"<\?xml.*?\?>\s*", "", svg)
    return (f'<figure class="diagram reveal"><div class="frame">{svg}</div>'
            f'<figcaption>{e(caption)}</figcaption></figure>')


DIAGRAM_FOR_CASE = {
    "cs-zero-data-loss": ("dc-dr", "Two tiers of cross-datacenter DR. Tier one is a remote replica promoted by hand; tier two adds a control plane that detects the loss of a whole datacenter and promotes the survivor on its own — with leadership semantics that let exactly one site win."),
    "cs-read-replica": ("read-replica", "Provisioned capacity before and after. The dashed line is what the workload actually needed; the flat line above it is what was being paid for every day of the year."),
    "cs-scale": ("shard-ring", "Clusters are hashed onto a ring and each operator replica owns the arc before its position. When a replica leaves, only its arc moves — every other cluster keeps its owner."),
}


# --------------------------------------------------------------------------- chrome


def head(title, description, canonical, extra=""):
    return f"""<!doctype html>
<html lang="en" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
<link rel="canonical" href="{e(canonical)}">
<meta property="og:type" content="website">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:url" content="{e(canonical)}">
<meta property="og:image" content="{SITE_URL}/assets/hero.jpg">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#fdfdfc" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0e1014" media="(prefers-color-scheme: dark)">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90' font-family='Georgia,serif'>S</text></svg>">
<link rel="stylesheet" href="{'../' if '/case/' in canonical else ''}styles/main.css">
<script>
(function(){{try{{var t=localStorage.getItem("theme");if(t)document.documentElement.setAttribute("data-theme",t);}}catch(e){{}}}})();
</script>
{extra}
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
"""


def site_header(prefix=""):
    return f"""<header class="site-header">
  <div class="wrap">
    <a class="brand" href="{prefix}index.html">Saurov Chandra Biswas</a>
    <nav class="site-nav" aria-label="Primary">
      <a class="nav-hide" href="{prefix}index.html#case-studies">Case studies</a>
      <a class="nav-hide" href="{prefix}index.html#work">Work</a>
      <a class="nav-hide" href="{prefix}index.html#writing">Writing</a>
      <a class="nav-hide" href="{prefix}index.html#contact">Contact</a>
      <a class="nav-keep" href="{prefix}index.html#work">Work</a>
      <a class="nav-keep" href="{prefix}index.html#contact">Contact</a>
      <button class="icon-btn" data-palette-open type="button" aria-label="Search this site">{ICONS['search']}</button>
      <span class="kbd-hint" aria-hidden="true">⌘K</span>
      <button class="icon-btn" data-theme-toggle type="button" aria-label="Switch theme">{ICONS['sun']}</button>
    </nav>
  </div>
</header>
"""


def site_footer(prefix=""):
    ident, contact = DATA["identity"], DATA["contact"]
    return f"""<footer class="site-footer">
  <div class="wrap">
    <p>© 2026 {e(ident['name'])} · Last updated August 2026 · Static site, no framework.</p>
    <nav aria-label="Footer">
      <a href="{e(contact['github'])}" rel="me noopener">GitHub</a>
      <a href="{e(contact['linkedin'])}" rel="me noopener">LinkedIn</a>
      <a href="mailto:{e(contact['email_personal'])}">Email</a>
      {f'<a href="{prefix}cv.pdf">CV</a>' if HAS_PUBLIC_CV else ''}
    </nav>
  </div>
</footer>
"""


def palette(prefix=""):
    entries = [("Home", f"{prefix}index.html", "page"),
               ("Case studies", f"{prefix}index.html#case-studies", "section"),
               ("Selected work", f"{prefix}index.html#work", "section"),
               ("Writing & talks", f"{prefix}index.html#writing", "section"),
               ("Release lifecycle", f"{prefix}index.html#releases", "section"),
               ("Experience", f"{prefix}index.html#experience", "section"),
               ("Toolkit", f"{prefix}index.html#toolkit", "section"),
               ("Education", f"{prefix}index.html#education", "section"),
               ("Contact", f"{prefix}index.html#contact", "section")]
    for c in DATA["case_studies"]:
        entries.append((c["title"], f"{prefix}case/{slug(c['id'])}.html", "case study"))
    for b in DATA["writing"]["blogs"]:
        if b.get("featured"):
            entries.append((b["title"], b["url"], "article"))
    for s in DATA["writing"]["speaking"]:
        entries.append((s["title"], s["video"], "talk"))
    if HAS_PUBLIC_CV:
        entries.append(("Download CV (PDF)", f"{prefix}cv.pdf", "file"))
    entries.append(("GitHub profile", DATA["contact"]["github"], "profile"))
    entries.append(("LinkedIn profile", DATA["contact"]["linkedin"], "profile"))

    lis = "\n".join(
        f'<li data-search="{e((t + " " + k).lower())}"><a href="{e(u)}">'
        f'<span>{e(t)}</span><span class="p-kind">{e(k)}</span></a></li>'
        for t, u, k in entries)
    return f"""<div class="palette-backdrop" data-palette hidden>
  <div class="palette" role="dialog" aria-modal="true" aria-label="Search this site">
    <input type="text" placeholder="Jump to…" aria-label="Search" autocomplete="off" spellcheck="false">
    <ul>{lis}</ul>
    <p class="p-empty" hidden>No matches.</p>
  </div>
</div>
"""


def tail(prefix=""):
    return f"{palette(prefix)}{site_footer(prefix)}<script src=\"{prefix}js/main.js\" defer></script>\n</body>\n</html>\n"


# --------------------------------------------------------------------------- home


HAS_PUBLIC_CV = (ROOT / "assets" / "cv-public.pdf").exists()

FAILOVER_CAPTION = (
    "Three Postgres pods form a Raft group. Each standby continuously receives the primary's WAL "
    "position over gRPC, so when the primary is lost the election already knows who is furthest "
    "ahead. Total time to writes resuming: 2–10 seconds."
)


def build_home():
    ident, contact, g = DATA["identity"], DATA["contact"], DATA["github_metrics"]
    FAILOVER_FIG = diagram("failover", FAILOVER_CAPTION)
    p = []
    a = p.append

    ld = {
        "@context": "https://schema.org", "@type": "Person",
        "name": ident["name"], "jobTitle": ident["title"],
        "worksFor": {"@type": "Organization", "name": ident["company"]},
        "url": SITE_URL, "image": f"{SITE_URL}/assets/hero.jpg",
        "email": f"mailto:{contact['email_personal']}",
        "address": {"@type": "PostalAddress", "addressLocality": "Dhaka", "addressCountry": "BD"},
        "sameAs": [contact["github"], contact["linkedin"]],
        "alumniOf": {"@type": "CollegeOrUniversity", "name": DATA["education"]["primary"]["institution"]},
        "knowsAbout": ["Kubernetes", "Go", "PostgreSQL", "Distributed Systems", "Site Reliability Engineering"],
    }
    a(head(f"{ident['name']} — {ident['title']}", ident["summary"], f"{SITE_URL}/",
           extra=f'<script type="application/ld+json">{json.dumps(ld)}</script>'))
    a(site_header())
    a('<main id="main">')

    # ---------------------------------------------------------------- hero
    a(f"""<section class="hero">
  <div class="wrap hero-grid">
    <div>
      <p class="role">{e(ident['title'])}</p>
      <h1>{e(ident['name'])}</h1>
      <p class="lede">{e(ident['tagline'])}</p>
      <p class="sub">I lead the KubeDB team at <a href="{e(ident['company_url'])}" rel="noopener">{e(ident['company'])}</a>,
      where I own PostgreSQL on Kubernetes — Raft-based high availability, cross-datacenter disaster recovery,
      and the Day-2 automation that keeps thousands of clusters running without anyone watching them.</p>
      <p class="meta-line">
        <span>{e(ident['location'])}</span>
        <span>Go · Kubernetes · PostgreSQL · Distributed Systems</span>
        <span>{e(ident['years_experience'])} years</span>
      </p>
      <div class="cta-row">
        <a class="btn btn--primary" href="#case-studies">Read the case studies {ICONS['arrow']}</a>
        {f'<a class="btn" href="cv.pdf">{ICONS["doc"]} CV</a>' if HAS_PUBLIC_CV else ''}
        <a class="btn" href="{e(contact['github'])}" rel="noopener">{ICONS['github']} GitHub</a>
        <a class="btn" href="{e(contact['linkedin'])}" rel="noopener">{ICONS['linkedin']} LinkedIn</a>
      </div>
    </div>
    <div class="hero-portrait">
      <picture>
        <source srcset="assets/hero.webp" type="image/webp">
        <img src="assets/hero.jpg" width="640" height="640" alt="{e(ident['name'])}" fetchpriority="high">
      </picture>
    </div>
  </div>
</section>""")

    # ---------------------------------------------------------------- stats
    tiles = []
    for s in g["headline_stats_for_site"]:
        v = s["value"]
        m = re.fullmatch(r"(\d+)(\+?)", v)
        val = (f'<span class="num" data-count="{m.group(1)}" data-suffix="{m.group(2)}">0</span>'
               if m else f'<span class="num">{e(v)}</span>')
        tiles.append(f'<div class="stat"><div class="v">{val}</div>'
                     f'<div class="l">{e(s["label"])}</div><div class="s">{e(s["sub"])}</div></div>')
    a(f"""<section class="stat-bar" aria-label="Key numbers">
  <div class="wrap"><div class="stat-grid">{''.join(tiles)}</div></div>
</section>""")

    # ---------------------------------------------------------------- signature diagram
    a(f"""<section class="section">
  <div class="wrap">
    <div class="section-head reveal">
      <p class="eyebrow">What I work on</p>
      <h2>Losing the primary should be boring</h2>
      <p>A database that fails over in seconds is not the same product as one that fails over when somebody notices.
      Most of my work is the distance between those two sentences — consensus, replication, and the Day-2 machinery
      that turns a 3 a.m. page into an event nobody was awake for.</p>
    </div>
    {FAILOVER_FIG}
  </div>
</section>""")

    # ---------------------------------------------------------------- experience
    xp = DATA["experience"][0]
    side = DATA["experience"][1]
    tl = "".join(f'<li><span class="t-when">{e(t["when"])}</span>{e(t["what"])}</li>'
                 for t in xp["progression"] if "DO NOT PRINT" not in t["what"])
    bullets = "".join(f"<li>{e(b)}</li>" for b in xp["bullets"])
    side_b = "".join(f"<li>{e(b)}</li>" for b in side["usable_content"])
    a(f"""<section class="section section--alt" id="experience">
  <div class="wrap">
    <div class="section-head reveal">
      <p class="eyebrow">Experience</p>
      <h2>Three years, two promotions, one team to lead</h2>
    </div>
    <div class="xp reveal">
      <div class="xp-side">
        <p class="when">Apr 2023 — present</p>
        <h3>{e(xp['display_title'])}</h3>
        <p class="org"><a href="{e(xp['company_url'])}" rel="noopener">{e(xp['company'])}</a> · {e(xp['location'])}</p>
        <ul class="timeline">{tl}</ul>
      </div>
      <div><ul class="bullets">{bullets}</ul></div>
    </div>
    <div class="xp reveal" style="margin-top:3rem">
      <div class="xp-side">
        <p class="when">Apr — Sep 2025</p>
        <h3>Independent engineering</h3>
        <p class="org">Remote · part-time · client confidential</p>
      </div>
      <div><ul class="bullets">{side_b}</ul></div>
    </div>
  </div>
</section>""")

    # ---------------------------------------------------------------- case studies
    cards = []
    for c in DATA["case_studies"]:
        tags = "".join(f'<span class="tag">{e(t)}</span>' for t in c["tags"])
        cards.append(f"""<a class="card card--case reveal" href="case/{slug(c['id'])}.html">
  <p class="card-meta">{e(c['tags'][0])}</p>
  <h3>{e(c['title'])}</h3>
  <p class="hook">{e(c['hook'])}</p>
  <div class="tags">{tags}</div>
  <span class="more">Read the case study <span class="arrow">→</span></span>
</a>""")
    a(f"""<section class="section" id="case-studies">
  <div class="wrap">
    <div class="section-head reveal">
      <p class="eyebrow">Case studies</p>
      <h2>Seven problems, and what it actually took</h2>
      <p>Each of these is real work with a measured outcome — the situation, why the obvious fix doesn't hold,
      the design, and how it was proven. Where something was a team effort, it says so.</p>
    </div>
    <div class="card-grid">{''.join(cards)}</div>
  </div>
</section>""")

    # ---------------------------------------------------------------- work
    cards = []
    for pr in DATA["flagship_projects"]:
        if pr["id"] == "misc-personal":
            continue
        links = " · ".join(f'<a href="{e(l["url"])}" rel="noopener">{e(l["label"])}</a>' for l in pr.get("links", []))
        org = pr.get("org") or "Independent"
        tags = "".join(f'<span class="tag">{e(t)}</span>' for t in pr.get("stack", [])[:5])
        cards.append(f"""<div class="card reveal">
  <p class="card-meta">{e(org)} · {e(pr['period'])}</p>
  <h3>{e(pr['name'])}</h3>
  <p>{e(pr['summary'])}</p>
  <div class="tags">{tags}</div>
  {f'<span class="more">{links}</span>' if links else ''}
</div>""")
    misc = next(x for x in DATA["flagship_projects"] if x["id"] == "misc-personal")
    misc_links = " · ".join(f'<a href="{e(l["url"])}" rel="noopener">{e(l["label"])}</a>' for l in misc["links"])
    a(f"""<section class="section section--alt" id="work">
  <div class="wrap">
    <div class="section-head reveal">
      <p class="eyebrow">Selected work</p>
      <h2>Systems I own or built</h2>
    </div>
    <div class="card-grid">{''.join(cards)}</div>
    <p class="reveal" style="margin-top:1.6rem;color:var(--muted);font-size:var(--step--1)">
      Smaller personal builds: {misc_links}.
    </p>
  </div>
</section>""")

    # ---------------------------------------------------------------- writing
    feat = [b for b in DATA["writing"]["blogs"] if b.get("featured")]
    rows = "".join(f"""<li><a href="{e(b['url'])}" rel="noopener">
  <span class="w-date">{e(b['date'])}</span>
  <span class="w-title">{e(b['title'])}</span>
  <span class="w-arrow">→</span></a></li>""" for b in feat)
    talks = "".join(f"""<li><a href="{e(s['video'])}" rel="noopener">
  <span class="w-date">{e(s['date'])}</span>
  <span class="w-title">{e(s['title'])}<small>Webinar · {e(s['channel'])}</small></span>
  <span class="w-arrow">→</span></a></li>""" for s in DATA["writing"]["speaking"])
    docs = "".join(f"<li>{e(d)}</li>" for d in DATA["writing"]["docs"])
    a(f"""<section class="section" id="writing">
  <div class="wrap">
    <div class="section-head reveal">
      <p class="eyebrow">Writing &amp; talks</p>
      <h2>Published under my own name</h2>
      <p>Four engineering deep-dives, two conference-style webinars, and the PostgreSQL documentation for KubeDB —
      roughly 2,300 lines of it across the disaster-recovery and migration guides alone, every procedure validated
      live on real clusters before it was written down.</p>
    </div>
    <ul class="writing-list reveal">{rows}</ul>
    <h3 style="margin:2.5rem 0 1rem" class="reveal">Talks</h3>
    <ul class="writing-list reveal">{talks}</ul>
    <details class="disclosure reveal" style="margin-top:2rem">
      <summary>Documentation authored for kubedb.com</summary>
      <ul class="bullets" style="padding-bottom:1.5rem">{docs}</ul>
    </details>
  </div>
</section>""")

    # ---------------------------------------------------------------- releases
    rl = DATA["release_lifecycle"]
    rrows = "".join(f"""<tr><td class="n">{e(r['version'])}</td><td class="n">{e(r['date'])}</td>
      <td><a href="{e(r['blog'])}" rel="noopener">Announcement</a></td></tr>""" for r in rl["releases"])
    sup = "".join(f"<li>{e(s)}</li>" for s in rl["supporting_work"])
    a(f"""<section class="section section--alt" id="releases">
  <div class="wrap">
    <div class="section-head reveal">
      <p class="eyebrow">Release lifecycle</p>
      <h2>Nine releases, shipped end to end</h2>
      <p>{e(rl['summary'])}</p>
    </div>
    <div class="table-wrap reveal">
      <table class="data"><thead><tr><th>Release</th><th>Date</th><th>Wrote the announcement</th></tr></thead>
      <tbody>{rrows}</tbody></table>
    </div>
    <ul class="bullets reveal" style="margin-top:1.8rem">{sup}</ul>
  </div>
</section>""")

    # ---------------------------------------------------------------- toolkit
    labels = {
        "languages": "Languages", "kubernetes": "Kubernetes", "databases": "Databases",
        "distributed_systems": "Distributed systems", "cloud_devops": "Cloud &amp; DevOps",
        "observability": "Observability", "protocols_security": "Protocols &amp; security",
        "practices": "Practices",
    }
    groups = "".join(f'<div><h3>{labels.get(k, k)}</h3><p>{e(" · ".join(v))}</p></div>'
                     for k, v in DATA["skills"].items())
    a(f"""<section class="section" id="toolkit">
  <div class="wrap">
    <div class="section-head reveal">
      <p class="eyebrow">Toolkit</p>
      <h2>What I reach for</h2>
    </div>
    <div class="toolkit reveal">{groups}</div>
  </div>
</section>""")

    # ---------------------------------------------------------------- education
    ed = DATA["education"]
    pri = ed["primary"]
    cert = DATA["certifications"][0]
    earlier = "".join(f"""<tr><td>{e(x['level'])}</td><td>{e(x['institution'])}</td>
      <td class="n">{e(x['result'] or '—')}</td><td>{e(x['distinction'] or '—')}</td></tr>"""
                      for x in ed["earlier"])
    a(f"""<section class="section section--alt" id="education">
  <div class="wrap">
    <div class="section-head reveal">
      <p class="eyebrow">Education</p>
      <h2>Where it started</h2>
    </div>
    <div class="rows reveal">
      <div class="row">
        <span class="when">{e(pri['start'][:4])} — {e(pri['end'][:4])}</span>
        <span class="what"><strong>{e(pri['degree'])}</strong>
          <small>{e(pri['institution'])}, {e(pri['location'])} · CGPA {e(pri['cgpa'])}</small></span>
        <span class="aside">{e(', '.join(pri['coursework'][:4]))}…</span>
      </div>
      <div class="row">
        <span class="when">2025</span>
        <span class="what"><strong>English — {e(cert['level'])}</strong>
          <small>{e(cert['issuer'])} · awarded {e(cert['awarded'])}</small></span>
        <span class="aside"><a href="{e(cert['url'])}" rel="noopener">Certificate</a></span>
      </div>
      <div class="row">
        <span class="when">2022 — 2023</span>
        <span class="what"><strong>President, Programming Club — CSE, University of Barishal</strong>
          <small>{e(ed['leadership']['detail'])}</small></span>
      </div>
    </div>
    <details class="disclosure reveal" style="margin-top:1.8rem">
      <summary>Full academic record</summary>
      <div class="table-wrap" style="padding-bottom:1.5rem">
        <table class="data"><thead><tr><th>Level</th><th>Institution</th><th>Result</th><th>Distinction</th></tr></thead>
        <tbody>{earlier}</tbody></table>
      </div>
    </details>
  </div>
</section>""")

    # ---------------------------------------------------------------- CP
    cp = DATA["competitive_programming"]
    dc = cp["divisional_champion_summary"]
    profiles = "".join(
        f'<a class="btn" href="{e(pf["url"])}" rel="noopener">{e(pf["platform"])} '
        f'<span class="num" style="color:var(--muted)">{e(pf.get("max_rating", ""))}</span></a>'
        for pf in cp["profiles"] if pf.get("primary"))
    champs = "".join(f"<li>{e(x)}</li>" for x in dc["events"])
    a(f"""<section class="section" id="before">
  <div class="wrap">
    <div class="section-head reveal">
      <p class="eyebrow">Before infrastructure</p>
      <h2>Five years of competitive programming</h2>
      <p>Where the instinct for algorithms and for debugging under time pressure came from.
      {cp['totals']['problems_solved']:,} problems solved across {cp['totals']['contests']} contests.</p>
    </div>
    <div class="result reveal">
      <div><div class="v">×5</div><div class="l">Divisional Champion, Barishal Division</div></div>
      <div><div class="v">11th</div><div class="l">ICPC Dhaka Regional 2021, of 165 teams</div></div>
      <div><div class="v">2,950</div><div class="l">problems solved across 15 judges</div></div>
      <div><div class="v">2064</div><div class="l">CodeChef peak — 5-star</div></div>
    </div>
    <p class="pull reveal">{e(dc['claim'])}</p>
    <ul class="bullets reveal">{champs}</ul>
    <div class="cta-row reveal">{profiles}</div>
  </div>
</section>""")

    # ---------------------------------------------------------------- contact
    a(f"""<section class="section section--alt" id="contact">
  <div class="wrap contact-grid">
    <div class="reveal">
      <p class="eyebrow">Contact</p>
      <h2>Let's talk</h2>
      <p style="color:var(--fg-soft);margin-top:1rem;max-width:46ch">
        I'm interested in hard problems in distributed systems, databases, and the platforms that run them.
        Email is the fastest way to reach me.
      </p>
    </div>
    <ul class="contact-list reveal">
      <li><a href="mailto:{e(contact['email_personal'])}">{ICONS['mail']}<span class="c-label">Email</span>{e(contact['email_personal'])}</a></li>
      <li><a href="{e(contact['github'])}" rel="me noopener">{ICONS['github']}<span class="c-label">GitHub</span>souravbiswassanto</a></li>
      <li><a href="{e(contact['linkedin'])}" rel="me noopener">{ICONS['linkedin']}<span class="c-label">LinkedIn</span>sourav-biswas-santo</a></li>
      {f'<li><a href="cv.pdf">{ICONS["doc"]}<span class="c-label">CV</span>Download PDF</a></li>' if HAS_PUBLIC_CV else f'<li><a href="mailto:{e(contact["email_personal"])}?subject=CV%20request">{ICONS["doc"]}<span class="c-label">CV</span>Available on request</a></li>'}
    </ul>
  </div>
</section>""")

    a("</main>")
    a(tail())
    return "\n".join(p)


# --------------------------------------------------------------------------- case pages


def build_case(case, prev_case, next_case):
    ident = DATA["identity"]
    sl = slug(case["id"])
    url = f"{SITE_URL}/case/{sl}.html"
    body = "".join(f"<p>{e(par)}</p>" for par in case["body"])
    tags = "".join(f'<span class="tag">{e(t)}</span>' for t in case["tags"])

    fig = ""
    if case["id"] in DIAGRAM_FOR_CASE:
        name, cap = DIAGRAM_FOR_CASE[case["id"]]
        fig = diagram(name, cap)

    team = ""
    if case.get("attribution"):
        team = ('<div class="callout"><b>This was a team effort.</b> The response was run together with our CEO '
                'and senior engineers. What follows is my part of it.</div>')

    writing = ""
    if case.get("related_writing"):
        items = "".join(
            f'<li><a href="{e(w["url"])}" rel="noopener">'
            f'<span class="w-date">{e(w["date"])}</span>'
            f'<span class="w-title">{e(w["title"])}<small>{e(w["role"])}</small></span>'
            f'<span class="w-arrow">→</span></a></li>' for w in case["related_writing"])
        writing = f'<h2>Published alongside this</h2><ul class="writing-list">{items}</ul>'

    nav = []
    for label, other in (("Previous", prev_case), ("Next", next_case)):
        if other:
            nav.append(f'<a class="card" href="{slug(other["id"])}.html">'
                       f'<p class="card-meta">{label}</p><h3>{e(other["title"])}</h3></a>')

    p = [head(f"{case['title']} — {ident['name']}", case["hook"], url),
         site_header("../"),
         '<main id="main">',
         f"""<section class="case-hero">
  <div class="wrap">
    <a class="back-link" href="../index.html#case-studies">← All case studies</a>
    <p class="eyebrow">Case study</p>
    <h1>{e(case['title'])}</h1>
    <p class="hook">{e(case['hook'])}</p>
    <div class="tags" style="margin-top:1.4rem">{tags}</div>
  </div>
</section>""",
         f"""<section class="case-body">
  <div class="wrap">
    <div class="prose">{team}{body}</div>
    {fig}
    <div class="prose">
      <h2>Evidence</h2>
      <p style="color:var(--muted);font-size:var(--step--1)">{e(case['evidence'])}</p>
      {writing}
    </div>
    <div class="case-nav">{''.join(nav)}</div>
  </div>
</section>""",
         "</main>", tail("../")]
    return "\n".join(p)


# --------------------------------------------------------------------------- assets


def copy_assets():
    (OUT / "styles").mkdir(parents=True, exist_ok=True)
    (OUT / "js").mkdir(parents=True, exist_ok=True)
    (OUT / "assets").mkdir(parents=True, exist_ok=True)
    shutil.copy2(SRC / "styles" / "main.css", OUT / "styles" / "main.css")
    shutil.copy2(SRC / "js" / "main.js", OUT / "js" / "main.js")

    src_photo = ROOT / "assets" / "photos" / "hero.jpg"
    if src_photo.exists():
        try:
            from PIL import Image
            im = Image.open(src_photo).convert("RGB")
            # Tighter than a plain square crop — brings the face up to headshot scale.
            side = int(min(im.size) * 0.84)
            left = (im.width - side) // 2
            top = int(im.height * 0.045)
            im = im.crop((left, top, left + side, top + side)).resize((640, 640), Image.LANCZOS)
            im.save(OUT / "assets" / "hero.jpg", "JPEG", quality=82, optimize=True, progressive=True)
            im.save(OUT / "assets" / "hero.webp", "WEBP", quality=80, method=6)
        except ImportError:
            shutil.copy2(src_photo, OUT / "assets" / "hero.jpg")

    # The CV in cv/ names the redacted employer and the customers, so it is NEVER published.
    # Only a purpose-built public CV placed at assets/cv-public.pdf is shipped, and the guard
    # below reads its text to prove it is clean before it goes out.
    public_cv = ROOT / "assets" / "cv-public.pdf"
    if public_cv.exists():
        shutil.copy2(public_cv, OUT / "cv.pdf")

    (OUT / ".nojekyll").write_text("")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")

    urls = [f"{SITE_URL}/"] + [f"{SITE_URL}/case/{slug(c['id'])}.html" for c in DATA["case_studies"]]
    entries = "".join(f"<url><loc>{u}</loc><changefreq>monthly</changefreq></url>" for u in urls)
    (OUT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{entries}</urlset>\n')


# --------------------------------------------------------------------------- guard


def pdf_text(path):
    """Crude but sufficient text extraction — enough to catch a redaction leak."""
    import zlib
    raw = path.read_bytes()
    chunks = []
    for m in re.finditer(rb"stream\r?\n(.*?)endstream", raw, re.S):
        try:
            chunks.append(b" ".join(re.findall(rb"\((.*?)\)", zlib.decompress(m.group(1)))))
        except Exception:
            continue
    return b" ".join(chunks).decode("latin1", errors="ignore")


def guard():
    """Fail the build if anything redacted reached the output.

    Scans PDFs as well as markup: the CV in cv/ names the redacted employer and the
    customers, so a stray copy of it would leak exactly what the site withholds.
    """
    problems = []
    for f in OUT.rglob("*"):
        if not f.is_file():
            continue
        if f.suffix == ".pdf":
            text = pdf_text(f)
        elif f.suffix in {".html", ".css", ".js", ".xml", ".txt", ".json", ".svg"}:
            text = f.read_text(errors="ignore")
        else:
            continue
        low = re.sub(r"\s+", " ", text).lower()
        # PDF text extraction splits words on kerning ("Orange T elecom"), and HTML can carry
        # tags mid-phrase, so also test a form with all whitespace and markup removed.
        squashed = re.sub(r"[^a-z0-9]", "", low)
        for bad in FORBIDDEN:
            b = bad.lower()
            if b in low or re.sub(r"[^a-z0-9]", "", b) in squashed:
                problems.append(f"{f.relative_to(OUT)}: contains {bad!r}")
    if problems:
        print("\nBUILD FAILED — redacted content reached the output:", file=sys.stderr)
        for x in problems:
            print("  " + x, file=sys.stderr)
        sys.exit(1)


# --------------------------------------------------------------------------- main


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--serve", action="store_true")
    ap.add_argument("--port", type=int, default=8000)
    args = ap.parse_args()

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    (OUT / "case").mkdir()

    (OUT / "index.html").write_text(build_home())

    cases = DATA["case_studies"]
    for i, c in enumerate(cases):
        prev_c = cases[i - 1] if i else None
        next_c = cases[i + 1] if i + 1 < len(cases) else None
        (OUT / "case" / f"{slug(c['id'])}.html").write_text(build_case(c, prev_c, next_c))

    copy_assets()
    guard()

    total = sum(f.stat().st_size for f in OUT.rglob("*") if f.is_file())
    pages = len(list(OUT.rglob("*.html")))
    print(f"built {pages} pages into {OUT}  ({total/1024:.0f} KB total)")
    for f in sorted(OUT.rglob("*")):
        if f.is_file():
            print(f"  {f.relative_to(OUT)!s:34} {f.stat().st_size/1024:7.1f} KB")

    if args.serve:
        import functools, http.server, socketserver
        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(OUT))
        with socketserver.TCPServer(("127.0.0.1", args.port), handler) as httpd:
            print(f"\nserving http://127.0.0.1:{args.port}/  (ctrl-c to stop)")
            httpd.serve_forever()


if __name__ == "__main__":
    main()
