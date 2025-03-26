import faiss
import sqlite3
import numpy as np
import ollama
from datetime import datetime

EMBEDDING_MODEL = 'hf.co/CompendiumLabs/bge-base-en-v1.5-gguf'
LANGUAGE_MODEL = 'hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF'

# Initialize FAISS with ID mapping
db_index = faiss.IndexIDMap(faiss.IndexFlatL2(768))
entry_store = {}

def initdb():
    conn = sqlite3.connect('mnemo.db')
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS entries (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   date TEXT NOT NULL,
                   text TEXT NOT NULL,
                   tags TEXT,
                   people TEXT)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS people (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   name TEXT UNIQUE NOT NULL,
                   relationship TEXT)''')
    
    conn.commit()
    conn.close()

def generate_embedding(text):
    embedding = ollama.embed(model=EMBEDDING_MODEL, input=text)['embeddings'][0]
    return np.array(embedding).reshape(1, -1).astype('float32')

def preload_entries():
    conn = sqlite3.connect('mnemo.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, text FROM entries")
    for entry_id, text in cursor.fetchall():
        entry_store[entry_id] = text
        embedding = generate_embedding(text)
        db_index.add_with_ids(embedding, np.array([entry_id]).astype('int64'))
        print(f"Loaded entry {entry_id}: {text}")
    
    conn.close()

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
    
    embedding = generate_embedding(text)
    db_index.add_with_ids(embedding, np.array([entry_id]).astype('int64'))
    entry_store[entry_id] = text
    print(f'Entry {entry_id} added.')

def retrieve_entries(query, top=3):
    query_emb = generate_embedding(query)
    dist, indices = db_index.search(query_emb, top)
    
    print(f"Retrieved indices: {indices}, Distances: {dist}")
    
    results = [(entry_store[idx], 1 - dist[0][i]) for i, idx in enumerate(indices[0]) if idx in entry_store]
    return results

def chat(query):
    ret = retrieve_entries(query)
    context = '\n'.join([f" - {chunk}" for chunk, _ in ret])
    instruction_prompt = f'''
    You are an assistant helping the user recall their past experiences.
    Use only the following pieces of context to answer the question. Answer directly to the point. 
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
    
    print("\nChatbot response:")
    for chunk in stream:
        print(chunk['message']['content'], end='', flush=True)

if __name__ == '__main__':
    initdb()
    preload_entries()
    question = input("Ask mnemo: ")
    print(f'Querying mnemo... searching database... {question}')
    chat(question)