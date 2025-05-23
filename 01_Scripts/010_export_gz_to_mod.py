import unreal
import os

EXPORT_DIR = r"S:/users/luka.croisez/ProcGenPipeline/Dependancies/PCG_HD/In/GZ/Mod"


def get_all_static_meshes_in_level():
    """Find all unique Static Mesh assets used by StaticMeshActors in the current level whose name contains 'genzone'."""
    editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    all_actors = editor_actor_subsystem.get_all_level_actors()
    static_meshes = set()
    for actor in all_actors:
        # Only StaticMeshActor (not Blueprints, etc)
        if isinstance(actor, unreal.StaticMeshActor):
            sm_comp = actor.static_mesh_component
            if sm_comp:
                mesh = sm_comp.static_mesh
                if mesh and 'genzone' in mesh.get_name().lower():
                    static_meshes.add(mesh)
    return list(static_meshes)


def export_static_mesh_to_fbx(static_mesh, export_dir, iteration_number):
    mesh_name = static_mesh.get_name()
    export_path = os.path.join(export_dir, f"{mesh_name}_{iteration_number}.fbx")
    
    # Setup export options
    fbx_options = unreal.FbxExportOption()
    fbx_options.collision = False
    fbx_options.vertex_color = True
    fbx_options.level_of_detail = False
    fbx_options.fbx_export_compatibility = unreal.FbxExportCompatibility.FBX_2020

    export_task = unreal.AssetExportTask()
    export_task.object = static_mesh
    export_task.filename = export_path
    export_task.automated = True
    export_task.replace_identical = True
    export_task.prompt = False
    export_task.options = fbx_options

    try:
        result = unreal.Exporter.run_asset_export_task(export_task)
        if result:
            unreal.log(f"Exported: {mesh_name} -> {export_path}")
        else:
            unreal.log_error(f"Failed to export: {mesh_name}")
        return result
    except Exception as e:
        unreal.log_error(f"Exception exporting {mesh_name}: {str(e)}")
        return False


def main(iteration_number=0):
    if not os.path.exists(EXPORT_DIR):
        try:
            os.makedirs(EXPORT_DIR, exist_ok=True)
            unreal.log(f"Created export directory: {EXPORT_DIR}")
        except Exception as e:
            unreal.log_error(f"Failed to create export directory: {EXPORT_DIR}. Error: {str(e)}")
            return

    meshes = get_all_static_meshes_in_level()
    if not meshes:
        unreal.log_warning("No Static Meshes with 'genzone' in the name found in the current level.")
        return

    unreal.log(f"Found {len(meshes)} unique Static Mesh assets with 'genzone' in the name.")
    success_count = 0
    for mesh in meshes:
        if export_static_mesh_to_fbx(mesh, EXPORT_DIR, iteration_number):
            success_count += 1

    unreal.log(f"Export complete: {success_count}/{len(meshes)} meshes exported to {EXPORT_DIR}")


if __name__ == "__main__":
    main(0)
