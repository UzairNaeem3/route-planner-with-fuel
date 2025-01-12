from rest_framework.views import APIView
from rest_framework.response import Response
from fuel_router_app.route_optimizer import RouteOptimizer


class RoutePlannerView(APIView):
    def post(self, request):
        start = request.data.get('start')
        end = request.data.get('end')
        
        if not start or not end:
            return Response({'error': 'Start and end locations are required'}, status=400)
            
        route_service = RouteOptimizer()
        
        try:
            # Get route from OSRM
            route_data = route_service.get_route(start, end)
            
            # Find stations near route
            stations = route_service.find_stations_near_route(route_data['geometry'])
            
            # Calculate optimal stops
            result = route_service.calculate_optimal_stops(route_data['distance'], stations)
            
            response_data = {
                'route': {
                    'distance': route_data['distance'],
                    'duration': route_data['duration'],
                    'geometry': route_data['geometry']
                },
                'fuel_stops': [
                    {
                        'station_name': stop['station'].name,
                        'address': stop['station'].address,
                        'city': stop['station'].city,
                        'state': stop['station'].state,
                        'price': float(stop['station'].retail_price),
                        'gallons': float(stop['gallons']),
                        'cost': float(stop['cost']),
                        'distance': float(stop['distance']),
                        'coordinates': [stop['station'].lat, stop['station'].lon]
                    }
                    for stop in result['stops']
                ],
                'total_cost': float(result['total_cost'])
            }
            
            return Response(response_data)
            
        except Exception as e:
            return Response({'error': str(e)}, status=400)
