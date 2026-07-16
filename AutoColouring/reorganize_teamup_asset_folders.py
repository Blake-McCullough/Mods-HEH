import os
import shutil
from pathlib import Path

asset_location = Path(r"C:\Users\Blake\Desktop\RivalsMods\UI Mods\Teamups")

# Define valid extensions
VALID_EXTENSIONS = {".pak", ".utoc", ".ucas"}

def reorganize_asset_files(base_path):
    """
    Reorganizes asset files (.pak, .utoc, .ucas) from:
    ASSETLOCATION/
    ├── AdamWarlock_blue_1046-Windows.pak
    ├── AdamWarlock_cyan_1046-Windows.utoc
    ├── Gambit_green_1058-Windows.ucas
    ├── ElsaBloodstone_yellow_1059-Windows.pak
    
    to:
    ASSETLOCATION/
    ├── DiffCharacter/
    │   ├── AdamWarlock/
    │   │   ├── AdamWarlock_blue_1046-Windows.pak
    │   │   └── AdamWarlock_cyan_1046-Windows.utoc
    │   ├── Gambit/
    │   │   └── Gambit_green_1058-Windows.ucas
    │   └── ElsaBloodstone/
    │       └── ElsaBloodstone_yellow_1059-Windows.pak
    └── Colours/
        ├── blue/
        │   └── AdamWarlock_blue_1046-Windows.pak (copy)
        ├── green/
        │   └── Gambit_green_1058-Windows.ucas (copy)
        └── yellow/
            └── ElsaBloodstone_yellow_1059-Windows.pak (copy)
    """
    
    if not base_path.exists():
        print(f"Error: Path '{base_path}' does not exist")
        return
    
    if not base_path.is_dir():
        print(f"Error: '{base_path}' is not a directory")
        return
    
    print(f"Processing directory: {base_path}")
    
    # Create the new directory structure
    diff_character_path = base_path / "DiffCharacter"
    colours_path = base_path / "Colours"
    
    diff_character_path.mkdir(exist_ok=True)
    colours_path.mkdir(exist_ok=True)
    
    # Get all valid files in the base directory
    valid_files = [f for f in base_path.iterdir() 
                   if f.is_file() and f.suffix in VALID_EXTENSIONS]
    
    if not valid_files:
        print(f"No valid files found to process! (Extensions: {', '.join(VALID_EXTENSIONS)})")
        return
    
    print(f"Found {len(valid_files)} valid files to process")
    
    # Track processed files
    processed = 0
    skipped = 0
    
    # Process each file
    for file_path in valid_files:
        file_name = file_path.name
        file_extension = file_path.suffix
        
        # Skip the base game files
        if file_name.startswith("pakchunk0-"):
            print(f"Skipping '{file_name}' (base game file)")
            skipped += 1
            continue
        
        # Parse file name format: Character_Color_Number-Windows.extension
        # Example: AdamWarlock_blue_1046-Windows.pak
        # Remove the -Windows part and extension for parsing
        base_name = file_name.rsplit('-Windows', 1)[0] if '-Windows' in file_name else file_name.rsplit('.', 1)[0]
        
        # Parse the base name
        parts = base_name.split('_')
        
        if len(parts) < 3:
            print(f"Skipping '{file_name}': doesn't match expected format")
            skipped += 1
            continue
        
        # Extract character and color
        # If there are more than 2 underscores, the character name has underscores
        if len(parts) > 3:
            # Last two parts are color and number
            color = parts[-2]
            number = parts[-1]
            # Everything else is the character name
            character = '_'.join(parts[:-2])
        else:
            # Standard format: character_color_number
            character = parts[0]
            color = parts[1]
            number = parts[2]
        
        print(f"Processing: {file_name} -> Character: '{character}', Color: '{color}', Extension: '{file_extension}'")
        
        # Create character directory structure
        character_dir = diff_character_path / character
        character_dir.mkdir(exist_ok=True)
        
        # Create color directory structure
        color_dir = colours_path / color
        color_dir.mkdir(exist_ok=True)
        
        # Destination paths
        dest_character = character_dir / file_name
        dest_color = color_dir / file_name
        
        try:
            # Copy file to character directory
            shutil.copy2(str(file_path), str(dest_character))
            print(f"  ✓ Copied '{file_name}' to DiffCharacter/{character}/")
            
            # Copy file to color directory
            shutil.copy2(str(file_path), str(dest_color))
            print(f"  ✓ Copied '{file_name}' to Colours/{color}/")
            processed += 1
            
        except Exception as e:
            print(f"  ✗ Error processing '{file_name}': {e}")
            skipped += 1
        
        print()
    
    print("\n" + "="*50)
    print("REORGANIZATION COMPLETE!")
    print("="*50)
    print(f"Processed: {processed} files")
    print(f"Skipped: {skipped} files")
    print(f"Total files copied: {processed * 2} (one to DiffCharacter/, one to Colours/)")
    print(f"All original files remain in the root folder")
    print("\nNew structure:")
    print(f"  {base_path}/")
    print(f"  ├── DiffCharacter/ (copies organized by character)")
    print(f"  └── Colours/ (copies organized by color)")

def main():
    print(f"Asset location: {asset_location}")
    print(f"Absolute path: {asset_location.absolute()}")
    print(f"Valid extensions: {', '.join(VALID_EXTENSIONS)}")
    print()
    
    # Count files to process
    valid_files = [f for f in asset_location.iterdir() 
                   if f.is_file() and f.suffix in VALID_EXTENSIONS]
    
    # Ask for confirmation before proceeding
    print(f"WARNING: This will COPY all valid files into new folders.")
    print(f"Found {len(valid_files)} valid files to process")
    print(f"Total disk space needed: ~{len(valid_files) * 2} file copies")
    print()
    response = input("Do you want to continue? (y/n): ")
    
    if response.lower() != 'y':
        print("Operation cancelled.")
        return
    
    reorganize_asset_files(asset_location)

if __name__ == "__main__":
    main()