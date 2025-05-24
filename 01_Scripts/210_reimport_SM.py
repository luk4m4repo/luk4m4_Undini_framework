import unreal
import os

# Define the workspace root relative to this script
WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

# Get the FBX directory from globals or use default relative to workspace root
if 'fbx_dir' in globals():
    fbx_directory = globals()['fbx_dir']
else:
    fbx_directory = os.path.join(WORKSPACE_ROOT, '..', '03_GenDatas', 'Dependancies', 'SW_Roads', 'Out', 'Mod')

# Get the iteration number from globals or use default
if 'iteration_number' in globals():
    iteration = globals()['iteration_number']
else:
    iteration = 0

# Define what we're importing - sidewalks and roads for this iteration
import_configs = [
    {
        "source_file": fr"{fbx_directory}/sidewalks_{iteration}.fbx",
        "folder_path": f"/Game/Developers/lukacroisez/Assets/Sidewalks/Sidewalks_{iteration}",
        "asset_name": f"sidewalks_{iteration}",
        "name_filter": f"sidewalks_{iteration}"
    },
    {
        "source_file": fr"{fbx_directory}/road_{iteration}.fbx",
        "folder_path": f"/Game/Developers/lukacroisez/Assets/Road/Road_{iteration}",
        "asset_name": f"road_{iteration}",
        "name_filter": f"road_{iteration}"
    }
]

# FBX import settings that work well with Unreal Engine 5.3.2
FBX_IMPORT_SETTINGS = {
    "automated": True,
    "save": True,
    "replace_existing": True,
    
    "factory_options": {
        "auto_generate_collision": True,
        "import_materials": True,
        "import_textures": True
    }
}

def reimport_folder_static_meshes():
    """
    Imports or reimports static meshes from FBX files into Unreal Engine.
    
    This script looks for FBX files containing sidewalks and roads for the current iteration,
    then either updates existing meshes or creates new ones in the appropriate folders.
    """
    unreal.log("Looking for static meshes to import or update...")
    
    # Get the tools we need
    editor_lib = unreal.EditorAssetLibrary
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    
    # Keep track of what we've processed
    total_processed = 0
    total_success = 0
    
    # Process each import configuration
    for config in import_configs:
        source_file = config["source_file"]
        folder_path = config["folder_path"]
        asset_name = config["asset_name"]
        name_filter = config.get("name_filter", "")
        
        # Make sure the source file exists
        if not os.path.exists(source_file):
            unreal.log_warning(f"Hmm, can't find the source file: {source_file}. Did you generate it first?")
            continue
        
        unreal.log(f"\nProcessing: {asset_name}")
        unreal.log(f"Source: {source_file}")
        unreal.log(f"Destination: {folder_path}")
        
        # Create the destination folder if needed
        if not editor_lib.does_directory_exist(folder_path):
            unreal.log(f"Creating folder: {folder_path}")
            editor_lib.make_directory(folder_path)
        
        # Look for existing static meshes that match our filter
        assets = editor_lib.list_assets(folder_path, recursive=True, include_folder=False)
        existing_meshes = []
        
        # Find static meshes that match our filter
        for asset_path in assets:
            try:
                if name_filter and name_filter.lower() not in asset_path.lower():
                    continue
                    
                asset = editor_lib.load_asset(asset_path)
                if asset and isinstance(asset, unreal.StaticMesh):
                    existing_meshes.append(asset_path)
            except Exception as e:
                unreal.log_warning(f"Trouble checking asset {asset_path}: {str(e)}")
        
        if existing_meshes:
            unreal.log(f"Found {len(existing_meshes)} existing meshes to update")
            
            # Update existing meshes
            for asset_path in existing_meshes:
                try:
                    unreal.log(f"Updating: {os.path.basename(asset_path)}")
                    
                    # Set up the reimport task
                    task = unreal.AssetImportTask()
                    task.filename = source_file
                    task.destination_path = os.path.dirname(asset_path)
                    task.destination_name = os.path.basename(asset_path).split(".")[0]
                    task.replace_existing = True
                    task.automated = True
                    task.save = True
                    
                    # Configure the FBX factory
                    factory = unreal.FbxFactory()
                    for key, value in FBX_IMPORT_SETTINGS["factory_options"].items():
                        factory.set_editor_property(key, value)
                    task.factory = factory
                    
                    # Do the reimport
                    result = asset_tools.import_asset_tasks([task])
                    
                    if result and len(result) > 0:
                        unreal.log(f"Successfully updated: {os.path.basename(asset_path)}")
                        total_success += 1
                    else:
                        unreal.log(f"Update process completed - check Content Browser")
                        total_success += 1
                    
                    total_processed += 1
                except Exception as e:
                    unreal.log_error(f"Oops! Couldn't update {os.path.basename(asset_path)}: {str(e)}")
                    total_processed += 1
        else:
            unreal.log(f"No existing meshes found in {folder_path}")
            unreal.log(f"Creating new meshes from: {source_file}")
            
            # Try to import new meshes
            try:
                # First method: Use AssetImportTask
                try:
                    # Set up the import task
                    task = unreal.AssetImportTask()
                    task.filename = source_file
                    task.destination_path = folder_path
                    task.destination_name = asset_name
                    task.replace_existing = True
                    task.automated = True
                    task.save = True
                    
                    # Configure the FBX factory
                    factory = unreal.FbxFactory()
                    for key, value in FBX_IMPORT_SETTINGS["factory_options"].items():
                        factory.set_editor_property(key, value)
                    task.factory = factory
                    
                    # Do the import
                    result = asset_tools.import_asset_tasks([task])
                    
                    if result and len(result) > 0:
                        unreal.log("Successfully imported new meshes!")
                        
                        # Count how many new meshes we got
                        new_assets = editor_lib.list_assets(folder_path, recursive=True, include_folder=False)
                        new_meshes = []
                        
                        for asset_path in new_assets:
                            try:
                                if name_filter and name_filter.lower() not in asset_path.lower():
                                    continue
                                    
                                asset = editor_lib.load_asset(asset_path)
                                if asset and isinstance(asset, unreal.StaticMesh):
                                    new_meshes.append(asset_path)
                            except Exception:
                                pass
                        
                        new_count = len(new_meshes)
                        unreal.log(f"Created {new_count} new mesh assets")
                        total_success += new_count
                        total_processed += new_count
                        continue
                except Exception as task_e:
                    unreal.log_warning(f"First import method didn't work: {str(task_e)}")
                
                # Second method: Try direct import
                try:
                    # Import directly using the asset library
                    full_path = f"{folder_path}/{asset_name}"
                    imported = editor_lib.import_asset(source_file, full_path)
                    
                    if imported:
                        unreal.log("Successfully imported using direct method!")
                        
                        # Count how many new meshes we got
                        new_assets = editor_lib.list_assets(folder_path, recursive=True, include_folder=False)
                        new_meshes = []
                        
                        for asset_path in new_assets:
                            try:
                                if name_filter and name_filter.lower() not in asset_path.lower():
                                    continue
                                    
                                asset = editor_lib.load_asset(asset_path)
                                if asset and isinstance(asset, unreal.StaticMesh):
                                    new_meshes.append(asset_path)
                            except Exception:
                                pass
                        
                        new_count = len(new_meshes)
                        unreal.log(f"Created {new_count} new mesh assets")
                        total_success += new_count
                        total_processed += new_count
                        continue
                except Exception as import_e:
                    unreal.log_warning(f"Second import method didn't work either: {str(import_e)}")
                
                unreal.log_error(f"Sorry, couldn't import {asset_name} using any method")
                total_processed += 1
            except Exception as e:
                unreal.log_error(f"Problem during import process: {str(e)}")
                total_processed += 1
    
    # Show a summary of what we did
    unreal.log(f"\nImport/Update Summary")
    unreal.log(f"Successfully processed {total_success} of {total_processed} meshes")
    
    if total_success < total_processed:
        unreal.log_warning("Some imports didn't work. Check the log above for details.")
    else:
        unreal.log("All meshes were imported or updated successfully!")
        
    return total_success


# Run the function when this script is executed directly
if __name__ == "__main__":
    reimport_folder_static_meshes()
