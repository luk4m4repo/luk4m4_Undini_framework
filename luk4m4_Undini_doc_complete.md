# 🚦 Undini Pipeline: Complete Documentation

## 🗺️ Pipeline Map

```mermaid
flowchart LR
    A[000_export_splines_as_json.py\n:splines to JSON] --> B[010_export_gz_to_mod.py\n:GenZone meshes to FBX]
    B --> C[100_headless_topnet_PCGHD.py\n:Houdini PCG (buildings)]
    C --> D[110_reimport_datatable.py\n:CSV to UE datatables]
    D --> E[120_create_pcg_graph.py\n:PCG graph Blueprint]
    E --> F[200_headless_topnet_SWR.py\n:Houdini (sidewalks/roads)]
    F --> G[210_reimport_SM.py\n:FBX to UE static meshes]
    G --> H[220_add_SM_to_lvl.py\n:Add meshes to level]
```

## Table of Contents

1. [Overview](#1-overview)
2. [Detailed Script Descriptions](#2-script-descriptions)
    - [999_UE_manager.py](#21-999_ue_managerpy)
    - [010_export_gz_to_mod.py](#22-010_export_gz_to_modpy)
    - [100_headless_topnet_PCGHD.py & 200_headless_topnet_SWR.py](#23-100_headless_topnet_pcgdhpy--200_headless_topnet_swrpy)
    - [110_reimport_datatable.py](#24-110_reimport_datatablepy)
    - [000_export_splines_as_json.py](#25-000_export_splines_as_jsonpy)
    - [120_create_pcg_graph.py](#26-120_create_pcg_graphpy)
    - [220_add_SM_to_lvl.py](#27-220_add_sm_to_lvlpy)
    - [210_reimport_SM.py](#28-210_reimport_smpy)
3. [Asset & File Arborescence](#3-asset--file-arborescence)
    - [Legend](#legend)
    - [System File Structure](#31-system-file-structure)
    - [Unreal Content Browser Structure](#32-unreal-content-browser-structure)
    - [In-Level Organization](#in-level-organization-world-outliner)
4. [Notes](#notes)

---

## 🛠️ How to Use with Your Own Houdini Files

You can use your own Houdini `.hip` files for city, sidewalk, and road generation. This pipeline is designed for flexibility, but your HIP files **must** follow certain conventions to work out of the box.

> **Templates Provided:**
> - You’ll find template Houdini files in `../04_Houdini/` with all the necessary nodes and structure to run the pipeline. Start here if you’re unsure!

### 1. Where to Place Your HIP Files
- Place all Houdini `.hip` files in `lcroisez_Undini_framework/04_Houdini/`.
- (You can use another location, but you’ll need to provide the full path each time.)

### 2. How to Reference Your HIP File
- In the pipeline widget, or when running scripts directly, specify the path to your `.hip` file in the relevant field or argument.
- Example (Python):
  ```python
  run_houdini_headless(iteration_number=1, hip_file="./04_Houdini/your_city_file.hip", ...)
  ```
- Example (Widget):
  - Set the HIP file path in the widget’s configuration before running the Houdini step.

---

### 3. PCGHD: Requirements for Procedural City HIP Files
**Script:** `100_headless_topnet_PCGHD.py`

Your HIP file must have:
- **A TOP network** (default: `/obj/geo1/topnet`).
- **Input:**
  - FBX file (GenZone meshes) **or**
  - JSON file (splines)
  - The script chooses via `--switch_bool` (0 = splines, 1 = meshes).
- **Nodes & Parameters:**
  - `/obj/geo1/pcg_export1` with:
    - `file_mesh` (CSV mesh output)
    - `file_mat` (CSV material output)
  - `/obj/geo1/python_import_splines_from_json` with:
    - `iteration_number` (int)
    - `base_path` (string)
  - `/obj/geo1/switch_bool` (or similar) to switch input type.
- **Outputs:**
  - Mesh CSV (e.g., `mesh_001.csv`)
  - Material CSV (e.g., `mat_001.csv`)
- **TOPnet must have a `cookbutton` parameter** to trigger cooking.

**To adapt your own HIP:**
- Copy the template and modify geometry, logic, or parameters as needed.
- If you use different node names/paths, update the pipeline config or script arguments.
- Make sure the input/output logic matches what the pipeline expects.

---

### 4. SWR: Requirements for Sidewalks & Roads HIP Files
**Script:** `200_headless_topnet_SWR.py`

Your HIP file must have:
- **A TOP network** (default: `/obj/geo1/topnet`).
- **Input:**
  - JSON file (splines), path set via `--base_path` and `--iteration_number`.
- **Nodes & Parameters:**
  - `/obj/geo1/rop_fbx_road` with `sopoutput` (road FBX output)
  - `/obj/geo1/rop_fbx_sidewalks` with `sopoutput` (sidewalks FBX output)
  - `/obj/geo1/python_import_splines_from_json` with:
    - `iteration_number` (int)
    - `base_path` (string)
  - `/obj/geo1/switch_bool` (or similar) to control network behavior.
- **Outputs:**
  - Road FBX (e.g., `road_001.fbx`)
  - Sidewalks FBX (e.g., `sidewalks_001.fbx`)
- **TOPnet must have a `cookbutton` parameter** to trigger cooking.

**To adapt your own HIP:**
- Start from the template, replace geometry/nodes as needed.
- If you use different node names/paths, update the pipeline config or script arguments.
- Make sure the outputs are written to the paths provided by the script.

---

### 5. Step-by-Step: Running with Your HIP File
1. Place your custom `.hip` in `04_Houdini/`.
2. In the widget or script, set the path to your HIP file.
3. Ensure your HIP has all required nodes/parameters as described above.
4. Run the pipeline step (widget or script). Check logs for errors about missing nodes, parameters, or outputs.
5. If you see errors, compare your HIP’s structure to the template and this documentation.

**Troubleshooting:**
- Errors about missing nodes/parameters mean your HIP file doesn’t match what the pipeline expects.
- Use the provided template as a reference for node names and structure.
- Check the logs for exact parameter/node names being set.

---

## Legend
- 🟦 `220_add_SM_to_lvl.py`
- 🟩 `120_create_pcg_graph.py`
- 🟧 `010_export_gz_to_mod.py`
- 🟪 `110_reimport_datatable.py`
- 🟫 `000_export_splines_as_json.py`
- 🟨 `100_headless_topnet_PCGHD.py` / `200_headless_topnet_SWR.py`
- 🟥 `210_reimport_SM.py`

---

## 1. Overview
This document details the functionality and workflow of the Unreal Engine pipeline automation scripts managed by `999_UE_manager.py`. It also provides a schema of all files and assets created or interacted with by these scripts, both on disk and in the Unreal Content Browser. The Undini framework provides a complete pipeline for procedural generation of urban environments in Unreal Engine, with Houdini processing for buildings, sidewalks, and roads.

---

## 2. Script Descriptions

### 2.1. 999_UE_manager.py
**Role:** Central orchestrator for the entire procedural pipeline.

- **What it does:**
  - Loads and executes all other pipeline scripts in sequence or individually.
  - Provides callable functions for each step, which can be triggered from Unreal or as part of a batch pipeline.
  - Handles argument passing, result logging, and error handling.
  - Manages Houdini subprocess execution for headless processing.
- **Functions:**
  - `run_script(script_name, function_name, **kwargs)` — Generic function to run any script in the pipeline.
  - `run_houdini_headless(iteration_number, ...)` — Runs Houdini in headless mode for PCG building generation.
  - `run_houdini_sidewalks_roads(iteration_number, ...)` — Runs Houdini in headless mode for sidewalks and roads generation.
- **Pipeline Steps (in order):**
  1. Export splines to JSON (`000_export_splines_as_json.py`)
  2. Export GenZone meshes to FBX (`010_export_gz_to_mod.py`)
  3. Run Houdini PCG building generation (`100_headless_topnet_PCGHD.py`)
  4. Reimport datatables from CSVs (`110_reimport_datatable.py`)
  5. Create PCG graph in the level (`120_create_pcg_graph.py`)
  6. Run Houdini sidewalks & roads generation (`200_headless_topnet_SWR.py`)
  7. Reimport static meshes from FBX (`210_reimport_SM.py`)
  8. Add sidewalks & roads to the level (`220_add_SM_to_lvl.py`)
- **Typical usage:**
  ```python
  # The manager script runs each step in sequence
  # Export splines to JSON
  result = run_script("000_export_splines_as_json.py", "main", iteration_number=5)
  
  # Export GenZone meshes
  result = run_script("010_export_gz_to_mod.py", "main", iteration_number=5)
  
  # Run Houdini PCG generation
  result = run_houdini_headless(iteration_number=5, ...)
  
  # Reimport datatables
  result = run_script("110_reimport_datatable.py", "reimport_all_datatables", iteration_number=5)
  
  # Create PCG graph
  result = run_script("120_create_pcg_graph.py", "duplicate_and_rename_pcg_blueprint", iteration_number=5)
  
  # Run Houdini sidewalks & roads generation
  result = run_houdini_sidewalks_roads(iteration_number=5, ...)
  
  # Reimport static meshes
  result = run_script("210_reimport_SM.py", "reimport_folder_static_meshes", iteration_number=5)
  
  # Add sidewalks & roads to level
  result = run_script("220_add_SM_to_lvl.py", "add_SM_sidewalks_and_roads_to_level", iteration_number=5)
  ```

### 2.2. 010_export_gz_to_mod.py
**Role:** Batch export of GenZone static meshes to FBX for Houdini/other DCCs.
- **Key Function:** `main(iteration_number=0)`
- **Workflow:**
    - Scans all `StaticMeshActor` assets in the current level whose mesh name contains "genzone" (case-insensitive).
    - For each, exports the mesh as an FBX to a target directory, appending the iteration number to the filename.
    - Uses Unreal's `AssetExportTask` for automation.
    - Logs all actions and errors to the Unreal Output Log with emoji indicators for better readability.
- **Arguments:**
    - `iteration_number`: Used to suffix exported filenames for versioning.
- **Inputs:** Static meshes in the level with "genzone" in their name.
- **Outputs:** FBX files in the project's `03_GenDatas/Dependancies/PCG_HD/In/GZ/Mod/` directory.
- **Error Handling:** Warns if no meshes found, logs export failures with detailed messages.
- **User-driven vs Automated:** Fully automated; user only needs to run the script from the manager.

### 2.3. 100_headless_topnet_PCGHD.py & 200_headless_topnet_SWR.py
**Role:** Procedural generation via Houdini in headless mode.
- **Key Functionality:** Launched as a subprocess from the manager, not a Python function.
- **Workflow:**
    - **100_headless_topnet_PCGHD.py**: Processes GenZone meshes and splines to generate building data
    - **200_headless_topnet_SWR.py**: Processes splines to generate sidewalks and roads
    - Both scripts receive HIP file, topnet, input/output file paths, and iteration number as arguments
    - Both run Houdini in headless mode (no GUI) for automation
    - Both log detailed progress with timestamps and error information
- **Inputs:**
    - FBX files from GenZone exports (e.g., `SM_genzones_PCG_HD_{iteration_number}.fbx`)
    - JSON files from spline exports (e.g., `splines_export_from_UE_{iteration_number}.json`)
- **Outputs:**
    - **100_headless_topnet_PCGHD.py**: CSV files for building data (`mesh_{iteration_number}.csv`, `mat_{iteration_number}.csv`)
    - **200_headless_topnet_SWR.py**: FBX files for sidewalks and roads (`sidewalks_{iteration_number}.fbx`, `road_{iteration_number}.fbx`)
- **Error Handling:** Logs errors to the console with detailed information, which are captured by the manager script.
- **User-driven vs Automated:** Fully automated; launched by the manager script.

### 2.4. 110_reimport_datatable.py
**Role:** Reimport CSV files as Unreal datatables.
- **Key Function:** `reimport_all_datatables(iteration_number=0, csv_dir=None)`
- **Workflow:**
    - Locates CSV files in the specified directory (e.g., `mesh_{iteration_number}.csv`, `mat_{iteration_number}.csv`)
    - Uses the Unreal Engine DataTable API to reimport the CSV data
    - Provides detailed logging with emoji indicators for better readability
    - Handles errors gracefully with informative messages
- **Arguments:**
    - `csv_dir`: Directory of CSVs (optional, default from pipeline)
    - `iteration_number`: Used for file naming
- **Inputs:** CSV files like `mesh_{iteration_number}.csv`, `mat_{iteration_number}.csv`.
- **Outputs:** Updated datatable assets in `/Game/Developers/lukacroisez/PCG_HD/CSV/`.
- **Error Handling:** Warns if files missing or reimport fails.
- **User-driven vs Automated:** Fully automated; user only needs to ensure CSVs are present.

### 2.5. 000_export_splines_as_json.py
**Role:** Export spline actors from Unreal to JSON for external tools or documentation.
- **Key Function:** `main(iteration_number=0, output_dir=None)`
- **Workflow:**
    - Finds all actors in the level whose name starts with `BP_CityKit_spline`
    - For each, extracts spline points, tangents, rotations, and other metadata
    - Organizes the data in a structured JSON format for Houdini processing
    - Writes all spline data to a JSON file, named with the current iteration number
    - Provides detailed logging with emoji indicators for better readability
- **Arguments:**
    - `iteration_number`: Used for output file naming
    - `output_dir`: Target directory for JSON (optional, uses default if not provided)
- **Inputs:** Spline actors in the level
- **Outputs:** JSON file named `splines_export_from_UE_{iteration_number}.json` in the specified output directory
- **Error Handling:** Warns if no splines found, logs JSON write failures with detailed messages
- **User-driven vs Automated:** Fully automated; user only needs to ensure splines exist in the level

### 2.6. 120_create_pcg_graph.py
**Role:** Duplicate and instantiate a PCG graph Blueprint for the current iteration.
- **Key Function:** `duplicate_and_rename_pcg_blueprint(iteration_number=0, template_bp_path=None)`
- **Workflow:**
    - Checks if the PCG template BP exists.
    - Duplicates the template, renames it to `BPi_PCG_HD_{iteration_number}` in the instance folder.
    - Spawns the new BP as an actor at world origin in the current level.
    - Logs all actions and errors.
- **Arguments:**
    - `iteration_number`: Used for naming the duplicate BP.
- **Inputs:** `/Game/Developers/lukacroisez/PCG_HD/BP/BP_PCG_HD_TEMPLATE.BP_PCG_HD_TEMPLATE`
- **Outputs:** `/Game/Developers/lukacroisez/PCG_HD/BP/BP_PCG_HD_inst/BPi_PCG_HD_{iteration_number}` and an actor in the level.
- **Error Handling:** Logs if template missing, duplication fails, or actor spawn fails.
- **User-driven vs Automated:** Fully automated; user only needs to run the manager.

### 2.7. 220_add_SM_to_lvl.py
**Role:** Add sidewalk and road static mesh chunks to the level and organize them.
- **Key Function:** `add_SM_sidewalks_and_roads_to_level(iteration_number=1)`
- **Workflow:**
    - Uses Unreal's AssetRegistry to find all static meshes matching `sidewalks_{iteration_number}_piece_*` and `road_{iteration_number}_piece_*`
    - Loads each mesh, spawns as a `StaticMeshActor` at the origin
    - Sets each actor's label and assigns it to either the `Sidewalks` or `Roads` folder in the World Outliner
    - Provides detailed logging with emoji indicators for better readability
    - Tracks success and failure counts for comprehensive reporting
- **Arguments:**
    - `iteration_number`: Used for mesh name filtering
- **Inputs:** Static meshes named with the correct pattern (previously imported by `210_reimport_SM.py`)
- **Outputs:** Spawned actors in the level, organized in folders
- **Error Handling:** Logs missing assets, failed spawns, or missing components with detailed messages
- **User-driven vs Automated:** Fully automated; user only needs to run the manager

### 2.8. 210_reimport_SM.py
**Role:** Import or reimport static meshes from FBX files.
- **Key Function:** `reimport_folder_static_meshes(iteration_number=None, fbx_dir=None)`
- **Workflow:**
    - Scans a directory for FBX files matching the specific iteration number pattern (`road_{iteration_number}.fbx` and `sidewalks_{iteration_number}.fbx`)
    - For each, attempts to reimport if the asset already exists in Unreal, or import as new if it doesn't
    - Uses multiple methods for import/reimport to handle different Unreal Engine versions:
      - Primary method: AssetImportTask with FbxFactory
      - Fallback 1: EditorAssetSubsystem import_asset method
      - Fallback 2: ContentBrowserSubsystem import methods
    - Provides detailed logging with emoji indicators for better readability
    - Generates a comprehensive summary of import results
- **Arguments:**
    - `iteration_number`: Used for asset naming/filtering
    - `fbx_dir`: Directory containing FBX files to import
- **Inputs:** FBX files in the specified directory (generated by `200_headless_topnet_SWR.py`)
- **Outputs:** Imported/updated static mesh assets in Unreal
- **Error Handling:** Logs import failures with detailed messages, tries multiple methods before giving up
- **User-driven vs Automated:** Automated, but user must ensure FBX files are present and named correctly

---

## 3. Asset & File Arborescence

### 3.1. System File Structure
```plaintext
/YourRepoRoot/
├── 01_Scripts/
│   ├── 999_UE_manager.py         # 🟦🟩🟧🟪🟫🟨🟥 (calls all scripts)
│   ├── 000_export_splines_as_json.py # 🟫 (step 1)
│   ├── 010_export_gz_to_mod.py   # 🟧 (step 2)
│   ├── 100_headless_topnet_PCGHD.py # 🟨 (step 3)
│   ├── 110_reimport_datatable.py # 🟪 (step 4)
│   ├── 120_create_pcg_graph.py   # 🟩 (step 5)
│   ├── 200_headless_topnet_SWR.py # 🟨 (step 6)
│   ├── 210_reimport_SM.py        # 🟥 (step 7)
│   ├── 220_add_SM_to_lvl.py      # 🟦 (step 8)
│   └── luk4m4_Undini_doc_complete.md # (this file)
│
├── 03_GenDatas/
│   ├── Dependancies/
│   │   ├── PCG_HD/
│   │   │   ├── In/
│   │   │   │   ├── GZ/
│   │   │   │   │   ├── Mod/
│   │   │   │   │   │   └── SM_genzones_PCG_HD_{iteration_number}.fbx # 🟧 (exported by export_gz_to_mod)
│   │   │   │   │   └── Splines/
│   │   │   │   │       └── splines_export_from_UE_{iteration_number}.json # 🟫 (exported by export_splines_as_json)
│   │   │   └── Out/
│   │   │       └── CSV/
│   │   │           ├── mesh_{iteration_number}.csv # 🟨🟪 (generated by Houdini, imported by reimport_datatable) 
│   │   │           └── mat_{iteration_number}.csv  # 🟨🟪 (generated by Houdini, imported by reimport_datatable)
│   │   └── SW_Roads/
│   │       └── Out/
│   │           └── Mod/
│   │               ├── sidewalks_{iteration_number}.fbx # 🟨🟥 (generated by Houdini, imported by reimport_SM)
│   │               └── road_{iteration_number}.fbx      # 🟨🟥 (generated by Houdini, imported by reimport_SM)
│
├── 04_Houdini/
│   ├── genbuildingbase3.hip      # 🟨 (Houdini file for PCG building generation)
│   └── sidewalks_roads.hip       # 🟨 (Houdini file for sidewalks and roads generation)
```

---

### 3.2. Unreal Content Browser Structure
```plaintext
/Game/luk4m4_Undini/
├── BP/
│   ├── BP_PCG_HD_TEMPLATE (Blueprint asset)                # 🟩 (read by create_pcg_graph)
│   ├── BP_CityKit_spline (Blueprint asset)                 # 🟫 (read by export_splines_as_json)
│   │
│   └── BP_PCG_HD_inst/                                    # 🟩 (written by create_pcg_graph)
│       ├── BPi_PCG_HD_0 (Blueprint instance)              # 🟩
│       ├── BPi_PCG_HD_1 (Blueprint instance)              # 🟩
│       └── BPi_PCG_HD_{iteration_number}                  # 🟩
│
├── CSV/                                              # 🟪 (read/written by reimport_datatable)
│   ├── mesh_template (DataTable asset)                  # 🟪 (template for mesh data)
│   ├── mat_template (DataTable asset)                   # 🟪 (template for material data)
│   ├── mesh_{iteration_number} (DataTable asset)         # 🟪 (imported by reimport_datatable)
│   └── mat_{iteration_number} (DataTable asset)          # 🟪 (imported by reimport_datatable)
│
├── Static Meshes/                                     # 🟦🟥 (read/written by add_SM_to_lvl, reimport_SM)
│   ├── sidewalks_{iteration_number}_piece_*             # 🟦🟥 (imported by reimport_SM, used by add_SM_to_lvl)
│   └── road_{iteration_number}_piece_*                  # 🟦🟥 (imported by reimport_SM, used by add_SM_to_lvl)
│
└── GenZones/                                          # 🟧 (read by export_gz_to_mod)
    └── [Static Mesh actors with "genzone" in their name]  # 🟧 (exported by export_gz_to_mod)
```

---

#### **In-Level Organization (World Outliner)**
- **Sidewalks** (folder) 🟦
  - All spawned `sidewalks_{iteration_number}_piece_*` actors (by 220_add_SM_to_lvl.py)
  - Organized for easy selection and manipulation
- **Roads** (folder) 🟦
  - All spawned `road_{iteration_number}_piece_*` actors (by 220_add_SM_to_lvl.py)
  - Organized for easy selection and manipulation
- **BPi_PCG_HD_{iteration_number}** 🟩
  - Spawned at world origin (by 120_create_pcg_graph.py)
  - Contains PCG nodes for procedural building generation

---

**Legend:** See top of document for script emoji meanings.

- Each emoji indicates which script(s) read/write or affect the asset/file/folder
- The numerical prefixes in script names (000_, 010_, etc.) indicate the order in the pipeline
- For any asset or file, you can quickly see which part of the pipeline is responsible

---

## Notes

### Pipeline Design Principles
- **Sequential Processing**: The pipeline is designed to be run in sequence, with each step building on the previous one
- **Iteration-Based**: All assets are versioned by iteration number for easy tracking and management
- **Modular Architecture**: Each script performs a specific task and can be run independently if needed
- **Robust Error Handling**: Scripts include detailed logging and fallback mechanisms for reliability
- **User-Friendly Feedback**: Emoji indicators and conversational logging make it easy to understand what's happening

### Technical Requirements
- All scripts are designed for Unreal Engine 5.3.2 and use the official Python API
- Houdini 20.0.653 is required for the procedural generation steps
- Asset naming and folder structure are critical for automation success—ensure consistency

### Best Practices
- Always run the scripts in order (as numbered in their filenames)
- Check the Unreal Output Log for detailed progress and error messages
- Keep consistent naming conventions for all assets
- Use the manager script (999_UE_manager.py) to orchestrate the entire pipeline

---

For further details or customization, see the inline docstrings in each script or contact the pipeline maintainer.
