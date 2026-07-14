#!/usr/bin/env python3
import os
import shutil
from pathlib import Path

# Set destination folder
dest_folder = Path("all_abilities_files")
dest_folder.mkdir(exist_ok=True)

# Walk through all directories
for root, dirs, files in os.walk(r"C:\Users\Blake\Desktop\RivalsMods\UI Mods\With Just Abilities"):
    if "JustAbilities" in dirs:
        abilities_dir = Path(root) / "JustAbilities"
        parent_dir = Path(root).name
        
        # Check for Black, fallback to Red
        black_dir = abilities_dir / "Black"
        red_dir = abilities_dir / "Red"
        
        if black_dir.exists() and black_dir.is_dir():
            source_dir = black_dir
            color = "Black"
        elif red_dir.exists() and red_dir.is_dir():
            source_dir = red_dir
            color = "Red"
        else:
            print(f"Warning: Neither Black nor Red found in {abilities_dir} - skipping")
            continue
        
        print(f"Processing {parent_dir} using {color}")
        
        # Copy all files
        for file_path in source_dir.iterdir():
            if file_path.is_file():
                # Basic copy - may overwrite if same filename exists
                shutil.copy2(file_path, dest_folder / file_path.name)
                
                # Alternative: Rename to include parent folder name (uncomment if needed)
                # new_name = f"{parent_dir}_{file_path.name}"
                # shutil.copy2(file_path, dest_folder / new_name)

print(f"Done! All files copied to {dest_folder}")