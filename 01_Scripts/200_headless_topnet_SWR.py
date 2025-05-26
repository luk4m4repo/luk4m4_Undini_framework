"""
HOUDINI headless script to cook a TOPnet for Sidewalks & Roads
-------------------------------------------------------------

To use this, simply enter:

& "C:\Program Files\Side Effects Software\Houdini 20.5.278\bin\hython.exe" "path\to\script.py" --hip "path\to\your\file.hip" --file1_path "S:/path/to/input.bgeo" --rop_fbx_road_path "S:/path/to/road.fbx" --rop_fbx_sidewalks_path "S:/path/to/sidewalks.fbx" --iteration_number 5

in Powershell.
"""

import hou
import os
import time
import argparse

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Cook a TOPnet in Houdini headlessly')
parser.add_argument('--hip', required=True, help='Path to the Houdini .hip file')
parser.add_argument('--topnet', default="/obj/geo1/topnet", help='Path to the TOPnet node (default: /obj/geo1/topnet)')
parser.add_argument('--file1_path', default=None, help="Value for the 'file' parameter in /obj/geo1/file1")
parser.add_argument('--rop_fbx_road_path', default=None, help="Value for the 'sopoutput' parameter in /obj/geo1/rop_fbx_road")
parser.add_argument('--rop_fbx_sidewalks_path', default=None, help="Value for the 'sopoutput' parameter in /obj/geo1/rop_fbx_sidewalks")
parser.add_argument('--iteration_number', type=int, default=None, help="Value for the 'iteration_number' parameter in /obj/geo1/python_import_splines_from_json")
parser.add_argument('--switch_bool', type=int, default=0, help="Value for the 'input' parameter in /obj/geo1/switch_bool")
parser.add_argument('--base_path', default=None, help="Value for the 'base_path' parameter in /obj/geo1/python_import_splines_from_json")
args = parser.parse_args()

print("*" * 80)
print("STARTING HOUDINI SIDEWALKS & ROADS GENERATION")
print("*" * 80)
print(f"Arguments received: {args}")

# Load the hip file
print("\nLoading Houdini file...")
hip_file_path = args.hip
try:
    hou.hipFile.load(hip_file_path)
    print(f"Successfully loaded: {hip_file_path}")
except Exception as e:
    print(f"ERROR loading hip file: {str(e)}")
    exit(1)

# Now set node parameters if arguments are provided
if args.file1_path is not None:
    file1_node = hou.node('/obj/geo1/file1')
    if file1_node is not None and file1_node.parm('file') is not None:
        file1_node.parm('file').set(args.file1_path)
        print(f"Set /obj/geo1/file1.file to: {args.file1_path}")
    else:
        print("WARNING: Could not set /obj/geo1/file1.file (node or parm not found)")

if args.base_path is not None:
    python_node = hou.node('/obj/geo1/python_import_splines_from_json')
    if python_node is not None and python_node.parm('base_path') is not None:
        python_node.parm('base_path').set(args.base_path)
        print(f"Set /obj/geo1/python_import_splines_from_json.base_path to: {args.base_path}")
    else:
        print("WARNING: Could not set /obj/geo1/python_import_splines_from_json.base_path (node or parm not found)")

if args.rop_fbx_road_path is not None:
    rop_road_node = hou.node('/obj/geo1/rop_fbx_road')
    if rop_road_node is not None and rop_road_node.parm('sopoutput') is not None:
        rop_road_node.parm('sopoutput').set(args.rop_fbx_road_path)
        print(f"Set /obj/geo1/rop_fbx_road.sopoutput to: {args.rop_fbx_road_path}")
    else:
        print("WARNING: Could not set /obj/geo1/rop_fbx_road.sopoutput (node or parm not found)")

if args.rop_fbx_sidewalks_path is not None:
    rop_sidewalks_node = hou.node('/obj/geo1/rop_fbx_sidewalks')
    if rop_sidewalks_node is not None and rop_sidewalks_node.parm('sopoutput') is not None:
        rop_sidewalks_node.parm('sopoutput').set(args.rop_fbx_sidewalks_path)
        print(f"Set /obj/geo1/rop_fbx_sidewalks.sopoutput to: {args.rop_fbx_sidewalks_path}")
    else:
        print("WARNING: Could not set /obj/geo1/rop_fbx_sidewalks.sopoutput (node or parm not found)")

# Set iteration_number parameter if provided
if args.iteration_number is not None:
    python_node = hou.node('/obj/geo1/python_import_splines_from_json')
    if python_node is not None:
        iteration_parm = python_node.parm('iteration_number')
        if iteration_parm is not None:
            iteration_parm.set(str(args.iteration_number))
            print(f"Set /obj/geo1/python_import_splines_from_json.iteration_number to: {args.iteration_number}")
        else:
            print("WARNING: iteration_number parameter not found on python_import_splines_from_json node")
    else:
        print("WARNING: Could not find /obj/geo1/python_import_splines_from_json node")

# Set switch_bool parameter if provided
if args.switch_bool is not None:
    switch_bool_node = hou.node('/obj/geo1/switch_bool')
    if switch_bool_node is not None:
        if switch_bool_node.parm('input') is not None:
            # Convert to string when setting the parameter to avoid type errors
            switch_bool_node.parm('input').set(str(args.switch_bool))
            print(f"Set /obj/geo1/switch_bool.input to: {args.switch_bool}")
        else:
            print("WARNING: input parameter not found on switch_bool node")
    else:
        print("WARNING: Could not find /obj/geo1/switch_bool node")

# Get the TOPnet node
topnet_path = args.topnet
topnet_node = hou.node(topnet_path)

if not topnet_node:
    print(f"ERROR: TOP network not found at {topnet_path}")
    exit(1)

print(f"\nFound TOPnet: {topnet_node.path()}")

# Check if the cookbutton parameter exists
cookbutton = topnet_node.parm("cookbutton")
if not cookbutton:
    print("ERROR: 'cookbutton' parameter not found on the TOPnet node")
    exit(1)

# Cook the TOPnet by pressing the cookbutton
try:
    print("\nCooking the TOP network...")
    cookbutton.pressButton()
    print("Cook button pressed, TOP network execution started")
    print("Waiting for cooking to complete...")
    time.sleep(10)
    max_wait_time = 120  # 2 minutes
    start_time = time.time()
    while time.time() - start_time < max_wait_time:
        time.sleep(5)  # Check every 5 seconds
        print("Still cooking...")
    print("Cooking complete or timed out")
except Exception as e:
    print(f"ERROR during cooking: {str(e)}")
    exit(1)

print("\nScript completed successfully")
print("Sidewalks & Roads export should now be complete")

# Check if the output files were created
if args.rop_fbx_road_path and os.path.exists(args.rop_fbx_road_path):
    print(f"Road FBX file created: {args.rop_fbx_road_path}")
else:
    print(f"Road FBX file not found at: {args.rop_fbx_road_path}")
    
if args.rop_fbx_sidewalks_path and os.path.exists(args.rop_fbx_sidewalks_path):
    print(f"Sidewalks FBX file created: {args.rop_fbx_sidewalks_path}")
else:
    print(f"Sidewalks FBX file not found at: {args.rop_fbx_sidewalks_path}")

print("\nScript execution complete.")