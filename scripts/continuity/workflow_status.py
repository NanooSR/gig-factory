from pathlib import Path
import sqlite3

DB = Path(__file__).resolve().parents[2] / '.hermes' / 'continuity' / 'gig_factory_continuity.sqlite3'
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
cur = conn.cursor()
print('WORKFLOWS:')
for row in cur.execute('SELECT workflow_id, name, status, current_stage, requires_browser FROM active_workflows ORDER BY updated_at DESC'):
    print(f"- {row['workflow_id']}: {row['name']} | {row['status']} | stage={row['current_stage']} | requires_browser={row['requires_browser']}")
print('\nTASKS:')
for row in cur.execute('SELECT task_id, status, priority, requires_browser, content FROM tasks ORDER BY priority ASC, task_id ASC'):
    print(f"- p{row['priority']} {row['task_id']} [{row['status']}] browser={row['requires_browser']} :: {row['content']}")
print('\nBLOCKERS:')
for row in cur.execute('SELECT blocker_id, status, owner, blocker, unblock_condition FROM blockers ORDER BY blocker_id ASC'):
    print(f"- {row['blocker_id']} [{row['status']}] owner={row['owner']} :: {row['blocker']} -> {row['unblock_condition']}")
print('\nAUTOMATION STATE:')
for row in cur.execute('SELECT state_key, state_value, notes FROM automation_state ORDER BY state_key ASC'):
    print(f"- {row['state_key']} = {row['state_value']} ({row['notes']})")
conn.close()
