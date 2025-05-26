import unreal
import os
import sys
import subprocess
import json
import time
import importlib.util

# ======================================================================
# Configuration - Modify these values as needed
# ======================================================================

# Set your project paths
WORKSPACE_ROOT = r"C:/Users/luka.croisez/Documents/GitHub/lcroisez_Undini_framework"
SCRIPTS_DIR = os.path.join(WORKSPACE_ROOT, "01_Scripts")

# Iteration number for file naming
ITERATION_NUMBER = 5  # Change this as needed

SWITCH_BOOL = 0

# Unreal Engine paths
UE_BASE_PATH = "/Game/luk4m4_Undini"
UE_PCG_TEMPLATE_BP_PATH = f"{UE_BASE_PATH}/BP/BP_PCG_HD_TEMPLATE"
UE_SPLINE_BP_PATH = f"{UE_BASE_PATH}/BP/BP_CityKit_spline"
UE_MESH_TEMPLATE_PATH = f"{UE_BASE_PATH}/CSV/mesh_template"
UE_MAT_TEMPLATE_PATH = f"{UE_BASE_PATH}/CSV/mat_template"

# Houdini paths
HOUDINI_INSTALL_PATH = r"C:/Program Files/Side Effects Software/Houdini 20.0.653"
# HIP file for PCG generation
HIP_FILE_PATH = r"C:/Users/luka.croisez/Documents/GitHub/lcroisez_Undini_framework/04_Houdini/genbuildingbase3.hip"
# HIP file for sidewalks and roads generation
SWR_HIP_FILE_PATH = r"C:/Users/luka.croisez/Documents/GitHub/lcroisez_Undini_framework/04_Houdini/sidewalks_roads.hip"

# Output directories
SPLINES_OUTPUT_DIR = os.path.join(WORKSPACE_ROOT, "03_GenDatas", "Dependancies", "PCG_HD", "In", "GZ", "Splines")
CSV_OUTPUT_DIR = os.path.join(WORKSPACE_ROOT, "03_GenDatas", "Dependancies", "PCG_HD", "Out", "CSV")
FBX_OUTPUT_DIR = os.path.join(WORKSPACE_ROOT, "03_GenDatas", "Dependancies", "PCG_HD", "Out", "FBX")
# Directory for sidewalks and roads FBX files
SWR_FBX_OUTPUT_DIR = os.path.join(WORKSPACE_ROOT, "03_GenDatas", "Dependancies", "SW_Roads", "Out", "Mod")

# Create necessary directories
for directory in [SPLINES_OUTPUT_DIR, CSV_OUTPUT_DIR, FBX_OUTPUT_DIR, SWR_FBX_OUTPUT_DIR]:
    os.makedirs(directory, exist_ok=True)

# ======================================================================
# Script Runner Function
# ======================================================================

def run_script(script_name, function_name, **kwargs):
    """
    Run a function from a script file with the given arguments
    
    Args:
        script_name (str): Name of the script file (e.g., "000_export_splines_as_json.py")
        function_name (str): Name of the function to call
        **kwargs: Arguments to pass to the function
    """
    try:
        # Full path to the script
        script_path = os.path.join(SCRIPTS_DIR, script_name)
        
        # Import the module dynamically
        module_name = os.path.splitext(script_name)[0]
        spec = importlib.util.spec_from_file_location(module_name, script_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        
        # Get the function
        if hasattr(module, function_name):
            func = getattr(module, function_name)
            
            # Call the function with the provided arguments
            unreal.log(f"Running {function_name} from {script_name} with args: {kwargs}")
            result = func(**kwargs)
            unreal.log(f"Result: {result}")
            return result
        else:
            unreal.log_error(f"Function '{function_name}' not found in {script_name}")
            return None
    except Exception as e:
        unreal.log_error(f"Error running {script_name}: {str(e)}")
        return None

# ======================================================================
# Script Functions - Uncomment the ones you want to run
# ======================================================================

# Export splines to JSON
#result = run_script("000_export_splines_as_json.py", "export_splines_to_json", 
#         iteration_number=ITERATION_NUMBER, 
#         output_dir=SPLINES_OUTPUT_DIR)
#unreal.log(f"Splines export result: {result}")

# Export GenZone meshes
#result = run_script("010_export_gz_to_mod.py", "main", 
#         iteration_number=ITERATION_NUMBER)
#unreal.log(f"GenZone export result: {result}")

# Run Houdini PCG generation

def run_houdini_headless(iteration_number, houdini_install_path, hip_file_path):
    """Run Houdini in headless mode to generate PCG data"""
    try:
        unreal.log(f"Starting Houdini headless process with iteration number: {iteration_number}")
        unreal.log(f"Houdini install path: {houdini_install_path}")
        unreal.log(f"Hip file path: {hip_file_path}")
        
        # Check if the hip file exists
        if not os.path.exists(hip_file_path):
            unreal.log_error(f"Houdini .hip file not found at: {hip_file_path}")
            return None
        else:
            unreal.log(f"Houdini .hip file found at: {hip_file_path}")
        
        # Get the path to the Houdini Python interpreter (hython)
        hython_path = os.path.join(houdini_install_path, "bin", "hython.exe")
        if not os.path.exists(hython_path):
            unreal.log_error(f"Hython not found at: {hython_path}")
            return None
        else:
            unreal.log(f"Hython found at: {hython_path}")
            
        # Get the path to the headless script
        headless_script = os.path.join(SCRIPTS_DIR, "100_headless_topnet_PCGHD.py")
        if not os.path.exists(headless_script):
            unreal.log_error(f"Headless script not found at: {headless_script}")
            return None
        else:
            unreal.log(f"Headless script found at: {headless_script}")
            
        # Helper function to normalize paths to use forward slashes
        def normalize_path(path):
            """Convert Windows path to use forward slashes"""
            return path.replace('\\', '/')
            
        # Define input/output paths with forward slashes for Houdini
        mesh_csv_path = normalize_path(os.path.join(CSV_OUTPUT_DIR, f"mesh_{iteration_number}.csv"))
        mat_csv_path = normalize_path(os.path.join(CSV_OUTPUT_DIR, f"mat_{iteration_number}.csv"))
        
        # Define the splines base path (without iteration number and file extension)
        splines_base_path = normalize_path(os.path.join(SPLINES_OUTPUT_DIR, "splines_export_from_UE_"))
        
        # Ensure output directories exist
        os.makedirs(os.path.dirname(mesh_csv_path), exist_ok=True)
        os.makedirs(os.path.dirname(mat_csv_path), exist_ok=True)
        os.makedirs(SPLINES_OUTPUT_DIR, exist_ok=True)
        
        # Log the normalized paths
        unreal.log(f"Normalized mesh CSV path: {mesh_csv_path}")
        unreal.log(f"Normalized material CSV path: {mat_csv_path}")
        unreal.log(f"Normalized splines base path: {splines_base_path}")
        
        # Build the command to run Houdini in headless mode
        cmd = [
            hython_path,
            headless_script,
            "--hip", hip_file_path,
            "--topnet", "/obj/geo1/topnet",
            "--rop_pcg_export1_mesh_path", mesh_csv_path,
            "--rop_pcg_export1_mat_path", mat_csv_path,
            "--iteration_number", str(iteration_number),
            "--switch_bool", str(SWITCH_BOOL)
            # Remove arguments that aren't recognized by the original script
            # "--ignore_load_warnings",
            # "--splines_base_path", splines_base_path
        ]
        
        unreal.log(f"Launching Houdini in headless mode...")
        unreal.log(f"Command: {' '.join(cmd)}")
        
        # Check if the hip file exists
        if not os.path.exists(hip_file_path):
            unreal.log_error(f"Houdini .hip file not found at: {hip_file_path}")
            return None
            
        # Check if the splines directory exists and has files
        splines_dir = os.path.dirname(splines_base_path)
        if not os.path.exists(splines_dir):
            unreal.log_warning(f"Splines directory does not exist: {splines_dir}")
            os.makedirs(splines_dir, exist_ok=True)
        else:
            # Check for the specific spline file we're expecting
            expected_spline_file = f"splines_export_from_UE_{iteration_number}.json"
            spline_files = [f for f in os.listdir(splines_dir) if f.endswith('.json')]
            if expected_spline_file not in spline_files:
                unreal.log_warning(f"Expected spline file not found: {expected_spline_file}")
                unreal.log_warning(f"You may need to run the spline export script first")
        
        # Run the command without creating a new console, to capture output
        unreal.log("Running Houdini process and capturing output...")
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        # Wait a short time and check if process is still running
        time.sleep(2)
        if process.poll() is not None:
            # Process has already terminated
            stdout, stderr = process.communicate()
            unreal.log_error(f"Houdini process terminated immediately with exit code: {process.returncode}")
            unreal.log(f"STDOUT: {stdout}")
            unreal.log_error(f"STDERR: {stderr}")
            return None
        
        unreal.log(f"Houdini process started with PID: {process.pid}")
        unreal.log(f"Process is running. Waiting for completion...")
        
        # Wait for process to complete with a timeout
        try:
            stdout, stderr = process.communicate(timeout=30)  # 30 second timeout
            unreal.log(f"Houdini process completed with exit code: {process.returncode}")
            unreal.log(f"STDOUT: {stdout}")
            if stderr:
                unreal.log_error(f"STDERR: {stderr}")
        except subprocess.TimeoutExpired:
            unreal.log("Houdini process is still running after timeout. Continuing in background.")
            # Don't kill the process, let it continue running
        
        return {
            'process_id': process.pid,
            'mesh_csv_path': mesh_csv_path,
            'mat_csv_path': mat_csv_path,
            'status': 'running'
        }
    except Exception as e:
        unreal.log_error(f"Error launching Houdini: {str(e)}")
        return None


# Run Houdini PCG generation
# result = run_houdini_headless(
#     iteration_number=ITERATION_NUMBER,
#     houdini_install_path=HOUDINI_INSTALL_PATH,
#     hip_file_path=HIP_FILE_PATH
# )
# unreal.log(f"Houdini PCG generation result: {result}")

# Reimport datatables
#result = run_script("110_reimport_datatable.py", "reimport_datatables",
#         iteration_number=ITERATION_NUMBER,
#         csv_dir=CSV_OUTPUT_DIR)
#unreal.log(f"Reimport datatables result: {result}")

# Create PCG graph (uncomment to use)
#result = run_script("120_create_pcg_graph.py", "create_pcg_graph",
#         iteration_number=ITERATION_NUMBER,
#         template_bp_path=UE_PCG_TEMPLATE_BP_PATH)
#unreal.log(f"Create PCG graph result: {result}")

# Run Houdini sidewalks & roads generation (uncomment to use)
def run_houdini_sidewalks_roads(iteration_number, houdini_install_path, hip_file_path=None):
    # Use SWR_HIP_FILE_PATH if hip_file_path is not provided
    if hip_file_path is None:
        hip_file_path = SWR_HIP_FILE_PATH
    """Run Houdini in headless mode to generate sidewalks and roads"""
    try:
        unreal.log(f"Starting Houdini sidewalks & roads generation with iteration number: {iteration_number}")
        unreal.log(f"Houdini install path: {houdini_install_path}")
        unreal.log(f"Hip file path: {hip_file_path}")
        
        # Check if the hip file exists
        if not os.path.exists(hip_file_path):
            unreal.log_error(f"Houdini .hip file not found at: {hip_file_path}")
            return None
        else:
            unreal.log(f"Houdini .hip file found at: {hip_file_path}")
        
        # Get the path to the Houdini Python interpreter (hython)
        hython_path = os.path.join(houdini_install_path, "bin", "hython.exe")
        if not os.path.exists(hython_path):
            unreal.log_error(f"Hython not found at: {hython_path}")
            return None
        else:
            unreal.log(f"Hython found at: {hython_path}")
        
        # Get the path to the headless script
        headless_script = os.path.join(SCRIPTS_DIR, "200_headless_topnet_SWR.py")
        if not os.path.exists(headless_script):
            unreal.log_error(f"Headless script not found at: {headless_script}")
            return None
        else:
            unreal.log(f"Headless script found at: {headless_script}")
            
        # Helper function to normalize paths to use forward slashes
        def normalize_path(path):
            """Convert Windows path to use forward slashes"""
            return path.replace('\\', '/')
            
        # Define input/output paths with forward slashes for Houdini
        road_fbx_path = normalize_path(os.path.join(SWR_FBX_OUTPUT_DIR, f"road_{iteration_number}.fbx"))
        sidewalks_fbx_path = normalize_path(os.path.join(SWR_FBX_OUTPUT_DIR, f"sidewalks_{iteration_number}.fbx"))
        
        # Define the splines base path (without iteration number and file extension)
        splines_base_path = normalize_path(os.path.join(SPLINES_OUTPUT_DIR, "splines_export_from_UE_"))
        
        # Ensure output directories exist
        os.makedirs(os.path.dirname(road_fbx_path), exist_ok=True)
        os.makedirs(os.path.dirname(sidewalks_fbx_path), exist_ok=True)
        
        # Log the normalized paths
        unreal.log(f"Normalized road FBX path: {road_fbx_path}")
        unreal.log(f"Normalized sidewalks FBX path: {sidewalks_fbx_path}")
        unreal.log(f"Normalized splines base path: {splines_base_path}")
        
        # Build the command to run Houdini in headless mode
        # Important: Use a string with proper quoting instead of a list to avoid issues with script path parsing
        cmd_str = f'"{hython_path}" "{headless_script}" --hip "{hip_file_path}" --topnet "/obj/geo1/topnet" --rop_fbx_road_path "{road_fbx_path}" --rop_fbx_sidewalks_path "{sidewalks_fbx_path}" --iteration_number {iteration_number} --switch_bool {SWITCH_BOOL}'
        
        # Check if we need to add a file1_path parameter for input geometry
        splines_json_path = normalize_path(os.path.join(SPLINES_OUTPUT_DIR, f"splines_export_from_UE_{iteration_number}.json"))
        if os.path.exists(splines_json_path):
            cmd_str += f' --file1_path "{splines_json_path}"'
            unreal.log(f"Adding splines JSON file path: {splines_json_path}")
        
        # For logging purposes, also create the command as a list
        cmd_list = [
            hython_path,
            headless_script,
            "--hip", hip_file_path,
            "--topnet", "/obj/geo1/topnet",
            "--rop_fbx_road_path", road_fbx_path,
            "--rop_fbx_sidewalks_path", sidewalks_fbx_path,
            "--iteration_number", str(iteration_number),
            "--switch_bool", str(SWITCH_BOOL)
        ]
        
        # Add file1_path to cmd_list if it exists
        if os.path.exists(splines_json_path):
            cmd_list.extend(["--file1_path", splines_json_path])
        
        unreal.log(f"Launching Houdini sidewalks & roads generation...")
        unreal.log(f"Command: {' '.join(cmd_list)}")
        
        # Check if the splines directory exists and has files
        splines_dir = os.path.dirname(splines_base_path)
        if not os.path.exists(splines_dir):
            unreal.log_warning(f"Splines directory does not exist: {splines_dir}")
            os.makedirs(splines_dir, exist_ok=True)
        else:
            # Check for the specific spline file we're expecting
            expected_spline_file = f"splines_export_from_UE_{iteration_number}.json"
            spline_files = [f for f in os.listdir(splines_dir) if f.endswith('.json')]
            if expected_spline_file not in spline_files:
                unreal.log_warning(f"Expected spline file not found: {expected_spline_file}")
                unreal.log_warning(f"You may need to run the spline export script first")
                unreal.log_warning(f"Available spline files: {spline_files}")
        
        # Run the command - don't create a new console window when running from UE
        unreal.log("Running Houdini process...")
        process = subprocess.Popen(
            cmd_str,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            shell=True  # Required when passing a command string instead of a list
            # No creationflags - this causes issues when running as a subprocess from UE
        )
        
        # Wait a short time and check if process is still running
        time.sleep(2)
        if process.poll() is not None:
            # Process has already terminated
            stdout, stderr = process.communicate()
            unreal.log_error(f"Houdini process terminated immediately with exit code: {process.returncode}")
            unreal.log(f"STDOUT: {stdout}")
            unreal.log_error(f"STDERR: {stderr}")
            return None
        
        unreal.log(f"Houdini process started with PID: {process.pid}")
        unreal.log(f"Process is running. Waiting for completion...")
        
        # Wait for process to complete with a timeout
        try:
            stdout, stderr = process.communicate(timeout=30)  # 30 second timeout
            unreal.log(f"Houdini process completed with exit code: {process.returncode}")
            unreal.log(f"STDOUT: {stdout}")
            if stderr:
                unreal.log_error(f"STDERR: {stderr}")
        except subprocess.TimeoutExpired:
            unreal.log("Houdini process is still running after timeout. Continuing in background.")
            # Don't kill the process, let it continue running
        
        # Check if the output files were created
        road_fbx_exists = os.path.exists(road_fbx_path)
        sidewalks_fbx_exists = os.path.exists(sidewalks_fbx_path)
        
        if not road_fbx_exists:
            unreal.log_warning(f"Road FBX file was not created: {road_fbx_path}")
        else:
            unreal.log(f"Road FBX file exists at: {road_fbx_path}")
            unreal.log(f"File size: {os.path.getsize(road_fbx_path)} bytes")
        
        if not sidewalks_fbx_exists:
            unreal.log_warning(f"Sidewalks FBX file was not created: {sidewalks_fbx_path}")
        else:
            unreal.log(f"Sidewalks FBX file exists at: {sidewalks_fbx_path}")
            unreal.log(f"File size: {os.path.getsize(sidewalks_fbx_path)} bytes")
        
        return {
            'process_id': process.pid,
            'road_fbx_path': road_fbx_path,
            'sidewalks_fbx_path': sidewalks_fbx_path,
            'status': 'running' if process.poll() is None else 'completed',
            'road_fbx_exists': road_fbx_exists,
            'sidewalks_fbx_exists': sidewalks_fbx_exists
        }
    except Exception as e:
        unreal.log_error(f"Error launching Houdini: {str(e)}")
        return None

# Run Houdini sidewalks & roads generation
result = run_houdini_sidewalks_roads(
     iteration_number=ITERATION_NUMBER,
     houdini_install_path=HOUDINI_INSTALL_PATH,
     hip_file_path=SWR_HIP_FILE_PATH
)
unreal.log(f"Houdini sidewalks & roads generation result: {result}")

# Reimport static meshes
#result = run_script("210_reimport_SM.py", "reimport_folder_static_meshes",
#         iteration_number=ITERATION_NUMBER,
#         fbx_dir=SWR_FBX_OUTPUT_DIR)
#unreal.log(f"Reimport static meshes result: {result}")

# Add sidewalks & roads to level (uncomment to use)
# result = run_script("220_add_SM_to_lvl.py", "add_SM_sidewalks_and_roads_to_level",
#          iteration_number=ITERATION_NUMBER)
# unreal.log(f"Add sidewalks & roads result: {result}")

unreal.log("Script execution completed")