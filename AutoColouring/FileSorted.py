from pathlib import Path
import shutil

# Folder containing the .pak files
SOURCE_FOLDER = Path(r"C:\Users\Blake\Desktop\RivalsMods\UI Mods\With Just Abilities\ScarletWitch UI")

colors = {
    'red': (255, 0, 0),
    'green': (0, 255, 0),
    'blue': (0, 0, 255),
    'yellow': (255, 255, 0),
    'cyan': (0, 255, 255),
    'magenta': (255, 0, 255),
    'orange': (255, 157, 0),
    'purple': (128, 0, 128),
    'pink': (255, 192, 203),
    'teal': (0, 128, 128),
    'black': (0, 0, 0),
    'lime': (204, 255, 0)
}
VALID_EXTENSIONS = {".pak", ".utoc", ".ucas"}

for file_path in SOURCE_FOLDER.iterdir():

    if file_path.suffix.lower() not in VALID_EXTENSIONS:
        continue

    filename = file_path.name.lower()

    # Find the color
    color_found = None
    for color in colors:
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