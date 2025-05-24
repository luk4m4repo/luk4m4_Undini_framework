# luk4m4_Undini_framework

![Houdini](https://img.shields.io/badge/Houdini-20.0+-orange) ![Unreal Engine](https://img.shields.io/badge/Unreal%20Engine-5.0+-blue) ![Python](https://img.shields.io/badge/Python-3.7+-green)

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

3. Copy the Unreal Engine widget blueprint from the `02_uasset` directory to your Unreal Engine project
   - The widget blueprint provides a user-friendly interface to run the pipeline directly within Unreal Engine
   - Place it in your project's Content folder (e.g., `/Game/YourProject/UI/`)

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

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
