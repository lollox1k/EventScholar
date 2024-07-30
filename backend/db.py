# db.py
import sqlite3

def init_db():
    conn = sqlite3.connect('./events.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS events
                 (event_name TEXT, date TEXT, topic TEXT, type TEXT, brief_description TEXT, location TEXT, link TEXT)''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()