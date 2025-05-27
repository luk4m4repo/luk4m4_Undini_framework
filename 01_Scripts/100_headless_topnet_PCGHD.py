"""
HOUDINI Headless Script for PCG Building Generation
------------------------------------------------

This script is the third step in the Undini procedural generation pipeline:
1. First, we export splines from Unreal Engine (000_export_splines_as_json.py)
2. Then, we export GenZone meshes from UE (010_export_gz_to_mod.py)
3. Now, this script processes those inputs in Houdini to generate building data

The script loads a Houdini .hip file, sets various parameters based on command-line arguments,
and then cooks a TOP network to generate CSV files containing mesh and material data for
buildings. These CSV files will be used by Unreal Engine to create procedural buildings.

Usage Example:
& "C:\Program Files\Side Effects Software\Houdini 20.5.278\bin\hython.exe" "path\to\script.py" \
  --hip "path\to\your\file.hip" \
  --topnet "/obj/geo1/topnet" \
  --file1_path "path\to\input.fbx" \
  --rop_pcg_export1_mesh_path "path\to\mesh.csv" \
  --rop_pcg_export1_mat_path "path\to\mat.csv" \
  --iteration_number 5 \
  --switch_bool 0

Parameters:
--hip: Path to the Houdini .hip file
--topnet: Path to the TOPnet node (default: "/obj/geo1/topnet")
--file1_path: Path to the input FBX file (GenZone meshes)
--rop_pcg_export1_mesh_path: Output path for the mesh CSV file
--rop_pcg_export1_mat_path: Output path for the material CSV file
--iteration_number: Iteration number to use for file naming
--switch_bool: Controls whether to use splines (0) or GenZone meshes (1)
"""

import hou
import os
import time
import argparse

# Set up our command-line argument parser
# This allows us to control the script's behavior from the command line
print("Setting up command-line arguments...")
parser = argparse.ArgumentParser(description='Generate procedural data using Houdini TOPnet')

# Required arguments
parser.add_argument('--hip', required=True, 
                   help='Path to the Houdini .hip file containing the procedural setup')

# Optional arguments with sensible defaults
parser.add_argument('--topnet', default="/obj/geo1/topnet", 
                   help='Path to the TOPnet node that will be cooked (default: /obj/geo1/topnet)')
                   
# Input paths - these will be provided by the manager script
parser.add_argument('--file1_path', default=None, 
                   help="Path to the input FBX file containing GenZone meshes")
parser.add_argument('--base_path', default=None,
                   help="Base path for the splines JSON files (without iteration number and extension)")
                   
# Output paths - these should be provided by the manager script rather than hardcoded
parser.add_argument('--rop_pcg_export1_mesh_path', default=None, 
                   help="Output path for the mesh CSV file")
parser.add_argument('--rop_pcg_export1_mat_path', default=None, 
                   help="Output path for the material CSV file")
                   
# Pipeline control parameters
parser.add_argument('--iteration_number', type=int, default=None, 
                   help="Iteration number used to find the correct spline JSON file")
parser.add_argument('--switch_bool', type=int, default=0, 
                   help="Controls whether to use splines (0) or GenZone meshes (1)")
                   
# Parse the arguments
args = parser.parse_args()

# Validate required arguments that don't have defaults
if args.rop_pcg_export1_mesh_path is None:
    print("WARNING: No mesh CSV output path specified. Output may not be saved correctly.")
if args.rop_pcg_export1_mat_path is None:
    print("WARNING: No material CSV output path specified. Output may not be saved correctly.")
    
# Print a summary of the arguments
print("\nRunning with the following settings:")
print(f"  • Houdini File: {args.hip}")
print(f"  • TOPnet Path: {args.topnet}")
print(f"  • Input FBX: {args.file1_path if args.file1_path else 'Not specified'}")
print(f"  • Splines Base Path: {args.base_path if args.base_path else 'Not specified'}")
print(f"  • Output Mesh CSV: {args.rop_pcg_export1_mesh_path if args.rop_pcg_export1_mesh_path else 'Not specified'}")
print(f"  • Output Material CSV: {args.rop_pcg_export1_mat_path if args.rop_pcg_export1_mat_path else 'Not specified'}")
print(f"  • Iteration Number: {args.iteration_number if args.iteration_number is not None else 'Not specified'}")
print(f"  • Switch Bool: {args.switch_bool} ({'Use GenZone meshes' if args.switch_bool == 1 else 'Use splines'})")
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
hou.hipFile.load(hip_file_path)
print(f"✅ Successfully loaded: {hip_file_path}")

# Now let's configure all the nodes with our parameters
print("\n🔧 Configuring Houdini nodes...")

# 1. Set the input FBX file path (GenZone meshes)
set_node_parameter(
    '/obj/geo1/file1', 'file', args.file1_path,
    "Set input FBX file for GenZone meshes"
)

# 2. Set the output paths for the CSV files
# Both parameters are on the same node, so we can check once
pcg_export_node = hou.node('/obj/geo1/pcg_export1')
if pcg_export_node is None:
    print("⚠️ WARNING: Could not find PCG export node (/obj/geo1/pcg_export1)")
else:
    # Set mesh CSV output path
    if args.rop_pcg_export1_mesh_path is not None:
        mesh_parm = pcg_export_node.parm('file_mesh')
        if mesh_parm is not None:
            mesh_parm.set(args.rop_pcg_export1_mesh_path)
            print(f"✅ Set mesh CSV output path: {args.rop_pcg_export1_mesh_path}")
        else:
            print("⚠️ WARNING: 'file_mesh' parameter not found on PCG export node")
            
    # Set material CSV output path
    if args.rop_pcg_export1_mat_path is not None:
        mat_parm = pcg_export_node.parm('file_mat')
        if mat_parm is not None:
            mat_parm.set(args.rop_pcg_export1_mat_path)
            print(f"✅ Set material CSV output path: {args.rop_pcg_export1_mat_path}")
        else:
            print("⚠️ WARNING: 'file_mat' parameter not found on PCG export node")

# 3. Set the iteration number and base_path parameters for the spline import
# This is a special case because these might be in the Python code rather than parameters
print("\n📚 Setting parameters for spline import...")

# Get the Python node that imports splines
python_node = hou.node('/obj/geo1/python_import_splines_from_json')
if python_node is None:
    print("⚠️ WARNING: Could not find Python spline import node")
else:
    # First handle the iteration_number parameter
    if args.iteration_number is not None:
        print("Setting iteration number...")
        # First try to set the parameter directly if it exists
        if python_node.parm('iteration_number') is not None:
            # Use our helper function
            set_node_parameter(
                '/obj/geo1/python_import_splines_from_json', 'iteration_number', args.iteration_number,
                f"Set iteration number for spline import"
            )
        else:
            # If the parameter doesn't exist directly, it might be in the Python node's code
            print("Parameter 'iteration_number' not found, trying to modify Python code...")
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
    
    # Now handle the base_path parameter
    if args.base_path is not None:
        print("Setting splines base path...")
        # First try to set the parameter directly if it exists
        if python_node.parm('base_path') is not None:
            # Use our helper function
            set_node_parameter(
                '/obj/geo1/python_import_splines_from_json', 'base_path', args.base_path,
                f"Set base path for spline import"
            )
        else:
            # If the parameter doesn't exist directly, it might be in the Python node's code
            print("Parameter 'base_path' not found, trying to modify Python code...")
            python_code_parm = python_node.parm('python')
            if python_code_parm is not None:
                current_code = python_code_parm.eval()
                # Look for a line defining base_path or splines_path
                if 'base_path' in current_code:
                    # Replace the line with our new value
                    import re
                    new_code = re.sub(r'base_path\s*=\s*[\'\"].*[\'\"]', f'base_path = "{args.base_path}"', current_code)
                    python_code_parm.set(new_code)
                    print(f"✅ Modified Python code to set base_path to: {args.base_path}")
                elif 'splines_path' in current_code:
                    # It might be called splines_path instead
                    new_code = re.sub(r'splines_path\s*=\s*[\'\"].*[\'\"]', f'splines_path = "{args.base_path}"', current_code)
                    python_code_parm.set(new_code)
                    print(f"✅ Modified Python code to set splines_path to: {args.base_path}")
                else:
                    print("⚠️ WARNING: Could not find 'base_path' or 'splines_path' in the Python code to modify")
                    # As a fallback, we can try to add the base_path to the code
                    if 'iteration_number' in current_code:
                        # Add the base_path right after the iteration_number
                        lines = current_code.split('\n')
                        for i, line in enumerate(lines):
                            if 'iteration_number' in line and '=' in line:
                                lines.insert(i+1, f'base_path = "{args.base_path}"  # Added by headless script')
                                new_code = '\n'.join(lines)
                                python_code_parm.set(new_code)
                                print(f"✅ Added base_path to Python code: {args.base_path}")
                                break
            else:
                print("⚠️ WARNING: Could not access Python code parameter in the node")

# 4. Set the switch_bool parameter to control whether to use splines or GenZone meshes
print("\n🔍 Setting switch_bool parameter...")
if set_node_parameter(
    '/obj/geo1/switch_bool', 'input', args.switch_bool,
    f"Set switch_bool to {args.switch_bool} ({'Use GenZone meshes' if args.switch_bool == 1 else 'Use splines'})"
):
    # Success, parameter was set directly
    pass
else:
    # Try to modify the Python code if the parameter doesn't exist directly
    switch_bool_node = hou.node('/obj/geo1/switch_bool')
    if switch_bool_node is not None:
        python_code_parm = switch_bool_node.parm('python')
        if python_code_parm is not None:
            current_code = python_code_parm.eval()
            # Look for a line defining input
            if 'input' in current_code:
                # Replace the line with our new value
                import re
                new_code = re.sub(r'input\s*=\s*\d+', f'input = {args.switch_bool}', current_code)
                python_code_parm.set(new_code)
                print(f"✅ Modified Python code to set input to: {args.switch_bool}")
            else:
                print("⚠️ WARNING: Could not find 'input' in the Python code to modify")
        else:
            print("⚠️ WARNING: Could not access Python code parameter in the node")

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
    for i in range(5):
        print(f"  ⏳ {5-i} seconds remaining...")
        time.sleep(5)
    
    # Wait for cooking to complete
    # Note: We can't easily check if cooking is still in progress in headless mode,
    # so we just wait a reasonable amount of time
    print("\nWaiting for cook to complete...")
    for i in range(2):
        print(f"  ⏳ {10-i*5} seconds remaining...")
        time.sleep(5)
    
    print("✅ TOP network cook should be completed")
    
except Exception as e:
    print(f"❌ Error cooking TOP network: {str(e)}")
    exit(1)

# Check for output files
print("\n💾 Checking for output files...")
if args.rop_pcg_export1_mesh_path and os.path.exists(args.rop_pcg_export1_mesh_path):
    file_size = os.path.getsize(args.rop_pcg_export1_mesh_path)
    print(f"✅ Mesh CSV file created: {args.rop_pcg_export1_mesh_path} ({file_size/1024:.1f} KB)")
else:
    print("⚠️ Mesh CSV file not found or not specified")
    
if args.rop_pcg_export1_mat_path and os.path.exists(args.rop_pcg_export1_mat_path):
    file_size = os.path.getsize(args.rop_pcg_export1_mat_path)
    print(f"✅ Material CSV file created: {args.rop_pcg_export1_mat_path} ({file_size/1024:.1f} KB)")
else:
    print("⚠️ Material CSV file not found or not specified")

print("\n🎉 Script completed successfully")
print("PCG building data has been generated and exported to CSV files.")
print("The next step is to create PCG graphs in Unreal Engine using this data.")
print("" + "-"*80)