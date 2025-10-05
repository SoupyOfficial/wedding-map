# Consolidation script for wedding planning OCR results
# Merges all markdown files from ocr_md/ into master.md

import os
import glob
from pathlib import Path

def consolidate_markdown():
    """Merge all OCR markdown files into master.md"""
    ocr_dir = Path("src/ocr_md")
    master_file = Path("src/master.md")
    
    if not ocr_dir.exists():
        print("No OCR markdown directory found. Run ocr_batch.py first.")
        return
    
    # Get all markdown files
    md_files = sorted(glob.glob(str(ocr_dir / "*.md")))
    
    if not md_files:
        print("No markdown files found in src/ocr_md/")
        return
    
    # Read master template header
    header = """---
title: "Wedding Planning Master Document - Consolidated"
tags: ["wedding", "planning", "master", "consolidated"]
created_at: "2025-10-05T00:00:00Z"
---

# Wedding Planning Master Document

Consolidated from {} OCR files.

""".format(len(md_files))
    
    # Consolidate all content
    consolidated = [header]
    
    for md_file in md_files:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add separator and content
        filename = os.path.basename(md_file)
        consolidated.append(f"\n## Source: {filename}\n\n{content}\n\n---\n")
    
    # Write consolidated file
    with open(master_file, 'w', encoding='utf-8') as f:
        f.write(''.join(consolidated))
    
    print(f"Consolidated {len(md_files)} files into {master_file}")

if __name__ == "__main__":
    consolidate_markdown()