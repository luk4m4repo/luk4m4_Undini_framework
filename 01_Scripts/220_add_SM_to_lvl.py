"""  
Static Mesh Level Placement Script for Unreal Engine
-----------------------------------------

This script is the eighth step in the Undini procedural generation pipeline:
1. Export splines from Unreal Engine (000_export_splines_as_json.py)
2. Export GenZone meshes from UE (010_export_gz_to_mod.py)
3. Process building data in Houdini (100_headless_topnet_PCGHD.py)
4. Import CSV files back into Unreal Engine (110_reimport_datatable.py)
5. Create PCG graphs in Unreal Engine (120_create_pcg_graph.py)
6. Generate sidewalks and roads in Houdini (200_headless_topnet_SWR.py)
7. Import sidewalk and road meshes into Unreal Engine (210_reimport_SM.py)
8. Add sidewalks and roads to the level (this script)

This script finds all static meshes with names matching the specified iteration number
pattern and adds them to the current level in organized folders.

Usage:
    From Python in Unreal Engine:
    ```python
    import add_SM_sidewalks_and_roads_to_level
    add_SM_sidewalks_and_roads_to_level(iteration_number=5)
    ```

    Or run directly:
    ```
    python 220_add_SM_to_lvl.py
    ```
"""

import unreal
import os


def add_SM_sidewalks_and_roads_to_level(iteration_number=1):
    """
    Adds sidewalk and road static meshes to the current level for a specific iteration.
    
    Args:
        iteration_number (int): The iteration number to use when finding assets.
            This should match the iteration used in the previous pipeline steps.
    
    Returns:
        bool: True if assets were added successfully, False otherwise.
    
    This finds all static meshes with names starting with 'sidewalks_{iteration_number}_piece_' 
    and 'road_{iteration_number}_piece_', then adds them to the level in organized folders.
    """
    # Get the asset registry to search for meshes
    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    editor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

    # Define names and folders for organizing actors in the level
    sidewalk_folder = "Sidewalks"
    road_folder = "Roads"
    
    # Simple debug log function with emoji indicators for better readability
    def debug_log(msg, level="info"):
        """Log a message with appropriate level and emoji indicator"""
        if level == "info":
            unreal.log(f"ℹ️ {msg}")
        elif level == "success":
            unreal.log(f"✅ {msg}")
        elif level == "warning":
            unreal.log_warning(f"⚠️ {msg}")
        elif level == "error":
            unreal.log_error(f"❌ {msg}")
        else:
            unreal.log(f"🔍 {msg}")  # Debug level

    # Set up asset registry filter to find static meshes
    debug_log(f"Starting search for sidewalks and roads for iteration {iteration_number}", "info")
    
    try:
        ar_filter = unreal.ARFilter(
            class_names=["StaticMesh"],
            recursive_classes=True,
            recursive_paths=True
        )
        
        # Get all static mesh assets
        debug_log("Querying asset registry for all static meshes...", "debug")
        asset_data_list = asset_registry.get_assets(ar_filter)
        debug_log(f"Found {len(asset_data_list)} total static meshes in the project", "debug")
        
        # Define prefixes for this iteration
        sidewalk_prefix = f"sidewalks_{iteration_number}_piece_"
        road_prefix = f"road_{iteration_number}_piece_"
        
        debug_log(f"Looking for assets with prefixes:", "debug")
        debug_log(f"  • Sidewalks: '{sidewalk_prefix}'", "debug")
        debug_log(f"  • Roads: '{road_prefix}'", "debug")
        
        # Filter assets by name prefix
        sidewalk_assets = [a for a in asset_data_list if str(a.asset_name).startswith(sidewalk_prefix)]
        road_assets = [a for a in asset_data_list if str(a.asset_name).startswith(road_prefix)]
        
        # Log what we found with appropriate emoji indicators
        if sidewalk_assets:
            debug_log(f"Found {len(sidewalk_assets)} sidewalk pieces for iteration {iteration_number}", "success")
        else:
            debug_log(f"No sidewalk pieces found for iteration {iteration_number}", "warning")
            
        if road_assets:
            debug_log(f"Found {len(road_assets)} road pieces for iteration {iteration_number}", "success")
        else:
            debug_log(f"No road pieces found for iteration {iteration_number}", "warning")
    except Exception as e:
        debug_log(f"Error searching for assets: {str(e)}", "error")
        return False

    # Helper function to spawn an actor and put it in the right folder
    def spawn_and_folder(asset_data, folder_name):
        """
        Spawn a static mesh actor in the level and organize it in a folder.
        
        Args:
            asset_data: The asset data object from the asset registry
            folder_name: The folder to place the actor in
            
        Returns:
            The spawned actor or None if unsuccessful
        """
        # Get the asset path and load it
        asset_path = str(asset_data.package_name)
        asset_name = str(asset_data.asset_name)
        debug_log(f"Loading asset: {asset_path}", "debug")
        
        try:
            # Load the asset
            asset = unreal.EditorAssetLibrary.load_asset(asset_path)
            
            # Check if the asset was loaded successfully
            if not asset:
                debug_log(f"Couldn't find the asset: {asset_path}. Is it in the right place?", "error")
                return None
                
            # Spawn a new StaticMeshActor at the origin
            debug_log(f"Spawning actor for {asset_name}", "debug")
            actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
                unreal.StaticMeshActor, 
                unreal.Vector(0, 0, 0), 
                unreal.Rotator(0, 0, 0)
            )
            
            if not actor:
                debug_log(f"Failed to spawn actor for: {asset_path}", "error")
                return None
                
            # Get the static mesh component and assign our mesh to it
            static_mesh_comp = actor.get_component_by_class(unreal.StaticMeshComponent)
            if static_mesh_comp:
                static_mesh_comp.set_static_mesh(asset)
                
                # Set the folder and name
                actor.set_folder_path(folder_name)
                actor.set_actor_label(asset_name, mark_dirty=True)
                debug_log(f"Added '{asset_name}' to level in folder '{folder_name}'", "success")
                return actor
            else:
                debug_log(f"No StaticMeshComponent found on actor: {actor.get_name()}", "error")
                # Clean up the actor since we couldn't set the mesh
                actor.destroy_actor()
                return None
                
        except Exception as e:
            debug_log(f"Error spawning actor for {asset_name}: {str(e)}", "error")
            return None

    # Check if we found any assets
    if not sidewalk_assets and not road_assets:
        debug_log(f"No sidewalk or road pieces found for iteration {iteration_number}", "warning")
        debug_log("Make sure you've completed these steps first:", "warning")
        debug_log("  1. Generated sidewalks and roads in Houdini (200_headless_topnet_SWR.py)", "warning")
        debug_log("  2. Imported the FBX files into Unreal Engine (210_reimport_SM.py)", "warning")
        return False
        
    # Track success and failure counts
    total_success = 0
    total_processed = 0
    
    # Add all the sidewalk pieces to the level
    if sidewalk_assets:
        debug_log(f"\n🛠 Adding {len(sidewalk_assets)} sidewalk pieces to the level...", "info")
        for i, asset_data in enumerate(sidewalk_assets):
            debug_log(f"Processing sidewalk piece {i+1}/{len(sidewalk_assets)}: {asset_data.asset_name}", "debug")
            actor = spawn_and_folder(asset_data, sidewalk_folder)
            total_processed += 1
            if actor:
                total_success += 1
    
    # Add all the road pieces to the level
    if road_assets:
        debug_log(f"\n🛠 Adding {len(road_assets)} road pieces to the level...", "info")
        for i, asset_data in enumerate(road_assets):
            debug_log(f"Processing road piece {i+1}/{len(road_assets)}: {asset_data.asset_name}", "debug")
            actor = spawn_and_folder(asset_data, road_folder)
            total_processed += 1
            if actor:
                total_success += 1

    # Show a summary of what we did
    debug_log(f"\n📊 Summary", "info")
    debug_log(f"  • Successfully placed: {total_success} of {total_processed} actors", "info")
    debug_log(f"  • Success rate: {(total_success/max(1, total_processed))*100:.1f}%", "info")
    
    if total_success < total_processed:
        debug_log("Some actors couldn't be placed. Check the log above for details.", "warning")
    else:
        debug_log(f"All sidewalks and roads for iteration {iteration_number} were added to the level!", "success")
    
    # Visual separator for the end of the script
    debug_log("\n" + "-" * 80, "info")
    return total_success > 0


# ======================================================================
# Main Execution
# ======================================================================

# Run the function when this script is executed directly
if __name__ == "__main__":
    debug_log("🚀 Starting Static Mesh placement process...", "info")
    debug_log("This is the eighth step in the Undini procedural generation pipeline.", "info")
    debug_log("It adds the sidewalks and roads to the current level.", "info")
    
    # You can modify this parameter for testing
    iteration_number = 5  # Change this as needed
    
    # Call the main function
    result = add_SM_sidewalks_and_roads_to_level(iteration_number=iteration_number)
    
    # Report the results
    if result:
        debug_log(f"\n🎉 Placement process completed successfully!", "success")
    else:
        debug_log(f"\n⚠️ No meshes were placed. Check the log above for details.", "warning")
