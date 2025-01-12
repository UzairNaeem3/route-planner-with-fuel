from rest_framework.views import APIView
from rest_framework.response import Response
from fuel_router_app.route_optimizer import RouteOptimizer
import folium
from fuel_router_app.serializers import RouteRequestSerializer, RouteResponseSerializer


class RoutePlannerView(APIView):
    def post(self, request):
        # Validate request data using serializer
        request_serializer = RouteRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        start = request_serializer.validated_data['start']
        end = request_serializer.validated_data['end']
        route_service = RouteOptimizer()
        
        try:
            # Convert locations to coordinates
            start_lat, start_lon = route_service.geocode_location(start)
            end_lat, end_lon = route_service.geocode_location(end)
            
            # Get route from OSRM
            route_data = route_service.get_route(start_lat, start_lon, end_lat, end_lon)

            # Calculate optimal stops
            result = route_service.find_optimal_fuel_stops(
                (start_lat, start_lon), (end_lat, end_lon)
                route_data['geometry'], route_data['distance'], tank_range=500, mpg=10
                )
            
            # Generate map
            map_html = self.generate_map(route_data['geometry'], result['fuel_stops'])
            
            response_data = {
            'route_coordinates': route_data['routes']['geometry'],
            'fuel_stops': result['fuel_stops'],
            'total_cost': result['total_cost'],
            'total_distance': result['total_distance'],
            'map_url': map_html
            }
            
            serializer = RouteResponseSerializer(data=response_data)
            serializer.is_valid(raise_exception=True)

            return Response(serializer.data)
            
        except Exception as e:
            return Response({'error': str(e)}, status=400)
        

    def generate_map(self, coordinates, fuel_stops):
        # Create map centered on route
        map_center = coordinates[len(coordinates)//2]
        
        m = folium.Map(location=[map_center[1], map_center[0]], zoom_start=14)
        
        # Add route
        folium.PolyLine(
            [(lat, lon) for lon, lat in coordinates],
            weight=2,
            color='blue',
            opacity=0.8
        ).add_to(m)
        
        # Add fuel stops
        for stop in fuel_stops:
            folium.Marker(
                [stop['location']['lat'], stop['location']['lng']],
                popup=f"{stop['name']}<br>Price: ${stop['price']}/gal"
            ).add_to(m)
            
        return m._repr_html_()
