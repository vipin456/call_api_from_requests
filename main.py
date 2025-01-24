import argparse
import os
import csv
import json
import xml.etree.ElementTree as ET
from scripts.extract_data_from_api import fetch_data, extract_all_details
from scripts.logger import CustomLogger  # Assuming logger is in the 'scripts' folder

# Set up the logger
logger = CustomLogger(log_file="app.log", dev_mode=True)  # You can change the log file name as needed
# Fetch API_KEY from the environment
API_KEY = os.getenv("API_KEY")

def get_output_file_from_manifest(manifest_path):
    """Extract the OUT_FILE_BASE path from the manifest XML."""
    try:
        # Open the file in binary mode and read all content
        with open(manifest_path, 'rb') as file:
            content = file.read()

        # Decode content and strip unwanted characters like BOM, leading/trailing whitespaces
        decoded_content = content.decode('utf-8-sig')  # utf-8-sig handles BOM

        # Parse the cleaned content
        tree = ET.ElementTree(ET.fromstring(decoded_content))
        root = tree.getroot()

        # Find the project-field with name="OUT_FILE_BASE"
        for elem in root.findall(".//project-field[@name='OUT_FILE_BASE']"):
            return elem.get('value')
        return None  # If the field is not found

    except ET.ParseError as e:
        logger.error(f"Error parsing manifest.xml: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error occurred while extracting output file path: {e}")
        return None

def get_output_file_path_from_settings(settings_path):
    """Get the output file path from the settings.json based on Docker status."""
    try:
        try:
            with open(settings_path, "r") as file:
                config = json.load(file)
                print(config)            
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
        except FileNotFoundError:
            print("The file was not found.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

        # Check Docker status
        docker_status = config.get('docker_status', 'not_running')
        base_dir = config.get('base_dir', 'C:\\Users\\vipin_sharma\\python\\24_Jan_2025')

        # Set the output directory based on Docker status
        if docker_status == 'running':
            output_dir = '/app/' + config.get('output_dir', 'output')
        else:
            output_dir = base_dir + '\\' + config.get('output_dir', 'output')

        return output_dir

    except Exception as e:
        logger.error(f"Error reading settings.json or processing Docker status: {e}")
        return None

def main():
    try:
        # Parsing arguments from launch.json
        parser = argparse.ArgumentParser(description="Extract data from the API and process it.")
        parser.add_argument("--input_file", type=str, required=True, help="Path to the input CSV file")
        parser.add_argument("--manifest", type=str, required=True, help="Path to the manifest XML file")
        parser.add_argument("--script", type=str, required=True, help="Path to the script file")
        parser.add_argument("--dev_mode", type=str, required=True, help="Development mode flag (true/false)")
        parser.add_argument("--settings", type=str, required=True, help="Path to the settings JSON file")
        
        args = parser.parse_args()

        # Extract the arguments
        input_file = args.input_file
        manifest = args.manifest
        script = args.script
        dev_mode = args.dev_mode.lower() == 'true'
        settings = args.settings
        
        # Fetch output file path from settings.json based on Docker status
        output_file = get_output_file_path_from_settings(settings)
        if not output_file:
            logger.error("Unable to extract output file path from the settings.")
            return

        # Log the extracted arguments
        logger.info(f"Arguments received - Input File: {input_file}, Manifest: {manifest}, Script: {script}, Dev Mode: {dev_mode}, Settings: {settings}, Output File: {output_file}")
        
        # Fetch the country data from the API
        fecth_status = fetch_data()
        if not fecth_status:
            logger.warning("No country data fetched. Exiting...")
            return
        else:
            logger.info(f"Successfully fetched data and stored into the csv file.")        
    except Exception as e:
        logger.error(f"Unexpected error occurred: {e}")
    finally:
        logger.close()

if __name__ == "__main__":
    logger.info("Starting the main function.")
    main()
