# LEO Satellite Tasking Simulation System

## Overview

This project provides a simulation system for satellite tasking, incorporating real-time data handling and visualization. The primary goal of this system is to simulate satellite orbits, visualize satellite paths over the Earth, and handle GPS-based tasking commands.

## Features

- Calculation of satellite orbital periods based on Kepler's third law.
- Generation of random GPS locations to simulate satellite coverage.
- Distance calculation between two points using the Haversine formula.
- Land detection at given GPS coordinates to determine if a point is on land using geospatial data.
- Real-time satellite tasking simulation with adjustable parameters.
- Visualization of satellite orbits and paths using Matplotlib and Cartopy.

## Dependencies

To run this project, you will need the following Python packages:

- `math`
- `random`
- `requests` (for API calls)
- `numpy`
- `matplotlib`
- `cartopy`
- `datetime`
- `shapely`

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>

2. Install requirements.txt

3. Run the script


## Configuration

You can configure the system by modifying the following constants:
- SATELLITE_ALTITUDE: The altitude of the satellite in kilometers.
- CAPTURE_RADIUS: The radius within which the satellite can capture data.
- INCLINATION: The inclination angle of the satellite's orbit.
- ORBITAL_PERIOD: The time it takes for the satellite to complete one orbit.
- EARTH_ROTATION_SPEED: The rotation speed of Earth in degrees per second.


## API Key
The system uses OpenWeatherMap API for real-time weather data. You must replace 'API_KEY' in the script with your actual API key from OpenWeatherMap.

## Visualization 
The visualization part of the script displays the satellite's orbit around the Earth in real-time, adjusting for the Earth's rotation and the satellite's orbital speed. 

## Disclaimer 

This project is for simulation purposes only and should not be used for actual satellite tasking operations.