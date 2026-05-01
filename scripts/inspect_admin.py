import sqlite3, os
DB = r'C:\Users\sijin\Downloads\waste-management-project\backend\database.db'
if not os.path.exists(DB):
    print('DB not found at', DB)
    raise SystemExit(1)
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
cur = conn.cursor()
rows = []
try:
    rows = cur.execute('SELECT username, password FROM admin').fetchall()
    if not rows:
        print('no admin rows')
    for r in rows:
        print('USERNAME:', r['username'])
        print('PASSWORD:', r['password'])
        pwd = r['password'] or ''
        print('looks_hashed:', pwd.startswith('pbkdf2:') or pwd.startswith('argon2:'))
except Exception as e:
    print('Error reading admin table:', e)
finally:
    conn.close()
