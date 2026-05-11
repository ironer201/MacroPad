import serial
import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sof
import os
import time
import threading
import sys
sys.stdout.reconfigure(encoding='utf-8')

PORT = 'COM8'  # Changed from COM3 to COM8
BAUD = 9600
serial_lock = threading.Lock()
# Add these variables after the existing global variables
heartbeat_running = False
heartbeat_thread = None

# Try to connect to Arduino
try:
    ser = serial.Serial(PORT, BAUD, timeout=0.1)
    time.sleep(2)  # Wait for Arduino to reset
    print(f"✓ Connected to Arduino on {PORT}")
    serial_connected = True
except Exception as e:
    ser = None
    serial_connected = False
    print(f"✗ Failed to connect to Arduino: {e}")

actions = ["VOL_UP", "VOL_DOWN", "MUTE", "PLAY", "COPY", "PASTE", "CUSTOM"]

action_codes = {
    "VOL_UP": 1,
    "VOL_DOWN": 2,
    "MUTE": 3,
    "PLAY": 4,
    "COPY": 5,
    "PASTE": 6
}

default_map = {
    "B1": "VOL_UP",
    "B2": "VOL_DOWN",
    "B3": "MUTE",
    "B4": "PLAY"
}

custom_keys = {}
software_folder_paths = {}

SOFTWARE_FOLDER_CONFIG = "software_folder_config.json"

# Load software/folder configurations
try:
    with open(SOFTWARE_FOLDER_CONFIG, "r") as f:
        software_folder_config = json.load(f)
        software_folder_paths = software_folder_config.get("paths", {})
        print(f"Loaded software/folder config")
except Exception as e:
    print(f"Creating new software/folder config")
    software_folder_paths = {
        "B1": {"type": "software", "path": "", "action": "VOL_UP"},
        "B2": {"type": "software", "path": "", "action": "VOL_DOWN"},
        "B3": {"type": "folder", "path": "", "action": "MUTE"},
        "B4": {"type": "folder", "path": "", "action": "PLAY"}
    }

try:
    with open("config.json", "r") as f:
        data = json.load(f)
        button_map = data.get("buttons", default_map.copy())
        custom_keys = data.get("custom", {})
        print(f"Loaded button config")
except Exception as e:
    print(f"Using default button config")
    button_map = default_map.copy()

root = tk.Tk()
root.title("MacroPad Configurator")
root.geometry("1000x900")

# Create a Notebook
notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True, padx=5, pady=5)

config_tab = ttk.Frame(notebook)
notebook.add(config_tab, text="MacroPad Configuration")

debug_tab = ttk.Frame(notebook)
notebook.add(debug_tab, text="Debug Console")

help_tab = ttk.Frame(notebook)
notebook.add(help_tab, text="Help")

# ========== TAB 1: MACROPAD CONFIGURATION ==========
dropdowns = {}

def open_custom(btn):
    win = tk.Toplevel(root)
    win.title(f"Custom Key Configuration - {btn}")
    win.geometry("450x500")
    win.transient(root)
    win.grab_set()
    
    mods = ["CTRL", "ALT", "SHIFT", "WIN"]
    vars_map = {}
    
    mod_frame = tk.LabelFrame(win, text="Modifier Keys", padx=10, pady=10)
    mod_frame.pack(pady=10, padx=10, fill="x")
    
    for m in mods:
        v = tk.BooleanVar()
        tk.Checkbutton(mod_frame, text=m, variable=v).pack(anchor="w")
        vars_map[m] = v
    
    key_frame = tk.LabelFrame(win, text="Key Selection", padx=10, pady=10)
    key_frame.pack(pady=10, padx=10, fill="x")
    
    tk.Label(key_frame, text="Press keys one after another:").pack()
    
    entry = tk.Entry(key_frame, width=30, font=("Arial", 10))
    entry.pack(pady=5)
    
    tk.Label(key_frame, text="Current sequence:", font=("Arial", 9, "bold")).pack()
    sequence_label = tk.Label(key_frame, text="", font=("Arial", 10), fg="blue")
    sequence_label.pack(pady=5)
    
    special_keys = [
        "Select a key...",
        "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m",
        "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
        "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
        "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12",
        "HOME", "TAB", "PAGEUP", "PAGEDOWN", "PRTSC", "DELETE",
        "END", "INSERT", "ESC", "SPACE", "ENTER", "BACKSPACE"
    ]
    
    key_var = tk.StringVar()
    key_var.set("Select a key...")
    key_dropdown = ttk.Combobox(key_frame, values=special_keys, textvariable=key_var, state="readonly", width=22)
    key_dropdown.pack(pady=5)
    
    pressed_keys = []
    
    def add_key_to_sequence(key):
        if key and key != "Select a key...":
            pressed_keys.append(key)
            sequence_label.config(text=" + ".join(pressed_keys))
            entry.delete(0, tk.END)
            entry.insert(0, "+".join(pressed_keys))
    
    def clear_sequence():
        pressed_keys.clear()
        sequence_label.config(text="")
        entry.delete(0, tk.END)
    
    def on_key_press(event):
        key_name = event.keysym
        special_mapping = {
            "Page_Up": "PAGEUP", "Page_Down": "PAGEDOWN", "Print": "PRTSC",
            "Home": "HOME", "Tab": "TAB", "Delete": "DELETE", "End": "END",
            "Insert": "INSERT", "Escape": "ESC", "space": "SPACE",
            "Return": "ENTER", "BackSpace": "BACKSPACE"
        }
        
        if key_name.startswith("F") and len(key_name) <= 3 and key_name[1:].isdigit():
            pass
        elif key_name in special_mapping:
            key_name = special_mapping[key_name]
        elif len(key_name) == 1 and key_name.isalpha():
            key_name = key_name.lower()
        elif key_name.isdigit():
            pass
        else:
            if key_name in ["Shift_L", "Shift_R", "Control_L", "Control_R", "Alt_L", "Alt_R"]:
                return "break"
            return "break"
        
        add_key_to_sequence(key_name)
        key_var.set(key_name)
        update_preview()
        return "break"
    
    def on_dropdown_select(event):
        selected = key_var.get()
        if selected != "Select a key...":
            add_key_to_sequence(selected)
            update_preview()
    
    key_dropdown.bind("<<ComboboxSelected>>", on_dropdown_select)
    entry.bind("<KeyPress>", on_key_press)
    
    clear_frame = tk.Frame(key_frame)
    clear_frame.pack(pady=5)
    tk.Button(clear_frame, text="Clear Sequence", command=clear_sequence, bg="orange", fg="white", padx=10).pack()
    
    preview_frame = tk.LabelFrame(win, text="Preview", padx=10, pady=10)
    preview_frame.pack(pady=10, padx=10, fill="x")
    preview_label = tk.Label(preview_frame, text="No combo selected", font=("Arial", 11, "bold"), fg="blue")
    preview_label.pack()
    
    def update_preview(*args):
        combo = []
        for m in mods:
            if vars_map[m].get():
                combo.append(m)
        for key in pressed_keys:
            combo.append(key)
        if combo:
            preview_label.config(text=" + ".join(combo))
        else:
            preview_label.config(text="No combo selected")
    
    for var in vars_map.values():
        var.trace_add('write', lambda *args: update_preview())
    
    def save():
        combo = []
        for m in mods:
            if vars_map[m].get():
                combo.append(m)
        for key in pressed_keys:
            combo.append(key)
        
        if not combo:
            messagebox.showwarning("Warning", "Please select at least one key!")
            return
        
        custom_keys[btn] = "+".join(combo)
        dropdowns[btn].set("CUSTOM")
        update_info_labels()
        win.destroy()
    
    def clear_custom():
        if btn in custom_keys:
            del custom_keys[btn]
            dropdowns[btn].set(default_map.get(btn, "VOL_UP"))
            update_info_labels()
            win.destroy()
    
    button_frame = tk.Frame(win)
    button_frame.pack(pady=10)
    tk.Button(button_frame, text="Save", command=save, bg="green", fg="white", padx=20).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Clear", command=clear_custom, bg="red", fg="white", padx=20).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Cancel", command=win.destroy, padx=20).pack(side=tk.LEFT, padx=5)
    
    update_preview()

def open_software_folder_config(btn):
    win = tk.Toplevel(root)
    win.title(f"Software/Folder Configuration - {btn}")
    win.geometry("600x500")
    win.transient(root)
    win.grab_set()
    
    current_type = software_folder_paths.get(btn, {}).get("type", "software")
    current_path = software_folder_paths.get(btn, {}).get("path", "")
    current_action = software_folder_paths.get(btn, {}).get("action", default_map.get(btn, "VOL_UP"))
    
    # Info label
    info_label = tk.Label(win, text="⚡ When Python is RUNNING → Button opens software/folder\n⚡ When Python is CLOSED → Button sends keybinding to Arduino", 
                          font=("Arial", 9, "bold"), fg="blue", wraplength=550)
    info_label.pack(pady=10)
    
    type_frame = tk.LabelFrame(win, text="🐍 When Python IS Running (Open this)", padx=10, pady=10)
    type_frame.pack(pady=10, padx=10, fill="x")
    
    type_var = tk.StringVar(value=current_type)
    tk.Radiobutton(type_frame, text="📱 Open Software (EXE file)", variable=type_var, value="software").pack(anchor="w", pady=5)
    tk.Radiobutton(type_frame, text="📁 Open Folder", variable=type_var, value="folder").pack(anchor="w", pady=5)
    
    path_frame = tk.LabelFrame(win, text="Select Path", padx=10, pady=10)
    path_frame.pack(pady=10, padx=10, fill="x")
    
    path_var = tk.StringVar(value=current_path)
    path_entry = tk.Entry(path_frame, textvariable=path_var, width=55, font=("Arial", 9))
    path_entry.pack(pady=5, padx=5)
    
    def browse_file():
        filename = filedialog.askopenfilename(
            title="Select Software Executable",
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
        )
        if filename:
            path_var.set(filename)
    
    def browse_folder():
        foldername = filedialog.askdirectory(title="Select Folder")
        if foldername:
            path_var.set(foldername)
    
    button_frame = tk.Frame(path_frame)
    button_frame.pack(pady=10)
    tk.Button(button_frame, text="Browse EXE", command=browse_file, bg="#2196F3", fg="white", padx=15).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Browse Folder", command=browse_folder, bg="#FF9800", fg="white", padx=15).pack(side=tk.LEFT, padx=5)
    
    action_frame = tk.LabelFrame(win, text="🔌 When Python IS NOT Running (Arduino Fallback)", padx=10, pady=10)
    action_frame.pack(pady=10, padx=10, fill="x")
    
    action_var = tk.StringVar(value=current_action)
    action_dropdown = ttk.Combobox(action_frame, textvariable=action_var, values=actions, state="readonly", width=20)
    action_dropdown.pack(pady=5)
    tk.Label(action_frame, text="This keybinding works even when Python is closed", 
             font=("Arial", 8), fg="gray").pack()
    
    def save_config():
        new_type = type_var.get()
        new_path = path_var.get()
        new_action = action_var.get()
        
        if new_path and not os.path.exists(new_path):
            result = messagebox.askyesno("Warning", f"Path does not exist!\n{new_path}\n\nSave anyway?")
            if not result:
                return
        
        software_folder_paths[btn] = {
            "type": new_type, 
            "path": new_path,
            "action": new_action
        }
        
        try:
            with open(SOFTWARE_FOLDER_CONFIG, "w") as f:
                json.dump({"paths": software_folder_paths}, f, indent=4)
            
            messagebox.showinfo("Success", f"✅ Configuration saved for {btn}!\n\n"
                                          f"🐍 Python RUNNING: {new_type.upper()}\n"
                                          f"   Path: {new_path}\n\n"
                                          f"🔌 Python CLOSED: {new_action}")
            update_software_folder_labels()
            debug_print(f"Saved config for {btn}")
            win.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {str(e)}")
    
    def clear_config():
        software_folder_paths[btn] = {"type": "software", "path": "", "action": default_map.get(btn, "VOL_UP")}
        try:
            with open(SOFTWARE_FOLDER_CONFIG, "w") as f:
                json.dump({"paths": software_folder_paths}, f, indent=4)
            update_software_folder_labels()
            debug_print(f"Cleared config for {btn}")
            win.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clear: {str(e)}")
    
    save_frame = tk.Frame(win)
    save_frame.pack(pady=20)
    tk.Button(save_frame, text="Save", command=save_config, bg="green", fg="white", padx=20).pack(side=tk.LEFT, padx=10)
    tk.Button(save_frame, text="Clear", command=clear_config, bg="red", fg="white", padx=20).pack(side=tk.LEFT, padx=10)
    tk.Button(save_frame, text="Cancel", command=win.destroy, padx=20).pack(side=tk.LEFT, padx=10)

info_labels = {}
software_folder_labels = {}

def update_info_labels():
    for b in info_labels:
        if b in custom_keys:
            info_labels[b].config(text=f"✓ {custom_keys[b]}", fg="green")
        else:
            info_labels[b].config(text="")

def update_software_folder_labels():
    for b in software_folder_labels:
        config = software_folder_paths.get(b, {})
        if config.get("path") and os.path.exists(config.get("path")):
            path = config.get("path")
            type_icon = "📱" if config.get("type") == "software" else "📁"
            short_path = os.path.basename(path) if len(path) > 30 else path
            software_folder_labels[b].config(text=f"{type_icon} {short_path}", fg="green")
        elif config.get("path"):
            software_folder_labels[b].config(text="⚠ Invalid path", fg="red")
        else:
            software_folder_labels[b].config(text="Not configured", fg="orange")

# Create UI for each button
row = 0
for b in ["B1", "B2", "B3", "B4"]:
    main_frame = tk.LabelFrame(config_tab, text=f"Button {b}", padx=10, pady=10, font=("Arial", 10, "bold"))
    main_frame.grid(row=row, column=0, columnspan=4, padx=10, pady=5, sticky="ew")
    
    # Fallback action (when Python is closed)
    tk.Label(main_frame, text="🔌 Fallback (Python closed):", font=("Arial", 9)).grid(row=0, column=0, padx=5, pady=5, sticky="w")
    fallback_action = software_folder_paths.get(b, {}).get("action", button_map.get(b, "VOL_UP"))
    cb = ttk.Combobox(main_frame, values=actions, state="readonly", width=20, font=("Arial", 10))
    cb.set(fallback_action)
    cb.grid(row=0, column=1, padx=5, pady=5, sticky="w")
    dropdowns[b] = cb
    
    # Custom key configuration
    tk.Label(main_frame, text="⚙ Custom Keys:", font=("Arial", 9)).grid(row=1, column=0, padx=5, pady=5, sticky="w")
    tk.Button(main_frame, text="Configure Custom Keys", command=lambda x=b: open_custom(x), 
              bg="#9C27B0", fg="white", font=("Arial", 9)).grid(row=1, column=1, padx=5, pady=5, sticky="w")
    info_label = tk.Label(main_frame, text="", font=("Arial", 9), fg="green")
    info_label.grid(row=1, column=2, padx=5, pady=5, sticky="w")
    info_labels[b] = info_label
    
    # Software/Folder (when Python is running)
    tk.Label(main_frame, text="🐍 Software/Folder (Python running):", font=("Arial", 9)).grid(row=2, column=0, padx=5, pady=5, sticky="w")
    tk.Button(main_frame, text="📂 Configure", command=lambda x=b: open_software_folder_config(x), 
              bg="#4CAF50", fg="white", font=("Arial", 9)).grid(row=2, column=1, padx=5, pady=5, sticky="w")
    sw_label = tk.Label(main_frame, text="", font=("Arial", 9), fg="green")
    sw_label.grid(row=2, column=2, padx=5, pady=5, sticky="w")
    software_folder_labels[b] = sw_label
    
    row += 1

separator = ttk.Separator(config_tab, orient='horizontal')
separator.grid(row=row, column=0, columnspan=4, sticky="ew", pady=10)
row += 1

update_info_labels()
update_software_folder_labels()

def save_json():
    # Save fallback actions
    for b in dropdowns:
        if b in software_folder_paths:
            software_folder_paths[b]["action"] = dropdowns[b].get()
    
    try:
        # Save button config
        button_config = {}
        for b in dropdowns:
            button_config[b] = dropdowns[b].get()
        
        with open("config.json", "w") as f:
            json.dump({"buttons": button_config, "custom": custom_keys}, f, indent=4)
        
        # Save software/folder config
        with open(SOFTWARE_FOLDER_CONFIG, "w") as f:
            json.dump({"paths": software_folder_paths}, f, indent=4)
        
        messagebox.showinfo("Success", "✅ All configurations saved!")
        update_info_labels()
        debug_print("All configurations saved")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save: {str(e)}")

def upload():
    if not serial_connected or ser is None:
        messagebox.showerror("Error", "❌ Arduino not connected!\nCheck USB connection and COM port.")
        return
    
    data = []
    warnings = []
    
    for b in ["B1", "B2", "B3", "B4"]:
        act = dropdowns[b].get()
        
        if act == "CUSTOM":
            if b in custom_keys and custom_keys[b]:
                data.append("C:" + custom_keys[b])
            else:
                warnings.append(f"{b} set to CUSTOM but no keys configured!")
                data.append(str(action_codes[default_map[b]]))
        else:
            data.append(str(action_codes[act]))
    
    if warnings:
        messagebox.showwarning("Warnings", "\n".join(warnings))
    
    try:
        with serial_lock:
            ser.write(("SET:" + "|".join(data) + "\n").encode())
            time.sleep(0.1)
            response = ser.readline().decode('utf-8', errors='ignore').strip()
        
        messagebox.showinfo("Success", f"✅ Uploaded to Arduino!\n\nSent: {' | '.join(data)}\nArduino response: {response}")
        debug_print(f"Uploaded to Arduino: {' | '.join(data)}")
        debug_print(f"Arduino response: {response}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to upload: {str(e)}")

def refresh_serial():
    global ser, serial_connected

        # Stop existing heartbeat if running
    if heartbeat_running:
        stop_heartbeat()

    try:
        if ser and ser.is_open:
            ser.close()
        ser = serial.Serial(PORT, BAUD, timeout=0.1)
        time.sleep(2)
        serial_connected = True
        status_label.config(text=f"✓ Connected to {PORT}", fg="green")
        debug_print(f"Connected to Arduino on {PORT}")
        
        # Test communication
        with serial_lock:
            ser.write(b"PING\n")
            time.sleep(0.1)
            response = ser.readline().decode('utf-8', errors='ignore').strip()
            debug_print(f"PING response: {response}")
        start_heartbeat()        
        messagebox.showinfo("Success", f"Connected to Arduino on {PORT}")
        start_serial_reader()

    except Exception as e:
        ser = None
        serial_connected = False
        status_label.config(text=f"✗ Not connected to {PORT}", fg="red")
        debug_print(f"Failed to connect: {e}")
        messagebox.showerror("Error", f"Failed to connect: {str(e)}")

# Debug console
debug_text = tk.Text(debug_tab, height=20, width=90, font=("Courier", 9))
debug_text.pack(padx=10, pady=10, fill="both", expand=True)

scrollbar = tk.Scrollbar(debug_text)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
debug_text.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=debug_text.yview)

def debug_print(message):
    timestamp = time.strftime("%H:%M:%S")
    debug_text.insert(tk.END, f"[{timestamp}] {message}\n")
    debug_text.see(tk.END)
    print(message)

def test_open_software_directly():
    """Test opening software/folder for B1"""
    button = "B1"
    config = software_folder_paths.get(button, {})
    if config.get("path") and os.path.exists(config.get("path")):
        debug_print(f"🧪 TEST: Opening {config['path']}")
        if config.get("type") == "software":
            result = sof.launch_software(config["path"])
            if result:
                debug_print(f"✓ Successfully opened software")
                update_launcher_status(f"✓ Opened: {os.path.basename(config['path'])}")
            else:
                debug_print(f"✗ Failed to open")
                update_launcher_status(f"✗ Failed to open", True)
        else:
            result = sof.open_folder(config["path"])
            if result:
                debug_print(f"✓ Successfully opened folder")
                update_launcher_status(f"✓ Opened: {os.path.basename(config['path'])}")
            else:
                debug_print(f"✗ Failed to open")
                update_launcher_status(f"✗ Failed to open", True)
    else:
        debug_print("No valid path configured for B1")
        update_launcher_status("No valid path configured for B1", True)

serial_reader_running = True

def start_serial_reader():
    """Start a thread to read serial data continuously"""
    def read_serial():
        global serial_reader_running
        while serial_reader_running:
            if serial_connected and ser and ser.is_open:
                try:
                    with serial_lock:
                        if ser.in_waiting > 0:
                            line = ser.readline().decode('utf-8', errors='ignore').strip()
                            if line:
                                debug_print(f"📨 Received: {line}")
                                root.after(0, lambda: process_command(line))
                except Exception as e:
                    debug_print(f"Serial read error: {e}")
            time.sleep(0.05)
    
    thread = threading.Thread(target=read_serial, daemon=True)
    thread.start()
    debug_print("Serial reader thread started")

def process_command(command):
    """Process commands from Arduino"""
    debug_print(f"Processing: {command}")
    
    if command.startswith("PRESS:"):
        button = command.split(":")[1]
        debug_print(f"🔘 Button {button} pressed!")
        
        # Check if software/folder is configured for this button
        config = software_folder_paths.get(button, {})
        if config.get("path") and os.path.exists(config.get("path")):
            # Python IS running - open software/folder
            debug_print(f"🐍 Python running - Opening configured item")
            if config.get("type") == "software":
                result = sof.launch_software(config["path"])
                if result:
                    debug_print(f"✓ Opened software: {config['path']}")
                    update_launcher_status(f"✓ Opened: {os.path.basename(config['path'])}")
                else:
                    debug_print(f"✗ Failed to open")
                    update_launcher_status(f"✗ Failed to open", True)
            else:
                result = sof.open_folder(config["path"])
                if result:
                    debug_print(f"✓ Opened folder: {config['path']}")
                    update_launcher_status(f"✓ Opened: {os.path.basename(config['path'])}")
                else:
                    debug_print(f"✗ Failed to open")
                    update_launcher_status(f"✗ Failed to open", True)
        else:
            # No software/folder configured - Arduino handles it
            debug_print(f"🔌 No software/folder configured - Arduino handles keybinding")
            update_launcher_status(f"Button {button}: Using Arduino keybinding")
    
    elif command.startswith("READY"):
        debug_print(f"✓ Arduino is ready")
        update_launcher_status("Arduino connected and ready")
                # Start heartbeat after receiving READY
        if not heartbeat_running:
            start_heartbeat()
    
    elif command.startswith("SET:"):
        debug_print(f"✓ Configuration received by Arduino")

    elif command.startswith("HEARTBEAT:ACK"):
        debug_print(f"✓ Arduino acknowledged heartbeat")

    elif command.startswith("PYTHON:DISCONNECTED"):
        debug_print(f"⚠ Arduino detected Python disconnect")
        update_launcher_status("Heartbeat lost - Arduino LED turned off", True)

def start_heartbeat():
    """Start sending heartbeat signals to Arduino"""
    global heartbeat_running, heartbeat_thread
    
    if heartbeat_thread and heartbeat_thread.is_alive():
        return
    
    heartbeat_running = True
    
    def send_heartbeat():
        global heartbeat_running, serial_connected, ser
        
        # Send initial start signal
        if serial_connected and ser and ser.is_open:
            try:
                with serial_lock:
                    ser.write(b"PYTHON:START\n")
                    time.sleep(0.1)
                    response = ser.readline().decode('utf-8', errors='ignore').strip()
                    debug_print(f"Heartbeat start response: {response}")
            except Exception as e:
                debug_print(f"Failed to send start signal: {e}")
        
        # Continuously send heartbeat every 1.5 seconds
        while heartbeat_running:
            if serial_connected and ser and ser.is_open:
                try:
                    with serial_lock:
                        ser.write(b"HEARTBEAT\n")
                        debug_print("💓 Heartbeat sent")
                except Exception as e:
                    debug_print(f"Heartbeat send error: {e}")
                    serial_connected = False
                    root.after(0, lambda: status_label.config(text=f"✗ Arduino disconnected", fg="red"))
            time.sleep(1.5)  # Send heartbeat every 1.5 seconds (faster than 2s timeout)
        
        # Send stop signal when heartbeat stops
        if serial_connected and ser and ser.is_open:
            try:
                with serial_lock:
                    ser.write(b"PYTHON:STOP\n")
                    debug_print("Sent stop signal to Arduino")
            except Exception as e:
                debug_print(f"Failed to send stop signal: {e}")
    
    heartbeat_thread = threading.Thread(target=send_heartbeat, daemon=True)
    heartbeat_thread.start()
    debug_print("Heartbeat thread started")

def stop_heartbeat():
    """Stop sending heartbeat signals"""
    global heartbeat_running
    heartbeat_running = False
    if heartbeat_thread:
        heartbeat_thread.join(timeout=2)
    debug_print("Heartbeat stopped")


action_frame = tk.Frame(config_tab)
action_frame.grid(row=row, column=0, columnspan=4, pady=20)

tk.Button(action_frame, text="💾 Save Configuration", command=save_json, 
          bg="green", fg="white", padx=20, pady=5, font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=10)
tk.Button(action_frame, text="📤 Upload to Arduino", command=upload, 
          bg="blue", fg="white", padx=20, pady=5, font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=10)
tk.Button(action_frame, text="🔄 Refresh Serial", command=refresh_serial, 
          bg="orange", fg="white", padx=20, pady=5, font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=10)
tk.Button(action_frame, text="🧪 Test B1", command=test_open_software_directly,
          bg="purple", fg="white", padx=20, pady=5, font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=10)

row += 1

status_frame = tk.Frame(config_tab)
status_frame.grid(row=row, column=0, columnspan=4, sticky="ew", pady=10)

if serial_connected:
    status_label = tk.Label(status_frame, text=f"✓ Connected to Arduino on {PORT}", fg="green", font=("Arial", 9))
else:
    status_label = tk.Label(status_frame, text=f"✗ Not connected to Arduino", fg="red", font=("Arial", 9))
status_label.pack()

launcher_status = tk.Label(status_frame, text="Ready - Configure buttons above", font=("Arial", 9), fg="blue")
launcher_status.pack()

def update_launcher_status(message, is_error=False):
    launcher_status.config(text=message, fg="red" if is_error else "blue")
    root.after(3000, lambda: launcher_status.config(text="Ready"))

row += 1

# ========== TAB 2: DEBUG INFO ==========
debug_info_frame = tk.LabelFrame(debug_tab, text="System Status", padx=10, pady=10)
debug_info_frame.pack(fill="x", padx=10, pady=10)

info_text = tk.Text(debug_info_frame, height=18, width=85, font=("Courier", 9))
info_text.pack(padx=5, pady=5)

info_text.insert(tk.END, "═" * 60 + "\n")
info_text.insert(tk.END, "MACROPAD CONFIGURATOR STATUS\n")
info_text.insert(tk.END, "═" * 60 + "\n\n")

info_text.insert(tk.END, f"Serial Port: {PORT}\n")
info_text.insert(tk.END, f"Baud Rate: {BAUD}\n")
info_text.insert(tk.END, f"Arduino Connected: {'✓ YES' if serial_connected else '✗ NO'}\n\n")

info_text.insert(tk.END, "═" * 60 + "\n")
info_text.insert(tk.END, "HOW IT WORKS:\n")
info_text.insert(tk.END, "═" * 60 + "\n")
info_text.insert(tk.END, "1️⃣ Python RUNNING → Button opens software/folder\n")
info_text.insert(tk.END, "2️⃣ Python CLOSED → Button sends keybinding to Arduino\n\n")

info_text.insert(tk.END, "═" * 60 + "\n")
info_text.insert(tk.END, "BUTTON CONFIGURATIONS:\n")
info_text.insert(tk.END, "═" * 60 + "\n")
for b in ["B1", "B2", "B3", "B4"]:
    fallback = dropdowns.get(b, tk.StringVar()).get() if b in dropdowns else "Unknown"
    info_text.insert(tk.END, f"🔘 {b}:\n")
    info_text.insert(tk.END, f"   🔌 Fallback (Python closed): {fallback}\n")
    
    config = software_folder_paths.get(b, {})
    if config.get("path") and os.path.exists(config.get("path")):
        info_text.insert(tk.END, f"   🐍 Python running: {config.get('type')} → {config.get('path')}\n")
    elif config.get("path"):
        info_text.insert(tk.END, f"   ⚠ Invalid path: {config.get('path')}\n")
    else:
        info_text.insert(tk.END, f"   🐍 Python running: Not configured\n")
    info_text.insert(tk.END, "\n")

info_text.config(state=tk.DISABLED)

# ========== TAB 3: HELP ==========
help_frame = tk.Frame(help_tab, padx=20, pady=20)
help_frame.pack(fill="both", expand=True)

help_title = tk.Label(help_frame, text="📖 COMPLETE USER GUIDE", font=("Arial", 16, "bold"), fg="blue")
help_title.pack(pady=10)

help_text = tk.Text(help_frame, font=("Arial", 10), wrap=tk.WORD, height=25)
help_text.pack(fill="both", expand=True, pady=10)

help_text.insert(tk.END, "═" * 70 + "\n")
help_text.insert(tk.END, "DUAL MODE OPERATION\n")
help_text.insert(tk.END, "═" * 70 + "\n\n")

help_text.insert(tk.END, "🎯 CONCEPT:\n")
help_text.insert(tk.END, "   • This software gives your MacroPad TWO ways to work\n")
help_text.insert(tk.END, "   • When Python is RUNNING → Opens software/folders\n")
help_text.insert(tk.END, "   • When Python is CLOSED → Sends keybindings to Arduino\n\n")

help_text.insert(tk.END, "═" * 70 + "\n")
help_text.insert(tk.END, "📝 STEP-BY-STEP SETUP\n")
help_text.insert(tk.END, "═" * 70 + "\n\n")

help_text.insert(tk.END, "1️⃣ CONFIGURE A BUTTON:\n")
help_text.insert(tk.END, "   a. Click 'Configure' button next to B1, B2, B3, or B4\n")
help_text.insert(tk.END, "   b. Select what to open when Python is running:\n")
help_text.insert(tk.END, "      - Software: Browse to any .exe file\n")
help_text.insert(tk.END, "      - Folder: Browse to any folder\n")
help_text.insert(tk.END, "   c. Select fallback keybinding for when Python is closed\n")
help_text.insert(tk.END, "   d. Click 'Save'\n\n")

help_text.insert(tk.END, "2️⃣ SAVE CONFIGURATION:\n")
help_text.insert(tk.END, "   • Click 'Save Configuration' to save settings to JSON files\n\n")

help_text.insert(tk.END, "3️⃣ UPLOAD TO ARDUINO:\n")
help_text.insert(tk.END, "   • Click 'Upload to Arduino' to send fallback keybindings\n")
help_text.insert(tk.END, "   • This ensures Arduino knows what to do when Python is closed\n\n")

help_text.insert(tk.END, "4️⃣ TEST:\n")
help_text.insert(tk.END, "   • Click 'Test B1' to test if software/folder opens\n")
help_text.insert(tk.END, "   • Press physical button on MacroPad\n")
help_text.insert(tk.END, "   • Check 'Debug Console' tab for detailed logs\n\n")

help_text.insert(tk.END, "═" * 70 + "\n")
help_text.insert(tk.END, "🔧 ARDUINO CODE REQUIRED\n")
help_text.insert(tk.END, "═" * 70 + "\n\n")

help_text.insert(tk.END, "Your Arduino MUST send these commands:\n\n")
help_text.insert(tk.END, "   Serial.println(\"READY\");           // When Arduino starts\n")
help_text.insert(tk.END, "   Serial.println(\"PRESS:B1\");        // When button B1 pressed\n")
help_text.insert(tk.END, "   Serial.println(\"PRESS:B2\");        // When button B2 pressed\n")
help_text.insert(tk.END, "   Serial.println(\"PRESS:B3\");        // When button B3 pressed\n")
help_text.insert(tk.END, "   Serial.println(\"PRESS:B4\");        // When button B4 pressed\n\n")

help_text.insert(tk.END, "After receiving SET command, Arduino should respond:\n\n")
help_text.insert(tk.END, "   Serial.println(\"SET:OK\");          // Acknowledge receipt\n\n")

help_text.insert(tk.END, "═" * 70 + "\n")
help_text.insert(tk.END, "🐛 TROUBLESHOOTING\n")
help_text.insert(tk.END, "═" * 70 + "\n\n")

help_text.insert(tk.END, "❌ Arduino not detected:\n")
help_text.insert(tk.END, "   • Check USB connection\n")
help_text.insert(tk.END, "   • Verify COM port is COM8 (change in code if needed)\n")
help_text.insert(tk.END, "   • Click 'Refresh Serial'\n\n")

help_text.insert(tk.END, "❌ Software/Folder not opening:\n")
help_text.insert(tk.END, "   • Check 'Debug Console' to see if button press is received\n")
help_text.insert(tk.END, "   • Verify the path exists\n")
help_text.insert(tk.END, "   • Test with 'Test B1' button\n\n")

help_text.insert(tk.END, "❌ Arduino not sending commands:\n")
help_text.insert(tk.END, "   • Make sure Arduino code has Serial.println(\"PRESS:B1\")\n")
help_text.insert(tk.END, "   • Check baud rate (must be 9600)\n")
help_text.insert(tk.END, "   • Use Serial Monitor to test Arduino output\n")

help_text.config(state=tk.DISABLED)

# Start serial reader
if serial_connected:
    start_serial_reader()  # Start serial reader FIRST
    start_heartbeat()      # Then start heartbeat
    debug_print("Started serial reader and heartbeat")
else:
    debug_print("Serial not connected. Click 'Refresh Serial' to connect.")

def on_closing():
    debug_print("Closing application...")
    stop_heartbeat()
    if ser and ser.is_open:
        ser.close()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()

# Cleanup
if ser and ser.is_open:
    ser.close()