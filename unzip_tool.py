import zipfile
import os
import tkinter as tk
from tkinter import filedialog, messagebox

def extract_zip():
    # Get the file path input by the user
    plux_file = entry_file_path.get()
    
    if not os.path.isfile(plux_file):
        messagebox.showerror("Error", "Please enter a valid file path!")
        return
    
    # Get the directory of the file and create an extraction folder
    file_dir = os.path.dirname(plux_file)
    output_folder = os.path.join(file_dir, "extracted_files")
    os.makedirs(output_folder, exist_ok=True)
    
    try:
        # Attempt to extract the file regardless of the extension
        with zipfile.ZipFile(plux_file, 'r') as zf:
            zf.extractall(output_folder)
        messagebox.showinfo("Success", f"Extraction completed! Files have been extracted to:\n{output_folder}")
    except zipfile.BadZipFile:
        messagebox.showerror("Error", "The selected file is not a valid compressed file!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during extraction:\n{str(e)}")

def browse_file():
    # Open a file dialog to select a file
    file_path = filedialog.askopenfilename(title="Select PLUX File", filetypes=[("PLUX Files", "*.plux"), ("All Files", "*.*")])
    if file_path:
        entry_file_path.delete(0, tk.END)
        entry_file_path.insert(0, file_path)

# Create the UI
root = tk.Tk()
root.title("PLUX Unzip Tool")

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

# Run the UI
root.mainloop()
