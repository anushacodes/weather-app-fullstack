from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
from contextlib import asynccontextmanager
import sqlite3
import requests
import csv
import io
import re

@asynccontextmanager
async def lifespan(app: FastAPI):
    conn = sqlite3.connect('weather.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS weather_logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  location TEXT, start_date TEXT, end_date TEXT, temperature TEXT)''')
    conn.commit()
    conn.close()
    yield

app = FastAPI(lifespan=lifespan)

class WeatherRequest(BaseModel):
    location: str
    start_date: str
    end_date: str

class UpdateRequest(BaseModel):
    location: str

@app.get("/")
async def serve_index():
    return FileResponse('index.html')


# create
@app.post("/api/weather")
async def create_weather(data: WeatherRequest):
    # geocode validation
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={data.location}&count=1"
    geo_res = requests.get(geo_url).json()
    if 'results' not in geo_res or not geo_res['results']:
        raise HTTPException(status_code=400, detail=f"Could not find location '{data.location}'.")
    
    lat = geo_res['results'][0]['latitude']
    lon = geo_res['results'][0]['longitude']
    exact_name = geo_res['results'][0]['name']

    weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&start_date={data.start_date}&end_date={data.end_date}&daily=temperature_2m_max&timezone=auto"
    weather_res = requests.get(weather_url).json()
    
    if 'daily' not in weather_res:
        raise HTTPException(status_code=400, detail="Failed to fetch weather. Ensure dates are valid.")
        
    avg_temp = sum(weather_res['daily']['temperature_2m_max']) / len(weather_res['daily']['temperature_2m_max'])
    temp_str = f"{avg_temp:.1f} °C"

    # fetch 5-Day forecast
    forecast_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min&timezone=auto&forecast_days=5"
    forecast_data = requests.get(forecast_url).json().get('daily', {})



    # fetch Wikipedia summary
    wiki_search_name = exact_name.replace(" ", "_")
    wiki_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{wiki_search_name}"
    
    headers = {"User-Agent": "WeatherAppAssessment/1.0 (student)"}
    wiki_res = requests.get(wiki_url, headers=headers)
    
    if wiki_res.status_code == 200:
        wiki_summary = wiki_res.json().get('extract', 'No Wikipedia description available.')
    else:
        wiki_summary = 'No Wikipedia description available for this specific location.'


    youtube_video_id = None
    try:
        yt_search_url = f"https://www.youtube.com/results?search_query={wiki_search_name}+city+tour+travel"
        yt_html_response = requests.get(yt_search_url, headers=headers)
        if yt_html_response.status_code == 200:
            # Regex to find the standard 11-character YouTube video ID in the raw HTML
            video_ids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', yt_html_response.text)
            if video_ids:
                youtube_video_id = video_ids[1] 
    except Exception as e:
        print(f"YouTube extraction failed: {e}")

    # Save to Database
    conn = sqlite3.connect('weather.db')

    # Save to Database
    conn = sqlite3.connect('weather.db')
    c = conn.cursor()
    c.execute("INSERT INTO weather_logs (location, start_date, end_date, temperature) VALUES (?, ?, ?, ?)",
              (exact_name, data.start_date, data.end_date, temp_str))
    conn.commit()
    conn.close()


    return {
        "message": f"Successfully saved {exact_name}!",
        "lat": lat,
        "lon": lon,
        "forecast": forecast_data,
        "wiki": wiki_summary,
        "youtube_id": youtube_video_id 
    }


# read
@app.get("/api/weather")
async def read_weather():
    conn = sqlite3.connect('weather.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM weather_logs")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


# update
@app.put("/api/weather/{id}")
async def update_weather(id: int, data: UpdateRequest):
    conn = sqlite3.connect('weather.db')
    c = conn.cursor()
    c.execute("UPDATE weather_logs SET location=? WHERE id=?", (data.location, id))
    conn.commit()
    conn.close()
    return {"message": "Location updated successfully"}


# delete
@app.delete("/api/weather/{id}")
async def delete_weather(id: int):
    conn = sqlite3.connect('weather.db')
    c = conn.cursor()
    c.execute("DELETE FROM weather_logs WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return {"message": "Deleted successfully"}


# export
@app.get("/api/export/csv")
async def export_csv():
    conn = sqlite3.connect('weather.db')
    c = conn.cursor()
    c.execute("SELECT * FROM weather_logs")
    rows = c.fetchall()
    conn.close()

    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['ID', 'Location', 'Start Date', 'End Date', 'Avg Max Temperature'])
    cw.writerows(rows)

    return Response(
        content=si.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=weather_data.csv"}
    )