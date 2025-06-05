from pprint import pprint
import json
from openai import OpenAI

# Implement 3 hàm


def get_current_weather(location: str, unit: str):
    """Get the current weather in a given location"""
    # Hardcoded response for demo purposes
    return "Trời rét vãi nôi, 7 độ C"


def get_stock_price(symbol: str):
    # Không làm gì cả, để hàm trống
    pass


# Bài 2: Implement hàm `view_website`, sử dụng `requests` và JinaAI để đọc markdown từ URL
def view_website(url: str):
    # Không làm gì cả, để hàm trống
    pass


# Bài 1: Thay vì tự viết object `tools`, hãy xem lại bài trước, sửa code và dùng `inspect` và `TypeAdapter` để define `tools`
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city name"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "The temperature unit"
                    }
                },
                "required": ["location", "unit"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_stock_price",
            "description": "Get the current stock price of a given symbol",
            "parameters": {"type": "object", "properties": {"symbol": {"type": "string"}}, "required": ["symbol"]}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "view_website",
            "description": "View a website",
            "parameters": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}
        }
    }
]

# https://platform.openai.com/api-keys
client = OpenAI(
    api_key='sk-proj-XXXX',
)
COMPLETION_MODEL = "gpt-4o-mini"

messages = [{"role": "user", "content": "Thời tiết ở Hà Nội hôm nay thế nào?"}]

print("Bước 1: Gửi message lên cho LLM")
pprint(messages)

response = client.chat.completions.create(
    model=COMPLETION_MODEL,
    messages=messages,
    tools=tools
)

print("Bước 2: LLM đọc và phân tích ngữ cảnh LLM")
pprint(response)

print("Bước 3: Lấy kết quả từ LLM")
tool_call = response.choices[0].message.tool_calls[0]

pprint(tool_call)
arguments = json.loads(tool_call.function.arguments)

print("Bước 4: Chạy function get_current_weather ở máy mình")

if tool_call.function.name == 'get_current_weather':
    weather_result = get_current_weather(
        arguments.get('location'), arguments.get('unit'))
    # Hoặc code này cũng tương tự
    # weather_result = get_current_weather(**arguments)
    print(f"Kết quả bước 4: {weather_result}")

    print("Bước 5: Gửi kết quả lên cho LLM")
    messages.append(response.choices[0].message)
    messages.append({
        "role": "tool",
        "content": weather_result,
        "tool_call_id": tool_call.id
    })

    pprint(messages)

    final_response = client.chat.completions.create(
        model=COMPLETION_MODEL,
        messages=messages
        # Ở đây không có tools cũng không sao, vì ta không cần gọi nữa
    )
    print(
        f"Kết quả cuối cùng từ LLM: {final_response.choices[0].message.content}.")
