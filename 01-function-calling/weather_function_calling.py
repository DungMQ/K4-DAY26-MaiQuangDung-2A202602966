"""Minh hoạ FUNCTION CALLING thuần với Google Gemini SDK.

Tool `get_weather` được định nghĩa schema thủ công VÀ thực thi ngay trong
chính file app này. Model chỉ QUYẾT ĐỊNH gọi tool nào; app mới là nơi chạy.

Cách chạy:
    pip install -r ../requirements.txt
    export GEMINI_API_KEY=...
    python weather_function_calling.py
"""

import json
import os
import sys

# Đảm bảo in tiếng Việt chuẩn UTF-8 trên Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

SYSTEM_INSTRUCTION = (
    "Bạn là trợ lý thời tiết thân thiện, trả lời bằng tiếng Việt tự nhiên. "
    "Dùng emoji phù hợp (🌧️ 🌤️ 💨 💧). "
    "Tóm tắt ngắn gọn, dễ hiểu, và đưa ra lời khuyên thực tế "
    "(ví dụ: mang ô, mặc áo mỏng, ...)."
)

from dotenv import load_dotenv

# Nạp biến môi trường từ .env
load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "04-lab", "mcp-client", ".env"))

# API Keys (lấy an toàn từ biến môi trường)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

# 1A. Schema kiểu OpenAI (Chuẩn JSON Schema phổ biến)
OPENAI_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Lấy thời tiết hiện tại của một thành phố",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "Tên thành phố"}
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_forecast",
            "description": "Dự báo thời tiết cho các ngày tới của một thành phố",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "Tên thành phố"},
                    "days": {
                        "type": "integer",
                        "description": "Số ngày cần dự báo (từ 1 đến 3 ngày)",
                    },
                },
                "required": ["city"],
            },
        },
    },
]

# 2. App tự thực thi tools (trong thực tế sẽ gọi API thời tiết thật)
def get_weather(city: str) -> str:
    """Trả về thời tiết hiện tại (mock) của *city*. Dùng làm tool cho model."""
    mock_data = {
        "Hà Nội": {
            "nhiệt_độ": "29°C",
            "thời_tiết": "trời mưa nhẹ",
            "độ_ẩm": "82%",
            "gió": {"hướng": "Đông Nam", "tốc_độ": "12 km/h"},
        },
        "Hồ Chí Minh": {
            "nhiệt_độ": "33°C",
            "thời_tiết": "mưa rào",
            "độ_ẩm": "75%",
            "gió": {"hướng": "Tây Nam", "tốc_độ": "15 km/h"},
        },
        "Đà Nẵng": {
            "nhiệt_độ": "30°C",
            "thời_tiết": "nhiều mây",
            "độ_ẩm": "78%",
            "gió": {"hướng": "Đông", "tốc_độ": "10 km/h"},
        },
    }
    default = {"nhiệt_độ": "28°C", "thời_tiết": "không có dữ liệu chi tiết"}
    return json.dumps({"city": city, **mock_data.get(city, default)}, ensure_ascii=False)


def get_forecast(city: str, days: int = 3) -> str:
    """Trả về dự báo thời tiết (mock) cho *city* trong *days* ngày tới."""
    mock_forecasts = {
        "Hà Nội": [
            {"ngày": "Ngày mai", "nhiệt_độ": "27°C - 31°C", "thời_tiết": "mưa rào rải rác", "khả_năng_mưa": "70%"},
            {"ngày": "Ngày kia", "nhiệt_độ": "26°C - 30°C", "thời_tiết": "nhiều mây, se lạnh về đêm", "khả_năng_mưa": "40%"},
            {"ngày": "Ngày thứ 3", "nhiệt_độ": "28°C - 33°C", "thời_tiết": "trời hửng nắng", "khả_năng_mưa": "20%"},
        ],
        "Đà Nẵng": [
            {"ngày": "Ngày mai", "nhiệt_độ": "28°C - 32°C", "thời_tiết": "nắng nhẹ, chiều tối có mưa dông", "khả_năng_mưa": "60%"},
            {"ngày": "Ngày kia", "nhiệt_độ": "29°C - 34°C", "thời_tiết": "trời nắng đẹp", "khả_năng_mưa": "15%"},
            {"ngày": "Ngày thứ 3", "nhiệt_độ": "27°C - 31°C", "thời_tiết": "mưa rào thoáng qua", "khả_năng_mưa": "50%"},
        ],
        "Hồ Chí Minh": [
            {"ngày": "Ngày mai", "nhiệt_độ": "26°C - 34°C", "thời_tiết": "nắng gián đoạn, mưa rào chiều tối", "khả_năng_mưa": "80%"},
            {"ngày": "Ngày kia", "nhiệt_độ": "27°C - 33°C", "thời_tiết": "mưa dông", "khả_năng_mưa": "75%"},
            {"ngày": "Ngày thứ 3", "nhiệt_độ": "26°C - 34°C", "thời_tiết": "nhiều mây, có lúc có mưa", "khả_năng_mưa": "55%"},
        ],
    }

    forecast_list = mock_forecasts.get(city)
    if not forecast_list:
        forecast_list = [
            {"ngày": f"Ngày +{i+1}", "nhiệt_độ": "27°C - 32°C", "thời_tiết": "thời tiết ôn hòa", "khả_năng_mưa": "30%"}
            for i in range(days)
        ]
    else:
        forecast_list = forecast_list[:days]

    return json.dumps({"city": city, "dự_báo": forecast_list}, ensure_ascii=False)


# Bản đồ các hàm tool sẵn sàng để app gọi
AVAILABLE_TOOLS = {
    "get_weather": get_weather,
    "get_forecast": get_forecast,
}


def run_openai(prompt: str) -> str:
    """Xử lý Function Calling với OpenAI (gpt-4o-mini)."""
    from openai import OpenAI

    print(f"🤖 Đang sử dụng OpenAI model: gpt-4o-mini")
    client = OpenAI(api_key=OPENAI_API_KEY)

    messages = [
        {"role": "system", "content": SYSTEM_INSTRUCTION},
        {"role": "user", "content": prompt},
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=OPENAI_TOOLS,
    )

    choice = response.choices[0]
    while choice.message.tool_calls:
        messages.append(choice.message)
        for tc in choice.message.tool_calls:
            func_name = tc.function.name
            args = json.loads(tc.function.arguments)
            print(f"  [model yêu cầu] {func_name}({args})")
            tool_func = AVAILABLE_TOOLS.get(func_name)
            if tool_func:
                result = tool_func(**args)
            else:
                result = json.dumps({"error": f"Tool '{func_name}' không tồn tại"})
            print(f"  [app thực thi]  -> {result}")
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result,
            })

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=OPENAI_TOOLS,
        )
        choice = response.choices[0]

    return choice.message.content


def run_gemini(prompt: str) -> str:
    """Xử lý Function Calling với Google Gemini."""
    from google import genai
    from google.genai import types

    print(f"🤖 Đang sử dụng Google Gemini model: gemini-2.5-flash")
    client = genai.Client()

    get_weather_declaration = types.FunctionDeclaration(
        name="get_weather",
        description="Lấy thời tiết hiện tại của một thành phố",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={"city": types.Schema(type=types.Type.STRING, description="Tên thành phố")},
            required=["city"],
        ),
    )
    get_forecast_declaration = types.FunctionDeclaration(
        name="get_forecast",
        description="Dự báo thời tiết cho các ngày tới của một thành phố",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "city": types.Schema(type=types.Type.STRING, description="Tên thành phố"),
                "days": types.Schema(type=types.Type.INTEGER, description="Số ngày dự báo"),
            },
            required=["city"],
        ),
    )
    gemini_tools = [types.Tool(function_declarations=[get_weather_declaration, get_forecast_declaration])]

    contents = [types.Content(role="user", parts=[types.Part.from_text(text=prompt)])]
    resp = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=contents,
        config=types.GenerateContentConfig(tools=gemini_tools, system_instruction=SYSTEM_INSTRUCTION),
    )

    while resp.function_calls:
        contents.append(resp.candidates[0].content)
        function_responses = []
        for fc in resp.function_calls:
            print(f"  [model yêu cầu] {fc.name}({fc.args})")
            tool_func = AVAILABLE_TOOLS.get(fc.name)
            result = tool_func(**fc.args) if tool_func else json.dumps({"error": f"Tool '{fc.name}' không tồn tại"})
            print(f"  [app thực thi]  -> {result}")
            function_responses.append(types.Part.from_function_response(name=fc.name, response={"result": result}))

        contents.append(types.Content(role="user", parts=function_responses))
        resp = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=types.GenerateContentConfig(tools=gemini_tools, system_instruction=SYSTEM_INSTRUCTION),
        )

    return resp.text


def run(prompt: str) -> str:
    """Tự động chọn OpenAI hoặc Gemini dựa trên API Key sẵn có."""
    if OPENAI_API_KEY and OPENAI_API_KEY.startswith("sk-"):
        return run_openai(prompt)
    return run_gemini(prompt)


if __name__ == "__main__":
    # Test kịch bản kết hợp: yêu cầu cả thời tiết hiện tại VÀ dự báo tương lai
    question = "Thời tiết hiện tại ở Hà Nội thế nào, và cho tôi xin dự báo thời tiết 3 ngày tới ở Đà Nẵng?"
    print(f"User: {question}\n")
    print("--- Bắt đầu xử lý Function Calling ---")
    answer = run(question)
    print("--- Hoàn thành ---")
    print("\nTrả lời:", answer)
