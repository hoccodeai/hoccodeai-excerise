import os
from openai import OpenAI
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup

load_dotenv(dotenv_path="../../../.env")
api_key = os.getenv("API_KEY_GROQ")

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=api_key,
)

url = input("Please enter website url to summarize content: \n")
# url ="https://tuoitre.vn/cac-nha-khoa-hoc-nga-bao-mat-troi-manh-nhat-20-nam-sap-do-bo-trai-dat-2024051020334196.htm"
html = requests.get(url)
soup = BeautifulSoup(html.text, 'html.parser')
div = soup.find("div", id="main-detail")

if div and div.text:
    text = div.text.replace("\n", " ").replace("\t", " ").strip()
    prompt = (
        'Below is the content of a website enclosed in triple quotes. '
        'Please summarize in 200 words in Vietnamese language'
        f'"""{text}"""'
    )
    stream = client.chat.completions.create(
        messages=[
            {                
                "role": "system",
                "content": "You are an editor who specializes in summarizing website content."
            },
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="llama3-8b-8192",
        stream=True
    )
    print("The summarized content of website is: ")
    for chunk in stream:
        print(chunk.choices[0].delta.content or "", end="", flush=True)
    print() 
else:
    print("No content found or content is empty.")
