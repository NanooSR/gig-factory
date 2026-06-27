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
