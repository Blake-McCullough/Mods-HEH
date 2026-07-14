import unreal
import re
import os

def create_labels_and_export():
    """
    Creates individual PrimaryAssetLabel for each texture with sequential chunk IDs starting from 100.
    Exports a file with chunk ID and filename.
    """
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    asset_library = unreal.EditorAssetLibrary()
    
    # Your source folder
    source_folder = "/Game/Marvel/UI/Textures/Ability/CollaborativeAbility/Icon"
    
    # Where to save the labels (Content root)
    label_folder = "/Game"
    
    # The additional asset that all labels need
    additional_asset_path = "/Game/Marvel/Environment/NewYork/NewYorkE01/CustomProps/Tex/SM_NewYorkE01Component149M/T_NewYorkE01Component149M_02_D.T_NewYorkE01Component149M_02_D"
    
    # Output file path (saved in the project's Saved folder)
    output_file = os.path.join(unreal.Paths.project_saved_dir(), "ChunkID_Export.txt")
    
    # Starting chunk ID
    base_chunk_id = 100
    
    # Load the PrimaryAssetLabel class
    label_class = unreal.load_class(None, "/Script/Engine.PrimaryAssetLabel")
    
    if not label_class:
        unreal.log_error("Failed to load PrimaryAssetLabel class.")
        return None
    
    # Load the additional asset once
    unreal.log(f"Loading additional asset: {additional_asset_path}")
    additional_asset = asset_library.load_asset(additional_asset_path)
    
    if not additional_asset:
        unreal.log_error(f"Failed to load additional asset: {additional_asset_path}")
        return None
    
    unreal.log(f"✓ Successfully loaded additional asset: {additional_asset.get_name()}")
    
    # Find all assets in the folder
    unreal.log(f"Scanning folder: {source_folder}")
    all_asset_paths = asset_library.list_assets(source_folder, recursive=False)
    
    if not all_asset_paths:
        unreal.log_warning(f"No assets found in {source_folder}")
        return None
    
    # Filter out existing label assets
    asset_paths = []
    for path in all_asset_paths:
        path_parts = path.split('/')
        full_filename = path_parts[-1]
        if '.' in full_filename:
            asset_name = full_filename.split('.')[0]
        else:
            asset_name = full_filename
        
        if not asset_name.startswith("Label_"):
            asset_paths.append(path)
    
    if not asset_paths:
        unreal.log_warning(f"No texture assets found in {source_folder}")
        return None
    
    unreal.log(f"Found {len(asset_paths)} texture assets")
    
    created_labels = []
    output_lines = []
    
    # Add header to output
    output_lines.append("chunkID | filename")
    output_lines.append("-" * 50)
    
    # Process each asset with sequential chunk IDs
    for index, asset_path in enumerate(asset_paths):
        try:
            # Calculate chunk ID: start from 100 and increment by 1 for each asset
            chunk_id = base_chunk_id + index
            
            path_parts = asset_path.split('/')
            full_filename = path_parts[-1]
            if '.' in full_filename:
                asset_name = full_filename.split('.')[0]
            else:
                asset_name = full_filename
            
            label_name = f"Label_{asset_name}"
            source_asset = asset_library.load_asset(asset_path)
            
            if not source_asset:
                continue
            
            # Delete existing label at /Game/
            existing_label_path = f"{label_folder}/{label_name}.{label_name}"
            if asset_library.does_asset_exist(existing_label_path):
                asset_library.delete_asset(existing_label_path)
            
            # Create label at /Game/
            label_asset = asset_tools.create_asset(
                asset_name=label_name,
                package_path=label_folder,
                asset_class=label_class,
                factory=unreal.DataAssetFactory()
            )
            
            if not label_asset:
                continue
            
            # Set explicit assets with BOTH assets
            label_asset.set_editor_property("explicit_assets", [source_asset, additional_asset])
            
            # Try to set chunk ID with various property names
            chunk_set = False
            for prop_name in ['ChunkID', 'chunk_id', 'ChunkId', 'chunkid', 'Chunk']:
                try:
                    label_asset.set_editor_property(prop_name, chunk_id)
                    chunk_set = True
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
                                break
                            except:
                                continue
                except:
                    pass
            
            # Set apply recursively
            for prop_name in ['apply_recursively', 'ApplyRecursively', 'bApplyRecursively']:
                try:
                    label_asset.set_editor_property(prop_name, False)
                    break
                except:
                    continue
            
            # Save the label
            asset_library.save_loaded_asset(label_asset)
            
            # Store for reporting
            created_labels.append({
                'label_name': label_name,
                'chunk_id': chunk_id,
                'source_asset': asset_name,
                'additional_asset': additional_asset.get_name()
            })
            
            # Add to output lines for file
            output_lines.append(f"{chunk_id} | {asset_name}")
            
            unreal.log(f"  [{index + 1}/{len(asset_paths)}] ✓ {label_name} → Chunk ID: {chunk_id}")
            
        except Exception as e:
            unreal.log_error(f"  Error processing {asset_path}: {str(e)}")
    
    # Write output file
    try:
        with open(output_file, 'w') as f:
            f.write('\n'.join(output_lines))
        unreal.log(f"\n✓ Output file saved to: {output_file}")
    except Exception as e:
        unreal.log_error(f"Failed to write output file: {str(e)}")
    
    # Print summary report
    unreal.log("\n" + "=" * 80)
    unreal.log("SUMMARY: Created Labels with Sequential Chunk IDs (starting from 100)")
    unreal.log("=" * 80)
    
    for label_info in created_labels:
        unreal.log(f"  {label_info['label_name']:45} | Chunk ID: {label_info['chunk_id']:10}")
    
    unreal.log("=" * 80)
    unreal.log(f"Total labels created: {len(created_labels)}")
    unreal.log(f"Chunk ID range: {base_chunk_id} to {base_chunk_id + len(created_labels) - 1}")
    unreal.log(f"Output file: {output_file}")
    unreal.log("=" * 80)
    
    # Also print the output lines to the log for easy viewing
    unreal.log("\n" + "=" * 80)
    unreal.log("EXPORTED DATA (chunkID | filename):")
    unreal.log("=" * 80)
    for line in output_lines:
        unreal.log(line)
    unreal.log("=" * 80)
    
    return created_labels, output_file

# --- Execute the script ---
if __name__ == "__main__":
    unreal.log("=" * 50)
    unreal.log("Creating individual labels with sequential chunk IDs...")
    results, output_file = create_labels_and_export()
    if results:
        unreal.log(f"\n✓ Process completed successfully!")
        unreal.log(f"✓ Created {len(results)} labels at /Game/")
        unreal.log(f"✓ Chunk IDs: 100 to {99 + len(results)}")
        unreal.log(f"✓ Exported data to: {output_file}")
    else:
        unreal.log_error("\n✗ Process failed!")
    unreal.log("=" * 50)

    #manually go and set the cook always, disable redirects, and priority 1