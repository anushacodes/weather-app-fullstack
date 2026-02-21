# Fullstack Weather App

A full-stack weather application that goes beyond basic temperature retrieval. I focused on building a resilient backend using Python and a responsive, framework-free frontend. I also intentionally used keyless APIs and web scraping so anyone cloning this repo can run it immediately without setting up billing accounts or API keys.The Product Manager Accelerator Program is designed to support PM professionals through every stage of their careers. From students looking for entry-level jobs to Directors looking to take on a leadership role, our program has helped over hundreds of students fulfill their career aspirations.

## Tech Stack

* **Backend:** Python, FastAPI, Uvicorn
* **Database:** SQLite 
* **Frontend:** Vanilla HTML, CSS, JavaScript

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

### 3. Data Extraction (YouTube)

I built a custom backend web scraper. When a user searches for a city, the backend quietly scrapes YouTube for a local travel tour video, parses the raw HTML using regex to find the first organic video ID, and serves it to a responsive iframe on the frontend.

### 4. Data Export

* Users can click the "Export Data to CSV" button.
* The backend queries the SQLite database, formats the data in memory, and triggers an immediate `.csv` file download.

### 5. Error Handling & Responsive UI

* **Graceful Failures:** If a user types gibberish or a city doesn't exist, the backend catches it and sends a clean error message back to the UI without crashing the server.
* **Responsive Design:** The CSS uses dynamic grids so the layout adapts perfectly for every device.


## How to Run the Project

1. **Clone the repository:**
```bash
git clone [Your-Repository-URL]
cd [Your-Repository-Folder]

```


2. **Install the required Python libraries:**
```bash
pip install fastapi uvicorn requests

```


3. **Start the FastAPI server:**
```bash
uvicorn app:app --reload

```


4. **Open the app:**
Open your web browser and go exactly to: `http://127.0.0.1:8000`


Author
Anusha Nandy | Master of Data Science Student