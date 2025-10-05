import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db.sqlite3')

def main():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        cur.execute('SELECT id, score, last_calculated, resume_id, job_posting_id FROM jobs_jobmatchscore')
        rows = cur.fetchall()
        if not rows:
            print('No JobMatchScore rows found.')
            return
        output = [dict(row) for row in rows]
        print(json.dumps(output, default=str, indent=2))
    except Exception as e:
        print('Error querying jobs_jobmatchscore:', e)
    finally:
        conn.close()

if __name__ == '__main__':
    main()
