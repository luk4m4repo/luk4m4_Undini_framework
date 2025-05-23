import unreal
import os

# Allow manager to override base FBX directory and iteration_number
if 'fbx_dir' in globals():
    base_fbx_dir = globals()['fbx_dir']
else:
    base_fbx_dir = r"S:/users/luka.croisez/ProcGenPipeline/Dependancies/SW_Roads/Out/Mod"

if 'iteration_number' in globals():
    it_num = globals()['iteration_number']
else:
    it_num = 0

# Define folder-based import/reimport configurations with dynamic source_file
folder_reimport_configs = [
    {
        "source_file": fr"{base_fbx_dir}/sidewalks_{it_num}.fbx",
        "folder_path": f"/Game/Developers/lukacroisez/Assets/Sidewalks/Sidewalks_{it_num}",
        "asset_name": f"sidewalks_{it_num}",  # Base name for the asset
        "name_filter": f"sidewalks_{it_num}"  # Optional filter to only reimport meshes containing this string
    },
    {
        "source_file": fr"{base_fbx_dir}/road_{it_num}.fbx",
        "folder_path": f"/Game/Developers/lukacroisez/Assets/Road/Road_{it_num}",
        "asset_name": f"road_{it_num}",  # Base name for the asset
        "name_filter": f"road_{it_num}"  # Optional filter to only reimport meshes containing this string
    },
    # Add more folder configurations as needed
]

# Simplified import settings for UE 5.3.2
# These settings will be applied to all FBX imports using properties that are known to work
FBX_IMPORT_SETTINGS = {
    # General import task settings
    "automated": True,
    "save": True,
    "replace_existing": True,
    
    # Basic factory options that are known to work in UE 5.3.2
    "factory_options": {
        "auto_generate_collision": True,  # Generate collision
        "import_materials": True,         # Import materials
        "import_textures": True          # Import textures
    }
}

def reimport_folder_static_meshes():
    print("\n=== IMPORTING/REIMPORTING STATIC MESHES ===")
    
    # Get references to necessary libraries
    editor_lib = unreal.EditorAssetLibrary
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    editor_asset_subsystem = unreal.get_editor_subsystem(unreal.EditorAssetSubsystem)
    
    total_assets_processed = 0
    total_success_count = 0
    
    # Process each folder configuration
    for config in folder_reimport_configs:
        source_file = config["source_file"]
        folder_path = config["folder_path"]
        asset_name = config["asset_name"]
        name_filter = config.get("name_filter", "")  # Optional filter
        
        # Check if the source file exists
        if not os.path.exists(source_file):
            print(f"\nWARNING: Source file does not exist: {source_file}")
            continue
        
        print(f"\n=== Processing: {asset_name} ===")
        print(f"Source file: {source_file}")
        print(f"Destination folder: {folder_path}")
        
        # Make sure the destination folder exists
        if not editor_lib.does_directory_exist(folder_path):
            print(f"Creating destination folder: {folder_path}")
            editor_lib.make_directory(folder_path)
        
        # Check if any static meshes with the name filter already exist in the folder
        assets = editor_lib.list_assets(folder_path, recursive=True, include_folder=False)
        existing_static_meshes = []
        
        # Filter for static meshes and apply name filter if provided
        for asset_path in assets:
            try:
                # Apply name filter if specified
                if name_filter and name_filter.lower() not in asset_path.lower():
                    continue
                    
                asset = editor_lib.load_asset(asset_path)
                if asset and isinstance(asset, unreal.StaticMesh):
                    existing_static_meshes.append(asset_path)
            except Exception as e:
                print(f"Error checking asset {asset_path}: {str(e)}")
        
        if existing_static_meshes:
            print(f"Found {len(existing_static_meshes)} existing static meshes matching filter in folder")
            
            # REIMPORT MODE: Process each existing static mesh
            for mesh_path in existing_static_meshes:
                mesh_name = mesh_path.split('/')[-1]
                print(f"\nReimporting: {mesh_name}")
                
                try:
                    # Approach 1: Try direct reimport first (fastest and most reliable)
                    try:
                        existing_mesh = editor_lib.load_asset(mesh_path)
                        if existing_mesh:
                            # Try to reimport the asset directly
                            if editor_asset_subsystem.reimport_asset(existing_mesh):
                                print(f"Successfully reimported {mesh_name} using direct method")
                                total_success_count += 1
                                total_assets_processed += 1
                                continue
                    except Exception as direct_e:
                        print(f"Direct reimport failed: {str(direct_e)}")
                    
                    # Approach 2: Try using AssetImportTask with simple settings
                    try:
                        # Create import task for the source file
                        task = unreal.AssetImportTask()
                        task.filename = source_file
                        task.destination_path = folder_path
                        task.destination_name = mesh_path.split('/')[-1].split('.')[0]  # Get just the name without path or extension
                        
                        # Apply general settings from FBX_IMPORT_SETTINGS
                        task.replace_existing = FBX_IMPORT_SETTINGS["replace_existing"]
                        task.automated = FBX_IMPORT_SETTINGS["automated"]
                        task.save = FBX_IMPORT_SETTINGS["save"]
                        
                        # Set up a simple FBX factory with basic settings
                        fbx_factory = unreal.FbxFactory()
                        
                        # Apply factory options that are known to work
                        for option, value in FBX_IMPORT_SETTINGS["factory_options"].items():
                            try:
                                fbx_factory.set_editor_property(option, value)
                            except Exception:
                                print(f"Warning: Could not set factory option: {option}")
                        
                        # Assign factory to task
                        task.factory = fbx_factory
                        
                        # Import the asset (this will replace the existing one)
                        result = asset_tools.import_asset_tasks([task])
                        
                        if result and len(result) > 0:
                            print(f"Successfully reimported {mesh_name} using import task")
                            total_success_count += 1
                            total_assets_processed += 1
                            continue
                    except Exception as task_e:
                        print(f"Import task failed: {str(task_e)}")
                    
                    # Approach 3: Try using a direct import method
                    try:
                        # Import the FBX file directly to the package path
                        package_path = mesh_path.split('.')[0]  # Remove the object name part
                        imported = editor_lib.import_asset(source_file, package_path)
                        
                        if imported:
                            print(f"Successfully reimported {mesh_name} using direct import")
                            total_success_count += 1
                            total_assets_processed += 1
                            continue
                    except Exception as import_e:
                        print(f"Direct import failed: {str(import_e)}")
                    
                    print(f"All reimport methods failed for {mesh_name}")
                    total_assets_processed += 1
                        
                except Exception as e:
                    print(f"Error processing {mesh_name}: {str(e)}")
                    total_assets_processed += 1
        else:
            print("No existing static meshes found - performing initial import")
            
            # IMPORT MODE: Create new static mesh assets
            try:
                # Method 1: Try using AssetImportTask
                try:
                    # Create import task for the source file
                    task = unreal.AssetImportTask()
                    task.filename = source_file
                    task.destination_path = folder_path
                    task.destination_name = asset_name
                    
                    # Apply general settings from FBX_IMPORT_SETTINGS
                    task.replace_existing = FBX_IMPORT_SETTINGS["replace_existing"]
                    task.automated = FBX_IMPORT_SETTINGS["automated"]
                    task.save = FBX_IMPORT_SETTINGS["save"]
                    
                    # Set up a simple FBX factory with basic settings
                    fbx_factory = unreal.FbxFactory()
                    
                    # Apply factory options that are known to work
                    for option, value in FBX_IMPORT_SETTINGS["factory_options"].items():
                        try:
                            fbx_factory.set_editor_property(option, value)
                        except Exception:
                            print(f"Warning: Could not set factory option: {option}")
                    
                    # Assign factory to task
                    task.factory = fbx_factory
                    
                    # Import the asset
                    result = asset_tools.import_asset_tasks([task])
                    
                    if result and len(result) > 0:
                        print(f"Successfully imported new static mesh assets using import task")
                        
                        # Count the number of static meshes that were created
                        new_assets = editor_lib.list_assets(folder_path, recursive=True, include_folder=False)
                        new_static_meshes = []
                        
                        for asset_path in new_assets:
                            try:
                                if name_filter and name_filter.lower() not in asset_path.lower():
                                    continue
                                    
                                asset = editor_lib.load_asset(asset_path)
                                if asset and isinstance(asset, unreal.StaticMesh):
                                    new_static_meshes.append(asset_path)
                            except Exception:
                                pass
                        
                        new_count = len(new_static_meshes)
                        print(f"Created {new_count} new static mesh assets")
                        total_success_count += new_count
                        total_assets_processed += new_count
                        continue
                except Exception as task_e:
                    print(f"Import task method failed: {str(task_e)}")
                
                # Method 2: Try direct import
                try:
                    # Import the FBX file directly
                    full_path = f"{folder_path}/{asset_name}"
                    imported = editor_lib.import_asset(source_file, full_path)
                    
                    if imported:
                        print(f"Successfully imported new static mesh assets using direct import")
                        
                        # Count the number of static meshes that were created
                        new_assets = editor_lib.list_assets(folder_path, recursive=True, include_folder=False)
                        new_static_meshes = []
                        
                        for asset_path in new_assets:
                            try:
                                if name_filter and name_filter.lower() not in asset_path.lower():
                                    continue
                                    
                                asset = editor_lib.load_asset(asset_path)
                                if asset and isinstance(asset, unreal.StaticMesh):
                                    new_static_meshes.append(asset_path)
                            except Exception:
                                pass
                        
                        new_count = len(new_static_meshes)
                        print(f"Created {new_count} new static mesh assets")
                        total_success_count += new_count
                        total_assets_processed += new_count
                        continue
                except Exception as import_e:
                    print(f"Direct import method failed: {str(import_e)}")
                
                print(f"All import methods failed for {asset_name}")
                total_assets_processed += 1
            except Exception as e:
                print(f"Error during initial import: {str(e)}")
                total_assets_processed += 1
    
    # Print overall summary
    print(f"\n=== OVERALL IMPORT/REIMPORT SUMMARY ===")
    print(f"Successfully processed {total_success_count} of {total_assets_processed} Static Meshes across all configurations")
    
    if total_success_count < total_assets_processed:
        print("Some imports failed. Check the log for details.")
    else:
        print("All Static Mesh operations completed successfully!")
        
    return total_success_count

# Run the reimport function
reimport_folder_static_meshes()
