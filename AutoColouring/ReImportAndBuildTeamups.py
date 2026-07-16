import subprocess
import sys
from pathlib import Path
import re
import shutil
import os

UE_CMD = r"C:\Program Files\Epic Games\UE_5.3\Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
UAT = r"C:\Program Files\Epic Games\UE_5.3\Engine\Build\BatchFiles\RunUAT.bat"

PROJECT = r"C:\Users\Blake\Documents\Unreal Projects\Marvel\Marvel.uproject"
PYTHON_SCRIPT = r"C:\Temp\test.py"
ARCHIVE_DIR = r"C:\Builds\Marvel"

OUTPUTLOCATION = Path(
        r"C:\Builds\Marvel\Windows\Marvel\Content\Paks"
)
# Add the current script's directory to Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from SHAREDASSETS import COLORS,ID_TO_NAME


#The asset we want.
ASSETLOCATION = Path(   
    r"C:\Users\Blake\Documents\Unreal Projects\Marvel\Plugins\MarvelGAS\Content\Marvel\UI\Common\Textures\AbilityIcon"
)

        # fbx_file_path = import_data.get_first_filename()
#All the colour options (Just copy past from auto colour lol.)





def run_command(command):
    print("=" * 80)
    print("RUNNING:")
    print(" ".join(command))
    print("=" * 80)

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    for line in process.stdout:
        print(line, end="")

    process.wait()

    print("\nExit code:", process.returncode)

    if process.returncode != 0:
        raise RuntimeError(f"Command failed ({process.returncode})")





def processThisColour(colour):

    # ----------------------------------------------------------------------
    # 1. Reimport assets
    # ----------------------------------------------------------------------

    run_command([
        UE_CMD,
        PROJECT,
        f'-ExecutePythonScript={PYTHON_SCRIPT}',
        '-unattended',
        '-nop4',
        '-log'
    ])

    # ----------------------------------------------------------------------
    # 2. Cook/package project
    # ----------------------------------------------------------------------

    run_command([
        UAT,
        'BuildCookRun',
        f'-project={PROJECT}',
        '-noP4',
        '-platform=Win64',
        '-clientconfig=Shipping',
        '-build',
        '-cook',
        '-stage',
        '-pak',
        '-archive',
        f'-archivedirectory={ARCHIVE_DIR}',
        '-utf8output',
        '-log'
    ])

    # ----------------------------------------------------------------------
    # 3. Rename Cooked Packages
    # ----------------------------------------------------------------------




    for chunk_id, new_name in ID_TO_NAME.items():

        old_file = OUTPUTLOCATION / f"pakchunk{chunk_id}-Windows.pak"

        if not old_file.exists():
            print(f"Missing: {old_file.name}")
            continue

        new_file = OUTPUTLOCATION / f"{new_name}_{colour}_{chunk_id}-Windows.pak"

        print(f"Renaming:")
        print(f"  {old_file.name}")
        print(f"  -> {new_file.name}")

        old_file.rename(new_file)

# Clear the files
# for file in OUTPUTLOCATION.iterdir():
#     if file.is_file():
#         file.unlink()

# print("All files deleted.")

# Loop through each first-level folder in ASSETLOCATION (e.g., 1021, 1022, etc.)
for asset_folder in ASSETLOCATION.iterdir():
    if not asset_folder.is_dir():
        continue
    
    asset_id = asset_folder.name
    print(f"Processing Asset ID: {asset_id}")

    colored_folder = asset_folder / "colored"

    if not colored_folder.exists():
        print(f"Missing folder: {colored_folder}")
        continue

    for color_name in COLORS.keys():
        print(f"Processing Colour: {color_name}")

        source_folder = colored_folder / color_name

        if not source_folder.exists():
            print(f"Missing folder: {source_folder}")
            continue

        for file in source_folder.iterdir():
            if file.is_file():
                destination = asset_folder / file.name

                print(f"  Copying {file.name}")

                # Overwrites existing file automatically
                shutil.copy2(file, destination)
        
        print(f"Copied Out All For the Colour: {color_name}")

        #Now we do the reimport and stuff.
        processThisColour(color_name)

        print(f"Processed the colour: {color_name}")




print("\nDONE.")