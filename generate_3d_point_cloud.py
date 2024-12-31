import os
import xml.etree.ElementTree as ET
import numpy as np
import pyvista as pv


# Function to parse and print XML file content
def parse_xml_file(filepath):
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
        print(f"Contents of {filepath}:\n")
        ET.dump(root)  # Print content to console
        return root
    except ET.ParseError as e:
        print(f"Error parsing XML file {filepath}: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error for {filepath}: {e}")
        return None


# Function to load raw point cloud data
def load_raw_data(filepath):
    try:
        with open(filepath, "rb") as f:
            data = np.fromfile(f, dtype=np.float32)
        # Replace invalid values with zeros
        data = np.nan_to_num(data, nan=0.0, posinf=0.0, neginf=0.0)
        return data
    except Exception as e:
        print(f"Error loading raw data from {filepath}: {e}")
        return None


# Function to generate and display 3D rendering using PyVista with 1:1 ratio
def display_3d_rendering(data, dimensions, additional_info=None):
    try:
        x_dim, y_dim = dimensions
        if data is None or len(data) != x_dim * y_dim:
            print("Invalid data for 3D rendering.")
            return

        # Reshape data into a grid
        z_values = data.reshape((y_dim, x_dim))
        x_values, y_values = np.meshgrid(np.arange(x_dim), np.arange(y_dim))

        # Convert grid to a PyVista surface
        surface = pv.StructuredGrid(x_values, y_values, z_values)

        # Adjust grid points for 1:1:1 aspect ratio
        surface.points[:, 0] *= 1  # X scaling
        surface.points[:, 1] *= 1  # Y scaling
        surface.points[:, 2] *= 1  # Z scaling

        # Create a plotter
        plotter = pv.Plotter()
        plotter.add_mesh(surface, cmap="viridis")
        plotter.add_axes()
        plotter.show_bounds(grid="front", location="outer", all_edges=True)

        # Display additional info on the plot
        if additional_info:
            plotter.add_text("\n".join(additional_info), position="upper_left", font_size=10, color="white")

        plotter.show()
    except Exception as e:
        print(f"Error displaying 3D rendering: {e}")


# Main function
def main():
    base_dir = "./extracted_files"
    analysis_dir = os.path.join(base_dir, "Analysis")

    # Parse and display all XML files
    files_to_parse = [
        os.path.join(analysis_dir, "criticalDimensions.txt"),
        os.path.join(analysis_dir, "criticalDimensionsProfile.txt"),
        os.path.join(analysis_dir, "display.txt"),
        os.path.join(analysis_dir, "recipe.txt"),
        os.path.join(base_dir, "index.xml"),
        os.path.join(base_dir, "recipe.txt"),
    ]

    for filepath in files_to_parse:
        if os.path.exists(filepath):
            parse_xml_file(filepath)
        else:
            print(f"File not found: {filepath}")

    # Load point cloud raw data
    raw_data_file = os.path.join(base_dir, "LAYER_0.raw")
    raw_data = load_raw_data(raw_data_file)

    # Determine dimensions from index.xml
    index_file = os.path.join(base_dir, "index.xml")
    index_data = parse_xml_file(index_file)
    x_dim, y_dim = None, None
    if index_data is not None:
        general = index_data.find("GENERAL")
        if general is not None:
            x_dim = int(general.find("IMAGE_SIZE_X").text)
            y_dim = int(general.find("IMAGE_SIZE_Y").text)

    if x_dim is None or y_dim is None:
        print("Image dimensions could not be determined from index.xml")
        return

    # Generate and display the 3D rendering
    additional_info = [
        f"Image Size: {x_dim}x{y_dim}",
        f"Raw Data File: {raw_data_file}",
        "Parsed XML Files: " + ", ".join([os.path.basename(f) for f in files_to_parse]),
    ]
    display_3d_rendering(raw_data, (x_dim, y_dim), additional_info)


# Run the program
if __name__ == "__main__":
    main()
