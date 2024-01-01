from django.http import JsonResponse

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


@api_view(['GET', 'POST'])
def hello_world(request):
    if request.method == 'GET':
        data = {'message': 'Hello, World'}
        return JsonResponse(data)
    elif request.method == 'POST':
        # Assuming you want to receive a list of locations in the request body
        received_data = request.data.get('locations', [])
        
        # Process the received locations as needed
        processed_data = []
        for location in received_data:
            lat = location.get('lat')
            lng = location.get('lng')
            
            # Add your logic here, for example, printing the coordinates
            print('Received location: Lat {}, Lng {}'.format(lat, lng))
            
            # Add the processed location to the list
            processed_data.append({'lat': lat, 'lng': lng, 'processed': True})
            
        return Response({'message': 'Locations received and processed successfully', 'data': processed_data}, status=status.HTTP_200_OK)

