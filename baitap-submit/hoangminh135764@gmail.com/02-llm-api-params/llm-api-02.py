import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path="../../../.env")
api_key = os.getenv("API_KEY_GROQ")

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=api_key,
)
print("Please ask anything")
print("Type 'exit' to quit.")
messages = [
    {
        "role": "system",
        "content": "You are a helpful assistant."
    }
]
while True:

    messageFromUser = input("\nUser: ").strip()
    if messageFromUser.lower() == "exit":
        break

    messages.append(
        {
            "role": "user",
            "content": messageFromUser,
        }
    )
    stream = client.chat.completions.create(
        messages=messages,
        model="llama3-8b-8192",
        stream=True
    )

    print("Assistant:", end=" ", flush=True)
    messageAssistant = ""
    for chunk in stream:
        messageAssistant += chunk.choices[0].delta.content or ""
        print(chunk.choices[0].delta.content or "", end="", flush=True)

    messages.append(
        {
            "role": "assistant",
            "content": messageAssistant,
        }
    )