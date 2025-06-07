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
messageFromUser = input("User: \n")

stream = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": messageFromUser,
        }
    ],
    model="llama3-8b-8192",
    stream=True
)
print("Assistant: ")
for chunk in stream:
    print(chunk.choices[0].delta.content or "", end="")
print()