# NYC 311 Monitor

A Python-based monitoring system that fetches NYC 311 complaints, processes them, stores them in a local database, and detects meaningful spikes or trends across categories and boroughs.

## Features

- **Automated data fetching**  
  Pulls the latest NYC 311 complaints from the official NYC Open Data API.

- **Data processing pipeline**  
  Normalizes fields, extracts time-of-day features, categorizes complaints, and enriches records.

- **SQLite database storage**  
  Saves new complaints while avoiding duplicates.

- **Trend + spike detection**  
  Identifies surges in:
  - total complaints  
  - complaint categories (Noise, Parking, Heat/Hot Water, etc.)  
  - borough activity  

- **Scheduled execution**  
  Runs automatically every 15 minutes using APScheduler.

- **Structured logging**  
  Console + rotating file logs for monitoring and debugging.

## Project Structure
