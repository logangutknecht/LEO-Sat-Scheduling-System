import math
import random
import requests
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.animation import FuncAnimation
from datetime import datetime, timedelta
from shapely.geometry import Point, MultiPolygon

# Constants
EARTH_RADIUS = 6371  # in kilometers
SATELLITE_ALTITUDE = 500  # in kilometers
CAPTURE_RADIUS = 500  # in kilometers (approximately 25 miles)
INCLINATION = 50  # in degrees
ORBITAL_PERIOD = 90 * 60  # in seconds (90 minutes)
EARTH_ROTATION_SPEED = 360 / (24 * 60 * 60)  # degrees per second

API_ENDPOINT = "http://api.openweathermap.org/data/2.5/weather"
API_KEY = "0a5ba3d622a689ae34ed257ba0b4b007"  # Replace with your actual API key


def calculate_orbital_period(altitude):
    # Calculate the orbital period using Kepler's third law
    GM = 3.986004418 * 10**14  # Earth's gravitational parameter
    orbital_radius = EARTH_RADIUS + altitude
    orbital_period = 2 * math.pi * math.sqrt(orbital_radius**3 / GM)
    return orbital_period

def generate_random_gps_location():
    # Generate a random GPS location within Earth's bounds
    latitude = random.uniform(-90, 90)
    longitude = random.uniform(-180, 180)
    return latitude, longitude

def distance_between_points(lat1, lon1, lat2, lon2):
    # Calculate the distance between two points using the Haversine formula
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = EARTH_RADIUS * c
    return distance

def is_land(lat, lon):
    # Check if the given coordinates are on land
    land_geom = cfeature.LAND.geometries()
    land_geom = MultiPolygon(list(land_geom))
    point = Point(lon, lat)
    return land_geom.contains(point)

def simulate_satellite_tasking(num_commands):
    commands = []
    while len(commands) < num_commands:
        lat = random.uniform(-60, 60)  # Adjust the latitude range to focus on land areas
        lon = random.uniform(-180, 180)
        if is_land(lat, lon):
            commands.append((lat, lon))
    return commands

def visualize_satellite_tasking(commands, speed_factor=1, figure=None):
    if figure is None:
        figure = plt.figure(figsize=(10, 8))
    ax = figure.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    ax.set_extent([-180, 180, -90, 90], crs=ccrs.PlateCarree())
    ax.add_feature(cfeature.LAND)
    ax.add_feature(cfeature.OCEAN)
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS, linestyle=':')

    num_commands = len(commands)
    lats, lons = zip(*commands)

    colors = ['white'] * num_commands
    scatter = ax.scatter(lons, lats, s=100, c=colors, marker='.', zorder=10, transform=ccrs.PlateCarree())

    # Calculate the orbital path
    num_points = 1000  # Increase the number of points for a smoother path
    theta = np.linspace(0, 2*np.pi, num_points)
    orbit_lons = np.rad2deg(theta)
    orbit_lats = INCLINATION * np.sin(theta)

    satellite, = ax.plot([], [], 'bo', markersize=10, transform=ccrs.PlateCarree())
    path, = ax.plot([], [], 'r-', linewidth=1, alpha=0.7, transform=ccrs.PlateCarree())

    time_text = ax.text(0.02, 0.95, '', transform=ax.transAxes, fontsize=12, ha='left', va='top')

    start_time = datetime.now()
    current_time = start_time

    path_lons = np.array([])
    path_lats = np.array([])
    path_segments = []

    def update(frame):
        nonlocal current_time, path_lons, path_lats, path_segments, colors
        elapsed_time = timedelta(seconds=frame * ORBITAL_PERIOD / num_points * speed_factor)
        current_time = start_time + elapsed_time

        unix_time = int(current_time.timestamp())
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

        # Calculate the satellite position based on the elapsed time
        angle = (elapsed_time.total_seconds() % ORBITAL_PERIOD) / ORBITAL_PERIOD * 2 * np.pi
        satellite_lon = np.rad2deg(angle) - EARTH_ROTATION_SPEED * elapsed_time.total_seconds()
        satellite_lat = INCLINATION * np.sin(angle)

        # Wrap the longitude values to stay within [-180, 180] range
        satellite_lon = (satellite_lon + 180) % 360 - 180

        # Check if any command GPS locations are within the capture radius
        capture_color = 'blue'
        for i, (command_lat, command_lon) in enumerate(commands):
            distance = distance_between_points(satellite_lat, satellite_lon, command_lat, command_lon)
            if distance <= CAPTURE_RADIUS:
                # Fetch weather data for the GPS location
                params = {
                    "lat": command_lat,
                    "lon": command_lon,
                    "appid": API_KEY,
                }
                response = requests.get(API_ENDPOINT, params=params)
                weather_data = response.json()

                # Check the cloud cover percentage
                clouds = weather_data["clouds"]["all"]
                if clouds < 50:
                    colors[i] = 'green'
                    print(f"Image captured at ({command_lat}, {command_lon}); {clouds}% cloud cover!")
                else:
                    colors[i] = 'red'
                    print(f"Image NOT captured at ({command_lat}, {command_lon}); {clouds}% cloud cover!")
                

        scatter.set_color(colors)
        satellite.set_data([satellite_lon], [satellite_lat])
        satellite.set_color(capture_color)

        # Update the path line
        path_lons = np.append(path_lons, satellite_lon)
        path_lats = np.append(path_lats, satellite_lat)

        # Calculate the index of the oldest point to keep (two orbits behind)
        max_points = int(2 * ORBITAL_PERIOD / (ORBITAL_PERIOD / num_points))
        if len(path_lons) > max_points:
            path_lons = path_lons[-max_points:]
            path_lats = path_lats[-max_points:]

        # Wrap the path longitude values to stay within [-180, 180] range
        path_lons = (path_lons + 180) % 360 - 180

        # Find the discontinuities in the path line
        lon_diffs = np.abs(np.diff(path_lons))
        lat_diffs = np.abs(np.diff(path_lats))
        discontinuities = np.where((lon_diffs > 180) | (lat_diffs > 90))[0]

        # Split the path line at the discontinuities
        split_lons = np.split(path_lons, discontinuities + 1)
        split_lats = np.split(path_lats, discontinuities + 1)

        # Clear the previous path segments
        for segment in path_segments:
            segment.remove()
        path_segments.clear()

        # Plot each continuous segment of the path line
        for lons, lats in zip(split_lons, split_lats):
            segment, = ax.plot(lons, lats, 'r-', linewidth=1, alpha=0.7, transform=ccrs.PlateCarree())
            path_segments.append(segment)

        time_text.set_text(f"Unix Time: {unix_time}\nDate/Time: {formatted_time}")

        return scatter, satellite, *path_segments, time_text

    num_frames = num_points
    ani = FuncAnimation(figure, update, frames=num_frames, blit=True, interval=ORBITAL_PERIOD*1000/num_frames//speed_factor)

    plt.show()
    
if __name__ == '__main__':
    # Run the simulation
    num_commands = 100
    commands = simulate_satellite_tasking(num_commands)
    speed_factor = 10  # Adjust the speed factor as desired
    visualize_satellite_tasking(commands, speed_factor)