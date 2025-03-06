"""
Audio Recording Module
------------------------
Objective:
- Identify available audio devices and allow the user to select the desired microphone.
- Continuously record audio chunks (each of CHUNK_DURATION seconds) and combine a configurable number (BUFFER_SIZE) of chunks.
- Save the combined audio as a WAV file in the recordings folder specified in the config.

Usage:
Run this file to start recording audio. The recorded WAV files are saved in the configured recordings folder.
"""

import os
import time
import wave
import json
from datetime import datetime
import numpy as np
import sounddevice as sd

def load_config():
    """Load configuration values from the yaml config file."""
    import yaml
    with open("config/module_config.yaml", "r") as f:
        return yaml.safe_load(f)

def record_audio(duration, sample_rate, channels, device=None):
    """Record audio for the specified duration and return the NumPy array data."""
    print(f"Recording audio for {duration} seconds on device {device}...")
    recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=channels, dtype='int16', device=device)
    sd.wait()
    return recording

def save_wav_file(filename, data, sample_rate, channels):
    """Save the NumPy array data as a WAV file with the given sample rate and channel count."""
    print(f"Saving WAV file to {filename}...")
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)  # 16 bits = 2 bytes
        wf.setframerate(sample_rate)
        wf.writeframes(data.tobytes())

def main():
    config = load_config()
    # Get configuration parameters
    BUFFER_SIZE = config["BUFFER_SIZE"]
    CHUNK_DURATION = config["CHUNK_DURATION"]
    SAMPLE_RATE = config["SAMPLE_RATE"]
    CHANNELS = config["CHANNELS"]
    RECORDINGS_FOLDER = config["RECORDINGS_FOLDER"]

    # Ensure recordings folder exists
    if not os.path.exists(RECORDINGS_FOLDER):
        os.makedirs(RECORDINGS_FOLDER)

    # Optionally clear existing WAV files in the recordings folder
    clear_choice = input("Do you want to delete existing WAV files in the recordings folder? (y/n): ").strip().lower()
    if clear_choice == 'y':
        for file in os.listdir(RECORDINGS_FOLDER):
            if file.endswith(".wav"):
                try:
                    os.remove(os.path.join(RECORDINGS_FOLDER, file))
                    print(f"Deleted {file}")
                except Exception as e:
                    print(f"Error deleting {file}: {e}")
    else:
        print("Existing files will be kept.")

    # List available audio devices and allow user to select one
    devices = sd.query_devices()
    print("Available audio devices:")
    for idx, device in enumerate(devices):
        print(f"{idx}: {device['name']} (Input channels: {device['max_input_channels']}, Output channels: {device['max_output_channels']})")
    device_index = int(input("Enter the device index for your microphone: "))

    audio_buffer = []
    timestamps = []

    # Main loop: continuously record audio chunks and save when BUFFER_SIZE is reached
    while True:
        chunk = record_audio(CHUNK_DURATION, SAMPLE_RATE, CHANNELS, device=device_index)
        timestamp = time.time()
        audio_buffer.append(chunk)
        timestamps.append(timestamp)
        # Keep only the last BUFFER_SIZE chunks in the buffer
        if len(audio_buffer) > BUFFER_SIZE:
            audio_buffer.pop(0)
            timestamps.pop(0)
        # Once enough chunks are collected, combine and save as one WAV file
        if len(audio_buffer) == BUFFER_SIZE:
            combined_audio = np.concatenate(audio_buffer)
            start_timestamp = timestamps[0]
            dt = datetime.fromtimestamp(start_timestamp)
            filename = dt.strftime('%Y%m%d_%H%M%S.wav')
            filepath = os.path.join(RECORDINGS_FOLDER, filename)
            save_wav_file(filepath, combined_audio, SAMPLE_RATE, CHANNELS)
            # The buffer remains rolling so that overlapping recordings may be processed

if __name__ == '__main__':
    main()
