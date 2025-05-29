# Undini Pipeline Framework

![Houdini](https://img.shields.io/badge/Houdini-20.0+-orange) ![Unreal Engine](https://img.shields.io/badge/Unreal%20Engine-5.3.2-blue) ![Python](https://img.shields.io/badge/Python-3.7+-green) ![Beta](https://img.shields.io/badge/Version-Beta%20v0.1-red)

A practical toolkit for automating procedural world-building between Unreal Engine 5 and Houdini. Run the whole pipeline or just the bits you need.

### IMPORTANT: This framework assumes that you already have your Houdini generation file(s), that you have your elements to instantiate in PCG, and that you have already used the PCG procedural generation tools in Unreal Engine. If this is not the case, I suggest you read the detailed documentation here : `luk4m4_Undini_doc_complete.md`.

---

## Pipeline Overview

**Choose ONE starting method:**
- **A. Spline Workflow:**
  → `000_export_splines_as_json.py` (Export splines from UE to JSON)
- **B. GenZone Mesh Workflow:**
  → `010_export_gz_to_mod.py` (Export GenZone meshes from UE to FBX)

➡️ **After A or B:**
**→ Make sure the widget checkbox matches your chosen method (A or B)!**

**Then continue:**
- `100_headless_topnet_PCGHD.py` (Houdini: generate buildings)
- `110_reimport_datatable.py` (Import CSV as UE datatables)
- `120_create_pcg_graph.py` (Duplicate PCG Blueprint, spawn in level)

**Alternate branch (after A or B):**
- `120_create_pcg_graph.py`
  → `200_headless_topnet_SWR.py` (Houdini: sidewalks/roads)
  → `210_reimport_SM.py` (Import static meshes)
  → `220_add_SM_to_lvl.py` (Add meshes to level)

---

---

## Quickstart

### 1. Requirements
- Unreal Engine **5.3.2** or later
- Houdini **20.0.653** or later
- Python **3.7+**

### 2. Setup
```bash
git clone https://github.com/yourusername/luk4m4_Undini_framework.git
```
- Copy the assets from `02_uasset/` into your Unreal project as described below.

### 3. Asset Placement
- **Widget Blueprint** → `/Game/luk4m4_Undini/UI/`
- **CSV/DataTable Templates** → `/Game/luk4m4_Undini/CSV/`
- **PCG Blueprint Template** → `/Game/luk4m4_Undini/BP/`
- **Spline Blueprint** → `/Game/luk4m4_Undini/BP/` (do **not** rename)

---

## Main Scripts (in pipeline order)

| Step | Script | What it Does |
|------|-------------------------------|------------------------------------------------------|
| 1    | `000_export_splines_as_json.py` | Export splines from UE to JSON                      |
| 2    | `010_export_gz_to_mod.py`       | Export GenZone meshes from UE to FBX                |
| 3    | `100_headless_topnet_PCGHD.py`  | Run Houdini (headless) to generate building data    |
| 4    | `110_reimport_datatable.py`     | Import CSVs as UE DataTables                        |
| 5    | `120_create_pcg_graph.py`       | Duplicate PCG Blueprint, spawn in level             |
| 6    | `200_headless_topnet_SWR.py`    | Houdini (headless) for sidewalks & roads            |
| 7    | `210_reimport_SM.py`            | Import/reimport static meshes from FBX              |
| 8    | `220_add_SM_to_lvl.py`          | Add sidewalk/road meshes to the level               |

- `999_UE_manager.py`: Orchestrates the whole show. Run all steps or just one.

---

## 📂 File & Asset Flow

```plaintext
[Splines / Meshes in UE]
   │
   ├─▶ (JSON/FBX export)
   │
[Houdini: PCG, sidewalks, roads]
   │
   ├─▶ (CSV/FBX output)
   │
[Reimport to Unreal]
   │
   ├─▶ (Add to level, organize)
```

- All files are named by iteration (e.g., `mesh_001.csv`, `road_001.fbx`).
- Stick to the naming conventions—automation relies on it.

---

## How to Use

### The Widget (Recommended)
1. Open your Unreal project.
2. Find the Undini Framework widget in your Content Browser.
3. Set your Houdini path, iteration number, and any other needed settings.
4. Click buttons to run steps—watch the log for progress and errors.

### Python Power Users
- Import and run scripts directly, or use `999_UE_manager.py` to automate the lot.
- Each script logs its actions (with emoji for clarity!).

---

## Principles
- **Automate everything.**
- **Name things right.**
- **Keep scripts modular.**
- **Minimal manual fiddling.**
- **Logs and folders keep you sane.**

---

## Using Your Own Houdini HIP Files

**Note:** The Houdini `.hip` files required for this pipeline are NOT included in this repository. This is due to licensing, size, or project-specific reasons.

### How to Use Your Own Houdini Files

You can use your own Houdini `.hip` files for city, sidewalk, and road generation. **Templates** are provided in `../04_Houdini/` with all required nodes and parameters—start here if unsure!

**Where to put HIP files:**
- Place your `.hip` files in `./04_Houdini/` (or provide the full path in the widget/script).

**For City (PCGHD):**
- A TOP network (`/obj/geo1/topnet`)
- `/obj/geo1/pcg_export1` with `file_mesh` and `file_mat` parameters
- `/obj/geo1/python_import_splines_from_json` with `iteration_number` and `base_path`
- `/obj/geo1/switch_bool` to switch input type
- Outputs: mesh/material CSVs

**For Sidewalks/Roads (SWR):**
- A TOP network (`/obj/geo1/topnet`)
- `/obj/geo1/rop_fbx_road` and `/obj/geo1/rop_fbx_sidewalks` with `sopoutput`
- `/obj/geo1/python_import_splines_from_json` with `iteration_number` and `base_path`
- `/obj/geo1/switch_bool` to control network
- Outputs: road/sidewalk FBXs

**How to reference:**
- In the widget or script, set the HIP file path before running the Houdini step.

**Troubleshooting:**
- Errors about missing nodes/parameters? Compare your HIP to the template and this doc.
- Check logs for the exact names the pipeline is trying to set.

1. **Create or obtain your own Houdini `.hip` files** for procedural generation (buildings, sidewalks, roads, etc.).
2. **Place your HIP files** wherever you like—ideally in a dedicated folder in your project (e.g., `./04_Houdini/` or outside the repo).
3. **Reference your HIP files in the pipeline:**
   - The relevant scripts (`100_headless_topnet_PCGHD.py`, `200_headless_topnet_SWR.py`) accept the HIP file path as a command-line argument or via the pipeline config.
   - In the widget or script call, specify your `.hip` file path using the appropriate parameter or field.
   - Example (Python):
     ```python
     run_houdini_headless(iteration_number=1, hip_file="/path/to/your_file.hip", ...)
     ```
   - Example (Widget):
     - Set the HIP file path in the widget’s configuration field before running the relevant step.

### What does the pipeline expect from your HIP files?
- **Inputs:**
  - The HIP file should expect inputs (FBX, JSON, etc.) matching the outputs of the Unreal export scripts.
  - Node names and file paths should match those referenced in the pipeline scripts/config.
- **Outputs:**
  - The HIP file should output CSV or FBX files as expected by the next pipeline step (see docs for details).
- **Node Structure:**
  - The pipeline assumes certain TOP nodes or output nodes exist in your HIP file (e.g., `/obj/topnet1`).
  - If you use different node names, update the pipeline config or script arguments accordingly.

### Tips
- Start from the example config/scripts and adapt paths/names to your setup.
- If your HIP file structure is different, you may need to adjust the pipeline scripts or their arguments.
- Check the script and widget logs for errors about missing nodes or files—these usually indicate a mismatch between your HIP file and the expected structure.

---

## Getting Started

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

## Pipeline Workflow

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

## Release Notes

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
- UE embedded plugin
- Support for more diverse procedural generation workflows
