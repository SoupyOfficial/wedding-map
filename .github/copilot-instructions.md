## Wedding Planning OCR Pipeline

This workspace provides wedding planning automation with Copilot prompts for organizing vendor information from photos.

### Key Features
- Batch OCR processing of wedding planning documents
- Smart tag classification (venue, budget, timeline, etc.)
- Markdown consolidation with frontmatter metadata
- Copilot-friendly organization prompts
- RTF export for MindMeister integration

### Copilot Usage Patterns
When working with `src/master.md`, use these prompts:

1. **Venue Organization**: "Extract venue data into a **Venues** section with bullets for name, capacity, price, pros, cons. Keep unknowns as 'TBD'."

2. **Budget Normalization**: "Under **Budget**, list all numeric amounts as `Item: $Amount (Due Date)` and normalize currency formats."

3. **Timeline Creation**: "Create **Timeline** with dated tasks sorted ascending. If a date is text (e.g., 'early Nov'), convert to `YYYY-11-05` as an estimate and mark `(est)`."

4. **Tag Mapping**: "Map paragraphs to tags from `normalize.yaml`. Add missing tags where obvious."

### Development Workflow
1. Drop photos in `src/images_raw/`
2. Run OCR: `python tools/ocr_batch.py`
3. Consolidate: `python tools/consolidate.py`
4. Organize with Copilot prompts above
5. Export: `pandoc src/master.md -o dist/wedding_consolidated.rtf --standalone`

### File Structure Context
- `tools/ocr_batch.py`: Main OCR processor with image preprocessing
- `tools/normalize.yaml`: Tag classification rules
- `src/master.md`: Consolidated output for Copilot organization
- `dist/`: Final RTF exports for MindMeister