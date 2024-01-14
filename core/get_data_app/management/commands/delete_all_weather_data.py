
def delete_everything(self):
    WeatherEntry.objects.all().delete()

#def drop_table(self):
#    cursor = connection.cursor()
#    table_name = self.model._meta.db_table
#    sql = "DROP TABLE %s;" % (table_name, )
#    cursor.execute(sql)



from django.core.management.base import BaseCommand, CommandError
from get_data_app.models import WeatherEntry


class Command(BaseCommand):
    help = "Delete all weather data"

    # def add_arguments(self, parser):
    #     parser.add_argument("poll_ids", nargs="+", type=int)

    def handle(self, *args, **options):
        try:
            WeatherEntry.objects.all().delete()
        except Exception as e:
            print(f"exception is ---> {e} ---------")