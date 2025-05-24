"""
Houdini Spline Import Script

This script imports spline data from a JSON file exported from Unreal Engine into Houdini.
It creates points with position, rotation, scale, and identification attributes.

The script is designed to be used within a Houdini Python SOP node.
"""

# Get the current node and its geometry
node = hou.pwd()
geo = node.geometry()

# Import necessary modules
import json
import os

# Define the workspace root and iteration number
iteration_number = 0  # Default value, can be overridden by Python node parameter

# Get the JSON file path based on the iteration number
WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(hou.hipFile.path()), '..', '..'))
JSON_DIRECTORY = os.path.join(WORKSPACE_ROOT, 'Exports', 'SplineExports')
json_file_path = os.path.join(JSON_DIRECTORY, f'splines_export_from_UE_{iteration_number}.json')

# Clear any existing geometry to start fresh
print(f"🧹 Clearing existing geometry...")
geo.clear()

# Create attributes for position, rotation, and scale
print(f"✨ Setting up point attributes...")
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
    # Check if the JSON file exists
    if not os.path.exists(json_file_path):
        print(f"❌ Oh no! I couldn't find the spline data file at: {json_file_path}")
        print(f"💡 Tip: Make sure you've exported splines from Unreal Engine first using the 000_export_splines_as_json.py script.")
        raise Exception(f"File not found: {json_file_path}")
    
    # Load the JSON file
    print(f"📂 Loading spline data from: {json_file_path}")
    with open(json_file_path, 'r') as json_file:
        splines_data = json.load(json_file)
    
    # Process each spline
    print(f"🔄 Found {len(splines_data)} splines to import...")
    point_count = 0
    
    for spline_index, spline_data in enumerate(splines_data):
        # Get the actor and component names for identification
        actor_name = spline_data["actor_name"]
        component_name = spline_data["component_name"]
        
        # Get the points data for this spline
        points_data = spline_data["points"]
        spline_point_count = len(points_data)
        point_count += spline_point_count
        
        print(f"  🛣️ Importing spline {spline_index+1}/{len(splines_data)}: '{actor_name}' with {spline_point_count} points")
        
        # Create points for each point in the spline
        for point_data in points_data:
            # Extract location data (called "location" in our JSON)
            loc = point_data["location"]
            
            # Create a new point in the geometry
            pt = geo.createPoint()
            
            # Set the point position (P is the built-in position attribute in Houdini)
            pt.setPosition((loc["x"], loc["y"], loc["z"]))
            
            # Store identification attributes for later processing
            pt.setAttribValue("spline_index", spline_index)
            pt.setAttribValue("actor_name", actor_name)
            pt.setAttribValue("component_name", component_name)
            
            # Store rotation if available in the data
            if "rotation" in point_data:
                rotation = point_data["rotation"]
                pt.setAttribValue("rotation", hou.Vector3(rotation["roll"], rotation["pitch"], rotation["yaw"]))
            
            # Store scale if available in the data
            if "scale" in point_data:
                scale = point_data["scale"]
                pt.setAttribValue("scale", hou.Vector3(scale["x"], scale["y"], scale["z"]))
    
    # Print a friendly summary
    print(f"\n✅ Success! Imported {point_count} points from {len(splines_data)} splines")
    print(f"🎯 Data source: {json_file_path}")
    print(f"🧩 Iteration: {iteration_number}")
    
except Exception as e:
    print(f"\n❌ Oops! Something went wrong while processing the spline data:")
    print(f"   {str(e)}")
    print(f"\n💡 Troubleshooting tips:")
    print(f"   - Check if the JSON file exists and has the correct format")
    print(f"   - Verify that the iteration number is correct")
    print(f"   - Make sure the Unreal Engine export was successful")