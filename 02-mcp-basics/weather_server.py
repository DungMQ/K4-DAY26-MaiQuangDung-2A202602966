"""MCP SERVER minh hoạ — công bố tool `get_weather` qua giao thức MCP.

Khác với function calling: tool nằm ở một server ĐỘC LẬP. Server tự "khai
báo" tool của mình; bất kỳ MCP client nào (Claude Code, Claude Desktop,
Cursor, hoặc weather_client.py) cũng cắm vào dùng được mà không cần biết
code bên trong.

Schema của tool được TỰ ĐỘNG sinh ra từ type hints + docstring.

Chạy trực tiếp:
    pip install -r ../requirements.txt
    python weather_server.py

Đăng ký với Claude Code (làm 1 lần, dùng mãi):
    claude mcp add weather -- python /đường/dẫn/tới/weather_server.py
"""

from mcp.server.mcpserver import MCPServer

mcp = MCPServer("weather")

_MOCK_DB = {
    "Hanoi": "29°C, trời mưa",
    "Haiphong": "33°C, mưa rào",
    "Danang": "30°C, nhiều mây",
}


@mcp.tool()
def get_weather(city: str) -> str:
    """Lấy thời tiết hiện tại của một thành phố."""
    return f"{city}: {_MOCK_DB.get(city, '28°C, không có dữ liệu chi tiết')}"


@mcp.tool()
def get_forecast(city: str, days: int = 3) -> str:
    """Dự báo thời tiết cho các ngày tới của một thành phố."""
    import json

    mock_forecasts = {
        "Hanoi": [
            {"day": "Ngày mai", "temp": "27°C - 31°C", "condition": "mưa rào rải rác"},
            {"day": "Ngày kia", "temp": "26°C - 30°C", "condition": "nhiều mây"},
            {"day": "Ngày thứ 3", "temp": "28°C - 33°C", "condition": "trời hửng nắng"},
        ],
        "Danang": [
            {"day": "Ngày mai", "temp": "28°C - 32°C", "condition": "nắng nhẹ, mưa dông chiều tối"},
            {"day": "Ngày kia", "temp": "29°C - 34°C", "condition": "trời nắng đẹp"},
            {"day": "Ngày thứ 3", "temp": "27°C - 31°C", "condition": "mưa rào thoáng qua"},
        ],
        "Haiphong": [
            {"day": "Ngày mai", "temp": "27°C - 32°C", "condition": "mưa rào"},
            {"day": "Ngày kia", "temp": "28°C - 33°C", "condition": "nhiều mây"},
            {"day": "Ngày thứ 3", "temp": "29°C - 34°C", "condition": "nắng gián đoạn"},
        ],
    }
    forecast_list = mock_forecasts.get(city)
    if not forecast_list:
        forecast_list = [{"day": f"Ngày +{i+1}", "temp": "28°C", "condition": "thời tiết ôn hòa"} for i in range(days)]
    else:
        forecast_list = forecast_list[:days]

    return json.dumps({"city": city, "forecast": forecast_list}, ensure_ascii=False)


if __name__ == "__main__":
    mcp.run()  # mặc định chạy qua stdio

