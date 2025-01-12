from fuel_router_app.models import FuelStation

def geocode_truckstops(truckstops, router):
    geocoded_data = []
    total_stops = len(truckstops)
    failed_count = 0
    duplicate_count = 0
    success_count = 0
    
    for stop in truckstops:
        formatted_location = stop['Address'].replace("EXIT", "").replace("&", "and").replace("  ", " ").strip()
        
        lat, lon = None, None
        for attempt in [
            f"{formatted_location}, {stop['City']}, {stop['State']}, USA",
            f"{stop['Address'].replace('EXIT', '').strip()}, {stop['City']}, {stop['State']}, USA",
            f"{stop['City']}, {stop['State']}, USA"
        ]:
            lat, lon = router.geocode_location(attempt)
            if lat and lon:
                failed_count += 1
                break
        
        if lat is None or lon is None:
            print(f"Geocoding attempt failed: No data returned for location: {formatted_location}")
            continue
        
        if FuelStation.objects.filter(opis_id=stop['OPIS Truckstop ID']).exists():
            print(f"Skipping FuelStation {stop['OPIS Truckstop ID']} as it already exists.")
            duplicate_count += 1
            continue
        
        geocoded_data.append({
            "Opis id": stop['OPIS Truckstop ID'],
            "Truckstop Name": stop['Truckstop Name'],
            "Address": stop['Address'],
            "City": stop['City'],
            "State": stop['State'],
            "Rack id": stop['Rack ID'],
            "Latitude": lat,
            "Longitude": lon,
            "Retail Price": stop['Retail Price'],
        })
        success_count += 1
    
    print("\n--- Geocoding Summary ---")
    print(f"Total stops processed: {total_stops}")
    print(f"Successfully geocoded: {success_count}")
    print(f"Failed to geocode: {failed_count}")
    print(f"Duplicates skipped: {duplicate_count}")
    print("Geocoding of all locations completed.")
    return geocoded_data