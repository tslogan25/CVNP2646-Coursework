#!/usr/bin/env python3
# organizer_create_separate_folder.py

import os
import shutil

# -------------------------
# CATEGORY MAP
# -------------------------
CATEGORY_MAP = {
    "documents": {"pdf", "doc", "docx", "txt"},
    "images": {"jpg", "jpeg", "png", "gif"},
    "videos": {"mp4", "avi"},
    "audio": {"mp3", "wav"},
    "archives": {"zip", "rar", "tar", "gz"},
    "executables": {"exe", "msi", "bat", "sh"},
}

DEFAULT_CATEGORY = "other"


# -------------------------
# GET EXTENSION
# -------------------------
def get_extension(filename):
    filename = filename.lower()

    if filename.endswith(".tar.gz"):
        return "tar.gz"

    if "." not in filename:
        return ""

    return filename.rsplit(".", 1)[1]


# -------------------------
# GET CATEGORY
# -------------------------
def get_category(filename):
    ext = get_extension(filename)

    for cat, exts in CATEGORY_MAP.items():
        if ext in exts:
            return cat

    return DEFAULT_CATEGORY


# -------------------------
# MAIN ORGANIZER
# -------------------------
def organize(source_folder):

    # Make absolute path
    source_folder = os.path.abspath(source_folder)

    # 🔥 CREATE NEW FOLDER NEXT TO SOURCE
    parent_dir = os.path.dirname(source_folder)
    base_name = os.path.basename(source_folder)

    new_folder = os.path.join(parent_dir, base_name + "_copy")

    print(f"\nSOURCE: {source_folder}")
    print(f"NEW FOLDER: {new_folder}\n")

    # Create new folder
    os.makedirs(new_folder, exist_ok=True)

    moved = 0

    for filename in os.listdir(source_folder):

        src = os.path.join(source_folder, filename)

        # Skip directories
        if os.path.isdir(src):
            continue

        category = get_category(filename)

        # Create category folder in NEW folder
        category_path = os.path.join(new_folder, category)
        os.makedirs(category_path, exist_ok=True)

        dest = os.path.join(category_path, filename)

        print(f"Moving: {filename} -> {category}")

        try:
            shutil.move(src, dest)
            moved += 1
        except Exception as e:
            print(f"ERROR: {e}")

    print(f"\nDONE. Files moved: {moved}")


# -------------------------
# RUN
# -------------------------
if __name__ == "__main__":

    # 🔥 CHANGE THIS PATH
    SOURCE = r"C:\Users\tslog\Python_Course\CVNP2646-Coursework\Week5\test_downloads"

    organize(SOURCE)