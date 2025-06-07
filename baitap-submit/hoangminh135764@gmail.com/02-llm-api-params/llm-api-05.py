import os
from openai import OpenAI
from dotenv import load_dotenv
import re

load_dotenv(dotenv_path="../../../.env")
api_key = os.getenv("API_KEY_GROQ")

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=api_key,
)
print("Please input a programming requirement.")
messageFromUser = input()

prompt = (
    'Below is a programming requirement.'
    "Please write a **complete, runnable Python program** to solve the problem\n"
    "**Return ONLY the code** "
    "no extra narration."
    f'"""{messageFromUser}"""'
)

response = client.chat.completions.create(
    messages=[
        {                
            "role": "system",
            "content": "You are a professional programmer."
        },
        {
            "role": "user",
            "content": prompt,
        }
    ],
    model="llama3-8b-8192",
    temperature=0.2, 
    top_p=0.9
)

generated_code = response.choices[0].message.content.strip()
print(generated_code)

generated_code = generated_code.replace("```python", "").replace("```", "")

with open("final.py", "w", encoding="utf-8") as f:
    f.write(generated_code.rstrip() + "\n")

print("The code has been saved to final.py")
