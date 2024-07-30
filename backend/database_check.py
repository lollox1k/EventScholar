import sqlite3

def fetch_all_data_from_all_tables():
    conn = sqlite3.connect('./events.db')
    c = conn.cursor()
    
    # Fetch all table names
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = c.fetchall()
    
    # Loop through all tables and fetch all data
    for table in tables:
        table_name = table[0]
        print(f"Contents of table: {table_name}")
        
        c.execute(f"SELECT * FROM {table_name}")
        rows = c.fetchall()
        
        for row in rows:
            print(row)
        print("\n")
    
    conn.close()
    
def get_events():
    conn = sqlite3.connect('./events.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS events
                 (event_name TEXT, date TEXT, topic TEXT, type TEXT, brief_description TEXT, location TEXT, link TEXT)''')
    c.execute("SELECT event_name, date, topic, type, brief_description, location, link FROM events")
    events = c.fetchall()
    conn.close()
    print('!!!!!!')
    print(events)

if __name__ == '__main__':
    fetch_all_data_from_all_tables()
