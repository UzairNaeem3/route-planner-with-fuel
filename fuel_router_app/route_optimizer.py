import requests
import polyline
from decimal import Decimal
from typing import List, Dict, Tuple
from .models import FuelStation
# from .geocoding import get_coordinates

class RouteOptimizer:
    def __init__(self):
        # Using public OSRM instance - you can also host your own
        self.OSRM_BASE_URL = 'http://router.project-osrm.org'
        self.NOMINATIM_BASE_URL = 'https://nominatim.openstreetmap.org'
        
    def geocode_location(self, location: str) -> Tuple[float, float]:
        """Convert location string to coordinates using Nominatim"""
        url = f'{self.NOMINATIM_BASE_URL}/search'
        params = {
            'q': location,
            'format': 'json',
            'limit': 10,
            'countrycodes': 'us'  # Limit to USA
        }
        headers = {
            'User-Agent': 'RouteOptimizer/1.0'
        }
        response = requests.get(url, params=params, headers=headers)
        if response.status_code != 200:
            raise ValueError(f"Nominatim API request failed with status code {response.status_code}")
        
        data = response.json()
        if not data:
            return None, None
            
        # Extract coordinates from the first non-empty result
        for result in data:
            if 'lat' in result and 'lon' in result:
                return float(result['lat']), float(result['lon'])
            
        return None, None

    def get_route(self, start: str, end: str) -> Dict:
        """Get route using OSRM"""
        # Convert locations to coordinates
        start_lat, start_lon = self.geocode_location(start)
        end_lat, end_lon = self.geocode_location(end)
        
        # Get route from OSRM
        url = f'{self.OSRM_BASE_URL}/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}'
        params = {
            'overview': 'full',
            'geometries': 'polyline',
            'steps': 'true'
        }
        response = requests.get(url, params=params)
        data = response.json()
        
        if data['code'] != 'Ok':
            raise ValueError("Could not calculate route")
            
        route = data['routes'][0]
        
        # Decode the polyline to get route points
        geometry = route['geometry']
        points = polyline.decode(geometry)
        
        return {
            'distance': route['distance'] / 1609.34,  # Convert meters to miles
            'duration': route['duration'] / 3600,  # Convert seconds to hours
            'geometry': points,
            'steps': route['legs'][0]['steps']
        }

    def find_stations_near_route(self, route_points: List[List[float]], max_distance: float = 5) -> List[FuelStation]:
        """Find fuel stations near the route points"""
        stations = []
        checked_states = set()
        
        for point in route_points:
            # Get state from reverse geocoding
            url = f'{self.NOMINATIM_BASE_URL}/reverse'
            params = {
                'lat': point[0],
                'lon': point[1],
                'format': 'json'
            }
            headers = {
                'User-Agent': 'RouteOptimizer/1.0'
            }
            response = requests.get(url, params=params, headers=headers)
            data = response.json()
            
            if 'address' in data and 'state' in data['address']:
                state = data['address']['state']
                if state not in checked_states:
                    # Get stations in this state
                    state_stations = FuelStation.objects.filter(
                        state=state
                    ).order_by('retail_price')[:5]  # Get 5 cheapest stations
                    stations.extend(state_stations)
                    checked_states.add(state)
        
        return stations

    def calculate_optimal_stops(self, route_length: float, stations: List[FuelStation], 
                              tank_range: float = 500, mpg: float = 10) -> Dict:
        """Calculate optimal fuel stops based on price and distance"""
        current_distance = 0
        fuel_stops = []
        total_cost = Decimal('0')
        
        while current_distance < route_length:
            # Find stations within range of current position
            available_stations = [
                station for station in stations 
                if current_distance <= route_length
            ]
            
            if not available_stations:
                break
                
            # Choose cheapest station
            best_station = min(available_stations, key=lambda x: x.retail_price)
            
            # Calculate fuel needed
            distance_to_next = min(tank_range, route_length - current_distance)
            gallons_needed = distance_to_next / mpg
            
            fuel_stops.append({
                'station': best_station,
                'distance': current_distance,
                'gallons': gallons_needed,
                'cost': best_station.retail_price * Decimal(str(gallons_needed))
            })
            
            total_cost += best_station.retail_price * Decimal(str(gallons_needed))
            current_distance += distance_to_next
            
        return {
            'stops': fuel_stops,
            'total_cost': total_cost
        }
