# Gig Factory Handoff / Resume

Generated: 2026-06-27T03:27:58.512853+00:00

## Current handoff summary
Dedicated visible Chrome CDP browser is configured and verified at http://127.0.0.1:9222 using the separate profile C:/Users/Ryan/AppData/Local/hermes/browser-profiles/cdp-chrome. GitHub is signed in and shows the dashboard; Vercel is signed in and shows the New Project page. Fresh Hermes browser use was verified by a separate hermes -z browser session reaching Example Domain through the same CDP browser. The gig-factory continuity DB and DB-first project instructions are in place; future sessions must read SQLite first before broad file reads. Git repo still has no commits and no remote configured.

## Browser state
- Required browser mode: visible local Chrome via CDP
- CDP endpoint: `http://127.0.0.1:9222`
- Dedicated Chrome profile: `C:/Users/Ryan/AppData/Local/hermes/browser-profiles/cdp-chrome`
- Browser launcher: `C:/Users/Ryan/gig-factory/scripts/browser/launch-hermes-chrome.cmd`
- Splash/identity page: `C:/Users/Ryan/gig-factory/docs/continuity/hermes-browser-start.html`
- Verified tabs currently present: `https://github.com/` and `https://vercel.com/new`
- Important: stay in this dedicated Hermes-controlled Chrome profile for GitHub/Vercel/browser-auth work.

## Verification completed
- `browser.cdp_url` set in Hermes config to `http://127.0.0.1:9222`
- `/json/version` responded with Chrome `149.0.7827.197`
- `/json/list` showed live page targets for GitHub and Vercel
- Dedicated Chrome profile directory exists and contains real Chrome profile files
- Fresh Hermes browser use was verified by running `hermes -z ... -t browser`, which changed a tab in the same CDP browser to `Example Domain`
- SQLite DB exists, schema is present, and `PRAGMA integrity_check` returned `ok`
- Helper scripts run successfully: resume summary, DB health, workflow status

## Git/project state
- Repo path: `C:/Users/Ryan/gig-factory`
- Git status banner: `## No commits yet on master`
- Git remotes: `No git remotes configured.`
- Next repo-level work should stay limited to the intended project only.

## SQLite-first resume order
1. `current_handoff_summary`
2. `resume_queue`
3. `active_workflows`
4. `automation_state`
5. `query_playbook`
6. `database_directory`
7. `tasks`
8. `blockers`
9. latest handoff doc
10. only then deeper files/code as needed

## Exact startup guidance for future Hermes sessions
- Start in `C:/Users/Ryan/gig-factory` so `.hermes.md` loads.
- Query the continuity SQLite DB first: `C:/Users/Ryan/gig-factory/.hermes/continuity/gig_factory_continuity.sqlite3`
- Do **not** begin with broad repo scans or giant file reads.
- Use the helper scripts first:
  - `C:/Users/Ryan/gig-factory/scripts/continuity/resume_summary.py`
  - `C:/Users/Ryan/gig-factory/scripts/continuity/db_health_check.py`
  - `C:/Users/Ryan/gig-factory/scripts/continuity/workflow_status.py`
- If browser/account work is needed, launch the dedicated browser and verify CDP before using browser tools.
- If a session changed browser config mid-flight and does not attach, use `/reset` or start a fresh Hermes session.

## Remaining manual/project actions
- Set git identity before committing/pushing.
- Create/select the intended GitHub repo/remote for this project only.

## 2026-07-18 — Vercel gig-factory live gig publish

Ryan pointed out the Vercel website account contains gigs. Verified Vercel project `the-wathers-edge/gig-factory` was production-deploying only `templates/landing-page` from `main` at old commit `6105d16`, so the 3 gig deliverables under `/gigs/` were not live and the public homepage still showed a generic LaunchFast landing page with no product screenshots.

Completed safe fix:
- Preserved TWEStore autonomous automation disabled/manual; no billing, paid ads, domain, or Vercel plan changes.
- Added the 3 mini-site gigs into the Vercel production root under `templates/landing-page/gigs/`.
- Generated real desktop/mobile output-state screenshots for each gig and served them from `templates/landing-page/assets/screenshots/gigs/`.
- Rebuilt the Vercel homepage into a Gig Factory index with 3 gig cards, actual product screenshots, and links to each working demo.
- Added screenshot proof assets under `docs/assets/screenshots/gigs/` and committed/pushed to GitHub `main`.
- Commit: `02b2708c94857d3658001321e651265b53503666` (`feat: publish gig demos with live screenshots`).
- Vercel dashboard verified new production deployment Ready for commit `02b2708`.
- Live cache-busted verification passed on `https://gig-factory-navy.vercel.app/?v=02b2708` and all 3 gig routes:
  - `/gigs/lead-value-roi-calculator/`
  - `/gigs/local-service-quote-calculator/`
  - `/gigs/website-audit-scorecard/`
- Live verification confirmed homepage has 3 gig cards and 3 screenshot images; every gig route has 2 real screenshot images with nonzero natural dimensions.

Key public URLs:
- `https://gig-factory-navy.vercel.app/`
- `https://gig-factory-navy.vercel.app/gigs/lead-value-roi-calculator/`
- `https://gig-factory-navy.vercel.app/gigs/local-service-quote-calculator/`
- `https://gig-factory-navy.vercel.app/gigs/website-audit-scorecard/`

Evidence:
- Generator/publish script: `scripts/publish_gigs_to_landing_page.py`
- Screenshot contact sheet: `docs/assets/screenshots/gigs/gig-factory-desktop-contact-sheet.jpg`
- Vercel dashboard readback: production deployment `feat: publish gig demos with live screenshots`, status `Ready`, commit `02b2708`, branch `main`.
