"""
HOUDINI headless script to cook a TOPnet
-----------------------------------------

To use this, simply enter:

& "C:\Program Files\Side Effects Software\Houdini 20.5.278\bin\hython.exe" "path\to\script.py" --hip "path\to\your\file.hip" --topnet "/obj/geo1/topnet" --file1_path "path/to/input.fbx" --rop_pcg_export1_mesh_path "path/to/mesh.csv" --rop_pcg_export1_mat_path "path/to/mat.csv" --iteration_number 5

in Powershell.
"""

import hou
import os
import time
import argparse

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Cook a TOPnet in Houdini headlessly')
parser.add_argument('--hip', required=True, help='Path to the Houdini .hip file')
parser.add_argument('--topnet', default="/obj/tower_00/topnet", help='Path to the TOPnet node (default: /obj/tower_00/topnet)')
parser.add_argument('--file1_path', default=None, help="Value for the 'file' parameter in /obj/geo1/file1")
parser.add_argument('--rop_pcg_export1_mesh_path', default="S:/users/luka.croisez/ProcGenPipeline/Dependancies/PCG_HD/Out/CSV/mesh.csv", help="Value for the 'file_mesh' parameter in /obj/geo1/pcg_export1")
parser.add_argument('--rop_pcg_export1_mat_path', default="S:/users/luka.croisez/ProcGenPipeline/Dependancies/PCG_HD/Out/CSV/mat.csv", help="Value for the 'file_mat' parameter in /obj/geo1/pcg_export1")
parser.add_argument('--iteration_number', type=int, default=None, help="Value for the 'iteration_number' parameter in /obj/geo1/python_import_splines_from_json")
parser.add_argument('--switch_bool', type=int, default=0, help="Value for the 'input' parameter in /obj/geo1/switch_bool")
args = parser.parse_args()

# Load the hip file
print("Loading Houdini file...")
hip_file_path = args.hip
hou.hipFile.load(hip_file_path)
print(f"Successfully loaded: {hip_file_path}")

# Now set node parameters if arguments are provided
if args.file1_path is not None:
    file1_node = hou.node('/obj/geo1/file1')
    if file1_node is not None and file1_node.parm('file') is not None:
        file1_node.parm('file').set(args.file1_path)
        print(f"Set /obj/geo1/file1.file to: {args.file1_path}")
    else:
        print("WARNING: Could not set /obj/geo1/file1.file (node or parm not found)")

if args.rop_pcg_export1_mesh_path is not None:
    pcg_export1_mesh_node = hou.node('/obj/geo1/pcg_export1')
    if pcg_export1_mesh_node is not None and pcg_export1_mesh_node.parm('file_mesh') is not None:
        pcg_export1_mesh_node.parm('file_mesh').set(args.rop_pcg_export1_mesh_path)
        print(f"Set /obj/geo1/pcg_export1.file_mesh to: {args.rop_pcg_export1_mesh_path}")
    else:
        print("WARNING: Could not set /obj/geo1/pcg_export1.file_mesh (node or parm not found)")

if args.rop_pcg_export1_mat_path is not None:
    pcg_export1_mat_node = hou.node('/obj/geo1/pcg_export1')
    if pcg_export1_mat_node is not None and pcg_export1_mat_node.parm('file_mat') is not None:
        pcg_export1_mat_node.parm('file_mat').set(args.rop_pcg_export1_mat_path)
        print(f"Set /obj/geo1/pcg_export1.file_mat to: {args.rop_pcg_export1_mat_path}")
    else:
        print("WARNING: Could not set /obj/geo1/rop_fbx_sidewalks.sopoutput (node or parm not found)")

# Set iteration_number parameter if provided
if args.iteration_number is not None:
    python_node = hou.node('/obj/geo1/python_import_splines_from_json')
    if python_node is not None:
        # Try to set the parameter directly if it exists
        if python_node.parm('iteration_number') is not None:
            # Convert to string when setting the parameter to avoid type errors
            python_node.parm('iteration_number').set(str(args.iteration_number))
            print(f"Set /obj/geo1/python_import_splines_from_json.iteration_number to: {args.iteration_number}")
        else:
            # If the parameter doesn't exist directly, it might be in the Python node's code
            # We'll need to modify the Python code parameter
            python_code_parm = python_node.parm('python')
            if python_code_parm is not None:
                current_code = python_code_parm.eval()
                # Look for a line defining iteration_number
                if 'iteration_number' in current_code:
                    # Replace the line with our new value
                    import re
                    new_code = re.sub(r'iteration_number\s*=\s*\d+', f'iteration_number = {args.iteration_number}', current_code)
                    python_code_parm.set(new_code)
                    print(f"Modified Python code to set iteration_number to: {args.iteration_number}")
                else:
                    print("WARNING: Could not find 'iteration_number' in the Python code to modify")
            else:
                print("WARNING: Could not access Python code parameter in the node")
    else:
        print("WARNING: Could not find /obj/geo1/python_import_splines_from_json node")
print(f"Successfully loaded: {hip_file_path}")

# Set switch_bool parameter if provided
if args.switch_bool is not None:
    switch_bool_node = hou.node('/obj/geo1/switch_bool')
    if switch_bool_node is not None:
        # Try to set the parameter directly if it exists
        if switch_bool_node.parm('input') is not None:
            # Convert to string when setting the parameter to avoid type errors
            switch_bool_node.parm('input').set(str(args.switch_bool))
            print(f"Set /obj/geo1/switch_bool.input to: {args.switch_bool}")
        else:
            # If the parameter doesn't exist directly, it might be in the Python node's code
            # We'll need to modify the Python code parameter
            python_code_parm = switch_bool_node.parm('python')
            if python_code_parm is not None:
                current_code = python_code_parm.eval()
                # Look for a line defining iteration_number
                if 'input' in current_code:
                    # Replace the line with our new value
                    import re
                    new_code = re.sub(r'input\s*=\s*\d+', f'input = {args.switch_bool}', current_code)
                    python_code_parm.set(new_code)
                    print(f"Modified Python code to set input to: {args.switch_bool}")
                else:
                    print("WARNING: Could not find 'input' in the Python code to modify")
            else:
                print("WARNING: Could not access Python code parameter in the node")
    else:
        print("WARNING: Could not find /obj/geo1/switch_bool node")
print(f"Successfully loaded: {hip_file_path}")

# Get the TOPnet node
topnet_path = args.topnet
topnet_node = hou.node(topnet_path)

if not topnet_node:
    print(f"ERROR: TOP network not found at {topnet_path}")
    # List top-level objects to help debugging
    for node in hou.node("/obj").children():
        print(f"Available node: {node.path()}")
    exit(1)

print(f"\nFound TOPnet: {topnet_node.path()}")

# Check if the cookbutton parameter exists
cookbutton = topnet_node.parm("cookbutton")
if not cookbutton:
    print("ERROR: 'cookbutton' parameter not found on the TOPnet node")
    print("Available parameters:")
    for parm in topnet_node.parms():
        print(f"  - {parm.name()}: {parm.description()}")
    exit(1)

# Cook the TOPnet by pressing the cookbutton
try:
    print("\nCooking the TOP network...")
    
    # Press the cookbutton to start cooking
    cookbutton.pressButton()
    print("Cook button pressed, TOP network execution started")
    
    # Wait for a few seconds to allow cooking to start
    print("Waiting 25 seconds for cooking to start...")
    time.sleep(25)
    
    # Optionally: You could add a loop here to check if the network is still cooking
    # However, this would require specific checks that might not be universally available
    # Instead, we'll wait a reasonable amount of time
    
    print("Waiting for cook to complete (10 seconds)...")
    time.sleep(10)
    
    print("TOP network cook should be completed")
    
except Exception as e:
    print(f"Error cooking TOP network: {str(e)}")
    exit(1)

print("\nScript completed successfully")
print("PCG export should now be complete")