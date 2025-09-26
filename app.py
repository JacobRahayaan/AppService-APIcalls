from flask import Flask, request, render_template_string
import requests
import datetime

app = Flask(__name__)

API_KEY = "efce1907ea51cc7170ec6f087b842c5c"
CURRENT_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
POLLUTION_URL = "http://api.openweathermap.org/data/2.5/air_pollution"

# Mapping AQI ke teks sederhana
AQI_TEXT = {1: "Good ✅", 2: "Fair 🙂", 3: "Moderate 😐", 4: "Poor ⚠️", 5: "Very Poor 🚨"}

# --- UI HTML ---
html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Weather App</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: Arial, sans-serif; background: #f7f8fa; color: #333; text-align: center; }
        .container { margin: 20px auto; width: 900px; padding: 20px; background: white; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
        input, button { padding: 10px; margin: 10px; border-radius: 8px; border: 1px solid #ddd; }
        button { background: #007BFF; color: white; border: none; cursor: pointer; }
        button:hover { background: #0056b3; }
        .card-container { display: flex; justify-content: space-around; margin-top: 20px; flex-wrap: wrap; }
        .card { flex: 1; margin: 10px; padding: 20px; border-radius: 15px; background: #e3f2fd; box-shadow: 0 2px 6px rgba(0,0,0,0.1); }
        .forecast { margin-top: 30px; display: flex; justify-content: space-around; flex-wrap: wrap; }
        .forecast-day { background: #f1f1f1; padding: 10px; border-radius: 10px; width: 100px; margin-bottom: 10px; }
        .forecast-day img { width: 50px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>🌤️ Weather App</h2>
        <form method="get">
            <input type="text" name="city" placeholder="Enter city" value="{{ city }}">
            <button type="submit">Search</button>
        </form>

        {% if error %}
            <p style="color:red;">{{ error }}</p>
        {% endif %}

        {% if current %}
        <h3>{{ current['name'] }}, {{ current['sys']['country'] }}</h3>
        <p><b>{{ current['weather'][0]['main'] }}</b> - {{ current['weather'][0]['description'] }}</p>

        <div class="card-container">
            <div class="card">🌡️ Temperature <br><b>{{ current['main']['temp'] }}°C</b></div>
            <div class="card">💧 Humidity <br><b>{{ current['main']['humidity'] }}%</b></div>
            <div class="card">💨 Wind <br><b>{{ current['wind']['speed'] }} m/s</b></div>
            <div class="card">☁️ Clouds <br><b>{{ current['clouds']['all'] }}%</b></div>
            {% if pollution %}
            <div class="card">
                🌫️ Air Quality <br>
                <b>{{ pollution['aqi_text'] }}</b><br>
                PM2.5: {{ pollution['pm2_5'] }} μg/m³<br>
                PM10: {{ pollution['pm10'] }} μg/m³
            </div>
            {% endif %}
        </div>
        {% endif %}

        {% if labels and temps %}
        <h3>Hourly Forecast</h3>
        <canvas id="tempChart" width="800" height="400"></canvas>
        <script>
            const ctx = document.getElementById('tempChart').getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: {{ labels|safe }},
                    datasets: [{
                        label: 'Temperature (°C)',
                        data: {{ temps|safe }},
                        borderColor: 'rgb(75, 192, 192)',
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        fill: true,
                        tension: 0.3
                    }]
                }
            });
        </script>
        {% endif %}

        {% if daily %}
        <h3>Daily Forecast</h3>
        <div class="forecast">
            {% for day in daily %}
            <div class="forecast-day">
                <p><b>{{ day['day'] }}</b></p>
                <img src="https://openweathermap.org/img/wn/{{ day['icon'] }}@2x.png">
                <p>{{ day['temp_min'] }}°C - {{ day['temp_max'] }}°C</p>
            </div>
            {% endfor %}
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    city = request.args.get("city", "Jakarta")
    current, labels, temps, daily, pollution, error = None, [], [], [], None, None

    # --- Current Weather ---
    params = {"q": city, "appid": API_KEY, "units": "metric"}
    r = requests.get(CURRENT_URL, params=params)
    if r.status_code == 200:
        current = r.json()

        # --- Air Pollution ---
        lat = current['coord']['lat']
        lon = current['coord']['lon']
        pollution_params = {"lat": lat, "lon": lon, "appid": API_KEY}
        r_pollution = requests.get(POLLUTION_URL, params=pollution_params)
        if r_pollution.status_code == 200:
            pol = r_pollution.json()['list'][0]
            pollution = {
                "aqi_text": AQI_TEXT.get(pol['main']['aqi'], "Unknown"),
                "pm2_5": pol['components']['pm2_5'],
                "pm10": pol['components']['pm10']
            }
    else:
        error = "City not found. Please try again."

    # --- Forecast (5 day / 3 hour) ---
    r = requests.get(FORECAST_URL, params=params)
    if r.status_code == 200:
        forecast = r.json()
        # Hourly (ambil 8 data pertama = 24 jam ke depan)
        for item in forecast['list'][:8]:
            time = datetime.datetime.fromtimestamp(item['dt']).strftime('%H:%M')
            labels.append(time)
            temps.append(item['main']['temp'])
        # Daily (ambil suhu min/max per hari)
        daily_data = {}
        for item in forecast['list']:
            date = datetime.datetime.fromtimestamp(item['dt']).strftime('%Y-%m-%d')
            day_name = datetime.datetime.fromtimestamp(item['dt']).strftime('%a')
            temp = item['main']['temp']
            icon = item['weather'][0]['icon']
            if date not in daily_data:
                daily_data[date] = {"min": temp, "max": temp, "icon": icon, "day": day_name}
            else:
                daily_data[date]["min"] = min(daily_data[date]["min"], temp)
                daily_data[date]["max"] = max(daily_data[date]["max"], temp)
        daily = [{"day": v["day"], "temp_min": round(v["min"],1), "temp_max": round(v["max"],1), "icon": v["icon"]} 
                 for v in daily_data.values()][:5]

    return render_template_string(html, current=current, labels=labels, temps=temps, daily=daily, city=city, pollution=pollution, error=error)

if __name__ == "__main__":
    app.run(debug=True)
