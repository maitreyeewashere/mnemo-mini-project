import faiss
import sqlite3
import numpy as np
import ollama
from datetime import datetime

EMBEDDING_MODEL = 'hf.co/CompendiumLabs/bge-base-en-v1.5-gguf'
LANGUAGE_MODEL = 'hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF'

def preload_entries():
    conn = sqlite3.connect('journal.db')
    cursor = conn.cursor()

    cursor.execute("SELECT id, text FROM entries")
    for entryid, text in cursor.fetchall():
        entry_store[entryid] = text

    conn.close()


def initdb(): #initialise sql database
    conn = sqlite3.connect('journal.db')
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS entries (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   date TEXT NOT NULL,
                   text TEXT NOT NULL,
                   tags TEXT,
                   people TEXT)
    ''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS people (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   name TEXT UNIQUE NOT NULL,
                   relationship TEXT)
''')
    
    conn.commit()
    conn.close()


embedding_dim = 768 
db_index = faiss.IndexFlatL2(embedding_dim)
entry_store = {}

def generateEmbedding(text):
    embedding = ollama.embed(model=EMBEDDING_MODEL,input=text)['embeddings'][0]
    return np.array(embedding).reshape(1,-1).astype('float32')

def addEntry(text, tags=None,people=None):
    conn = sqlite3.connect('journal.db')
    cursor = conn.cursor()

    date = datetime.now().isoformat()
    people_str = ', '.join(map(str,people)) if people else None

    cursor.execute("INSERT INTO entries(date,text,tags, people) VALUES (?,?,?,?)",(date,text,tags, people_str))

    entryid = cursor.lastrowid
    conn.commit()
    conn.close()

    embedding = generateEmbedding(text)
    db_index.add(embedding)
    entry_store[entryid] = text

    print(f'Entry {entryid} added')

def addPerson(name, rel):
    conn = sqlite3.connect('journal.db')
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO people(name,relationship) VALUES (?,?)", (name,rel))
    except sqlite3.IntegrityError:
        print('f"Person {name} already exists')

    conn.commit()

    conn.close()

def retrieveEntries(query, top=3):
    queryemb = generateEmbedding(query)
    dist, indices = db_index.search(queryemb,top)

    results = [(entry_store[idx], 1 - dist[0][1]) for i, idx in enumerate(indices[0]) if idx in entry_store]

    return results

def retrievePerson(name):
    conn = sqlite3.connect("journal.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM people WHERE name = ?",(name,))
    person = cursor.fetchone()
    if not person:
        return []
    person_id = person[0]

    cursor.execute("SELECT text, date FROM entries WHERE people LIKE ?", (f"%{person_id}%",))


    results = cursor.fetchall()
    conn.close()

    return results

def chat(query):
    ret = retrieveEntries(query)
    context = '\n'.join([f" - {chunk}" for chunk, _ in ret])
    instruction_prompt = f'''
    You are an assistant helping the user recall their past experiences. 
    Use only the following pieces of context to answer the question. 
    Do not make up any information not explicitly mentioned:
    {context}
    '''

    stream = ollama.chat(
        model=LANGUAGE_MODEL,
        messages=[
            {'role': 'system', 'content': instruction_prompt},
            {'role': 'user', 'content': query},
        ],
        stream=True,
    )

    print("\nChatbot respons: ")
    for chunk in stream:
        print(chunk['message']['content'],end='',flush=True)

initdb()
preload_entries()

if __name__ == '__main__':
    addPerson('Jane','Friend')
    addPerson('Jon Smith', 'Doctor')

    addEntry('watched Nosferatu with Jane today',tags='movie,outing',people=[1])
    addEntry('appointment with dr smith',tags = 'checkup, doctor',people=[2])

    print(f"\nRetrieving entries that mention Jane Doe: {retrievePerson('Jane')}")

    question = input("Ask mnemo: ")
    print(f'Querying mnemo... searching database... {question}')
    chat(question)