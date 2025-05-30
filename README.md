# mnemo

**mnemo** is a journalling tool and memory aid based on Retrieval-Augmented Generation (RAG). 

mnemo was made by [Maitreyee](github.com/maitreyeewashere), [Shubhangini](https://github.com/shubhusararthy), [Sneha](https://github.com/SnehaMishra05) and [Shrestha](https://github.com/ShresthaRay) as a 6th Semester Mini Project (in partial fulfilment of their BTech degree in Computer Science and Engineering).



https://github.com/user-attachments/assets/7ef901a0-8125-4724-b50a-ef625ee4e825




## Abstract
One of the primary causes of Alzheimer’s disease and other neurodegenerative diseases is the loss of memory. At present, there is no way to treat memory loss itself. For individuals with amnesia, a strong support system can significantly improve the quality of their daily life. This includes family, friends and healthcare professionals who can help with memory aids, daily tasks and emotional support, ensuring safety and promoting a sense of normalcy. 

Mnemo is an intelligent journal-like system that helps users create a personal memory store, and simultaneously retrieve contextual information in an intuitive and accessible way. It leverages FAISS, HuggingFace and Ollama to improve personalized care and foster autonomy and a comforting sense of continuity in navigating daily life with dignity and clarity. 

Keywords: RAG, memory impairment, personal memory aid, assistive technology, human-AI interaction

## Tech Stack
### Flask, FAISS, Ollama, HuggingFace, SQLite3, HTML, CSS

- At its core, Mnemo leverages Retrieval-Augmented Generation (RAG) to create a seamless experience along with Natural Language Processing (NLP). Users (patients, caregivers) log memories or reminders in natural language (such, “What did my sister and I do last week?”). 
-  Mnemo retrieves relevant past entries using a vector similarity search (FAISS) and generates context-aware responses using an LLM (Ollama).
- SQLite3 is used for storage and management of structured data i.e. the user’s memory logs and information about the user’s family, friends and caregivers, are stored in SQLite databases. 
- These entries are processed by HuggingFace to create vector embeddings.

