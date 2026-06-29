import subprocess
import sys
from pathlib import Path
import re
import shutil

UE_CMD = r"C:\Program Files\Epic Games\UE_5.3\Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
UAT = r"C:\Program Files\Epic Games\UE_5.3\Engine\Build\BatchFiles\RunUAT.bat"

PROJECT = r"C:\Users\Blake\Documents\Unreal Projects\Marvel\Marvel.uproject"
PYTHON_SCRIPT = r"C:\Temp\test.py"
ARCHIVE_DIR = r"C:\Builds\Marvel"


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

OUTPUTLOCATION = Path(
    r"C:\Builds\Marvel\Windows\Marvel\Content\Paks"
)

renames = {
    6248: "WhiteFox",
    6298: "WhiteFox_JustAbilities",
}

colour = "Blue"

for chunk_id, new_name in renames.items():

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


print("\nDONE.")