# Portfolio

Static site for Saurov Chandra Biswas. Hand-written HTML/CSS/JS generated from one JSON file.
No framework, no dependencies at runtime, ~120 KB per page.

| Path | What it is |
|---|---|
| `data/profile.json` | **Source of truth.** All content. Edit here, rebuild, push. |
| `build.py` | Renders `data/` + `src/` into `site/`. Fails the build if redacted content leaks. |
| `src/styles/main.css` | The design system — tokens at the top, everything derives from them. |
| `src/js/main.js` | Theme toggle, scroll reveal, stat counters, ⌘K palette. All progressive enhancement. |
| `src/diagrams/*.svg` | Four hand-drawn, theme-aware diagrams. |
| `site/` | Build output. This is what GitHub Pages serves. Not edited by hand. |
| `DEPLOY.md` | GitHub Pages setup, workflow hardening, custom domain. |
| `PLAN.md` | Information architecture, design direction, editorial decisions. |
| `GAPS.md` | Open questions. |
| `review/index.html` | Plain data-review page (the fact-checking sheet, not the portfolio). |
| `build-review.py` | Regenerates `review/index.html`. |

```bash
python3 build.py --serve     # build + preview on :8000
python3 build-review.py      # regenerate the fact-check sheet
```

## Where the data came from

`cv/main.tex` and both archived CV versions · `cv/achievements.md` (the ledger) · the three legacy
2021–2023 CVs supplied in chat · live GitHub API queries via `gh` (PR counts, per-repo and per-year
breakdowns, blog and docs PR titles) · the Codeforces API · `Problem-Solving-Stats` · and local working
dirs (`webinar/`, `kubevault/`, `large-scale-test/`, `coredge.md`).

Every headline number was re-verified against the GitHub API on 2026-08-06 rather than copied from the CV.

## Standing constraints

- **The second, part-time role is never named** — not the company, not the job title, not a link to their
  site. Its technical content is used unattributed, as independent engineering work. Enforced across all
  files here; verify with `grep -ri` before any publish.
- **Never print "Staff Software Engineer."** The site says "Senior Software Engineer, KubeDB Team Lead".
- **Never call the KubeDB/KubeOps/KubeVault repos "open source"** — public, but not all OSI-licensed.
- **No upstream open-source claims** — the two candidate PRs were closed, not merged.
- **No customer names, anywhere.** Nokia, Orange Telecom, GreenHouse, Coredge, VNPAY, SoftBank, ace-cloud —
  none of them. Customers are described by sector and geography. The names survive in `profile.json` *only*
  inside the do-not-publish rule that forbids them.
- **No phone number** on the public site (`contact.phone_publish: false`).
- Legacy student projects (Jackpot, Hangman, Object Finder, Boimela, The Reviver) are deliberately excluded.

- **The CV in `cv/` is never published.** Its PDF names the redacted employer, the job title, the customers
  and the phone number. Only a purpose-built clean CV placed at `assets/cv-public.pdf` is shipped; when it
  is absent, the CV links disappear and the contact row says "available on request". The guard reads PDF
  text — including whitespace-kerned text like `Orange T elecom` — so a stray copy fails the build.

**Build rule for the real site:** fields whose names encode guidance rather than content — `_meta`,
`*_note`, `*_caveat`, `*_status`, `*_decision`, `naming_decision`, `attribution`, `publication_rule`,
`removed_bullets`, `display_note`, `verified`, `result_uncertain` — are review scaffolding. The site
generator must never emit them. They exist so the constraints travel with the data.
