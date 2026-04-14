"""
StoneFactory ERP Meeting Analysis Prompt
=========================================
This prompt instructs Twelve Labs to analyze meeting recordings where:
- Client stakeholders discuss ERP requirements for a stone import/export business
- Screens may show SAP forms, Excel spreadsheets, flow charts, mockup screenshots,
  or our custom Next.js ERP application
- Audio contains feature discussions, business rules, approval workflows, and process descriptions

The prompt captures BOTH audio AND visual content to produce a structured requirements document.
"""

from config import Config


def get_analysis_prompt(chunk_index, zoom_context=""):
    """
    Generate the analysis prompt for a given video chunk.

    Args:
        chunk_index: Which chunk this is (for time offset context)
        zoom_context: Transcript text for speaker identification
    """

    start_min = chunk_index * Config.CHUNK_DURATION_MINS
    end_min = (chunk_index + 1) * Config.CHUNK_DURATION_MINS
    speakers_list = ", ".join(Config.KNOWN_SPEAKERS)
    modules_list = ", ".join(Config.ERP_MODULES)

    prompt = f"""
ROLE: You are an Expert ERP Business Analyst, Requirements Engineer, and Visual Document Analyzer working on the "{Config.PROJECT_NAME}" project for {Config.CLIENT_NAME}, a {Config.CLIENT_INDUSTRY} company based in Bhopal, India with facilities in Mundra.

OBJECTIVE: Extract EVERY piece of information from this video segment — both from what people SAY (audio) and what is SHOWN ON SCREEN (visual). This is a client meeting where ERP requirements are being discussed, demonstrated, and reviewed. Your output becomes the official requirements specification that development agents will use to build the system.

VIDEO SEGMENT: {start_min}m - {end_min}m of the full meeting recording.

KNOWN PARTICIPANTS: {speakers_list}
- Alok = Client (Global Impex) - Business owner, domain expert, decision maker
- Uday = Client IT contact
- Yatin = Confer Solutions - Project Lead
- Tanmay = Confer Solutions - Technical Lead
- Shrikanth = Confer Solutions - Data/AI Engineer

ERP MODULES FOR CLASSIFICATION: {modules_list}

TRANSCRIPT CONTEXT (for speaker identification and speech content):
'''{zoom_context[:5000]}'''

=====================================================================
CRITICAL INSTRUCTIONS - READ CAREFULLY
=====================================================================

You must analyze BOTH channels of this video:

## CHANNEL 1: AUDIO/SPEECH ANALYSIS

For everything that is SAID in this segment, extract:

1. **Feature Requirements**: Any mention of what the system should do.
   - "We need...", "The system must...", "It should support...", "Currently in SAP we have..."
   - Record the EXACT requirement, who said it, and which module it belongs to.

2. **Business Rules & Constraints**:
   - Approval thresholds ("amounts above X need manager approval")
   - Calculation formulas ("density factor times volume gives weight")
   - Validation rules ("GSTIN must be 15 characters")
   - Workflow sequences ("first create PI, then get approval, then create PO")

3. **Data Entities & Fields**:
   - Any mention of master data (Stone Types, Colors, Shapes, Items, Customers, Suppliers, Ports, Warehouses)
   - Specific fields mentioned ("we need a density factor on the color master")
   - Relationships between entities ("each item belongs to a stone type and color")
   - Data volumes ("we have 555 colors", "12 stone types", "49MB item master")

4. **Process Flows & Workflows**:
   - End-to-end business processes (Lead -> Quote -> PI -> PO -> Production -> Shipment -> Invoice)
   - Approval chains (who approves what, at what thresholds)
   - Exception handling ("if the material is rejected at inspection...")
   - Multi-location workflows (Bhopal office -> Mundra factory -> Port)

5. **Integration Requirements**:
   - GST/Tax compliance (SGST, CGST, IGST, HSN codes, state codes)
   - Tally accounting integration
   - Mobile app requirements
   - Export documentation (Commercial Invoice, Packing List, Bill of Lading)
   - Banking/payment integrations

6. **UOM (Unit of Measurement) Discussions**:
   - Conversion formulas (SQM to SQFT, MT to KG, etc.)
   - Density factors per stone type/color
   - Mixed UOM scenarios (purchase in MT, sell in SQM)
   - Crate/packing quantity calculations

7. **Reporting & Dashboard Requirements**:
   - Any mention of reports, dashboards, analytics, KPIs
   - Specific metrics discussed (profitability, aging, inventory levels)
   - Who needs what report (management vs. warehouse vs. sales team)

8. **Pain Points & Priorities**:
   - Current problems with SAP or existing system
   - Urgency indicators ("this is critical", "we need this first", "this can wait")
   - Client frustrations or emphatic requests

## CHANNEL 2: VISUAL/SCREEN ANALYSIS

For everything SHOWN ON SCREEN, extract:

1. **SAP Screens & Forms**:
   - If you see any SAP interface, identify the transaction code or form name
   - List EVERY visible field with its label and value (if populated)
   - Note dropdown options visible
   - Note which fields are mandatory vs optional
   - Capture the exact layout/grouping of fields

2. **Excel Spreadsheets & Data Tables**:
   - If you see Excel or a spreadsheet, read ALL visible column headers
   - Note the data types in each column
   - Count approximate number of rows if visible
   - Read any specific cell values that are legible
   - Identify which master data entity this represents

3. **Flow Charts & Diagrams**:
   - If you see a process flow, document EVERY step/box in order
   - Capture decision points (diamonds) and their conditions
   - Note all arrows and their directions
   - Identify swim lanes if present (which department/role handles each step)
   - Read all text labels on the diagram

4. **Mockup Screenshots & UI Designs**:
   - If you see a UI mockup or application screen, describe the layout
   - List all form fields, buttons, tabs, menus visible
   - Note any color coding, status indicators, or visual hierarchy
   - Identify if this is our new ERP (Next.js/React styled) or legacy SAP

5. **Documents & PDFs**:
   - If you see any document (PI format, invoice template, report), describe its structure
   - Read all visible text, headers, and field labels
   - Note the document layout (header, line items, footer/totals)
   - Identify which business process this document supports

6. **Whiteboards, Notes, or Handwritten Content**:
   - Transcribe any handwritten notes or whiteboard drawings
   - Capture diagrams, arrows, and annotations

=====================================================================
OUTPUT FORMAT - STRICTLY FOLLOW THIS STRUCTURE
=====================================================================

For EACH distinct topic, requirement, or screen shown in this segment, output a block in this EXACT format:

---

### [MM:SS] {{Topic Title}}

**Module:** {{One of: {modules_list}}}
**Type:** {{One of: feature_request, entity_mention, workflow, field_requirement, business_rule, integration, report_requirement, approval_rule, uom_requirement, screen_capture, data_table, process_flow, pain_point, mobile_requirement, document_format}}
**Priority:** {{urgent / high / normal / low / not_specified}}
**Source:** {{audio / visual / both}}

**Description:**
{{Detailed description of what was discussed or shown. Be specific and thorough. Include exact field names, values, formulas, and rules.}}

**Speaker:** {{Name}} ("{{Verbatim quote if available, keep exact words}}")

**Visual Content (if screen was shown):**
{{Describe exactly what was on screen - form name, visible fields, data, layout. If nothing relevant was shown, write "N/A"}}

**Fields/Data Identified:**
- {{Field 1}}: {{Type/Description}} {{(mandatory/optional)}}
- {{Field 2}}: {{Type/Description}} {{(mandatory/optional)}}
(List every field mentioned or visible. If none, write "N/A")

**Business Rules:**
- {{Rule 1}}
- {{Rule 2}}
(List any business rules stated or implied. If none, write "N/A")

**Relationships:**
- {{This entity}} -> {{Related entity}} ({{relationship type: one-to-many, many-to-many, etc.}})
(List data relationships. If none, write "N/A")

**Current SAP Reference:**
{{If they mention how it works in current SAP system, note it here. If none, write "N/A"}}

---

=====================================================================
CRITICAL RULES
=====================================================================

1. **EXHAUSTIVE CAPTURE**: Do not skip ANYTHING. Even seemingly minor mentions matter. If someone says "and we also track the vehicle number", that is a field requirement. Capture it.

2. **NO HALLUCINATION**: Only report what you actually SEE and HEAR. If a screen is blurry or audio is unclear, say "Unclear" — do not guess.

3. **EXACT QUOTES**: When a speaker says something important, capture their EXACT words in quotes. Paraphrase only when the exact quote is not audible.

4. **VISUAL PRECISION**: If you see a form with 15 fields, list ALL 15 fields. Do not summarize as "various fields." Read every label.

5. **EVERY TRANSITION**: When the screen changes to a new view, document it as a separate block even if the discussion continues on the same topic.

6. **COMPLETE DATA TABLES**: If you see an Excel or grid with column headers, list EVERY column header exactly as written, even if abbreviated (e.g., "CU_TYPE", "CU_COLOR", "ARTFAC").

7. **FIELD VALUES**: If you see data populated in fields (e.g., a dropdown showing "Sandstone", or a code showing "ARSA"), capture those values.

8. **WORKFLOW SEQUENCES**: If a process is described in order, number the steps explicitly (Step 1, Step 2, Step 3...).

9. **CONTRADICTIONS**: If something discussed contradicts something shown on screen, note both versions.

10. **CONTEXT PERSISTENCE**: If a topic from the previous segment continues into this one, still document it fully — do not say "as discussed earlier."

11. **STONE INDUSTRY SPECIFICS**: Pay special attention to:
    - Stone types (Marble, Granite, Sandstone, Basalt, Limestone, Quartzite, Slate, etc.)
    - Surface finishes (Polished, Honed, Brushed, Flamed, Natural, Bush Hammered, etc.)
    - Dimensions and measurements (Length x Breadth x Thickness in various UOMs)
    - Container stuffing / packing (Crates, Pallets, Boxes, Loose material)
    - Port operations (Mundra, Chennai, JNPT, Krishnampatnam)
    - Export documentation (PI, CI, Packing List, BL, Certificate of Origin, Fumigation Certificate)

12. **MULTI-LOCATION AWARENESS**: The business operates across:
    - Bhopal (Head Office - Sales, Purchase, Finance, Management)
    - Mundra (Factory + Godown - Production, Inventory, Loading)
    - Field (Supplier sites - Inspection, Quality Control)
    - Ports (Shipping - Container stuffing, Customs)
    Note which location each requirement applies to.

"""
    return prompt


def get_lightweight_prompt(chunk_index, zoom_context=""):
    """
    A shorter prompt for faster processing (if rate limits are tight).
    Still captures key information but with less structural overhead.
    """
    start_min = chunk_index * Config.CHUNK_DURATION_MINS
    end_min = (chunk_index + 1) * Config.CHUNK_DURATION_MINS
    speakers_list = ", ".join(Config.KNOWN_SPEAKERS)

    prompt = f"""
You are analyzing a meeting recording ({start_min}m-{end_min}m) for the StoneFactory ERP project.
Client: Global Impex (stone import/export, India).
Speakers: {speakers_list}

Transcript context: '''{zoom_context[:3000]}'''

Extract ALL requirements from AUDIO and VISUAL content:

For each topic/screen, output:
### [MM:SS] Topic
- **Module:** (Masters/Sales/Purchase/Inventory/Production/Finance/Logistics/Dashboard/Mobile/Approvals/CRM/UOM/Reports/Settings)
- **Type:** (feature/entity/workflow/field/rule/integration/report/approval/screen/data/flow/pain_point)
- **Priority:** (urgent/high/normal/low)
- **Source:** (audio/visual/both)
- **Description:** (detailed)
- **Speaker:** Name ("quote")
- **Fields:** (list every field mentioned or visible)
- **Visual:** (describe screen content if shown)
- **SAP Reference:** (if current SAP behavior mentioned)

RULES: Capture EVERYTHING. List ALL visible fields/columns. Do NOT hallucinate. Exact quotes when possible.
"""
    return prompt
