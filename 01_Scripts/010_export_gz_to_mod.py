import unreal
import os

# Define the root directory of the workspace and the export directory for FBX files
# This is used when the script is run standalone, otherwise the export_dir parameter is used
WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Default export directory - follows the same structure as in the manager script
# This is where we'll save the FBX files that will be used by Houdini
DEFAULT_EXPORT_DIR = os.path.join(WORKSPACE_ROOT, "03_GenDatas", "Dependancies", "PCG_HD", "In", "GZ", "Mod")


def get_all_static_meshes_in_level():
    """
    Finds all unique Static Mesh assets used by StaticMeshActors in the current Unreal level whose name contains 'genzone'.
    Returns a list of meshes that match.
    
    This is the second step in our pipeline - after exporting splines, we need to export the GenZone meshes
    that will be used by Houdini for procedural generation. This function identifies which meshes need to be exported.
    
    The function looks for both actors with 'genzone' in their name and meshes with 'genzone' in their name,
    ensuring we catch all relevant assets regardless of how they're named in the level.
    """
    # First, let's access all actors in the current level
    unreal.log("🔍 Starting search for GenZone meshes in the current level...")
    editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    all_actors = editor_actor_subsystem.get_all_level_actors()
    
    # We'll use a set to automatically eliminate duplicates
    static_meshes = set()
    
    # Keep track of some stats for reporting
    total_static_mesh_actors = 0
    genzone_actors = 0
    
    # Now let's go through all actors and find the ones we need
    for actor in all_actors:
        # We only care about StaticMeshActors (not Blueprints, Lights, etc.)
        if isinstance(actor, unreal.StaticMeshActor):
            total_static_mesh_actors += 1
            actor_name = actor.get_actor_label()
            
            # First check: Is 'genzone' in the actor's name?
            if 'genzone' in actor_name.lower():
                genzone_actors += 1
                unreal.log(f"Found GenZone actor: {actor_name}")
                
            # Now let's check the actual mesh asset
            sm_comp = actor.static_mesh_component
            if sm_comp:
                mesh = sm_comp.static_mesh
                if mesh:
                    mesh_name = mesh.get_name()
                    
                    # Second check: Is 'genzone' in either the actor name OR the mesh name?
                    # This catches cases where the mesh name contains 'genzone' but the actor doesn't
                    if ('genzone' in mesh_name.lower()) or ('genzone' in actor_name.lower()):
                        # Add this mesh to our export list (the set automatically prevents duplicates)
                        static_meshes.add(mesh)
                        unreal.log(f"✅ Added to export list: {mesh_name} (from actor {actor_name})")
    
    # Let's summarize what we found
    unreal.log(f"\n📊 Search summary:")
    unreal.log(f"  • Total static mesh actors in level: {total_static_mesh_actors}")
    unreal.log(f"  • Actors with 'genzone' in name: {genzone_actors}")
    unreal.log(f"  • Unique meshes to export: {len(static_meshes)}")
    
    if len(static_meshes) == 0:
        unreal.log_warning("⚠️ No GenZone meshes found! Make sure you have GenZone actors in your level.")
    else:
        unreal.log(f"🔍 Found {len(static_meshes)} unique GenZone meshes to export.")
    
    # Return the list of unique static meshes
    return list(static_meshes)


def export_static_mesh_to_fbx(static_mesh, export_dir, iteration_number):
    """
    Exports a given static mesh to FBX format with a filename based on the mesh name.
    
    This function handles the actual export of each GenZone mesh to FBX format. The exported FBX files
    will be used by Houdini when switch_bool is set to 1 in the pipeline. Each mesh is exported to its own file
    inside a folder named SM_genzones_PCG_HD_{iteration_number}.
    
    Args:
        static_mesh: The Unreal Engine static mesh asset to export
        export_dir: Directory where the FBX file will be saved
        iteration_number: The current iteration number for the folder name
        
    Returns:
        bool: True if the export was successful, False otherwise
    """
    # First, get the name of the mesh we're exporting
    mesh_name = static_mesh.get_name()
    
    # Create the folder path where we'll save all the FBX files
    folder_name = f"SM_genzones_PCG_HD_{iteration_number}"
    folder_path = os.path.join(export_dir, folder_name)
    
    # Make sure the folder exists
    if not os.path.exists(folder_path):
        try:
            os.makedirs(folder_path, exist_ok=True)
            unreal.log(f"📁 Created export folder: {folder_path}")
        except Exception as e:
            unreal.log_error(f"❌ Couldn't create export folder '{folder_path}'. Error: {str(e)}")
            return False
    
    # Create the full path where we'll save this specific mesh
    export_path = os.path.join(folder_path, f"{mesh_name}.fbx")
    unreal.log(f"Preparing to export {mesh_name} to {export_path}")
    
    # Configure the FBX export options for best compatibility with Houdini
    # These settings are optimized for our pipeline
    fbx_options = unreal.FbxExportOption()
    fbx_options.collision = False        # We don't need collision data
    fbx_options.vertex_color = True      # Preserve vertex colors if present
    fbx_options.level_of_detail = False  # Don't include LODs
    fbx_options.fbx_export_compatibility = unreal.FbxExportCompatibility.FBX_2020  # Use FBX 2020 format
    
    # Set up the export task with our configured options
    export_task = unreal.AssetExportTask()
    export_task.object = static_mesh
    export_task.filename = export_path
    export_task.automated = True         # Run without user interaction
    export_task.replace_identical = True  # Overwrite existing files
    export_task.prompt = False           # Don't show any prompts
    export_task.options = fbx_options
    try:
        # Now let's actually perform the export
        unreal.log(f"Exporting {mesh_name}...")
        result = unreal.Exporter.run_asset_export_task(export_task)
        
        if result:
            # Success! Let the user know
            unreal.log(f"🎉 Successfully exported {mesh_name} to {export_path}!")
            
            # Verify the file was actually created
            if os.path.exists(export_path):
                file_size = os.path.getsize(export_path)
                unreal.log(f"   File size: {file_size / 1024:.1f} KB")
            else:
                # This should never happen if result is True, but just in case
                unreal.log_warning(f"⚠️ Export reported success but file not found at {export_path}")
                return False
        else:
            # Something went wrong with the export
            unreal.log_error(f"⚠️ Failed to export {mesh_name}. Please check the export settings and try again.")
            unreal.log_error(f"   This might be due to the mesh being invalid or having unsupported features.")
        
        return result
    except Exception as e:
        # An unexpected error occurred
        unreal.log_error(f"❌ An error occurred while exporting {mesh_name}:")
        unreal.log_error(f"   Error details: {str(e)}")
        return False

def export_actor_transforms_to_json(actors, export_dir, iteration_number):
    """
    Exports the transforms (location, rotation, scale) of the provided actors to a JSON file.
    
    Args:
        actors: List of actors whose transforms should be exported
        export_dir: Directory where the JSON file will be saved
        iteration_number: The current iteration number for file naming
        
    Returns:
        bool: True if the export was successful, False otherwise
    """
    import json
    
    # Create the folder path where we'll save all files
    folder_name = f"SM_genzones_PCG_HD_{iteration_number}"
    folder_path = os.path.join(export_dir, folder_name)
    
    # Make sure the folder exists
    if not os.path.exists(folder_path):
        try:
            os.makedirs(folder_path, exist_ok=True)
            unreal.log(f"📁 Created export folder: {folder_path}")
        except Exception as e:
            unreal.log_error(f"❌ Couldn't create export folder '{folder_path}'. Error: {str(e)}")
            return False
    
    # Create the full path where we'll save the JSON file
    json_filename = "transforms.json"
    json_path = os.path.join(folder_path, json_filename)
    unreal.log(f"Preparing to export transforms of {len(actors)} actors to {json_path}")
    
    # Create a dictionary to store the transforms
    transforms_data = {
        "actors": []
    }
    
    # Extract transform data from each actor
    for actor in actors:
        actor_name = actor.get_actor_label()
        
        # Get the static mesh component
        sm_comp = actor.static_mesh_component
        if not sm_comp:
            unreal.log_warning(f"⚠️ Actor {actor_name} has no static mesh component, skipping...")
            continue
            
        # Get the mesh name
        mesh = sm_comp.static_mesh
        if not mesh:
            unreal.log_warning(f"⚠️ Actor {actor_name} has no static mesh, skipping...")
            continue
            
        mesh_name = mesh.get_name()
        
        # Get the transform
        transform = sm_comp.get_relative_transform()
        location = transform.translation
        rotation = transform.rotation.rotator()
        scale = transform.scale3d
        
        # Add to our data structure
        actor_data = {
            "actor_name": actor_name,
            "mesh_name": mesh_name,
            "transform": {
                "location": {
                    "x": location.x,
                    "y": location.y,
                    "z": location.z
                },
                "rotation": {
                    "pitch": rotation.pitch,
                    "yaw": rotation.yaw,
                    "roll": rotation.roll
                },
                "scale": {
                    "x": scale.x,
                    "y": scale.y,
                    "z": scale.z
                }
            }
        }
        
        transforms_data["actors"].append(actor_data)
        unreal.log(f"Added transform data for actor: {actor_name}")
    
    try:
        # Write the JSON file
        with open(json_path, 'w') as json_file:
            json.dump(transforms_data, json_file, indent=4)
        
        unreal.log(f"🎉 Successfully exported transforms of {len(transforms_data['actors'])} actors to {json_path}!")
        return True
    except Exception as e:
        unreal.log_error(f"❌ An error occurred while exporting transforms to JSON:")
        unreal.log_error(f"   Error details: {str(e)}")
        return False


def main(iteration_number=0, export_dir=None):
    """
    Main entry point: exports all 'genzone' static meshes in the current level to a single FBX file.
    
    This is the second step in our pipeline - after exporting splines, we need to export the GenZone meshes
    that will be used by Houdini for procedural generation when switch_bool is set to 1.
    The exported file will be named SM_genzones_PCG_HD_[iteration_number].fbx.
    
    Args:
        iteration_number (int): The current iteration number for file naming (default: 0)
        export_dir (str): Optional directory to save the FBX files. If None, uses DEFAULT_EXPORT_DIR
        
    Returns:
        dict: Information about the export process including success count and export directory
    """
    # Create a result dictionary to return
    result = {
        'success_count': 0,
        'total_count': 0,
        'export_dir': None,
        'export_folder': None
    }
    
    # Determine which export directory to use
    if export_dir is None:
        export_dir = DEFAULT_EXPORT_DIR
        unreal.log(f"Using default export directory: {export_dir}")
    else:
        unreal.log(f"Using specified export directory: {export_dir}")
    
    # Store the export directory in the result
    result['export_dir'] = export_dir
    
    # Make sure the export directory exists
    if not os.path.exists(export_dir):
        try:
            os.makedirs(export_dir, exist_ok=True)
            unreal.log(f"📁 Created export directory: {export_dir}")
        except Exception as e:
            unreal.log_error(f"❌ Couldn't create export directory '{export_dir}'. Error: {str(e)}")
            return result
    
    # Find all GenZone meshes in the current level
    unreal.log("\n🔍 Looking for GenZone meshes to export...")
    meshes = get_all_static_meshes_in_level()
    
    # Update the result with the total count
    result['total_count'] = len(meshes)
    
    # Check if we found any meshes
    if not meshes:
        unreal.log_warning("⚠️ No GenZone meshes found in the current level. Nothing to export!")
        return result

        # Find all GenZone actors in the current level
    unreal.log("\n🔍 Looking for GenZone actors in the current level...")
    genzone_actors = []
    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        if isinstance(actor, unreal.StaticMeshActor) and 'genzone' in actor.get_actor_label().lower():
            genzone_actors.append(actor)
    
    # Export transforms to JSON
    if genzone_actors:
        unreal.log(f"\n📊 Exporting transforms of {len(genzone_actors)} GenZone actors to JSON...")
        export_actor_transforms_to_json(genzone_actors, export_dir, iteration_number)
    
    # Start the export process
    unreal.log(f"\n📦 Starting export of {len(meshes)} GenZone meshes to FBX format...")
    
    # Keep track of successful exports
    success_count = 0
    
    # Export each mesh
    for mesh in meshes:
        if export_static_mesh_to_fbx(mesh, export_dir, iteration_number):
            success_count += 1
    
    # Update the result with the success count
    result['success_count'] = success_count
    
    # Create the folder path for reference in the summary
    folder_name = f"SM_genzones_PCG_HD_{iteration_number}"
    folder_path = os.path.join(export_dir, folder_name)
    
    # Store the folder path in the result
    result['export_folder'] = folder_path
    
    # Summarize the results
    if success_count == len(meshes):
        unreal.log(f"\n✅ Export complete: All {success_count} meshes successfully exported to folder:\n   {folder_path}")
    else:
        unreal.log(f"\n⚠️ Export partially complete: {success_count}/{len(meshes)} meshes exported to folder:\n   {folder_path}")
        if success_count == 0:
            unreal.log_error("❌ All exports failed! Check the log for error details.")
    
    return result


if __name__ == "__main__":
    # When run as a standalone script, we'll use environment variables or defaults
    unreal.log("🔹 Starting GenZone mesh export script...")
    
    # Get the iteration number from the environment variable, or use 0 if not set
    iteration_number = int(os.environ.get("ITERATION_NUMBER", 0))
    unreal.log(f"Using iteration number: {iteration_number}")
    
    # Call the main function with the iteration number
    result = main(iteration_number)
    
    # Report the final status
    if result['success_count'] > 0:
        unreal.log(f"🔹 GenZone mesh export completed with {result['success_count']}/{result['total_count']} successful exports.")
    else:
        unreal.log_error("🔹 GenZone mesh export failed. Please check the logs for details.")
    
    # This helps to visually separate this script's output from the next script in the pipeline
    unreal.log("\n" + "-" * 80 + "\n")
