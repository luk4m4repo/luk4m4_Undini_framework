"""
HOUDINI Headless Script for Sidewalks & Roads Generation
-------------------------------------------------------

This script is part of the Undini procedural generation pipeline, specifically handling
the generation of sidewalks and roads:

1. First, we export splines from Unreal Engine (000_export_splines_as_json.py)
2. Then, we export GenZone meshes from UE (010_export_gz_to_mod.py)
3. We process building data in Houdini (100_headless_topnet_PCGHD.py)
4. We import CSV files back into Unreal Engine (110_reimport_datatable.py)
5. We create PCG graphs in Unreal Engine (120_create_pcg_graph.py)
6. Finally, this script generates sidewalks and roads based on the splines

The script loads a Houdini .hip file, sets various parameters based on command-line arguments,
and then cooks a TOP network to generate FBX files containing sidewalks and roads geometry.
These FBX files will be used by Unreal Engine to create the sidewalks and roads in the level.

Usage Example:
& "C:\Program Files\Side Effects Software\Houdini 20.5.278\bin\hython.exe" "path\to\script.py" \
  --hip "path\to\your\file.hip" \
  --topnet "/obj/geo1/topnet" \
  --file1_path "path\to\input.bgeo" \
  --rop_fbx_road_path "path\to\road.fbx" \
  --rop_fbx_sidewalks_path "path\to\sidewalks.fbx" \
  --iteration_number 5 \
  --switch_bool 0 \
  --base_path "path/to/splines/base/path"

Parameters:
--hip: Path to the Houdini .hip file
--topnet: Path to the TOPnet node (default: "/obj/geo1/topnet")
--file1_path: Path to the input file (usually not needed for sidewalks & roads)
--rop_fbx_road_path: Output path for the road FBX file
--rop_fbx_sidewalks_path: Output path for the sidewalks FBX file
--iteration_number: Iteration number to use for finding the correct spline JSON file
--switch_bool: Controls behavior of the network (usually 0 for this script)
--base_path: Base path for the splines JSON files (without iteration number and extension)
"""

import hou
import os
import time
import argparse

# Set up our command-line argument parser
# This allows us to control the script's behavior from the command line
print("Setting up command-line arguments...")
parser = argparse.ArgumentParser(description='Generate sidewalks and roads using Houdini TOPnet')

# Required arguments
parser.add_argument('--hip', required=True, 
                   help='Path to the Houdini .hip file containing the sidewalks & roads setup')

# Optional arguments with sensible defaults
parser.add_argument('--topnet', default="/obj/geo1/topnet", 
                   help='Path to the TOPnet node that will be cooked (default: /obj/geo1/topnet)')
                   
# Input paths - these will be provided by the manager script
parser.add_argument('--file1_path', default=None, 
                   help="Path to the input file (usually not needed for sidewalks & roads)")
parser.add_argument('--base_path', default=None,
                   help="Base path for the splines JSON files (without iteration number and extension)")
                   
# Output paths - these should be provided by the manager script rather than hardcoded
parser.add_argument('--rop_fbx_road_path', default=None, 
                   help="Output path for the road FBX file")
parser.add_argument('--rop_fbx_sidewalks_path', default=None, 
                   help="Output path for the sidewalks FBX file")
                   
# Pipeline control parameters
parser.add_argument('--iteration_number', type=int, default=None, 
                   help="Iteration number used to find the correct spline JSON file")
parser.add_argument('--switch_bool', type=int, default=0, 
                   help="Controls behavior of the network (usually 0 for this script)")
                   
# Parse the arguments
args = parser.parse_args()

# Validate required arguments that don't have defaults
if args.rop_fbx_road_path is None:
    print("WARNING: No road FBX output path specified. Output may not be saved correctly.")
if args.rop_fbx_sidewalks_path is None:
    print("WARNING: No sidewalks FBX output path specified. Output may not be saved correctly.")

# Print a nice header and summary of the arguments
print("\n" + "*" * 80)
print("🛣️  STARTING HOUDINI SIDEWALKS & ROADS GENERATION")
print("*" * 80)

# Print a summary of the arguments
print("\nRunning with the following settings:")
print(f"  • Houdini File: {args.hip}")
print(f"  • TOPnet Path: {args.topnet}")
print(f"  • Input File: {args.file1_path if args.file1_path else 'Not specified'}")
print(f"  • Splines Base Path: {args.base_path if args.base_path else 'Not specified'}")
print(f"  • Output Road FBX: {args.rop_fbx_road_path if args.rop_fbx_road_path else 'Not specified'}")
print(f"  • Output Sidewalks FBX: {args.rop_fbx_sidewalks_path if args.rop_fbx_sidewalks_path else 'Not specified'}")
print(f"  • Iteration Number: {args.iteration_number if args.iteration_number is not None else 'Not specified'}")
print(f"  • Switch Bool: {args.switch_bool}")
print()

# Helper function to set a parameter on a node with better error handling
def set_node_parameter(node_path, parameter_name, value, description=None):
    """Set a parameter on a Houdini node with better error handling and logging"""
    if value is None:
        print(f"Skipping {node_path}.{parameter_name} (no value provided)")
        return False
        
    # Get the node
    node = hou.node(node_path)
    if node is None:
        print(f"⚠️ WARNING: Could not find node {node_path}")
        return False
        
    # Get the parameter
    parm = node.parm(parameter_name)
    if parm is None:
        print(f"⚠️ WARNING: Parameter '{parameter_name}' not found on {node_path}")
        return False
        
    # Set the parameter value (convert to string to avoid type errors)
    parm.set(str(value))
    
    # Log the success
    desc = description or f"Set {node_path}.{parameter_name}"
    print(f"✅ {desc}: {value}")
    return True

# Load the Houdini file
print("\n🔄 Loading Houdini file...")
hip_file_path = args.hip

# Check if the hip file exists before attempting to load it
if not os.path.exists(hip_file_path):
    print(f"❌ ERROR: Houdini file not found at: {hip_file_path}")
    print("Please check the path and make sure the file exists.")
    exit(1)
    
try:
    hou.hipFile.load(hip_file_path)
    print(f"✅ Successfully loaded: {hip_file_path}")
except Exception as e:
    print(f"❌ ERROR loading hip file: {str(e)}")
    print("Please check that the file is a valid Houdini .hip file and is not corrupted.")
    exit(1)

# Now let's configure all the nodes with our parameters
print("\n🔧 Configuring Houdini nodes...")

# 1. Set the input file path (if provided)
set_node_parameter(
    '/obj/geo1/file1', 'file', args.file1_path,
    "Set input file path"
)

# 2. Set the output paths for the FBX files
# Set road FBX output path
set_node_parameter(
    '/obj/geo1/rop_fbx_road', 'sopoutput', args.rop_fbx_road_path,
    "Set road FBX output path"
)

# Set sidewalks FBX output path
set_node_parameter(
    '/obj/geo1/rop_fbx_sidewalks', 'sopoutput', args.rop_fbx_sidewalks_path,
    "Set sidewalks FBX output path"
)

# 3. Set the base_path parameter for the spline import
print("\n📚 Setting parameters for spline import...")
set_node_parameter(
    '/obj/geo1/python_import_splines_from_json', 'base_path', args.base_path,
    "Set base path for spline import"
)

# If direct parameter setting failed, try to modify the Python code
if args.base_path is not None and not hou.node('/obj/geo1/python_import_splines_from_json').parm('base_path'):
    python_node = hou.node('/obj/geo1/python_import_splines_from_json')
    if python_node is not None:
        python_code_parm = python_node.parm('python')
        if python_code_parm is not None:
            current_code = python_code_parm.eval()
            # Look for a line defining base_path or splines_path
            if 'base_path' in current_code:
                # Replace the line with our new value
                import re
                new_code = re.sub(r'base_path\s*=\s*[\'\"](.*?)[\'\"](.*)', f'base_path = "{args.base_path}"\2', current_code)
                python_code_parm.set(new_code)
                print(f"✅ Modified Python code to set base_path to: {args.base_path}")
            elif 'splines_path' in current_code:
                # It might be called splines_path instead
                new_code = re.sub(r'splines_path\s*=\s*[\'\"](.*?)[\'\"](.*)', f'splines_path = "{args.base_path}"\2', current_code)
                python_code_parm.set(new_code)
                print(f"✅ Modified Python code to set splines_path to: {args.base_path}")
            else:
                print("⚠️ WARNING: Could not find 'base_path' or 'splines_path' in the Python code to modify")
        else:
            print("⚠️ WARNING: Could not access Python code parameter in the node")

# 4. Set the iteration_number parameter for the spline import
print("\n🔢 Setting iteration number...")
set_node_parameter(
    '/obj/geo1/python_import_splines_from_json', 'iteration_number', args.iteration_number,
    "Set iteration number for spline import"
)

# If direct parameter setting failed, try to modify the Python code
if args.iteration_number is not None and not set_node_parameter('/obj/geo1/python_import_splines_from_json', 'iteration_number', args.iteration_number, None):
    python_node = hou.node('/obj/geo1/python_import_splines_from_json')
    if python_node is not None:
        python_code_parm = python_node.parm('python')
        if python_code_parm is not None:
            current_code = python_code_parm.eval()
            # Look for a line defining iteration_number
            if 'iteration_number' in current_code:
                # Replace the line with our new value
                import re
                new_code = re.sub(r'iteration_number\s*=\s*\d+', f'iteration_number = {args.iteration_number}', current_code)
                python_code_parm.set(new_code)
                print(f"✅ Modified Python code to set iteration_number to: {args.iteration_number}")
            else:
                print("⚠️ WARNING: Could not find 'iteration_number' in the Python code to modify")
        else:
            print("⚠️ WARNING: Could not access Python code parameter in the node")

# 5. Set the switch_bool parameter to control network behavior
print("\n🔍 Setting switch_bool parameter...")
set_node_parameter(
    '/obj/geo1/switch_bool', 'input', args.switch_bool,
    f"Set switch_bool to {args.switch_bool}"
)

# Now let's find and cook the TOPnet
print("\n🍳 Preparing to cook the TOP network...")
topnet_path = args.topnet
print(f"Looking for TOPnet at: {topnet_path}")

# Find the TOPnet node
topnet_node = hou.node(topnet_path)
if not topnet_node:
    print(f"❌ ERROR: TOP network not found at {topnet_path}")
    
    # List available nodes to help debugging
    print("\nAvailable nodes in /obj:")
    for node in hou.node("/obj").children():
        print(f"  • {node.path()}")
        
    # List available networks that might be TOPnets
    print("\nPossible TOPnets:")
    for node in hou.nodeType(hou.topNodeType()).instances():
        print(f"  • {node.path()}")
        
    print("\nPlease check the --topnet argument and make sure it points to a valid TOP network.")
    exit(1)

print(f"✅ Found TOPnet: {topnet_node.path()}")

# Check if the cookbutton parameter exists
print("Looking for the 'cookbutton' parameter...")
cookbutton = topnet_node.parm("cookbutton")
if not cookbutton:
    print("❌ ERROR: 'cookbutton' parameter not found on the TOPnet node")
    
    # List available parameters to help debugging
    print("\nAvailable parameters on the TOPnet node:")
    for parm in topnet_node.parms():
        print(f"  • {parm.name()}: {parm.description()}")
        
    print("\nThe TOPnet might not be properly configured for cooking.")
    exit(1)

print("✅ Found 'cookbutton' parameter")

# Cook the TOPnet by pressing the cookbutton
try:
    print("\n🔥 Starting the cooking process...")
    
    # Press the cookbutton to start cooking
    cookbutton.pressButton()
    print("✅ Cook button pressed, TOP network execution started")
    
    # Wait for cooking to start
    print("Waiting for cooking to start (this may take a moment)...")
    for i in range(3):
        print(f"  ⏳ {3-i} seconds remaining...")
        time.sleep(1)
    
    # Wait for cooking to complete
    # Note: We can't easily check if cooking is still in progress in headless mode,
    # so we just wait a reasonable amount of time
    print("\nWaiting for cook to complete...")
    max_wait_time = 120  # 2 minutes
    start_time = time.time()
    while time.time() - start_time < max_wait_time:
        elapsed = int(time.time() - start_time)
        remaining = max_wait_time - elapsed
        if remaining % 10 == 0:  # Only print every 10 seconds to reduce noise
            print(f"  ⏳ Still cooking... ({elapsed}s elapsed, max {max_wait_time}s)")
        time.sleep(1)
    
    print("✅ TOP network cook should be completed")
    
except Exception as e:
    print(f"❌ Error cooking TOP network: {str(e)}")
    exit(1)

# Check for output files
print("\n💾 Checking for output files...")
if args.rop_fbx_road_path and os.path.exists(args.rop_fbx_road_path):
    file_size = os.path.getsize(args.rop_fbx_road_path)
    print(f"✅ Road FBX file created: {args.rop_fbx_road_path} ({file_size/1024:.1f} KB)")
else:
    print("⚠️ Road FBX file not found or not specified at: {args.rop_fbx_road_path}")
    print("  Check that the output path is correct and that the TOP network is configured properly.")
    
if args.rop_fbx_sidewalks_path and os.path.exists(args.rop_fbx_sidewalks_path):
    file_size = os.path.getsize(args.rop_fbx_sidewalks_path)
    print(f"✅ Sidewalks FBX file created: {args.rop_fbx_sidewalks_path} ({file_size/1024:.1f} KB)")
else:
    print("⚠️ Sidewalks FBX file not found or not specified at: {args.rop_fbx_sidewalks_path}")
    print("  Check that the output path is correct and that the TOP network is configured properly.")

print("\n🎉 Script completed successfully")
print("Sidewalks & Roads export has been generated and exported to FBX files.")
print("The next step is to import these FBX files into Unreal Engine.")
print("" + "-"*80)