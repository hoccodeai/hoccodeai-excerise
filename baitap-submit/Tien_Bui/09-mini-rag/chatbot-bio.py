# 1. Dùng chunking để làm bot trả lời tiểu sử người nổi tiếng, anime v...v
#   - <https://en.wikipedia.org/wiki/S%C6%A1n_T%C3%B9ng_M-TP>
#   - <https://en.wikipedia.org/wiki/Jujutsu_Kaisen>

from wikipediaapi import Wikipedia
from openai import OpenAI
import chromadb
from chromadb.utils import embedding_functions
import os
from dotenv import load_dotenv

COLLECTION_NAME = "Jujutsu_Kaisen"

client = chromadb.PersistentClient(path="./data")
client.heartbeat()

embedding_function = embedding_functions.DefaultEmbeddingFunction()

if not client.get_collection(COLLECTION_NAME):
    collection = client.create_collection(name=COLLECTION_NAME,
                                        embedding_function=embedding_function)
else :
    collection = client.get_collection(COLLECTION_NAME)

wiki = Wikipedia('baitap', 'en')
doc = wiki.page('Jujutsu_Kaisen').text

paragraphs = doc.split('\n\n')
for index, paragraph in enumerate(paragraphs):
    collection.add(documents=[paragraph], ids=[str(index)])


load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

query = "Who is Jujutsu Kaisen?"

q = collection.query(query_texts=[query], n_results=3)
CONTEXT = q["documents"][0]

prompt = f"""
Use the following CONTEXT to answer the QUESTION at the end.
If you don't know the answer, just say that you don't know, don't try to make up an answer.
Use an unbiased and journalistic tone.

CONTEXT: {CONTEXT}

QUESTION: {query}
"""

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": prompt},
    ]
)

print(response.choices[0].message.content)
