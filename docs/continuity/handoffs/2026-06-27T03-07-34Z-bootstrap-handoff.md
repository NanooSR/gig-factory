# Gig Factory Handoff / Resume

Generated: 2026-06-27T03:07:34.967079+00:00

## Current handoff summary
Project workspace C:/Users/Ryan/gig-factory contains three starter templates (landing-page, mini-app, browser-game), prompt files, and workflow docs. Git repo has no commits yet and no remote configured. Hermes must use the dedicated visible Chrome CDP profile for GitHub/Vercel sign-in work; future sessions must query the continuity SQLite DB first before broad file reads.

## Browser state
- Required browser mode: visible local Chrome via CDP
- CDP endpoint: `http://127.0.0.1:9222`
- Dedicated Chrome profile: `C:/Users/Ryan/AppData/Local/hermes/browser-profiles/cdp-chrome`
- Browser launcher: `C:/Users/Ryan/gig-factory/scripts/browser/launch-hermes-chrome.cmd`
- Splash/identity page: `C:/Users/Ryan/gig-factory/docs/continuity/hermes-browser-start.html`
- Important: user must sign in inside this dedicated Hermes-controlled Chrome window, not their everyday browser profile.

## Git/project state
- Repo path: `C:/Users/Ryan/gig-factory`
- Git status banner: `## No commits yet on master`
- Git remotes: `No git remotes configured.`
- No commits yet and no remote configured at time of handoff.

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
- If the current chat cannot adopt browser/tool config, use `/reset` or start a fresh Hermes session.

## Pending manual actions
- Sign into GitHub in the dedicated Hermes-controlled Chrome window.
- Sign into Vercel with GitHub in the same dedicated profile if deployment work is needed.
- Set git identity before committing/pushing.
- Create/select the intended GitHub repo/remote for this project only.

## Helper locations
- DB: `C:/Users/Ryan/gig-factory/.hermes/continuity/gig_factory_continuity.sqlite3`
- Launcher: `C:/Users/Ryan/gig-factory/scripts/browser/launch-hermes-chrome.cmd`
- Profile: `C:/Users/Ryan/AppData/Local/hermes/browser-profiles/cdp-chrome`
- Project rules: `C:/Users/Ryan/gig-factory/.hermes.md`
