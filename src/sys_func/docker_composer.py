"""
docker_composer.py
--------------------
This file resides in the 'sys_func' folder and provides two functions for dynamically
building and running a Docker Compose file based on the machine type and module usage
specified in ./config/module_config.yaml.

It can:
1) Generate a docker-compose.yml file in ./log/ if a module's system_type matches the
   MACHINE_TYPE, and if 'available' and 'using' are true in the config.
2) Update a JSON status file (system_status_var.json) in ./log/ with build/run timestamps.
3) Append log messages to system_interface_log.txt in ./log/ for each step.

Usage:
  from docker_composer import build_docker_compose, run_docker_compose
  build_docker_compose()
  run_docker_compose()
"""

import os
import yaml
import json
import datetime
import subprocess
import threading

def build_docker_compose():
    """
    1) Reads ./config/module_config.yaml to get MACHINE_TYPE and modules data.
    2) Dynamically creates a docker-compose file (docker-compose.generated.yml) in ./log/
       for each module that matches:
         - system_type == MACHINE_TYPE
         - available == true
         - using == true
    3) Updates/creates ./log/system_status_var.json with:
         docker-compose_build -> true
         docker-compose_build_date -> current date/time
         docker-compose_run -> false
         docker-compose_run_date -> 'NOT RUN'
    4) Prints each step to terminal and appends them to ./log/system_interface_log.txt
    """

    # Paths (assuming this file is in src/sys_func/)
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    #base_dir = os.getcwd()
    
    # Define paths for config, log, and compose file.
    config_path = os.path.join(base_dir, "config", "module_config.yaml")
    log_dir = os.path.join(base_dir, "log")
    compose_file_path = os.path.join(log_dir, "docker-compose.generated.yml")
    status_file_path = os.path.join(log_dir, "system_status_var.json")
    interface_log_path = os.path.join(log_dir, "system_interface_log.txt")
    
    # Ensure the log directory exists.
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        print(f"[{current_time()}] Created log directory at {log_dir}")
    
    # Step (a): Read in the configuration file.
    with open(config_path, "r") as f:
        config_data = yaml.safe_load(f)
    print(f"[{current_time()}] Loaded configuration from {config_path}")
    
    # Step (b): Get MACHINE_TYPE from the global config.
    machine_type = config_data["global"].get("MACHINE_TYPE", "")
    print(f"[{current_time()}] MACHINE_TYPE from config: {machine_type}")
    
    # Step (c): Determine BASE_IMAGE based on MACHINE_TYPE.
    if machine_type.lower() == "pi":
        base_image = "arm64v8/python:3.9-slim"
    elif machine_type.lower() == "mac-m":
        base_image = "python:3.9-slim"
    else:
        base_image = "python:3.9-slim"  # Default fallback.
    print(f"[{current_time()}] Using BASE_IMAGE: {base_image}")
    
    # Step (d): Build the docker-compose dictionary.
    docker_compose_dict = {
        "version": "3.8",
        "services": {}
    }
    
    modules_data = config_data.get("modules", {})
    included_modules = []
    
    for module_name, module_info in modules_data.items():
        sys_type = module_info.get("system_type", "")
        available = module_info.get("available", False)
        using = module_info.get("using", False)
        dockerfile_fname = module_info.get("dockerfile_fname", "")
        
        # Only add the module if the system_type matches MACHINE_TYPE and it is available and in use.
        if sys_type.lower() == machine_type.lower() and available and using:
            included_modules.append(module_name)
            docker_compose_dict["services"][module_name] = {
                "build": {
                    "context": ".",
                    "dockerfile": dockerfile_fname,
                    "args": {
                        "BASE_IMAGE": base_image
                    }
                },
                "volumes": [
                    "./local_data:/app/local_data",
                    "./log:/app/log"
                ],
                "restart": "always"
            }
            print(f"[{current_time()}] Including module: {module_name}")
    
    # Step (e): Write out the generated docker-compose file.
    with open(compose_file_path, "w") as f:
        yaml.dump(docker_compose_dict, f, default_flow_style=False)
    print(f"[{current_time()}] Generated docker-compose file at {compose_file_path}")
    
    # Step (f): Update system_status_var.json.
    now_str = current_time()
    status_data = {
        "docker-compose_build": True,
        "docker-compose_build_date": now_str,
        "docker-compose_run": False,
        "docker-compose_run_date": "NOT RUN"
    }
    with open(status_file_path, "w") as sf:
        json.dump(status_data, sf, indent=2)
    print(f"[{current_time()}] Updated system status in {status_file_path}")
    
    # Step (g): Print statements and append them to system_interface_log.txt.
    log_messages = [
        f"[{now_str}] build_docker_compose: Created {compose_file_path} with modules: {included_modules}",
        f"[{now_str}] Updated {status_file_path} with docker-compose_build=true, docker-compose_run=false."
    ]
    append_to_log(interface_log_path, log_messages)

def run_docker_compose():
    """
    Run the generated docker-compose file if the system_status_var.json indicates that a build has occurred.
    
    Steps:
      (a) Read ./log/system_status_var.json and check if docker-compose_build is true.
      (b) Update docker-compose_run to true and set docker-compose_run_date to current date/time.
      (c) Log these updates to ./log/system_interface_log.txt.
      (d) Execute 'docker-compose -f docker-compose.generated.yml up -d' to run the containers.
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    log_dir = os.path.join(base_dir, "log")
    compose_file_path = os.path.join(log_dir, "docker-compose.generated.yml")
    status_file_path = os.path.join(log_dir, "system_status_var.json")
    interface_log_path = os.path.join(log_dir, "system_interface_log.txt")
    
    now_str = current_time()
    
    # Step (a): Read the status file.
    if not os.path.exists(status_file_path):
        msg = f"[{now_str}] run_docker_compose: {status_file_path} not found. Cannot run."
        print(msg)
        append_to_log(interface_log_path, [msg])
        return
    
    with open(status_file_path, "r") as sf:
        try:
            status_data = json.load(sf)
        except json.JSONDecodeError:
            status_data = {}
    
    if not status_data.get("docker-compose_build", False):
        msg = f"[{now_str}] run_docker_compose: docker-compose_build is not true. No action taken."
        print(msg)
        append_to_log(interface_log_path, [msg])
        return
    
    # Step (b): Update status file for run.
    status_data["docker-compose_run"] = True
    status_data["docker-compose_run_date"] = now_str
    
    with open(status_file_path, "w") as sf:
        json.dump(status_data, sf, indent=2)
    msg_run = f"[{now_str}] run_docker_compose: Updated {status_file_path} with docker-compose_run=true."
    print(msg_run)
    append_to_log(interface_log_path, [msg_run])
    
    # Step (c): Execute docker-compose up -d using the generated file.
    if not os.path.exists(compose_file_path):
        msg_err = f"[{now_str}] run_docker_compose: {compose_file_path} not found. Cannot run."
        print(msg_err)
        append_to_log(interface_log_path, [msg_err])
        return
    
    cmd = ["docker-compose", "-f", compose_file_path, "up", "-d"]
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        stdout, stderr = proc.communicate()
        msg_done = f"[{now_str}] run_docker_compose: Executed {' '.join(cmd)}"
        print(msg_done)
        print(stdout, stderr)
        append_to_log(interface_log_path, [msg_done, stdout, stderr])
    except Exception as e:
        err_msg = f"[{now_str}] run_docker_compose: Error executing docker-compose: {e}"
        print(err_msg)
        append_to_log(interface_log_path, [err_msg])

def current_time():
    """Return the current system time as a formatted string."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def append_to_log(log_path, messages):
    """
    Append a list of messages to the log file at log_path.
    Each message is appended on a new line.
    """
    with open(log_path, "a") as lf:
        for msg in messages:
            lf.write(msg + "\n")

# For testing purposes, you can run these functions directly.
if __name__ == "__main__":
    # Uncomment these lines to test building and running:
    build_docker_compose()
    # run_docker_compose()
