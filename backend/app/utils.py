# backend/app/utils.py
# Utility functions for distance calculations and station filtering

import math
import pandas as pd
from typing import List, Dict, Tuple

def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the Haversine distance between two coordinates in kilometers
    Formula: great-circle distance between two points on a sphere
    """
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Earth's radius in kilometers
    r = 6371
    return c * r

def filter_stations_on_route(
    stations_df: pd.DataFrame,
    car_lat: float,
    car_lon: float,
    dest_lat: float,
    dest_lon: float,
    corridor_km: float = 5.0
) -> List[Dict]:
    """
    Filter stations that lie along the route corridor
    A station is on route if: d(car, station) + d(station, dest) <= d(car, dest) + corridor_km
    Returns sorted list of stations by distance from car
    """
    # Calculate direct distance from car to destination
    car_to_dest = haversine(car_lat, car_lon, dest_lat, dest_lon)
    
    on_route_stations = []
    
    for _, station in stations_df.iterrows():
        station_lat = station['latitude']
        station_lon = station['longitude']
        
        # Calculate distances
        car_to_station = haversine(car_lat, car_lon, station_lat, station_lon)
        station_to_dest = haversine(station_lat, station_lon, dest_lat, dest_lon)
        
        # Check if station is within corridor
        if car_to_station + station_to_dest <= car_to_dest + corridor_km:
            on_route_stations.append({
                'station': station,
                'distance_from_car_km': round(car_to_station, 2),
                'distance_to_dest_km': round(station_to_dest, 2)
            })
    
    # Sort by distance from car ascending
    on_route_stations.sort(key=lambda x: x['distance_from_car_km'])
    
    # Return only top 3
    return on_route_stations[:3]
