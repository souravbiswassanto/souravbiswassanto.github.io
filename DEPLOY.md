# Deploying to GitHub Pages

The site is built to `site/` and served as static files. Nothing runs at request time.

## Local

```bash
python3 build.py            # -> site/
python3 build.py --serve    # build, then serve on http://127.0.0.1:8000
```

`build.py` fails the build if any redacted string reaches the output — including inside PDFs. That check
is the last thing it does, so a failed build means nothing was written you'd regret publishing.

## One-time setup

1. **Create the repo.** Public, named exactly `souravbiswassanto.github.io`. That name makes the URL
   `https://souravbiswassanto.github.io` — short, and it reads as your own site rather than a project.
   This is a *different* repo from `souravbiswassanto/souravbiswassanto`, which holds your profile README;
   creating it won't disturb that.

2. **Push.**
   ```bash
   cd /home/saurov/sourav/portfolio
   git init -b main
   git add .
   git commit -s -m "Add portfolio site"
   git remote add origin git@github.com:souravbiswassanto/souravbiswassanto.github.io.git
   git push -u origin main
   ```

3. **Turn on Pages.** Repo → Settings → Pages → Source: **GitHub Actions**. Not "Deploy from a branch" —
   the workflow needs the Actions source.

4. **Watch the first run** under the Actions tab. It builds, re-runs the redaction guard independently, and
   deploys. About a minute.

After that, every push to `main` redeploys. To change content, edit `data/profile.json` and push — you
should rarely need to touch HTML.

## What's in the workflow

`.github/workflows/deploy.yml` mirrors the hardening you rolled out at work:

- every action pinned to a **commit SHA**, not a tag — a tag can be moved, a SHA cannot
- explicit **least-privilege `permissions:`** — `contents: read`, `pages: write`, `id-token: write`
- `concurrency: pages` with `cancel-in-progress: false`, so a deploy in flight finishes rather than being
  killed halfway
- the **redaction guard runs a second time** as its own step, independent of the builder, so a regression
  in `build.py` cannot quietly publish something it shouldn't

## Custom domain (optional, later)

1. Buy the domain.
2. Add a `CNAME` file at the repo root containing just the hostname.
3. DNS: `ALIAS`/`ANAME` at the apex to `souravbiswassanto.github.io`, or four `A` records to GitHub's
   Pages IPs; `CNAME` for `www`.
4. Settings → Pages → Custom domain, then tick **Enforce HTTPS** once the certificate is issued.
5. Update `SITE_URL` in `build.py` so canonical URLs, Open Graph tags and the sitemap follow.

## After it's live

Link it from your GitHub profile README, the **Website** field on your GitHub profile (currently empty),
LinkedIn, and your CV header.

## Unpublishing

Settings → Pages → remove the source, or make the repo private. The site goes down immediately; search
engines take longer to drop it.
