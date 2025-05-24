import unreal

# ======================================================================
# PCG Graph Blueprint Creation Script
# ======================================================================

def duplicate_and_rename_pcg_blueprint(iteration_number=0):
    """
    Creates a new Procedural Content Generation (PCG) graph for the current iteration.
    
    This function performs the following operations:
    1. Duplicates the template PCG blueprint (BP_PCG_HD_TEMPLATE)
    2. Renames it with the current iteration number (BPi_PCG_HD_{iteration_number})
    3. Places the new blueprint in the designated folder
    4. Spawns an instance of the blueprint in the current level at the origin
    
    Args:
        iteration_number (int): The current iteration number to append to the blueprint name
        
    Returns:
        unreal.Blueprint: The newly created blueprint asset, or None if the operation failed
    """
    # Define source and destination paths for the blueprint
    template_blueprint_path = "/Game/Developers/lukacroisez/PCG_HD/BP/BP_PCG_HD_TEMPLATE.BP_PCG_HD_TEMPLATE"
    destination_folder_path = "/Game/Developers/lukacroisez/PCG_HD/BP/BP_PCG_HD_inst"
    new_blueprint_name = f"BPi_PCG_HD_{iteration_number}"
    full_destination_path = f"{destination_folder_path}/{new_blueprint_name}"

    # Get Unreal Engine asset management utilities
    asset_tools_helper = unreal.AssetToolsHelpers.get_asset_tools()
    editor_asset_library = unreal.EditorAssetLibrary

    # Validate that the template blueprint exists
    if not editor_asset_library.does_asset_exist(template_blueprint_path):
        unreal.log_error(f"❌ Template blueprint not found: {template_blueprint_path}")
        unreal.log_warning(f"⚠️ Please ensure the PCG template blueprint exists before running this script.")
        return None
    
    # Attempt to duplicate the blueprint asset
    try:
        unreal.log(f"🔄 Creating new PCG blueprint for iteration {iteration_number}...")
        
        # Duplicate the template blueprint
        new_blueprint_asset = asset_tools_helper.duplicate_asset(
            asset_name=new_blueprint_name,
            package_path=destination_folder_path,
            original_object=editor_asset_library.load_asset(template_blueprint_path)
        )
        
        # Verify the duplication was successful
        if not new_blueprint_asset:
            unreal.log_error(f"❌ Failed to duplicate blueprint from {template_blueprint_path} to {full_destination_path}")
            return None
            
        unreal.log(f"✅ Successfully created new PCG blueprint: {full_destination_path}")
        
        # Attempt to spawn the blueprint in the current level
        try:
            # Spawn the blueprint at the world origin with default rotation
            spawned_actor = unreal.EditorLevelLibrary.spawn_actor_from_object(
                new_blueprint_asset, 
                unreal.Vector(0, 0, 0),  # Position at origin
                unreal.Rotator(0, 0, 0)   # Default rotation
            )
            
            # Verify the actor was spawned successfully
            if spawned_actor:
                unreal.log(f"🎮 Placed new PCG actor '{new_blueprint_name}' in the current level at origin.")
            else:
                unreal.log_error(f"⚠️ Failed to place PCG actor in the level. You may need to add it manually.")
                
        except Exception as spawn_error:
            unreal.log_error(f"❌ Error while placing PCG actor in level: {spawn_error}")
            unreal.log_warning(f"⚠️ The blueprint was created successfully, but couldn't be placed in the level.")
            
        return new_blueprint_asset
        
    except Exception as duplication_error:
        unreal.log_error(f"❌ Error during blueprint creation: {duplication_error}")
        return None

# ======================================================================
# Main Execution
# ======================================================================

if __name__ == "__main__":
    # When run directly, create a PCG blueprint for iteration 0
    unreal.log("🚀 Starting PCG Graph creation process...")
    result = duplicate_and_rename_pcg_blueprint(iteration_number=0)
    
    if result:
        unreal.log("🎉 PCG Graph creation completed successfully!")
    else:
        unreal.log_error("❌ PCG Graph creation failed. Please check the log for details.")
