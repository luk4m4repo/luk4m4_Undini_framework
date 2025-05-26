import unreal
import json
import os


def export_splines_to_json(iteration_number=0, output_dir=None):
    """
    Finds all BP_CityKit_spline actors in the current Unreal level, extracts their spline data,
    and saves everything as a JSON file for use in Houdini or other tools.
    
    Args:
        iteration_number (int): The current iteration number for file naming
        output_dir (str): Directory to save the JSON file. If None, uses the project's Saved directory
        
    Returns:
        dict: Information about the exported splines including count and file path
    """
    # Create a result dictionary
    result = {
        'spline_count': 0,
        'file_path': None
    }
    
    # Find all spline actors
    editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    all_actors = editor_actor_subsystem.get_all_level_actors()
    spline_actors = []
    for actor in all_actors:
        actor_name = actor.get_actor_label()
        if actor_name.startswith("BP_CityKit_spline"):
            spline_actors.append(actor)
    
    if not spline_actors:
        unreal.log_warning("No BP_CityKit_spline* actors found in the current level. Did you forget to add some?")
        return result
    
    # Process splines
    splines_data = []
    for actor in spline_actors:
        actor_name = actor.get_actor_label()
        actor_location = actor.get_actor_location()
        
        # Get spline components
        components = actor.get_components_by_class(unreal.SplineComponent)
        spline_components = list(components)
        
        if not spline_components:
            unreal.log_warning(f"No spline components found in actor '{actor_name}'. Skipping this one.")
            continue
            
        for comp_index, spline_component in enumerate(spline_components):
            component_name = spline_component.get_name()
            
            # Extract points data
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
            
            # Create spline data entry
            spline_data = {
                "actor_name": actor_name,
                "actor_location": {"x": actor_location.x, "y": actor_location.y, "z": actor_location.z},
                "component_name": component_name,
                "component_index": comp_index,
                "points": points_data
            }
            splines_data.append(spline_data)
    
    # Set output directory
    if output_dir is None:
        # Use a default path in the project directory
        project_dir = unreal.Paths.project_dir()
        output_dir = os.path.join(project_dir, "Saved", "SplineExports")
    
    # Create the directory if it doesn't exist
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            unreal.log(f"Created output directory for splines: {output_dir}")
        except Exception as e:
            unreal.log_error(f"Couldn't create output directory '{output_dir}'. Error: {str(e)}")
            return result
    
    # Write JSON file
    output_file = os.path.join(output_dir, f"splines_export_from_UE_{iteration_number}.json")
    try:
        with open(output_file, 'w') as f:
            json.dump(splines_data, f, indent=4)
        
        result['spline_count'] = len(splines_data)
        result['file_path'] = output_file
        
        unreal.log(f"Successfully exported {len(splines_data)} spline components to: {output_file}")
        return result
    except Exception as e:
        unreal.log_error(f"Failed to write JSON file '{output_file}'. Error: {str(e)}")
        return result


# Run the export when this script is executed directly
if __name__ == "__main__":
    result = export_splines_to_json()
    unreal.log(f"Export result: {result}")
