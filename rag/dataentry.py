import sqlite3
from datetime import datetime

def add_entry(text, tags=None, people=None):
    conn = sqlite3.connect('mnemo.db')
    cursor = conn.cursor()
    
    date = datetime.now().isoformat()
    people_str = ', '.join(people) if people else None
    
    cursor.execute("INSERT INTO entries(date, text, tags, people) VALUES (?, ?, ?, ?)",
                   (date, text, tags, people_str))
    entry_id = cursor.lastrowid
    conn.commit()
    conn.close()

    print(f'Entry {entry_id} added.')


def add_person(name, rel=None):
    conn = sqlite3.connect('mnemo.db')
    cursor = conn.cursor()

    cursor.execute("INSERT INTO people(name,relationship) VALUES (?, ?)",
                   (name,rel))
    person_id = cursor.lastrowid
    conn.commit()
    conn.close()

    print(f'Entry {person_id} added.')

add_entry('I have a test in April','school,exams,reminder')