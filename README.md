# Ora public website

Static public website for Ora at `oracoach.app`.

This repository is intended only for public website files used by GitHub Pages,
TestFlight, and App Store Connect support/privacy URLs. Do not add app source
code, backend code, API keys, secrets, environment files, private notes, or
internal business documents.

## Pages

- `/` - public homepage
- `/privacy/` - starter beta privacy policy
- `/support/` - beta support page

## GitHub Pages deployment

1. Open the repository on GitHub.
2. Go to **Settings** -> **Pages**.
3. Under **Build and deployment**, set **Source** to **Deploy from a branch**.
4. Set **Branch** to `main` and folder to `/ (root)`.
5. Save the settings.
6. In **Custom domain**, enter `oracoach.app`.
7. Keep **Enforce HTTPS** enabled once GitHub finishes provisioning the
   certificate.

The included `CNAME` file should contain exactly:

```text
oracoach.app
```

## Namecheap DNS records

Add these records manually in Namecheap DNS for the `oracoach.app` domain:

```text
Type   Host   Value              TTL
A      @      185.199.108.153    Automatic
A      @      185.199.109.153    Automatic
A      @      185.199.110.153    Automatic
A      @      185.199.111.153    Automatic
CNAME  www    ora-sps.github.io  Automatic
```

## Confirm HTTPS

After DNS and GitHub Pages are configured:

1. Wait for DNS propagation and certificate provisioning.
2. Open `https://oracoach.app/`.
3. Confirm the browser shows a valid HTTPS connection.
4. Open `https://oracoach.app/privacy/` and `https://oracoach.app/support/`.
5. Confirm GitHub Pages has **Enforce HTTPS** checked in repository settings.

## App Store Connect URL checklist

Before using the URLs in App Store Connect:

1. Review the starter beta privacy policy with counsel or the responsible
   product owner before public App Store launch.
2. Confirm `https://oracoach.app/privacy/` loads over HTTPS.
3. Confirm `https://oracoach.app/support/` loads over HTTPS.
4. Confirm `support@oracoach.app` is active and monitored.
5. Confirm GitHub Pages is serving the latest `main` branch.

## Local preview

Because the site is plain static HTML/CSS, it can be previewed with any local
static server:

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000/`.
