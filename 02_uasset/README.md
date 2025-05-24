# Unreal Engine Widget Blueprint

This directory will contain the Unreal Engine Widget Blueprint that provides a user-friendly interface for the Undini Framework.

## Widget Features

The widget blueprint will include:

- Text input fields for configuring paths and settings
  - Houdini installation path
  - Iteration number
  - Custom input/output directories
  
- Buttons for executing pipeline steps:
  - Export Splines to JSON
  - Export GenZone Meshes
  - Run Houdini PCG Generation
  - Reimport CSV Data
  - Create PCG Graph
  - Run Houdini Sidewalks & Roads Generation
  - Reimport Static Meshes
  - Add Sidewalks & Roads to Level
  - Run Full Pipeline
  
- Status indicators and log output

## Installation Instructions

1. Copy the `.uasset` file from this directory to your Unreal Engine project
2. Place it in your project's Content folder (e.g., `/Game/YourProject/UI/`)
3. Open the widget in your Unreal Engine project
4. Configure the paths and settings
5. Use the buttons to run the pipeline steps

## Development Notes

When creating the widget blueprint:
- Use the scripts from the `01_Scripts` directory
- Reference the scripts using relative paths from the project
- Provide clear labels and tooltips for all inputs
- Include error handling and status feedback
