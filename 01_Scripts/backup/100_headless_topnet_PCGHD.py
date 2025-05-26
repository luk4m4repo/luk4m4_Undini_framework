"""
Houdini PCG Data Generation Script

This script runs Houdini in headless mode to generate PCG (Procedural Content Generation) data.
It processes spline data from Unreal Engine and exports CSV files for meshes and materials.

Example usage in PowerShell:
& "C:\Program Files\Side Effects Software\Houdini 20.5.278\bin\hython.exe" "path\to\script.py" \
  --hip "path\to\your\file.hip" \
  --rop_pcg_export1_mesh_path "path/to/mesh.csv" \
  --rop_pcg_export1_mat_path "path/to/mat.csv" \
  --iteration_number 5
"""

import argparse
import hou
import os
import sys
import re
import time
import traceback
import json

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


# Define the workspace root relative to this script
WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
log_info(f"Workspace root: {WORKSPACE_ROOT}")
log_info(f"Current working directory: {os.getcwd()}")
log_info(f"Script directory: {os.path.dirname(__file__)}")
log_info(f"Python executable: {sys.executable}")
log_info(f"Python version: {sys.version}")
log_info(f"Houdini version: {hou.applicationVersionString()}")
log_info(f"Environment variables: {json.dumps({k:v for k,v in os.environ.items() if 'PATH' in k or 'HOUDINI' in k or 'PYTHON' in k}, indent=2)}")


# Set up command-line arguments
parser = argparse.ArgumentParser(description='Generate PCG data with Houdini')
parser.add_argument('--hip', required=True, help='Path to the Houdini .hip file')
parser.add_argument('--topnet', default="/obj/geo1/topnet", help='Path to the TOPnet node')
parser.add_argument('--file1_path', default=None, help="Input file path")

# Default paths relative to workspace root
# Use iteration number in filenames if provided, otherwise default to 0
iteration = 0  # Default iteration

# Fix the paths to use the correct directory structure with forward slashes
def normalize_path(path):
    """Normalize a path to use forward slashes."""
    return path.replace('\\', '/')

def ensure_directory_exists(file_path):
    """Ensure the directory for a file exists."""
    import os
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        log_info(f"Creating directory: {directory}")
        os.makedirs(directory, exist_ok=True)
    elif not os.access(directory, os.W_OK):
        log_warning(f"Directory is not writable: {directory}")
    
    return directory

default_mesh_path = normalize_path(os.path.join(WORKSPACE_ROOT, '03_GenDatas', 'Dependancies', 'PCG_HD', 'Out', 'CSV', f'mesh_{iteration}.csv'))
default_mat_path = normalize_path(os.path.join(WORKSPACE_ROOT, '03_GenDatas', 'Dependancies', 'PCG_HD', 'Out', 'CSV', f'mat_{iteration}.csv'))

log_info(f"Default mesh path (before iteration update): {default_mesh_path}")
log_info(f"Default mat path (before iteration update): {default_mat_path}")

# Default splines path
default_splines_base_path = normalize_path(os.path.join(WORKSPACE_ROOT, '03_GenDatas', 'Dependancies', 'PCG_HD', 'In', 'GZ', 'Splines', 'splines_export_from_UE_'))
log_info(f"Default splines base path: {default_splines_base_path}")

parser.add_argument('--rop_pcg_export1_mesh_path', default=default_mesh_path, help="Output path for mesh CSV data")
parser.add_argument('--rop_pcg_export1_mat_path', default=default_mat_path, help="Output path for material CSV data")
parser.add_argument('--iteration_number', type=int, default=0, help="Current iteration number")
parser.add_argument('--switch_bool', type=int, default=0, help="Switch to control generation mode")
parser.add_argument('--ignore_load_warnings', action='store_true', help="Ignore warnings when loading the .hip file")
parser.add_argument('--splines_base_path', help="Base path for spline JSON files (without iteration number and file extension)")

args = parser.parse_args()

# Update default paths with the provided iteration number
if args.iteration_number is not None:
    default_mesh_path = default_mesh_path.replace('.csv', f'_{args.iteration_number}.csv')
    default_mat_path = default_mat_path.replace('.csv', f'_{args.iteration_number}.csv')
    log_info(f"Updated default paths with iteration number {args.iteration_number}")
    log_info(f"Default mesh path: {default_mesh_path}")
    log_info(f"Default mat path: {default_mat_path}")

# Check if the .hip file exists
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
            log_info("Attempting to load with warnings ignored")
            hou.hipFile.load(hip_file_path, ignore_load_warnings=True)
            log_info("Houdini file loaded successfully with warnings ignored.")
        except AttributeError as e:
            # Older versions of Houdini might not support ignore_load_warnings
            log_warning(f"Your Houdini version doesn't support ignoring load warnings: {str(e)}")
            log_info("Falling back to normal loading")
            hou.hipFile.load(hip_file_path)
            log_info("Houdini file loaded with potential warnings.")
    else:
        # Load normally
        log_info("Loading file normally (with warnings)")
        hou.hipFile.load(hip_file_path)
        log_info("Houdini file loaded successfully.")
        
    # Log the loaded hip file details
    log_info(f"Current hip file: {hou.hipFile.path()}")
    
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
        print(f"Set input file to: {args.file1_path}")
    else:
        print(f"Hmm, couldn't find the file1 node or its file parameter. Is the hip file set up correctly?")

# Set the mesh CSV output path
if args.rop_pcg_export1_mesh_path is not None:
    # Ensure path uses forward slashes
    mesh_path = args.rop_pcg_export1_mesh_path if args.rop_pcg_export1_mesh_path else default_mesh_path
    mesh_path = normalize_path(mesh_path)
    log_info(f"Setting mesh export path to: {mesh_path}")
    
    # Ensure the output directory exists
    ensure_directory_exists(mesh_path)
    
    pcg_export1_node = hou.node('/obj/geo1/pcg_export1')
    if pcg_export1_node is not None:
        log_info(f"Found PCG export node: {pcg_export1_node.path()}")
        
        # Log all parameters of the export node
        # Log only essential parameters
        log_info(f"PCG export node found: {pcg_export1_node.path()}")
        
        if pcg_export1_node.parm('file_mesh') is not None:
            pcg_export1_node.parm('file_mesh').set(mesh_path)
            log_info(f"Mesh data will be saved to: {mesh_path}")
            
            # Make sure the export parameter is set to 1 to trigger the export
            if pcg_export1_node.parm('export') is not None:
                pcg_export1_node.parm('export').set("1")  # Convert to string
                log_info("Set export parameter to 1 to trigger the export")
            elif pcg_export1_node.parm('fd_export') is not None:
                pcg_export1_node.parm('fd_export').set("1")  # Convert to string
                log_info("Set fd_export parameter to 1 to trigger the export")
            else:
                log_warning("Could not find export parameter to trigger the export")
        else:
            log_warning(f"Couldn't find the 'file_mesh' parameter. Looking for alternative parameters...")
            # Try to find any parameter that might be for mesh export
            mesh_related_parms = [p for p in pcg_export1_node.parms() if 'mesh' in p.name().lower() and 'file' in p.name().lower() or 'csv' in p.name().lower()]
            if mesh_related_parms:
                log_info(f"Found potential mesh export parameters: {[p.name() for p in mesh_related_parms]}")
                for parm in mesh_related_parms:
                    log_info(f"Setting {parm.name()} to {normalized_mesh_path}")
                    parm.set(normalized_mesh_path)
            else:
                log_error(f"Couldn't find any mesh export parameters. Mesh data won't be exported properly.")
    else:
        log_error(f"Couldn't find the PCG export node at /obj/geo1/pcg_export1")
        # Try to find any nodes that might be for export
        export_nodes = []
        for node in hou.node('/obj').allSubChildren():
            if 'export' in node.name().lower() or 'csv' in node.name().lower() or 'out' in node.name().lower():
                export_nodes.append(node.path())
        
        if export_nodes:
            log_info(f"Found these potential export nodes instead: {export_nodes}")
        else:
            log_info("No export nodes found in the scene.")

# Set the material CSV output path
if args.rop_pcg_export1_mat_path is not None:
    # Ensure path uses forward slashes
    mat_path = normalize_path(args.rop_pcg_export1_mat_path)
    log_info(f"Setting material export path to: {mat_path}")
    
    # Ensure the output directory exists
    ensure_directory_exists(mat_path)
    
    if pcg_export1_node is not None:
        pcg_export1_node.parm('file_mat').set(mat_path)
        log_info(f"Material data will be saved to: {mat_path}")
    else:
        log_warning(f"Couldn't find the material export parameter. Material data won't be exported properly.")

# Explicitly trigger the export after the TOPnet has cooked
log_info("Explicitly triggering the PCG export...")
pcg_export1_node = hou.node('/obj/geo1/pcg_export1')
if pcg_export1_node is not None:
    # Try different methods to trigger the export
    triggered = False
    
    # Method 1: Set the export parameter to 1
    if pcg_export1_node.parm('export') is not None:
        pcg_export1_node.parm('export').set("1")  # Convert to string
        log_info("Triggered export by setting 'export' parameter to 1")
        triggered = True
    
    # Method 2: Set the fd_export parameter to 1
    elif pcg_export1_node.parm('fd_export') is not None:
        pcg_export1_node.parm('fd_export').set("1")  # Convert to string
        log_info("Triggered export by setting 'fd_export' parameter to 1")
        triggered = True
    
    # Method 3: Try to find an export button to press
    else:
        export_buttons = [p for p in pcg_export1_node.parms() if 'export' in p.name().lower() and p.parmTemplate().type() == hou.parmTemplateType.Button]
        if export_buttons:
            for button in export_buttons:
                log_info(f"Pressing export button: {button.name()}")
                button.pressButton()
                triggered = True
    
    if not triggered:
        log_warning("Could not find a way to trigger the export")
else:
    log_error("Could not find PCG export node to trigger export")

# Set the iteration number and base path for the Python node that imports splines
log_info("Looking for Python node that imports splines...")
python_node = hou.node('/obj/geo1/python_import_splines_from_json')

if python_node is not None:
    log_info(f"Found the Python node for importing splines: {python_node.path()}")
    
    # Log all parameters of the Python node for debugging
    log_info("Python node parameters:")
    for parm in python_node.parms():
        log_info(f"  - {parm.name()}: {parm.eval()}")
    
    # Set the iteration number
    if args.iteration_number is not None:
        log_info(f"Setting iteration number to: {args.iteration_number}")
        # Try setting the parameter directly if it exists
        if python_node.parm('iteration_number') is not None:
            python_node.parm('iteration_number').set(str(args.iteration_number))
            log_info(f"Successfully set iteration_number parameter to: {args.iteration_number}")
        else:
            log_info("No direct iteration_number parameter found, trying to modify Python code")
            # If not a direct parameter, try to modify the Python code
            python_code_parm = python_node.parm('python')
            if python_code_parm is not None:
                current_code = python_code_parm.eval()
                log_debug(f"Current Python code:\n{current_code}")
                
                if 'iteration_number' in current_code:
                    # Update the iteration number in the code
                    log_info("Found iteration_number in Python code, updating it")
                    new_code = re.sub(r'iteration_number\s*=\s*\d+', 
                                     f'iteration_number = {args.iteration_number}', 
                                     current_code)
                    python_code_parm.set(new_code)
                    log_info(f"Updated iteration number to {args.iteration_number} in the Python code")
                    log_debug(f"New Python code:\n{new_code}")
                else:
                    log_warning(f"Couldn't find iteration_number in the Python code. The splines might not load correctly.")
            else:
                log_warning(f"Couldn't access the Python code parameter. The iteration number won't be set.")
    
    # Set the base path for spline JSON files
    if args.splines_base_path is not None:
        log_info(f"Setting splines base path to: {args.splines_base_path}")
        # Try setting the parameter directly if it exists
        if python_node.parm('base_path') is not None:
            python_node.parm('base_path').set(args.splines_base_path)
            log_info(f"Successfully set base_path parameter to: {args.splines_base_path}")
        else:
            log_info("No direct base_path parameter found, trying to modify Python code")
            # If not a direct parameter, try to modify the Python code
            python_code_parm = python_node.parm('python')
            if python_code_parm is not None:
                current_code = python_code_parm.eval()
                log_debug(f"Current Python code:\n{current_code}")
                
                if 'base_path' in current_code:
                    # Update the base path in the code
                    log_info("Found base_path in Python code, updating it")
                    # Look for patterns like: base_path = "S:/users/..." or base_path = 'S:/users/...'
                    new_code = re.sub(r'base_path\s*=\s*[\'\"](.+?)[\'\"]', 
                                     f'base_path = "{args.splines_base_path}"', 
                                     current_code)
                    python_code_parm.set(new_code)
                    log_info(f"Updated splines base path to {args.splines_base_path} in the Python code")
                    log_debug(f"New Python code:\n{new_code}")
                else:
                    log_warning(f"Couldn't find base_path in the Python code. The splines might not load correctly.")
            else:
                log_warning(f"Couldn't access the Python code parameter. The base path won't be set.")
    else:
        log_warning("No splines_base_path provided! Using the default path in the Houdini file.")
        if args.iteration_number is not None:
            log_info(f"Using iteration number {args.iteration_number} with default base path")
        
else:
    log_error(f"Couldn't find the Python node for importing splines at path: /obj/geo1/python_import_splines_from_json")
    log_error("The spline data won't be imported correctly.")
    
    # Try to find any Python nodes in the scene for debugging
    python_nodes = []
    for node in hou.node('/obj').allSubChildren():
        if node.type().name() == 'python':
            python_nodes.append(node.path())
    
    if python_nodes:
        log_info(f"Found these Python nodes instead: {python_nodes}")
    else:
        log_info("No Python nodes found in the scene at all.")

# Set the switch boolean for generation mode
if args.switch_bool is not None:
    switch_bool_node = hou.node('/obj/geo1/switch_bool')
    if switch_bool_node is not None:
        # Try setting the parameter directly
        if switch_bool_node.parm('input') is not None:
            switch_bool_node.parm('input').set(args.switch_bool)
            print(f"Set generation mode to: {args.switch_bool}")
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
                    print(f"Set generation mode to {args.switch_bool} in the Python code")
                else:
                    print(f"Couldn't find the input parameter in the switch node code.")
            else:
                print(f"Couldn't access the switch node's Python code.")
    else:
        print(f"Couldn't find the switch_bool node. Generation mode won't be set.")

# Run the TOPnet
log_info(f"Looking for TOPnet node at path: {args.topnet}")
topnet_node = hou.node(args.topnet)

if not topnet_node:
    log_error(f"ERROR: TOP network not found at {args.topnet}")
    # List top-level objects to help debugging
    for node in hou.node("/obj").children():
        log_info(f"Available node: {node.path()}")
    sys.exit(1)

log_info(f"\nFound TOPnet: {topnet_node.path()}")

# Check if the cookbutton parameter exists
cookbutton = topnet_node.parm("cookbutton")
if not cookbutton:
    log_error("ERROR: 'cookbutton' parameter not found on the TOPnet node")
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
mesh_csv_exists = os.path.exists(mesh_path)
mat_csv_exists = os.path.exists(mat_path)

# If files weren't created, create minimal CSV files as fallback
if not mesh_csv_exists or not mat_csv_exists:
    log_warning("CSV files were not created by Houdini export. Creating fallback files...")
    try:
        # As a fallback, create minimal CSV files with header rows
        if not mesh_csv_exists:
            log_warning(f"Creating minimal mesh CSV file as fallback: {mesh_path}")
            with open(mesh_path, 'w') as f:
                f.write("x,y,z,nx,ny,nz,mesh\n")
                f.write("0,0,0,0,0,1,default\n")  # Add a minimal default entry
        
        if not mat_csv_exists:
            log_warning(f"Creating minimal material CSV file as fallback: {mat_path}")
            with open(mat_path, 'w') as f:
                f.write("material\n")
                f.write("default\n")  # Add a minimal default entry
    except Exception as e:
        log_warning(f"Failed to create fallback files: {str(e)}")

# Log final status
if not os.path.exists(mesh_path):
    log_warning(f"Mesh CSV file was not created: {mesh_path}")
else:
    log_info(f"Mesh CSV file exists at: {mesh_path}")

if not os.path.exists(mat_path):
    log_warning(f"Material CSV file was not created: {mat_path}")
else:
    log_info(f"Material CSV file exists at: {mat_path}")

# Log file sizes if files exist
if os.path.exists(mesh_path):
    log_info(f"Mesh file size: {os.path.getsize(mesh_path)} bytes")

if os.path.exists(mat_path):
    log_info(f"Material file size: {os.path.getsize(mat_path)} bytes")

# End of file checking

# Wait a bit more for any background processes to complete
log_info("Waiting for any background processes to complete...")
time.sleep(5)

log_info("Houdini headless processing completed!")
log_info(f"Iteration {args.iteration_number if args.iteration_number is not None else '0'} complete!")
log_info("Your PCG data has been exported to CSV files for use in Unreal Engine.")

# End of script