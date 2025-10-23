# pip install requests
import urllib.parse
import urllib.request
from tkinter import Tk, messagebox, simpledialog

try:
    import requests
except ImportError:
    requests = None


def get_weather_data(location, api_key=None):
    """Get weather data using OpenWeatherMap API or wttr.in (no API key needed)."""
    try:
        if api_key:
            # OpenWeatherMap API (requires API key)
            base_url = "http://api.openweathermap.org/data/2.5/weather"
            params = {"q": location, "appid": api_key, "units": "metric"}

            if requests:
                response = requests.get(base_url, params=params, timeout=10)
                if response.status_code == 200:
                    return response.json()
                else:
                    return {"error": f"API Error: {response.status_code}"}
            else:
                return {"error": "requests library not available"}
        else:
            # wttr.in service (no API key required)
            url = f"https://wttr.in/{urllib.parse.quote(location)}?format=j1"

            if requests:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    return response.json()
                else:
                    return {"error": f"Service Error: {response.status_code}"}
            else:
                # Fallback using urllib
                with urllib.request.urlopen(url) as response:
                    import json

                    return json.loads(response.read().decode())

    except Exception as e:
        return {"error": str(e)}


def format_weather_openweather(data):
    """Format weather data from OpenWeatherMap."""
    try:
        weather = data["weather"][0]
        main = data["main"]
        wind = data.get("wind", {})

        return f"""Weather for {data["name"]}, {data["sys"]["country"]}
Description: {weather["description"].title()}
Temperature: {main["temp"]:.1f}°C (feels like {main["feels_like"]:.1f}°C)
Humidity: {main["humidity"]}%
Pressure: {main["pressure"]} hPa
Wind: {wind.get("speed", "N/A")} m/s
Visibility: {data.get("visibility", "N/A")} m"""

    except KeyError as e:
        return f"Error formatting weather data: {e}"


def format_weather_wttr(data):
    """Format weather data from wttr.in."""
    try:
        current = data["current_condition"][0]
        location = data["nearest_area"][0]

        return f"""Weather for {location["areaName"][0]["value"]}, {location["country"][0]["value"]}
Description: {current["weatherDesc"][0]["value"]}
Temperature: {current["temp_C"]}°C (feels like {current["FeelsLikeC"]}°C)
Humidity: {current["humidity"]}%
Pressure: {current["pressure"]} mb
Wind: {current["windspeedKmph"]} km/h {current["winddir16Point"]}
Visibility: {current["visibility"]} km
UV Index: {current["uvIndex"]}"""

    except KeyError as e:
        return f"Error formatting weather data: {e}"


def main():
    root = Tk()
    root.withdraw()

    # Get location
    location = simpledialog.askstring(
        "Weather Checker",
        "Enter location (city, country):\n"
        "Examples:\n"
        "- London, UK\n"
        "- New York, US\n"
        "- Tokyo\n"
        "- Paris, France",
    )

    if not location:
        return

    # Ask about API key
    use_api = messagebox.askyesno(
        "API Choice",
        "Do you have an OpenWeatherMap API key?\n\n"
        "Yes: Use OpenWeatherMap (more detailed)\n"
        "No: Use wttr.in (free, no registration)",
    )

    api_key = None
    if use_api:
        api_key = simpledialog.askstring(
            "API Key",
            "Enter your OpenWeatherMap API key:\n(Get free key at openweathermap.org)",
        )
        if not api_key:
            messagebox.showinfo("Info", "Using wttr.in service instead.")

    print(f"Getting weather data for: {location}")

    # Get weather data
    weather_data = get_weather_data(location, api_key)

    if "error" in weather_data:
        error_msg = f"Error getting weather data: {weather_data['error']}"
        print(error_msg)
        messagebox.showerror("Error", error_msg)
        return

    # Format and display weather
    if api_key and "main" in weather_data:
        # OpenWeatherMap format
        weather_report = format_weather_openweather(weather_data)
    else:
        # wttr.in format
        weather_report = format_weather_wttr(weather_data)

    print("\n" + "=" * 50)
    print("WEATHER REPORT")
    print("=" * 50)
    print(weather_report)

    # Show in dialog
    messagebox.showinfo("Weather Report", weather_report)


if __name__ == "__main__":
    main()
