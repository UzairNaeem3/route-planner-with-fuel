from django.core.management.base import BaseCommand
import csv
from fuel_router_app.models import FuelStation
from fuel_router_app.route_optimizer import RouteOptimizer
from django.conf import settings
from pathlib import Path
from fuel_router_app.management.commands.utils import geocode_truckstops


class Command(BaseCommand):
    help = 'Import fuel stations from CSV file'

    def handle(self, *args, **options):
        base_dir = settings.BASE_DIR
        fule_prices_csv = base_dir / 'fuel-prices-for-be-assessment.csv'
        route_optimizer = RouteOptimizer()

        with open(fule_prices_csv, mode='r') as file:
            reader = csv.DictReader(file)
            truckstops = list(reader)
        
        geocoded_truckstops = geocode_truckstops(truckstops, route_optimizer)
        for stop in geocoded_truckstops:
            try:
                FuelStation.objects.create(
                    opis_id=stop['Opis id'],
                    name=stop['Truckstop Name'],
                    address=stop['Address'],
                    city=stop['City'],
                    state=stop['State'],
                    rack_id=stop['Rack id'],
                    lat=stop['Latitude'],
                    lon=stop['Longitude'],
                    retail_price=stop['Retail Price'],
                )
                print(f"Successfully imported {stop['Truckstop Name']}")
            except Exception as e:
                print(f"Failed to import {stop['Truckstop Name']}: {e}")