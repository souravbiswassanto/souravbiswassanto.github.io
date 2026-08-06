# Portfolio — plan

Status: **data collection complete, nothing built yet.** This document is the proposal; `data/profile.json`
is the collected source of truth; `review/index.html` is a plain page for reviewing what was collected.

---

## 1. What this site has to do

You are not a junior looking for a first job, and you are not a designer. The portfolio has one job:
**make a hiring manager at an infrastructure/database company believe within 20 seconds that you operate at
senior/staff level on distributed systems, then give them the evidence to confirm it.**

That means the site must lead with *proof*, not adjectives. You have unusually strong proof:

- 733 PRs authored / 542 reviewed — a verifiable, auditable output record
- Real numbers on real systems: 2–10 s failover, 37–43 s migration write gap, 5 TB / 15 replicas,
  2000+ clusters on one control plane, 16+ chaos experiments
- Published writing under your own name, including a chaos-engineering deep-dive
- Named enterprise customers (Nokia, Orange) — pending your permission to name them
- An ICPC/CodeChef record that explains where the algorithmic instinct came from

The failure mode to avoid: a wall of technologies. Every portfolio in this space lists Go, Kubernetes,
Docker, Terraform. Almost none can say "we deleted the primary with its PVCs and the other continent still
had every byte." Lead with that.

## 2. Information architecture

Single page, deep-linkable sections, plus a small number of case-study sub-pages.

```
/                       Home (one long page)
├─ Hero                 Name · "Senior Software Engineer, KubeDB Team Lead" · one-line positioning
│                       Primary CTA: Read the case studies · Secondary: CV (PDF) · GitHub · LinkedIn
├─ Proof bar            6 stat tiles: 733 PRs · 542 reviews · 12 engineers · 9 releases · 2–10s failover · 2000+ clusters
├─ Now                  3–4 sentences: what you own today and at what scale
├─ Case studies         5 cards → each opens a sub-page (this is the centrepiece, see §3)
├─ Selected work        6 project cards: KubeDB PostgreSQL · PetSet · DC-DR control plane ·
│                       Shard Manager · Oracle operator · Path-Pulse IoT
├─ Writing              4 featured deep-dives + collapsed list of 9 release posts + docs authored
├─ Experience           Appscode timeline with progression; unnamed side engineering as one dateless entry
├─ Toolkit              Grouped skills, no bars/percentages (they read as junior)
├─ Before infrastructure  Compact competitive-programming block: 2950 problems, ICPC 11th/165, 4 profile links
└─ Contact              Email · LinkedIn · GitHub · CV download

/case/zero-data-loss    Proving zero data loss by destroying the primary
/case/read-replica      5 TB, 15 replicas, and the cost of always being ready
/case/failover          Raft failover in 2–10 seconds
/case/sharding          One control plane, 2000+ clusters
/case/supply-chain      A CI workflow deleted GitHub orgs — then we hardened everything
```

Two more case studies are already written up in `data/profile.json` (migration with a 37 s write gap,
AI-assisted feature parity across 25+ engines) — hold them as page 2 rather than crowding the first five.

## 3. Case studies are the differentiator

Each case-study page follows the same five-beat structure, because it is the structure that survives a
skim:

1. **The situation** — one paragraph, concrete, with the number that made it a problem
2. **Why the obvious fix doesn't work** — this is where senior signal lives
3. **The design** — a diagram plus 3–5 sentences
4. **How it was proven** — the measurement, the chaos experiment, the destroyed primary
5. **What it cost / what it saved** — the honest outcome, including limits

Five hand-drawn SVG diagrams are planned (listed under `assets.diagram_opportunities` in profile.json).
These are what get a portfolio shared around. They must be original, in-theme, and legible in both light
and dark — no stock cloud icons.

## 4. Design direction

Restrained, typographic, fast. The content is dense and technical; the design should get out of its way.

- **Type-led**: one strong display face for headings (e.g. a grotesque), one highly legible mono for code
  and stats. No decorative fonts.
- **Colour**: near-monochrome base with a single accent used for links, stat values, and diagram highlights.
  Full dark/light support, respecting `prefers-color-scheme` with a manual toggle.
- **Motion**: almost none. A subtle reveal on scroll at most. No parallax, no particles, no typing effect —
  those read as junior in this audience.
- **Performance budget**: < 150 KB total, no web-font FOUT, Lighthouse 100/100/100/100. A slow portfolio
  from an infrastructure engineer is self-refuting.
- **Accessible**: real semantic HTML, keyboard navigable, WCAG AA contrast in both themes, works with JS off.

## 5. Tech stack

**Recommendation: hand-written static HTML/CSS + a tiny Python build step that renders `data/profile.json`
into the pages.** No framework.

Why not Astro/Next/Hugo: you would be adding a toolchain, a lockfile and a dependency-update burden to
produce eight static pages. A build script you fully control is a better story on an infrastructure
engineer's own site, and it means the content lives in one JSON file that stays easy to update.

```
portfolio/
├─ data/profile.json         # single source of truth (already written)
├─ src/templates/*.html      # page templates
├─ src/styles/main.css
├─ src/assets/               # diagrams (SVG), headshot, CV pdf
├─ build.py                  # profile.json + templates → site/
├─ site/                     # build output — this is what GitHub Pages serves
└─ .github/workflows/deploy.yml
```

If you would rather not have a build step at all, the fallback is plain hand-maintained HTML — simpler, but
then a number that changes (PR count) has to be edited in several places.

## 6. Deployment on GitHub

**Recommended: a user site at `https://souravbiswassanto.github.io`.**

That URL is short, memorable, and immediately reads as "this is the person's own site" — better on a CV
than a `/portfolio` subpath.

1. Create a new public repo named exactly `souravbiswassanto.github.io`.
2. Push this folder's contents to `main`.
3. Settings → Pages → Source: **GitHub Actions**.
4. Add `.github/workflows/deploy.yml` — runs `build.py`, uploads `site/` as a Pages artifact, deploys.
   Pin every action to a commit SHA and give the job `permissions: {contents: read, pages: write,
   id-token: write}` — the same hardening you rolled out at work, applied to your own site.
5. Optional custom domain later (e.g. `saurov.dev`): add a `CNAME` file, point an ALIAS/A record at
   GitHub's IPs, enable "Enforce HTTPS".

Note: your profile README repo is `souravbiswassanto/souravbiswassanto` — a *different* repo from
`souravbiswassanto.github.io`. Creating the site repo will not disturb your profile README.

**Alternative** if you would rather keep it as a project repo: name it `portfolio`, serve from
GitHub Actions the same way, URL becomes `souravbiswassanto.github.io/portfolio`. Everything else is
identical. Slightly worse URL, no other downside.

Once live, link it from: GitHub profile README, GitHub profile "Website" field (currently empty),
LinkedIn, and the CV header.

## 7. Editorial decisions taken

| Decision | Rationale |
|---|---|
| Title shown as "Senior Software Engineer, KubeDB Team Lead" | Never print "Staff" — at 3y4m it reads as title inflation and discounts everything else. "Team Lead" is scope, defensible with 542 reviews and 12 reports. |
| Second part-time role is **unnamed** — no company, no job title | Your explicit instruction. Its technical content appears as unattributed independent engineering work. |
| Legacy C++/Java projects dropped | Jackpot, Hangman, Object Finder, Boimela, the BU migration tool, "The Reviver". Your instruction, and correct — they would drag a staff-level profile down. |
| Competitive programming kept, but compact and near the bottom | It is genuinely differentiating (2950 problems, ICPC 11th/165) but it is your past, not your pitch. One section, four links, no table of 30 alt accounts. |
| Release blogs live in a Release lifecycle section, deep-dives attach to the work they describe | Your instruction. A blog next to the thing it documents is evidence; a flat list of 13 links is a bibliography. |
| CI supply-chain work framed as a team effort | Your correction — it was run with the CEO and senior engineers. Framed as "my part of it", which is both accurate and stronger than an overclaim someone could puncture in an interview. |
| School results (HSC/SSC/JSC/PSC) included but collapsed on the public site | Your instruction to include them. Normal on a Bangladeshi CV; unusual enough on a senior engineer's public page in Western markets that I'd put the degree up front and the rest behind a "full academic record" toggle. Your call to overrule. |
| KubeDB repos never called "open source" | Public on GitHub, not all OSI-licensed. Say "repositories in the KubeDB / KubeOps / KubeVault projects". |
| No upstream-OSS claims | Verified false: `buraksezer/consistent#28` and the Oracle upstream PR were both closed, not merged. |
| Vague percentage claims from the 2024 CV dropped | "99.999% availability", "99% reduction in outages", "90% fewer interventions" are unbacked. You now have better, citable numbers. Do not put the old ones on a public page. |
| No skill percentage bars | Reads as junior, and "Go 85%" means nothing to a hiring manager. |

## 8. Open questions

See `GAPS.md` — six items, two of which block publishing (customer naming, headshot).
