import sqlite3

def view():
    conn = sqlite3.connect('mnemo.db')
    cursor = conn.cursor()

    
    cursor.execute("SELECT * FROM entries")
    results = cursor.fetchall()
    
    for r in results:
        print(r)
        
    cursor.execute("SELECT * FROM people")
    results = cursor.fetchall()
    
    for r in results:
        print(r)
    
    conn.close()
    
view()