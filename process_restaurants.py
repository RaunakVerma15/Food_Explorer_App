import json
import os

# Path for the JSON file to store restaurant data
JSON_FILE_PATH = "data/restaurants.json"
# Google Places API Key
API_KEY = 'AIzaSyBCKckQBVOOtg2XKzuqBtnu0Z73atKUyH4'

# Function to load the existing data from the JSON file
def load_existing_data():
    if os.path.exists(JSON_FILE_PATH):
        with open(JSON_FILE_PATH, 'r') as file:
            return json.load(file)
    else:
        return []

# Function to save the updated restaurant data into the JSON file
def save_data(data):
    with open(JSON_FILE_PATH, 'w') as file:
        json.dump(data, file, indent=4)

# Function to check if a restaurant (by place_id) already exists
def restaurant_exists(existing_data, place_id):
    return any(restaurant['id'] == place_id for restaurant in existing_data)

# Function to process and extract the required information from the API response
def process_restaurant_data(api_response):
    existing_data = load_existing_data()
    
    for restaurant in api_response:
        place_id = restaurant.get("place_id")
        name = restaurant.get("name", "")
        rating = restaurant.get("rating", "")
        image_url = restaurant.get("photos", [{}])[0].get("photo_reference", "")
        vicinity = restaurant.get("vicinity", "")
        lat = restaurant["geometry"]["location"].get("lat", "")
        lng = restaurant["geometry"]["location"].get("lng", "")
        
        # Construct the new restaurant entry
        new_restaurant = {
            "id": place_id,
            "name": name,
            "cuisine": "",  # No cuisine data in the response, keeping it empty
            "rating": rating,
            "image": f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={image_url}&key={API_KEY}",
            "dishes": [],  # Empty array for dishes, to be filled later
            "reviews": [],
            "address": {
                "vicinity": vicinity,
                "pincode": "",  # If needed, add logic to extract pincode from vicinity or another source
                "lat": lat,
                "lng": lng
            }
        }
        
        # Check if the restaurant already exists, if not, add to the list
        if not restaurant_exists(existing_data, place_id):
            existing_data.append(new_restaurant)

    # Save updated data back to the JSON file
    save_data(existing_data)