"""
Dashboard Backend Module
--------------------------
This Flask application serves the dashboard’s API endpoints and static frontend.
It loads configuration from config/module_config.yaml, exposes available module definitions,
and executes Docker Compose build/run commands based on the user’s selection.
It also recreates and writes the effective docker-compose file to log/current-docker-compose.yml.

Compatible with Raspberry Pi 5, mac M‑series, and Intel-based systems.
"""

import os
import time
import subprocess
import threading
import yaml
from flask import Flask, request, jsonify
from flask_cors import CORS

# --- 1) Set the BASE_DIR as the /app folder.
BASE_DIR = os.getcwd()

# --- 2) Compute the absolute path to the dashboard_frontend folder, config file, and logs.
STATIC_FOLDER = os.path.join(BASE_DIR, "dashboard_frontend")
CONFIG_PATH = os.path.join(BASE_DIR, "config", "module_config.yaml")
LOG_DIR = os.path.join(BASE_DIR, "log")
CURRENT_COMPOSE_FILE = os.path.join(LOG_DIR, "current-docker-compose.yml")

# Create the Flask app with the computed static folder.
app = Flask(__name__, static_folder=STATIC_FOLDER, static_url_path="")
CORS(app)  # Enable CORS if needed for local development

def load_config():
    """Load the consolidated configuration from the config/module_config.yaml file."""
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)

def generate_compose(selected_modules, config):
    """
    Generate a minimal docker-compose snippet based on the user's selected modules.
    It uses the dockerfile_fname and main_code_fname values from the config.
    """
    services = {}
    modules_config = config.get("modules", {})
    for mod_name in selected_modules:
        mod_config = modules_config.get(mod_name, {})
        # Only include modules that are marked as available.
        if mod_config.get("available", False):
            services[mod_name] = {
                "build": {
                    "context": ".",
                    "dockerfile": mod_config.get("dockerfile_fname")
                },
                "restart": "always"
            }
    compose_dict = {
        "version": "3.8",
        "services": services
    }
    return compose_dict

def write_compose_file(compose_dict):
    """Write the docker-compose configuration to log/current-docker-compose.yml."""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    with open(CURRENT_COMPOSE_FILE, "w") as f:
        yaml.dump(compose_dict, f, default_flow_style=False)

@app.route("/api/available-modules", methods=["GET"])
def available_modules():
    """Return a list of available modules from the configuration."""
    config = load_config()
    modules_config = config.get("modules", {})
    available = {}
    for mod_name, mod_data in modules_config.items():
        if mod_data.get("available", False):
            available[mod_name] = mod_data.get("main_code_fname", "")
    return jsonify(available)

@app.route("/api/build", methods=["POST"])
def build_modules():
    """
    Build the selected modules.
    Expects JSON payload: { "modules": [ "audio_recording", "birdnet_analyzer", ... ] }
    Generates the effective docker-compose file, writes it to log/current-docker-compose.yml,
    and executes docker-compose build asynchronously.
    """
    data = request.get_json()
    selected_modules = data.get("modules", [])
    config = load_config()
    compose_config = generate_compose(selected_modules, config)
    write_compose_file(compose_config)

    build_cmd = ["docker-compose", "-f", CURRENT_COMPOSE_FILE, "build"] + selected_modules

    def run_build():
        try:
            proc = subprocess.Popen(build_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            stdout, stderr = proc.communicate()
            # Log the build output
            timestamp = int(time.time())
            with open(os.path.join(LOG_DIR, f"build_log_{timestamp}.txt"), "w") as log_file:
                log_file.write("Command: " + " ".join(build_cmd) + "\n")
                log_file.write(stdout + "\n" + stderr)
        except Exception as e:
            print(f"Build error: {e}")

    threading.Thread(target=run_build).start()
    return jsonify({"message": "Build started", "compose": compose_config})

@app.route("/api/run", methods=["POST"])
def run_modules():
    """
    Run the selected modules.
    Expects JSON payload: { "modules": [ "audio_recording", "birdnet_analyzer", ... ] }
    Uses the generated docker-compose file from log/current-docker-compose.yml and executes 'docker-compose up -d'.
    """
    data = request.get_json()
    selected_modules = data.get("modules", [])
    config = load_config()
    compose_config = generate_compose(selected_modules, config)
    write_compose_file(compose_config)

    run_cmd = ["docker-compose", "-f", CURRENT_COMPOSE_FILE, "up", "-d"] + selected_modules
    try:
        proc = subprocess.Popen(run_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        stdout, stderr = proc.communicate()
        output = stdout + "\n" + stderr

        timestamp = int(time.time())
        with open(os.path.join(LOG_DIR, f"run_log_{timestamp}.txt"), "w") as log_file:
            log_file.write("Command: " + " ".join(run_cmd) + "\n")
            log_file.write(output)

        return jsonify({"message": "Run command executed", "output": output})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/module-status", methods=["GET"])
def module_status():
    """
    Check and return the status of running containers.
    This calls 'docker-compose ps' on the current docker-compose file in log/.
    """
    try:
        status_cmd = ["docker-compose", "-f", CURRENT_COMPOSE_FILE, "ps"]
        result = subprocess.check_output(status_cmd, stderr=subprocess.STDOUT, universal_newlines=True)
        return jsonify({"modules": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/terminal/<module>", methods=["GET", "POST"])
def terminal(module):
    """
    Provides a stubbed-out terminal integration.
    GET: returns a placeholder message
    POST: runs 'docker exec <module> bash -c "<command>"'
    """
    if request.method == "GET":
        return jsonify({"message": "Terminal streaming not implemented. Use websockets integration."})
    else:
        data = request.get_json()
        command = data.get("command", "")
        exec_cmd = ["docker", "exec", module, "bash", "-c", command]
        try:
            proc = subprocess.Popen(exec_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            stdout, stderr = proc.communicate()
            output = stdout + "\n" + stderr
            return jsonify({"output": output})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@app.route("/")
def index():
    """
    Serve index.html from the computed static folder.
    """
    return app.send_static_file("index.html")

if __name__ == "__main__":
    # Listen on port 5001; the host port is mapped in docker-compose.yml
    print("Dashboard Working Directory: " + BASE_DIR)
    app.run(host="0.0.0.0", port=5001, debug=True)
