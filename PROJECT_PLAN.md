# Wedding Planning OCR Pipeline - Three-Phase Project Plan

## Project Overview

Transform wedding planning documents and research into a comprehensive, organized mind map through intelligent OCR processing, Pinterest data gathering, and consolidation.

---

## Phase 1: Enhanced Document Processing ✅ (Current Phase)

### 1.1 Two-Stage OCR Implementation

**Current Status:** In Development  
**Goal:** Process existing wedding planning photos with maximum formatting preservation and intelligent structuring

#### Stage 1: Raw Text Extraction
- **Purpose:** Extract every visible character with basic formatting
- **Model:** GPT-4o with high-detail vision processing
- **Focus:** Preserve line breaks, spacing, lists, headers
- **Output:** Raw text with structural elements intact

#### Stage 2: Intelligent Content Structuring  
- **Purpose:** Transform raw OCR into professional markdown
- **Model:** GPT-4o with specialized formatting instructions
- **Features:**
  - Logical section organization
  - Professional contact info formatting
  - Pricing tables and package structures
  - Enhanced readability with markdown
  - Category-based content grouping

#### Deliverables:
- [ ] Updated `ocr_batch.py` with two-stage processing
- [ ] Enhanced retry logic for failed images
- [ ] Structured output in `src/ocr_md_structured/`
- [ ] Comparison analysis vs single-stage OCR
- [ ] 94%+ success rate maintained

---

## Phase 2: Pinterest Data Integration 📌

### 2.1 Pinterest Data Collection

**Timeline:** After Phase 1 completion  
**Goal:** Scrape and organize pinned wedding planning content

#### 2.1.1 Pinterest API Setup
- **Authentication:** Pinterest Business API access
- **Scope:** Access to pinned boards and saved content
- **Rate Limits:** Implement respectful scraping practices

#### 2.1.2 Content Extraction Strategy
```python
pinterest_data_types = {
    "venue_pins": {
        "boards": ["Wedding Venues", "Reception Locations"],
        "extract": ["venue_name", "location", "pricing_hints", "capacity", "description", "website"]
    },
    "vendor_pins": {
        "boards": ["Wedding Vendors", "Photography", "Catering", "Flowers"],
        "extract": ["business_name", "contact_info", "services", "portfolio_links", "pricing"]
    },
    "inspiration_pins": {
        "boards": ["Wedding Ideas", "Decorations", "Themes"],
        "extract": ["concept", "style", "color_scheme", "budget_range", "diy_instructions"]
    },
    "timeline_pins": {
        "boards": ["Wedding Timeline", "Planning Checklist"],
        "extract": ["task", "deadline", "priority", "vendor_contact", "notes"]
    }
}
```

#### 2.1.3 Pinterest Processing Pipeline
1. **Board Scanning:** Identify all wedding-related boards
2. **Pin Extraction:** Download pin metadata, descriptions, linked content
3. **Image Analysis:** OCR any text in pinned images
4. **Link Following:** Extract info from linked websites (when possible)
5. **Content Classification:** Auto-tag based on content type

#### 2.1.4 Data Structuring
```markdown
# Pinterest Integration Output Structure

## Venue Research
- **Saved Venues:** [From Pinterest boards]
- **Venue Comparisons:** [Extracted from pins/descriptions]
- **Location Preferences:** [Based on pinned locations]

## Vendor Research  
- **Photography:** [Pinned photographers with contact info]
- **Catering:** [Saved catering options and menus]
- **Flowers:** [Florist pins with style preferences]

## Style & Theme Research
- **Color Schemes:** [From inspiration pins]
- **Decoration Ideas:** [DIY and vendor options]
- **Dress & Attire:** [Style preferences and vendors]

## Planning Timeline
- **Saved Checklists:** [From planning pins]
- **Timeline Templates:** [Extracted from pinned schedules]
- **Task Reminders:** [Deadline-based organization]
```

#### Tools & Technologies:
- **Pinterest API:** Official business API for data access
- **Selenium/Playwright:** For browser automation if API insufficient  
- **Beautiful Soup:** HTML parsing for linked content
- **OCR Integration:** Apply two-stage OCR to pinned images
- **Data Storage:** Structured JSON/YAML for processing

#### Deliverables:
- [ ] Pinterest API integration script
- [ ] Automated board scanning and pin extraction
- [ ] OCR processing for pinned images with text
- [ ] Website scraping for linked vendor info
- [ ] Structured Pinterest data in `src/pinterest_data/`
- [ ] Integration with existing classification system

---

## Phase 3: Comprehensive Mind Map Generation 🧠

### 3.1 Data Consolidation Engine

**Timeline:** After Phase 2 completion  
**Goal:** Merge OCR documents, Pinterest data, and additional research into unified mind map structure

#### 3.1.1 Multi-Source Data Integration
```python
data_sources = {
    "ocr_documents": "src/ocr_md_structured/",
    "pinterest_pins": "src/pinterest_data/", 
    "additional_research": "src/research_data/",
    "vendor_contacts": "src/contacts_consolidated/",
    "budget_tracking": "src/budget_analysis/"
}
```

#### 3.1.2 Intelligent Consolidation Process

**Step 1: Entity Recognition & Deduplication**
- Identify duplicate vendors across sources
- Merge contact information from multiple mentions
- Reconcile pricing data from different documents
- Standardize business names and contact formats

**Step 2: Relationship Mapping**
- Link venues to their vendor recommendations
- Connect services to pricing and availability
- Map timeline tasks to responsible vendors
- Associate style preferences with vendor capabilities

**Step 3: Priority & Decision Scoring**
- Weight information by source reliability
- Score vendors by multiple mentions/positive indicators
- Prioritize venues by saved pins + document mentions
- Identify decision-ready vs needs-more-research items

#### 3.1.3 Mind Map Structure Generation
```markdown
# Wedding Planning Mind Map Structure

## Core Branches

### 1. VENUES & LOCATIONS
├── Reception Venues
│   ├── [Venue Name]
│   │   ├── Contact Info
│   │   ├── Pricing Packages  
│   │   ├── Capacity & Layout
│   │   ├── Available Dates
│   │   ├── Included Services
│   │   ├── Vendor Restrictions
│   │   └── Notes & Preferences
│   └── [Additional Venues...]
├── Ceremony Locations
└── Photo Locations

### 2. VENDORS & SERVICES
├── Photography
├── Catering  
├── Music & Entertainment
├── Flowers & Decorations
├── Transportation
├── Hair & Makeup
└── Officiants

### 3. BUDGET & TIMELINE
├── Budget Breakdown
│   ├── Venue Costs
│   ├── Vendor Costs
│   ├── Additional Expenses
│   └── Payment Schedules
├── Planning Timeline
│   ├── 12+ Months Before
│   ├── 6-12 Months Before
│   ├── 3-6 Months Before
│   ├── 1-3 Months Before
│   └── Final Month
└── Decision Deadlines

### 4. STYLE & PREFERENCES
├── Theme & Colors
├── Menu Preferences
├── Music & Entertainment Style
├── Photography Style
└── Decoration Preferences
```

#### 3.1.4 Output Formats

**Primary:** RTF for MindMeister Import
```
- Professional formatting for mind mapping software
- Hierarchical structure with proper indentation
- Rich text formatting for different content types
- Embedded links and contact information
```

**Secondary:** Interactive HTML Dashboard
```
- Searchable vendor database
- Interactive timeline with deadlines
- Budget tracking with real-time calculations
- Contact management with communication history
```

**Tertiary:** Structured Data Export
```
- JSON for programmatic access
- CSV for spreadsheet analysis
- YAML for configuration and future processing
```

#### Advanced Features:
- **Conflict Detection:** Identify overlapping vendor services or date conflicts
- **Gap Analysis:** Highlight missing vendor types or timeline gaps
- **Budget Optimization:** Suggest cost-saving alternatives based on data
- **Decision Support:** Rank options by multiple criteria scoring

#### Deliverables:
- [ ] Multi-source data consolidation engine
- [ ] Entity deduplication and relationship mapping
- [ ] Intelligent mind map structure generation
- [ ] RTF export optimized for MindMeister
- [ ] HTML dashboard for interactive planning
- [ ] Automated conflict and gap detection
- [ ] Budget analysis and optimization suggestions

---

## Implementation Timeline

### Phase 1: Enhanced OCR (Weeks 1-2)
- **Week 1:** Implement two-stage OCR system
- **Week 2:** Test, refine, and process all existing images

### Phase 2: Pinterest Integration (Weeks 3-5)  
- **Week 3:** Pinterest API setup and initial scraping
- **Week 4:** Content extraction and classification
- **Week 5:** Integration with existing OCR data

### Phase 3: Mind Map Consolidation (Weeks 6-8)
- **Week 6:** Data consolidation engine development
- **Week 7:** Mind map structure generation and RTF export
- **Week 8:** Testing, refinement, and dashboard creation

---

## Success Metrics

### Phase 1 Success Criteria:
- [ ] 95%+ OCR success rate maintained
- [ ] Significantly improved formatting in structured output
- [ ] Clear content organization with proper headers/sections
- [ ] Professional markdown output ready for further processing

### Phase 2 Success Criteria:  
- [ ] Complete Pinterest board extraction
- [ ] Successful OCR of pinned images containing text
- [ ] Structured vendor/venue data from Pinterest research
- [ ] Integration with document-based data sources

### Phase 3 Success Criteria:
- [ ] Unified mind map incorporating all data sources
- [ ] Clean RTF export importable to MindMeister
- [ ] No data loss from consolidation process
- [ ] Interactive dashboard for ongoing planning
- [ ] Automated conflict detection and gap analysis

---

## Technology Stack

### Core Technologies:
- **Python 3.11+** - Primary development language
- **OpenAI GPT-4o** - OCR and content structuring
- **Pinterest Business API** - Data collection
- **Selenium/Playwright** - Browser automation
- **Pandoc** - Document format conversion

### Data Processing:
- **PIL/Pillow** - Image preprocessing
- **Beautiful Soup** - HTML parsing
- **PyYAML** - Configuration and data storage
- **Pandas** - Data analysis and manipulation

### Output Generation:
- **Jinja2** - Template-based RTF generation
- **Flask/FastAPI** - Interactive dashboard
- **Chart.js** - Budget visualization
- **FullCalendar** - Timeline management

This comprehensive plan ensures we extract maximum value from both your existing documents and Pinterest research, creating a truly comprehensive wedding planning resource.