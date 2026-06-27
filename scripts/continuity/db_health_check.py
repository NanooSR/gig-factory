from pathlib import Path
import sqlite3
import sys

DB = Path(__file__).resolve().parents[2] / '.hermes' / 'continuity' / 'gig_factory_continuity.sqlite3'
required_tables = {
    'current_handoff_summary', 'resume_queue', 'active_workflows', 'automation_state',
    'handoff_summaries', 'audit_log', 'query_playbook', 'database_directory',
    'file_locations', 'tasks', 'blockers'
}
if not DB.exists():
    print('MISSING DB:', DB)
    sys.exit(1)
conn = sqlite3.connect(DB)
cur = conn.cursor()
print('DB:', DB)
print('integrity_check:', cur.execute('PRAGMA integrity_check').fetchone()[0])
existing = {row[0] for row in cur.execute("SELECT name FROM sqlite_master WHERE type='table'")}
missing = sorted(required_tables - existing)
print('tables_present:', len(existing))
print('required_tables_missing:', missing)
for table in sorted(required_tables):
    count = cur.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
    print(f'row_count[{table}] = {count}')
conn.close()
sys.exit(0 if not missing else 1)
