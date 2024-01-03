import openmeteo_requests
import pandas as pd
from pprint import pprint

from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

# Setup the Open-Meteo API client with cache and retry on error
openmeteo = openmeteo_requests.Client()

@api_view(['GET', 'POST'])
def hello_world(request):
    if request.method == 'GET':
        data = {'message': 'Hello, World'}
        return JsonResponse(data)
    elif request.method == 'POST':
        received_data = request.data.get('locations', [])

        # Process the received locations as needed
        processed_data = []
        for location in received_data:
            lat = location.get('lat')
            lng = location.get('lng')

            # Retrieve weather data from OpenMeteo API
            weather_data = get_weather_data(lat, lng)

            # Add your custom logic here to save weather_data to the database
            # For demonstration purposes, save the weather_data to an Excel file
            save_to_excel(weather_data, lat, lng)

            # Add the processed location and weather data to the list
            processed_data.append({'lat': lat, 'lng': lng, 'weather_data': weather_data})

        return Response({'message': 'Locations received and processed successfully', 'data': processed_data}, status=status.HTTP_200_OK)
    
def get_weather_data(lat, lng):
    try:
        # Specify the additional weather variables you want
        additional_variables = [
            "relative_humidity_2m",
            "dewpoint_2m",
            # Add other variables as needed
        ]

        # Construct the list of hourly variables
        hourly_variables = ["temperature_2m"] + additional_variables

        # Add the hourly variables to the params dictionary
        params = {
            "latitude": lat,
            "longitude": lng,
            "hourly": hourly_variables
        }

        # Make the API request
        responses = openmeteo.weather_api("https://api.open-meteo.com/v1/forecast", params=params)

        # Process first location. Add a for-loop for multiple locations or weather models
        response = responses[0]

        # Process hourly data. The order of variables needs to be the same as requested.
        hourly = response.Hourly()

        # Create a dictionary to store the data for each variable
        variable_data = {"date": pd.to_datetime(hourly.Time(), unit="s")}

        for variable in hourly_variables:
            variable_values = hourly.VariablesByName(variable).ValuesAsNumpy()
            variable_data[variable] = variable_values

        # Create a DataFrame from the variable data
        variable_dataframe = pd.DataFrame(data=variable_data)

        # Combine the data from different variables into a single DataFrame
        result_dataframe = pd.concat([variable_dataframe], axis=1)

        return result_dataframe.to_dict(orient='records')

    except Exception as e:
        print(f'Error retrieving weather data: {e}')
        return None

def save_to_excel(weather_data, lat, lng):
    try:
        # Create a Pandas DataFrame from the weather data
        df = pd.DataFrame(weather_data)

        # Define the file path where you want to save the Excel file
        file_path = f'/home/mohammadamin/Desktop/openmeteo_crawler/get_weather_data/weather_data_{lat}_{lng}.xlsx'

        # Save the DataFrame to an Excel file
        df.to_excel(file_path, index=False)

        print(f'Data saved to Excel file: {file_path}')

    except Exception as e:
        print(f'Error saving data to Excel: {e}')
