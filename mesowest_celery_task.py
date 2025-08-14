# backend/app/tasks/mesowest.py
"""
Celery task wrapper around your existing get_mesowest_data.py
"""
import os
import logging
from datetime import datetime, timedelta
from celery import Celery
from typing import Dict, List

from app.core.config import settings
from app.utils.data_processing import process_mesowest_data
from app.models.station import Station
from app.core.database import SessionLocal

# Your existing imports (we'll move your get_mesowest_data.py code here)
import requests
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

def get_mesowest_data(stations: List[str], start_time: datetime, end_time: datetime) -> Dict:
    """
    Your existing get_mesowest_data function - moved here with minimal changes
    """
    # Base URL for MesoWest API
    base_url = "https://api.mesowest.net/v2/stations/timeseries"
    
    # Your existing API token
    token = settings.MESOWEST_TOKEN
    
    # Parameters for API request
    params = {
        'token': token,
        'stid': ','.join(stations),
        'start': start_time.strftime('%Y%m%d%H%M'),
        'end': end_time.strftime('%Y%m%d%H%M'),
        'vars': 'air_temp,relative_humidity,wind_speed,wind_direction,solar_radiation,snow_depth,precipitation_increment',
        'units': 'metric',
        'output': 'json'
    }
    
    try:
        logger.info(f"Fetching MesoWest data for stations: {stations}")
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('SUMMARY', {}).get('RESPONSE_CODE') != 1:
            logger.error(f"MesoWest API error: {data.get('SUMMARY', {}).get('RESPONSE_MESSAGE')}")
            return {}
        
        # Process the data (your existing logic)
        processed_data = {}
        for station_data in data.get('STATION', []):
            station_id = station_data['STID']
            processed_data[station_id] = process_station_data(station_data)
        
        logger.info(f"Successfully processed data for {len(processed_data)} stations")
        return processed_data
        
    except requests.RequestException as e:
        logger.error(f"Error fetching MesoWest data: {e}")
        return {}
    except Exception as e:
        logger.error(f"Unexpected error processing MesoWest data: {e}")
        return {}

def process_station_data(station_data: Dict) -> Dict:
    """
    Process individual station data - your existing logic
    """
    observations = station_data.get('OBSERVATIONS', {})
    
    # Convert to pandas DataFrame for easier processing
    df_data = {}
    for var, values in observations.items():
        if var == 'date_time':
            df_data[var] = pd.to_datetime(values)
        else:
            df_data[var] = values
    
    df = pd.DataFrame(df_data)
    
    # Your existing data cleaning and processing logic here
    # Fill missing values, quality control, etc.
    
    return df.to_dict('records')

# Celery task definitions
from app.tasks.celery_app import celery_app

@celery_app.task(bind=True, max_retries=3)
def fetch_mesowest_data_task(self, station_ids: List[str] = None, hours_back: int = 24):
    """
    Celery task to fetch MesoWest data for specified stations
    """
    try:
        # Get station list from database if not provided
        if station_ids is None:
            db = SessionLocal()
            try:
                stations = db.query(Station).filter(Station.is_active == True).all()
                station_ids = [station.mesowest_id for station in stations if station.mesowest_id]
            finally:
                db.close()
        
        # Calculate time range
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours_back)
        
        # Fetch data using your existing function
        mesowest_data = get_mesowest_data(station_ids, start_time, end_time)
        
        if not mesowest_data:
            raise Exception("No data returned from MesoWest API")
        
        # Store results in database
        store_mesowest_results(mesowest_data)
        
        logger.info(f"Successfully fetched and stored MesoWest data for {len(mesowest_data)} stations")
        return {
            "status": "success",
            "stations_processed": len(mesowest_data),
            "time_range": f"{start_time} to {end_time}"
        }
        
    except Exception as exc:
        logger.error(f"MesoWest data fetch failed: {exc}")
        # Retry the task with exponential backoff
        raise self.retry(countdown=60 * (2 ** self.request.retries), exc=exc)

def store_mesowest_results(data: Dict):
    """
    Store MesoWest results in database
    """
    db = SessionLocal()
    try:
        # Store the raw data and processed results
        # We'll implement this when we create the database models
        pass
    finally:
        db.close()

@celery_app.task
def daily_mesowest_fetch():
    """
    Daily scheduled task to fetch MesoWest data
    Called at 4 AM and 4 PM
    """
    logger.info("Starting daily MesoWest data fetch")
    
    # Fetch last 24 hours of data
    result = fetch_mesowest_data_task.delay(hours_back=24)
    
    return {
        "task": "daily_mesowest_fetch",
        "started_at": datetime.utcnow().isoformat(),
        "celery_task_id": result.id
    }