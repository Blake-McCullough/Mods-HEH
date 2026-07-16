#pip install Pillow numpy
import os
from PIL import Image
import numpy as np
import sys
from pathlib import Path

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from SHAREDASSETS import COLORS

def change_white_to_color(input_folder=".", output_folder="./colored", target_color=(255, 0, 0), color_name="red"):
    """
    Convert all PNGs with transparent backgrounds and white content to a specific color.
    
    Args:
        input_folder: Folder containing the PNG files
        output_folder: Folder to save colored PNGs
        target_color: RGB tuple (r, g, b) for the target color
        color_name: Name for the output subfolder (e.g., "red", "blue")
    """
    # Create output folder with color name
    full_output_path = os.path.join(output_folder, color_name)
    if not os.path.exists(full_output_path):
        os.makedirs(full_output_path)
    
    # Get all PNG files
    png_files = [f for f in os.listdir(input_folder) 
                 if f.lower().endswith('.png') and 
                 os.path.isfile(os.path.join(input_folder, f))]
    
    if not png_files:
        print(f"No PNG files found in {input_folder}")
        return 0
    
    print(f"Converting to {color_name.upper()} ({target_color})...")
    
    processed = 0
    for filename in png_files:
        try:
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(full_output_path, filename)
            
            # Open and convert to RGBA
            img = Image.open(input_path)
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            data = np.array(img)
            
            # Get alpha channel
            alpha = data[:, :, 3]
            
            # Get RGB channels
            rgb = data[:, :, :3]
            
            # Calculate luminance to detect white
            luminance = rgb.mean(axis=2)
            
            # Create mask for white pixels (with tolerance)
            white_mask = (luminance > 200) & (alpha > 10)
            
            # Apply color to white pixels
            new_data = data.copy()
            new_data[white_mask, 0] = target_color[0]  # R
            new_data[white_mask, 1] = target_color[1]  # G
            new_data[white_mask, 2] = target_color[2]  # B
            
            # Save
            new_img = Image.fromarray(new_data, 'RGBA')
            new_img.save(output_path)
            
            processed += 1
            
        except Exception as e:
            print(f"✗ Error processing {filename}: {str(e)}")
    
    print(f"✓ Saved {processed} images to {full_output_path}")
    return processed

def process_all_colors(input_folder=".", output_folder="./colored"):
    """
    Process PNGs for all main colors.
    """
    # Define main colors with names
 
    
    total_processed = 0
    for color_name, rgb in COLORS.items():
        processed = change_white_to_color(input_folder, output_folder, rgb, color_name)
        total_processed += processed
    
    print(f"\n✅ Complete! Processed {total_processed} images across {len(COLORS)} colors")
    print(f"📁 All files saved in: {output_folder}/[color_name]/")



# Main execution
if __name__ == "__main__":
    ASSETLOCATION = Path(   
        r"C:\Users\Blake\Documents\Unreal Projects\Marvel\Plugins\MarvelGAS\Content\Marvel\UI\Common\Textures\AbilityIcon"
    )
    for asset_folder in ASSETLOCATION.iterdir():
        if not asset_folder.is_dir():
            continue
        
        asset_id = asset_folder.name
        print(f"Processing Asset ID: {asset_id}")

        colored_folder = asset_folder / "colored"
        # Option 1: Process all main colors
        process_all_colors(asset_folder,colored_folder)