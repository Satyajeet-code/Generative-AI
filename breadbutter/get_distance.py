from geopy.geocoders import Nominatim
import geopy.distance
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import time
geolocator = Nominatim(user_agent="BreadButterProject")


def get_lat_long(city, retries=3, delay=1):
    
    for attempt in range(retries):
        try:
            loc = geolocator.geocode(city, timeout=10)  # Increase timeout from 1 → 10 seconds
            if loc:
                coords = [loc.latitude, loc.longitude]

                return coords
            else:
                print(f"City not found: {city}")
                return None
        except (GeocoderTimedOut, GeocoderUnavailable) as e:
            print(f"[Attempt {attempt+1}] Geocoding failed for {city}: {e}")
            time.sleep(delay)
    
    raise Exception(f"Failed to get coordinates for '{city}' after {retries} attempts.")


def calculateDistance(lat1, lon1, lat2, lon2):
    coord1 = (lat1, lon1)
    coord2 = (lat2, lon2)

    return geopy.distance.geodesic(coord1, coord2).kilometers


def get_dist(place1,place2):

    position1 = get_lat_long(place1)
    position2 = get_lat_long(place2)

    distance = calculateDistance(
        position1[0], position1[1], position2[0], position2[1])

    return distance