import unreal
import os
import re
from pathlib import Path

# ============================================================================
# CONFIGURATION - EDIT THIS DICTIONARY WITH YOUR FOLDER ID TO NAME MAPPING
# ============================================================================
# Format: "folder_id": "desired_label_name"
FOLDER_ID_TO_NAME = {
    "1023": "YourAbilityName1",
    # Add all your folder IDs and their corresponding names here
    # Example: "1023": "Fireball_Ability"
}

# ============================================================================
# CONFIGURATION - SOURCE AND DESTINATION PATHS
# ============================================================================
SOURCE_DIRECTORY = r"C:\Users\Blake\Documents\Unreal Projects\Marvel\Plugins\MarvelGAS\Content\Marvel\UI\Common\Textures\AbilityIcon"
UNREAL_CONTENT_PATH = "/Game/Marvel/UI/Common/Textures/AbilityIcon"
LABEL_FOLDER= "/Game"

# Additional asset to include in all labels (set to None if not needed)
ADDITIONAL_ASSET_PATH = None  # Example: "/Game/Some/Path/To/Asset.Asset"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_asset_name_from_path(asset_path):
    """Extract asset name from a full asset path."""
    path_parts = asset_path.split('/')
    full_filename = path_parts[-1]
    if '.' in full_filename:
        return full_filename.split('.')[0]
    return full_filename

def import_texture_asset(file_path, destination_folder):
    """Import a single texture asset using AssetImportTask."""
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    asset_library = unreal.EditorAssetLibrary()
    
    file_name = os.path.basename(file_path)
    file_name_without_ext = os.path.splitext(file_name)[0]
    
    # Create the destination path
    destination_path = f"{destination_folder}/{file_name_without_ext}"
    
    # Check if asset already exists and delete it
    if asset_library.does_asset_exist(destination_path):
        unreal.log(f"    Asset already exists, deleting: {destination_path}")
        asset_library.delete_asset(destination_path)
    
    # Import the asset using AssetImportTask
    try:
        # Get the absolute file path
        abs_file_path = os.path.abspath(file_path)
        
        # Create import task
        import_task = unreal.AssetImportTask()
        import_task.filename = abs_file_path
        import_task.destination_path = destination_folder
        import_task.destination_name = file_name_without_ext
        import_task.replace_existing = True
        import_task.automated = True
        import_task.save = True
        
        # Set up the factory based on file extension
        ext = os.path.splitext(file_name)[1].lower()
        if ext in ['.png', '.jpg', '.jpeg', '.bmp']:
            import_task.factory = unreal.TextureFactory()
        elif ext == '.tga':
            import_task.factory = unreal.TargaTextureFactory()
        elif ext in ['.dds', '.psd']:
            import_task.factory = unreal.TextureFactory()
        else:
            import_task.factory = unreal.TextureFactory()
        
        # Execute the import
        asset_tools.import_asset_tasks([import_task])
        
        # Check if the import was successful by looking for the asset
        if asset_library.does_asset_exist(destination_path):
            imported_asset = asset_library.load_asset(destination_path)
            if imported_asset:
                return imported_asset
        
        # If not found, try to find it by listing assets in the folder
        assets_in_folder = asset_library.list_assets(destination_folder, recursive=False)
        for asset in assets_in_folder:
            if file_name_without_ext in asset:
                imported_asset = asset_library.load_asset(asset)
                if imported_asset:
                    return imported_asset
        
        unreal.log_error(f"    Failed to import: {file_name}")
        return None
        
    except Exception as e:
        unreal.log_error(f"    Exception importing {file_name}: {str(e)}")
        return None

# ============================================================================
# MAIN FUNCTION
# ============================================================================

def import_textures_and_create_labels():
    """
    Imports textures from local folders into Unreal and creates PrimaryAssetLabels
    with chunk IDs based on folder names.
    """
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    asset_library = unreal.EditorAssetLibrary()
    
    # Load the PrimaryAssetLabel class
    label_class = unreal.load_class(None, "/Script/Engine.PrimaryAssetLabel")
    if not label_class:
        unreal.log_error("Failed to load PrimaryAssetLabel class.")
        return None
    
    # Load additional asset if specified
    additional_asset = None
    if ADDITIONAL_ASSET_PATH:
        unreal.log(f"Loading additional asset: {ADDITIONAL_ASSET_PATH}")
        additional_asset = asset_library.load_asset(ADDITIONAL_ASSET_PATH)
        if not additional_asset:
            unreal.log_error(f"Failed to load additional asset: {ADDITIONAL_ASSET_PATH}")
            return None
        unreal.log(f"✓ Successfully loaded additional asset: {additional_asset.get_name()}")
    
    # Get all subdirectories in the source folder
    unreal.log(f"Scanning source directory: {SOURCE_DIRECTORY}")
    
    if not os.path.exists(SOURCE_DIRECTORY):
        unreal.log_error(f"Source directory does not exist: {SOURCE_DIRECTORY}")
        return None
    
    # Get all subdirectories
    subdirs = []
    for item in os.listdir(SOURCE_DIRECTORY):
        item_path = os.path.join(SOURCE_DIRECTORY, item)
        if os.path.isdir(item_path):
            # Check if the folder name is in our dictionary
            if item in FOLDER_ID_TO_NAME:
                subdirs.append(item)
                unreal.log(f"  Found folder: {item} → {FOLDER_ID_TO_NAME[item]}")
            else:
                unreal.log_warning(f"  Skipping folder '{item}' - not in dictionary")
    
    if not subdirs:
        unreal.log_error("No matching folders found in the source directory.")
        unreal.log("Please check your FOLDER_ID_TO_NAME dictionary and folder names.")
        return None
    
    unreal.log(f"Found {len(subdirs)} folders to process")
    
    # Create the label folder in Unreal if it doesn't exist
    if not asset_library.does_directory_exist(LABEL_FOLDER):
        asset_library.make_directory(LABEL_FOLDER)
        unreal.log(f"Created label directory: {LABEL_FOLDER}")
    
    created_labels = []
    output_lines = []
    
    # Add header to output
    output_lines.append("chunkID | folder | label_name | imported_files")
    output_lines.append("-" * 80)
    
    # Process each folder
    for folder_id in subdirs:
        try:
            folder_path = os.path.join(SOURCE_DIRECTORY, folder_id)
            label_name = FOLDER_ID_TO_NAME[folder_id]
            
            # Use folder ID as chunk ID (convert to int if possible)
            try:
                chunk_id = int(folder_id)
            except ValueError:
                chunk_id = folder_id
            
            unreal.log(f"\n{'='*60}")
            unreal.log(f"Processing folder: {folder_id} (Chunk ID: {chunk_id})")
            unreal.log(f"  Label name: {label_name}")
            unreal.log(f"  Path: {folder_path}")
            unreal.log(f"{'='*60}")
            
            # Get all texture files in the folder
            texture_files = []
            valid_extensions = {'.png', '.jpg', '.jpeg', '.tga', '.bmp', '.dds', '.psd', '.exr', '.hdr'}
            
            for file in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file)
                if os.path.isfile(file_path):
                    ext = os.path.splitext(file)[1].lower()
                    if ext in valid_extensions:
                        texture_files.append(file_path)
            
            if not texture_files:
                unreal.log_warning(f"  No texture files found in {folder_path}")
                continue
            
            unreal.log(f"  Found {len(texture_files)} texture file(s)")
            
            # Create the destination folder in Unreal
            dest_folder = f"{UNREAL_CONTENT_PATH}/{folder_id}"
            if not asset_library.does_directory_exist(dest_folder):
                asset_library.make_directory(dest_folder)
                unreal.log(f"  Created Unreal folder: {dest_folder}")
            
            imported_assets = []
            
            # Import each texture
            for file_path in texture_files:
                file_name = os.path.basename(file_path)
                unreal.log(f"  Importing: {file_name}")
                
                imported_asset = import_texture_asset(file_path, dest_folder)
                if imported_asset:
                    imported_assets.append(imported_asset)
                    unreal.log(f"    ✓ Imported: {imported_asset.get_name()} to {dest_folder}")
                else:
                    unreal.log_error(f"    ✗ Failed to import: {file_name}")
            
            if not imported_assets:
                unreal.log_warning(f"  No assets imported for folder {folder_id}")
                continue
            
            # ================================================================
            # CREATE LABEL - Using the exact same logic as the original script
            # ================================================================
            
            # Create the label asset
            label_asset_name = f"Label_{label_name}"
            label_path = f"{LABEL_FOLDER}/{label_asset_name}"
            
            # Delete existing label if it exists
            if asset_library.does_asset_exist(label_path):
                unreal.log(f"  Deleting existing label: {label_path}")
                asset_library.delete_asset(label_path)
            
            # Create new label (using the original script's approach)
            unreal.log(f"  Creating label: {label_asset_name}")
            label_asset = asset_tools.create_asset(
                asset_name=label_asset_name,
                package_path=LABEL_FOLDER,
                asset_class=label_class,
                factory=unreal.DataAssetFactory()
            )
            
            if not label_asset:
                unreal.log_error(f"  ✗ Failed to create label: {label_asset_name}")
                continue
            
            # Set explicit assets with BOTH imported assets and additional asset
            # Using the exact same approach as the original script
            explicit_assets = imported_assets.copy()
            if additional_asset:
                explicit_assets.append(additional_asset)
            
            label_asset.set_editor_property("explicit_assets", explicit_assets)
            unreal.log(f"  Set {len(explicit_assets)} explicit asset(s)")
            
            # Try to set chunk ID with various property names (same as original)
            chunk_set = False
            for prop_name in ['ChunkID', 'chunk_id', 'ChunkId', 'chunkid', 'Chunk']:
                try:
                    label_asset.set_editor_property(prop_name, chunk_id)
                    chunk_set = True
                    unreal.log(f"  ✓ Set {prop_name} = {chunk_id}")
                    break
                except:
                    continue
            
            if not chunk_set:
                try:
                    rules = label_asset.get_editor_property("rules")
                    if rules:
                        for rule_prop in ['ChunkID', 'chunk_id', 'ChunkId']:
                            try:
                                rules.set_editor_property(rule_prop, chunk_id)
                                label_asset.set_editor_property("rules", rules)
                                chunk_set = True
                                unreal.log(f"  ✓ Set rules.{rule_prop} = {chunk_id}")
                                break
                            except:
                                continue
                except:
                    pass
            
            if not chunk_set:
                unreal.log_warning(f"  ⚠ Could not set chunk ID for {label_asset_name}")
            
            # Set apply recursively (same as original)
            for prop_name in ['apply_recursively', 'ApplyRecursively', 'bApplyRecursively']:
                try:
                    label_asset.set_editor_property(prop_name, False)
                    break
                except:
                    continue
            
            # Save the label (same as original)
            asset_library.save_loaded_asset(label_asset)
            unreal.log(f"  ✓ Saved label: {label_asset_name}")
            
            # Store for reporting
            created_labels.append({
                'folder_id': folder_id,
                'label_name': label_asset_name,
                'chunk_id': chunk_id,
                'imported_count': len(imported_assets),
                'imported_files': [asset.get_name() for asset in imported_assets]
            })
            
            # Add to output lines for file
            imported_files_str = ", ".join([asset.get_name() for asset in imported_assets])
            output_lines.append(f"{chunk_id} | {folder_id} | {label_asset_name} | {imported_files_str}")
            
        except Exception as e:
            unreal.log_error(f"Error processing folder {folder_id}: {str(e)}")
            import traceback
            unreal.log_error(traceback.format_exc())
    
    # Write output file
    output_file = os.path.join(unreal.Paths.project_saved_dir(), "Texture_Import_Export.txt")
    try:
        with open(output_file, 'w') as f:
            f.write('\n'.join(output_lines))
        unreal.log(f"\n✓ Output file saved to: {output_file}")
    except Exception as e:
        unreal.log_error(f"Failed to write output file: {str(e)}")
    
    # Print summary
    unreal.log("\n" + "=" * 80)
    unreal.log("SUMMARY: Processed Folders and Created Labels")
    unreal.log("=" * 80)
    
    if created_labels:
        for label_info in created_labels:
            unreal.log(f"  Folder: {label_info['folder_id']:10} | Label: {label_info['label_name']:45} | Chunk: {label_info['chunk_id']:10} | Files: {label_info['imported_count']}")
        
        unreal.log("=" * 80)
        unreal.log(f"Total folders processed: {len(created_labels)}")
        unreal.log(f"Total files imported: {sum(info['imported_count'] for info in created_labels)}")
        unreal.log(f"Output file: {output_file}")
        unreal.log("=" * 80)
        
        # Print the output lines to the log
        unreal.log("\n" + "=" * 80)
        unreal.log("EXPORTED DATA:")
        unreal.log("=" * 80)
        for line in output_lines:
            unreal.log(line)
        unreal.log("=" * 80)
    else:
        unreal.log_error("No labels were created. Please check your configuration and folder structure.")
    
    return created_labels, output_file

# ============================================================================
# EXECUTION
# ============================================================================

if __name__ == "__main__":
    unreal.log("=" * 60)
    unreal.log("Starting Texture Import and Label Creation Script")
    unreal.log("=" * 60)
    
    # Verify dictionary is populated
    if not FOLDER_ID_TO_NAME:
        unreal.log_error("FOLDER_ID_TO_NAME dictionary is empty! Please add your folder ID to name mappings.")
        unreal.log_error("Example: FOLDER_ID_TO_NAME = {'1023': 'Fireball', '1024': 'IceBlast'}")
    else:
        # Verify source directory exists
        if not os.path.exists(SOURCE_DIRECTORY):
            unreal.log_error(f"Source directory does not exist: {SOURCE_DIRECTORY}")
            unreal.log_error("Please check the SOURCE_DIRECTORY path.")
        else:
            # Verify at least one folder matches the dictionary
            found_matches = False
            for item in os.listdir(SOURCE_DIRECTORY):
                if os.path.isdir(os.path.join(SOURCE_DIRECTORY, item)) and item in FOLDER_ID_TO_NAME:
                    found_matches = True
                    break
            
            if not found_matches:
                unreal.log_error("No folders in the source directory match your FOLDER_ID_TO_NAME dictionary.")
                unreal.log(f"Folders found in {SOURCE_DIRECTORY}:")
                for item in os.listdir(SOURCE_DIRECTORY):
                    if os.path.isdir(os.path.join(SOURCE_DIRECTORY, item)):
                        unreal.log(f"  - {item}")
                unreal.log("\nPlease update your FOLDER_ID_TO_NAME dictionary to match these folder names.")
            else:
                results, output_file = import_textures_and_create_labels()
                if results:
                    unreal.log(f"\n✓ Process completed successfully!")
                    unreal.log(f"✓ Processed {len(results)} folders")
                    unreal.log(f"✓ Exported data to: {output_file}")
                    
                    # Optional: Set cook settings
                    unreal.log("\n" + "=" * 60)
                    unreal.log("MANUAL STEPS NEEDED:")
                    unreal.log("=" * 60)
                    unreal.log("1. Set 'Cook Always' for each label")
                    unreal.log("2. Disable redirects for each label")
                    unreal.log("3. Set priority to 1 for each label")
                    unreal.log("=" * 60)
                else:
                    unreal.log_error("\n✗ Process failed or no labels were created!")
    
    unreal.log("=" * 60)