#!/usr/bin/env python3
# test_directory.py
# Creates test_downloads folder with sample files

from pathlib import Path

def create_test_files(base_path):
    base = Path(base_path)

    # Create directory if it doesn't exist
    base.mkdir(parents=True, exist_ok=True)

    # File groups
    files = [
        # Documents
        "report.pdf", "presentation.pptx", "notes.txt", "README",

        # Images
        "photo.jpg", "screenshot.PNG", "diagram.svg",

        # Archives
        "backup.zip", "archive.tar.gz", "files.rar",

        # Executables / scripts
        "installer.exe", "setup.msi", "script.sh",

        # Media
        "video.mp4", "song.mp3",

        # Edge cases
        "UPPERCASE.PDF", "noextension", "weird.FILE"
    ]

    # Create files
    for file_name in files:
        file_path = base / file_name
        file_path.touch(exist_ok=True)
        print(f"Created: {file_path}")

    print("\n✅ Test structure created successfully!")

if __name__ == "__main__":
    # CHANGE THIS PATH if needed
    target_directory = r"C:\Users\tslog\Python_Course\CVNP2646-Coursework\Week5\test_downloads"

    create_test_files(target_directory)