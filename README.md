# Ora public website

Static public website for Ora at `oracoach.app`.

This repository contains only the public marketing and support website used for
GitHub Pages, TestFlight, and App Store Connect support/privacy URLs. Do not add
private app source code, backend functions, backend code, credentials,
environment files, internal notes, Flutter build output, or private business
documents.

## Site shape

- `/` - Ora marketing homepage copied from the main repo's public `web_seo/` bundle.
- `/privacy/` - public privacy policy.
- `/support/` - beta support page.
- SEO routes: `/workout-tracker/`, `/nutrition-tracker/`, `/progress-tracker/`,
  `/reports/`, `/coach-console/`, `/ai-fitness-coach/`, `/biomechanics-lab/`,
  `/local-first-fitness-app/`, and `/mobile-check/`.
- `/robots.txt` and `/sitemap.xml`.

## Build and package manager

There is no framework, package manager, install step, or build command in this
repository. The site is plain static HTML/CSS/JS and public image assets.

The beta form is static: it opens a prefilled email to
`support@oracoach.app` instead of posting to a private backend.

## GitHub Pages deployment

1. Open the repository on GitHub.
2. Go to **Settings** -> **Pages**.
3. Set **Source** to **Deploy from a branch**.
4. Set the branch to `codex/static-website` and the folder to `/ (root)`.
5. Confirm the custom domain is `oracoach.app`.
6. Keep **Enforce HTTPS** enabled after GitHub provisions the certificate.

The included `CNAME` file must contain exactly:

```text
oracoach.app
```

## Local preview

Run a static server from the repository root:

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000/`.

## Verification checklist

- `git diff --check`
- Confirm `CNAME` contains exactly `oracoach.app`.
- Confirm `/`, `/privacy/`, `/support/`, `/robots.txt`, `/sitemap.xml`, and SEO
  routes return HTTP 200 from a local static server.
- Confirm no private app code, backend functions, credentials, environment files,
  or backend config are present.
- Confirm `https://oracoach.app/`, `https://oracoach.app/privacy/`, and
  `https://oracoach.app/support/` load over HTTPS after deployment.
