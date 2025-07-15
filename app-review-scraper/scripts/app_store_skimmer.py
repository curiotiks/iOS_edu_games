import pandas as pd
import subprocess
import requests
import time
import json
import os

# Load the moby games dataset

def load_names (path="app-review-scraper/data/mobygames_iphone-ipad-edu_2025-06-09.csv"):
    """
    Load the MobyGames dataset from a specified path.
    """
    df = pd.read_csv(path)
    
    # df = df.head(15) # Limit to first 15 rows for testing
    
    game_names = df['title'].dropna().unique()
    return game_names, df


def safe_request(url, params, retries=3, delay=1.0):
    """
    Make a safe HTTP GET request with retries and error handling.
    Args:
        url (str): The URL to request.
        params (dict): The parameters for the request.
        retries (int): Number of retries on failure.
        delay (float): Delay between retries in seconds.
    Returns:
        dict or None: The JSON response if successful, None otherwise.
    """
    
    for attempt in range(retries):
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code != 200 or not response.content:
                print(f"❌ Bad response [{response.status_code}] on attempt {attempt+1}")
                time.sleep(delay)
                continue
            return response.json()
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            print(f"⚠️ Error on attempt {attempt+1}: {e}")
            time.sleep(delay)
    return None


def fetch_reviews(app_id):
    """
    Fetch reviews for a given app ID using the TypeScript script.
    Args:
        app_id (str): The App Store ID of the app.
    Returns:
        str: The output from the TypeScript script.
    """
    # Fetch reviews using the Node.js script
    try:
        result = subprocess.run(
            ['npx', 'ts-node', 'app-review-scraper/scripts/fetch_reviews.ts', str(app_id)],
            capture_output=True, text=True, env={**os.environ, "NODE_NO_WARNINGS": "1"}
        )

        print("STDERR:", result.stderr)
        reviews = json.loads(result.stdout)
        return(reviews)

    except Exception as e:
        print(f"⚠️ Failed to fetch reviews for {app_id}: {e}")
        return []


if __name__ == "__main__":
    
    # Setup files and data structure
    moby_name_list, df = load_names()
    
    results = {}
    
    if not os.path.exists("app-review-scraper/data/midscrape"):
        print("Creating directory for interim results...")
        os.makedirs("app-review-scraper/data/midscrape")
    
    # Loop over name list and query the App Store API
    for name in moby_name_list: 
        
        params = {
            'term': name, 
            'entity': 'software',
            'country': 'us',
            'limit': 1
        }
        
        print("========================================")
        print("Searching for:", name) 
        data = safe_request('https://itunes.apple.com/search', params=params)
        if not data:
            print("❌ Failed to retrieve data for:", name)
            continue

        if data['resultCount'] > 0:
            print("Found:", name)

            app = data['results'][0]
            
            ## ADD the fetch_reviews.ts call here
            print("Calling fetch_reviews.ts for app ID:", app.get('trackId'))
            collected_reviews = fetch_reviews(app.get('trackId'))

            app_entry = {
                'app_store_id': app.get('trackId'),
                'moby_name': name,
                'app_store_name': app.get('trackName'),
                'developers': df[df['title'] == name]['developers'].values[0] if not df[df['title'] == name]['developers'].empty else None,
                'publisher': df[df['title'] == name]['publishers'].values[0] if not df[df['title'] == name]['publishers'].empty else None,
                'seller_name': app.get('sellerName'),
                'release_date': app.get('releaseDate'),
                
                'target_age': app.get('contentAdvisoryRating'),
                'average_user_rating': app.get('averageUserRating'),
                'user_rating_count': app.get('userRatingCount'),
                'reviews': collected_reviews  # Assign the fetched reviews here
            }
            
            with open(f"app-review-scraper/data/midscrape/{app_entry['app_store_id']}_{app_entry['app_store_name']}.json", "w") as temp_out:
                json.dump(app, temp_out, indent=2)
                print(f"💾 Interim save: DONE")

        else:
            print(" ¯\_(ツ)_/¯ No results found for:", name)
            print("Skipping to next name...")
            print("\n")
            continue
        
        key = app_entry['app_store_id']
        results[key] = app_entry
        
        print("========================================")
        print("\n")
        
        time.sleep(0.5)  # Be polite to the API
        
with open(f"app-review-scraper/data/scraped_game_data.json", "w") as output:
    json.dump(results, output, indent=2)
    print(f"💾 💯 SAVED FINAL RESULTS: {len(results)} entries")

