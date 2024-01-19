import openmeteo_requests
import pandas as pd
from pprint import pprint
import numpy as np
import os

from django.http import JsonResponse
from django.http import HttpResponse
from .models import WeatherEntry
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from tqdm import tqdm

from geopy.distance import geodesic

import logging

logging.basicConfig(
    filename="/home/mohammadamin/Desktop/openmeteo_crawler/get_weather_data/logfile.log",
    level=logging.ERROR,
)


# Setup the Open-Meteo API client with cache and retry on error
openmeteo = openmeteo_requests.Client()


@api_view(["GET", "POST"])
def handle_weather_request(request):
    if request.method == "GET":
        data = {"message": "Hello, World"}
        return JsonResponse(data)
    elif request.method == "POST":
        received_data = request.data
        selected_locations = received_data.get("locations", [])
        distance_resolution = float(received_data.get("resolution", 5.0))  # Default distance resolution is 5 km if not provided
        processed_data = {}
        received_lat = selected_locations[0].get("lat")
        received_lng = selected_locations[0].get("lng")

        received_lat1 = selected_locations[1].get("lat")
        received_lng1 = selected_locations[1].get("lng")

        # Calculate the resolution based on distance in kilometers
        resolution = calculate_resolution((received_lat, received_lng), (received_lat1, received_lng1), distance_resolution)

        # Create a tuple
        coordinate_tuple = (received_lat, received_lng)
        coordinate_tuple1 = (received_lat1, received_lng1)

        grid_points = generate_points(coordinate_tuple, coordinate_tuple1, resolution)

        for lat, lng in tqdm(grid_points, desc="Fetching data", unit="location"):
            weather_data = get_weather_data(lat, lng)

            if weather_data:
                save_to_excel(weather_data, lat, lng, processed_data)
                save_to_database(
                    weather_data, lat, lng
                )  # Call the save_to_database function

        seperate_excel_files()
        return Response(
            {
                "message": "Locations received and processed successfully",
                "data": processed_data,
            },
            status=status.HTTP_200_OK,
        )


def generate_points(point1, point2, resolution):
    x_min, y_min = np.min([point1, point2], axis=0)
    x_max, y_max = np.max([point1, point2], axis=0)
    x_distance = geodesic((x_min, y_min), (x_max, y_min)).kilometers
    y_distance = geodesic((x_min, y_min), (x_min, y_max)).kilometers

    x_steps = int(x_distance / resolution)
    y_steps = int(y_distance / resolution)

    x = np.linspace(x_min, x_max, x_steps)
    y = np.linspace(y_min, y_max, y_steps)

    xv, yv = np.meshgrid(x, y)
    points = np.column_stack((xv.flatten(), yv.flatten()))

    # Save points to the specified file
    file_path = "/home/mohammadamin/Desktop/openmeteo_crawler/get_weather_data/points.txt"
    np.savetxt(file_path, points, delimiter=',')
    # num_points = len(points)
    # print(f"Total number of points generated: {num_points}")

    return points

def calculate_resolution(point1, point2, distance_resolution):
    distance = geodesic(point1, point2).kilometers
    resolution = distance_resolution / distance
    return resolution

def get_weather_data(lat, lng):
    try:
        params = {
            "latitude": lat,
            "longitude": lng,
            "hourly": [
                "temperature_2m",
                "relative_humidity_2m",
                "dew_point_2m",
                "apparent_temperature",
                "precipitation_probability",
                "precipitation",
                "rain",
            ],
        }
        responses = openmeteo.weather_api(
            "https://api.open-meteo.com/v1/forecast", params=params
        )

        response = responses[0]

        hourly = response.Hourly()
        hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
        hourly_relative_humidity_2m = hourly.Variables(1).ValuesAsNumpy()
        hourly_dew_point_2m = hourly.Variables(2).ValuesAsNumpy()
        hourly_apparent_temperature = hourly.Variables(3).ValuesAsNumpy()
        hourly_precipitation_probability = hourly.Variables(4).ValuesAsNumpy()
        hourly_precipitation = hourly.Variables(5).ValuesAsNumpy()
        hourly_rain = hourly.Variables(6).ValuesAsNumpy()

        hourly_data = {
            "date": pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit="s"),
                end=pd.to_datetime(hourly.TimeEnd(), unit="s"),
                freq=pd.Timedelta(seconds=hourly.Interval()),
                inclusive="left",
            )
        }
        hourly_data["temperature_2m"] = hourly_temperature_2m
        hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m
        hourly_data["dew_point_2m"] = hourly_dew_point_2m
        hourly_data["apparent_temperature"] = hourly_apparent_temperature
        hourly_data["precipitation_probability"] = hourly_precipitation_probability
        hourly_data["precipitation"] = hourly_precipitation
        hourly_data["rain"] = hourly_rain

        hourly_dataframe = pd.DataFrame(data=hourly_data)
        return hourly_dataframe.to_dict(orient="records")

    except Exception as e:
        # print(f'Error retrieving weather data: {e}')
        return None


def save_to_excel(weather_data, lat, lng, processed_data):
    try:
        # Create a Pandas DataFrame from the weather data
        df = pd.DataFrame(weather_data)
        location = f"{lat}, {lng}"
        df["location"] = location

        # Get the layer name from the DataFrame (assuming the first column is the layer name)
        layer_name = df.columns[0]

        # Define the file path where you want to save the Excel file based on the layer name
        file_path = "/home/mohammadamin/Desktop/openmeteo_crawler/get_weather_data/full_data.xlsx"

        # Save the DataFrame to an Excel file with improved error handling
        if os.path.exists(file_path):
            try:
                # If the file already exists, append the data to the existing file
                existing_df = pd.read_excel(file_path)
                updated_df = pd.concat([existing_df, df], ignore_index=True)
                updated_df.to_excel(file_path, index=False)
            except Exception as save_error:
                logging.error(f"Error appending data to Excel file: {save_error}")
        else:
            try:
                # If the file does not exist, create a new file
                df.to_excel(file_path, index=False)
            except Exception as save_error:
                logging.error(f"Error creating new Excel file: {save_error}")

        # Update the processed_data dictionary
        if layer_name not in processed_data:
            processed_data[layer_name] = []
        processed_data[layer_name].append(
            {"lat": lat, "lng": lng, "location": location}
        )

        # print(f"Data saved to Excel file: {file_path}")

    except Exception as e:
        logging.error(f"Error saving data to Excel: {e}")
        # You may choose to raise the exception or handle it in a way that suits your needs


def seperate_excel_files():
    excel_file_path = (
        f"/home/mohammadamin/Desktop/openmeteo_crawler/get_weather_data/full_data.xlsx"
    )
    df = pd.read_excel(excel_file_path)

    file1 = df.iloc[:, [0, 1, -1]]
    file1["unit"] = "°C"
    file1.to_excel(
        "/home/mohammadamin/Desktop/openmeteo_crawler/get_weather_data/temperature_2m.xlsx",
        index=False,
    )

    file2 = df.iloc[:, [0, 2, -1]]
    file2["unit"] = "%"
    file2.to_excel(
        "/home/mohammadamin/Desktop/openmeteo_crawler/get_weather_data/relative_humidity_2m.xlsx",
        index=False,
    )

    file3 = df.iloc[:, [0, 3, -1]]
    file3["unit"] = "°C"
    file3.to_excel(
        "/home/mohammadamin/Desktop/openmeteo_crawler/get_weather_data/dew_point_2m.xlsx",
        index=False,
    )

    file4 = df.iloc[:, [0, 4, -1]]
    file4["unit"] = "°C"
    file4.to_excel(
        "/home/mohammadamin/Desktop/openmeteo_crawler/get_weather_data/apparent_temperature.xlsx",
        index=False,
    )

    file5 = df.iloc[:, [0, 5, -1]]
    file5["unit"] = "mm"
    file5.to_excel(
        "/home/mohammadamin/Desktop/openmeteo_crawler/get_weather_data/precipitation_probability.xlsx",
        index=False,
    )

    file6 = df.iloc[:, [0, 6, -1]]
    file6["unit"] = "mm"
    file6.to_excel(
        "/home/mohammadamin/Desktop/openmeteo_crawler/get_weather_data/precipitation.xlsx",
        index=False,
    )

    file7 = df.iloc[:, [0, 7, -1]]
    file7["unit"] = "mm"
    file7.to_excel(
        "/home/mohammadamin/Desktop/openmeteo_crawler/get_weather_data/rain.xlsx",
        index=False,
    )


def save_to_database(weather_data, lat, lng):
    try:
        # Iterate through the weather data and save entries to the database
        for entry in weather_data:
            for key, value in entry.items():
                if key != "date" and key != "location":
                    WeatherEntry.objects.create(
                        layer_name=key, value=value, latitude=lat, longitude=lng
                    )
    except Exception as e:
        logging.error(f"Error saving data to database: {e}")
