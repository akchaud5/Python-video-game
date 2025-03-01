import os
import sys
import subprocess
import platform

def create_executable():
    """Create standalone executable using PyInstaller"""
    try:
        # Check if PyInstaller is installed
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        
        # Determine the appropriate icon for the platform
        icon_path = None
        if platform.system() == "Windows":
            icon_path = "pygame/pygame_icon.bmp"
        elif platform.system() == "Darwin":  # macOS
            icon_path = "pygame/pygame_icon.icns"
        
        # Set PyInstaller command arguments
        pyinstaller_args = [
            "pyinstaller",
            "--onefile",
            "--windowed",
            "--name=PingPong",
            "main.py"
        ]
        
        # Add icon if available
        if icon_path and os.path.exists(icon_path):
            pyinstaller_args.append(f"--icon={icon_path}")
        
        # Execute PyInstaller
        subprocess.check_call(pyinstaller_args)
        
        print("Build completed successfully!")
        print(f"Executable can be found in the 'dist' directory:")
        print("- PingPong (Game with single player and multiplayer modes)")
        
    except Exception as e:
        print(f"Error creating executable: {e}")
        return False
    
    return True

def create_requirements():
    """Create requirements.txt file for easy installation of dependencies"""
    with open("requirements.txt", "w") as f:
        f.write("pygame>=2.0.0\n")
    print("Created requirements.txt file")

def main():
    print("==== Ping Pong Game Build Utility ====")
    print("1. Create executable (requires PyInstaller)")
    print("2. Generate requirements.txt")
    print("3. Exit")
    
    choice = input("Enter your choice (1-3): ")
    
    if choice == "1":
        create_executable()
    elif choice == "2":
        create_requirements()
    elif choice == "3":
        print("Exiting...")
    else:
        print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()