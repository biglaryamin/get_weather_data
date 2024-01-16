from django.contrib import admin
from .models import WeatherEntry

class WeatherEntryAdmin(admin.ModelAdmin):
    # Your existing configurations for the admin class

    def save_to_excel(self, request, queryset):
        # Your custom logic goes here
        # `queryset` contains the selected objects
        print("************************")
        # self.message_user(request, f'Custom function executed for {queryset.count()} items.')

    save_to_excel.short_description = "save_to_excel"

    actions = ['save_to_excel']
# Register the admin class with the model
admin.site.register(WeatherEntry, WeatherEntryAdmin)

