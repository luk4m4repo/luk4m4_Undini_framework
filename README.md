# luk4m4_Undini_framework

![Houdini](https://img.shields.io/badge/Houdini-20.0+-orange) ![Unreal Engine](https://img.shields.io/badge/Unreal%20Engine-5.0+-blue) ![Python](https://img.shields.io/badge/Python-3.7+-green) ![Version](https://img.shields.io/badge/Version-Beta%20v0.1-red)

A comprehensive framework that simplifies the procedural generation pipeline between Houdini and Unreal Engine 5. This framework automates the exchange of data between the two applications, streamlining the creation of procedural environments.

## 🌟 Features

- **Automated Pipeline**: Run the entire procedural generation workflow with a single command
- **Modular Architecture**: Use individual components or the complete pipeline
- **Spline-Based Generation**: Export splines from UE5 to drive procedural generation in Houdini
- **Headless Houdini Processing**: Run Houdini operations without the GUI for faster processing
- **Seamless Reimporting**: Automatically reimport generated assets back into Unreal Engine
- **Iteration Support**: Easily manage multiple iterations of your procedural content

## 📋 Requirements

- Unreal Engine 5.0 or later
- Houdini 20.0 or later
- Python 3.7 or later

## 🗂️ Repository Structure

```
luk4m4_Undini_framework/
├── 01_Scripts/                    # Python scripts for the pipeline
│   ├── 000_export_splines_as_json.py       # Export splines from UE to JSON
│   ├── 010_export_gz_to_mod.py             # Export GenZone meshes to FBX
│   ├── 100_headless_topnet_PCGHD.py        # Run Houdini PCG generation headless
│   ├── 110_reimport_datatable.py           # Reimport CSV data into UE DataTables
│   ├── 120_create_pcg_graph.py             # Create PCG graph in UE
│   ├── 200_headless_topnet_SWR.py          # Generate sidewalks & roads in Houdini
│   ├── 210_reimport_SM.py                  # Reimport static meshes into UE
│   ├── 220_add_SM_to_lvl.py                # Add static meshes to UE level
│   ├── 991_HOUDINI_import_splines_from_json.py  # Import splines in Houdini
│   └── 999_UE_manager.py                   # Main pipeline manager
└── README.md                      # Documentation
```

## 🚀 Getting Started

### Setup

1. Clone this repository to your local machine using Git:
   ```bash
   git clone https://github.com/yourusername/luk4m4_Undini_framework.git
   ```

2. Make sure Unreal Engine 5.0+ and Houdini 20.0+ are properly installed on your system

3. Copy the required Unreal Engine assets from the `02_uasset` directory to your Unreal Engine project:

   a. **Widget Blueprint**:
   - Copy the widget blueprint to your project's Content folder (e.g., `/Game/YourProject/UI/`)
   - This provides a user-friendly interface to run the pipeline directly within Unreal Engine

   b. **Template Files**:
   - Copy `mat_template.uasset` and `mesh_template.uasset` to `/Game/luk4m4_Undini/CSV/`
   - These templates are required for the CSV DataTables to work correctly
   - **Important**: If you change the CSV path in the configuration, you must move these template files to the new location

   c. **PCG Blueprint Template**:
   - Copy `BP_PCG_HD_TEMPLATE.uasset` to `/Game/luk4m4_Undini/BP/`
   - This template is required for creating PCG graph instances

   d. **Spline Blueprint**:
   - Copy `BP_CityKit_spline.uasset` to `/Game/luk4m4_Undini/BP/`
   - **Important**: Do not rename this blueprint, as its name is used to identify splines for export
   - When placed in the level, the name and asset number of each instance drives the export of splines to Houdini

### Using the Pipeline

#### Using the Widget Blueprint (Recommended)

1. Open your Unreal Engine project

2. Find and open the Undini Framework widget blueprint you copied earlier

3. Configure the necessary parameters in the widget's text fields:
   - Houdini installation path (if not using the default)
   - Iteration number for your procedural generation
   - Any other required paths or settings

4. Use the buttons in the widget to run individual steps or the complete pipeline:
   - Export Splines to JSON
   - Run Houdini PCG Generation
   - Reimport DataTables
   - Create PCG Graph
   - And more...

5. Monitor the progress through the widget's output log

#### Advanced: Direct Python Access

For advanced users who prefer direct script access, you can also run the pipeline through Python:

```python
# Import the manager script
exec(open(r"path/to/luk4m4_Undini_framework/01_Scripts/999_UE_manager.py").read())

# Run the full pipeline with a specific iteration number
run_full_pipeline(1)

# Or run individual steps
call_export_splines_to_json(1)  # Export splines
run_houdini_pcg_generation(1)   # Generate PCG data
```

## 🔄 Pipeline Workflow

1. **Export Splines**: Exports spline components from UE to JSON
2. **Export GenZone Meshes**: Exports GenZone meshes from UE to FBX
3. **Houdini PCG Generation**: Processes meshes in Houdini to generate PCG data
4. **Reimport CSV Data**: Imports CSV data back into UE DataTables
5. **Create PCG Graph**: Creates a PCG graph blueprint in UE
6. **Houdini Sidewalks & Roads**: Generates sidewalks and roads in Houdini
7. **Reimport Static Meshes**: Imports FBX files back into UE
8. **Add to Level**: Places sidewalks and roads in the UE level

## 📝 Notes

- Each script can be run independently or as part of the pipeline
- The iteration number is used to track different versions of your procedural content
- Paths are now relative to the repository root for better portability
- Error handling is included to make the process more robust

## ⚙️ Customizing Unreal Engine Paths

The framework uses a centralized configuration system in the `999_UE_manager.py` script. You can customize the Unreal Engine paths to match your project structure:

```python
# Base content path - change this to match your project structure
UE_BASE_PATH = "/Game/Developers/lukacroisez"

# PCG DataTable paths
UE_PCG_CSV_PATH = f"{UE_BASE_PATH}/PCG_HD/CSV"

# PCG Blueprint paths
UE_PCG_TEMPLATE_BP_PATH = f"{UE_BASE_PATH}/PCG_HD/BP/BP_PCG_HD_TEMPLATE.BP_PCG_HD_TEMPLATE"
UE_PCG_INSTANCE_BP_PATH = f"{UE_BASE_PATH}/PCG_HD/BP/BP_PCG_HD_inst"

# Static Mesh paths
UE_SIDEWALKS_PATH = f"{UE_BASE_PATH}/Assets/Sidewalks"
UE_ROADS_PATH = f"{UE_BASE_PATH}/Assets/Road"
```

Simply modify the `UE_BASE_PATH` to match your project's content structure, or adjust individual paths as needed. After changing these paths, make sure to copy the template files to the corresponding locations in your Unreal Engine project.

## 📝 Release Notes

### Beta v0.1 (Current)

**Status**: This framework is currently in beta. Expect potential bugs and ongoing improvements.

**Key Features**:
- Complete Houdini-UE5 procedural generation pipeline with widget UI integration
- Spline-based city generation with automatic PCG graph creation
- Sidewalks and roads generation with automatic placement in UE level
- Centralized configuration system for easy path customization
- Improved error handling and user feedback throughout the pipeline
- Relative path support for better portability between projects

**Known Limitations**:
- Templates must be manually copied to the correct UE directories
- Limited to the specific procedural generation workflow demonstrated
- Requires specific Houdini .hip files (included in the framework)

**Upcoming Features**:
- Improved template management and automatic asset copying
- Support for more diverse procedural generation workflows
- Enhanced documentation and examples

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
