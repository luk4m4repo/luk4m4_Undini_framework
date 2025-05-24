import unreal
import json
import os


def get_current_level():
    """
    Returns the current level in the Unreal Editor.
    """
    return unreal.EditorLevelLibrary.get_editor_world()


def find_spline_actors():
    """
    Finds all actors in the current level whose names start with 'BP_CityKit_spline'.
    Returns a list of matching actors.
    """
    editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    all_actors = editor_actor_subsystem.get_all_level_actors()
    spline_actors = []
    for actor in all_actors:
        actor_name = actor.get_actor_label()
        if actor_name.startswith("BP_CityKit_spline"):
            spline_actors.append(actor)
    return spline_actors


def get_spline_components(actor):
    """
    Retrieves all SplineComponent objects from the given actor.
    Returns a Python list of spline components.
    """
    components = actor.get_components_by_class(unreal.SplineComponent)
    return list(components)


def get_spline_points_data(spline_component):
    """
    Extracts all relevant data for each point in the given spline component.
    Returns a list of dictionaries, one per point.
    """
    points_data = []
    num_points = spline_component.get_number_of_spline_points()
    for i in range(num_points):
        location = spline_component.get_location_at_spline_point(i, unreal.SplineCoordinateSpace.WORLD)
        tangent = spline_component.get_tangent_at_spline_point(i, unreal.SplineCoordinateSpace.WORLD)
        rotation = spline_component.get_rotation_at_spline_point(i, unreal.SplineCoordinateSpace.WORLD)
        scale = spline_component.get_scale_at_spline_point(i)
        point_type = spline_component.get_spline_point_type(i)
        point_data = {
            "index": i,
            "location": {"x": location.x, "y": location.y, "z": location.z},
            "tangent": {"x": tangent.x, "y": tangent.y, "z": tangent.z},
            "rotation": {"roll": rotation.roll, "pitch": rotation.pitch, "yaw": rotation.yaw},
            "scale": {"x": scale.x, "y": scale.y, "z": scale.z},
            "point_type": str(point_type)
        }
        points_data.append(point_data)
    return points_data


def export_splines_to_json():
    """
    Finds all BP_CityKit_spline actors in the current Unreal level, extracts their spline data,
    and saves everything as a friendly JSON file for use in Houdini or other tools.
    If you want to customize the output directory or iteration number, set 'output_dir' and 'iteration_number' as globals before running.
    """
    spline_actors = find_spline_actors()
    if not spline_actors:
        unreal.log_warning("Hey! No BP_CityKit_spline* actors found in the current level. Did you forget to add some?")
        return
    splines_data = []
    for actor in spline_actors:
        actor_name = actor.get_actor_label()
        actor_location = actor.get_actor_location()
        spline_components = get_spline_components(actor)
        if not spline_components:
            unreal.log_warning(f"Heads up: No spline components found in actor '{actor_name}'. Skipping this one.")
            continue
        for comp_index, spline_component in enumerate(spline_components):
            component_name = spline_component.get_name()
            spline_data = {
                "actor_name": actor_name,
                "actor_location": {"x": actor_location.x, "y": actor_location.y, "z": actor_location.z},
                "component_name": component_name,
                "component_index": comp_index,
                "points": get_spline_points_data(spline_component)
            }
            splines_data.append(spline_data)
    # Set output directory, allowing override from globals
    if 'output_dir' in globals():
        output_dir = globals()['output_dir']
    else:
        # Default to ../03_GenDatas/Dependancies/PCG_HD/In/GZ/Splines relative to repo root
        output_dir = os.path.join('03_GenDatas', 'Dependancies', 'PCG_HD', 'In', 'GZ', 'Splines')
    # Create the directory if it doesn't exist
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            unreal.log(f"Created output directory for splines: {output_dir}")
        except Exception as e:
            unreal.log_error(f"Couldn't create output directory '{output_dir}'. Error: {str(e)}. Please check your permissions!")
            return None
    # Use iteration_number in the output filename
    if 'iteration_number' in globals():
        it_num = globals()['iteration_number']
    else:
        it_num = 0
    # Always resolve output_dir relative to workspace root if not absolute
    WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    if not os.path.isabs(output_dir):
        output_dir = os.path.join(WORKSPACE_ROOT, output_dir)
    output_file = os.path.join(output_dir, f"splines_export_from_UE_{it_num}.json")
    # Write JSON file
    try:
        with open(output_file, 'w') as f:
            json.dump(splines_data, f, indent=4)
        unreal.log(f"Successfully exported {len(splines_data)} spline components to: {output_file}")
        return output_file
    except Exception as e:
        unreal.log_error(f"Oops! Failed to write JSON file '{output_file}'. Error: {str(e)}")
        return None


# Run the export when this script is executed directly
if __name__ == "__main__":
    export_file = export_splines_to_json()
    if export_file:
        unreal.log(f"Splines exported to: {export_file}")
    else:
        unreal.log_error("Failed to export splines. See error above for details.")
