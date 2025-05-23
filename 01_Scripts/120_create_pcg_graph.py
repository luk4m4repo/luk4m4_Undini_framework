import unreal

def duplicate_and_rename_pcg_blueprint(iteration_number=0):
    """
    Duplicates the BP_PCG_HD_TEMPLATE blueprint and saves it as BPi_PCG_HD_{iteration_number}
    in /Game/Developers/lukacroisez/PCG_HD/BP/BP_PCG_HD_inst/
    """
    src_path = "/Game/Developers/lukacroisez/PCG_HD/BP/BP_PCG_HD_TEMPLATE.BP_PCG_HD_TEMPLATE"
    dst_folder = "/Game/Developers/lukacroisez/PCG_HD/BP/BP_PCG_HD_inst"
    dst_base_name = f"BPi_PCG_HD_{iteration_number}"
    dst_path = f"{dst_folder}/{dst_base_name}"

    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    editor_asset_lib = unreal.EditorAssetLibrary

    # Check if source exists
    if not editor_asset_lib.does_asset_exist(src_path):
        unreal.log_error(f"Source blueprint does not exist: {src_path}")
        return None
    
    # Duplicate asset
    try:
        new_asset = asset_tools.duplicate_asset(
            asset_name=dst_base_name,
            package_path=dst_folder,
            original_object=editor_asset_lib.load_asset(src_path)
        )
        if not new_asset:
            unreal.log_error(f"Failed to duplicate asset {src_path} to {dst_path}")
            return None
        unreal.log(f"Successfully duplicated blueprint to {dst_path}")
        # Spawn the new BP in the current level
        try:
            actor = unreal.EditorLevelLibrary.spawn_actor_from_object(new_asset, unreal.Vector(0,0,0), unreal.Rotator(0,0,0))
            if actor:
                unreal.log(f"Spawned new BP actor '{dst_base_name}' in the level at origin.")
            else:
                unreal.log_error("Failed to spawn new BP actor in the level.")
        except Exception as spawn_e:
            unreal.log_error(f"Error spawning BP in level: {spawn_e}")
        return new_asset
    except Exception as e:
        unreal.log_error(f"Error duplicating blueprint: {e}")
        return None

if __name__ == "__main__":

    duplicate_and_rename_pcg_blueprint(iteration_number=0)
