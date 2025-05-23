# Unreal Pipeline Manager: Quick Reference

## What is this?
A set of Python scripts that automate the process of exporting, processing, and importing assets (meshes, splines, blueprints) between Unreal Engine and Houdini, making procedural content generation and asset management much faster and more reliable.

---

## Pipeline Overview

1. **Export**
   - Export static meshes (genzones, sidewalks, roads) and splines from Unreal to FBX/JSON.
2. **Process**
   - Use Houdini (headless) to generate new geometry, CSVs, or FBXs from exported data.
3. **Import**
   - Reimport processed meshes and datatables (CSV) into Unreal.
   - Duplicate and spawn new Blueprint graphs as needed.
   - Add generated meshes to the level, organized in folders.

---

## Key Scripts & Roles

- **019_UE_manager.py**: Orchestrates the whole pipeline (calls all other scripts).
- **019_UE_export_gz_to_mod.py**: Exports static meshes (genzones) to FBX.
- **019_HOUDINI_headless_topnet_PCGHD.py / SWR.py**: Runs Houdini to process exported assets and generate new ones.
- **019_UE_reimport_datatable.py**: Reimports CSVs as Unreal datatables.
- **019_UE_export_splines_as_json.py**: Exports all spline actors to JSON.
- **019_UE_create_pcg_graph.py**: Duplicates a PCG Blueprint and spawns it in the level.
- **019_UE_add_SM_to_lvl.py**: Adds sidewalk/road meshes to the level and organizes them.
- **019_reimport_SM.py**: Reimports static meshes from FBX.

---

## File & Asset Flow (Simplified)

```plaintext
- PCG HD
[Unreal Static Meshes or Splines] ──▶ (FBX export or JSON export) ──▶ [Houdini] ──▶ (CSV out) ──▶ [Unreal reimport]

- SW & Roads
[Unreal Static Meshes or Splines] ──▶ (FBX export or JSON export) ──▶ [Houdini] ──▶ (FBX out) ──▶ [Unreal reimport]

- Add to level
[BP Template] ──▶ (duplicate/instance) ──▶ [Level]
```

- All files are organized and versioned by iteration number.
- Naming conventions are important for automation.

---

## Main Principles
- **Automate everything possible.**
- **Follow naming conventions** for assets/files.
- **Scripts are modular**: manager script calls each step.
- **Minimal manual intervention**: user only triggers steps and checks outputs.
- **Logs and folders** keep things organized and debuggable.

---

## See also
- [Full Documentation](./019_UE_manager_doc.md)

