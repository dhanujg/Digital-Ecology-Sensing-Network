"""
Audio Recording Module - Mac Version
--------------------------------------
This module identifies available audio devices, allows the user to select a microphone,
records audio chunks, and saves the recordings into the configured recordings data folder.
This version is adapted for testing on a Mac (M series chip).
"""

import os
import time
import wave
from datetime import datetime
import numpy as np
import sounddevice as sd

def load_config():
    # Load configuration from YAML file in the config folder
    import yaml
    with open("config/module_config.yaml", "r") as f:
        return yaml.safe_load(f)

def record_audio(duration, sample_rate, channels, device=None):
    print(f"Recording audio for {duration} seconds on device {device}...")
    recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=channels, dtype='int16', device=device)
    sd.wait()
    return recording

def save_wav_file(filename, data, sample_rate, channels):
    print(f"Saving WAV file to {filename}...")
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)  # 16 bits = 2 bytes
        wf.setframerate(sample_rate)
        wf.writeframes(data.tobytes())

def main():
    config = load_config()
    BUFFER_SIZE = config["BUFFER_SIZE"]
    CHUNK_DURATION = config["CHUNK_DURATION"]
    SAMPLE_RATE = config["SAMPLE_RATE"]
    CHANNELS = config["CHANNELS"]
    RECORDINGS_FOLDER = config["RECORDINGS_FOLDER"]

    if not os.path.exists(RECORDINGS_FOLDER):
        os.makedirs(RECORDINGS_FOLDER)

    # List available audio devices
    devices = sd.query_devices()
    print("Available audio devices:")
    for idx, device in enumerate(devices):
        print(f"{idx}: {device['name']} (In: {device['max_input_channels']}, Out: {device['max_output_channels']})")
    device_index = int(input("Enter the device index for your microphone: "))

    audio_buffer = []
    timestamps = []

    while True:
        chunk = record_audio(CHUNK_DURATION, SAMPLE_RATE, CHANNELS, device=device_index)
        timestamp = time.time()
        audio_buffer.append(chunk)
        timestamps.append(timestamp)
        if len(audio_buffer) > BUFFER_SIZE:
            audio_buffer.pop(0)
            timestamps.pop(0)
        if len(audio_buffer) == BUFFER_SIZE:
            combined_audio = np.concatenate(audio_buffer)
            dt = datetime.fromtimestamp(timestamps[0])
            filename = dt.strftime('%Y%m%d_%H%M%S.wav')
            filepath = os.path.join(RECORDINGS_FOLDER, filename)
            save_wav_file(filepath, combined_audio, SAMPLE_RATE, CHANNELS)

if __name__ == '__main__':
    main()
