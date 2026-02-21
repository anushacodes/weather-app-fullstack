from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
from contextlib import asynccontextmanager
import sqlite3
import requests
import csv
import io
import re
import os, html
from fastapi.staticfiles import StaticFiles


DB_NAME = "weather.db"
REQUEST_TIMEOUT = 10

@asynccontextmanager
async def lifespan(app: FastAPI):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS weather_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT,
            start_date TEXT,
            end_date TEXT,
            temperature TEXT
        )
    """)
    conn.commit()
    conn.close()
    yield
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)

app = FastAPI(lifespan=lifespan)
app.mount("/imgs", StaticFiles(directory="imgs"), name="imgs")


class WeatherRequest(BaseModel):
    location: str
    start_date: str
    end_date: str

class UpdateRequest(BaseModel):
    location: str

def get_db():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

@app.get("/")
async def serve_index():
    return FileResponse("index.html")

@app.post("/api/weather")
async def create_weather(data: WeatherRequest):

    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={data.location}&count=1"
    geo_res = requests.get(geo_url, timeout=REQUEST_TIMEOUT).json()

    if not geo_res.get("results"):
        raise HTTPException(status_code=400, detail=f"Could not find location '{data.location}'.")

    location_data = geo_res["results"][0]
    lat = location_data["latitude"]
    lon = location_data["longitude"]
    exact_name = location_data["name"]

    weather_url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&start_date={data.start_date}&end_date={data.end_date}"
        f"&daily=temperature_2m_max&timezone=auto"
    )

    weather_res = requests.get(weather_url, timeout=REQUEST_TIMEOUT).json()

    if "daily" not in weather_res:
        raise HTTPException(status_code=400, detail="Invalid date range.")

    temps = weather_res["daily"]["temperature_2m_max"]
    avg_temp = sum(temps) / len(temps)
    temp_str = f"{avg_temp:.1f} °C"

    forecast_url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&daily=temperature_2m_max,temperature_2m_min"
        f"&forecast_days=5&timezone=auto"
    )

    forecast_data = requests.get(forecast_url, timeout=REQUEST_TIMEOUT).json().get("daily", {})

    wiki_name = exact_name.replace(" ", "_")
    wiki_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{wiki_name}"
    headers = {"User-Agent": "WeatherAppAssessment/1.0"}

    wiki_res = requests.get(wiki_url, headers=headers, timeout=REQUEST_TIMEOUT)
    wiki_summary = (
        wiki_res.json().get("extract")
        if wiki_res.status_code == 200
        else "No Wikipedia description available."
    )

    youtube_video_id = None
    try:
        yt_url = f"https://www.youtube.com/results?search_query={wiki_name}+city+tour+travel"
        yt_html = requests.get(yt_url, headers=headers, timeout=REQUEST_TIMEOUT)

        if yt_html.status_code == 200:
            video_ids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', yt_html.text)
            if len(video_ids) > 1:
                youtube_video_id = video_ids[1]
            elif video_ids:
                youtube_video_id = video_ids[0]

    except Exception:
        pass

    conn = get_db()
    c = conn.cursor()
    c.execute(
        "SELECT id FROM weather_logs WHERE location=? AND start_date=? AND end_date=?",
        (exact_name, data.start_date, data.end_date),
    )
    if not c.fetchone():
        c.execute(
            "INSERT INTO weather_logs (location, start_date, end_date, temperature) VALUES (?, ?, ?, ?)",
            (exact_name, data.start_date, data.end_date, temp_str),
        )
    conn.commit()
    conn.close()

    return {
        "message": f"Successfully saved {exact_name}!",
        "lat": lat,
        "lon": lon,
        "forecast": forecast_data,
        "wiki": wiki_summary,
        "youtube_id": youtube_video_id,
    }

@app.get("/api/weather")
async def read_weather():
    conn = get_db()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM weather_logs")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

@app.put("/api/weather/{id}")
async def update_weather(id: int, data: UpdateRequest):
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE weather_logs SET location=? WHERE id=?", (data.location, id))
    conn.commit()
    conn.close()
    return {"message": "Location updated successfully"}

@app.delete("/api/weather/{id}")
async def delete_weather(id: int):
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM weather_logs WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return {"message": "Deleted successfully"}

@app.get("/api/export/csv")
async def export_csv():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM weather_logs")
    rows = c.fetchall()
    conn.close()

    si = io.StringIO()
    writer = csv.writer(si)
    writer.writerow(["ID", "Location", "Start Date", "End Date", "Avg Max Temperature"])
    writer.writerows(rows)

    return Response(
        content=si.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=weather_data.csv"},
    )