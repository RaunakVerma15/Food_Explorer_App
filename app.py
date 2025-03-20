from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import requests
from service.process_restaurants import process_restaurant_data

app = Flask(__name__)
CORS(app)

# Load restaurant data
with open('data/restaurants.json') as f:
    restaurants = json.load(f)

with open('data/dishes.json') as f:
    dishes = json.load(f)

with open('data/cuisines.json') as f:
    cuisines = json.load(f)

# Google Places API Key
API_KEY = 'AIzaSyBCKckQBVOOtg2XKzuqBtnu0Z73atKUyH4'

# Route to search restaurants based on lat/lng or pincode
@app.route('/search/restaurants', methods=['GET'])
def search_restaurants():
    lat = request.args.get('lat')
    lng = request.args.get('lng')
    pincode = request.args.get('pincode')
    
    if lat and lng:
        # Search by latitude and longitude
        location = f'{lat},{lng}'
        radius = 5000  # 5km radius
        google_places_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={location}&radius={radius}&type=restaurant&key={API_KEY}"
    
    elif pincode:
        # Search by pincode (convert pincode to lat/lng using geocoding)
        geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={pincode}&key={API_KEY}"
        geocode_response = requests.get(geocode_url).json()
        if geocode_response['status'] == 'OK':
            location = geocode_response['results'][0]['geometry']['location']
            lat = location['lat']
            lng = location['lng']
            radius = 5000
            google_places_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius={radius}&type=restaurant&key={API_KEY}"
        else:
            return jsonify({"error": "Invalid pincode"}), 400
    
    else:
        return jsonify({"error": "Latitude/Longitude or Pincode required"}), 400

    # Fetching data from Google Places API
    response = requests.get(google_places_url)
    data = response.json()
    
    if data['status'] == 'OK':
        process_restaurant_data(data['results'])
        return jsonify(data['results']), 200
    else:
        return jsonify({"error": "No restaurants found"}), 404

@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    cuisine_id = request.args.get('cuisine')
    dish_id = request.args.get('dish')
    lat = request.args.get('lat')
    lng = request.args.get('lng')
    pincode = request.args.get('pincode')

    print(lat, lng, pincode)
    
    if lat and lng:
        # Search by latitude and longitude
        location = f'{lat},{lng}'
        radius = 5000  # 5km radius
        google_places_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={location}&radius={radius}&type=restaurant&key={API_KEY}"
    
    elif pincode:
        # Search by pincode (convert pincode to lat/lng using geocoding)
        geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={pincode}&key={API_KEY}"
        geocode_response = requests.get(geocode_url).json()
        if geocode_response['status'] == 'OK':
            location = geocode_response['results'][0]['geometry']['location']
            lat = location['lat']
            lng = location['lng']
            radius = 5000
            google_places_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius={radius}&type=restaurant&key={API_KEY}"
        else:
            return jsonify({"error": "Invalid pincode"}), 400
        
    # Fetching data from Google Places API
    response = requests.get(google_places_url)
    data = response.json()

    place_ids = []
    for restaurant in data['results']:
        place_ids.append(restaurant.get("place_id"))

    print(place_ids)
    filtered_restaurants = []
    
    for place_id in place_ids:
        filtered_restaurants.append(next((r for r in restaurants if place_id in r['id']), ''))

    if cuisine_id:
        cuisine = next((item['name'] for item in cuisines if item['id'] == int(cuisine_id)), '')
        filtered_restaurants = [r for r in filtered_restaurants if cuisine.lower() in r['cuisine'].lower()]
    elif dish_id:
        filtered_restaurants = [r for r in filtered_restaurants if int(dish_id) in r['dishes']]

    if not filtered_restaurants:
        filtered_restaurants = restaurants

    return jsonify(filtered_restaurants)


@app.route('/recommendations', methods=['GET'])
def get_recommendations():
    user_id = request.args.get('user_id')
    recommended_restaurants = sorted(restaurants, key=lambda x: x['rating'], reverse=True)[:5]
    return jsonify(recommended_restaurants)

@app.route('/reviews/<int:restaurant_id>', methods=['GET', 'POST'])
def manage_reviews(restaurant_id):
    if request.method == 'GET':
        restaurant = next((r for r in restaurants if r['id'] == restaurant_id), None)
        if restaurant:
            return jsonify(restaurant.get('reviews', []))
        return jsonify([])

    if request.method == 'POST':
        data = request.json
        restaurant = next((r for r in restaurants if r['id'] == restaurant_id), None)
        if restaurant:
            restaurant['reviews'].append(data)
            ratings = [review['rating'] for review in restaurant['reviews']]
            restaurant['rating'] = sum(ratings) / len(ratings)
            return jsonify(restaurant)
        return jsonify({'error': 'Restaurant not found'}), 404
    

@app.route('/cuisines', methods=['GET'])
def get_all_cuisines():
    cuisine = request.args.get('cuisine')
    filtered_cuisines = []

    if cuisine:
        filtered_cuisines = [c for c in cuisines if c['name'].lower() == cuisine.lower()]

    if not filtered_cuisines:
        filtered_cuisines = cuisines
    return jsonify(filtered_cuisines)


@app.route('/dishes', methods=['GET'])
def get_all_dishes():
    dish = request.args.get('dish')
    category = request.args.get('category')
    filtered_dishes = []

    if dish:
        filtered_dishes = [d for d in dishes if d['name'].d.lower() == dish.lower()]
    elif category:
        filtered_dishes = [d for d in dishes if category.lower() in [c.lower() for c in d['category']]]

    if not filtered_dishes:
        filtered_dishes = dishes
    return jsonify(filtered_dishes)


@app.route('/search_dishes', methods=['GET'])
def search_dishes():
    search_text = request.args.get('text', '').lower()

    # Filter dishes based on name, cuisine, or category
    matching_dishes = [
        dish for dish in dishes
        if search_text in dish['name'].lower() or
           (isinstance(dish['cuisine'], list) and any(search_text in cuisine.lower() for cuisine in dish['cuisine'])) or
           (isinstance(dish['cuisine'], str) and search_text in dish['cuisine'].lower()) or
           any(search_text in category.lower() for category in dish['category'])
    ]

    # Return the matching dishes as a JSON response
    return jsonify(matching_dishes)


if __name__ == '__main__':
    app.run(debug=True)
