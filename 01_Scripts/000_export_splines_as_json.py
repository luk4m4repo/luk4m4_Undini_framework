import unreal
import json
import os


def export_splines_to_json(iteration_number=0, output_dir=None):
    """
    Finds all BP_CityKit_spline actors in the current Unreal level, extracts their spline data,
    and saves everything as a JSON file for use in Houdini or other tools.
    
    This is the first step in our pipeline - we export spline data from Unreal Engine
    to be used later by Houdini for procedural generation.
    
    Args:
        iteration_number (int): The current iteration number for file naming
        output_dir (str): Directory to save the JSON file. If None, uses the project's Saved directory
        
    Returns:
        dict: Information about the exported splines including count and file path
    """
    # We'll track our progress and results in this dictionary
    result = {
        'spline_count': 0,
        'file_path': None
    }
    
    # First, let's find all the spline actors in the current level
    # We're looking specifically for actors named 'BP_CityKit_spline*'
    unreal.log("Looking for BP_CityKit_spline actors in the current level...")
    editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    all_actors = editor_actor_subsystem.get_all_level_actors()
    spline_actors = []
    for actor in all_actors:
        actor_name = actor.get_actor_label()
        if actor_name.startswith("BP_CityKit_spline"):
            spline_actors.append(actor)
    
    # If we didn't find any splines, let the user know and exit early
    if not spline_actors:
        unreal.log_warning("No BP_CityKit_spline* actors found in the current level. Did you forget to add some?")
        return result
    
    # Now let's process each spline and extract all the data we need
    unreal.log(f"Processing {len(spline_actors)} spline actors...")
    splines_data = []
    for actor in spline_actors:
        actor_name = actor.get_actor_label()
        actor_location = actor.get_actor_location()
        
        # Each spline actor might have multiple spline components
        # We need to extract data from each one
        components = actor.get_components_by_class(unreal.SplineComponent)
        spline_components = list(components)
        
        if not spline_components:
            unreal.log_warning(f"No spline components found in actor '{actor_name}'. Skipping this one.")
            continue
            
        for comp_index, spline_component in enumerate(spline_components):
            component_name = spline_component.get_name()
            
            # For each spline component, we need to extract data for every point
            # This includes position, tangent, rotation, scale, and point type
            # Houdini will use this data to recreate the splines exactly
            points_data = []
            num_points = spline_component.get_number_of_spline_points()
            unreal.log(f"Extracting data from {num_points} points in component '{component_name}'")
            
            for i in range(num_points):
                # Get all the data in world space coordinates so it's consistent
                location = spline_component.get_location_at_spline_point(i, unreal.SplineCoordinateSpace.WORLD)
                tangent = spline_component.get_tangent_at_spline_point(i, unreal.SplineCoordinateSpace.WORLD)
                rotation = spline_component.get_rotation_at_spline_point(i, unreal.SplineCoordinateSpace.WORLD)
                scale = spline_component.get_scale_at_spline_point(i)
                point_type = spline_component.get_spline_point_type(i)
                
                # Store all the point data in a structured format for JSON export
                # This makes it easy for Houdini to parse later
                point_data = {
                    "index": i,
                    "location": {"x": location.x, "y": location.y, "z": location.z},
                    "tangent": {"x": tangent.x, "y": tangent.y, "z": tangent.z},
                    "rotation": {"roll": rotation.roll, "pitch": rotation.pitch, "yaw": rotation.yaw},
                    "scale": {"x": scale.x, "y": scale.y, "z": scale.z},
                    "point_type": str(point_type)
                }
                points_data.append(point_data)
            
            # Now create a complete entry for this spline component
            # We include the actor name, location, component info, and all point data
            spline_data = {
                "actor_name": actor_name,
                "actor_location": {"x": actor_location.x, "y": actor_location.y, "z": actor_location.z},
                "component_name": component_name,
                "component_index": comp_index,
                "points": points_data
            }
            splines_data.append(spline_data)
    
    # Now we need to save our data to a JSON file
    # First, let's determine where to save it
    if output_dir is None:
        # If no output directory was specified, use a default path
        # This is consistent with the manager script's SPLINES_OUTPUT_DIR
        project_dir = unreal.Paths.project_dir()
        output_dir = os.path.join(project_dir, "Saved", "SplineExports")
        unreal.log(f"No output directory specified, using default: {output_dir}")
    else:
        unreal.log(f"Using specified output directory: {output_dir}")
    
    # Make sure the directory exists before we try to write to it
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            unreal.log(f"Created output directory for splines: {output_dir}")
        except Exception as e:
            unreal.log_error(f"Couldn't create output directory '{output_dir}'. Error: {str(e)}")
            return result
    
    # Create our output filename with the iteration number
    # This naming convention is important for the rest of the pipeline
    output_file = os.path.join(output_dir, f"splines_export_from_UE_{iteration_number}.json")
    unreal.log(f"Saving spline data to: {output_file}")
    
    # Write all our spline data to the JSON file
    try:
        with open(output_file, 'w') as f:
            json.dump(splines_data, f, indent=4)
        
        # Update our result with the final counts and path
        result['spline_count'] = len(splines_data)
        result['file_path'] = output_file
        
        unreal.log(f"✅ Successfully exported {len(splines_data)} spline components to: {output_file}")
        return result
    except Exception as e:
        unreal.log_error(f"❌ Failed to write JSON file '{output_file}'. Error: {str(e)}")
        return result


# Run the export when this script is executed directly (not imported by another script)
if __name__ == "__main__":
    unreal.log("Starting spline export process...")
    result = export_splines_to_json()
    unreal.log(f"Export complete! Result: {result}")
    unreal.log("This script can also be run from the UE_manager.py script with specific parameters.")
    unreal.log("Check 999_UE_manager.py for more information.")

