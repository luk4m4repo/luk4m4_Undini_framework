import unreal
import os

# Define the workspace root relative to this script
WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

# FBX import settings that work well with Unreal Engine 5.3.2
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

def reimport_folder_static_meshes(iteration_number=None, fbx_dir=None):
    """
    Imports or reimports static meshes from FBX files into Unreal Engine.
    
    Args:
        iteration_number (int): The iteration number for file naming
        fbx_dir (str): Directory containing the FBX files to import
    
    Returns:
        int: Number of successfully processed meshes
    """
    unreal.log("Looking for static meshes to import or update...")
    
    # Set default values if not provided
    if iteration_number is None:
        iteration_number = 0
    
    # Determine the FBX directory
    if fbx_dir is None:
        fbx_dir = os.path.join(WORKSPACE_ROOT, "03_GenDatas", "Dependancies", "SW_Roads", "Out", "Mod")
    
    unreal.log(f"Using FBX directory: {fbx_dir}")
    unreal.log(f"Using iteration number: {iteration_number}")
    
    # Define what we're importing - PCG HD meshes for this iteration
    import_configs = []
    
    # Look for all FBX files in the directory
    fbx_files = [f for f in os.listdir(fbx_dir) if f.endswith('.fbx')]
    unreal.log(f"Found {len(fbx_files)} FBX files in directory: {fbx_dir}")
    
    for fbx_file in fbx_files:
        # Extract the base name without extension
        base_name = os.path.splitext(fbx_file)[0]
        
        # Create a config for each FBX file
        import_configs.append({
            "source_file": os.path.join(fbx_dir, fbx_file),
            "folder_path": f"/Game/luk4m4_Undini/Assets/{base_name}",
            "asset_name": base_name,
            "name_filter": base_name
        })
        
    if not import_configs:
        unreal.log_warning(f"No FBX files found in directory: {fbx_dir}")
        unreal.log_warning("Please run the Houdini PCG generation script first")
        return 0
    
    # Get references to necessary libraries
    editor_lib = unreal.EditorAssetLibrary
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    editor_asset_subsystem = unreal.get_editor_subsystem(unreal.EditorAssetSubsystem)
    
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
                    
                    # Try to reimport using the asset registry
                    asset = editor_lib.load_asset(asset_path)
                    if asset:
                        # Create a reimport task
                        task = unreal.AssetImportTask()
                        task.filename = source_file
                        task.destination_path = os.path.dirname(asset_path)
                        task.destination_name = os.path.basename(asset_path).split(".")[0]
                        task.replace_existing = True
                        task.automated = True
                        task.save = True
                        
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
                # Create an import task
                task = unreal.AssetImportTask()
                task.filename = source_file
                task.destination_path = folder_path
                task.destination_name = asset_name
                task.replace_existing = True
                task.automated = True
                task.save = True
                
                # Create a factory with the right settings
                factory = unreal.FbxFactory()
                
                # Try different approaches to set the properties based on UE version
                try:
                    # Try using set_editor_property
                    factory.set_editor_property('ImportMaterials', True)
                    factory.set_editor_property('ImportTextures', True)
                    unreal.log("Using set_editor_property for factory configuration")
                except Exception as prop_e:
                    unreal.log_warning(f"Could not set properties using set_editor_property: {str(prop_e)}")
                    
                    # Try direct property access as a fallback
                    try:
                        # Different UE versions might use different property names
                        if hasattr(factory, 'ImportMaterials'):
                            factory.ImportMaterials = True
                            factory.ImportTextures = True
                            unreal.log("Using ImportMaterials property")
                        elif hasattr(factory, 'import_materials'):
                            factory.import_materials = True
                            factory.import_textures = True
                            unreal.log("Using import_materials property")
                    except Exception as attr_e:
                        unreal.log_warning(f"Could not set properties directly: {str(attr_e)}")
                
                # Assign the factory to the task
                task.factory = factory
                
                # Do the import
                unreal.log("Importing with asset tools...")
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
                else:
                    # Try alternative methods
                    unreal.log("First method didn't work, trying alternatives...")
                    
                    # Method 2: Try using the editor subsystem
                    try:
                        full_path = f"{folder_path}/{asset_name}"
                        unreal.log(f"Trying editor subsystem import to: {full_path}")
                        
                        # Import using the editor subsystem if available
                        if hasattr(editor_asset_subsystem, 'import_asset'):
                            result = editor_asset_subsystem.import_asset(source_file, full_path)
                            
                            if result:
                                unreal.log("Successfully imported using editor subsystem!")
                                total_success += 1
                                continue
                            else:
                                unreal.log_warning(f"Editor subsystem import failed for {asset_name}")
                        else:
                            unreal.log_warning("Editor subsystem doesn't have import_asset method")
                    except Exception as subsys_e:
                        unreal.log_warning(f"Editor subsystem import error: {str(subsys_e)}")
                    
                    # Method 3: Try using the content browser directly
                    try:
                        unreal.log("Trying content browser import...")
                        # Get the content browser module
                        content_browser = unreal.get_editor_subsystem(unreal.ContentBrowserSubsystem)
                        if content_browser:
                            # Create the destination path
                            destination_path = f"{folder_path}/{asset_name}"
                            unreal.log(f"Importing to content browser at: {destination_path}")
                            
                            # Try to import using the content browser
                            imported = False
                            
                            # Different UE versions have different methods
                            if hasattr(content_browser, 'import_assets_autosave'):
                                imported = content_browser.import_assets_autosave([source_file], folder_path)
                            elif hasattr(content_browser, 'import_asset_from_path'):
                                imported = content_browser.import_asset_from_path(source_file, folder_path)
                            
                            if imported:
                                unreal.log("Successfully imported using content browser!")
                                total_success += 1
                                continue
                            else:
                                unreal.log_warning("Content browser import returned False")
                        else:
                            unreal.log_warning("Could not get content browser subsystem")
                    except Exception as cb_e:
                        unreal.log_warning(f"Content browser import error: {str(cb_e)}")
                        
                    # If we get here, all methods failed
                    unreal.log_error(f"All import methods failed for {asset_name}")
                    unreal.log_error(f"This might be due to incompatibility with your UE version")
                    unreal.log_error(f"Consider importing the FBX files manually through the Unreal Editor")
                    
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
