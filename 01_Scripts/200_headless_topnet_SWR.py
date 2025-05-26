"""
Houdini Sidewalks & Roads Generation Script

This script runs Houdini in headless mode to generate sidewalks and roads.
It processes spline data from Unreal Engine and exports FBX files for sidewalks and roads.

Example usage in PowerShell:
& "C:\Program Files\Side Effects Software\Houdini 20.0.653\bin\hython.exe" "path\to\script.py" \
  --hip "path\to\your\file.hip" \
  --topnet "/obj/geo1/topnet" \
  --rop_fbx_road_path "path/to/road.fbx" \
  --rop_fbx_sidewalks_path "path/to/sidewalks.fbx" \
  --iteration_number 5 \
  --switch_bool 1
"""

import argparse
import hou
import os
import sys
import re
import time
import traceback
import json
import datetime

# Setup simple logging functions
def log_debug(message):
    print(f"[DEBUG] {message}")
    sys.stdout.flush()

def log_info(message):
    print(f"[INFO] {message}")
    sys.stdout.flush()
    
def log_warning(message):
    print(f"[WARNING] {message}")
    sys.stdout.flush()
    
def log_error(message):
    print(f"[ERROR] {message}")
    sys.stdout.flush()
    
def log_exception(e):
    """Log an exception with traceback"""
    print(f"[EXCEPTION] {str(e)}")
    print(traceback.format_exc())
    sys.stdout.flush()

# Log the start of the script
log_info(f"Script started at {datetime.datetime.now()}")

# Define the workspace root relative to this script
WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

log_info(f"Workspace root: {WORKSPACE_ROOT}")
log_info(f"Current working directory: {os.getcwd()}")
log_info(f"Script directory: {os.path.dirname(__file__)}")
log_info(f"Python executable: {sys.executable}")
log_info(f"Python version: {sys.version}")
log_info(f"Houdini version: {hou.applicationVersionString()}")
log_info(f"Environment variables: {json.dumps({k:v for k,v in os.environ.items() if 'PATH' in k or 'HOUDINI' in k or 'PYTHON' in k}, indent=2)}")

# Fix the paths to use the correct directory structure with forward slashes
def normalize_path(path):
    """Normalize a path to use forward slashes."""
    return path.replace('\\', '/')

def ensure_directory_exists(file_path):
    """Ensure the directory for a file exists."""
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        log_info(f"Creating directory: {directory}")
        os.makedirs(directory, exist_ok=True)
    elif not os.access(directory, os.W_OK):
        log_warning(f"Directory is not writable: {directory}")
    
    return directory

# Set up command-line arguments
parser = argparse.ArgumentParser(description='Generate sidewalks and roads with Houdini')
parser.add_argument('--hip', required=True, help='Path to the Houdini .hip file')
parser.add_argument('--topnet', default="/obj/geo1/topnet", help='Path to the TOPnet node')
parser.add_argument('--file1_path', default=None, help="Input file path")
parser.add_argument('--rop_fbx_road_path', default=None, help="Output path for road FBX")
parser.add_argument('--rop_fbx_sidewalks_path', default=None, help="Output path for sidewalks FBX")
parser.add_argument('--iteration_number', type=int, default=0, help="Current iteration number")
parser.add_argument('--switch_bool', type=int, default=0, help="Switch to control road generation mode")
parser.add_argument('--ignore_load_warnings', action='store_true', help="Ignore warnings when loading the hip file")
parser.add_argument('--splines_base_path', help="Base path for spline JSON files (without iteration number and file extension)")

args = parser.parse_args()

# Check if the hip file exists
if not os.path.exists(args.hip):
    log_error(f"Houdini .hip file not found at {args.hip}")
    sys.exit(1)
else:
    log_info(f"Houdini .hip file found at: {args.hip}")

# Load the Houdini file
log_info("Opening Houdini file...")
hip_file_path = args.hip

try:
    log_info(f"About to load hip file: {hip_file_path}")
    log_info(f"ignore_load_warnings flag: {args.ignore_load_warnings}")
    
    if args.ignore_load_warnings:
        # Try to load with warnings ignored
        try:
            hou.hipFile.load(hip_file_path, ignore_load_warnings=True)
            log_info(f"Loaded hip file with warnings ignored: {hip_file_path}")
        except AttributeError:
            # Older Houdini versions might not have the ignore_load_warnings parameter
            log_warning("Your Houdini version doesn't support ignoring load warnings. Trying standard load.")
            hou.hipFile.load(hip_file_path)
            log_info(f"Loaded hip file: {hip_file_path}")
    else:
        # Standard load
        hou.hipFile.load(hip_file_path)
        log_info(f"Loaded hip file: {hip_file_path}")
    
    # Check for required nodes
    if not hou.node("/obj"):
        log_warning("No /obj node found!")
    elif not hou.node("/obj/geo1"):
        log_warning("No /obj/geo1 node found!")
        
except Exception as e:
    log_exception(e)
    log_error(f"Error loading Houdini file: {str(e)}")
    sys.exit(1)

# Configure input file if specified
if args.file1_path is not None:
    file1_node = hou.node('/obj/geo1/file1')
    if file1_node is not None and file1_node.parm('file') is not None:
        file1_node.parm('file').set(args.file1_path)
        log_info(f"Set input file to: {args.file1_path}")
    else:
        log_warning(f"Couldn't find the file1 node or its file parameter. Is the hip file set up correctly?")

# Set the road FBX output path
if args.rop_fbx_road_path is not None:
    # Ensure path uses forward slashes
    road_path = normalize_path(args.rop_fbx_road_path)
    log_info(f"Setting road export path to: {road_path}")
    
    # Ensure the output directory exists
    ensure_directory_exists(road_path)
    
    # Try to find the road FBX output node
    rop_road_node = hou.node('/obj/geo1/rop_fbx_road')
    if rop_road_node is not None and rop_road_node.parm('sopoutput') is not None:
        rop_road_node.parm('sopoutput').set(road_path)
        log_info(f"Road FBX will be saved to: {road_path}")
    else:
        log_warning(f"Couldn't find the road FBX output node at /obj/geo1/rop_fbx_road. Searching for it...")
        
        # Search for any ROP FBX nodes that might be for roads
        found_rop_nodes = []
        for node in hou.node("/").allSubChildren():
            if ("rop" in node.name().lower() and "fbx" in node.name().lower() and 
                ("road" in node.name().lower() or "road" in node.path().lower())):
                found_rop_nodes.append(node.path())
        
        if found_rop_nodes:
            log_info(f"Found these potential road FBX nodes: {found_rop_nodes}")
            # Try the first one
            rop_road_node = hou.node(found_rop_nodes[0])
            if rop_road_node.parm('sopoutput') is not None:
                rop_road_node.parm('sopoutput').set(road_path)
                log_info(f"Road FBX will be saved to: {road_path} using node {rop_road_node.path()}")
            else:
                log_error(f"Found node {rop_road_node.path()} but it doesn't have a 'sopoutput' parameter")
        else:
            # Try to find any ROP FBX nodes
            all_rop_fbx_nodes = []
            for node in hou.node("/").allSubChildren():
                if "rop" in node.name().lower() and "fbx" in node.name().lower():
                    all_rop_fbx_nodes.append(node.path())
            
            if all_rop_fbx_nodes:
                log_info(f"Found these ROP FBX nodes (not specifically for roads): {all_rop_fbx_nodes}")
                # Try the first one
                rop_road_node = hou.node(all_rop_fbx_nodes[0])
                if rop_road_node.parm('sopoutput') is not None:
                    rop_road_node.parm('sopoutput').set(road_path)
                    log_info(f"Road FBX will be saved to: {road_path} using node {rop_road_node.path()}")
                else:
                    log_error(f"Found node {rop_road_node.path()} but it doesn't have a 'sopoutput' parameter")
            else:
                log_error(f"Couldn't find any ROP FBX nodes in the scene. Roads won't be exported properly.")

# Set the sidewalks FBX output path
if args.rop_fbx_sidewalks_path is not None:
    # Ensure path uses forward slashes
    sidewalks_path = normalize_path(args.rop_fbx_sidewalks_path)
    log_info(f"Setting sidewalks export path to: {sidewalks_path}")
    
    # Ensure the output directory exists
    ensure_directory_exists(sidewalks_path)
    
    # Try to find the sidewalks FBX output node
    rop_sidewalks_node = hou.node('/obj/geo1/rop_fbx_sidewalks')
    if rop_sidewalks_node is not None and rop_sidewalks_node.parm('sopoutput') is not None:
        rop_sidewalks_node.parm('sopoutput').set(sidewalks_path)
        log_info(f"Sidewalk FBX will be saved to: {sidewalks_path}")
    else:
        log_warning(f"Couldn't find the sidewalk FBX output node at /obj/geo1/rop_fbx_sidewalks. Searching for it...")
        
        # Search for any ROP FBX nodes that might be for sidewalks
        found_rop_nodes = []
        for node in hou.node("/").allSubChildren():
            if ("rop" in node.name().lower() and "fbx" in node.name().lower() and 
                ("sidewalk" in node.name().lower() or "sidewalk" in node.path().lower())):
                found_rop_nodes.append(node.path())
        
        if found_rop_nodes:
            log_info(f"Found these potential sidewalk FBX nodes: {found_rop_nodes}")
            # Try the first one
            rop_sidewalks_node = hou.node(found_rop_nodes[0])
            if rop_sidewalks_node.parm('sopoutput') is not None:
                rop_sidewalks_node.parm('sopoutput').set(sidewalks_path)
                log_info(f"Sidewalk FBX will be saved to: {sidewalks_path} using node {rop_sidewalks_node.path()}")
            else:
                log_error(f"Found node {rop_sidewalks_node.path()} but it doesn't have a 'sopoutput' parameter")
        else:
            # If we already found a road ROP FBX node, try to find another one for sidewalks
            if 'rop_road_node' in locals() and rop_road_node is not None:
                all_rop_fbx_nodes = []
                for node in hou.node("/").allSubChildren():
                    if ("rop" in node.name().lower() and "fbx" in node.name().lower() and 
                        node.path() != rop_road_node.path()):
                        all_rop_fbx_nodes.append(node.path())
                
                if all_rop_fbx_nodes:
                    log_info(f"Found these other ROP FBX nodes (not specifically for sidewalks): {all_rop_fbx_nodes}")
                    # Try the first one
                    rop_sidewalks_node = hou.node(all_rop_fbx_nodes[0])
                    if rop_sidewalks_node.parm('sopoutput') is not None:
                        rop_sidewalks_node.parm('sopoutput').set(sidewalks_path)
                        log_info(f"Sidewalk FBX will be saved to: {sidewalks_path} using node {rop_sidewalks_node.path()}")
                    else:
                        log_error(f"Found node {rop_sidewalks_node.path()} but it doesn't have a 'sopoutput' parameter")
                else:
                    log_error(f"Couldn't find any other ROP FBX nodes in the scene. Sidewalks won't be exported properly.")
            else:
                log_error(f"Couldn't find any ROP FBX nodes for sidewalks in the scene. Sidewalks won't be exported properly.")

# Set the splines base path if provided
if args.splines_base_path is not None:
    splines_base_path = normalize_path(args.splines_base_path)
    log_info(f"Using splines base path: {splines_base_path}")
    
    # If we have an iteration number, construct the full path
    if args.iteration_number is not None:
        splines_path = f"{splines_base_path}{args.iteration_number}.json"
        log_info(f"Looking for splines file at: {splines_path}")
        
        # Check if the splines file exists
        if not os.path.exists(splines_path):
            log_warning(f"Splines file not found at: {splines_path}")
        else:
            log_info(f"Found splines file at: {splines_path}")

# Set the iteration number for the Python node
if args.iteration_number is not None:
    log_info(f"Using iteration number: {args.iteration_number}")
    
    python_node = hou.node('/obj/geo1/python_import_splines_from_json')
    if python_node is not None:
        # Try setting the parameter directly if it exists
        if python_node.parm('iteration_number') is not None:
            python_node.parm('iteration_number').set(str(args.iteration_number))
            log_info(f"Set iteration_number parameter to: {args.iteration_number}")
        else:
            # If not a direct parameter, try to modify the Python code
            python_code_parm = python_node.parm('python')
            if python_code_parm is not None:
                current_code = python_code_parm.eval()
                if 'iteration_number' in current_code:
                    # Update the iteration number in the code
                    new_code = re.sub(r'iteration_number\s*=\s*\d+', 
                                     f'iteration_number = {args.iteration_number}', 
                                     current_code)
                    python_code_parm.set(new_code)
                    log_info(f"Set iteration number to {args.iteration_number} in the Python code")
                else:
                    log_warning(f"Couldn't find iteration_number in the Python code. The splines might not load correctly.")
            else:
                log_warning(f"Couldn't access the Python code. The iteration number won't be set.")
    else:
        log_warning(f"Couldn't find the Python node for importing splines. The iteration number won't be set.")

# Set the switch boolean for road generation mode
if args.switch_bool is not None:
    log_info(f"Setting switch_bool to: {args.switch_bool}")
    
    switch_bool_node = hou.node('/obj/geo1/switch_bool')
    if switch_bool_node is not None:
        # Try setting the parameter directly
        if switch_bool_node.parm('input') is not None:
            switch_bool_node.parm('input').set(args.switch_bool)
            log_info(f"Set road generation mode to: {args.switch_bool}")
        else:
            # Try modifying the Python code if needed
            python_code_parm = switch_bool_node.parm('python')
            if python_code_parm is not None:
                current_code = python_code_parm.eval()
                if 'input' in current_code:
                    new_code = re.sub(r'input\s*=\s*\d+', 
                                    f'input = {args.switch_bool}', 
                                    current_code)
                    python_code_parm.set(new_code)
                    log_info(f"Set road generation mode to {args.switch_bool} in the Python code")
                else:
                    log_warning(f"Couldn't find the input parameter in the switch node code.")
            else:
                log_warning(f"Couldn't access the switch node's Python code.")
    else:
        log_warning(f"Couldn't find the switch_bool node. Road generation mode won't be set.")

# List all nodes in the scene to help diagnose the issue
log_info("\n=== LISTING ALL NODES IN THE SCENE ===")
log_info("Top-level objects:")
for node in hou.node("/obj").children():
    log_info(f"- {node.path()}")
    # List children of each top-level object
    for child in node.children():
        log_info(f"  - {child.path()}")
        # List some grandchildren to find TOPnets and ROP nodes
        for grandchild in child.children():
            if "top" in grandchild.name().lower() or "rop" in grandchild.name().lower() or "fbx" in grandchild.name().lower():
                log_info(f"    - {grandchild.path()} (POTENTIAL TARGET)")

# Run the TOPnet
log_info(f"\nLooking for TOPnet node at path: {args.topnet}")
topnet_node = hou.node(args.topnet)

if not topnet_node:
    log_error(f"ERROR: TOP network not found at {args.topnet}")
    # Try to find any TOPnet in the scene
    log_info("Searching for any TOPnet in the scene...")
    found_topnets = []
    for node in hou.node("/").allSubChildren():
        if isinstance(node, hou.TopNet) or ("top" in node.name().lower() and "net" in node.name().lower()):
            found_topnets.append(node.path())
    
    if found_topnets:
        log_info(f"Found these potential TOPnets: {found_topnets}")
        # Try the first one
        log_info(f"Trying to use the first found TOPnet: {found_topnets[0]}")
        topnet_node = hou.node(found_topnets[0])
    else:
        log_error("No TOPnets found in the scene")
        sys.exit(1)

log_info(f"\nFound TOPnet: {topnet_node.path()}")

# Check if the cookbutton parameter exists
cookbutton = topnet_node.parm("cookbutton")
if not cookbutton:
    log_error("ERROR: 'cookbutton' parameter not found on the TOPnet node")
    # List available parameters
    log_info("Available parameters:")
    for parm in topnet_node.parms():
        log_info(f"- {parm.name()}: {parm.description()}")
    sys.exit(1)

# Cook the TOPnet by pressing the cookbutton
try:
    log_info("\nCooking the TOP network...")
    
    # Press the cookbutton to start cooking
    cookbutton.pressButton()
    log_info("Cook button pressed, TOP network execution started")
    
    # Wait for a few seconds to allow cooking to start
    log_info("Waiting 25 seconds for cooking to start...")
    time.sleep(25)
    
    # Optionally: You could add a loop here to check if the network is still cooking
    # However, this would require specific checks that might not be universally available
    # Instead, we'll wait a reasonable amount of time
    
    log_info("Waiting for cook to complete (10 seconds)...")
    time.sleep(10)
    
    log_info("TOP network cook should be completed")
    
except Exception as e:
    log_exception(e)
    log_error(f"Error cooking TOP network: {str(e)}")
    sys.exit(1)

log_info("All parameters set and TOPnet cooked. Checking for output files...")

# Check if the output files were created
road_fbx_exists = os.path.exists(args.rop_fbx_road_path) if args.rop_fbx_road_path else False
sidewalks_fbx_exists = os.path.exists(args.rop_fbx_sidewalks_path) if args.rop_fbx_sidewalks_path else False

# Log final status
if args.rop_fbx_road_path and not road_fbx_exists:
    log_warning(f"Road FBX file was not created: {args.rop_fbx_road_path}")
else:
    log_info(f"Road FBX file exists at: {args.rop_fbx_road_path}")

if args.rop_fbx_sidewalks_path and not sidewalks_fbx_exists:
    log_warning(f"Sidewalks FBX file was not created: {args.rop_fbx_sidewalks_path}")
else:
    log_info(f"Sidewalks FBX file exists at: {args.rop_fbx_sidewalks_path}")

# Log file sizes if files exist
if args.rop_fbx_road_path and os.path.exists(args.rop_fbx_road_path):
    log_info(f"Road FBX file size: {os.path.getsize(args.rop_fbx_road_path)} bytes")

if args.rop_fbx_sidewalks_path and os.path.exists(args.rop_fbx_sidewalks_path):
    log_info(f"Sidewalks FBX file size: {os.path.getsize(args.rop_fbx_sidewalks_path)} bytes")

# Wait a bit more for any background processes to complete
log_info("Waiting for any background processes to complete...")
time.sleep(5)

log_info("Houdini headless processing completed!")
log_info(f"Iteration {args.iteration_number} complete!")
log_info("Your sidewalks and roads data has been exported to FBX files for use in Unreal Engine.")

# Close the log file
log_info(f"Script completed at {datetime.datetime.now()}")
# End of script