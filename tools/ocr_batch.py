import os, re, json, yaml, base64, time
from datetime import datetime
from PIL import Image, ImageOps, ImageFilter, ImageEnhance
from dateutil.parser import parse as dtparse
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

IN_DIR  = "src/images_raw"
OUT_DIR = "src/ocr_md"
RULES   = "tools/normalize.yaml"

os.makedirs(OUT_DIR, exist_ok=True)
rules = yaml.safe_load(open(RULES)) if os.path.exists(RULES) else {}

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def preprocess(p):
    """Enhanced preprocessing for better OCR results"""
    try:
        img = Image.open(p)
        
        # Handle MPO files (iPhone Live Photos)
        if hasattr(img, 'n_frames') and img.n_frames > 1:
            print(f"      📱 Detected MPO file, extracting primary frame...")
            img.seek(0)  # Use the first/primary frame
        
        img = img.convert("RGB")
        
        # OCR-specific enhancements
        img = ImageOps.autocontrast(img, cutoff=2)  # Better contrast with cutoff
        img = img.filter(ImageFilter.SHARPEN)
        
        # Additional enhancement for text documents
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.2)  # Slightly increase contrast
        
        # Resize intelligently - keep high resolution for text but respect API limits
        max_size = 2048
        if max(img.size) > max_size:
            # Use LANCZOS for better quality on text
            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            print(f"      🔍 Resized from {img.size} to fit API limits")
        
        return img
    except Exception as e:
        print(f"      ⚠️ Preprocessing error: {e}")
        # Fallback to simple processing
        img = Image.open(p).convert("RGB")
        if max(img.size) > 2048:
            img.thumbnail((2048, 2048), Image.Resampling.LANCZOS)
        return img

def encode_image(image):
    """Convert PIL Image to base64 string for OpenAI API"""
    import io
    img_buffer = io.BytesIO()
    image.save(img_buffer, format='JPEG', quality=85)
    img_buffer.seek(0)
    return base64.b64encode(img_buffer.read()).decode('utf-8')

def classify(text):
    tags = []
    t = text.lower()
    for tag, kws in rules.get("tags", {}).items():
        if any(k in t for k in kws):
            tags.append(tag)
    return sorted(set(tags))

def guess_title(text, fallback):
    first = next((l.strip() for l in text.splitlines() if l.strip()), "")
    first = re.sub(r"[^A-Za-z0-9 :&/.,-]", "", first)[:80]
    return first or fallback

def exif_datetime(path):
    try:
        from PIL.ExifTags import TAGS
        with Image.open(path) as img:
            exif = img.getexif()
            if exif:
                # Convert tag IDs to names
                byname = {TAGS.get(k, k): v for k, v in exif.items()}
                dt = byname.get("DateTimeOriginal") or byname.get("DateTime")
                return dtparse(dt).isoformat() if dt else None
        return None
    except Exception:
        return None

def validate_stage_output(stage_name, text, min_length=50):
    """Validate stage output quality"""
    if not text or len(text.strip()) < min_length:
        return False, f"Output too short ({len(text)} chars)"
    
    # Check for obvious failures
    failure_indicators = [
        'error occurred', 'failed to process', 'unable to read',
        'image quality too poor', 'text not clear enough'
    ]
    
    text_lower = text.lower()
    for indicator in failure_indicators:
        if indicator in text_lower:
            return False, f"Contains failure indicator: {indicator}"
    
    # For wedding documents, expect some typical elements
    if stage_name == "stage_2":
        has_structure = any(marker in text for marker in ['#', '**', '*', '•', '|', '---'])
        if not has_structure:
            return False, "No markdown structure detected"
    
    return True, "Validation passed"

def calculate_quality_score(raw_text, structured_text):
    """Calculate a simple quality score for the processing"""
    score = 50  # Base score
    
    # Length improvements
    if len(structured_text) > len(raw_text) * 0.8:
        score += 10
    
    # Structure indicators
    structure_markers = ['#', '**', '•', '|', '---', '*']
    structure_count = sum(1 for marker in structure_markers if marker in structured_text)
    score += min(structure_count * 5, 20)
    
    # Wedding-specific content
    wedding_indicators = [
        'venue', 'catering', 'wedding', 'reception', 'ceremony',
        'phone', 'email', '$', 'price', 'contact', 'address'
    ]
    content_score = sum(1 for indicator in wedding_indicators 
                       if indicator.lower() in structured_text.lower())
    score += min(content_score * 2, 20)
    
    return min(score, 100)

def clean_markdown_codeblocks(text):
    """Stage 3: Remove outer markdown code blocks and ensure proper closing"""
    # Look for markdown code blocks that wrap the entire content
    patterns = [
        r'^```\s*markdown\s*\n(.*?)\n```\s*$',  # ```markdown ... ```
        r'^```\s*md\s*\n(.*?)\n```\s*$',       # ```md ... ```
        r'^```\s*\n(.*?)\n```\s*$',            # ``` ... ```
    ]
    
    for pattern in patterns:
        match = re.match(pattern, text.strip(), re.DOTALL)
        if match:
            print(f"      🧹 Stage 3: Removing outer markdown code block...")
            return match.group(1).strip()
    
    # Check for unclosed code blocks at start
    if text.strip().startswith('```'):
        lines = text.strip().split('\n')
        if len(lines) > 1:
            # Remove first line if it's a code block opener
            first_line = lines[0].strip()
            if re.match(r'^```\s*(markdown|md)?\s*$', first_line):
                content = '\n'.join(lines[1:])
                # Check if there's a closing ``` at the end
                if content.rstrip().endswith('```'):
                    content = content.rstrip()[:-3].rstrip()
                print(f"      🧹 Stage 3: Removing unclosed markdown code block...")
                return content.strip()
    
    # No code blocks found, return as-is
    return text

def ocr_one(img_path, max_retries=3):
    """Three-stage OCR: Extract text, structure it, then clean code blocks"""
    processing_metadata = {
        "attempts": 0,
        "stage_1_length": 0,
        "stage_2_length": 0,
        "quality_score": 0,
        "validations": {}
    }
    
    for attempt in range(max_retries):
        processing_metadata["attempts"] = attempt + 1
        
        try:
            # Stage 1: Raw text extraction with formatting preservation
            img = preprocess(img_path)
            base64_image = encode_image(img)
            
            print(f"      📄 Stage 1: Extracting raw text...")
            
            # Adaptive token limits based on image size
            img_area = img.size[0] * img.size[1]
            max_tokens_stage1 = 4000 if img_area < 1000000 else 5000
            
            stage1_response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text", 
                                "text": """Please transcribe all text visible in this image with EXACT formatting preservation. This is a wedding planning document.

CRITICAL FORMATTING REQUIREMENTS:
• Preserve all line breaks, spacing, and indentation exactly as shown
• Maintain bullet points, numbered lists, and table structures
• Keep headers, subheaders, and section divisions intact
• Preserve alignment (left, center, right) when visible
• Maintain any special characters, symbols, or dividers (|, -, •, etc.)
• Keep phone numbers, prices, and dates in their original format
• Preserve any bold, italic, or different font styling cues through markdown

CONTENT TO EXTRACT:
- Company/venue names with exact capitalization
- Complete contact information (phones, emails, websites)
- Pricing with currency symbols and formatting
- Addresses with full formatting
- Lists and categories as they appear
- Any terms, conditions, or fine print

FORMATTING OUTPUT:
Use markdown formatting to preserve document structure:
- Headers: # ## ### 
- Lists: • - * for bullets, 1. 2. 3. for numbers
- Tables: | Column | Format | when applicable
- Bold: **text** for emphasized text
- Spacing: Maintain blank lines between sections

Return ONLY the transcribed text with preserved formatting - no commentary or interpretation."""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=max_tokens_stage1,
                timeout=90  # Longer timeout for complex images
            )
            
            raw_text = stage1_response.choices[0].message.content or ""
            processing_metadata["stage_1_length"] = len(raw_text)
            
            # Validate Stage 1 output
            is_valid, validation_msg = validate_stage_output("stage_1", raw_text)
            processing_metadata["validations"]["stage_1"] = {"valid": is_valid, "message": validation_msg}
            
            if not is_valid:
                print(f"      ⚠️ Stage 1 validation failed: {validation_msg}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
            
            # Check for refusal in Stage 1
            if any(phrase in raw_text.lower() for phrase in [
                'i\'m sorry', 'i can\'t', 'i cannot', 'unable to transcribe', 
                'can\'t assist', 'sorry, i can\'t', 'i\'m unable'
            ]):
                if attempt < max_retries - 1:
                    print(f"      ⚠️  Stage 1 attempt {attempt + 1} was refused, retrying...")
                    time.sleep(2)
                    continue
                else:
                    return raw_text  # Return the refusal if all attempts fail
            
            # Stage 2: Intelligent structuring
            print(f"      🎨 Stage 2: Structuring content...")
            time.sleep(1)  # Brief pause between API calls
            
            # Adaptive token limits for Stage 2
            max_tokens_stage2 = min(4500 if len(raw_text) > 2000 else 3500, 6000)
            
            stage2_response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a wedding-planning document formatter. "
                            "Your job is to transform raw OCR output into clean, scannable, professional Markdown while preserving every factual detail exactly. "
                            "STRICT RULES:\n"
                            "- Return ONLY the formatted Markdown content (no commentary, no analysis, no metadata, no code fences).\n"
                            "- Do NOT include YAML frontmatter (the caller will add frontmatter).\n"
                            "- Preserve all original facts, punctuation, numbers, phone numbers, addresses, and prices.\n"
                            "- When a value is missing or unreadable, use the literal string 'TBD'.\n"
                            "- Do not invent new facts; if uncertain, mark as 'TBD' or append '(est)' for estimated dates.\n"
                            "- Keep lists, tables, headings, and emphasis concise and consistent.\n"
                        )
                    },
                    {
                        "role": "user",
                        "content": f"""Structure this wedding planning text into professional, information-dense markdown.

RAW OCR TEXT (do not echo this block back verbatim; use only to extract and structure information):
{raw_text}

PRIMARY OUTPUT SECTIONS (include only those with content; you may create additional sensible sections):
- Venues
- Services
- Pricing / Budget
- Timeline
- Contacts
- Policies / Notes
- Other

FORMAT RULES (apply exactly):
1) Venue Organization:
   - Create a "Venues" section. For each venue, provide bullets for:
     - Name: **Company Name**
     - Capacity: numeric or 'TBD'
     - Price: $Amount or 'TBD'
     - Pros: • bullet list
     - Cons: • bullet list
   - Keep unknowns as 'TBD'.

   Example:
   Venues
   - Name: **The Grand Hall**
     Capacity: 200
     Price: $5,000
     Pros: • Large dance floor • Included AV
     Cons: • No outdoor space

2) Budget Normalization:
   - Under "Budget" or "Pricing", list all monetary amounts as:
     Item: $Amount (Due Date)
   - Normalize currency formatting to a dollar sign and digits (e.g., $5,000.00 or $5000).
   - If a due date is present, convert to ISO YYYY-MM-DD; if a date is fuzzy (e.g., "early Nov"), convert to an estimate YYYY-11-05 and append " (est)". If year is missing, choose the nearest reasonable year and mark "(est)". If no date, omit parentheses.
   - Keep the original currency/format next to normalized if it differs, in parentheses.

   Example:
   Budget
   - Venue Deposit: $5,000 (2025-06-01)
   - Catering: $4,500 ($4,500.00) (Due: 2025-10-01)

3) Timeline Creation:
   - Create a "Timeline" section with dated tasks sorted ascending by date.
   - Convert fuzzy dates to ISO with "(est)" as above.
   - Use "YYYY-MM-DD — Task description" format.

   Example:
   Timeline
   - 2025-06-01 — Venue deposit due
   - 2025-11-05 (est) — Final guest count (early Nov)

4) Contacts:
   - Format contacts uniformly as:
     **Company/Person Name** — Website | Phone | Email
   - If any field is missing, use 'TBD' for that field.

5) Pricing / Tables:
   - When multiple price items appear, prefer a Markdown table:
     | Item | Price | Details |
   - If a table is not appropriate, use bullet lines as in Budget normalization.

6) Lists and Emphasis:
   - Use bullets (•) for unordered lists and numbers (1., 2., 3.) for ordered lists.
   - Use **bold** for names/titles and *italic* for notes/terms.

7) Tag Mapping (suggested):
   - At the end include a small "Suggested Tags:" YAML-style list (not full frontmatter), e.g.:
     Suggested Tags:
     - venue
     - pricing
   - Derive tags from content (venue, budget, timeline, contacts, policy, catering, florist, music, etc.). Keep tags short, lowercase, hyphenated if needed.

ADDITIONAL GUIDELINES:
- Prefer clarity and scannability over verbosity.
- Do not wrap your output in code fences or add any extra explanation lines.
- If the OCR text contains full blocks that look like tables, preserve them as Markdown tables where possible.
- If you must make a best-effort normalization (dates, currency), always mark estimates with "(est)".

Now generate the cleaned, structured Markdown using the RAW OCR TEXT above as the source. Output only the Markdown document."""
                    }
                ],
                max_tokens=max_tokens_stage2,
                timeout=90
            )
            
            structured_text = stage2_response.choices[0].message.content or ""
            processing_metadata["stage_2_length"] = len(structured_text)
            
            # Validate Stage 2 output
            is_valid, validation_msg = validate_stage_output("stage_2", structured_text)
            processing_metadata["validations"]["stage_2"] = {"valid": is_valid, "message": validation_msg}
            
            if not is_valid:
                print(f"      ⚠️ Stage 2 validation failed: {validation_msg}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
            
            # Stage 3: Clean markdown code blocks
            cleaned_text = clean_markdown_codeblocks(structured_text)
            
            # Calculate quality score
            quality_score = calculate_quality_score(raw_text, cleaned_text)
            processing_metadata["quality_score"] = quality_score
            
            print(f"      ✅ Processing complete (Quality: {quality_score}/100)")
            
            # Add processing metadata
            final_text = cleaned_text + f"\n\n---\n*Three-stage OCR processing: {os.path.basename(img_path)} (Quality: {quality_score}/100)*"
            
            return re.sub(r"\n{4,}", "\n\n\n", final_text).strip()
            
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2
                print(f"      ❌ Attempt {attempt + 1} failed: {e}")
                print(f"      ⏳ Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"      ❌ Failed after {max_retries} attempts: {e}")
                return f"ERROR: Three-stage OCR failed after {max_retries} attempts - {str(e)}"

def write_md(base, text, tags, taken_at, src):
    title = guess_title(text, base)
    front = {
        "title": title,
        "tags": tags,
        "source_image": src,
        "taken_at": taken_at,
        "created_at": datetime.utcnow().isoformat()+"Z",
        "processing_method": "three_stage_ocr",
        "stage_1": "raw_text_extraction", 
        "stage_2": "intelligent_structuring",
        "stage_3": "markdown_cleanup"
    }
    md = f"---\n{yaml.safe_dump(front, sort_keys=False)}---\n\n{text}\n"
    out = os.path.join(OUT_DIR, base + ".md")
    open(out, "w", encoding="utf-8").write(md)

def main():
    # Check for OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Error: OPENAI_API_KEY environment variable not set.")
        print("Please create a .env file with your OpenAI API key:")
        print("OPENAI_API_KEY=your_api_key_here")
        return
    
    # Check for single image debug mode
    debug_single = os.getenv('DEBUG_SINGLE_IMAGE')
    if debug_single:
        print(f"🔍 Debug mode: Processing single image '{debug_single}'")
        files_to_process = [debug_single] if debug_single in os.listdir(IN_DIR) else []
        if not files_to_process:
            print(f"❌ Debug image '{debug_single}' not found in {IN_DIR}")
            return
    else:
        files_to_process = [fn for fn in sorted(os.listdir(IN_DIR)) 
                          if fn.lower().endswith((".png",".jpg",".jpeg",".heic",".webp"))]
    
    processed_count = 0
    error_count = 0
    
    print(f"📸 Processing {len(files_to_process)} image(s)...")
    print(f"📁 Input: {IN_DIR}")
    print(f"📁 Output: {OUT_DIR}")
    print("-" * 50)
    
    for fn in files_to_process:
        path = os.path.join(IN_DIR, fn)
        base = os.path.splitext(fn)[0]
        
        print(f"\n🔄 Processing {fn}...")
        
        try:
            text = ocr_one(path)
            tags = classify(text)
            taken_at = exif_datetime(path)
            write_md(base, text, tags, taken_at, fn)
            processed_count += 1
            print(f"✅ {fn} processed successfully")
            
            # Small delay to be respectful of API rate limits (skip in debug mode)
            if not debug_single:
                time.sleep(1)
            
        except Exception as e:
            print(f"❌ Error processing {fn}: {e}")
            error_count += 1
    
    print(f"\n" + "=" * 50)
    print(f"🎉 Processing complete!")
    print(f"✅ Successfully processed: {processed_count} files")
    if error_count > 0:
        print(f"❌ Errors: {error_count} files")
    print(f"📁 Output directory: {OUT_DIR}")
    
    if debug_single:
        # Show the processed content for debugging
        output_file = os.path.join(OUT_DIR, f"{os.path.splitext(debug_single)[0]}.md")
        if os.path.exists(output_file):
            print(f"\n📄 Debug output preview:")
            print("-" * 30)
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()
                print(content[:800] + "..." if len(content) > 800 else content)

if __name__ == "__main__":
    main()