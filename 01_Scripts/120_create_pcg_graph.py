import unreal

# ======================================================================
# PCG Graph Blueprint Creation Script
# ======================================================================
#
# This is the fifth step in the Undini procedural generation pipeline:
# 1. Export splines from Unreal Engine (000_export_splines_as_json.py)
# 2. Export GenZone meshes from UE (010_export_gz_to_mod.py)
# 3. Process inputs in Houdini to generate building data (100_headless_topnet_PCGHD.py)
# 4. Import CSV files back into Unreal Engine as DataTables (110_reimport_datatable.py)
# 5. Create PCG graphs in Unreal Engine using the imported data (this script)
#
# This script creates a new PCG (Procedural Content Generation) graph for the
# current iteration by duplicating a template blueprint, renaming it with the
# iteration number, and placing an instance in the current level.
#
# The PCG graph uses the DataTables imported in the previous step to generate
# procedural buildings in the level based on the splines and GenZone meshes.

def create_pcg_graph(iteration_number=None, template_bp_path=None):
    """
    Entry point function called by the manager script
    
    This function creates a new PCG graph for the current iteration by duplicating
    a template blueprint and placing it in the level. It serves as a wrapper around
    the implementation function, handling default values and parameter passing.
    
    Args:
        iteration_number (int, optional): The iteration number to use for naming. Defaults to 0.
        template_bp_path (str, optional): Path to the template blueprint. If provided, overrides the default.
        
    Returns:
        unreal.Blueprint: The newly created blueprint asset, or None if the operation failed
    """
    unreal.log("🔹 Starting PCG Graph creation process...")
    
    # Set default values if not provided
    if iteration_number is None:
        iteration_number = 0
        unreal.log(f"ℹ️ No iteration number provided, using default: {iteration_number}")
    else:
        unreal.log(f"ℹ️ Using iteration number: {iteration_number}")
    
    # Call the implementation function with the appropriate parameters
    if template_bp_path is not None:
        unreal.log(f"ℹ️ Using custom template blueprint path: {template_bp_path}")
        return duplicate_and_rename_pcg_blueprint(iteration_number, template_bp_path)
    else:
        unreal.log(f"ℹ️ Using default template blueprint path")
        return duplicate_and_rename_pcg_blueprint(iteration_number)

def duplicate_and_rename_pcg_blueprint(iteration_number=0, template_blueprint_path=None):
    """
    Creates a new Procedural Content Generation (PCG) graph for the current iteration.
    
    This function performs the following operations:
    1. Duplicates the template PCG blueprint (BP_PCG_HD_TEMPLATE)
    2. Renames it with the current iteration number (BPi_PCG_HD_{iteration_number})
    3. Places the new blueprint in the designated folder
    4. Spawns an instance of the blueprint in the current level at the origin
    
    The PCG graph will use the DataTables imported in the previous step (mesh_{iteration_number}.csv
    and mat_{iteration_number}.csv) to generate procedural buildings in the level.
    
    Args:
        iteration_number (int): The current iteration number to append to the blueprint name
        template_blueprint_path (str, optional): Path to the template blueprint. If None, uses default.
        
    Returns:
        unreal.Blueprint: The newly created blueprint asset, or None if the operation failed
    """
    # Define source and destination paths for the blueprint
    if template_blueprint_path is None:
        # Use the default template path if none was provided
        template_blueprint_path = "/Game/luk4m4_Undini/BP/BP_PCG_HD_TEMPLATE.BP_PCG_HD_TEMPLATE"
    
    # Define the destination folder and naming convention
    destination_folder_path = "/Game/luk4m4_Undini/BP/BP_PCG_HD_inst"
    new_blueprint_name = f"BPi_PCG_HD_{iteration_number}"
    full_destination_path = f"{destination_folder_path}/{new_blueprint_name}"
    
    unreal.log(f"\n📚 Blueprint creation details:")
    unreal.log(f"  • Template: {template_blueprint_path}")
    unreal.log(f"  • Destination: {destination_folder_path}")
    unreal.log(f"  • New name: {new_blueprint_name}")
    unreal.log(f"  • Full path: {full_destination_path}")


    # Get the Unreal Engine asset management utilities we need
    unreal.log("\n🔍 Getting Unreal Engine asset management utilities...")
    asset_tools_helper = unreal.AssetToolsHelpers.get_asset_tools()
    editor_asset_library = unreal.EditorAssetLibrary

    # First, let's make sure the template blueprint exists
    unreal.log("\n🔍 Checking if template blueprint exists...")
    if not editor_asset_library.does_asset_exist(template_blueprint_path):
        unreal.log_error(f"❌ Template blueprint not found: {template_blueprint_path}")
        unreal.log_warning(f"⚠️ Please ensure the PCG template blueprint exists before running this script.")
        unreal.log_warning(f"   Check the path in the manager script (UE_PCG_TEMPLATE_BP_PATH variable).")
        return None
    else:
        unreal.log(f"✅ Template blueprint found at: {template_blueprint_path}")
    
    # Make sure the destination folder exists
    unreal.log("\n🔍 Checking if destination folder exists...")
    if not editor_asset_library.does_directory_exist(destination_folder_path):
        unreal.log(f"⚠️ Destination folder does not exist: {destination_folder_path}")
        unreal.log(f"   Attempting to create the folder...")
        try:
            editor_asset_library.make_directory(destination_folder_path)
            unreal.log(f"✅ Successfully created destination folder")
        except Exception as folder_error:
            unreal.log_error(f"❌ Failed to create destination folder: {folder_error}")
            unreal.log_warning(f"   Please create the folder manually and try again.")
            return None
    else:
        unreal.log(f"✅ Destination folder exists")
    
    # Check if the blueprint with this name already exists
    unreal.log("\n🔍 Checking if blueprint already exists...")
    if editor_asset_library.does_asset_exist(full_destination_path):
        unreal.log(f"⚠️ A blueprint with the name '{new_blueprint_name}' already exists")
        unreal.log(f"   Will attempt to replace it...")
        
        # Try to delete the existing blueprint
        try:
            editor_asset_library.delete_asset(full_destination_path)
            unreal.log(f"✅ Successfully deleted existing blueprint")
        except Exception as delete_error:
            unreal.log_error(f"❌ Failed to delete existing blueprint: {delete_error}")
            unreal.log_warning(f"   Will attempt to proceed anyway, but this may cause issues.")
    
    # Now let's duplicate the blueprint asset
    unreal.log("\n🌟 Creating new PCG blueprint...")
    try:
        # Load the template blueprint asset
        template_asset = editor_asset_library.load_asset(template_blueprint_path)
        if not template_asset:
            unreal.log_error(f"❌ Failed to load template blueprint: {template_blueprint_path}")
            return None
        
        # Duplicate the template blueprint
        unreal.log(f"Duplicating template blueprint...")
        new_blueprint_asset = asset_tools_helper.duplicate_asset(
            asset_name=new_blueprint_name,
            package_path=destination_folder_path,
            original_object=template_asset
        )
        
        # Verify the duplication was successful
        if not new_blueprint_asset:
            unreal.log_error(f"❌ Failed to duplicate blueprint from {template_blueprint_path} to {full_destination_path}")
            return None
            
        unreal.log(f"✅ Successfully created new PCG blueprint: {full_destination_path}")
        
        # Now let's place the blueprint in the current level
        unreal.log("\n🌎 Placing PCG actor in the current level...")
        try:
            # First check if we have an open level
            if not unreal.EditorLevelLibrary.get_editor_world():
                unreal.log_warning(f"⚠️ No level is currently open. Cannot place actor.")
                unreal.log_warning(f"   Please open a level and add the PCG actor manually.")
                return new_blueprint_asset
            
            # Spawn the blueprint at the world origin with default rotation
            unreal.log(f"Spawning actor at world origin (0,0,0)...")
            spawned_actor = unreal.EditorLevelLibrary.spawn_actor_from_object(
                new_blueprint_asset, 
                unreal.Vector(0, 0, 0),  # Position at origin
                unreal.Rotator(0, 0, 0)   # Default rotation
            )
            
            # Verify the actor was spawned successfully
            if spawned_actor:
                unreal.log(f"✅ Successfully placed new PCG actor '{new_blueprint_name}' in the current level.")
                unreal.log(f"   The actor is positioned at the world origin (0,0,0).")
                unreal.log(f"   You may need to move it to the desired location.")
            else:
                unreal.log_error(f"⚠️ Failed to place PCG actor in the level. You may need to add it manually.")
                unreal.log_warning(f"   To add it manually, drag the blueprint from the Content Browser to the level.")
                
        except Exception as spawn_error:
            unreal.log_error(f"❌ Error while placing PCG actor in level: {spawn_error}")
            unreal.log_warning(f"⚠️ The blueprint was created successfully, but couldn't be placed in the level.")
            unreal.log_warning(f"   To add it manually, drag the blueprint from the Content Browser to the level.")
        
        # Save all assets to ensure the changes are persisted
        unreal.log("\n💾 Saving assets...")
        try:
            unreal.EditorAssetLibrary.save_loaded_assets([new_blueprint_asset], True)
            unreal.log(f"✅ Successfully saved all assets")
        except Exception as save_error:
            unreal.log_warning(f"⚠️ Failed to save assets: {save_error}")
            unreal.log_warning(f"   You may need to save manually.")
            
        return new_blueprint_asset
        
    except Exception as duplication_error:
        unreal.log_error(f"❌ Error during blueprint creation: {duplication_error}")
        import traceback
        unreal.log_error(f"   Error details: {traceback.format_exc()}")
        return None

# ======================================================================
# Main Execution
# ======================================================================

if __name__ == "__main__":
    # When run directly (not imported by the manager), create a PCG blueprint for iteration 0
    unreal.log("🚀 Starting PCG Graph creation process...")
    unreal.log("This is the fifth step in the Undini procedural generation pipeline.")
    unreal.log("It creates a PCG graph that will use the DataTables imported in the previous step.")
    
    # You can modify these parameters for testing
    iteration_number = 0
    template_bp_path = None  # Use default
    
    # Call the main function
    unreal.log(f"\nCreating PCG graph for iteration {iteration_number}...")
    result = create_pcg_graph(iteration_number=iteration_number, template_bp_path=template_bp_path)
    
    # Report the results
    if result:
        unreal.log(f"\n🎉 PCG Graph creation completed successfully!")
        unreal.log(f"Created blueprint: {result.get_path_name()}")
        unreal.log(f"The next step is to use this PCG graph to generate buildings in your level.")
    else:
        unreal.log_error(f"\n❌ PCG Graph creation failed. Please check the log above for details.")
        unreal.log_error(f"Common issues include:")
        unreal.log_error(f"  • Missing template blueprint")
        unreal.log_error(f"  • Incorrect template path")
        unreal.log_error(f"  • Permission issues when creating assets")
    
    # Visual separator for the end of the script
    unreal.log("\n" + "-" * 80)
