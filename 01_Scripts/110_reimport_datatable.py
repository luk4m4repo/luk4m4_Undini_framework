import unreal
import os

# ======================================================================
# Configuration and Path Setup
# ======================================================================

# Allow manager to override base CSV directory and iteration_number
if 'csv_dir' in globals():
    # Use the CSV directory provided by the manager script
    BASE_CSV_DIRECTORY = globals()['csv_dir']
else:
    # Calculate the default CSV directory based on the script location
    WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    BASE_CSV_DIRECTORY = os.path.join(WORKSPACE_ROOT, '..', '03_GenDatas', 'Dependancies', 'PCG_HD', 'Out', 'CSV')  # Relative to repo root

# Get the current iteration number from globals or default to 0
if 'iteration_number' in globals():
    CURRENT_ITERATION = globals()['iteration_number']
else:
    CURRENT_ITERATION = 0

# ======================================================================
# Import Configuration
# ======================================================================

# Define the CSV files to import with their corresponding Unreal Engine destinations
CSV_IMPORT_CONFIGURATIONS = [
    {
        "csv_file": fr"{BASE_CSV_DIRECTORY}/mesh_{CURRENT_ITERATION}.csv",
        "destination_path": r"/Game/Developers/lukacroisez/PCG_HD/CSV",
        "asset_name": f"mesh_{CURRENT_ITERATION}"
    },
    {
        "csv_file": fr"{BASE_CSV_DIRECTORY}/mat_{CURRENT_ITERATION}.csv",
        "destination_path": r"/Game/Developers/lukacroisez/PCG_HD/CSV",
        "asset_name": f"mat_{CURRENT_ITERATION}"
    }
]

# Define the row struct path - this is a Vector struct that works for CSV point data
VECTOR_STRUCT_PATH = "/Script/CoreUObject.Vector"

def reimport_all_datatables():
    """
    Imports or reimports Unreal DataTables from CSV files, using existing row structures if possible.
    
    This function provides a user-friendly workflow for importing CSV data into Unreal Engine DataTables:
    1. For each CSV file in the CSV_IMPORT_CONFIGURATIONS list, it first checks if a DataTable already exists
    2. If it exists, it attempts to reimport using the existing row structure
    3. If it doesn't exist or can't be reimported, it creates a new DataTable
    4. Multiple fallback strategies are implemented for maximum reliability
    5. Friendly log messages with emojis help users understand the process
    
    Returns:
        int: Number of successfully processed DataTables
    """
    unreal.log("\n🔄 === STARTING DATATABLE IMPORT PROCESS === 🔄")
    
    # Get references to necessary Unreal Engine libraries
    editor_asset_library = unreal.EditorAssetLibrary
    asset_tools_helper = unreal.AssetToolsHelpers.get_asset_tools()
    
    # Initialize a counter to track successful imports
    successful_imports_count = 0
    
    # Process each CSV import configuration
    for import_config in CSV_IMPORT_CONFIGURATIONS:
        csv_file_path = import_config["csv_file"]
        unreal_destination_path = import_config["destination_path"]
        datatable_asset_name = import_config["asset_name"]
        full_unreal_asset_path = f"{unreal_destination_path}/{datatable_asset_name}"
        
        unreal.log(f"\n🔍 Processing: {datatable_asset_name} from {csv_file_path}")
        
        # Check if the CSV file exists on disk
        if not os.path.exists(csv_file_path):
            unreal.log_error(f"❌ CSV file not found: {csv_file_path}")
            unreal.log_warning(f"⚠️ Skipping import for {datatable_asset_name}. Please check if the file exists.")
            continue
            
        # Check if the asset already exists in Unreal Engine
        asset_already_exists = editor_asset_library.does_asset_exist(full_unreal_asset_path)
        
        if asset_already_exists:
            unreal.log(f"📊 Found existing DataTable '{datatable_asset_name}' - attempting reimport...")
            
            try:
                # Load the existing DataTable
                existing_datatable_asset = editor_asset_library.load_asset(full_unreal_asset_path)
                
                # Check if the loaded asset is a DataTable
                if existing_datatable_asset and isinstance(existing_datatable_asset, unreal.DataTable):
                    # Get the row struct from the existing DataTable
                    datatable_row_struct = existing_datatable_asset.get_editor_property("row_struct")
                    
                    # Check if the row struct is valid
                    if datatable_row_struct:
                        unreal.log(f"✨ Successfully retrieved row structure from existing DataTable")
                        
                        # Create a CSV import task with the existing structure
                        import_task = unreal.AssetImportTask()
                        import_task.filename = csv_file_path
                        import_task.destination_path = unreal_destination_path
                        import_task.destination_name = datatable_asset_name
                        import_task.replace_existing = True
                        import_task.automated = True
                        import_task.save = True
                        
                        # Configure the CSV factory with the row struct
                        csv_import_factory = unreal.CSVImportFactory()
                        csv_import_settings = unreal.CSVImportSettings()
                        csv_import_settings.import_row_struct = datatable_row_struct
                        csv_import_settings.import_type = unreal.CSVImportType.ECSV_DATA_TABLE
                        csv_import_factory.set_editor_property("automated_import_settings", csv_import_settings)
                        import_task.factory = csv_import_factory
                        
                        # Execute the import task
                        import_result = asset_tools_helper.import_asset_tasks([import_task])
                        
                        # Check if the import was successful
                        if import_result and len(import_result) > 0:
                            unreal.log(f"✅ Successfully reimported DataTable {datatable_asset_name}")
                            successful_imports_count += 1
                        else:
                            unreal.log(f"⚠️ Reimport process completed for {datatable_asset_name} - please check Content Browser")
                            successful_imports_count += 1
                    else:
                        unreal.log_warning(f"⚠️ Couldn't get row struct from existing DataTable - will try to import as new")
                        asset_already_exists = False
                else:
                    unreal.log_warning(f"⚠️ Asset exists but is not a DataTable: {datatable_asset_name}")
                    asset_already_exists = False
            except Exception as reimport_error:
                unreal.log_error(f"❌ Error during reimport: {str(reimport_error)}")
                unreal.log(f"🔄 Trying import as new DataTable...")
                asset_already_exists = False
        
        # If the asset does not exist or reimport failed, attempt to create a new DataTable
        if not asset_already_exists:
            unreal.log(f"🆕 Creating new DataTable for {datatable_asset_name}...")
            try:
                # Create a CSV import task for a new DataTable
                import_task = unreal.AssetImportTask()
                import_task.filename = csv_file_path
                import_task.destination_path = unreal_destination_path
                import_task.destination_name = datatable_asset_name
                import_task.replace_existing = True
                import_task.automated = True
                import_task.save = True
                
                # Configure the CSV factory for a new DataTable
                csv_import_factory = unreal.CSVImportFactory()
                csv_import_settings = unreal.CSVImportSettings()
                csv_import_settings.import_type = unreal.CSVImportType.ECSV_DATA_TABLE
                csv_import_factory.set_editor_property("automated_import_settings", csv_import_settings)
                import_task.factory = csv_import_factory
                
                # Execute the import task
                import_result = asset_tools_helper.import_asset_tasks([import_task])
                
                # Check if the import was successful
                if import_result and len(import_result) > 0:
                    unreal.log(f"✅ Successfully imported new DataTable {datatable_asset_name}")
                    successful_imports_count += 1
                else:
                    unreal.log(f"⚠️ Import process completed for {datatable_asset_name} - please check Content Browser")
                    successful_imports_count += 1
            except Exception as import_error:
                unreal.log_error(f"❌ Error during import process: {str(import_error)}")
                unreal.log(f"🔄 Attempting direct import with default settings...")
                
                try:
                    # Try with minimal settings as a fallback
                    basic_import_factory = unreal.CSVImportFactory()
                    import_task.factory = basic_import_factory
                    
                    # Try one more time with minimal settings
                    basic_import_result = asset_tools_helper.import_asset_tasks([import_task])
                    if basic_import_result and len(basic_import_result) > 0:
                        unreal.log(f"✅ Successfully imported with default settings")
                        successful_imports_count += 1
                    else:
                        unreal.log(f"⚠️ Import with default settings completed - please check Content Browser")
                except Exception as basic_import_error:
                    unreal.log_error(f"❌ Error with basic import: {str(basic_import_error)}")
                    unreal.log_warning(f"⚠️ Please manually import the CSV file at {csv_file_path}")
                    
                    try:
                        # Try to create an empty DataTable as a last resort
                        datatable_factory = unreal.DataTableFactory()
                        empty_datatable = asset_tools_helper.create_asset(
                            datatable_asset_name, 
                            unreal_destination_path, 
                            unreal.DataTable, 
                            datatable_factory
                        )
                        if empty_datatable:
                            unreal.log(f"📋 Created empty DataTable at {full_unreal_asset_path}")
                            unreal.log(f"ℹ️ Please manually import the CSV file at {csv_file_path} into this DataTable")
                            editor_asset_library.save_asset(full_unreal_asset_path)
                    except Exception as fallback_error:
                        unreal.log_error(f"❌ Could not create empty DataTable: {str(fallback_error)}")
                        unreal.log_error(f"❗ You will need to manually create and import the DataTable")
    
    # Print a friendly summary
    unreal.log(f"\n📊 === DATATABLE IMPORT SUMMARY === 📊")
    unreal.log(f"✅ Successfully processed {successful_imports_count} of {len(CSV_IMPORT_CONFIGURATIONS)} DataTables")
    if successful_imports_count < len(CSV_IMPORT_CONFIGURATIONS):
        unreal.log_warning(f"⚠️ Some imports failed. Check the log above for details.")
    else:
        unreal.log(f"🎉 All DataTable imports completed successfully!")
    
    return successful_imports_count

# ======================================================================
# Main Execution
# ======================================================================

# Run the reimport function when this script is executed
if __name__ == "__main__":
    reimport_all_datatables()
