from django.urls import path, include
from .views import handle_weather_request
from rest_framework.routers import DefaultRouter
from .views import generate_points

# from .views import LocationViewSet

# router = DefaultRouter()
# router.register(r'locations', LocationViewSet, basename='locations')

urlpatterns = [
    path("main/", handle_weather_request, name="handle_weather_request"),
    path("get_points/", generate_points, name="generate_points"),
]
