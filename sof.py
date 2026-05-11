"""
Software and Folder Launcher Module
Handles opening applications and folders from the system
"""

import subprocess
import os
import platform

def open_folder(folder_path):
    """Opens a folder in the system's file explorer"""
    if not folder_path or folder_path.strip() == "":
        print("Error: No folder path provided")
        return False
    
    folder_path = os.path.expanduser(folder_path)
    
    if not os.path.exists(folder_path):
        print(f"Error: Path does not exist - {folder_path}")
        return False
    
    try:
        if platform.system() == "Windows":
            os.startfile(folder_path)
        elif platform.system() == "Darwin":
            subprocess.run(["open", folder_path])
        else:
            subprocess.run(["xdg-open", folder_path])
        
        print(f"Successfully opened folder: {folder_path}")
        return True
    except Exception as e:
        print(f"Error opening folder: {e}")
        return False

def launch_software(software_path):
    """Launches a software application"""
    if not software_path or software_path.strip() == "":
        print("Error: No software path provided")
        return False
    
    software_path = os.path.expanduser(software_path)
    
    try:
        if platform.system() == "Windows":
            subprocess.Popen(software_path, shell=True)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", software_path])
        else:
            subprocess.Popen([software_path])
        
        print(f"Successfully launched: {software_path}")
        return True
    except Exception as e:
        print(f"Error launching software: {e}")
        return False