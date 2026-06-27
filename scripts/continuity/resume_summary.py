from pathlib import Path
import sqlite3

DB = Path(__file__).resolve().parents[2] / '.hermes' / 'continuity' / 'gig_factory_continuity.sqlite3'
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
cur = conn.cursor()
summary = cur.execute('SELECT summary, updated_at, latest_handoff_doc, browser_mode FROM current_handoff_summary WHERE id = 1').fetchone()
print('DB:', DB)
print('UPDATED:', summary['updated_at'])
print('BROWSER_MODE:', summary['browser_mode'])
print('SUMMARY:', summary['summary'])
print('\nRESUME_QUEUE:')
for row in cur.execute('SELECT priority, item, status, notes FROM resume_queue ORDER BY priority, id'):
    print(f"  [{row['priority']}] {row['status']} - {row['item']} :: {row['notes'] or ''}")
print('\nACTIVE_WORKFLOWS:')
for row in cur.execute('SELECT workflow_id, status, current_stage FROM active_workflows ORDER BY updated_at DESC'):
    print(f"  {row['workflow_id']} :: {row['status']} :: {row['current_stage']}")
print('\nAUTOMATION_STATE:')
for row in cur.execute('SELECT state_key, state_value FROM automation_state ORDER BY state_key'):
    print(f"  {row['state_key']} = {row['state_value']}")
print('\nLATEST_HANDOFF_DOC:', summary['latest_handoff_doc'])
conn.close()
