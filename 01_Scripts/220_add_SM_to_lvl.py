# Script to add an asset to the current level in UE5.3.2

import unreal


def add_SM_sidewalks_and_roads_to_level(iteration_number=1):
    """
    Adds all static meshes named 'sidewalks_{iteration_number}' and 'road_{iteration_number}' to the current level.
    Sidewalk meshes are placed in a 'Sidewalks' folder, road meshes in a 'Roads' folder in the World Outliner.
    """
    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    editor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

    sidewalk_asset_name = f"sidewalks_{iteration_number}"
    road_asset_name = f"road_{iteration_number}"
    sidewalk_folder = "Sidewalks"
    road_folder = "Roads"

    # Use AssetRegistry filter to find all StaticMesh assets
    ar_filter = unreal.ARFilter(
        class_names=["StaticMesh"],
        recursive_classes=True,
        recursive_paths=True
    )
    asset_data_list = asset_registry.get_assets(ar_filter)
    def debug_log(msg):
        unreal.log_warning(msg)

    debug_log(f"[DEBUG] Iteration: {iteration_number}")
    debug_log(f"[DEBUG] Looking for asset names: {sidewalk_asset_name} (sidewalk), {road_asset_name} (road)")
    debug_log(f"[DEBUG] Listing all StaticMesh assets found:")
    for a in asset_data_list:
        debug_log(f"[DEBUG]   asset_name: {a.asset_name}, full_name: {a.get_full_name()}, package_name: {a.package_name}")

    sidewalk_prefix = f"sidewalks_{iteration_number}_piece_"
    road_prefix = f"road_{iteration_number}_piece_"
    sidewalk_assets = [a for a in asset_data_list if str(a.asset_name).startswith(sidewalk_prefix)]
    road_assets = [a for a in asset_data_list if str(a.asset_name).startswith(road_prefix)]
    debug_log(f"[DEBUG] Found {len(sidewalk_assets)} sidewalk assets: {[a.get_full_name() for a in sidewalk_assets]}")
    debug_log(f"[DEBUG] Found {len(road_assets)} road assets: {[a.get_full_name() for a in road_assets]}")

    # Helper to spawn and folder
    def spawn_and_folder(asset_data, folder_name):
        # Use package_name to load asset
        asset_path = str(asset_data.package_name)
        debug_log(f"[DEBUG] Attempting to load asset: {asset_path}")
        asset = unreal.EditorAssetLibrary.load_asset(asset_path)
        if not asset:
            msg = f"Asset not found: {asset_path}"
            unreal.log_error(msg)
            debug_log(f"[DEBUG] {msg}")
            return None
        debug_log(f"[DEBUG] Asset loaded: {asset_path}")
        # Spawn a StaticMeshActor in the level
        actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0,0,0), unreal.Rotator(0,0,0))
        if actor:
            debug_log(f"[DEBUG] Spawned StaticMeshActor: {actor.get_name()}")
            static_mesh_comp = actor.get_component_by_class(unreal.StaticMeshComponent)
            if static_mesh_comp:
                static_mesh_comp.set_static_mesh(asset)
                debug_log(f"[DEBUG] Set static mesh for actor: {actor.get_name()} to {asset_path}")
            else:
                debug_log(f"[DEBUG] StaticMeshComponent not found on actor: {actor.get_name()}")
            actor.set_folder_path(folder_name)
            actor.set_actor_label(asset_data.asset_name, mark_dirty=True)
            msg = f"Added '{asset_data.asset_name}' to level in folder '{folder_name}'"
            unreal.log(msg)
            debug_log(f"[DEBUG] {msg}")
        else:
            msg = f"Failed to spawn StaticMeshActor for: {asset_path}"
            unreal.log_error(msg)
            debug_log(f"[DEBUG] {msg}")
        return actor

    # Add sidewalks
    for asset_data in sidewalk_assets:
        spawn_and_folder(asset_data, sidewalk_folder)
    # Add roads
    for asset_data in road_assets:
        spawn_and_folder(asset_data, road_folder)

    unreal.log(f"Finished adding sidewalks and roads for iteration {iteration_number}.")
    return True

if __name__ == "__main__":
    # Default call for testing or direct execution
    add_SM_sidewalks_and_roads_to_level(iteration_number=5)
