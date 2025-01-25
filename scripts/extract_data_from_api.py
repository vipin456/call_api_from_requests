import requests
import os
import csv
import pandas as pd
from dotenv import load_dotenv
from scripts.logger import CustomLogger  # Assuming logger.py is in the 'scripts' folder

# Load environment variables from .env file
load_dotenv()

# Fetch API_KEY from the environment
API_KEY = os.getenv("API_KEY")

# Set up the custom logger
logger = CustomLogger(log_file="app.log", dev_mode=True)  # You can change the log file name as needed

# Check if API_KEY is available
if not API_KEY:
    logger.error("API_KEY is not set in the environment. Exiting...")
    exit(1)

# Fetching data from the API
def fetch_data():
    try:
        logger.info("Fetching data from the API...")
        url = "https://restcountries.com/v3.1/all"
        
        # Set up headers with the API_KEY (assuming the API requires it)
        headers = {
            "Authorization": f"Bearer {API_KEY}"
        }
        
        # Make the request with headers
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Will raise an error for bad status codes (4xx, 5xx)
        logger.info("Successfully fetched data from the API.")
        records = response.json()
        status = transformation_function(records)
        return status
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data from the API: {e}")
        return False

# Function to extract all details for a single country
def extract_all_details(country_data):
    try:
        country_info = {
            'name': country_data['name']['common'],  # Common name
            'name_official': country_data['name']['official'],  # Official name
            'languages': country_data.get('languages', {}),  # Languages, defaults to empty dict
            'capital': country_data.get('capital', [None])[0],  # Capital, or None if not available
            'region': country_data.get('region', 'Unknown'),  # Region
            'population': country_data.get('population', 0),  # Population, default 0
            'currency': country_data['currencies'].get('SHP', {}).get('name', 'No currency info'),  # Currency
            'flag': country_data['flags']['png'],  # Flag image URL
            'timezone': country_data.get('timezones', [None])[0],  # Timezone, or None if not available
            'map_link': country_data['maps']['googleMaps'],  # Map link
        }
        # logger.info(f"Successfully extracted details for {country_data['name']['common']}")
        return country_info
    except KeyError as e:
        logger.error(f"KeyError: Missing key {e} in country data.")
        return {}

def transformation_function(countries):
    try:
        output_file = 'output/output.csv'
        file_exists = False  # Set this to True if the file already exists
        country_data_list = []
        # Process each country's data and store it in a list
        for country_data in countries:
            logger.info(f"Looping through fetching the country data.")
            country_info = extract_all_details(country_data)

            if country_info:  # Only process valid country info
                # logger.info(f"Successfully extracted details.")
                # logger.info(f"Details for {country_info['name']} (Official: {country_info['name_official']}):")
                country_data_list.append(country_info)  # Add the country info to the list
                # for key, value in country_info.items():
                    # logger.info(f"{key}: {value}")
                # logger.info("-" * 50)

        # Convert the list of dictionaries to a Pandas DataFrame
        df = pd.DataFrame(country_data_list)
        df_filtered = df[(df['population'] > 10000000) & (df['languages'].apply(lambda x: 'eng' in x and x['eng'] == 'English'))]
        # df_filtered = df[df['name'].str.contains('United', case=False, na=False)]
        logger.info("Finished processing data.")
        # Open the CSV file in append mode if it exists, otherwise in write mode
        mode = 'a' if file_exists else 'w'
        # Write DataFrame to CSV
        df_filtered.to_csv(output_file, mode=mode, header=not file_exists, index=False, encoding='utf-8')
        logger.info("Finished writing data to CSV.")
        return True
    except Exception as e:
        logger.error(f"Error processing data: {e}")
        return False