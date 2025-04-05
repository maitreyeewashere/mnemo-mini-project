import faiss
import sqlite3
import numpy as np
import ollama

EMBEDDING_MODEL = 'hf.co/CompendiumLabs/bge-base-en-v1.5-gguf'
LANGUAGE_MODEL = 'hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF'

#FAISS index (output size)
db_index = faiss.IndexIDMap(faiss.IndexFlatL2(768))
entry_store = {}

def initdb():
    conn = sqlite3.connect('mnemo.db')
    cursor = conn.cursor()
    #main journal entries
    cursor.execute('''CREATE TABLE IF NOT EXISTS entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        text TEXT NOT NULL,
        tags TEXT,
        people TEXT
    )''')

    #People relationship table
    cursor.execute('''CREATE TABLE IF NOT EXISTS people (
        name TEXT PRIMARY KEY,
        relationship TEXT
    )''')

    conn.commit()
    conn.close()

def join_relations(text, people_str):
    #Enrich text with relationship info from DB
    if not people_str:
        return text

    conn = sqlite3.connect('mnemo.db')
    cursor = conn.cursor()

    enriched_text = text
    people = [p.strip() for p in people_str.split(',') if p.strip()]

    for person in people:
        cursor.execute("SELECT relationship FROM people WHERE name = ?", (person,))
        result = cursor.fetchone()
        if result:
            enriched_text += f" (Person mentioned: {person}, my {result[0]})"

    conn.close()
    return enriched_text

def generate_embedding(text, tags="", people=""):
    #Create embedding from text enriched with tags and people
    combined_text = join_relations(text, people)
    if tags:
        combined_text += f" Tags: {tags}"
    embedding = ollama.embed(model=EMBEDDING_MODEL, input=combined_text)['embeddings'][0]
    return np.array(embedding).reshape(1, -1).astype('float32')

def preload_entries():
    #Loading and embed all journal entries into FAISS
    conn = sqlite3.connect('mnemo.db')
    cursor = conn.cursor()

    cursor.execute("SELECT id, text, tags, people FROM entries")
    for entry_id, text, tags, people in cursor.fetchall():
        # Fall back to empty string if tags/people are None
        tags = tags if tags else ""
        people = people if people else ""

        entry_store[entry_id] = (text, tags, people)
        embedding = generate_embedding(text, tags, people)
        db_index.add_with_ids(embedding, np.array([entry_id]).astype('int64'))

        print(f"Loaded entry {entry_id}: {text} | Tags: {tags} | People: {people}")

    conn.close()

def retrieve_entries(query, top=3):
    #Search similar journal entries for a given query
    query_emb = generate_embedding(query)
    dist, indices = db_index.search(query_emb, top)

    print(f"Retrieved indices: {indices}, Distances: {dist}")

    results = [
        (entry_store[idx], 1 - dist[0][i])  # convert L2 to similarity-ish score
        for i, idx in enumerate(indices[0]) if idx in entry_store
    ]
    return results

def chat(query):
    #Use retrieved entries as context and query the language model.
    ret = retrieve_entries(query)

    if not ret:
        context = "I couldn't find anything relevant in the database."
    else:
        context = '\n'.join([
            f"- Entry: {text} (Tags: {tags}, People: {people})"
            for (text, tags, people), _ in ret
        ])

    instruction_prompt = f'''
You are 'mnemo', an assistant helping the user recall past experiences.
If the retrieved entry says 'I', it refers to the user.
DON'T SAY 'I' unless you're referring to yourself (mnemo). Use 'you' to refer to me, the user. You and I are NOT the same. You are not involved in my personal memories.
Do NOT make up any personal details or invent people.
Be concise and stick to the retrieved information only.

Context:
{context}

If the user asks about school, exams, or reminders, extract relevant info.
If the user greets you (e.g., "hi"), respond casually.

User Query: {query}
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
    response = ''
    for chunk in stream:
        print(chunk['message']['content'], end='', flush=True)
        response += chunk['message']['content']

    return response

def askmnemo(query):
    #Initialize DB, preload, and start chat
    initdb()
    preload_entries()
    print(f'Querying mnemo... searching database... {query}')
    return chat(query)
