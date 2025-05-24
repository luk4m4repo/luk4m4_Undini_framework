import unreal


def add_SM_sidewalks_and_roads_to_level(iteration_number=1):
    """
    Adds sidewalk and road static meshes to the current level for a specific iteration.
    
    This finds all static meshes with names starting with 'sidewalks_{iteration_number}_piece_' 
    and 'road_{iteration_number}_piece_', then adds them to the level in organized folders.
    """
    # Get the asset registry to search for meshes
    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    editor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

    # Define names and folders
    sidewalk_folder = "Sidewalks"
    road_folder = "Roads"
    
    # Simple debug log function
    def debug_log(msg):
        unreal.log_warning(msg)

    # Set up asset registry filter to find static meshes
    ar_filter = unreal.ARFilter(
        class_names=["StaticMesh"],
        recursive_classes=True,
        recursive_paths=True
    )
    
    # Get all static mesh assets
    asset_data_list = asset_registry.get_assets(ar_filter)
    
    # Log debug info
    debug_log(f"[DEBUG] Looking for assets for iteration: {iteration_number}")
    
    # Define prefixes for this iteration
    sidewalk_prefix = f"sidewalks_{iteration_number}_piece_"
    road_prefix = f"road_{iteration_number}_piece_"
    
    # Filter assets by name prefix
    sidewalk_assets = [a for a in asset_data_list if str(a.asset_name).startswith(sidewalk_prefix)]
    road_assets = [a for a in asset_data_list if str(a.asset_name).startswith(road_prefix)]
    
    # Log what we found
    debug_log(f"[DEBUG] Found {len(sidewalk_assets)} sidewalk pieces and {len(road_assets)} road pieces")

    # Helper function to spawn an actor and put it in the right folder
    def spawn_and_folder(asset_data, folder_name):
        # Get the asset path and load it
        asset_path = str(asset_data.package_name)
        debug_log(f"[DEBUG] Loading asset: {asset_path}")
        asset = unreal.EditorAssetLibrary.load_asset(asset_path)
        
        # Check if the asset was loaded successfully
        if not asset:
            unreal.log_error(f"Hmm, couldn't find the asset: {asset_path}. Is it in the right place?")
            return None
            
        # Spawn a new StaticMeshActor at the origin
        actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.StaticMeshActor, 
            unreal.Vector(0, 0, 0), 
            unreal.Rotator(0, 0, 0)
        )
        
        if actor:
            # Get the static mesh component and assign our mesh to it
            static_mesh_comp = actor.get_component_by_class(unreal.StaticMeshComponent)
            if static_mesh_comp:
                static_mesh_comp.set_static_mesh(asset)
            else:
                debug_log(f"[DEBUG] No StaticMeshComponent on actor: {actor.get_name()}")
                
            # Set the folder and name
            actor.set_folder_path(folder_name)
            actor.set_actor_label(asset_data.asset_name, mark_dirty=True)
            unreal.log(f"Added '{asset_data.asset_name}' to level in folder '{folder_name}'")
        else:
            unreal.log_error(f"Couldn't spawn actor for: {asset_path}. Something went wrong.")
            
        return actor

    # Check if we found any assets
    if not sidewalk_assets and not road_assets:
        unreal.log_warning(f"Hey! No sidewalk or road pieces found for iteration {iteration_number}. Did you generate them first?")
        return False
        
    # Add all the sidewalk pieces to the level
    if sidewalk_assets:
        unreal.log(f"Adding {len(sidewalk_assets)} sidewalk pieces to the level...")
        for asset_data in sidewalk_assets:
            spawn_and_folder(asset_data, sidewalk_folder)
    
    # Add all the road pieces to the level
    if road_assets:
        unreal.log(f"Adding {len(road_assets)} road pieces to the level...")
        for asset_data in road_assets:
            spawn_and_folder(asset_data, road_folder)

    unreal.log(f"All done! Added sidewalks and roads for iteration {iteration_number} to the level.")
    return True


# Run the function when this script is executed directly
if __name__ == "__main__":
    add_SM_sidewalks_and_roads_to_level(iteration_number=5)
