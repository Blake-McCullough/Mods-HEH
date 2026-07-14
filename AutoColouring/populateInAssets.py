import unreal
import re

def create_individual_labels_for_textures():
    """
    Creates individual PrimaryAssetLabel for each texture in the CollaborativeAbility/Icon folder.
    Each label is named Label_{filename} and saved at /Game/
    """
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    asset_library = unreal.EditorAssetLibrary()
    
    # Your source folder
    source_folder = "/Game/Marvel/UI/Textures/Ability/CollaborativeAbility/Icon"
    
    # Where to save the labels (Content root)
    label_folder = "/Game"
    
    # Load the PrimaryAssetLabel class
    label_class = unreal.load_class(None, "/Script/Engine.PrimaryAssetLabel")
    
    if not label_class:
        unreal.log_error("Failed to load PrimaryAssetLabel class.")
        return None
    
    # 1. Find all assets in the folder
    unreal.log(f"Scanning folder: {source_folder}")
    all_asset_paths = asset_library.list_assets(source_folder, recursive=False)
    
    if not all_asset_paths:
        unreal.log_warning(f"No assets found in {source_folder}")
        return None
    
    # Filter out existing label assets - only process texture assets
    asset_paths = []
    for path in all_asset_paths:
        # Extract the asset name
        path_parts = path.split('/')
        full_filename = path_parts[-1]
        if '.' in full_filename:
            asset_name = full_filename.split('.')[0]
        else:
            asset_name = full_filename
        
        # Skip assets that are already labels (start with "Label_")
        if not asset_name.startswith("Label_"):
            asset_paths.append(path)
        else:
            unreal.log(f"Skipping existing label: {asset_name}")
    
    if not asset_paths:
        unreal.log_warning(f"No texture assets found in {source_folder} (only labels exist)")
        return None
    
    unreal.log(f"Found {len(asset_paths)} texture assets in the folder (skipped {len(all_asset_paths) - len(asset_paths)} existing labels)")
    
    # Store created labels for reporting
    created_labels = []
    
    # 2. Process each asset individually
    for asset_path in asset_paths:
        try:
            # Extract the asset name from the path
            path_parts = asset_path.split('/')
            full_filename = path_parts[-1]
            
            if '.' in full_filename:
                asset_name = full_filename.split('.')[0]
            else:
                asset_name = full_filename
            
            unreal.log(f"Processing: {asset_name}")
            
            # Create label name: Label_{filename}
            label_name = f"Label_{asset_name}"
            
            # Load the source asset
            source_asset = asset_library.load_asset(asset_path)
            if not source_asset:
                unreal.log_warning(f"  Failed to load: {asset_path}")
                continue
            
            # Check if label already exists at /Game/ and delete it
            existing_label_path = f"{label_folder}/{label_name}.{label_name}"
            if asset_library.does_asset_exist(existing_label_path):
                unreal.log(f"  Deleting existing label at /Game/...")
                asset_library.delete_asset(existing_label_path)
            
            # Create the PrimaryAssetLabel at /Game/
            label_asset = asset_tools.create_asset(
                asset_name=label_name,
                package_path=label_folder,  # This is "/Game"
                asset_class=label_class,
                factory=unreal.DataAssetFactory()
            )
            
            if not label_asset:
                unreal.log_error(f"  Failed to create label for {asset_name}")
                continue
            
            # Extract the number from the asset name for chunk ID
            numbers = re.findall(r'\d+', asset_name)
            if numbers:
                chunk_id = int(numbers[0])
            else:
                chunk_id = 100000
            
            # Set the explicit assets (this works)
            label_asset.set_editor_property("explicit_assets", [source_asset])
            
            # Try to set the chunk ID with various property names
            chunk_set = False
            for prop_name in ['ChunkID', 'chunk_id', 'ChunkId', 'chunkid', 'Chunk']:
                try:
                    # Try to get the property to see if it exists
                    test = label_asset.get_editor_property(prop_name)
                    # If we get here, the property exists, so set it
                    label_asset.set_editor_property(prop_name, chunk_id)
                    unreal.log(f"  Set chunk ID using property: {prop_name} = {chunk_id}")
                    chunk_set = True
                    break
                except:
                    continue
            
            if not chunk_set:
                # Try using PrimaryAssetRules if it exists
                try:
                    # Check if the asset has a "rules" property
                    rules = label_asset.get_editor_property("rules")
                    if rules:
                        # Try different property names on the rules object
                        for rule_prop in ['ChunkID', 'chunk_id', 'ChunkId']:
                            try:
                                rules.set_editor_property(rule_prop, chunk_id)
                                label_asset.set_editor_property("rules", rules)
                                unreal.log(f"  Set chunk ID via rules.{rule_prop} = {chunk_id}")
                                chunk_set = True
                                break
                            except:
                                continue
                except:
                    pass
            
            if not chunk_set:
                unreal.log_warning(f"  Could not set chunk ID for {asset_name}")
            
            # Set apply recursively (try different property names)
            for prop_name in ['apply_recursively', 'ApplyRecursively', 'bApplyRecursively']:
                try:
                    label_asset.set_editor_property(prop_name, False)
                    break
                except:
                    continue
            
            # Save the label at /Game/
            asset_library.save_loaded_asset(label_asset)
            
            # Store for reporting
            created_labels.append({
                'label_name': label_name,
                'chunk_id': chunk_id if chunk_set else "NOT SET",
                'source_asset': asset_name,
                'location': label_folder
            })
            
            unreal.log(f"  ✓ Created: {label_name} at /Game/ with Chunk ID: {chunk_id if chunk_set else 'NOT SET'}")
            
        except Exception as e:
            unreal.log_error(f"  Error processing {asset_path}: {str(e)}")
    
    # 3. Print summary report
    unreal.log("\n" + "=" * 80)
    unreal.log("SUMMARY: Created Labels at /Game/ with Chunk IDs")
    unreal.log("=" * 80)
    
    for label_info in created_labels:
        chunk_display = str(label_info['chunk_id'])
        unreal.log(f"  {label_info['label_name']:50} | Chunk ID: {chunk_display:10} | Contains: {label_info['source_asset']}")
    
    unreal.log("=" * 80)
    unreal.log(f"Total labels created: {len(created_labels)}")
    unreal.log(f"All labels saved at: /Game/")
    unreal.log("=" * 80)
    
    return created_labels

# --- Execute the script ---
if __name__ == "__main__":
    unreal.log("=" * 50)
    unreal.log("Creating individual labels for textures at /Game/...")
    results = create_individual_labels_for_textures()
    if results:
        unreal.log(f"\n✓ Process completed successfully! Created {len(results)} labels at /Game/")
    else:
        unreal.log_error("\n✗ Process failed!")
    unreal.log("=" * 50)