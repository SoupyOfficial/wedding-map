#!/usr/bin/env python3
"""
Quick OCR test utility for single images
Usage: python quick_test.py [image_name]
"""

import sys
import os

# Add tools to path
sys.path.append('tools')

def test_single_image(image_name=None):
    """Test OCR on a single image"""
    if not image_name:
        image_name = "IMG_1945.jpeg"  # Default test image
    
    from ocr_batch import ocr_one, write_md, classify, exif_datetime
    
    image_path = os.path.join("src/images_raw", image_name)
    
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        available = [f for f in os.listdir("src/images_raw") 
                    if f.lower().endswith(('.jpg', '.jpeg', '.png', '.heic', '.webp'))]
        print(f"Available images: {available[:5]}...")
        return
    
    print(f"🔍 Testing OCR on: {image_name}")
    print("=" * 50)
    
    try:
        # Process the image
        result = ocr_one(image_path)
        
        # Save result
        base = os.path.splitext(image_name)[0]
        tags = classify(result)
        taken_at = exif_datetime(image_path)
        write_md(base, result, tags, taken_at, image_name)
        
        print("\n" + "=" * 50)
        print("✅ OCR RESULT PREVIEW:")
        print("=" * 50)
        print(result[:800] + "..." if len(result) > 800 else result)
        
        print(f"\n📁 Full result saved to: src/ocr_md/{base}.md")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    image_name = sys.argv[1] if len(sys.argv) > 1 else None
    test_single_image(image_name)