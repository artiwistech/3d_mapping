import zipfile
import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
import xml.etree.ElementTree as ET
import numpy as np
import pyvista as pv


# Function to extract the .plux file
def extract_zip():
    plux_file = entry_file_path.get()

    if not os.path.isfile(plux_file):
        messagebox.showerror("Error", "Please enter a valid file path!")
        return

    # Get the base name of the .plux file for renaming extracted_files
    base_name = os.path.splitext(os.path.basename(plux_file))[0]
    file_dir = os.path.dirname(plux_file)
    output_folder = os.path.join(file_dir, f"{base_name}_extracted_files")
    os.makedirs(output_folder, exist_ok=True)

    try:
        with zipfile.ZipFile(plux_file, 'r') as zf:
            zf.extractall(output_folder)
        messagebox.showinfo("Success", f"Extraction completed! Files have been extracted to:\n{output_folder}")
        return output_folder
    except zipfile.BadZipFile:
        messagebox.showerror("Error", "The selected file is not a valid compressed file!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during extraction:\n{str(e)}")
    return None


# Function to parse XML file
def parse_xml_file(filepath):
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
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
        data = np.nan_to_num(data, nan=0.0, posinf=0.0, neginf=0.0)
        return data
    except Exception as e:
        print(f"Error loading raw data from {filepath}: {e}")
        return None


# Function to display 3D rendering with adjustable color range
def display_3d_rendering(base_dir, color_by_height):
    analysis_dir = os.path.join(base_dir, "Analysis")

    # Load raw data
    raw_data_file = os.path.join(base_dir, "LAYER_0.raw")
    raw_data = load_raw_data(raw_data_file)

    # Get dimensions from index.xml
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

    # Reshape data
    z_values = raw_data.reshape((y_dim, x_dim))
    x_values, y_values = np.meshgrid(np.arange(x_dim), np.arange(y_dim))
    x_values = x_values.astype(float)
    y_values = y_values.astype(float)
    z_values = z_values.astype(float)

    # Create PyVista surface
    surface = pv.StructuredGrid(x_values, y_values, z_values)

    # Ensure correct mapping for color
    surface["Elevation"] = z_values.ravel()

    # Create plotter
    plotter = pv.Plotter()
    plotter.add_mesh(surface, scalars="Elevation", cmap="rainbow", clim=[z_values.min(), z_values.max()])
    plotter.add_axes()
    plotter.show_bounds(grid="front", location="outer", all_edges=True)

    # Create sliders for dynamic color adjustment
    def update_color_range(value):
        new_min = slider_min.GetValue()
        new_max = slider_max.GetValue()
        plotter.update_scalar_bar_range([new_min, new_max])
        surface["Elevation"] = np.clip(surface["Elevation"], new_min, new_max)
        plotter.render()

    slider_min = plotter.add_slider_widget(
        callback=lambda value: update_color_range(value),
        rng=[z_values.min(), z_values.max()],
        value=z_values.min(),
        title="Min Elevation",
        pointa=(0.1, 0.1),
        pointb=(0.4, 0.1),
    )

    slider_max = plotter.add_slider_widget(
        callback=lambda value: update_color_range(value),
        rng=[z_values.min(), z_values.max()],
        value=z_values.max(),
        title="Max Elevation",
        pointa=(0.6, 0.1),
        pointb=(0.9, 0.1),
    )

    # Callback for cleaning up files after window is closed
    def on_close():
        try:
            shutil.rmtree(base_dir)
            print(f"Deleted temporary files: {base_dir}")
        except Exception as e:
            print(f"Error deleting temporary files: {e}")

    plotter.close_callback = on_close  # Bind the callback
    plotter.show()


# Function to handle the display button
def handle_display():
    plux_file = entry_file_path.get()
    if not os.path.isfile(plux_file):
        messagebox.showerror("Error", "Please select a valid PLUX file and extract it first!")
        return

    # Get the base name for the extracted directory
    base_name = os.path.splitext(os.path.basename(plux_file))[0]
    extracted_dir = os.path.join(os.path.dirname(plux_file), f"{base_name}_extracted_files")

    if not os.path.exists(extracted_dir):
        messagebox.showerror("Error", "Extraction folder does not exist! Please extract the file first.")
        return

    # Check if height coloring is enabled
    color_by_height = height_color_var.get()
    display_3d_rendering(extracted_dir, color_by_height)


# Function to browse for the .plux file
def browse_file():
    file_path = filedialog.askopenfilename(title="Select PLUX File", filetypes=[("PLUX Files", "*.plux"), ("All Files", "*.*")])
    if file_path:
        entry_file_path.delete(0, tk.END)
        entry_file_path.insert(0, file_path)


# Create UI
root = tk.Tk()
root.title("PLUX Processing Tool")

# Input file path
frame = tk.Frame(root)
frame.pack(pady=10, padx=10)

label = tk.Label(frame, text="File Path:")
label.grid(row=0, column=0, padx=5, pady=5)

entry_file_path = tk.Entry(frame, width=50)
entry_file_path.grid(row=0, column=1, padx=5, pady=5)

browse_button = tk.Button(frame, text="Browse", command=browse_file)
browse_button.grid(row=0, column=2, padx=5, pady=5)

# Extract button
extract_button = tk.Button(root, text="Extract", command=extract_zip)
extract_button.pack(pady=10)

# Display options
height_color_var = tk.BooleanVar(value=True)
height_color_checkbox = tk.Checkbutton(root, text="Color by Height (Rainbow)", variable=height_color_var)
height_color_checkbox.pack(pady=5)

# Display button
display_button = tk.Button(root, text="Display 3D Rendering", command=handle_display)
display_button.pack(pady=10)

# Run the UI
root.mainloop()
