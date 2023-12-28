from django.urls import path, include
from .views import hello_world
from rest_framework.routers import DefaultRouter
# from .views import LocationViewSet

# router = DefaultRouter()
# router.register(r'locations', LocationViewSet, basename='locations')

urlpatterns = [
    path('hello/', hello_world, name='hello_world'),
]