import requests
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()


# Setup templates (Note: For this example, we'll put the HTML in a string for 1-file ease)
# In a real project, you'd use: templates = Jinja2Templates(directory="templates")

def get_weather_data(station_id: str):
    """Fetch latest weather from NWS and parse it."""
    url = f"https://api.weather.gov/stations/{station_id}/observations/latest"
    headers = {"User-Agent": "FCC-Student-App"}

    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json().get("properties", {})

            # NWS returns Celsius. Let's convert to Fahrenheit.
            temp_c = data.get("temperature", {}).get("value")
            temp_f = round((temp_c * 9 / 5) + 32) if temp_c is not None else "N/A"

            return {
                "temp": f"{temp_f}°F",
                "condition": data.get("textDescription", "Unknown"),
                "humidity": f"{round(data.get('relativeHumidity', {}).get('value') or 0)}%",
                "station": station_id
            }
    except Exception:
        return {"temp": "Error", "condition": "Offline", "humidity": "N/A", "station": station_id}

    return {"temp": "N/A", "condition": "Unavailable", "humidity": "N/A", "station": station_id}


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    # Fetch data for both cities
    fresno = get_weather_data("KFAT")
    nyc = get_weather_data("KNYC")

    # High-end HTML/CSS Template
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Weather Dashboard</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;500;700&display=swap" rel="stylesheet">
        <style>
            body {{
                margin: 0;
                font-family: 'Inter', sans-serif;
                background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
                height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                color: white;
            }}
            .dashboard {{
                display: flex;
                gap: 2rem;
            }}
            .card {{
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(12px);
                -webkit-backdrop-filter: blur(12px);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 24px;
                padding: 2.5rem;
                width: 280px;
                box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
                text-align: center;
                transition: transform 0.3s ease;
            }}
            .card:hover {{ transform: translateY(-10px); }}
            .city-name {{ font-size: 1.5rem; font-weight: 700; margin-bottom: 0.5rem; }}
            .station-id {{ font-size: 0.8rem; opacity: 0.6; text-transform: uppercase; letter-spacing: 1px; }}
            .temp {{ font-size: 4rem; font-weight: 300; margin: 1.5rem 0; }}
            .condition {{ font-size: 1.1rem; font-weight: 500; color: #fbbf24; }}
            .stats {{ margin-top: 2rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.1); display: flex; justify-content: space-between; font-size: 0.9rem; }}
        </style>
    </head>
    <body>
        <div class="dashboard">
            <div class="card">
                <div class="city-name">Fresno, CA</div>
                <div class="station-id">Station: {fresno['station']}</div>
                <div class="temp">{fresno['temp']}</div>
                <div class="condition">{fresno['condition']}</div>
                <div class="stats">
                    <span>Humidity</span>
                    <span>{fresno['humidity']}</span>
                </div>
            </div>

            <div class="card">
                <div class="city-name">New York, NY</div>
                <div class="station-id">Station: {nyc['station']}</div>
                <div class="temp">{nyc['temp']}</div>
                <div class="condition">{nyc['condition']}</div>
                <div class="stats">
                    <span>Humidity</span>
                    <span>{nyc['humidity']}</span>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)