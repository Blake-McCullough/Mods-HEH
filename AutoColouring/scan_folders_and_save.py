import os

SOURCE_DIRECTORY = r"C:\Users\Blake\Documents\Unreal Projects\Marvel\Plugins\MarvelGAS\Content\Marvel\UI\Common\Textures\AbilityIcon"

def scan_folders_and_save(source_dir, output_file="assets.txt"):
    """
    Scans a directory for folders and saves them in a dictionary format to a file.
    
    Args:
        source_dir (str): Path to the directory to scan
        output_file (str): Name of the output file (default: assets.txt)
    """
    
    # Check if the source directory exists
    if not os.path.exists(source_dir):
        print(f"Error: Source directory '{source_dir}' does not exist!")
        return
    
    # Get all items in the directory
    try:
        items = os.listdir(source_dir)
    except PermissionError:
        print(f"Error: Permission denied to access '{source_dir}'")
        return
    except OSError as e:
        print(f"Error: Could not read directory - {e}")
        return
    
    # Filter to only include directories
    folders = [item for item in items if os.path.isdir(os.path.join(source_dir, item))]
    
    if not folders:
        print(f"No folders found in '{source_dir}'")
        return
    
    # Sort folders alphabetically
    folders.sort()
    
    # Create the output content
    output_lines = ["ID_TO_NAME = {"]
    
    for folder in folders:
        output_lines.append(f'    "{folder}": "",')
    
    output_lines.append("}")
    
    # Write to file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output_lines))
        print(f"Successfully saved {len(folders)} folders to '{output_file}'")
        print(f"First few folders: {', '.join(folders[:5])}")
        if len(folders) > 5:
            print(f"... and {len(folders) - 5} more")
    except Exception as e:
        print(f"Error: Could not write to file - {e}")

if __name__ == "__main__":
    scan_folders_and_save(SOURCE_DIRECTORY)