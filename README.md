# Route Optimization and Fuel Cost API

## Overview
This project provides an API designed to calculate and display:
1. The optimal route between a start and finish location within the USA.
2. Cost-effective fuel stops along the route, based on fuel prices.
3. The total fuel cost for the journey, considering the vehicle's fuel efficiency and range.

## Key Features
- **Route Optimization**: Generates a route between the specified start and finish locations using a free map and routing API.
- **Fuel Stops**: Identifies the optimal locations for refueling along the route, prioritizing cost-effective options.
- **Fuel Cost Calculation**: Estimates the total money spent on fuel for the journey based on:
  - Vehicle range: 500 miles per tank.
  - Fuel efficiency: 10 miles per gallon.
- **Fuel Price Dataset**: Leverages the provided fuel price dataset to determine refueling costs.

## How It Works
1. **Input**: Users provide a start and finish location within the USA.
2. **Route Calculation**: The API calculates the best route using a free map and routing service.
3. **Fuel Stop Optimization**:
   - The route is divided into 500-mile segments (the maximum vehicle range).
   - Optimal refueling stops are selected within each segment based on fuel prices.
4. **Output**:
   - A map showing the route and marked refueling stops.
   - A summary of the total fuel cost for the journey.

## Prerequisites
- Python 3.7+
- Install dependencies listed in `requirements.txt`.
