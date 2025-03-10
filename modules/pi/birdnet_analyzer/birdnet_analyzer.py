"""
BirdNET Analyzer Module (Raspberry Pi)
----------------------------------------
This module loads the BirdNET model, monitors the recordings folder for new WAV files,
analyzes each recording, updates the ledger CSV with detection results, and deletes processed files.
"""

import os
import time
import csv
from datetime import datetime, timedelta
from threading import Lock
from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer
import yaml

csv_lock = Lock()

def load_config():
    # Load configuration from config/module_config.yaml
    with open("config/module_config.yaml", "r") as f:
        return yaml.safe_load(f)

def analyze_recording(analyzer, wav_file, config, timestamp):
    print(f"Analyzing {wav_file}...")
    LAT = config["global"]["LAT"]
    LON = config["global"]["LON"]
    recording = Recording(analyzer, wav_file, lat=LAT, lon=LON, min_conf=0.25)
    recording.analyze()
    return recording.detections

def update_ledger(detections, timestamp, config):
    print("Updating ledger...")
    LAT = config["global"]["LAT"]
    LON = config["global"]["LON"]
    CHUNK_DURATION = config["global"]["CHUNK_DURATION"]
    BUFFER_SIZE = config["global"]["BUFFER_SIZE"]
    LEDGER_FILE = config["global"]["LEDGER_FILE"]

    dt = datetime.fromtimestamp(timestamp)
    date_str = dt.strftime('%Y-%m-%d')
    start_time_str = dt.strftime('%H:%M:%S')
    end_time_str = (dt + timedelta(seconds=CHUNK_DURATION * BUFFER_SIZE)).strftime('%H:%M:%S')
    file_exists = os.path.isfile(LEDGER_FILE)
    with csv_lock, open(LEDGER_FILE, 'a', newline='') as csvfile:
        fieldnames = ["date", "start_Time", "end_Time", "lat", "lon", "label", "scientific_name", "confidence"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        for detection in detections:
            writer.writerow({
                "date": date_str,
                "start_Time": start_time_str,
                "end_Time": end_time_str,
                "lat": LAT,
                "lon": LON,
                "label": detection.get('common_name', ''),
                "scientific_name": detection.get('scientific_name', ''),
                "confidence": detection.get('confidence', '')
            })
            # Stop after the first valid detection.
            if detection.get('scientific_name', ''):
                break

def process_wav_file(wav_file, analyzer, config):
    print(f"Processing file: {wav_file}")
    basename = os.path.basename(wav_file)
    try:
        dt = datetime.strptime(basename.replace(".wav", ""), '%Y%m%d_%H%M%S')
        timestamp = dt.timestamp()
    except Exception as e:
        print(f"Error parsing timestamp from {wav_file}: {e}")
        timestamp = time.time()
    detections = analyze_recording(analyzer, wav_file, config, timestamp)
    update_ledger(detections, timestamp, config)
    try:
        os.remove(wav_file)
        print(f"Deleted processed file {wav_file}")
    except Exception as e:
        print(f"Error deleting {wav_file}: {e}")

def monitor_recordings_folder(analyzer, config):
    RECORDINGS_FOLDER = config["global"]["RECORDINGS_FOLDER"]
    processed_files = set()
    while True:
        files = [os.path.join(RECORDINGS_FOLDER, f) for f in os.listdir(RECORDINGS_FOLDER) if f.endswith(".wav")]
        for wav_file in files:
            if wav_file not in processed_files:
                process_wav_file(wav_file, analyzer, config)
                processed_files.add(wav_file)
        time.sleep(2)

def main():
    config = load_config()
    BIRDNET_DATA_STREAM_FOLDER = config["global"]["BIRDNET_DATA_STREAM_FOLDER"]
    if not os.path.exists(BIRDNET_DATA_STREAM_FOLDER):
        os.makedirs(BIRDNET_DATA_STREAM_FOLDER)
    print("Loading BirdNET model (this may take a moment)...")
    analyzer = Analyzer()
    print("BirdNET model loaded.")
    monitor_recordings_folder(analyzer, config)

if __name__ == '__main__':
    main()
