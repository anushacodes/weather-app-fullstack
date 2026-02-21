# Fullstack Weather App

A full-stack weather application that goes beyond basic temperature retrieval. I focused on building a resilient backend using Python and a responsive, framework-free frontend. The app integrates multiple APIs for weather data, location context, mapping, and travel videos.

## Tech Stack

* **Backend:** Python, FastAPI, Uvicorn
* **Database:** SQLite 
* **Frontend:** HTML, CSS, JavaScript

## Core Functionalities

### 1. Full CRUD Database Operations

I used SQLite to persist user search history.

* **Create:** Users input a location and date range. The app geocodes the input, fetches the weather, and saves the record.
* **Read:** All past searches are pulled from the database and displayed in a UI table.
* **Update:** Users can click "Edit" to fix or rename a saved location in the database.
* **Delete:** Users can permanently remove any record from their history.

### 2. Advanced API Integrations

I integrated multiple data sources to give the user a complete picture of their destination.

* **Weather & Geocoding:** Uses the Open-Meteo API to validate locations, grab exact coordinates, and calculate the average max temperature for the requested dates.
* **5-Day Forecast:** Automatically generates a 5-day high/low temperature forecast for the searched city.
* **Location Context:** Connects to the Wikipedia API to pull a quick summary of the destination.
* **Interactive Mapping:** Embeds a dynamic map of the exact coordinates using OpenStreetMap.

### 3. YouTube Travel Videos

When a user searches for a city, the backend calls the YouTube Data API v3 to find relevant travel guide videos. Two video links are returned and displayed as clickable links on the frontend. Requires a YouTube API key set in the `.env` file.

### 4. Data Export

* Users can click the "Export Data to CSV" button.
* The backend queries the SQLite database, formats the data in memory, and triggers an immediate `.csv` file download.

### 5. Session-Based Database

* The SQLite database automatically clears when the server shuts down.
* Each session starts fresh so old search data doesn't persist between runs.


## How to Run the Project

1. **Clone the repository:**
```bash
git clone https://github.com/anushacodes/weather-app-fullstack.git
```


2. **Install the required Python libraries:**
```bash
pip install -r requirements.txt
```


3. **Set up your `.env` file:**
```bash
YOUTUBE_API_KEY=your_youtube_api_key_here
```


4. **Start the FastAPI server:**
```bash
uvicorn app:app --reload
```


5. **Open the app:**
Open your web browser and go exactly to: `http://127.0.0.1:8000`



The Product Manager Accelerator Program is designed to support PM professionals through every stage of their careers. From students looking for entry-level jobs to Directors looking to take on a leadership role, our program has helped over hundreds of students fulfill their career aspirations.



Author

Anusha Nandy | Master of Data Science Student