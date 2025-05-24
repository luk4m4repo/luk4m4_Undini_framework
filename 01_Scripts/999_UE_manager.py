"""
Unreal Engine Pipeline Manager Script

This script serves as the central manager for the entire Unreal Engine procedural generation pipeline.
It coordinates the execution of multiple scripts in sequence to generate procedural content:

1. Export GenZone meshes from Unreal Engine to FBX files
2. Process meshes in Houdini to generate PCG data
3. Generate sidewalks and roads in Houdini
4. Reimport CSV data into Unreal Engine DataTables
5. Export splines from Unreal Engine to JSON
6. Create and add PCG graph to the current level
7. Add sidewalks and roads to the current level
8. Reimport static meshes from FBX files

Each function can be called individually or the entire pipeline can be executed in sequence.

Example usage:
    - Set the desired iteration_number and paths below
    - Call the functions in sequence or individually
    - Monitor the progress through the log messages
"""

import unreal
import os
import subprocess
import time

# ======================================================================
# CONFIGURATION - MODIFY THESE SETTINGS AS NEEDED
# ======================================================================

# Current iteration number for the procedural generation
ITERATION_NUMBER = 0

# Houdini installation path
HOUDINI_INSTALL_PATH = r"C:/Program Files/Side Effects Software/Houdini 20.0.653"
HOUDINI_PYTHON_PATH = os.path.join(HOUDINI_INSTALL_PATH, "bin", "hython.exe")

# Houdini .hip file paths
HOUDINI_PCG_HIP_PATH = r"C:/Users/luka.croisez/Documents/Houdini/genbuildingbase3.hip"  # PCG generation
HOUDINI_SWR_HIP_PATH = r"C:/Users/luka.croisez/Documents/Houdini/sidewalks.hip"         # Sidewalks & Roads

# Topnet node paths in Houdini
HOUDINI_PCG_TOPNET_PATH = "/obj/geo1/topnet"
HOUDINI_SWR_TOPNET_PATH = "/obj/geo1/topnet"

# Switch boolean values for Houdini generation modes
PCG_SWITCH_BOOL_VALUE = 1
SWR_SWITCH_BOOL_VALUE = 1

# ======================================================================
# WORKSPACE SETUP - DO NOT MODIFY UNLESS NECESSARY
# ======================================================================

# Define the workspace root relative to this script
WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

# Define paths relative to the workspace root
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))

# ======================================================================
# GenZone Meshes Export Script
# ======================================================================

genzone_export_script = os.path.join(SCRIPTS_DIR, "010_export_gz_to_mod.py")

def call_export_genzone_meshes(iteration_number=None):
    """
    Run the GenZone Static Mesh export script with the given iteration_number.
    
    This function exports all static meshes with 'genzone' in the name to FBX files,
    appending the iteration_number to each exported file for proper versioning.
    
    Args:
        iteration_number (int, optional): The current iteration number to append to exported files.
                                          If None, uses the global ITERATION_NUMBER.
    
    Returns:
        bool: True if export was successful, False otherwise
    """
    # Use global configuration if parameter is not provided
    if iteration_number is None:
        iteration_number = ITERATION_NUMBER
    unreal.log(f"\n🏙️ === EXPORTING GENZONE MESHES (ITERATION {iteration_number}) === 🏙️")
    
    try:
        exec_globals = {}
        with open(genzone_export_script, 'r', encoding='utf-8') as f:
            code = f.read()
            exec(code, exec_globals)
            
            # Call main() from the export script with the provided iteration_number
            if 'main' in exec_globals:
                unreal.log(f"🔄 Starting GenZone mesh export process...")
                result = exec_globals['main'](iteration_number)
                unreal.log(f"✅ GenZone mesh export completed successfully!")
                return result
            else:
                unreal.log_error(f"❌ ERROR: 'main' function not found in export script: {genzone_export_script}")
                return False
    except Exception as e:
        unreal.log_error(f"❌ Error during GenZone mesh export: {str(e)}")
        return False

# Example usage with iteration number 5
# call_export_genzone_meshes(5)


# ======================================================================
# Houdini Headless Script - PCG HD (Procedural Content Generation)
# ======================================================================

def run_houdini_pcg_generation(iteration_number=None, switch_bool_value=None):
    """
    Run Houdini in headless mode to generate PCG (Procedural Content Generation) data.
    
    This function processes GenZone meshes exported from Unreal Engine and generates
    CSV files containing mesh and material data for PCG graphs.
    
    Args:
        iteration_number (int, optional): The current iteration number for file naming. If None, uses ITERATION_NUMBER.
        switch_bool_value (int, optional): Switch to control generation mode (0 or 1). If None, uses PCG_SWITCH_BOOL_VALUE.
        
    Returns:
        subprocess.Popen: The process object for the Houdini subprocess
    """
    # Use global configuration if parameters are not provided
    if iteration_number is None:
        iteration_number = ITERATION_NUMBER
    if switch_bool_value is None:
        switch_bool_value = PCG_SWITCH_BOOL_VALUE
        
    unreal.log(f"\n🌍 === RUNNING HOUDINI PCG GENERATION (ITERATION {iteration_number}) === 🌍")
    
    # Use paths from global configuration
    hython_path = HOUDINI_PYTHON_PATH
    houdini_script = os.path.join(SCRIPTS_DIR, "100_headless_topnet_PCGHD.py")
    hip_file_path = HOUDINI_PCG_HIP_PATH
    topnet_path = HOUDINI_PCG_TOPNET_PATH
    
    # Define input/output paths relative to workspace root
    gen_data_dir = os.path.join(WORKSPACE_ROOT, ".." , "03_GenDatas")
    
    # Input path for GenZone meshes
    file1_path = os.path.join(gen_data_dir, "Dependancies", "PCG_HD", "In", "GZ", "Mod", 
                             f"SM_genzones_PCG_HD_{iteration_number}.fbx")
    
    # Output paths for CSV files
    rop_pcg_export1_mesh_path = os.path.join(gen_data_dir, "Dependancies", "PCG_HD", "Out", "CSV", 
                                           f"mesh_{iteration_number}.csv")
    rop_pcg_export1_mat_path = os.path.join(gen_data_dir, "Dependancies", "PCG_HD", "Out", "CSV", 
                                          f"mat_{iteration_number}.csv")
    
    # Ensure directories exist
    os.makedirs(os.path.dirname(rop_pcg_export1_mesh_path), exist_ok=True)
    os.makedirs(os.path.dirname(rop_pcg_export1_mat_path), exist_ok=True)
    
    unreal.log(f"🔍 Input FBX: {file1_path}")
    unreal.log(f"📂 Output Mesh CSV: {rop_pcg_export1_mesh_path}")
    unreal.log(f"📂 Output Material CSV: {rop_pcg_export1_mat_path}")
    
    # Launch Houdini in headless mode
    unreal.log(f"🚀 Launching Houdini in headless mode...")
    process = subprocess.Popen([
        hython_path, 
        houdini_script, 
        "--hip", hip_file_path,
        "--topnet", topnet_path,
        "--file1_path", file1_path,
        "--rop_pcg_export1_mesh_path", rop_pcg_export1_mesh_path,
        "--rop_pcg_export1_mat_path", rop_pcg_export1_mat_path,
        "--iteration_number", str(iteration_number),
        "--switch_bool", str(switch_bool_value)
    ], creationflags=subprocess.CREATE_NEW_CONSOLE)
    
    unreal.log(f"📢 Houdini process started in a separate window")
    unreal.log(f"📚 Check the Houdini console window for detailed progress")
    
    return process

# Example usage with iteration number 5
# run_houdini_pcg_generation(5, 1)



# ======================================================================
# Houdini Headless Script - Sidewalks & Roads Generation
# ======================================================================

def run_houdini_sidewalks_roads_generation(iteration_number=None, switch_bool_value=None):
    """
    Run Houdini in headless mode to generate sidewalks and roads.
    
    This function processes spline data from Unreal Engine and generates
    FBX files for sidewalks and roads that can be imported back into Unreal.
    
    Args:
        iteration_number (int, optional): The current iteration number for file naming. If None, uses ITERATION_NUMBER.
        switch_bool_value (int, optional): Switch to control road generation mode (0 or 1). If None, uses SWR_SWITCH_BOOL_VALUE.
        
    Returns:
        subprocess.Popen: The process object for the Houdini subprocess
    """
    # Use global configuration if parameters are not provided
    if iteration_number is None:
        iteration_number = ITERATION_NUMBER
    if switch_bool_value is None:
        switch_bool_value = SWR_SWITCH_BOOL_VALUE
        
    unreal.log(f"\n🛣️ === RUNNING HOUDINI SIDEWALKS & ROADS GENERATION (ITERATION {iteration_number}) === 🛣️")
    
    # Use paths from global configuration
    hython_path = HOUDINI_PYTHON_PATH
    houdini_script = os.path.join(SCRIPTS_DIR, "200_headless_topnet_SWR.py")
    hip_file_path = HOUDINI_SWR_HIP_PATH
    topnet_path = HOUDINI_SWR_TOPNET_PATH
    
    # Define input/output paths relative to workspace root
    gen_data_dir = os.path.join(WORKSPACE_ROOT, ".." , "03_GenDatas")
    
    # Input path for GenZone meshes (same as PCG HD input)
    file1_path = os.path.join(gen_data_dir, "Dependancies", "PCG_HD", "In", "GZ", "Mod", 
                             f"SM_genzones_PCG_HD_{iteration_number}.fbx")
    
    # Output paths for FBX files
    sw_roads_dir = os.path.join(gen_data_dir, "Dependancies", "SW_Roads", "Out", "Mod")
    rop_fbx_road_path = os.path.join(sw_roads_dir, f"road_{iteration_number}.fbx")
    rop_fbx_sidewalks_path = os.path.join(sw_roads_dir, f"sidewalks_{iteration_number}.fbx")
    
    # Ensure output directory exists
    os.makedirs(sw_roads_dir, exist_ok=True)
    
    unreal.log(f"🔍 Input FBX: {file1_path}")
    unreal.log(f"📂 Output Road FBX: {rop_fbx_road_path}")
    unreal.log(f"📂 Output Sidewalks FBX: {rop_fbx_sidewalks_path}")
    
    # Launch Houdini in headless mode
    unreal.log(f"🚀 Launching Houdini in headless mode...")
    process = subprocess.Popen([
        hython_path,
        houdini_script,
        "--hip", hip_file_path,
        "--topnet", topnet_path,
        "--file1_path", file1_path,
        "--rop_fbx_road_path", rop_fbx_road_path,
        "--rop_fbx_sidewalks_path", rop_fbx_sidewalks_path,
        "--iteration_number", str(iteration_number),
        "--switch_bool", str(switch_bool_value)
    ], creationflags=subprocess.CREATE_NEW_CONSOLE)
    
    unreal.log(f"📢 Houdini process started in a separate window")
    unreal.log(f"📚 Check the Houdini console window for detailed progress")
    
    return process

# Example usage with iteration number 5
# run_houdini_sidewalks_roads_generation(5, 1)



# ======================================================================
# CSV Reimport for DataTables
# ======================================================================

def call_reimport_all_datatables(iteration_number=None, csv_dir=None):
    """
    Reimport CSV data into Unreal Engine DataTables.
    
    This function loads and executes the reimport_datatable.py script, which imports
    CSV files containing mesh and material data into Unreal Engine DataTables.
    
    Args:
        iteration_number (int, optional): The current iteration number for file naming.
                                          If None, uses the global ITERATION_NUMBER.
        csv_dir (str, optional): Directory containing CSV files. If None, uses default path
        
    Returns:
        int: Number of successfully processed DataTables
    """
    # Use global configuration if parameter is not provided
    if iteration_number is None:
        iteration_number = ITERATION_NUMBER
    unreal.log(f"\n📃 === REIMPORTING CSV DATA TO DATATABLES (ITERATION {iteration_number}) === 📃")
    
    # Define the script path
    reimport_script = os.path.join(SCRIPTS_DIR, "110_reimport_datatable.py")
    
    # If csv_dir is not provided, use default path relative to workspace root
    if csv_dir is None:
        csv_dir = os.path.join(WORKSPACE_ROOT, ".." , "03_GenDatas", "Dependancies", "PCG_HD", "Out", "CSV")
    
    unreal.log(f"📂 CSV Directory: {csv_dir}")
    unreal.log(f"🔄 Iteration Number: {iteration_number}")
    
    try:
        # Set up globals to pass to the script
        exec_globals = {'iteration_number': iteration_number, 'csv_dir': csv_dir}
        
        # Read and execute the script
        with open(reimport_script, 'r', encoding='utf-8') as f:
            code = f.read()
            exec(code, exec_globals)
            
            unreal.log(f"🔍 Calling reimport_all_datatables() function...")
            result = exec_globals['reimport_all_datatables']()
            
            if result > 0:
                unreal.log(f"✅ Successfully processed {result} DataTables!")
            else:
                unreal.log_warning(f"⚠️ No DataTables were processed. Check the logs for details.")
                
            return result
    except Exception as e:
        unreal.log_error(f"❌ Error during CSV reimport: {str(e)}")
        return 0

# Example usage with iteration number 5
# call_reimport_all_datatables(5)



# ======================================================================
# Splines to JSON Export
# ======================================================================

def call_export_splines_to_json(iteration_number=None, output_dir=None):
    """
    Export splines from the current Unreal Engine level to JSON format.
    
    This function loads and executes the export_splines_as_json.py script, which finds
    all spline components in the current level and exports their data to a JSON file.
    
    Args:
        iteration_number (int, optional): The current iteration number for file naming.
                                          If None, uses the global ITERATION_NUMBER.
        output_dir (str, optional): Directory to save the JSON file. If None, uses default path
        
    Returns:
        dict: Information about the exported splines including count and file path
    """
    # Use global configuration if parameter is not provided
    if iteration_number is None:
        iteration_number = ITERATION_NUMBER
    unreal.log(f"\n🖌️ === EXPORTING SPLINES TO JSON (ITERATION {iteration_number}) === 🖌️")
    
    # Define the script path
    splines_script = os.path.join(SCRIPTS_DIR, "000_export_splines_as_json.py")
    
    # If output_dir is not provided, use default path relative to workspace root
    if output_dir is None:
        output_dir = os.path.join(WORKSPACE_ROOT, ".." , "03_GenDatas", "Exports", "SplineExports")
    
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    unreal.log(f"📂 Output Directory: {output_dir}")
    unreal.log(f"🔄 Iteration Number: {iteration_number}")
    
    try:
        # Set up globals to pass to the script
        exec_globals = {'iteration_number': iteration_number, 'output_dir': output_dir}
        
        # Read and execute the script
        with open(splines_script, 'r', encoding='utf-8') as f:
            code = f.read()
            exec(code, exec_globals)
            
            unreal.log(f"🔍 Calling export_splines_to_json() function...")
            result = exec_globals['export_splines_to_json']()
            
            if result and 'spline_count' in result and result['spline_count'] > 0:
                unreal.log(f"✅ Successfully exported {result['spline_count']} splines to {result['file_path']}")
            else:
                unreal.log_warning(f"⚠️ No splines were found or exported. Check the level for spline components.")
                
            return result
    except Exception as e:
        unreal.log_error(f"❌ Error during splines export: {str(e)}")
        return {'spline_count': 0, 'file_path': None, 'error': str(e)}

# Example usage with iteration number 5
# call_export_splines_to_json(5)
    


# ======================================================================
# PCG Graph Creation and Placement
# ======================================================================

def call_create_and_add_pcg_graph(iteration_number=None):
    """
    Create a new PCG graph blueprint and add it to the current level.
    
    This function loads and executes the create_pcg_graph.py script, which duplicates
    a template PCG blueprint, renames it with the iteration number, and places it in the level.
    
    Args:
        iteration_number (int, optional): The current iteration number for blueprint naming.
                                          If None, uses the global ITERATION_NUMBER.
        
    Returns:
        unreal.Blueprint: The newly created blueprint asset, or None if creation failed
    """
    # Use global configuration if parameter is not provided
    if iteration_number is None:
        iteration_number = ITERATION_NUMBER
    unreal.log(f"\n🗺️ === CREATING PCG GRAPH BLUEPRINT (ITERATION {iteration_number}) === 🗺️")
    
    # Define the script path
    create_pcg_graph_script_path = os.path.join(SCRIPTS_DIR, "120_create_pcg_graph.py")
    
    unreal.log(f"🔄 Iteration Number: {iteration_number}")
    
    try:
        # Set up globals to pass to the script
        exec_globals = {}
        
        # Read and execute the script
        with open(create_pcg_graph_script_path, 'r', encoding='utf-8') as f:
            code = f.read()
            exec(code, exec_globals)
            
            unreal.log(f"🔍 Calling duplicate_and_rename_pcg_blueprint() function...")
            result = exec_globals['duplicate_and_rename_pcg_blueprint'](iteration_number)
            
            if result:
                unreal.log(f"✅ Successfully created and placed PCG graph blueprint for iteration {iteration_number}")
            else:
                unreal.log_warning(f"⚠️ Failed to create PCG graph blueprint. Check the logs for details.")
                
            return result
    except Exception as e:
        unreal.log_error(f"❌ Error during PCG graph creation: {str(e)}")
        return None

# Example usage with iteration number 5
# call_create_and_add_pcg_graph(5)

# ======================================================================
# Add Sidewalks & Roads to Level
# ======================================================================

def call_add_SM_sidewalks_and_roads_to_level(iteration_number=None):
    """
    Add sidewalks and roads static meshes to the current level.
    
    This function loads and executes the add_SM_to_lvl.py script, which finds
    static meshes named 'sidewalks_{iteration_number}' and 'road_{iteration_number}'
    and adds them to the current level in organized folders.
    
    Args:
        iteration_number (int, optional): The current iteration number for finding the correct static meshes.
                                          If None, uses the global ITERATION_NUMBER.
        
    Returns:
        dict: Information about the added static meshes including counts and paths
    """
    # Use global configuration if parameter is not provided
    if iteration_number is None:
        iteration_number = ITERATION_NUMBER
    unreal.log(f"\n🛣️ === ADDING SIDEWALKS & ROADS TO LEVEL (ITERATION {iteration_number}) === 🛣️")
    
    # Define the script path
    add_sm_sidewalks_roads_script_path = os.path.join(SCRIPTS_DIR, "220_add_SM_to_lvl.py")
    
    unreal.log(f"🔄 Iteration Number: {iteration_number}")
    
    try:
        # Set up globals to pass to the script
        exec_globals = {}
        
        # Read and execute the script
        with open(add_sm_sidewalks_roads_script_path, 'r', encoding='utf-8') as f:
            code = f.read()
            exec(code, exec_globals)
            
            unreal.log(f"🔍 Calling add_SM_sidewalks_and_roads_to_level() function...")
            result = exec_globals['add_SM_sidewalks_and_roads_to_level'](iteration_number)
            
            if result and isinstance(result, dict) and result.get('success', False):
                unreal.log(f"✅ Successfully added sidewalks and roads to the current level!")
                if 'sidewalks_count' in result:
                    unreal.log(f"   🛣️ Added {result['sidewalks_count']} sidewalk meshes")
                if 'roads_count' in result:
                    unreal.log(f"   🛣️ Added {result['roads_count']} road meshes")
            else:
                unreal.log_warning(f"⚠️ Failed to add sidewalks and roads. Check the logs for details.")
                
            return result
    except Exception as e:
        unreal.log_error(f"❌ Error adding sidewalks and roads to level: {str(e)}")
        return {'success': False, 'error': str(e)}

# Example usage with iteration number 5
# call_add_SM_sidewalks_and_roads_to_level(5)



# ======================================================================
# Reimport Static Meshes
# ======================================================================

def call_reimport_folder_static_meshes(iteration_number=None, fbx_dir=None):
    """
    Reimport static meshes from FBX files into Unreal Engine.
    
    This function loads and executes the reimport_SM.py script, which finds
    FBX files in the specified directory and reimports them as static meshes.
    
    Args:
        iteration_number (int, optional): The current iteration number for finding the correct FBX files.
                                          If None, uses the global ITERATION_NUMBER.
        fbx_dir (str, optional): Directory containing FBX files. If None, uses default path
        
    Returns:
        dict: Information about the reimported static meshes including counts and paths
    """
    # Use global configuration if parameter is not provided
    if iteration_number is None:
        iteration_number = ITERATION_NUMBER
    unreal.log(f"\n🏗️ === REIMPORTING STATIC MESHES (ITERATION {iteration_number}) === 🏗️")
    
    # Define the script path
    reimport_sm_script = os.path.join(SCRIPTS_DIR, "210_reimport_SM.py")
    
    # If fbx_dir is not provided, use default path relative to workspace root
    if fbx_dir is None:
        fbx_dir = os.path.join(WORKSPACE_ROOT, ".." , "03_GenDatas", "Dependancies", "SW_Roads", "Out", "Mod")
    
    unreal.log(f"📂 FBX Directory: {fbx_dir}")
    unreal.log(f"🔄 Iteration Number: {iteration_number}")
    
    try:
        # Set up globals to pass to the script
        exec_globals = {'iteration_number': iteration_number, 'fbx_dir': fbx_dir}
        
        # Read and execute the script
        with open(reimport_sm_script, 'r', encoding='utf-8') as f:
            code = f.read()
            exec(code, exec_globals)
            
            unreal.log(f"🔍 Calling reimport_folder_static_meshes() function...")
            result = exec_globals['reimport_folder_static_meshes']()
            
            if result and isinstance(result, dict) and result.get('success', False):
                unreal.log(f"✅ Successfully reimported static meshes!")
                if 'imported_count' in result:
                    unreal.log(f"   💾 Reimported {result['imported_count']} static meshes")
                if 'meshes' in result and result['meshes']:
                    unreal.log(f"   📚 First few meshes: {', '.join(result['meshes'][:3])}{'...' if len(result['meshes']) > 3 else ''}")
            else:
                unreal.log_warning(f"⚠️ Failed to reimport static meshes. Check the logs for details.")
                
            return result
    except Exception as e:
        unreal.log_error(f"❌ Error reimporting static meshes: {str(e)}")
        return {'success': False, 'error': str(e)}

# Example usage with iteration number 5
# call_reimport_folder_static_meshes(5)


# ======================================================================
# Main Pipeline Function
# ======================================================================

def run_full_pipeline(iteration_number=None):
    """
    Run the complete procedural generation pipeline from start to finish.
    
    This function executes all steps of the pipeline in sequence with the specified iteration number.
    If no iteration number is provided, it uses the global ITERATION_NUMBER defined at the top of this file.
    
    Args:
        iteration_number (int, optional): The iteration number to use for all pipeline steps.
                                          If None, uses the global ITERATION_NUMBER.
        
    Returns:
        dict: Summary of the pipeline execution with success/failure status for each step
    """
    # Use global configuration if parameter is not provided
    if iteration_number is None:
        iteration_number = ITERATION_NUMBER
    unreal.log(f"\n🌐 === STARTING FULL PIPELINE (ITERATION {iteration_number}) === 🌐")
    unreal.log(f"Starting time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    pipeline_results = {
        'iteration_number': iteration_number,
        'start_time': time.time(),
        'steps': {}
    }
    
    # Step 1: Export GenZone meshes
    unreal.log(f"\n🔹 STEP 1: Export GenZone meshes")
    try:
        result = call_export_genzone_meshes(iteration_number)
        pipeline_results['steps']['export_genzone'] = {'success': bool(result), 'result': result}
    except Exception as e:
        unreal.log_error(f"Failed at step 1: {str(e)}")
        pipeline_results['steps']['export_genzone'] = {'success': False, 'error': str(e)}
    
    # Step 2: Run Houdini PCG generation
    unreal.log(f"\n🔹 STEP 2: Run Houdini PCG generation")
    try:
        result = run_houdini_pcg_generation(iteration_number)
        pipeline_results['steps']['houdini_pcg'] = {'success': bool(result), 'process_id': result.pid if result else None}
        # Give Houdini time to finish processing
        unreal.log("Waiting for Houdini PCG generation to complete (60 seconds)...")
        time.sleep(60)
    except Exception as e:
        unreal.log_error(f"Failed at step 2: {str(e)}")
        pipeline_results['steps']['houdini_pcg'] = {'success': False, 'error': str(e)}
    
    # Step 3: Reimport CSV data
    unreal.log(f"\n🔹 STEP 3: Reimport CSV data")
    try:
        result = call_reimport_all_datatables(iteration_number)
        pipeline_results['steps']['reimport_csv'] = {'success': result > 0, 'count': result}
    except Exception as e:
        unreal.log_error(f"Failed at step 3: {str(e)}")
        pipeline_results['steps']['reimport_csv'] = {'success': False, 'error': str(e)}
    
    # Step 4: Create PCG graph
    unreal.log(f"\n🔹 STEP 4: Create PCG graph")
    try:
        result = call_create_and_add_pcg_graph(iteration_number)
        pipeline_results['steps']['create_pcg_graph'] = {'success': bool(result), 'result': str(result)}
    except Exception as e:
        unreal.log_error(f"Failed at step 4: {str(e)}")
        pipeline_results['steps']['create_pcg_graph'] = {'success': False, 'error': str(e)}
    
    # Step 5: Export splines to JSON
    unreal.log(f"\n🔹 STEP 5: Export splines to JSON")
    try:
        result = call_export_splines_to_json(iteration_number)
        pipeline_results['steps']['export_splines'] = {'success': result and 'spline_count' in result and result['spline_count'] > 0, 'result': result}
    except Exception as e:
        unreal.log_error(f"Failed at step 5: {str(e)}")
        pipeline_results['steps']['export_splines'] = {'success': False, 'error': str(e)}
    
    # Step 6: Run Houdini sidewalks & roads generation
    unreal.log(f"\n🔹 STEP 6: Run Houdini sidewalks & roads generation")
    try:
        result = run_houdini_sidewalks_roads_generation(iteration_number)
        pipeline_results['steps']['houdini_swr'] = {'success': bool(result), 'process_id': result.pid if result else None}
        # Give Houdini time to finish processing
        unreal.log("Waiting for Houdini sidewalks & roads generation to complete (60 seconds)...")
        time.sleep(60)
    except Exception as e:
        unreal.log_error(f"Failed at step 6: {str(e)}")
        pipeline_results['steps']['houdini_swr'] = {'success': False, 'error': str(e)}
    
    # Step 7: Reimport static meshes
    unreal.log(f"\n🔹 STEP 7: Reimport static meshes")
    try:
        result = call_reimport_folder_static_meshes(iteration_number)
        pipeline_results['steps']['reimport_sm'] = {'success': result and isinstance(result, dict) and result.get('success', False), 'result': result}
    except Exception as e:
        unreal.log_error(f"Failed at step 7: {str(e)}")
        pipeline_results['steps']['reimport_sm'] = {'success': False, 'error': str(e)}
    
    # Step 8: Add sidewalks & roads to level
    unreal.log(f"\n🔹 STEP 8: Add sidewalks & roads to level")
    try:
        result = call_add_SM_sidewalks_and_roads_to_level(iteration_number)
        pipeline_results['steps']['add_sm_to_level'] = {'success': result and isinstance(result, dict) and result.get('success', False), 'result': result}
    except Exception as e:
        unreal.log_error(f"Failed at step 8: {str(e)}")
        pipeline_results['steps']['add_sm_to_level'] = {'success': False, 'error': str(e)}
    
    # Calculate pipeline completion time
    pipeline_results['end_time'] = time.time()
    pipeline_results['duration_seconds'] = pipeline_results['end_time'] - pipeline_results['start_time']
    
    # Count successful steps
    successful_steps = sum(1 for step in pipeline_results['steps'].values() if step.get('success', False))
    total_steps = len(pipeline_results['steps'])
    
    # Print summary
    unreal.log(f"\n🌐 === PIPELINE EXECUTION COMPLETE === 🌐")
    unreal.log(f"End time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    unreal.log(f"Total duration: {pipeline_results['duration_seconds']:.2f} seconds")
    unreal.log(f"Steps completed: {successful_steps}/{total_steps}")
    
    if successful_steps == total_steps:
        unreal.log(f"🎉 All pipeline steps completed successfully!")
    else:
        unreal.log_warning(f"⚠️ {total_steps - successful_steps} steps failed. Check the logs for details.")
    
    return pipeline_results

# Example usage with iteration number 5
# run_full_pipeline(5)