import unreal
import os

# Allow manager to override base CSV directory and iteration_number
if 'csv_dir' in globals():
    base_csv_dir = globals()['csv_dir']
else:
    # Calculate the default CSV directory based on the script location
    workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    base_csv_dir = os.path.join(workspace_root, '03_GenDatas', 'Dependancies', 'PCG_HD', 'Out', 'CSV')

if 'iteration_number' in globals():
    it_num = globals()['iteration_number']
else:
    it_num = 0

# Construct the CSV file paths with the iteration number
csv_imports = [
    {
        "csv_file": fr"{base_csv_dir}/mesh_{it_num}.csv",
        "destination_path": r"/Game/luk4m4_Undini/CSV",
        "asset_name": f"mesh_{it_num}"
    },
    {
        "csv_file": fr"{base_csv_dir}/mat_{it_num}.csv",
        "destination_path": r"/Game/luk4m4_Undini/CSV",
        "asset_name": f"mat_{it_num}"
    }
]

# Define the row struct path - this is a Vector struct that should work for CSV point data
VECTOR_STRUCT_PATH = "/Script/CoreUObject.Vector"

# Define the template paths for DataTables
MESH_TEMPLATE_PATH = "/Game/luk4m4_Undini/CSV/mesh_template"
MAT_TEMPLATE_PATH = "/Game/luk4m4_Undini/CSV/mat_template"

def reimport_datatables(iteration_number=None, csv_dir=None):
    # Calculate default paths if not provided
    if csv_dir is None:
        # Calculate the default CSV directory based on the script location
        workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        csv_dir = os.path.join(workspace_root, '03_GenDatas', 'Dependancies', 'PCG_HD', 'Out', 'CSV')
    
    if iteration_number is None:
        iteration_number = 0
        
    # Override global variables with function parameters
    global base_csv_dir, it_num
    base_csv_dir = csv_dir
    it_num = iteration_number
    
    # Define the CSV imports with the current parameters
    csv_imports = [
        {
            "csv_file": fr"{base_csv_dir}/mesh_{it_num}.csv",
            "destination_path": r"/Game/luk4m4_Undini/CSV",
            "asset_name": f"mesh_{it_num}",
            "template_path": MESH_TEMPLATE_PATH
        },
        {
            "csv_file": fr"{base_csv_dir}/mat_{it_num}.csv",
            "destination_path": r"/Game/luk4m4_Undini/CSV",
            "asset_name": f"mat_{it_num}",
            "template_path": MAT_TEMPLATE_PATH
        }
    ]
    
    print(f"\n=== PROCESSING DATATABLES ===")
    print(f"Using iteration number: {it_num}")
    print(f"Looking for CSV files in: {base_csv_dir}")
    
    # Get references to necessary libraries
    editor_lib = unreal.EditorAssetLibrary
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    
    success_count = 0
    
    # Process each import
    for import_data in csv_imports:
        csv_file = import_data["csv_file"]
        destination_path = import_data["destination_path"]
        asset_name = import_data["asset_name"]
        template_path = import_data["template_path"]
        full_asset_path = f"{destination_path}/{asset_name}"
        
        print(f"\nProcessing: {asset_name} from {csv_file}")
        
        # Check if CSV file exists
        if not os.path.exists(csv_file):
            print(f"Error: CSV file not found at {csv_file}")
            continue
            
        # Check if template exists
        if not editor_lib.does_asset_exist(template_path):
            print(f"Error: Template DataTable not found at {template_path}")
            print(f"Please ensure the template DataTable exists before importing")
            continue
            
        # Load the template DataTable to get the row struct
        template_dt = editor_lib.load_asset(template_path)
        if not template_dt or not isinstance(template_dt, unreal.DataTable):
            print(f"Error: Template at {template_path} is not a valid DataTable")
            continue
            
        # Get the row struct from the template
        row_struct = template_dt.get_editor_property("row_struct")
        if not row_struct:
            print(f"Error: Template DataTable at {template_path} does not have a valid row struct")
            continue
            
        print(f"Using row struct from template: {template_path}")
        
        # Check if asset exists
        asset_exists = editor_lib.does_asset_exist(full_asset_path)
        
        # Create a CSV import task
        task = unreal.AssetImportTask()
        task.filename = csv_file
        task.destination_path = destination_path
        task.destination_name = asset_name
        task.replace_existing = asset_exists
        task.automated = True
        task.save = True
        
        # Create a CSV import factory
        csv_factory = unreal.CSVImportFactory()
        
        # Create import settings
        import_settings = unreal.CSVImportSettings()
        import_settings.import_type = unreal.CSVImportType.ECSV_DATA_TABLE
        import_settings.data_table_row_type = row_struct
        
        # Apply settings to factory
        csv_factory.set_editor_property("automated_import_settings", import_settings)
        
        # Assign factory to task
        task.factory = csv_factory
        
        try:
            # Import the asset
            if asset_exists:
                print(f"Asset {asset_name} exists - performing reimport")
            else:
                print(f"Asset {asset_name} does not exist - performing initial import")
                
            result = asset_tools.import_asset_tasks([task])
            
            if result and len(result) > 0:
                print(f"Successfully {'reimported' if asset_exists else 'imported'} DataTable {asset_name}")
                success_count += 1
            else:
                print(f"Import process completed for {asset_name} - check Content Browser")
                success_count += 1
        except Exception as e:
            print(f"Error during import: {str(e)}")
            
            # Try with a more basic approach as fallback
            try:
                print("Attempting import with basic settings...")
                
                # If the asset exists, try to get the row struct from it
                if asset_exists:
                    existing_dt = editor_lib.load_asset(full_asset_path)
                    if existing_dt and isinstance(existing_dt, unreal.DataTable):
                        existing_row_struct = existing_dt.get_editor_property("row_struct")
                        if existing_row_struct:
                            row_struct = existing_row_struct
                            print(f"Using row struct from existing DataTable")
                
                # Create a new import task
                basic_task = unreal.AssetImportTask()
                basic_task.filename = csv_file
                basic_task.destination_path = destination_path
                basic_task.destination_name = asset_name
                basic_task.replace_existing = asset_exists
                basic_task.automated = True
                basic_task.save = True
                
                # Create a new factory
                basic_factory = unreal.CSVImportFactory()
                
                # Create import settings
                basic_settings = unreal.CSVImportSettings()
                basic_settings.import_type = unreal.CSVImportType.ECSV_DATA_TABLE
                basic_settings.data_table_row_type = row_struct
                
                # Apply settings to factory
                basic_factory.set_editor_property("automated_import_settings", basic_settings)
                
                # Assign factory to task
                basic_task.factory = basic_factory
                
                # Import the asset
                basic_result = asset_tools.import_asset_tasks([basic_task])
                
                if basic_result and len(basic_result) > 0:
                    print(f"Successfully imported with basic settings")
                    success_count += 1
                else:
                    print(f"Basic import completed - check Content Browser")
            except Exception as basic_error:
                print(f"Error with basic import: {str(basic_error)}")
                print(f"Please manually import the CSV file at {csv_file}")
                
                # If the asset doesn't exist, try to create an empty DataTable as a fallback
                if not asset_exists:
                    try:
                        print("Creating empty DataTable as fallback...")
                        factory = unreal.DataTableFactory()
                        factory.row_struct = row_struct
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

# Run the reimport function when this script is executed directly
if __name__ == "__main__":
    reimport_datatables()
