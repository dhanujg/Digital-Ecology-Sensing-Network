# Digital-Ecology-Sensing-Network


**Author:** Dhanuj Gandikota

---

## Overview

The *Digital Ecology Sensing Network* is a modular sensing system prototype for Raspberry Pi ecological sensing. It leverages networked sensing, multi-modal sensors, Docker containers for sensing models, on-device AI processing, and more. This project is being developed in the University of Texas at Austin Digital Ecology Lab.

---

## Purpose

This repository contains three Python modules that operate as separate Docker containers:
- **Audio Recording Module:** Captures audio from a selected microphone, buffers chunks, and saves recordings.
- **BirdNET Analyzer Module:** Loads a BirdNET model, analyzes new audio recordings, updates a detection ledger, and cleans up processed files.
- **BirdNET Image Demo Module:** Monitors the detection ledger and fetches corresponding bird images from Wikimedia Commons when a new species is detected.

All modules share a common configuration (in `config.json`) and interact with a shared `local_data/` folder.

---

## Prerequisites: Installing Docker & Docker Compose on Raspberry Pi

### 1. Install Docker

Run the following commands on your Raspberry Pi (this script automatically detects the ARM architecture):

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

After installation, add your user to the Docker group (log out and back in to apply changes):

```bash
sudo usermod -aG docker ${USER}
```

### 2. Install Docker Compose

Install Docker Compose using the official Docker Compose installation script:

```bash
sudo apt-get update
sudo apt-get install -y docker-compose
```

Alternatively, for the latest version on ARM devices, you might use:

```bash
sudo curl -L "https://github.com/docker/compose/releases/download/<VERSION>/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

Replace `<VERSION>` with the desired version number (e.g., `1.29.2`).

---

## Downloading the Repository

Clone the repository onto your Raspberry Pi (insert your repo URL where indicated):

```bash
git clone https://github.com/dhanujg/Digital-Ecology-Sensing-Network.git
cd Digital-Ecology-Sensing-Network
```

Ensure that all files (Python modules, Dockerfiles, `config.json`) and the `local_data/` folder are in the repository’s root.

---

## Building and Running with Docker Compose

### Building and then running

Below is an updated section of the README that separates the Docker Compose build and run commands:


#### Step 1: Build the Docker Images
From the repository root, run:
```bash
docker-compose build
```

#### Step 2: Start the Containers
After the build completes, start the containers with:
```bash
docker-compose up
```
Alternatively, if you prefer to run in detached mode:
```bash
docker-compose up -d
```

These instructions ensure that you first build the images and then run them as separate steps.

#### Building and Running all at once

From the repository root, run the following command to build and launch all three containers simultaneously:

```bash
docker-compose up --build
```

This command will build the Docker images for:
- The Audio Recording Module
- The BirdNET Analyzer Module
- The BirdNET Image Demo Module

All containers share the `local_data/` folder, ensuring that audio recordings, ledger CSV files, and images are accessible across modules.

---

## File Descriptions

Below is a brief three-word description for each file in the repository:

### Python Files
- **audio_recording.py:**  
  **Description:** Identifies audio devices, allows microphone selection, records buffered audio chunks, and saves them as WAV files.

- **birdnet_analyzer.py:**    
  **Description:** Loads the BirdNET model, monitors recordings, processes WAV files, updates a ledger CSV with detection data, and deletes processed files.

- **birdnet_image_demo.py:**   
  **Description:** Checks for internet connectivity, monitors the ledger CSV for new detections, and fetches and saves bird images from Wikimedia Commons.

### Configuration File
- **config.json:**   
  **Description:** Contains shared configuration parameters such as buffer sizes, sample rate, folder paths, and geographic coordinates. (Annotated with extra comments in the `_comments` section.)

### Docker Files
- **Dockerfile.audio_recording:**   
  **Description:** Builds a Docker image for the audio recording module, installs dependencies (including audio libraries), and runs `audio_recording.py`.

- **Dockerfile.birdnet_analyzer:**   
  **Description:** Builds a Docker image for the BirdNET analyzer module, installs necessary libraries, and runs `birdnet_analyzer.py`.

- **Dockerfile.birdnet_image_demo:**  
  **Description:** Builds a Docker image for the bird image demo module, installs required packages, and runs `birdnet_image_demo.py`.

- **docker-compose.yml:**   
  **Description:** Orchestrates the three Docker containers, ensuring they share the `local_data/` folder and providing necessary device access (e.g., audio hardware) for the recording module.

---

## Additional Notes

- **Local Data Sharing:**  
  All modules share the `local_data/` folder via Docker volumes. Ensure that the folder exists in your repository root and is accessible by all containers.

- **Raspberry Pi Considerations:**  
  The Dockerfiles use ARM64 base images (e.g., `arm64v8/python:3.9-slim`) compatible with the Raspberry Pi 5. The audio container runs in privileged mode and mounts `/dev/snd` to access the sound hardware.

- **Troubleshooting:**  
  If you experience issues with device permissions or volume mounts, check your Docker configuration and ensure that your user has appropriate permissions.

---

Happy sensing!
