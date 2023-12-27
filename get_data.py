import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

# List of coordinates (latitude, longitude) for multiple locations
locations = [
    {"latitude": 52.52, "longitude": 13.41},
    {"latitude": 40.7128, "longitude": -74.0060},  # Example additional location
    # Add more locations as needed in the same format
]

# Weather variables to retrieve
weather_variables = ["temperature_2m", "relative_humidity_2m", "dew_point_2m"]

# Initialize an empty list to store all weather data
all_weather_data = []

# Iterate through each location and fetch weather data
for location in locations:
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "hourly": weather_variables,
        "timezone": "Asia/Bangkok",  # Adjust timezone if needed
        "forecast_days": 14
    }
    responses = openmeteo.weather_api(url, params=params)

    # Process the response for each location
    for response in responses:
        hourly = response.Hourly()
        hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
        hourly_relative_humidity_2m = hourly.Variables(1).ValuesAsNumpy()
        hourly_dew_point_2m = hourly.Variables(2).ValuesAsNumpy()

        hourly_data = {
            "location": f"{location['latitude']},{location['longitude']}",
            "date": pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit="s"),
                end=pd.to_datetime(hourly.TimeEnd(), unit="s"),
                freq=pd.Timedelta(seconds=hourly.Interval()),
                inclusive="left"
            )
        }
        hourly_data["temperature_2m"] = hourly_temperature_2m
        hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m
        hourly_data["dew_point_2m"] = hourly_dew_point_2m

        all_weather_data.append(pd.DataFrame(data=hourly_data))

# Concatenate all weather dataframes into a single dataframe
combined_weather_data = pd.concat(all_weather_data, ignore_index=True)

# Print the combined weather data for all locations
print(combined_weather_data)
