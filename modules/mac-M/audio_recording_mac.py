"""
Audio Recording Module - Mac Version
--------------------------------------
This module (for Mac M series) records audio using a selected microphone,
buffers chunks, and saves the combined audio as a WAV file in the folder defined in the config.
"""

import os
import time
import wave
from datetime import datetime
import numpy as np
import sounddevice as sd
import yaml

def load_config():
    # Load configuration from config/module_config.yaml
    with open("config/module_config.yaml", "r") as f:
        return yaml.safe_load(f)

def record_audio(duration, sample_rate, channels, device=None):
    print(f"Recording audio for {duration} seconds on device {device}...")
    recording = sd.rec(int(duration * sample_rate),
                       samplerate=sample_rate,
                       channels=channels,
                       dtype='int16',
                       device=device)
    sd.wait()
    return recording

def save_wav_file(filename, data, sample_rate, channels):
    print(f"Saving WAV file to {filename}...")
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(data.tobytes())

def main():
    config = load_config()
    BUFFER_SIZE = config["global"]["BUFFER_SIZE"]
    CHUNK_DURATION = config["global"]["CHUNK_DURATION"]
    SAMPLE_RATE = config["global"]["SAMPLE_RATE"]
    CHANNELS = config["global"]["CHANNELS"]
    RECORDINGS_FOLDER = config["global"]["RECORDINGS_FOLDER"]

    if not os.path.exists(RECORDINGS_FOLDER):
        os.makedirs(RECORDINGS_FOLDER)

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
