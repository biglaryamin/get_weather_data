from django.http import JsonResponse

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


@api_view(['GET'])
def hello_world(request):
    data = {'message':'Hello, World'}
    return JsonResponse(data)