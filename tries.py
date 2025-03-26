import sqlite3

conn = sqlite3.connect('mnemo.db')
cursor = conn.cursor()

cursor.execute("SELECT * FROM entries")
entries = cursor.fetchall()

if entries:
    print("Database contains:")
    for entry in entries:
        print(entry)
else:
    print("No entries found!")

conn.close()
