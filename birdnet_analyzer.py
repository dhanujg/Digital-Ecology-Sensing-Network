"""
BirdNET Analyzer Module
-------------------------
Objective:
- Load the BirdNET model (using birdnetlib) and monitor the recordings folder for new WAV files.
- For each new recording, analyze the audio file using the BirdNET analyzer and generate detection results.
- Update a ledger CSV file (saved in the BirdNET data stream folder as specified in the config) with detection information.
- Delete the original WAV file after processing to prevent reanalysis.

Usage:
Run this file to continuously process new audio recordings. It assumes the recordings folder is being populated by audio_recording.py.
"""

import os
import time
import json
import csv
from datetime import datetime, timedelta
from threading import Lock
from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer

# Lock for CSV writes (to minimize concurrent access issues)
csv_lock = Lock()

def load_config():
    """Load configuration values from the JSON config file."""
    with open("config.json", "r") as f:
        return json.load(f)

def analyze_recording(analyzer, wav_file, config, timestamp):
    """Analyze a WAV file using BirdNET and return detection results."""
    print(f"Analyzing {wav_file}...")
    LAT = config["LAT"]
    LON = config["LON"]
    CHUNK_DURATION = config["CHUNK_DURATION"]
    BUFFER_SIZE = config["BUFFER_SIZE"]
    # Create a Recording instance from birdnetlib and analyze it
    recording = Recording(analyzer, wav_file, lat=LAT, lon=LON, min_conf=0.25)
    recording.analyze()
    return recording.detections

def update_ledger(detections, timestamp, config):
    """Update the ledger CSV with detection results from the analysis."""
    print("Updating ledger CSV with detection results...")
    LAT = config["LAT"]
    LON = config["LON"]
    CHUNK_DURATION = config["CHUNK_DURATION"]
    BUFFER_SIZE = config["BUFFER_SIZE"]
    LEDGER_FILE = config["LEDGER_FILE"]

    date_obj = datetime.fromtimestamp(timestamp)
    date_str = date_obj.strftime('%Y-%m-%d')
    start_time_str = date_obj.strftime('%H:%M:%S')
    end_time = date_obj + timedelta(seconds=CHUNK_DURATION * BUFFER_SIZE)
    end_time_str = end_time.strftime('%H:%M:%S')

    file_exists = os.path.isfile(LEDGER_FILE)
    with csv_lock, open(LEDGER_FILE, 'a', newline='') as csvfile:
        fieldnames = ["date", "start_Time", "end_Time", "lat", "lon", "label", "scientific_name", "confidence"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        # Write only one row per file (first valid detection) to avoid duplicates.
        for detection in detections:
            common_name = detection.get('common_name', '')
            scientific_name = detection.get('scientific_name', '')
            confidence = detection.get('confidence', '')
            writer.writerow({
                "date": date_str,
                "start_Time": start_time_str,
                "end_Time": end_time_str,
                "lat": LAT,
                "lon": LON,
                "label": common_name,
                "scientific_name": scientific_name,
                "confidence": confidence
            })
            # Stop after the first detection with a valid scientific name.
            if scientific_name:
                break

def process_wav_file(wav_file, analyzer, config):
    """Process an individual WAV file: analyze, update ledger, and delete the file."""
    print(f"Processing file: {wav_file}")
    # Attempt to extract the timestamp from the filename (expected format: YYYYmmdd_HHMMSS.wav)
    basename = os.path.basename(wav_file)
    try:
        dt = datetime.strptime(basename.replace(".wav", ""), '%Y%m%d_%H%M%S')
        timestamp = dt.timestamp()
    except Exception as e:
        print(f"Error parsing timestamp from filename {wav_file}: {e}")
        timestamp = time.time()
    detections = analyze_recording(analyzer, wav_file, config, timestamp)
    update_ledger(detections, timestamp, config)
    try:
        os.remove(wav_file)
        print(f"Deleted processed file {wav_file}")
    except Exception as e:
        print(f"Error deleting file {wav_file}: {e}")

def monitor_recordings_folder(analyzer, config):
    """Continuously monitor the recordings folder for new WAV files to process."""
    RECORDINGS_FOLDER = config["RECORDINGS_FOLDER"]
    processed_files = set()
    while True:
        files = [os.path.join(RECORDINGS_FOLDER, f) for f in os.listdir(RECORDINGS_FOLDER) if f.endswith(".wav")]
        for wav_file in files:
            if wav_file not in processed_files:
                process_wav_file(wav_file, analyzer, config)
                processed_files.add(wav_file)
        time.sleep(2)  # Polling interval in seconds

def main():
    config = load_config()
    # Ensure the BirdNET data stream folder exists (ledger CSV and images will be saved here)
    BIRDNET_DATA_STREAM_FOLDER = config["BIRDNET_DATA_STREAM_FOLDER"]
    if not os.path.exists(BIRDNET_DATA_STREAM_FOLDER):
        os.makedirs(BIRDNET_DATA_STREAM_FOLDER)
    # Load the BirdNET model (this might take a moment)
    print("Loading BirdNET model (this may take a moment)...")
    analyzer = Analyzer()
    print("BirdNET model loaded.")
    # Start the monitoring loop for new recordings
    monitor_recordings_folder(analyzer, config)

if __name__ == '__main__':
    main()
