import os
import subprocess
import sys
import tempfile
import json
import webbrowser
from pathlib import Path

def read_chunk_id_file(file_path=None):
    """
    Reads the ChunkID_Export.txt file and returns the data.
    """
    if file_path is None:
        possible_paths = [
            "ChunkID_Export.txt",
            os.path.join(os.getcwd(), "ChunkID_Export.txt"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "ChunkID_Export.txt"),
            os.path.join(os.path.expanduser("~"), "Desktop", "ChunkID_Export.txt"),
            r"C:\Users\Blake\Documents\Unreal Projects\Marvel\Saved\ChunkID_Export.txt"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                file_path = path
                break
        
        if file_path is None:
            print("Error: ChunkID_Export.txt not found. Please specify the file path.")
            return None, None
    
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return None, None
    
    print(f"Reading: {file_path}")
    
    data = []
    with open(file_path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            if line and '|' in line and not line.startswith('-') and not line.startswith('chunkID'):
                parts = line.split('|')
                if len(parts) >= 2:
                    chunk_id = parts[0].strip()
                    filename = parts[1].strip()
                    data.append({
                        'chunk_id': chunk_id,
                        'filename': filename,
                        'input': ''
                    })
    
    return data, file_path

def get_image_path(filename, base_path=None):
    """
    Gets the full path to the image for a given filename.
    """
    if base_path is None:
        base_path = r"C:\Users\Blake\Documents\Unreal Projects\Marvel\Content\Marvel\UI\Textures\Ability\CollaborativeAbility\Icon"
    
    extensions = ['.png', '.PNG', '.tga', '.TGA', '.jpg', '.JPG', '.jpeg', '.JPEG', '.bmp', '.BMP']
    
    for ext in extensions:
        image_path = os.path.join(base_path, f"{filename}{ext}")
        if os.path.exists(image_path):
            return image_path
    
    return None

def open_in_browser(html_path):
    """
    Tries multiple methods to open the HTML file in a browser.
    """
    # Method 1: Try webbrowser module
    try:
        webbrowser.open(html_path)
        return True
    except:
        pass
    
    # Method 2: Try os.startfile (Windows)
    try:
        if sys.platform == 'win32':
            os.startfile(html_path)
            return True
    except:
        pass
    
    # Method 3: Try subprocess with default browser
    try:
        if sys.platform == 'win32':
            subprocess.run(['start', html_path], shell=True)
            return True
        elif sys.platform == 'darwin':
            subprocess.run(['open', html_path])
            return True
        else:
            subprocess.run(['xdg-open', html_path])
            return True
    except:
        pass
    
    return False

def web_annotation_mode():
    """
    Web-based annotation tool with a self-contained HTML file.
    """
    print("=" * 80)
    print("IMAGE ANNOTATION TOOL - Web Mode")
    print("=" * 80)
    
    file_path = input("Enter path to ChunkID_Export.txt (press Enter for default): ").strip()
    if not file_path:
        file_path = None
    
    data, source_file = read_chunk_id_file(file_path)
    if not data:
        print("No data found. Please make sure ChunkID_Export.txt exists.")
        return
    
    print(f"\nFound {len(data)} entries to process.")
    
    image_base = input("\nEnter the folder path containing images (press Enter for default): ").strip()
    if not image_base:
        image_base = r"C:\Users\Blake\Documents\Unreal Projects\Marvel\Content\Marvel\UI\Textures\Ability\CollaborativeAbility\Icon"
    
    # Create HTML content with embedded data
    html_content = f'''<!DOCTYPE html>
<html>
<head>
    <title>Image Annotation Tool</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; max-width: 900px; margin: auto; background: #f5f5f5; }}
        .header {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }}
        .header h1 {{ margin: 0; color: #333; }}
        .header .sub {{ color: #666; margin: 5px 0; }}
        .entry {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }}
        .filename {{ font-size: 18px; font-weight: bold; color: #333; }}
        .chunk {{ color: #666; font-size: 14px; }}
        .image-container {{ margin: 15px 0; text-align: center; background: #f9f9f9; border-radius: 4px; padding: 10px; min-height: 100px; }}
        .image-container img {{ max-width: 100%; max-height: 400px; border-radius: 4px; }}
        .image-container .not-found {{ color: #999; padding: 40px; }}
        input[type="text"] {{ width: 100%; padding: 12px; margin: 10px 0; border: 2px solid #ddd; border-radius: 4px; font-size: 16px; box-sizing: border-box; }}
        input[type="text"]:focus {{ border-color: #007bff; outline: none; }}
        .status {{ padding: 8px; border-radius: 4px; margin: 5px 0; }}
        .status.annotated {{ background: #d4edda; color: #155724; }}
        .status.skipped {{ background: #fff3cd; color: #856404; }}
        .status.pending {{ background: #f8f9fa; color: #6c757d; }}
        .nav {{ display: flex; gap: 10px; margin: 20px 0; flex-wrap: wrap; }}
        .nav button {{ padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; }}
        .nav button:hover {{ background: #0056b3; }}
        .nav button:disabled {{ background: #ccc; cursor: not-allowed; }}
        .nav .save-btn {{ background: #28a745; }}
        .nav .save-btn:hover {{ background: #1e7e34; }}
        .nav .skip-btn {{ background: #ffc107; color: #333; }}
        .nav .skip-btn:hover {{ background: #e0a800; }}
        #progress {{ font-weight: bold; color: #333; margin: 10px 0; }}
        #message {{ padding: 10px; border-radius: 4px; margin: 10px 0; display: none; }}
        #message.success {{ background: #d4edda; color: #155724; display: block; }}
        #message.error {{ background: #f8d7da; color: #721c24; display: block; }}
        .shortcuts {{ color: #666; font-size: 12px; margin: 5px 0; }}
        .annotation-count {{ float: right; color: #666; }}
        .image-path {{ font-size: 11px; color: #999; word-break: break-all; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🖼️ Image Annotation Tool</h1>
        <div class="sub">Annotate images with chunk IDs</div>
        <div id="progress">Entry 1 / {len(data)} <span class="annotation-count" id="annotation-count"></span></div>
    </div>
    
    <div id="message"></div>
    <div id="entry-container"></div>
    
    <div class="nav">
        <button onclick="previousEntry()" id="prev-btn">◀ Previous</button>
        <button onclick="nextEntry()" id="next-btn">Next ▶</button>
        <button onclick="skipEntry()" class="skip-btn" id="skip-btn">⏭️ Skip</button>
        <button onclick="saveAndFinish()" class="save-btn">💾 Save & Finish</button>
    </div>
    
    <div class="shortcuts">
        <strong>Keyboard shortcuts:</strong> Enter = Next, Shift+Enter = Save, Esc = Skip
    </div>
    
    <script>
        const data = {json.dumps(data)};
        const imageBase = "{image_base.replace('\\', '/')}";
        let currentIndex = 0;
        let annotations = {{}};
        let skipSet = new Set();
        
        function updateAnnotationCount() {{
            let count = 0;
            for (let entry of data) {{
                if (annotations[entry.filename] && !skipSet.has(entry.filename)) {{
                    count++;
                }}
            }}
            document.getElementById('annotation-count').textContent = `Annotated: ${{count}} / ${{data.length}}`;
        }}
        
        function displayEntry(index) {{
            const entry = data[index];
            if (!entry) return;
            
            document.getElementById('progress').textContent = `Entry ${{index + 1}} / ${{data.length}} `;
            document.getElementById('prev-btn').disabled = index === 0;
            document.getElementById('next-btn').disabled = index === data.length - 1;
            
            const container = document.getElementById('entry-container');
            const hasAnnotation = annotations[entry.filename] !== undefined;
            const hasSkipped = skipSet.has(entry.filename);
            
            let statusHtml = '';
            if (hasSkipped) {{
                statusHtml = '<div class="status skipped">⏭️ Skipped</div>';
            }} else if (hasAnnotation && annotations[entry.filename]) {{
                statusHtml = `<div class="status annotated">✅ Annotated: "${{annotations[entry.filename]}}"</div>`;
            }} else {{
                statusHtml = '<div class="status pending">⏳ Awaiting input...</div>';
            }}
            
            // Build image path
            const imagePath = `${{imageBase}}/${{entry.filename}}.png`;
            
            container.innerHTML = `
                <div class="entry">
                    <div class="filename">📄 ${{entry.filename}}</div>
                    <div class="chunk">Chunk ID: ${{entry.chunk_id}}</div>
                    <div class="image-container">
                        <img src="${{imagePath}}" 
                             onerror="this.style.display='none'; this.parentElement.innerHTML='<div class=\\'not-found\\'>⚠️ Image not found: ${{entry.filename}}.png<br><span class=\\'image-path\\'>Searched in: ${{imagePath}}</span></div>';" 
                             style="max-width: 100%; max-height: 400px;" />
                    </div>
                    <div id="status-container">${{statusHtml}}</div>
                    <input type="text" id="annotation-input" 
                           placeholder="Enter your annotation..." 
                           value="${{hasAnnotation ? annotations[entry.filename] : ''}}"
                           autofocus />
                </div>
            `;
            
            const input = document.getElementById('annotation-input');
            if (input) {{
                input.addEventListener('keydown', function(e) {{
                    if (e.key === 'Enter' && !e.shiftKey) {{
                        e.preventDefault();
                        saveCurrentAnnotation();
                        nextEntry();
                    }} else if (e.key === 'Enter' && e.shiftKey) {{
                        e.preventDefault();
                        saveCurrentAnnotation();
                    }} else if (e.key === 'Escape') {{
                        skipEntry();
                    }}
                }});
                input.focus();
            }}
            
            updateAnnotationCount();
        }}
        
        function saveCurrentAnnotation() {{
            const input = document.getElementById('annotation-input');
            if (!input) return;
            
            const entry = data[currentIndex];
            if (!entry) return;
            
            const value = input.value.trim();
            if (value) {{
                annotations[entry.filename] = value;
                skipSet.delete(entry.filename);
                updateStatus();
                updateAnnotationCount();
            }}
        }}
        
        function updateStatus() {{
            const entry = data[currentIndex];
            if (!entry) return;
            
            const statusContainer = document.getElementById('status-container');
            if (skipSet.has(entry.filename)) {{
                statusContainer.innerHTML = '<div class="status skipped">⏭️ Skipped</div>';
            }} else if (annotations[entry.filename]) {{
                statusContainer.innerHTML = `<div class="status annotated">✅ Annotated: "${{annotations[entry.filename]}}"</div>`;
            }} else {{
                statusContainer.innerHTML = '<div class="status pending">⏳ Awaiting input...</div>';
            }}
        }}
        
        function skipEntry() {{
            const entry = data[currentIndex];
            if (!entry) return;
            
            skipSet.add(entry.filename);
            delete annotations[entry.filename];
            updateStatus();
            const input = document.getElementById('annotation-input');
            if (input) input.value = '';
            updateAnnotationCount();
            nextEntry();
        }}
        
        function nextEntry() {{
            saveCurrentAnnotation();
            if (currentIndex < data.length - 1) {{
                currentIndex++;
                displayEntry(currentIndex);
            }}
        }}
        
        function previousEntry() {{
            saveCurrentAnnotation();
            if (currentIndex > 0) {{
                currentIndex--;
                displayEntry(currentIndex);
            }}
        }}
        
        function saveAndFinish() {{
            saveCurrentAnnotation();
            
            const results = data.map(entry => ({{
                chunk_id: entry.chunk_id,
                filename: entry.filename,
                input: skipSet.has(entry.filename) ? 'SKIPPED' : (annotations[entry.filename] || '')
            }}));
            
            let content = 'chunkID | filename | input\\n';
            content += '----------------------------------------------------------------------\\n';
            for (let item of results) {{
                content += `${{item.chunk_id}} | ${{item.filename}} | ${{item.input}}\\n`;
            }}
            
            const blob = new Blob([content], {{type: 'text/plain'}});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'ChunkID_Export_With_Input.txt';
            a.click();
            URL.revokeObjectURL(url);
            
            const msg = document.getElementById('message');
            msg.className = 'success';
            msg.innerHTML = '✅ Annotations saved! File downloaded as ChunkID_Export_With_Input.txt';
            msg.style.display = 'block';
        }}
        
        displayEntry(0);
    </script>
</body>
</html>'''
    
    # Create a temporary HTML file
    html_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html', encoding='utf-8')
    html_file.write(html_content)
    html_file.close()
    html_path = html_file.name
    
    print(f"\n📄 HTML file created at:")
    print(f"   {html_path}")
    
    # Try to open the browser
    print("\n🌐 Attempting to open browser...")
    opened = open_in_browser(html_path)
    
    if opened:
        print("✅ Browser should be open!")
    else:
        print("⚠️ Could not automatically open browser.")
        print("\nPlease manually open this file in your browser:")
        print(f"   {html_path}")
        print("\nOr copy and paste this path into your browser's address bar.")
    
    print("\n" + "=" * 80)
    print("Web annotation tool is ready.")
    print("When you're done, click 'Save & Finish' to download the results.")
    print("Close the browser window when finished.")
    print("=" * 80)
    
    input("\nPress Enter to close this window and clean up the temp file...")
    
    # Clean up
    try:
        os.unlink(html_path)
        print("Temp file cleaned up.")
    except:
        pass

def console_annotation_mode():
    """
    Console-based annotation tool.
    """
    print("=" * 80)
    print("IMAGE ANNOTATION TOOL - Console Mode")
    print("=" * 80)
    
    file_path = input("Enter path to ChunkID_Export.txt (press Enter for default): ").strip()
    if not file_path:
        file_path = None
    
    data, source_file = read_chunk_id_file(file_path)
    if not data:
        print("No data found. Please make sure ChunkID_Export.txt exists.")
        return
    
    print(f"\nFound {len(data)} entries to process.")
    print("=" * 80)
    print("Commands:")
    print("  - Enter your annotation (text) and press Enter")
    print("  - Type 'skip' to skip the current image")
    print("  - Type 'quit' to exit early")
    print("  - Type 'show' to show the image again")
    print("=" * 80)
    
    image_base = input("\nEnter the folder path containing images (press Enter for default): ").strip()
    if not image_base:
        image_base = r"C:\Users\Blake\Documents\Unreal Projects\Marvel\Content\Marvel\UI\Textures\Ability\CollaborativeAbility\Icon"
    
    if not os.path.exists(image_base):
        print(f"Warning: Image folder not found: {image_base}")
    
    for index, item in enumerate(data):
        filename = item['filename']
        chunk_id = item['chunk_id']
        
        print("\n" + "=" * 80)
        print(f"Entry {index + 1}/{len(data)}")
        print(f"Chunk ID: {chunk_id}")
        print(f"Filename: {filename}")
        print("-" * 80)
        
        image_path = get_image_path(filename, image_base)
        if image_path:
            print(f"📷 Opening image: {image_path}")
            try:
                if sys.platform == 'win32':
                    os.startfile(image_path)
                elif sys.platform == 'darwin':
                    subprocess.run(['open', image_path])
                else:
                    subprocess.run(['xdg-open', image_path])
            except Exception as e:
                print(f"Could not open image: {e}")
        else:
            print(f"⚠️  Image not found for: {filename}")
            print(f"  Full path would be: {os.path.join(image_base, filename + '.png')}")
        
        while True:
            user_input = input("\nEnter annotation (or command): ").strip()
            
            if user_input.lower() == 'quit':
                print("Quitting early...")
                break
            elif user_input.lower() == 'skip':
                print(f"⏭️  Skipped: {filename}")
                item['input'] = 'SKIPPED'
                break
            elif user_input.lower() == 'show':
                if image_path:
                    try:
                        if sys.platform == 'win32':
                            os.startfile(image_path)
                        elif sys.platform == 'darwin':
                            subprocess.run(['open', image_path])
                        else:
                            subprocess.run(['xdg-open', image_path])
                        print("🔄 Image shown again.")
                    except:
                        print("❌ Could not open image.")
                else:
                    print("❌ No image to show.")
                continue
            elif user_input:
                item['input'] = user_input
                print(f"✅ Recorded: {filename} -> '{user_input}'")
                break
        
        if user_input.lower() == 'quit':
            break
    
    output_file = "ChunkID_Export_With_Input.txt"
    with open(output_file, 'w') as f:
        f.write("chunkID | filename | input\n")
        f.write("-" * 70 + "\n")
        for item in data:
            f.write(f"{item['chunk_id']} | {item['filename']} | {item['input']}\n")
    
    print(f"\n✅ Annotations saved to: {output_file}")
    
    total_processed = len([item for item in data if item['input']])
    total_skipped = len([item for item in data if item['input'] == 'SKIPPED'])
    total_annotated = len([item for item in data if item['input'] and item['input'] != 'SKIPPED'])
    print("\n" + "=" * 80)
    print("ANNOTATION SUMMARY")
    print("=" * 80)
    print(f"  Total entries: {len(data)}")
    print(f"  Processed: {total_processed}")
    print(f"  Skipped: {total_skipped}")
    print(f"  Annotated: {total_annotated}")
    print("=" * 80)

def main():
    """
    Main entry point for the standalone tool.
    """
    print("=" * 80)
    print(" 🖼️  STANDALONE IMAGE ANNOTATION TOOL")
    print("=" * 80)
    print("\nThis tool reads ChunkID_Export.txt, displays images, and collects annotations.")
    print("\nSelect mode:")
    print("  1. Console Mode - Simple text-based annotation")
    print("  2. Web Mode - Interactive web interface in your browser")
    print("  3. Help - Show usage information")
    print("=" * 80)
    
    choice = input("\nEnter your choice (1, 2, or 3): ").strip()
    
    if choice == '1':
        console_annotation_mode()
    elif choice == '2':
        web_annotation_mode()
    elif choice == '3':
        print("\n" + "=" * 80)
        print("USAGE INFORMATION")
        print("=" * 80)
        print("1. Make sure ChunkID_Export.txt is in the same folder as this script,")
        print("   or specify the full path when prompted.")
        print("\n2. The script will display each image using your default image viewer.")
        print("\n3. For each image, type your annotation and press Enter.")
        print("\n4. Results will be saved to ChunkID_Export_With_Input.txt")
        print("\n5. The web mode provides a more interactive experience in your browser.")
        print("=" * 80)
    else:
        print("Invalid choice. Please run again and select 1 or 2.")

if __name__ == "__main__":
    main()