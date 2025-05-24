"""
Houdini Headless Cooking Script

This script runs Houdini in headless mode to cook a TOPnet that generates sidewalks and roads.
It takes spline data from Unreal Engine, processes it, and exports FBX files back to Unreal.

Example usage in PowerShell:
& "C:\Program Files\Side Effects Software\Houdini 20.5.278\bin\hython.exe" "path\to\script.py" \
  --hip "path\to\your\file.hip" \
  --rop_fbx_road_path "S:/path/to/road.fbx" \
  --rop_fbx_sidewalks_path "S:/path/to/sidewalks.fbx" \
  --iteration_number 5
"""

import hou
import os
import time
import argparse
import re

# Define the workspace root relative to this script
WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

# Set up command-line arguments
parser = argparse.ArgumentParser(description='Cook a Houdini TOPnet to generate roads and sidewalks')
parser.add_argument('--hip', required=True, help='Path to the Houdini .hip file')
parser.add_argument('--topnet', default="/obj/tower_00/topnet", help='Path to the TOPnet node')
parser.add_argument('--file1_path', default=None, help="Input file path for /obj/geo1/file1")
parser.add_argument('--rop_fbx_road_path', default=None, help="Output path for road FBX")
parser.add_argument('--rop_fbx_sidewalks_path', default=None, help="Output path for sidewalks FBX")
parser.add_argument('--iteration_number', type=int, default=None, help="Current iteration number")
parser.add_argument('--switch_bool', type=int, default=0, help="Switch to control road generation mode")
args = parser.parse_args()

# Load the Houdini file
print("Opening Houdini file...")
hip_file_path = args.hip
hou.hipFile.load(hip_file_path)
print(f"Opened: {hip_file_path}")

# Configure input file if specified
if args.file1_path is not None:
    file1_node = hou.node('/obj/geo1/file1')
    if file1_node is not None and file1_node.parm('file') is not None:
        file1_node.parm('file').set(args.file1_path)
        print(f"Set input file to: {args.file1_path}")
    else:
        print(f"Hmm, couldn't find the file1 node or its file parameter. Is the hip file set up correctly?")

# Set the road FBX output path
if args.rop_fbx_road_path is not None:
    rop_road_node = hou.node('/obj/geo1/rop_fbx_road')
    if rop_road_node is not None and rop_road_node.parm('sopoutput') is not None:
        rop_road_node.parm('sopoutput').set(args.rop_fbx_road_path)
        print(f"Road FBX will be saved to: {args.rop_fbx_road_path}")
    else:
        print(f"Couldn't find the road FBX output node. Roads won't be exported properly.")

# Set the sidewalks FBX output path
if args.rop_fbx_sidewalks_path is not None:
    rop_sidewalks_node = hou.node('/obj/geo1/rop_fbx_sidewalks')
    if rop_sidewalks_node is not None and rop_sidewalks_node.parm('sopoutput') is not None:
        rop_sidewalks_node.parm('sopoutput').set(args.rop_fbx_sidewalks_path)
        print(f"Sidewalk FBX will be saved to: {args.rop_fbx_sidewalks_path}")
    else:
        print(f"Couldn't find the sidewalk FBX output node. Sidewalks won't be exported properly.")

# Set the iteration number for the Python node
if args.iteration_number is not None:
    python_node = hou.node('/obj/geo1/python_import_splines_from_json')
    if python_node is not None:
        # Try setting the parameter directly if it exists
        if python_node.parm('iteration_number') is not None:
            python_node.parm('iteration_number').set(str(args.iteration_number))
            print(f"Using iteration number: {args.iteration_number}")
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
                    print(f"Set iteration number to {args.iteration_number} in the Python code")
                else:
                    print(f"Couldn't find iteration_number in the Python code. The splines might not load correctly.")
            else:
                print(f"Couldn't access the Python code. The iteration number won't be set.")
    else:
        print(f"Couldn't find the Python node for importing splines. The iteration number won't be set.")

# Set the switch boolean for road generation mode
if args.switch_bool is not None:
    switch_bool_node = hou.node('/obj/geo1/switch_bool')
    if switch_bool_node is not None:
        # Try setting the parameter directly
        if switch_bool_node.parm('input') is not None:
            switch_bool_node.parm('input').set(args.switch_bool)
            print(f"Set road generation mode to: {args.switch_bool}")
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
                    print(f"Set road generation mode to {args.switch_bool} in the Python code")
                else:
                    print(f"Couldn't find the input parameter in the switch node code.")
            else:
                print(f"Couldn't access the switch node's Python code.")
    else:
        print(f"Couldn't find the switch_bool node. Road generation mode won't be set.")

print("All parameters set. Ready to cook the network.")

# Find the TOPnet node we need to cook
topnet_path = args.topnet
topnet_node = hou.node(topnet_path)

# Make sure we found the TOPnet
if not topnet_node:
    print(f"Hmm, couldn't find the TOP network at {topnet_path}. Let me see what's available:")
    for node in hou.node("/obj").children():
        print(f"- {node.path()}")
    print("Please check the --topnet argument and try again.")
    exit(1)

print(f"Found the TOP network: {topnet_node.path()}")

# Make sure the cook button exists
cookbutton = topnet_node.parm("cookbutton")
if not cookbutton:
    print("Uh oh! The cook button is missing from the TOP network.")
    print("Here are the available parameters:")
    for parm in topnet_node.parms():
        print(f"- {parm.name()}: {parm.description()}")
    print("Please check that the TOP network is set up correctly.")
    exit(1)

# Time to cook the network!
try:
    print("Starting the cooking process...")
    
    # Press the cook button
    cookbutton.pressButton()
    print("Cook button pressed! The TOP network is now processing...")
    
    # Wait for cooking to start and complete
    print("This will take a little while. Giving Houdini time to work...")
    time.sleep(25)
    
    print("Almost there, just a bit longer...")
    time.sleep(10)
    
    print("Cooking should be complete now!")
    
except Exception as e:
    print(f"Oh no! Something went wrong while cooking: {str(e)}")
    print("Please check the Houdini scene and try again.")
    exit(1)

print("\nAll done! The script ran successfully.")
print("Your road and sidewalk FBX files should be ready for import into Unreal Engine.")
print(f"Iteration {args.iteration_number if args.iteration_number is not None else '0'} complete!")