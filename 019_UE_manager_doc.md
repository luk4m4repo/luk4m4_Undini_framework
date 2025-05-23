# Unreal Pipeline Manager: Script Documentation & Asset/File Schema

## Table of Contents

1. [Overview](#1-overview)
2. [Detailed Script Descriptions](#2-script-descriptions)
    - [019_UE_manager.py](#21-019_ue_managerpy)
    - [019_UE_export_gz_to_mod.py](#22-019_ue_export_gz_to_modpy)
    - [019_HOUDINI_headless_topnet_PCGHD.py & 019_HOUDINI_headless_topnet_SWR.py](#23-019_houdini_headless_topnet_pcgdhpy--019_houdini_headless_topnet_swrpy)
    - [019_UE_reimport_datatable.py](#24-019_ue_reimport_datatablepy)
    - [019_UE_export_splines_as_json.py](#25-019_ue_export_splines_as_jsonpy)
    - [019_UE_create_pcg_graph.py](#26-019_ue_create_pcg_graphpy)
    - [019_UE_add_SM_to_lvl.py](#27-019_ue_add_sm_to_lvlpy)
    - [019_reimport_SM.py](#28-019_reimport_smpy)
3. [Asset & File Arborescence](#3-asset--file-arborescence)
    - [Legend](#legend)
    - [System File Structure](#31-system-file-structure)
    - [Unreal Content Browser Structure](#32-unreal-content-browser-structure)
    - [In-Level Organization](#in-level-organization-world-outliner)
4. [Notes](#notes)

---

## Legend
- 🟦 `019_UE_add_SM_to_lvl.py`
- 🟩 `019_UE_create_pcg_graph.py`
- 🟧 `019_UE_export_gz_to_mod.py`
- 🟪 `019_UE_reimport_datatable.py`
- 🟫 `019_UE_export_splines_as_json.py`
- 🟨 `019_HOUDINI_headless_topnet_PCGHD.py` / `019_HOUDINI_headless_topnet_SWR.py`
- 🟥 `019_reimport_SM.py`

---

## 1. Overview
This document details the functionality and workflow of the Unreal Engine pipeline automation scripts managed by `019_UE_manager.py`. It also provides a schema of all files and assets created or interacted with by these scripts, both on disk and in the Unreal Content Browser.

---

## 2. Script Descriptions

### 2.1. 019_UE_manager.py
**Role:** Central orchestrator for the entire procedural pipeline.

- **What it does:**
  - Loads and executes all other pipeline scripts in sequence or individually.
  - Provides callable functions for each step, which can be triggered from Unreal or as part of a batch pipeline.
  - Handles argument passing, result logging, and error handling.
- **Functions:**
  - `call_export_genzone_meshes(iteration_number)` — Exports GenZone static meshes to FBX files.
  - `call_reimport_all_datatables(iteration_number, csv_dir)` — Reimports all datatables from CSVs.
  - `call_export_splines_to_json(iteration_number, output_dir)` — Exports splines to JSON.
  - `call_create_and_add_pcg_graph(iteration_number)` — Duplicates and adds a PCG graph BP to the level.
  - `call_add_SM_sidewalks_and_roads_to_level(iteration_number)` — Adds sidewalk and road mesh actors to the level.
  - `call_reimport_folder_static_meshes(iteration_number, fbx_dir)` — Reimports static meshes from FBX files.
- **Typical usage:**
  ```python
  call_export_genzone_meshes(5)
  call_reimport_all_datatables(5, "<csv_dir>")
  call_export_splines_to_json(5, "<output_dir>")
  call_create_and_add_pcg_graph(5)
  call_add_SM_sidewalks_and_roads_to_level(5)
  call_reimport_folder_static_meshes(5, "<fbx_dir>")
  ```

### 2.2. 019_UE_export_gz_to_mod.py
**Role:** Batch export of GenZone static meshes to FBX for Houdini/other DCCs.
- **Key Function:** `main(iteration_number=0)`
- **Workflow:**
    - Scans all `StaticMeshActor` assets in the current level whose mesh name contains "genzone" (case-insensitive).
    - For each, exports the mesh as an FBX to a target directory, appending the iteration number to the filename.
    - Uses Unreal's `AssetExportTask` for automation.
    - Logs all actions and errors to the Unreal Output Log.
- **Arguments:**
    - `iteration_number`: Used to suffix exported filenames for versioning.
- **Inputs:** Static meshes in the level with "genzone" in their name.
- **Outputs:** FBX files in `S:/users/luka.croisez/ProcGenPipeline/Dependancies/PCG_HD/In/GZ/Mod/`.
- **Error Handling:** Warns if no meshes found, logs export failures.
- **User-driven vs Automated:** Fully automated; user only needs to run the script from the manager.

### 2.3. 019_HOUDINI_headless_topnet_PCGHD.py & 019_HOUDINI_headless_topnet_SWR.py
**Role:** Procedural generation via Houdini in headless mode.
- **Key Functionality:** Launched as a subprocess from the manager, not a Python function.
- **Workflow:**
    - Receives HIP file, topnet, input/output file paths, and iteration number as arguments.
    - Runs Houdini's `hython` to process geometry and export CSV/FBX data for Unreal import.
    - PCGHD variant: Generates PCG mesh/material CSVs.
    - SWR variant: Generates sidewalk/road FBX files.
- **Arguments:** All paths and iteration number passed as CLI args.
- **Inputs:** Pre-exported FBX files from Unreal.
- **Outputs:** CSVs and/or FBXs for import into Unreal.
- **Error Handling:** Minimal; relies on Houdini's own logging. Errors may need to be checked in Houdini logs.
- **User-driven vs Automated:** Fully automated; user triggers from manager, but must ensure Houdini and scripts are accessible.

### 2.4. 019_UE_reimport_datatable.py
**Role:** Reimport Unreal Engine datatables from generated CSVs.
- **Key Function:** `reimport_all_datatables()`
- **Workflow:**
    - Determines CSV directory and iteration number from globals (set by manager) or defaults.
    - Constructs paths for mesh and material CSVs for the current iteration.
    - For each CSV, checks existence and triggers Unreal's reimport for the corresponding datatable asset.
    - Logs successes and errors.
- **Arguments:**
    - `csv_dir`: Directory of CSVs (optional, default from pipeline).
    - `iteration_number`: Used for file naming.
- **Inputs:** CSV files like `mesh_{iteration_number}.csv`, `mat_{iteration_number}.csv`.
- **Outputs:** Updated datatable assets in `/Game/Developers/lukacroisez/PCG_HD/CSV/`.
- **Error Handling:** Warns if files missing or reimport fails.
- **User-driven vs Automated:** Fully automated; user only needs to ensure CSVs are present.

### 2.5. 019_UE_export_splines_as_json.py
**Role:** Export spline actors from Unreal to JSON for external tools or documentation.
- **Key Function:** `export_splines_to_json()`
- **Workflow:**
    - Finds all actors in the level whose name starts with `BP_CityKit_spline`.
    - For each, extracts spline points, tangents, rotations, and other metadata.
    - Writes all spline data to a JSON file, named with the current iteration number.
    - Output path can be set by the manager.
- **Arguments:**
    - `iteration_number`: Used for output file naming.
    - `output_dir`: Target directory for JSON.
- **Inputs:** Spline actors in the level.
- **Outputs:** JSON file per iteration.
- **Error Handling:** Warns if no splines found or file write fails.
- **User-driven vs Automated:** Automated; user can specify output location.

### 2.6. 019_UE_create_pcg_graph.py
**Role:** Duplicate and instantiate a PCG graph Blueprint for the current iteration.
- **Key Function:** `duplicate_and_rename_pcg_blueprint(iteration_number=0)`
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

### 2.7. 019_UE_add_SM_to_lvl.py
**Role:** Add sidewalk and road static mesh chunks to the level and organize them.
- **Key Function:** `add_SM_sidewalks_and_roads_to_level(iteration_number=1)`
- **Workflow:**
    - Uses Unreal's AssetRegistry to find all static meshes matching `sidewalks_{iteration_number}_piece_*` and `road_{iteration_number}_piece_*`.
    - Loads each mesh, spawns as a `StaticMeshActor` at the origin.
    - Sets each actor's label and assigns it to either the `Sidewalks` or `Roads` folder in the World Outliner.
    - Logs each step for debugging.
- **Arguments:**
    - `iteration_number`: Used for mesh name filtering.
- **Inputs:** Static meshes named with the correct pattern.
- **Outputs:** Spawned actors in the level, organized in folders.
- **Error Handling:** Logs missing assets, failed spawns, or missing components.
- **User-driven vs Automated:** Fully automated; user triggers from manager, must ensure mesh naming convention.

### 2.8. 019_reimport_SM.py
**Role:** Batch reimport of static meshes from FBX files.
- **Key Function:** `reimport_folder_static_meshes()`
- **Workflow:**
    - Reads FBX directory and iteration number from globals or defaults.
    - For each configured mesh (sidewalks, roads, etc.), constructs expected FBX filename and Unreal asset path.
    - Uses Unreal's AssetTools to import or reimport, applying basic import settings (auto collision, import materials/textures).
    - Logs results for each asset.
- **Arguments:**
    - `fbx_dir`: Directory containing FBX files.
    - `iteration_number`: Used for file/asset naming.
- **Inputs:** FBX files named like `sidewalks_{iteration_number}.fbx`, `road_{iteration_number}.fbx`.
- **Outputs:** Updated static meshes in Unreal asset folders.
- **Error Handling:** Logs missing files, import failures, or option mismatches.
- **User-driven vs Automated:** Automated, but user must ensure FBX files are present and named correctly.

---

## 3. Asset & File Arborescence

### 3.1. System File Structure
```plaintext
/YourRepoRoot/
├── Various_Scripts/
│   ├── 019_UE_manager.py         # 🟦🟩🟧🟪🟫🟨🟥 (calls all scripts)
│   ├── 019_UE_add_SM_to_lvl.py   # 🟦
│   ├── 019_UE_create_pcg_graph.py # 🟩
│   ├── 019_UE_export_gz_to_mod.py # 🟧
│   ├── 019_UE_reimport_datatable.py # 🟪
│   ├── 019_UE_export_splines_as_json.py # 🟫
│   ├── 019_reimport_SM.py        # 🟥
│   ├── 019_HOUDINI_headless_topnet_PCGHD.py # 🟨
│   ├── 019_HOUDINI_headless_topnet_SWR.py   # 🟨
│   └── 019_UE_manager_doc.md     # (this file)
│
├── [Other Houdini/CSV/FBX/JSON files]
│   ├── ...
```

---

### 3.2. Unreal Content Browser Structure
```plaintext
/Game/Developers/lukacroisez/PCG_HD/BP/
│
├── BP_PCG_HD_TEMPLATE (Blueprint asset)                # 🟩 (read by create_pcg_graph)
│
├── BP_PCG_HD_inst/                                    # 🟩 (written by create_pcg_graph)
│   ├── BPi_PCG_HD_0 (Blueprint instance)              # 🟩
│   ├── BPi_PCG_HD_1 (Blueprint instance)              # 🟩
│   └── BPi_PCG_HD_{iteration_number}                  # 🟩
│
├── [Other BP assets]
│
├── [Static Meshes]                                    # 🟦🟥 (read/written by add_SM_to_lvl, reimport_SM)
│   ├── sidewalks_0_piece_*                            # 🟦🟥
│   ├── sidewalks_1_piece_*                            # 🟦🟥
│   ├── road_0_piece_*                                 # 🟦🟥
│   └── road_1_piece_*                                 # 🟦🟥
│   ...
│
├── CSV/                                              # 🟪 (read/written by reimport_datatable)
│   ├── mesh_{iteration_number}                        # 🟪
│   ├── mat_{iteration_number}                         # 🟪
│   ...
```

---

#### **In-Level Organization (World Outliner)**
- **Sidewalks** (folder) 🟦
  - All spawned `sidewalks_{iteration_number}_piece_*` actors (by add_SM_to_lvl)
- **Roads** (folder) 🟦
  - All spawned `road_{iteration_number}_piece_*` actors (by add_SM_to_lvl)
- **BPi_PCG_HD_{iteration_number}** 🟩
  - Spawned at world origin (by create_pcg_graph)

---

#### **External/Intermediate Files**
```plaintext
S:/users/luka.croisez/ProcGenPipeline/Dependancies/PCG_HD/In/GZ/Mod/      # 🟧🟨
├── SM_genzones_PCG_HD_{iteration_number}.fbx                             # 🟧 (written by export_gz_to_mod, read by Houdini)

S:/users/luka.croisez/ProcGenPipeline/Dependancies/PCG_HD/Out/CSV/        # 🟨🟪
├── mesh_{iteration_number}.csv                                           # 🟨🟪
├── mat_{iteration_number}.csv                                            # 🟨🟪

S:/users/luka.croisez/ProcGenPipeline/Dependancies/SW_Roads/Out/Mod/      # 🟨🟥
├── sidewalks_{iteration_number}.fbx                                      # 🟨🟥
├── road_{iteration_number}.fbx                                           # 🟨🟥

[JSON Export Directory]                                                   # 🟫
├── splines_export_from_UE_{iteration_number}.json                        # 🟫
```

---

**Legend:** See top of document for script emoji meanings.

- Each emoji indicates which script(s) read/write or affect the asset/file/folder.
- For any asset or file, you can quickly see which part of the pipeline is responsible.

---

## Notes
- All scripts are designed for Unreal Engine 5.3.2 and use the official Python API.
- Asset naming and folder structure are critical for automation success—ensure consistency.
- Logs are primarily sent to the Unreal Output Log for easy debugging.

---

For further details or customization, see the inline docstrings in each script or contact the pipeline maintainer.
