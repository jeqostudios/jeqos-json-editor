import os
import json
import tkinter as tk
from tkinter import ttk
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

def change_selected_texture_name():
    selected_items = texture_treeview.selection()
    if not selected_items:
        display_error_banner(main_window, "No texture selected.")
        return

    selected_texture_name = texture_treeview.item(selected_items[0], "text")
    selected_file_items = json_files_treeview.selection()
    if not selected_file_items:
        display_error_banner(main_window, "No JSON file selected.")
        return

    selected_file_name = json_files_treeview.item(selected_file_items[0], "text")
    new_texture_name = file_name_entry.get()

    if not new_texture_name:
        display_error_banner(main_window, "Invalid new texture name provided.")
        return

    change_textures(main_window, "Texture Name", new_texture_name, selected_texture_name, selected_file_name)

    # Update the texture name in the texture treeview
    selected_texture_variable = selected_texture_name.split()[0]  # Extract the texture variable
    new_texture_display_name = f"{selected_texture_variable} ({new_texture_name})"
    texture_treeview.item(selected_items[0], text=new_texture_display_name)

    # Update the second current label with the new value
    current_label_2.config(text=f"Current: {new_texture_name}")

def change_textures(window, option, new_value, texture_name, selected_file_name):
    selected_file = f"{selected_file_name}.json"  # Reattach the extension
    script_dir = os.path.dirname(os.path.realpath(__file__))
    selected_file_path = os.path.join(script_dir, selected_file)  # Construct the full file path

    success_message = ""  # Define success_message here

    if not os.path.isfile(selected_file_path):
        display_error_banner(main_window, f"File '{selected_file}' not found!")
        return

    with open(selected_file_path, "r") as file:
        json_data = json.load(file)

    if option == "Path":
        # Update the common prefix for all textures in the JSON data
        for texture_name, texture_path in json_data.get("textures", {}).items():
            # Find the common prefix up to the last "/"
            last_slash_index = texture_path.rfind("/")
            if last_slash_index != -1:
                common_prefix = texture_path[:last_slash_index]  # Exclude the last "/"
                updated_texture_path = f"{new_value}{texture_path[last_slash_index:]}"
                json_data["textures"][texture_name] = updated_texture_path
            else:
                # If no "/" found, update the entire texture path
                json_data["textures"][texture_name] = f"{new_value}/{texture_path}"
        success_message = "Successfully changed path for all textures."
    elif option == "File Name":
        # Implementation for changing file name remains the same
        pass
    elif option == "Texture Name":
        if not validate_texture_input(new_value):
            error_message = "Texture name contains invalid characters."
            display_error_banner(window, error_message)
            return

        if not texture_name:
            display_error_banner(main_window, "No texture was selected.")
            return

        # Extract the texture variable by the first parameter of the selected texture
        selected_texture_variable = texture_name.split()[0]
        
        if selected_texture_variable in json_data["textures"]:
            # Get the texture path
            texture_path = json_data["textures"][selected_texture_variable]
            
            # Extract the texture name from the path
            last_slash_index = texture_path.rfind("/")
            if last_slash_index != -1:
                old_texture_name = texture_path[last_slash_index + 1:]
                new_texture_path = texture_path[:last_slash_index + 1] + new_value
                json_data["textures"][selected_texture_variable] = new_texture_path
                success_message = "Successfully changed texture name."
            else:
                display_error_banner(main_window, "Texture name cannot be changed. Invalid texture path.")
                return
        else:
            display_error_banner(main_window, f"Selected texture variable '{selected_texture_variable}' not found in JSON file.")
            return
    else:
        display_error_banner(main_window, "Invalid option provided.")
        return

    with open(selected_file_path, "w") as file:
        json.dump(json_data, file, separators=(",", ":"), ensure_ascii=False)

    success_label = tk.Label(window, text=success_message, bg="#4CAF50", fg="white", padx=6, pady=6)
    success_label.place(relx=0.5, rely=1.0, anchor=tk.S, y=0, relwidth=1.0)
    window.after(3000, lambda: fade_out(success_label))  # Fade out after 3 seconds

def change_all_textures(window, new_path):
    if not new_path:
        display_error_banner(window, "Invalid new path provided.")
        return

    # Check if only a single "/" is provided
    if new_path == "/":
        display_error_banner(window, "Please provide a valid path.")
        return

    # Remove leading and trailing "/" characters from the new path
    new_path = new_path.strip("/")
    
    for item in json_files_treeview.get_children():
        selected_file_name = json_files_treeview.item(item, "text")
        change_textures(window, "Path", new_path, None, selected_file_name)

    # Update the second current label with the new value
    current_label.config(text=f"Current: {new_path}")

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

def select_json_file(event):
    global current_label  # Ensure current_label is accessed globally

    selected_items = json_files_treeview.selection()
    if not selected_items:
        display_error_banner(main_window, "No JSON file selected.")
        return

    selected_item = selected_items[0]
    selected_file_name = json_files_treeview.item(selected_item, "text")
    if not selected_file_name:
        display_error_banner(main_window, "No JSON file selected.")
        return

    selected_file = f"{selected_file_name}.json"  # Reattach the extension
    script_dir = os.path.dirname(os.path.realpath(__file__))
    selected_file_path = os.path.join(script_dir, selected_file)  # Construct the full file path

    if not os.path.isfile(selected_file_path):
        display_error_banner(main_window, f"File '{selected_file}' not found.")
        return

    # Update window title
    file_name = os.path.splitext(selected_file)[0]

    with open(selected_file_path, "r") as file:
        global json_data  # Ensure json_data is global
        json_data = json.load(file)

    # Populate texture listbox
    texture_treeview.delete(*texture_treeview.get_children())  # Clear the existing items
    for texture_name in json_data.get("textures", {}):
        texture_path = json_data["textures"][texture_name]
        texture_name_placeholder = get_texture_name_placeholder(texture_path)
        texture_treeview.insert("", "end", text=f"{texture_name} ({texture_name_placeholder})")

    # Extract the full path up until the last "/"
    first_texture_path = ""
    if json_data.get("textures"):
        first_texture_path = next(iter(json_data["textures"].values()))
        last_slash_index = first_texture_path.rfind("/")
        if last_slash_index != -1:
            first_texture_path = first_texture_path[:last_slash_index]

    # Update current label with the path of the first texture variable
    current_label.config(text=f"Current: {first_texture_path}")

    # Update banner
    banner_label.config(text=f"Selected: {file_name}")

def select_texture(event):
    selected_items = texture_treeview.selection()
    if not selected_items:
        return

    selected_texture_item = texture_treeview.item(selected_items[0], "text")
    # Extract the texture name from the selected item
    selected_texture_name = selected_texture_item.split(" ")[0]

    # Extract the texture variable value
    texture_value = json_data["textures"][selected_texture_name]

    # Extract the texture name from the texture path
    texture_name = texture_value.split("/")[-1]

    # Update the second current label with the texture name
    current_label_2.config(text=f"Current: {texture_name}")

def on_title_bar_drag(event):
    x = main_window.winfo_pointerx() - main_window._offsetx
    y = main_window.winfo_pointery() - main_window._offsety
    main_window.geometry(f"+{x}+{y}")

def on_title_bar_drag_start(event):
    main_window._offsetx = event.x
    main_window._offsety = event.y

def remove_texture(remove_texture_button):
    def confirm_removal():
        selected_texture_item = texture_treeview.item(selected_items[0], "text")
        selected_texture_name = selected_texture_item.split(" ")[0]

        selected_file_items = json_files_treeview.selection()
        if not selected_file_items:
            display_error_banner(main_window, "No JSON file selected.")
            return

        selected_file_name = json_files_treeview.item(selected_file_items[0], "text")
        selected_file = f"{selected_file_name}.json"  # Reattach the extension

        selected_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), selected_file))

        if not os.path.isfile(selected_file_path):
            display_error_banner(main_window, f"File {selected_file_path} not found!")
            return

        with open(selected_file_path, "r") as file:
            json_data = json.load(file)

        if selected_texture_name in json_data.get("textures", {}):
            del json_data["textures"][selected_texture_name]
            success_message = f"Texture successfully removed: {selected_texture_name}"
            with open(selected_file_path, "w") as file:
                json.dump(json_data, file, separators=(",", ":"), ensure_ascii=False)

            # Remove the selected item from the texture treeview
            texture_treeview.delete(selected_items)

            success_banner = tk.Label(main_window, text=success_message, bg="#4CAF50", fg="white", padx=6, pady=6)
            success_banner.place(relx=0, rely=1.0, anchor=tk.SW, y=0, relwidth=1.0)
            main_window.after(3000, lambda: success_banner.destroy())  # Remove banner after 3 seconds
        else:
            display_error_banner(main_window, f"Texture '{selected_texture_name}' not found in JSON file!")

    selected_items = texture_treeview.selection()
    if not selected_items:
        display_error_banner(main_window, "No texture selected.")
        return

    if remove_texture_button.cget("bg") == "#d90b20":
        confirm_removal()
        remove_texture_button.config(bg="#333", text="Remove Texture")
    else:
        remove_texture_button.config(bg="#d90b20", text="Are You Sure?")
        main_window.after(3000, lambda: remove_texture_button.config(bg="#333", text="Remove Texture"))

def change_path():
    selected_items = json_files_treeview.selection()
    if not selected_items:
        display_error_banner(main_window, "No JSON file selected.")
        return

    selected_file_name = json_files_treeview.item(selected_items[0], "text")
    new_path = path_entry.get()
    
    # Check if only a single "/" is provided
    if new_path == "/":
        display_error_banner(main_window, "Please provide a valid path.")
        return

    if not new_path:
        display_error_banner(main_window, "Invalid new path provided.")
        return

    # Remove leading and trailing "/" characters from the new path
    new_path = new_path.strip("/")

    # Check if the JSON file has any texture entries
    with open(f"{selected_file_name}.json", "r") as file:
        json_data = json.load(file)
        if not json_data.get("textures"):
            display_error_banner(main_window, "JSON file does not have any textures.")
            return

    change_textures(main_window, "Path", new_path, None, selected_file_name)
    
    # Update the second current label with the new value
    current_label.config(text=f"Current: {new_path}")

def refresh_function():
    # Clear the existing items in the JSON treeview
    json_files_treeview.delete(*json_files_treeview.get_children())

    # Repopulate the JSON treeview with current JSON files in the directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    for file in os.listdir(script_dir):
        if file.endswith(".json"):
            file_name = os.path.splitext(file)[0]  # Get file name without extension
            json_files_treeview.insert("", "end", text=file_name)
    
    # Reset the selected banner
    banner_label.config(text="")
    
    # Reset the current labels
    current_label.config(text="")
    current_label_2.config(text="")
    
    # Display success banner
    display_info_banner(main_window, "JSON file list refreshed.")

def display_success_banner(window, message):
    success_label = tk.Label(window, text=message, bg="#4CAF50", fg="white", padx=6, pady=6)
    success_label.place(relx=0.5, rely=1.0, anchor=tk.S, y=0, relwidth=1.0)
    window.after(3000, lambda: fade_out(success_label))  # Fade out after 3 seconds

def display_error_banner(window, message):
    error_label = tk.Label(window, text=message, bg="#d90b20", fg="white", padx=6, pady=6)
    error_label.place(relx=0.5, rely=1.0, anchor=tk.S, y=0, relwidth=1.0)
    window.after(3000, lambda: fade_out(error_label))  # Fade out after 3 seconds

def display_info_banner(window, message):
    info_label = tk.Label(window, text=message, bg="#0b80d9", fg="white", padx=6, pady=6)
    info_label.place(relx=0.5, rely=1.0, anchor=tk.S, y=0, relwidth=1.0)
    window.after(1500, lambda: fade_out(info_label))  # Fade out after 3 seconds

def display_selected_banner(window, selected_file_name):
    selected_banner = tk.Label(window, text=f"Selected: {selected_file_name}", bg="#222", fg="white", padx=6, pady=6)
    selected_banner.place(relx=0.5, rely=1.0, anchor=tk.S, y=0, relwidth=1.0)
    window.after(3000, lambda: fade_out(selected_banner))  # Fade out after 3 seconds

def on_hover_close(event):
    if close_button:
        close_button.config(bg="#d90b20")

close_button = None

def main():
    global main_window, json_files_treeview, texture_treeview, path_entry, banner_label, file_name_entry, frame, current_label, current_label_2

    main_window = tk.Tk()
    main_window.title("Jeqo's JSON Editor")
    main_window.configure(bg="#000")
    main_window.overrideredirect(True)  # Hide default title bar

    # Calculate the position of the window to center it on the screen
    screen_width = main_window.winfo_screenwidth()
    screen_height = main_window.winfo_screenheight()
    window_width = 605
    window_height = 605
    x_position = (screen_width - window_width) // 2
    y_position = (screen_height - window_height) // 2
    main_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

    # Create custom title bar
    title_bar = tk.Frame(main_window, bg="#222", relief="raised", bd=0)
    title_label = tk.Label(title_bar, text="Jeqo's JSON Editor (JJE)", bg="#222", fg="white", padx=6, pady=6)
    title_bar.pack(fill="x")
    title_label.pack(side="left")
    close_button = tk.Button(title_bar, text="X", command=main_window.quit, bg="#222", fg="white", relief="flat", padx=12, pady=6, activebackground="#d90b20", activeforeground="white", font=("Arial", 10, "bold"), borderwidth=0)
    close_button.pack(side="right")
    
    # Add hover effect to the close button
    close_button.bind("<Enter>", lambda event: close_button.config(bg="#d90b20"))
    close_button.bind("<Leave>", lambda event: close_button.config(bg="#222"))

    # Event handlers for dragging the window
    title_bar.bind("<ButtonPress-1>", on_title_bar_drag_start)
    title_bar.bind("<B1-Motion>", on_title_bar_drag)

    frame = tk.Frame(main_window, bg="#111", padx=30, pady=30)
    frame.pack(expand=True, fill="both")

    banner_label = tk.Label(main_window, text="", bg="#222", fg="white", padx=6, pady=6)  # Banner label
    banner_label.pack(fill="x")

    # Add "Current:" label
    current_label = tk.Label(frame, text="", bg="#111", fg="white")  # First current label
    current_label.grid(row=6, column=0, sticky="w", pady=(0, 10), padx=(0, 30))

    current_label_2 = tk.Label(frame, text="", bg="#111", fg="white")  # Second current label
    current_label_2.grid(row=6, column=1, sticky="w", pady=(0, 10), padx=(30, 0))

    json_files_label = tk.Label(frame, text="Select JSON File:", bg="#111", fg="white")
    json_files_label.grid(row=0, column=0, sticky="w", pady=(0, 10))

    # Define custom style for the treeviews
    treeview_style = ttk.Style()
    treeview_style.configure("Custom.Treeview", background="#fff", fieldbackground="#fff", foreground="black", bordercolor="#fff", highlightcolor="#fff")

    json_files_treeview = ttk.Treeview(frame, selectmode="browse", columns=("name",), show="tree", style="Custom.Treeview")
    json_files_treeview.grid(row=1, column=0, pady=(0, 10), padx=(0, 30), sticky="nsew")

    json_files_scrollbar = ttk.Scrollbar(frame, orient="vertical", command=json_files_treeview.yview)
    json_files_scrollbar.grid(row=1, column=0, pady=(1, 21), padx=(196, 0), sticky="ns")
    json_files_treeview.configure(yscrollcommand=json_files_scrollbar.set)
    
    # Hide other columns
    json_files_treeview.heading("#1", text="", anchor=tk.W)
    json_files_treeview.column("#1", width=0, stretch=tk.NO)

    texture_label = tk.Label(frame, text="Select texture:", bg="#111", fg="white")
    texture_label.grid(row=0, column=1, sticky="w", pady=(0, 10), padx=(30, 0))

    # Create the texture treeview
    texture_treeview = ttk.Treeview(frame, selectmode="browse", columns=("name",), show="tree", style="Custom.Treeview")
    texture_treeview.grid(row=1, column=1, pady=(0, 10), padx=(30, 0), sticky="nsew")

    texture_scrollbar = ttk.Scrollbar(frame, orient="vertical", command=texture_treeview.yview)
    texture_scrollbar.grid(row=1, column=1, pady=(1, 21), padx=(256, 0), sticky="ns")
    texture_treeview.configure(yscrollcommand=texture_scrollbar.set)

    # Hide other columns
    texture_treeview.heading("#1", text="", anchor=tk.W)
    texture_treeview.column("#1", width=0, stretch=tk.NO)

    texture_treeview.bind("<<TreeviewSelect>>", select_texture)

    path_label = tk.Label(frame, text="Enter new path:", bg="#111", fg="white")
    path_label.grid(row=4, column=0, sticky="w", pady=(0, 10), padx=(0, 30))

    path_entry = tk.Entry(frame, width=40, bg="#333", fg="white", insertbackground="white", relief=tk.FLAT)
    path_entry.grid(row=5, column=0, sticky="ew", pady=(0, 0), padx=(0, 30))

    file_name_label = tk.Label(frame, text="Enter new texture name:", bg="#111", fg="white")
    file_name_label.grid(row=4, column=1, sticky="w", pady=(0, 10), padx=(30, 0))

    file_name_entry = tk.Entry(frame, width=40, bg="#333", fg="white", insertbackground="white", relief=tk.FLAT)
    file_name_entry.grid(row=5, column=1, sticky="ew", pady=(0, 0), padx=(30, 0))

    json_files_treeview.bind("<<TreeviewSelect>>", select_json_file)

    refresh_button = tk.Button(frame, text="Refresh", command=refresh_function, bg="#333", fg="white", activebackground="#444", activeforeground="white", relief=tk.FLAT)
    refresh_button.grid(row=3, column=0, sticky="ew", pady=(0, 30), padx=(0, 30))

    change_path_button = tk.Button(frame, text="Change Path", command=change_path, bg="#333", fg="white", activebackground="#444", activeforeground="white", relief=tk.FLAT)
    change_path_button.grid(row=7, column=0, sticky="ew", pady=(10, 10), padx=(0, 30))

    change_all_button = tk.Button(frame, text="Change All Paths", command=lambda: change_all_textures(main_window, path_entry.get()), bg="#333", fg="white", activebackground="#444", activeforeground="white", relief=tk.FLAT, width=15)
    change_all_button.grid(row=8, column=0, sticky="ew", pady=(0, 0), padx=(0, 30))

    change_texture_button = tk.Button(frame, text="Change Name", command=change_selected_texture_name, bg="#333", fg="white", activebackground="#444", activeforeground="white", relief=tk.FLAT)
    change_texture_button.grid(row=7, column=1, sticky="ew", pady=(10, 10), padx=(30, 0))

    remove_texture_button = tk.Button(frame, text="Remove Texture", bg="#333", fg="white", activebackground="#444", activeforeground="white", relief=tk.FLAT, width=15)
    remove_texture_button.grid(row=8, column=1, sticky="ew", pady=(0, 0), padx=(30, 0))
    remove_texture_button.config(command=lambda: remove_texture(remove_texture_button))

    # Populate JSON file treeview
    script_dir = os.path.dirname(os.path.abspath(__file__))
    for file in os.listdir(script_dir):
        if file.endswith(".json"):
            file_name = os.path.splitext(file)[0]  # Get file name without extension
            json_files_treeview.insert("", "end", text=file_name)

    main_window.mainloop()

if __name__ == "__main__":
    main()
