"""
StoneFactory ERP Meeting Analysis Prompt (under 8000 char limit)
"""

from config import Config


def get_analysis_prompt(chunk_index, zoom_context=""):
    start_min = chunk_index * Config.CHUNK_DURATION_MINS
    end_min = (chunk_index + 1) * Config.CHUNK_DURATION_MINS
    speakers_list = ", ".join(Config.KNOWN_SPEAKERS)
    modules_list = ", ".join(Config.ERP_MODULES)

    prompt = f"""ROLE: Expert ERP Business Analyst and Visual Document Analyzer for StoneFactory ERP (Global Impex Pvt. Ltd., natural stone import/export, Bhopal/Mundra, India).

OBJECTIVE: Extract EVERY requirement from this video segment ({start_min}m-{end_min}m) from BOTH audio (speech) AND visual (screens shown). Output becomes the official requirements spec for development.

SPEAKERS: {speakers_list} (Alok=Client owner, Uday=Client IT, Yatin/Tanmay/Shrikanth=Confer dev team)
MODULES: {modules_list}

AUDIO EXTRACTION - capture ALL of these:
- Feature requirements ("we need...", "system must...", "in SAP we have...")
- Business rules (approval thresholds, calculation formulas, validation rules, workflow sequences)
- Data entities & fields (master data mentions, specific fields, relationships, data volumes)
- Process flows (Lead->Quote->PI->PO->Production->Shipment->Invoice, approval chains, exceptions)
- Integration needs (GST/SGST/CGST/IGST, Tally, mobile, export docs like CI/PL/BL)
- UOM discussions (SQM/SQFT/MT/KG conversions, density factors, mixed UOM scenarios)
- Reports/dashboards (metrics, KPIs, who needs what report)
- Pain points & priorities (SAP problems, urgency, frustrations)

VISUAL EXTRACTION - capture ALL of these:
- SAP screens: identify form name, list EVERY visible field with label and value, note dropdowns, mandatory fields
- Excel/spreadsheets: read ALL column headers exactly as written, note data types, count rows, read cell values
- Flow charts: document EVERY step/box, decision points, arrows, swim lanes, text labels
- UI mockups: describe layout, list all form fields, buttons, tabs, menus, color coding
- Documents/PDFs: read all headers, field labels, describe layout (header/line items/totals)
- Whiteboards/notes: transcribe all handwritten content

OUTPUT FORMAT - for EACH topic/screen/requirement:

---
### [MM:SS] Topic Title
**Module:** (one of: {modules_list})
**Type:** (feature_request/entity_mention/workflow/field_requirement/business_rule/integration/report_requirement/approval_rule/uom_requirement/screen_capture/data_table/process_flow/pain_point/mobile_requirement/document_format)
**Priority:** (urgent/high/normal/low/not_specified)
**Source:** (audio/visual/both)

**Description:**
Detailed description. Include exact field names, values, formulas, rules.

**Speaker:** Name ("verbatim quote")

**Visual Content:**
Exactly what was on screen. If nothing shown, write "N/A"

**Fields/Data Identified:**
- Field: Type (mandatory/optional)
(List ALL. If none, "N/A")

**Business Rules:**
- Rule
(If none, "N/A")

**Relationships:**
- Entity -> Entity (type)
(If none, "N/A")

**Current SAP Reference:**
How it works in current SAP. If none, "N/A"
---

RULES:
1. EXHAUSTIVE: Do not skip anything. Every field mention, every screen change, every minor comment matters.
2. NO HALLUCINATION: Only what you SEE and HEAR. Say "Unclear" if blurry/inaudible.
3. EXACT QUOTES: Capture verbatim when possible.
4. VISUAL PRECISION: A form with 15 fields = list ALL 15 fields. Never say "various fields."
5. EVERY SCREEN CHANGE: New screen = new block, even if same topic continues.
6. COMPLETE TABLES: List EVERY column header exactly (e.g. "CU_TYPE", "CU_COLOR").
7. CAPTURE VALUES: If dropdown shows "Sandstone" or code shows "ARSA", record it.
8. NUMBER WORKFLOWS: Step 1, Step 2, Step 3...
9. Stone industry terms: types (Marble/Granite/Sandstone/Basalt), surfaces (Polished/Honed/Flamed/Natural), dimensions (LxBxT), containers (Crates/Pallets), ports (Mundra/Chennai), export docs (PI/CI/PL/BL/COO).
10. Locations: Bhopal=Office, Mundra=Factory+Godown, Field=Suppliers, Ports=Shipping. Note which applies."""
    return prompt


def get_lightweight_prompt(chunk_index, zoom_context=""):
    start_min = chunk_index * Config.CHUNK_DURATION_MINS
    end_min = (chunk_index + 1) * Config.CHUNK_DURATION_MINS
    speakers_list = ", ".join(Config.KNOWN_SPEAKERS)

    prompt = f"""Analyze this meeting recording ({start_min}m-{end_min}m) for StoneFactory ERP (Global Impex, stone import/export, India).
Speakers: {speakers_list}

Extract ALL requirements from AUDIO and VISUAL:

For each topic/screen:
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

RULES: Capture EVERYTHING. List ALL visible fields/columns. Do NOT hallucinate. Exact quotes when possible."""
    return prompt
