# 2. Thay vì hardcode `doc = wiki.page('Hayao_Miyazaki').text`, sử dụng function calling để:
#   - Lấy thông tin cần tìm từ câu hỏi
#   - Dùng `wiki.page` để lấy thông tin về
#   - Sử dụng RAG để có kết quả trả lời đúng.

from wikipediaapi import Wikipedia
from openai import OpenAI
import chromadb
from chromadb.utils import embedding_functions
import os
from dotenv import load_dotenv
import inspect
from pydantic import TypeAdapter
import json

COLLECTION_NAME = "chatbot-ask"

client = chromadb.PersistentClient(path="./data")
client.heartbeat()

embedding_function = embedding_functions.DefaultEmbeddingFunction()

try:
    collection = client.get_collection(COLLECTION_NAME)
except Exception:
    collection = client.create_collection(name=COLLECTION_NAME,
                                        embedding_function=embedding_function)


wiki = Wikipedia('baitap', 'en')

def fetch_wiki_content(topic: str) -> str:
    """
    Fetch Wikipedia content for a given topic.
    Convert the topic name to Wikipedia format (e.g., 'Elon Musk' -> 'Elon_Musk').
    :param topic: The Wikipedia page topic to fetch, e.g., 'Elon Musk' or 'Jujutsu Kaisen'.
    :output: The full text content from the Wikipedia page.
    """
    try:
        doc = wiki.page(topic).text
        if not doc:
            return f"No content found for topic: {topic}"

        # Add to collection
        paragraphs = doc.split('\n\n')
        for index, paragraph in enumerate(paragraphs):
            collection.add(documents=[paragraph], ids=[f"{topic}_{index}"])

        return f"Successfully loaded {len(paragraphs)} paragraphs from {topic}"
    except Exception as e:
        return f"Error fetching {topic}: {str(e)}"


def query_rag(question: str, n_results: int = 3) -> str:
    """
    Query the RAG system to find relevant context for a question.
    :param question: The question to answer.
    :param n_results: Number of relevant documents to retrieve.
    :output: Relevant context from the knowledge base.
    """
    q = collection.query(query_texts=[question], n_results=n_results)
    if q["documents"] and q["documents"][0]:
        context = "\n\n".join(q["documents"][0])
        return context
    return "No relevant context found."


tools = [
    {
        "type": "function",
        "function": {
            "name": "fetch_wiki_content",
            "description": inspect.getdoc(fetch_wiki_content),
            "parameters": TypeAdapter(fetch_wiki_content).json_schema(),
        },
    },
    {
        "type": "function",
        "function": {
            "name": "query_rag",
            "description": inspect.getdoc(query_rag),
            "parameters": TypeAdapter(query_rag).json_schema(),
        },
    }
]

FUNCTION_MAP = {
    "fetch_wiki_content": fetch_wiki_content,
    "query_rag": query_rag,
}


load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)


def get_completion(messages):
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools,
        temperature=0
    )
    return response


messages = [
    {"role": "system", "content": "You are a helpful assistant that uses tools to fetch Wikipedia content and query the knowledge base to answer questions accurately. Be thorough and helpful."},
]

while True:
    question = input("Who do you want to know about? (or 'quit' to exit): ")

    if question.lower() in ['quit', 'q', 'close', 'exit']:
        break

    messages.append(
        {"role": "user", "content": question}
    )

    response = get_completion(messages)
    first_choice = response.choices[0]
    finish_reason = first_choice.finish_reason

    while finish_reason != "stop":
        tool_call = first_choice.message.tool_calls[0]

        tool_call_function = tool_call.function
        tool_call_arguments = json.loads(tool_call_function.arguments)

        tool_function = FUNCTION_MAP[tool_call_function.name]
        result = tool_function(**tool_call_arguments)

        messages.append(first_choice.message)
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": tool_call_function.name,
            "content": json.dumps({"result": result})
        })

        response = get_completion(messages)
        first_choice = response.choices[0]
        finish_reason = first_choice.finish_reason

    print("\nChat Bot:", first_choice.message.content, "\n")
    messages.append(
        {"role": "assistant", "content": first_choice.message.content}
    )

