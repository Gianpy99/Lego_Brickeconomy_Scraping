"""
Quick verification that web pages are working correctly
"""

import os
from pathlib import Path

def check_web_files():
    """Check that web files exist and contain correct data"""
    web_dir = Path("lego_database")
    
    files_to_check = [
        "index.html",
        "sets.html", 
        "minifigs.html",
        "analytics.html"
    ]
    
    print("=== Web Files Status ===")
    for file_name in files_to_check:
        file_path = web_dir / file_name
        if file_path.exists():
            file_size = file_path.stat().st_size
            print(f"✅ {file_name}: {file_size:,} bytes")
            
            # Check for image path corrections in JavaScript
            if file_name in ["sets.html", "minifigs.html"]:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "lego_database/images/" in content:
                        print(f"   📸 Contains corrected forward-slash image paths")
                    else:
                        print(f"   ⚠️ May still have backslash paths")
        else:
            print(f"❌ {file_name}: Missing")
    
    print(f"\n=== Image Directory ===")
    images_dir = web_dir / "images"
    if images_dir.exists():
        image_count = len(list(images_dir.glob("*.jpg")))
        print(f"✅ {image_count} images available")
    else:
        print("❌ Images directory missing")

if __name__ == "__main__":
    check_web_files()
