"""
=======GENZONE MESHES EXPORT SCRIPT=========
"""
import unreal
import os
import subprocess
import time

genzone_export_script = r"C:/Users/luka.croisez/Documents/GitHub/professional/Various_Scripts/019_UE_export_gz_to_mod.py"

def call_export_genzone_meshes(iteration_number=0):
    """
    Run the GenZone Static Mesh export script with the given iteration_number.
    This will export all static meshes with 'genzone' in the name to FBX files,
    appending the iteration_number to each exported file.
    """
    exec_globals = {}
    with open(genzone_export_script, 'r', encoding='utf-8') as f:
        code = f.read()
        exec(code, exec_globals)
        # Call main() from the export script with the provided iteration_number
        if 'main' in exec_globals:
            exec_globals['main'](iteration_number)
        else:
            print("ERROR: 'main' function not found in export script.")

call_export_genzone_meshes(5)


"""
=======HOUDINI HEADLESS SCRIPT - PCG HD=======
"""

import unreal
import os
import subprocess
import time

# Use local file paths
hython_path = r"C:/Program Files/Side Effects Software/Houdini 20.0.653/bin/hython.exe"
houdini_script = r"C:/Users/luka.croisez/Documents/GitHub/professional/Various_Scripts/019_HOUDINI_headless_topnet_PCGHD.py"
hip_file_path = r"S:/users/claude.levastre/cityv2/genbuildingbase3.hip"
topnet_path = "/obj/geo1/topnet"

iteration_number = 5
switch_bool_value = 1

file1_path = fr"S:/users/luka.croisez/ProcGenPipeline/Dependancies/PCG_HD/In/GZ/Mod/SM_genzones_PCG_HD_{iteration_number}.fbx"
rop_pcg_export1_mesh_path = fr"S:/users/luka.croisez/ProcGenPipeline/Dependancies/PCG_HD/Out/CSV/mesh_{iteration_number}.csv"
rop_pcg_export1_mat_path = fr"S:/users/luka.croisez/ProcGenPipeline/Dependancies/PCG_HD/Out/CSV/mat_{iteration_number}.csv"

print("=== LAUNCHING HOUDINI ===")
subprocess.Popen([
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
print("Houdini launched in separate window")
print("Generation complete!")



"""
=======HOUDINI HEADLESS SCRIPT - Sidewalks & Roads=======
"""

import unreal
import os
import subprocess
import time

hython_path = r"C:/Program Files/Side Effects Software/Houdini 20.0.653/bin/hython.exe"
houdini_script = r"C:/Users/luka.croisez/Documents/GitHub/professional/Various_Scripts/019_HOUDINI_headless_topnet_SWR.py"
hip_file_path = r"S:/users/luka.croisez/houdini/tool/USD_env_pipeline/sidewalks.hip"
topnet_path = "/obj/geo1/topnet"

iteration_number = 5
switch_bool_value = 1

file1_path = fr"S:/users/luka.croisez/ProcGenPipeline/Dependancies/PCG_HD/In/GZ/Mod/SM_genzones_PCG_HD_{iteration_number}.fbx"
rop_fbx_road_path = fr"S:/users/luka.croisez/ProcGenPipeline/Dependancies/SW_Roads/Out/Mod/road_{iteration_number}.fbx"
rop_fbx_sidewalks_path = fr"S:/users/luka.croisez/ProcGenPipeline/Dependancies/SW_Roads/Out/Mod/sidewalks_{iteration_number}.fbx"

print("=== LAUNCHING HOUDINI WITH CUSTOM PATHS ===")
subprocess.Popen([
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
print("Houdini launched in separate window")
print("Generation complete!")



"""
=======CSV REIMPORT SCRIPT=======
"""

reimport_script = r"C:/Users/luka.croisez\Documents/GitHub/professional/Various_Scripts/019_UE_reimport_datatable.py"

def call_reimport_all_datatables(iteration_number=0, csv_dir=None):
    exec_globals = {'iteration_number': iteration_number}
    if csv_dir is not None:
        exec_globals['csv_dir'] = csv_dir
    with open(reimport_script, 'r', encoding='utf-8') as f:
        code = f.read()
        exec(code, exec_globals)
        print("About to call reimport_all_datatables()")
        result = exec_globals['reimport_all_datatables']()
        print("Result:", result)
        return result

call_reimport_all_datatables(5, r"S:/users/luka.croisez/ProcGenPipeline/Dependancies/PCG_HD/Out/CSV")

print("CSV reimport complete!")



"""
=======SPLINES TO JSON EXPORT SCRIPT=========
"""

splines_script = r"C:/Users/luka.croisez/Documents/GitHub/professional/Various_Scripts/019_UE_export_splines_as_json.py"

def call_export_splines_to_json(iteration_number=0, output_dir=None):
    exec_globals = {'iteration_number': iteration_number}
    if output_dir is not None:
        exec_globals['output_dir'] = output_dir
    with open(splines_script, 'r', encoding='utf-8') as f:
        code = f.read()
        exec(code, exec_globals)
        print("About to call export_splines_to_json()")
        result = exec_globals['export_splines_to_json']()
        print("Result:", result)
        return result

call_export_splines_to_json(5, r"S:/users/luka.croisez/ProcGenPipeline/Dependancies/PCG_HD/In/GZ/Splines")
    


"""
=======CREATE AND ADD PCG GRAPH SCRIPT=========
"""

create_pcg_graph_script_path = r"C:/Users/luka.croisez/Documents/GitHub/professional/Various_Scripts/019_UE_create_pcg_graph.py"

def call_create_and_add_pcg_graph(iteration_number=0):
    """
    Calls the duplicate_and_rename_pcg_blueprint function from the 019_UE_create_pcg_graph.py script.
    Duplicates the PCG template BP, renames it, and adds it to the current level.
    """
    exec_globals = {}
    with open(create_pcg_graph_script_path, 'r', encoding='utf-8') as f:
        code = f.read()
        exec(code, exec_globals)
        print("About to call duplicate_and_rename_pcg_blueprint()")
        result = exec_globals['duplicate_and_rename_pcg_blueprint'](iteration_number)
        print("Result:", result)
        return result

call_create_and_add_pcg_graph(5)

"""
=======ADD SIDEWALKS & ROADS TO LEVEL SCRIPT=========
"""

add_sm_sidewalks_roads_script_path = r"C:/Users/luka.croisez/Documents/GitHub/professional/Various_Scripts/019_UE_add_SM_to_lvl.py"

def call_add_SM_sidewalks_and_roads_to_level(iteration_number=0):
    """
    Calls the add_SM_sidewalks_and_roads_to_level function from the 019_UE_add_SM_to_lvl.py script.
    Adds all static meshes named 'sidewalks_{iteration_number}' and 'road_{iteration_number}' to the current level,
    placing them in 'Sidewalks' and 'Roads' folders respectively.
    """
    exec_globals = {}
    with open(add_sm_sidewalks_roads_script_path, 'r', encoding='utf-8') as f:
        code = f.read()
        exec(code, exec_globals)
        print("About to call add_SM_sidewalks_and_roads_to_level()")
        result = exec_globals['add_SM_sidewalks_and_roads_to_level'](iteration_number)
        print("Result:", result)
        return result

call_add_SM_sidewalks_and_roads_to_level(5)



"""
=======REIMPORT STATIC MESHES SCRIPT=======
"""

reimport_sm_script = r"C:/Users/luka.croisez/Documents/GitHub/professional/Various_Scripts/019_reimport_SM.py"

def call_reimport_folder_static_meshes(iteration_number=0, fbx_dir=None):
    exec_globals = {'iteration_number': iteration_number}
    if fbx_dir is not None:
        exec_globals['fbx_dir'] = fbx_dir
    with open(reimport_sm_script, 'r', encoding='utf-8') as f:
        code = f.read()
        exec(code, exec_globals)
        print("About to call reimport_folder_static_meshes()")
        result = exec_globals['reimport_folder_static_meshes']()
        print("Result:", result)
        return result

call_reimport_folder_static_meshes(5, r"S:/users/luka.croisez/ProcGenPipeline/Dependancies/SW_Roads/Out/Mod")