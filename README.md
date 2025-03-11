# Digital-Ecology-Sensing-Network

**Author:** Dhanuj Gandikota

---

## Overview

The *Digital Ecology Sensing Network* is a modular sensing system prototype for ecological monitoring. It leverages networked sensing, multi-modal sensors, Docker containers for sensing models, on-device AI processing, and more. This project is being developed at the University of Texas at Austin Digital Ecology Lab and is designed to run on diverse hardware platforms including Raspberry Pi 5, mac M‑series, and Intel‑based devices.

---

## Purpose

This repository contains multiple Python modules that each run in separate Docker containers. They perform tasks such as:
- **Audio Recording:** Capturing audio from a selected microphone, buffering audio chunks, and saving recordings.
- **BirdNET Analysis:** Loading the BirdNET model to analyze recorded audio, updating a detection ledger (CSV), and cleaning up processed files.
- **Bird Image Demo:** Monitoring the detection ledger to fetch and save bird images from Wikimedia Commons when a new species is detected.
- **Dashboard:** Providing a web interface for monitoring system status, selecting modules to build and run, and even executing commands in an interactive terminal.

All modules share a single, consolidated configuration file (**config/module_config.yaml**) and use a common data folder (**local_data/**).

---

## Repository Structure

The repository is organized as follows:

```
.
├── README.md                                    # Repository instructions and details
├── config/                                      # User‑modifiable configuration files
│   └── module_config.yaml                       # Consolidated YAML config for global parameters, module selection/definitions
├── src/                                         # Main source code for the Dashboard
│   ├── dashboard/                               # Dashboard Interface Frontend
│   │   ├── dashboard_frontend/                     # Bundled React/JS/CSS for the dashboard interface
│   │   │   ├── index.html                              # Main HTML entry point
│   │   │   ├── main.js                                 # React/JS code (JSX, loaded via Babel)
│   │   │   └── styles.css                              # Custom CSS (Material-UI loaded via CDN)
│   │   ├── dashboard.py                            # Dashboard backend module (Flask)
│   │   └── Dockerfile.dashboard                    # Dockerfile for building the Dashboard container
│   ├── terminal/                                # Terminal Interface Frontend
│   │   ├── terminal.py                             # Terminal Frontend code for system (python/bash)
│   │   └── Dockerfile.terminal                     # Dockerfile for building the Terminal container 
│   └── sys_func/                               # Functions/Code for System to support Terminal or Dashboard Interface Startup
│       └── ...                                     # System Func Code
├── modules/                                    # Backend code for each module
│   ├── mac-M/                                      # Modules specifically for Mac M‑series devices
│   │   ├── audio_recording_mac/                        # Mac M-series audio recording module
│   │   │   ├── audio_recording_mac.py                      # Main Python code for audio recording on Mac
│   │   │   └── Dockerfile.audio_recording_mac              # Dockerfile for building the Mac audio recording container
│   │   ├── birdnet_analyzer_mac/                       # Mac M-series BirdNET analyzer module
│   │   │   ├── birdnet_analyzer_mac.py                     # Main Python code for BirdNET analysis on Mac
│   │   │   └── Dockerfile.birdnet_analyzer_mac             # Dockerfile for building the Mac BirdNET analyzer container
│   │   └── birdnet_image_demo_mac/                     # Mac M-series bird image demo module
│   │       ├── birdnet_image_demo_mac.py                   # Main Python code for bird image retrieval on Mac
│   │       └── Dockerfile.birdnet_image_demo_mac           # Dockerfile for building the Mac bird image demo container
│   └── pi/                                         # Modules specifically for Raspberry Pi devices
│       ├── audio_recording/                            # Pi audio recording module
│       │   ├── audio_recording.py                          # Main Python code for audio recording on Raspberry Pi
│       │   └── Dockerfile.audio_recording                  # Dockerfile for building the Pi audio recording container
│       ├── birdnet_analyzer/                           # Pi BirdNET analyzer module
│       │   ├── birdnet_analyzer.py                         # Main Python code for BirdNET analysis on Raspberry Pi
│       │   └── Dockerfile.birdnet_analyzer                 # Dockerfile for building the Pi BirdNET analyzer container
│       └── birdnet_image_demo/                         # Pi bird image demo module
│           ├── birdnet_image_demo.py                       # Main Python code for bird image retrieval on Raspberry Pi
│           └── Dockerfile.birdnet_image_demo               # Dockerfile for building the Pi bird image demo container
├── local_data/                                 # Shared data folder (recordings, CSV logs, images, etc.)
├── log/                                        # Logs and snapshots of Docker Compose commands
│   └── current-docker-compose.yml                  # Recreated compose file generated by the dashboard/terminal
├── .gitignore                                  # Git ignore file
└── docker-compose.yml                          # Docker Compose file for spinning up the Dashboard and Terminal container


```

---

## Prerequisites

### Docker & Docker Compose Installation

#### On Raspberry Pi (ARM-based systems)
1. **Install Docker:**
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   ```
   Then add your user to the Docker group:
   ```bash
   sudo usermod -aG docker ${USER}
   ```

2. **Install Docker Compose:**
   ```bash
   sudo apt-get update
   sudo apt-get install -y docker-compose
   ```
   Or download the latest version:
   ```bash
   sudo curl -L "https://github.com/docker/compose/releases/download/<VERSION>/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

#### On macOS (M‑series / Intel)
- **Install Docker Desktop for Mac:**  
  Download and install Docker Desktop from [Docker’s official site](https://www.docker.com/products/docker-desktop). Docker Compose is included.

---

## Downloading the Repository

Clone the repository to your local machine. For example:
```bash
git clone https://github.com/dhanujg/Digital-Ecology-Sensing-Network.git
cd Digital-Ecology-Sensing-Network
```

Ensure that all folders (`modules/`, `config/`, `module_dockerfiles/`, `dashboard_frontend/`, etc.) and the `local_data/` folder are present in the repository root.

---

## Building and Running the System

### Dashboard Container

The Dashboard is the central control module that:
- Serves a React-based web interface.
- Reads available modules from **config/module_config.yaml**.
- Generates and updates the effective Docker Compose file in **log/current-docker-compose.yml** based on user selections.
- Executes Docker Compose commands to build and run selected modules.

#### Step 1: Build the Dashboard Image
From the repository root, run:
```bash
docker-compose build
```

#### Step 2: Start the Dashboard Container
After building, start the container:
```bash
docker-compose up
```
For detached mode:
```bash
docker-compose up -d
```

### Non-Dashboard Modules

Individual modules (audio recording, BirdNET analyzer, bird image demo) are built via their own Dockerfiles (in **module_dockerfiles/** or **module_dockerfiles/mac-M/** for mac versions). They share the `local_data/` folder for data exchange.

When using the Dashboard to build or run modules, the Dashboard will generate a docker-compose file (stored in **log/current-docker-compose.yml**) and invoke Docker Compose commands accordingly.

---

## File Descriptions

### Python Modules

- **modules/audio_recording.py:**  
  *Purpose:* Records audio using selected microphone, buffers chunks, and saves recordings as WAV files (Raspberry Pi version).

- **modules/birdnet_analyzer.py:**  
  *Purpose:* Loads the BirdNET model, analyzes recorded WAV files, updates a ledger CSV, and cleans up processed files (Raspberry Pi version).

- **modules/birdnet_image_demo.py:**  
  *Purpose:* Monitors the ledger CSV for new detections and fetches bird images from Wikimedia Commons (Raspberry Pi version).

- **modules/dashboard.py:**  
  *Purpose:* Provides a Flask backend for the dashboard; reads configuration, exposes API endpoints for module management, executes Docker Compose commands, and logs the effective compose file.

- **modules/mac-M/audio_recording_mac.py:**  
  *Purpose:* Mac-specific audio recording module.

- **modules/mac-M/birdnet_analyzer_mac.py:**  
  *Purpose:* Mac-specific BirdNET analyzer module.

- **modules/mac-M/birdnet_image_demo_mac.py:**  
  *Purpose:* Mac-specific bird image demo module.

### Configuration File

- **config/module_config.yaml:**  
  *Purpose:* Consolidated YAML configuration file containing global parameters (buffer sizes, sample rates, folder paths, etc.) and module definitions (availability, main code file, Dockerfile location).

### Docker Files

- **module_dockerfiles/Dockerfile.audio_recording:**  
  *Purpose:* Builds the Docker image for the Raspberry Pi audio recording module.

- **module_dockerfiles/Dockerfile.birdnet_analyzer:**  
  *Purpose:* Builds the Docker image for the Raspberry Pi BirdNET analyzer module.

- **module_dockerfiles/Dockerfile.birdnet_image_demo:**  
  *Purpose:* Builds the Docker image for the Raspberry Pi bird image demo module.

- **module_dockerfiles/mac-M/Dockerfile.audio_recording_mac:**  
  *Purpose:* Builds the Docker image for the Mac audio recording module.

- **module_dockerfiles/mac-M/Dockerfile.birdnet_analyzer_mac:**  
  *Purpose:* Builds the Docker image for the Mac BirdNET analyzer module.

- **module_dockerfiles/mac-M/Dockerfile.birdnet_image_demo_mac:**  
  *Purpose:* Builds the Docker image for the Mac bird image demo module.

- **docker-compose.yml:**  
  *Purpose:* Orchestrates the Dashboard container. The Dashboard then manages building/running of other modules based on user selections.

### Frontend Files (Dashboard)

- **dashboard_frontend/index.html:**  
  *Purpose:* Main HTML page for the dashboard.

- **dashboard_frontend/main.js:**  
  *Purpose:* React/JavaScript code implementing a 3×3 grid dashboard with Material-UI components, module selection, build/run actions, and terminal integration.

- **dashboard_frontend/styles.css:**  
  *Purpose:* Custom CSS styling for the dashboard interface.

### Shared Data and Logs

- **local_data/**  
  *Purpose:* Shared folder for storing recordings, ledger CSV files, images, etc.

- **log/**  
  *Purpose:* Folder for logging Docker Compose command outputs and storing the current effective compose file (**current-docker-compose.yml**).

---

## Additional Notes

- **Unified Configuration:**  
  All modules use **config/module_config.yaml** for configuration. Global parameters and module-specific settings (such as available status and file paths) are defined here.

- **Local Data Sharing:**  
  The `local_data/` folder is mounted into all containers via Docker volumes to ensure consistent data access across modules.

- **Cross-Platform Compatibility:**  
  The Dockerfiles and code have been updated to support Raspberry Pi (ARM64), mac M‑series, and Intel‑based systems. The Dashboard container (and its Docker Compose file) is designed to run on all target platforms.

- **Dashboard Module Management:**  
  The dashboard reads the available modules from the configuration file and displays them for selection. Based on user choices, it generates a Docker Compose snippet that is saved in **log/current-docker-compose.yml** and uses that file to execute `docker-compose build` and `docker-compose up -d` commands.

- **Terminal Integration:**  
  The dashboard includes a basic interactive terminal stub (with commented code for integrating a fully interactive terminal using xterm.js) that allows execution of commands inside running containers.


