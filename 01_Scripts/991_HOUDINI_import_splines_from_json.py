node = hou.pwd()
geo = node.geometry()

# Import necessary modules
import json
import os

# Get the JSON file path - hardcode it instead of using a parameter
json_file_path = r"S:\users\claude.levastre\cityv2\usd\splines_export_from_UE.json"

# Clear any existing geometry
geo.clear()

# Create attributes for position, rotation, and scale
# Note: Houdini automatically creates the 'P' attribute for position
if "rotation" not in geo.pointAttribs():
    geo.addAttrib(hou.attribType.Point, "rotation", hou.Vector3(0, 0, 0))
if "scale" not in geo.pointAttribs():
    geo.addAttrib(hou.attribType.Point, "scale", hou.Vector3(1, 1, 1))

# Also add attributes for spline identification
if "spline_index" not in geo.pointAttribs():
    geo.addAttrib(hou.attribType.Point, "spline_index", 0)
if "actor_name" not in geo.pointAttribs():
    geo.addAttrib(hou.attribType.Point, "actor_name", "")
if "component_name" not in geo.pointAttribs():
    geo.addAttrib(hou.attribType.Point, "component_name", "")

try:
    # Check if file exists
    if not os.path.exists(json_file_path):
        print(f"File not found: {json_file_path}")
        raise Exception(f"File not found: {json_file_path}")
    
    # Load the JSON file
    with open(json_file_path, 'r') as json_file:
        splines_data = json.load(json_file)
    
    # Process each spline
    for spline_index, spline_data in enumerate(splines_data):
        # Get the actor and component names
        actor_name = spline_data["actor_name"]
        component_name = spline_data["component_name"]
        
        # Get the points data
        points_data = spline_data["points"]
        
        # Create points for each point in the spline (without creating polylines)
        for point_data in points_data:
            # Get location data (called "location" in our JSON)
            loc = point_data["location"]
            
            # Create a new point
            pt = geo.createPoint()
            
            # Set the point position (P is the built-in position attribute in Houdini)
            pt.setPosition((loc["x"], loc["y"], loc["z"]))
            
            # Store identification attributes
            pt.setAttribValue("spline_index", spline_index)
            pt.setAttribValue("actor_name", actor_name)
            pt.setAttribValue("component_name", component_name)
            
            # Store rotation if available
            if "rotation" in point_data:
                rotation = point_data["rotation"]
                pt.setAttribValue("rotation", hou.Vector3(rotation["roll"], rotation["pitch"], rotation["yaw"]))
            
            # Store scale if available
            if "scale" in point_data:
                scale = point_data["scale"]
                pt.setAttribValue("scale", hou.Vector3(scale["x"], scale["y"], scale["z"]))
    
    # Print summary
    print(f"Imported points from {len(splines_data)} splines in {json_file_path}")
    
except Exception as e:
    print(f"Error processing JSON file: {str(e)}")