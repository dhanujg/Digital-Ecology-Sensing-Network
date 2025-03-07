"""
Dashboard Module (Flask Backend)
----------------------------------
This module provides API endpoints for controlling and monitoring the sensing modules.
It serves a bundled React/JavaScript frontend (from the dashboard_frontend folder)
and executes Docker Compose commands to build and run selected modules.
All Docker Compose command outputs are logged to the log/ folder.
"""

from flask import Flask, request, jsonify, send_from_directory
import subprocess
import threading
import os
import time
import yaml
from flask_cors import CORS

app = Flask(__name__, static_folder="../dashboard_frontend", static_url_path="")
CORS(app)  # Enable cross-origin requests if needed

# Global state variables
build_status = {"last_built": None, "build_in_progress": False}
# module_status will store module status information (updated via polling)
module_status = {}

# Helper function to log executed Docker Compose commands and their outputs
def log_command(command, output):
    log_dir = "../log"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    log_file = os.path.join(log_dir, f"current-docker-compose-{timestamp}.yml")
    with open(log_file, "w") as f:
        f.write(f"Command: {command}\n")
        f.write(output)

# API endpoint: GET /api/status
@app.route("/api/status", methods=["GET"])
def get_status():
    # For now, simply return a default status. Could be extended.
    return jsonify({"status": "Not Running"})

# API endpoint: GET /api/module-status
@app.route("/api/module-status", methods=["GET"])
def get_module_status():
    try:
        # Execute "docker-compose ps" to retrieve container statuses.
        # This is a lightweight method to check running modules.
        result = subprocess.check_output(
            ["docker-compose", "ps"],
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        # For demo purposes, we simply return the raw output.
        return jsonify({"modules": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API endpoint: POST /api/build
@app.route("/api/build", methods=["POST"])
def build_modules():
    global build_status
    if build_status["build_in_progress"]:
        return jsonify({"message": "Build already in progress"}), 400
    data = request.get_json()
    modules = data.get("modules", [])
    # Construct the docker-compose build command for the selected modules
    cmd = ["docker-compose", "build"] + modules

    def run_build():
        global build_status
        build_status["build_in_progress"] = True
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            stdout, stderr = proc.communicate()
            output = stdout + "\n" + stderr
            log_command(" ".join(cmd), output)
            build_status["last_built"] = time.strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            build_status["last_built"] = f"Error: {str(e)}"
        finally:
            build_status["build_in_progress"] = False

    threading.Thread(target=run_build).start()
    return jsonify({"message": "Build started"})

# API endpoint: GET /api/build-status
@app.route("/api/build-status", methods=["GET"])
def get_build_status():
    return jsonify(build_status)

# API endpoint: POST /api/run
@app.route("/api/run", methods=["POST"])
def run_modules():
    data = request.get_json()
    modules = data.get("modules", [])
    # Construct the docker-compose up command for the selected modules (detached mode)
    cmd = ["docker-compose", "up", "-d"] + modules
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        stdout, stderr = proc.communicate()
        output = stdout + "\n" + stderr
        log_command(" ".join(cmd), output)
        return jsonify({"message": "Run command executed", "output": output})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API endpoint: Terminal integration (stub)
@app.route("/api/terminal/<module>", methods=["GET", "POST"])
def terminal(module):
    if request.method == "GET":
        # For full interactive terminal integration, use websockets (e.g., with Flask-SocketIO).
        # Here we return a dummy response.
        return jsonify({"message": "Terminal streaming not implemented. Use websockets integration."})
    else:
        # Execute a command in the specified container using docker exec
        data = request.get_json()
        cmd_input = data.get("command", "")
        # Example: docker exec <module> bash -c "<cmd_input>"
        cmd = ["docker", "exec", module, "bash", "-c", cmd_input]
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            stdout, stderr = proc.communicate()
            output = stdout + "\n" + stderr
            # In a full implementation, stream this output back in real time.
            return jsonify({"output": output})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

# Serve static files (index.html, main.js, styles.css, etc.) from the dashboard_frontend folder.
@app.route("/<path:path>")
def static_proxy(path):
    return send_from_directory(app.static_folder, path)

if __name__ == "__main__":
    # Start the Flask app on port 5000
    app.run(host="0.0.0.0", port=5000, debug=True)
