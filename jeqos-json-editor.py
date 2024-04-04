import os
import json
import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog

def validate_path_input(text):
    allowed_chars = set("abcdefghijklmnopqrstuvwxyz0123456789-_/")
    return all(char in allowed_chars for char in text)

def validate_texture_input(text):
    allowed_chars = set("abcdefghijklmnopqrstuvwxyz0123456789-_")
    return all(char in allowed_chars for char in text)

def get_texture_name_placeholder(texture_path):
    parts = texture_path.split("/")
    if len(parts) > 0:
        return parts[-1]
    return ""

def change_textures(window, option, new_value, texture_name, selected_file_name):
    selected_file = f"{selected_file_name}.json"  # Reattach the extension
    if not os.path.isfile(selected_file):
        messagebox.showerror("Error", f"File {selected_file} not found!")
        return

    with open(selected_file, "r") as file:
        json_data = json.load(file)

    if option == "Path":
        if not validate_path_input(new_value):
            error_message = "Invalid characters provided in path."
            display_error_banner(window, error_message)
            return

        for key in json_data["textures"]:
            # Split the existing path by the last occurrence of "/"
            parts = json_data["textures"][key].rsplit("/", 1)
            # Join the new path with the existing file name
            json_data["textures"][key] = new_value + "/" + parts[-1]
        success_message = "Successfully changed texture path(s)."
    elif option == "File Name":
        if not validate_texture_input(new_value):
            error_message = "Invalid characters provided in texture name provided."
            display_error_banner(window, error_message)
            return

        if texture_name is None:
            messagebox.showerror("Error", "Please select a texture first!")
            return
        # Split the existing path and file name
        parts = json_data["textures"][texture_name].rsplit("/", 1)
        # Join the existing path with the new file name
        json_data["textures"][texture_name] = parts[0] + "/" + new_value
        success_message = "Successfully changed texture name."
    else:
        messagebox.showerror("Error", "Invalid option!")
        return

    with open(selected_file, "w") as file:
        json.dump(json_data, file, separators=(",", ":"), ensure_ascii=False)

    success_label = tk.Label(window, text=success_message, bg="#4CAF50", fg="white", padx=6, pady=6) # Adjusted padding
    success_label.place(relx=0.5, rely=1.0, anchor=tk.S, y=0, relwidth=1.0)
    window.after(3000, lambda: fade_out(success_label))  # Fade out after 3 seconds

def change_all_textures(window, new_path):
    for file_name in json_files_listbox.get(0, tk.END):
        change_textures(window, "Path", new_path, None, file_name)

def display_error_banner(window, message):
    error_label = tk.Label(window, text=message, bg="red", fg="white", padx=6, pady=6) # Adjusted padding and color
    error_label.place(relx=0.5, rely=1.0, anchor=tk.S, y=0, relwidth=1.0)
    window.after(3000, lambda: fade_out(error_label))  # Fade out after 3 seconds

def fade_out(widget):
    alpha = widget.winfo_rgb(widget.cget("bg"))  # Get color tuple
    if len(alpha) > 3:  # Check if alpha channel is available
        alpha_value = alpha[3]
        if alpha_value > 0:
            alpha_value -= 1
            widget.config(bg=f'#{alpha[0]:02x}{alpha[1]:02x}{alpha[2]:02x}{alpha_value:02x}')
            widget.after(10, lambda: fade_out(widget))  # Schedule next fade-out step
        else:
            widget.destroy()  # Destroy the widget when completely faded out
    else:
        widget.destroy()  # Destroy the widget if alpha channel is not available

def select_json_file(json_files_listbox, texture_listbox, texture_label, path_entry, current_path_label, current_texture_label, json_files_label):
    selected_file_name = json_files_listbox.get(tk.ACTIVE)
    if not selected_file_name:
        messagebox.showerror("Error", "Please select a JSON file first!")
        return

    selected_file = f"{selected_file_name}.json"  # Reattach the extension
    if not os.path.isfile(selected_file):
        messagebox.showerror("Error", f"File {selected_file} not found!")
        return

    # Update window title
    file_name = os.path.splitext(selected_file)[0]
    json_files_label.config(text=f"Selected: {file_name}")

    # Update texture label
    texture_label.config(text="Select texture:")

    with open(selected_file, "r") as file:
        global json_data  # Ensure json_data is global
        json_data = json.load(file)

    # Populate texture listbox
    texture_listbox.delete(0, tk.END)  # Clear the existing items
    for texture in json_data["textures"]:
        texture_listbox.insert(tk.END, texture)

    # Set placeholder for path entry
    if "textures" in json_data and json_data["textures"]:
        first_texture = next(iter(json_data["textures"].values()))
        current_path = os.path.dirname(first_texture)
        current_path_label.config(text=f"Current: {current_path}") # Update current path label

    # Clear current texture label
    current_texture_label.config(text="")

def main():
    global main_window, json_files_listbox, json_files_label
    main_window = tk.Tk()
    main_window.title("Jeqo's FIE")
    main_window.configure(bg="#2b2b2b")  # Set dark background color

    # Calculate the screen width and height
    screen_width = main_window.winfo_screenwidth()
    screen_height = main_window.winfo_screenheight()

    # Set the window width and height
    window_width = 800
    window_height = 600

    # Calculate the x and y coordinates for the Tk window
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)

    # Set the position of the window
    main_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    frame = tk.Frame(main_window, bg="#2b2b2b", padx=30, pady=30)  # Set dark background color and padding
    frame.pack()

    json_files_label = tk.Label(frame, text="Select JSON File:", bg="#2b2b2b", fg="white")  # Set dark theme colors
    json_files_label.grid(row=0, column=0, sticky="w", pady=(0, 10))

    json_files_listbox = tk.Listbox(frame, selectmode=tk.SINGLE, width=40, bg="#2b2b2b", fg="white", selectbackground="#007acc")
    json_files_listbox.grid(row=1, column=0, pady=(0, 20), padx=(0, 30), sticky="nsew")
    json_files_listbox.config(yscrollcommand="disable")

    texture_label = tk.Label(frame, text="Select texture:", bg="#2b2b2b", fg="white")  # Set dark theme colors
    texture_label.grid(row=0, column=1, sticky="w", pady=(0, 10), padx=(30, 0))

    texture_listbox = tk.Listbox(frame, selectmode=tk.SINGLE, width=40, bg="#2b2b2b", fg="white", selectbackground="#007acc")
    texture_listbox.grid(row=1, column=1, pady=(0, 20), padx=(30, 0), sticky="nsew")
    texture_listbox.config(yscrollcommand="disable")

    path_label = tk.Label(frame, text="Enter new path:", bg="#2b2b2b", fg="white")  # Set dark theme colors
    path_label.grid(row=2, column=0, sticky="w", pady=(0, 10), padx=(0, 30))

    path_entry = tk.Entry(frame, width=40, bg="#2b2b2b", fg="white", insertbackground="white")  # Set dark theme colors
    path_entry.grid(row=3, column=0, sticky="ew", pady=(0, 10), padx=(0, 30))

    current_path_label = tk.Label(frame, text="", bg="#2b2b2b", fg="white")  # Set dark theme colors
    current_path_label.grid(row=4, column=0, sticky="w", pady=(0, 10), padx=(0, 30))

    texture_name_label = tk.Label(frame, text="", bg="#2b2b2b", fg="white")  # Set dark theme colors
    texture_name_label.grid(row=4, column=1, sticky="w", pady=(0, 10), padx=(30, 0))

    file_name_label = tk.Label(frame, text="Enter new texture name:", bg="#2b2b2b", fg="white")  # Set dark theme colors
    file_name_label.grid(row=2, column=1, sticky="w", pady=(0, 10), padx=(30, 0))

    file_name_entry = tk.Entry(frame, width=40, bg="#2b2b2b", fg="white", insertbackground="white")  # Set dark theme colors
    file_name_entry.grid(row=3, column=1, sticky="ew", pady=(0, 10), padx=(30, 0))

    def on_json_select(event):
        select_json_file(json_files_listbox, texture_listbox, texture_label, path_entry, current_path_label, texture_name_label, json_files_label)

    json_files_listbox.bind("<ButtonRelease-1>", on_json_select)

    def on_texture_select(event):
        selected_texture = texture_listbox.get(tk.ACTIVE)
        if selected_texture:
            texture_name_placeholder = get_texture_name_placeholder(json_data["textures"][selected_texture])
            texture_name_label.config(text=f"Current: {texture_name_placeholder}")

    texture_listbox.bind("<ButtonRelease-1>", on_texture_select)

    change_path_button = tk.Button(frame, text="Change Path", command=lambda: change_textures(main_window, "Path", path_entry.get(), None, json_files_listbox.get(tk.ACTIVE)), bg="#d3d3d3", fg="black")  # Neutral colors
    change_path_button.grid(row=5, column=0, sticky="ew", pady=(10, 20), padx=(0, 30))

    change_all_button = tk.Button(frame, text="Change All", command=lambda: change_all_textures(main_window, path_entry.get()), bg="#d3d3d3", fg="black")  # Neutral colors
    change_all_button.grid(row=6, column=0, sticky="ew", pady=(10, 20), padx=(0, 30))

    change_name_button = tk.Button(frame, text="Change Texture Name", command=lambda: change_textures(main_window, "File Name", file_name_entry.get(), texture_listbox.get(tk.ACTIVE), json_files_listbox.get(tk.ACTIVE)), bg="#d3d3d3", fg="black")  # Neutral colors
    change_name_button.grid(row=5, column=1, sticky="ew", pady=(10, 20), padx=(30, 0))

    # Populate JSON file listbox
    script_dir = os.path.dirname(os.path.realpath(__file__))
    for file in os.listdir(script_dir):
        if file.endswith(".json"):
            file_name = os.path.splitext(file)[0]  # Get file name without extension
            json_files_listbox.insert(tk.END, file_name)

    main_window.mainloop()

if __name__ == "__main__":
    main()
