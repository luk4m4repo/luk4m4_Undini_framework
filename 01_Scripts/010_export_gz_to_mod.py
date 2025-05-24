import unreal
import os

# Define the root directory of the workspace and the export directory for FBX files
WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
EXPORT_DIR = os.path.join(WORKSPACE_ROOT, '..', '03_GenDatas', 'Dependancies', 'PCG_HD', 'In', 'GZ', 'Mod')  # Relative to repo root


def get_all_static_meshes_in_level():
    """
    Finds all unique Static Mesh assets used by StaticMeshActors in the current Unreal level whose name contains 'genzone'.
    Returns a list of meshes that match.

    This function is the core of our export process. It searches the current level for Static Mesh Actors that contain
    'genzone' in their name, and returns a list of unique Static Mesh assets used by those actors.
    """
    # Get the editor actor subsystem to access level actors
    editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    # Get all actors in the current level
    all_actors = editor_actor_subsystem.get_all_level_actors()
    # Initialize a set to store unique static meshes
    static_meshes = set()
    # Iterate over all actors in the level
    for actor in all_actors:
        # Only consider StaticMeshActor (not Blueprints, etc)
        if isinstance(actor, unreal.StaticMeshActor):
            # Get the static mesh component of the actor
            sm_comp = actor.static_mesh_component
            if sm_comp:
                # Get the static mesh asset
                mesh = sm_comp.static_mesh
                # Check if the mesh name contains 'genzone' (case-insensitive)
                if mesh and 'genzone' in mesh.get_name().lower():
                    # Add the mesh to the set of unique meshes
                    static_meshes.add(mesh)
    # Return the list of unique static meshes
    return list(static_meshes)


def export_static_mesh_to_fbx(static_mesh, export_dir, iteration_number):
    """
    Exports a given static mesh to FBX format with a filename that includes the mesh name and iteration number.
    Returns True if successful, False otherwise.

    This function takes a Static Mesh asset, an export directory, and an iteration number, and exports the mesh to
    FBX format. The filename includes the mesh name and iteration number.
    """
    # Get the name of the static mesh
    mesh_name = static_mesh.get_name()
    # Construct the export path for the FBX file
    export_path = os.path.join(export_dir, f"{mesh_name}_{iteration_number}.fbx")
    # Set up FBX export options
    fbx_options = unreal.FbxExportOption()
    fbx_options.collision = False
    fbx_options.vertex_color = True
    fbx_options.level_of_detail = False
    fbx_options.fbx_export_compatibility = unreal.FbxExportCompatibility.FBX_2020
    # Create an asset export task for the static mesh
    export_task = unreal.AssetExportTask()
    export_task.object = static_mesh
    export_task.filename = export_path
    export_task.automated = True
    export_task.replace_identical = True
    export_task.prompt = False
    export_task.options = fbx_options
    try:
        # Run the asset export task
        result = unreal.Exporter.run_asset_export_task(export_task)
        if result:
            # Log a success message with a party popper emoji
            unreal.log(f"🎉 Successfully exported {mesh_name} to {export_path}!")
        else:
            # Log an error message with a warning sign emoji
            unreal.log_error(f"⚠️ Failed to export {mesh_name}. Please check the export settings and try again.")
        return result
    except Exception as e:
        # Log an error message with a red cross emoji
        unreal.log_error(f"❌ An error occurred while exporting {mesh_name}: {str(e)}")
        return False


def main(iteration_number=0):
    """
    Main entry point: exports all 'genzone' static meshes in the current level to FBX files.

    This function is the main entry point of our script. It checks if the export directory exists, gets all static
    meshes in the level with 'genzone' in their name, and exports each mesh to FBX format.
    """
    # Check if the export directory exists
    if not os.path.exists(EXPORT_DIR):
        try:
            # Create the export directory if it doesn't exist
            os.makedirs(EXPORT_DIR, exist_ok=True)
            # Log a message indicating the directory was created
            unreal.log(f"Created export directory: {EXPORT_DIR}")
        except Exception as e:
            # Log an error message if directory creation fails
            unreal.log_error(f"Couldn't create export directory '{EXPORT_DIR}'. Error: {str(e)}")
            return
    # Get all static meshes in the level with 'genzone' in their name
    meshes = get_all_static_meshes_in_level()
    if not meshes:
        # Log a warning message if no meshes are found
        unreal.log_warning("No Static Meshes with 'genzone' in the name found in the current level. Nothing to export!")
        return
    # Log a message indicating the number of meshes found
    unreal.log(f"Found {len(meshes)} unique Static Mesh assets with 'genzone' in the name.")
    # Initialize a counter for successful exports
    success_count = 0
    # Iterate over the meshes and export each one
    for mesh in meshes:
        if export_static_mesh_to_fbx(mesh, EXPORT_DIR, iteration_number):
            # Increment the success counter if the export is successful
            success_count += 1
    # Log a message indicating the export is complete
    unreal.log(f"✅ Export complete: {success_count}/{len(meshes)} meshes exported to {EXPORT_DIR}")


if __name__ == "__main__":
    main(0)
