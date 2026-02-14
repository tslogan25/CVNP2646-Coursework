#!/usr/bin/env python3
# file_organizer.py
# Safely moves files into category folders

from pathlib import Path
import shutil

# -------------------------
# Hardcoded Directory Path
# -------------------------
BASE_DIRECTORY = Path(r"C:\Users\tslog\Python_Course\CVNP2646-Coursework\Week5")

# -------------------------
# Category Mapping
# -------------------------
EXTENSION_CATEGORIES = {
    "documents": {"pdf", "doc", "docx", "txt", "xls", "xlsx", "ppt", "pptx"},
    "images": {"jpg", "jpeg", "png", "gif", "bmp", "svg"},
    "executables": {"exe", "msi", "bat", "sh"},
}

OTHER_CATEGORY = "other"


def get_file_extension(file_path):
    """
    Extract file extension in lowercase.
    Returns empty string if no extension.
    """
    return file_path.suffix[1:].lower() if file_path.suffix else ""


def categorize_file(file_path):
    """
    Determine category based on file extension.
    """
    extension = get_file_extension(file_path)

    for category, extensions in EXTENSION_CATEGORIES.items():
        if extension in extensions:
            return category

    return OTHER_CATEGORY


def ensure_category_folder(base_dir, category):
    """
    Create category folder if it doesn't exist.
    """
    category_path = base_dir / category
    category_path.mkdir(exist_ok=True)
    return category_path


def move_file_safely(file_path, destination_dir):
    """
    Safely move a file, handling common errors.
    """
    destination = destination_dir / file_path.name

    try:
        if destination.exists():
            print(f"[SKIPPED] {file_path.name} already exists in {destination_dir.name}")
            return

        shutil.move(str(file_path), str(destination))
        print(f"[MOVED]   {file_path.name} → {destination_dir.name}")

    except PermissionError:
        print(f"[ERROR]   Permission denied: {file_path.name}")

    except OSError as e:
        print(f"[ERROR]   Could not move {file_path.name}: {e}")


# -------------------------
# Main Program
# -------------------------
if __name__ == "__main__":

    print("=" * 60)
    print("WEEK 5 FILE ORGANIZER")
    print("=" * 60)

    # Validate base directory
    if not BASE_DIRECTORY.exists() or not BASE_DIRECTORY.is_dir():
        print(f"Error: '{BASE_DIRECTORY}' is not a valid directory.")
        exit(1)

    files = [item for item in BASE_DIRECTORY.iterdir() if item.is_file()]

    if not files:
        print("No files to organize.")
        exit(0)

    for file in files:
        category = categorize_file(file)
        category_folder = ensure_category_folder(BASE_DIRECTORY, category)
        move_file_safely(file, category_folder)

    print("\nOrganization complete.")
