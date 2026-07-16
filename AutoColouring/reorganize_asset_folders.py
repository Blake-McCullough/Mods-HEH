import os
import shutil
from pathlib import Path

asset_location = Path(r"C:\Users\Blake\Desktop\RivalsMods\UI Mods\Teamups")

def reorganize_asset_files(base_path):
    """
    Reorganizes asset .pak files from:
    ASSETLOCATION/
    ├── AdamWarlock_blue_1046-Windows.pak
    ├── AdamWarlock_cyan_1046-Windows.pak
    ├── Gambit_green_1058-Windows.pak
    ├── ElsaBloodstone_yellow_1059-Windows.pak
    
    to:
    ASSETLOCATION/
    ├── DiffCharacter/
    │   ├── AdamWarlock/
    │   │   ├── AdamWarlock_blue_1046-Windows.pak
    │   │   └── AdamWarlock_cyan_1046-Windows.pak
    │   ├── Gambit/
    │   │   └── Gambit_green_1058-Windows.pak
    │   └── ElsaBloodstone/
    │       └── ElsaBloodstone_yellow_1059-Windows.pak
    └── Colours/
        ├── blue/
        │   └── AdamWarlock_blue_1046-Windows.pak (copy)
        ├── green/
        │   └── Gambit_green_1058-Windows.pak (copy)
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
    
    # Get all .pak files in the base directory
    pak_files = [f for f in base_path.iterdir() if f.is_file() and f.suffix == '.pak']
    
    if not pak_files:
        print("No .pak files found to process!")
        return
    
    print(f"Found {len(pak_files)} .pak files to process")
    
    # Track processed files
    processed = 0
    skipped = 0
    
    # Process each file
    for file_path in pak_files:
        file_name = file_path.name
        
        # Skip the pakchunk0 file
        if file_name == "pakchunk0-Windows.pak":
            print(f"Skipping '{file_name}' (base game file)")
            skipped += 1
            continue
        
        # Parse file name format: Character_Color_Number-Windows.pak
        # Example: AdamWarlock_blue_1046-Windows.pak
        parts = file_name.rsplit('_', 2)  # Split from right to get color and number
        if len(parts) < 3:
            print(f"Skipping '{file_name}': doesn't match expected format")
            skipped += 1
            continue
        
        # Reconstruct the parts
        # parts[0] = everything before last underscore (character name + maybe more)
        # parts[1] = color
        # parts[2] = number-Windows.pak
        character_part = parts[0]
        color = parts[1]
        number_part = parts[2]
        
        # Handle character names that might have underscores (like "CloakAndDagger")
        # If there are more than 2 underscores total, we need to reconstruct
        underscore_count = file_name.count('_')
        if underscore_count > 2:
            # Reconstruct character name from all parts except the last two
            temp_parts = file_name.split('_')
            character = '_'.join(temp_parts[:-2])
            color = temp_parts[-2]
        else:
            character = character_part
        
        print(f"Processing: {file_name} -> Character: '{character}', Color: '{color}'")
        
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
    print()
    
    # Ask for confirmation before proceeding
    print("WARNING: This will COPY all .pak files into new folders.")
    print(f"Total disk space needed: ~{len([f for f in asset_location.iterdir() if f.is_file() and f.suffix == '.pak']) * 2} file copies")
    print()
    response = input("Do you want to continue? (y/n): ")
    
    if response.lower() != 'y':
        print("Operation cancelled.")
        return
    
    reorganize_asset_files(asset_location)

if __name__ == "__main__":
    main()