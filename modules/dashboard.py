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
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder="../dashboard_frontend", static_url_path="")
CORS(app)  # Enable CORS if needed for local development

CONFIG_PATH = "config/module_config.yaml"
LOG_DIR = "log"
CURRENT_COMPOSE_FILE = os.path.join(LOG_DIR, "current-docker-compose.yml")

def load_config():
    """Load the consolidated configuration from config/module_config.yaml."""
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
                # Additional service configuration can be added here as needed.
                "restart": "always"
            }
    compose_dict = {
        "version": "3.8",
        "services": services
    }
    return compose_dict

def write_compose_file(compose_dict):
    """Write the given docker-compose configuration to the current-docker-compose.yml file in the log folder."""
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
            # Return only the module name and its main code filename for display.
            available[mod_name] = mod_data.get("main_code_fname", "")
    return jsonify(available)

@app.route("/api/build", methods=["POST"])
def build_modules():
    """
    Build selected modules.
    Expects JSON payload: { "modules": [ "audio_recording", "birdnet_analyzer", ... ] }
    Generates the effective docker-compose file, writes it to log/current-docker-compose.yml,
    and executes the build command asynchronously.
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
            # For simplicity, we just log the output.
            with open(os.path.join(LOG_DIR, f"build_log_{int(time.time())}.txt"), "w") as log_file:
                log_file.write("Command: " + " ".join(build_cmd) + "\n")
                log_file.write(stdout + "\n" + stderr)
        except Exception as e:
            print(f"Build error: {e}")

    threading.Thread(target=run_build).start()
    return jsonify({"message": "Build started", "compose": compose_config})

@app.route("/api/run", methods=["POST"])
def run_modules():
    """
    Run selected modules.
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
        # Optionally log the output.
        with open(os.path.join(LOG_DIR, f"run_log_{int(time.time())}.txt"), "w") as log_file:
            log_file.write("Command: " + " ".join(run_cmd) + "\n")
            log_file.write(output)
        return jsonify({"message": "Run command executed", "output": output})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/module-status", methods=["GET"])
def module_status():
    """
    Check and return the status of running containers.
    This uses 'docker-compose ps' on the current docker-compose file.
    """
    try:
        status_cmd = ["docker-compose", "-f", CURRENT_COMPOSE_FILE, "ps"]
        result = subprocess.check_output(status_cmd, stderr=subprocess.STDOUT, universal_newlines=True)
        return jsonify({"modules": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Terminal endpoints are stubbed out; for full interactive terminal integration, consider Flask-SocketIO.
@app.route("/api/terminal/<module>", methods=["GET", "POST"])
def terminal(module):
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

# Serve static files for the dashboard frontend
@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(app.static_folder, path)

if __name__ == "__main__":
    # Run the Flask server on port 5000, accessible to all interfaces.
    app.run(host="0.0.0.0", port=5000, debug=True)
