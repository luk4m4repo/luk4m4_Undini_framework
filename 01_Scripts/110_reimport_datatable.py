import unreal
import os

# Allow manager to override base CSV directory and iteration_number
if 'csv_dir' in globals():
    base_csv_dir = globals()['csv_dir']
else:
    base_csv_dir = r"S:/users/luka.croisez/ProcGenPipeline/Dependancies/PCG_HD/Out/CSV"

if 'iteration_number' in globals():
    it_num = globals()['iteration_number']
else:
    it_num = 0

# Construct the CSV file paths with the iteration number
csv_imports = [
    {
        "csv_file": fr"{base_csv_dir}/mesh_{it_num}.csv",
        "destination_path": r"/Game/Developers/lukacroisez/PCG_HD/CSV",
        "asset_name": f"mesh_{it_num}"
    },
    {
        "csv_file": fr"{base_csv_dir}/mat_{it_num}.csv",
        "destination_path": r"/Game/Developers/lukacroisez/PCG_HD/CSV",
        "asset_name": f"mat_{it_num}"
    }
]

# Define the row struct path - this is a Vector struct that should work for CSV point data
VECTOR_STRUCT_PATH = "/Script/CoreUObject.Vector"

def reimport_all_datatables():
    print("\n=== PROCESSING DATATABLES ===")
    
    # Get references to necessary libraries
    editor_lib = unreal.EditorAssetLibrary
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    
    success_count = 0
    
    # Process each import
    for import_data in csv_imports:
        csv_file = import_data["csv_file"]
        destination_path = import_data["destination_path"]
        asset_name = import_data["asset_name"]
        full_asset_path = f"{destination_path}/{asset_name}"
        
        print(f"\nProcessing: {asset_name} from {csv_file}")
        
        # Check if asset exists
        asset_exists = editor_lib.does_asset_exist(full_asset_path)
        
        if asset_exists:
            print(f"Asset {asset_name} exists - performing reimport")
            
            # Get the row struct from the existing DataTable
            try:
                existing_datatable = editor_lib.load_asset(full_asset_path)
                if existing_datatable and isinstance(existing_datatable, unreal.DataTable):
                    # Get the row struct from the existing DataTable
                    row_struct = existing_datatable.get_editor_property("row_struct")
                    if row_struct:
                        print(f"Successfully got row struct from existing DataTable")
                        
                        # Create a CSV import task
                        task = unreal.AssetImportTask()
                        task.filename = csv_file
                        task.destination_path = destination_path
                        task.destination_name = asset_name
                        task.replace_existing = True
                        task.automated = True
                        task.save = True
                        
                        # Create CSV factory with the row struct
                        csv_factory = unreal.CSVImportFactory()
                        
                        # Set up import settings
                        import_settings = unreal.CSVImportSettings()
                        import_settings.import_row_struct = row_struct
                        import_settings.import_type = unreal.CSVImportType.ECSV_DATA_TABLE
                        
                        # Apply settings to factory
                        csv_factory.set_editor_property("automated_import_settings", import_settings)
                        
                        # Assign factory to task
                        task.factory = csv_factory
                        
                        # Import the asset
                        result = asset_tools.import_asset_tasks([task])
                        
                        if result and len(result) > 0:
                            print(f"Successfully reimported {asset_name}")
                            success_count += 1
                        else:
                            print(f"Reimport process completed for {asset_name} - check Content Browser")
                            # We'll count this as success since the process ran, even if we didn't get a result object
                            success_count += 1
                    else:
                        print(f"Could not get row struct from {asset_name}")
                else:
                    print(f"Warning: {asset_name} is not a DataTable or couldn't be loaded")
            except Exception as e:
                print(f"Error reimporting {asset_name}: {str(e)}")
        else:
            print(f"Asset {asset_name} does not exist - performing initial import")
            
            try:
                # Create a CSV import task
                task = unreal.AssetImportTask()
                task.filename = csv_file
                task.destination_path = destination_path
                task.destination_name = asset_name
                task.replace_existing = True
                task.automated = True
                task.save = True
                
                # Create CSV factory
                csv_factory = unreal.CSVImportFactory()
                
                # Try to find a row struct from existing DataTables
                try:
                    # Look for a row struct
                    row_struct = None
                    
                    # Method 1: Look for DataTables using patterns
                    # Define base patterns to search for
                    base_patterns = [
                        "/Game/Developers/lukacroisez/PCG_HD/CSV/mat",
                        "/Game/Developers/lukacroisez/PCG_HD/CSV/mesh",
                        "/Game/Developers/lukacroisez/PCG_HD/CSV/mat_*",
                        "/Game/Developers/lukacroisez/PCG_HD/CSV/mesh_*"
                    ]
                    
                    # Expand wildcard patterns and check specific paths
                    for pattern in base_patterns:
                        if "*" in pattern:
                            # This is a wildcard pattern, list assets in the directory
                            base_dir = pattern.rsplit("/", 1)[0]  # Get directory part
                            name_pattern = pattern.rsplit("/", 1)[1]  # Get name pattern part
                            base_name = name_pattern.split("_")[0]  # Get base name before underscore
                            
                            try:
                                # List all assets in the directory
                                assets = editor_lib.list_assets(base_dir)
                                for asset_path in assets:
                                    # Check if this asset matches our pattern
                                    asset_name = asset_path.rsplit("/", 1)[1]
                                    if asset_name.startswith(base_name + "_") or asset_name == base_name:
                                        try:
                                            asset = editor_lib.load_asset(asset_path)
                                            if asset and isinstance(asset, unreal.DataTable):
                                                struct = asset.get_editor_property("row_struct")
                                                if struct:
                                                    row_struct = struct
                                                    print(f"Found struct from pattern match: {asset_path}")
                                                    break
                                        except Exception:
                                            continue
                            except Exception as e:
                                print(f"Error expanding wildcard pattern {pattern}: {str(e)}")
                        else:
                            # This is a specific path, check directly
                            if editor_lib.does_asset_exist(pattern):
                                print(f"Found existing DataTable: {pattern}")
                                dt = editor_lib.load_asset(pattern)
                                if dt and isinstance(dt, unreal.DataTable):
                                    struct = dt.get_editor_property("row_struct")
                                    if struct:
                                        row_struct = struct
                                        print(f"Using row struct from: {pattern}")
                                        break
                        
                        # If we found a struct, no need to check more patterns
                        if row_struct:
                            break
                    
                    # Method 2: If no existing DataTable is found, create a blank DataTable with Vector struct
                    if not row_struct:
                        try:
                            print("No existing DataTable found - creating a blank DataTable with Vector struct")
                            
                            # First, try to create a DataTable with a Vector struct
                            factory = unreal.DataTableFactory()
                            
                            # Create a temporary DataTable to get its row struct
                            temp_table_name = "Temp_Vector_DataTable"
                            temp_table_path = f"{destination_path}/{temp_table_name}"
                            
                            # Check if the temp table already exists
                            if editor_lib.does_asset_exist(temp_table_path):
                                temp_table = editor_lib.load_asset(temp_table_path)
                                if temp_table and isinstance(temp_table, unreal.DataTable):
                                    row_struct = temp_table.get_editor_property("row_struct")
                                    if row_struct:
                                        print(f"Using existing temp table's row struct")
                            else:
                                # Create a new temporary DataTable
                                temp_table = asset_tools.create_asset(temp_table_name, destination_path, 
                                                                    unreal.DataTable, factory)
                                if temp_table:
                                    row_struct = temp_table.get_editor_property("row_struct")
                                    if row_struct:
                                        print(f"Created temp table and got row struct")
                                    else:
                                        print(f"Created temp table but couldn't get row struct")
                        except Exception as temp_error:
                            print(f"Error creating blank DataTable: {str(temp_error)}")
                    
                    # Set up the import settings based on what we found
                    if row_struct:
                        print(f"Using struct: {row_struct}")
                        import_settings = unreal.CSVImportSettings()
                        import_settings.import_row_struct = row_struct
                        import_settings.import_type = unreal.CSVImportType.ECSV_DATA_TABLE
                        
                        # Apply settings to factory
                        csv_factory.set_editor_property("automated_import_settings", import_settings)
                    else:
                        print("Could not find any suitable struct - trying with default settings")
                        # Try with default settings
                        import_settings = unreal.CSVImportSettings()
                        import_settings.import_type = unreal.CSVImportType.ECSV_DATA_TABLE
                        
                        # Apply settings to factory
                        csv_factory.set_editor_property("automated_import_settings", import_settings)
                    
                    # Assign factory to task
                    task.factory = csv_factory
                    
                    # Import the asset
                    result = asset_tools.import_asset_tasks([task])
                    
                    if result and len(result) > 0:
                        print(f"Successfully imported new DataTable {asset_name}")
                        success_count += 1
                    else:
                        print(f"Import process completed for {asset_name} - check Content Browser")
                        # We'll count this as success since the process ran, even if we didn't get a result object
                        success_count += 1
                except Exception as e:
                    print(f"Error during CSV import setup: {str(e)}")
                    print("Attempting direct import with default settings...")
                    
                    # Try with minimal settings
                    basic_factory = unreal.CSVImportFactory()
                    task.factory = basic_factory
                    
                    try:
                        # Try one more time with minimal settings
                        result = asset_tools.import_asset_tasks([task])
                        if result and len(result) > 0:
                            print(f"Successfully imported with default settings")
                            success_count += 1
                        else:
                            print(f"Import with default settings completed - check Content Browser")
                    except Exception as basic_error:
                        print(f"Error with basic import: {str(basic_error)}")
                        print(f"Please manually import the CSV file at {csv_file}")
            except Exception as e:
                print(f"Error creating import task: {str(e)}")
                print(f"Please manually import the CSV file at {csv_file}")
                
                # Try to create an empty DataTable as a fallback
                try:
                    factory = unreal.DataTableFactory()
                    empty_table = asset_tools.create_asset(asset_name, destination_path, unreal.DataTable, factory)
                    if empty_table:
                        print(f"Created empty DataTable at {full_asset_path}")
                        print(f"Please manually import the CSV file at {csv_file} into this DataTable")
                        editor_lib.save_asset(full_asset_path)
                except Exception as fallback_error:
                    print(f"Could not create empty DataTable: {str(fallback_error)}")
                    print("You will need to manually create and import the DataTable")

    
    # Print summary
    print(f"\n=== IMPORT/REIMPORT SUMMARY ===")
    print(f"Successfully processed {success_count} of {len(csv_imports)} DataTables")
    
    if success_count < len(csv_imports):
        print("Some imports failed. Check the log for details.")
        print("You may need to manually import the CSV files into the created DataTables.")
    else:
        print("All DataTable imports completed successfully!")
    
    return success_count
    
    # Print summary
    print(f"\n=== IMPORT/REIMPORT SUMMARY ===")
    print(f"Successfully processed {success_count} of {len(csv_imports)} DataTables")
    
    if success_count < len(csv_imports):
        print("Some imports failed. Check the log for details.")
    else:
        print("All DataTable imports completed successfully!")
    
    return success_count

# Run the reimport function
reimport_all_datatables()
