from pathlib import Path
import shutil
import sys
import os

# Folder containing the .pak files
SOURCE_FOLDER = Path(r"C:\Users\Blake\Desktop\RivalsMods\UI Mods\With Just Abilities\ElsaBloodstone UI")

# Add the current script's directory to Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from SHAREDASSETS import COLORS

VALID_EXTENSIONS = {".pak", ".utoc", ".ucas"}

for file_path in SOURCE_FOLDER.iterdir():

    if file_path.suffix.lower() not in VALID_EXTENSIONS:
        continue

    filename = file_path.name.lower()

    # Find the color
    color_found = None
    for color in COLORS:
        if f"_{color}_" in filename:
            
            color_found = color.capitalize()
            break

    if color_found is None:
        print(f"No color found: {file_path.name}")
        continue

    # Determine folder
    if "justabilities" in filename:
        category = "JustAbilities"
    else:
        category = "Everything"

    destination = SOURCE_FOLDER / category / color_found
    destination.mkdir(parents=True, exist_ok=True)

    shutil.move(
        str(file_path),
        destination / file_path.name
    )

    print(f"Moved: {file_path.name}")