"""
BirdNET Image Demo Module (Raspberry Pi)
------------------------------------------
This module checks for an internet connection, monitors the ledger CSV for new detections,
and fetches corresponding bird images from Wikimedia Commons when a new species is detected.
"""

import os
import time
import csv
import requests
import urllib.parse
import yaml

def load_config():
    # Load configuration from config/module_config.yaml
    with open("config/module_config.yaml", "r") as f:
        return yaml.safe_load(f)

def check_internet_connection(test_url="https://www.google.com", timeout=5):
    try:
        requests.get(test_url, timeout=timeout)
        return True
    except requests.RequestException:
        return False

def fetch_and_save_bird_image(scientific_name, config):
    print(f"Fetching image for new bird: {scientific_name}")
    encoded_name = urllib.parse.quote(scientific_name)
    search_url = (
        "https://commons.wikimedia.org/w/api.php?"
        "action=query&format=json&prop=imageinfo&generator=search&"
        f"gsrsearch={encoded_name}&gsrnamespace=6&gsrlimit=1&"
        "iiprop=url|mime&iiurlwidth=500"
    )
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; BirdImageFetcher/1.0)'}
    try:
        response = requests.get(search_url, headers=headers)
        data = response.json()
        pages = data.get('query', {}).get('pages', {})
        if pages:
            for page in pages.values():
                imageinfo = page.get('imageinfo', [{}])[0]
                image_url = imageinfo.get('thumburl')
                if image_url:
                    print(f"Image URL: {image_url}")
                    image_response = requests.get(image_url, headers=headers, allow_redirects=True)
                    if image_response.status_code == 200:
                        CURRENT_BIRD_IMAGE = config["global"]["CURRENT_BIRD_IMAGE"]
                        with open(CURRENT_BIRD_IMAGE, 'wb') as img_file:
                            img_file.write(image_response.content)
                        print(f"Saved image for {scientific_name} as {CURRENT_BIRD_IMAGE}")
                    else:
                        print(f"Failed to download image for {scientific_name}. HTTP status: {image_response.status_code}")
                else:
                    print(f"No image URL found for {scientific_name}")
        else:
            print(f"No images found for {scientific_name}")
    except Exception as e:
        print(f"Error fetching image for {scientific_name}: {e}")

def monitor_ledger(config):
    LEDGER_FILE = config["global"]["LEDGER_FILE"]
    last_scientific_name = None
    while True:
        try:
            with open(LEDGER_FILE, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                rows = list(reader)
                if rows:
                    last_row = rows[-1]
                    scientific_name = last_row.get("scientific_name", "")
                    if scientific_name and scientific_name != last_scientific_name:
                        fetch_and_save_bird_image(scientific_name, config)
                        last_scientific_name = scientific_name
        except Exception as e:
            print(f"Error reading ledger file: {e}")
        time.sleep(3)

def main():
    config = load_config()
    if not check_internet_connection():
        print("No internet connection detected. Exiting image demo module.")
        return
    print("Internet connection detected. Starting image demo...")
    monitor_ledger(config)

if __name__ == '__main__':
    main()
