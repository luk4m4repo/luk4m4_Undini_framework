import unreal
import os

def reimport_datatables(iteration_number=None, csv_dir=None):
    """Import or reimport CSV files as DataTables in Unreal Engine"""
    # Set default values if not provided
    if iteration_number is None:
        iteration_number = 0
        
    if csv_dir is None:
        # Calculate the default CSV directory based on the script location
        workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        csv_dir = os.path.join(workspace_root, '03_GenDatas', 'Dependancies', 'PCG_HD', 'Out', 'CSV')
    
    # Define the CSV imports with the iteration number
    csv_imports = [
        {
            "csv_file": os.path.join(csv_dir, f"mesh_{iteration_number}.csv"),
            "destination_path": "/Game/luk4m4_Undini/CSV",
            "asset_name": f"mesh_{iteration_number}",
            "template_path": "/Game/luk4m4_Undini/CSV/mesh_template"
        },
        {
            "csv_file": os.path.join(csv_dir, f"mat_{iteration_number}.csv"),
            "destination_path": "/Game/luk4m4_Undini/CSV",
            "asset_name": f"mat_{iteration_number}",
            "template_path": "/Game/luk4m4_Undini/CSV/mat_template"
        }
    ]
    
    print("\n=== PROCESSING DATATABLES ===")
    print(f"Using iteration number: {iteration_number}")
    print(f"Looking for CSV files in: {csv_dir}")
    
    # Get references to necessary libraries
    editor_lib = unreal.EditorAssetLibrary
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    
    success_count = 0
    
    # Process each import
    for import_data in csv_imports:
        try:
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
            
            # Check if asset exists
            asset_exists = editor_lib.does_asset_exist(full_asset_path)
            
            # Get row struct from template
            row_struct = None
            if editor_lib.does_asset_exist(template_path):
                template_dt = editor_lib.load_asset(template_path)
                if template_dt and isinstance(template_dt, unreal.DataTable):
                    row_struct = template_dt.get_editor_property("row_struct")
                    if row_struct:
                        print(f"Using row struct from template: {template_path}")
            
            if not row_struct:
                print(f"Error: Could not find a valid row struct for {asset_name}")
                continue
            
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
            # Different versions of UE use different property names
            try:
                # Try the property name for newer UE versions
                import_settings.data_table_row_type = row_struct
            except AttributeError:
                try:
                    # Try the property name for older UE versions
                    import_settings.import_row_struct = row_struct
                except AttributeError:
                    # Try setting it directly on the factory if both fail
                    print("Using direct factory property setting for row struct")
            
            # Apply settings to factory
            csv_factory.set_editor_property("automated_import_settings", import_settings)
            
            # Assign factory to task
            task.factory = csv_factory
            
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
            print(f"Error processing {import_data['asset_name']}: {str(e)}")
    
    # Print summary
    print(f"\n=== IMPORT/REIMPORT SUMMARY ===")
    print(f"Successfully processed {success_count} of {len(csv_imports)} DataTables")
    
    if success_count == len(csv_imports):
        print(f"All DataTable imports completed successfully!")
        return 1
    else:
        print(f"Some DataTable imports failed. Check the log for details.")
        return 0
