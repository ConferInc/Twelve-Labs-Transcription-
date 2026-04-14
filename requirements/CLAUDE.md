# CLAUDE.md - StoneFactory Validation Pipeline

> **Project:** StoneFactory Video Transcription Validation Pipeline
> **Priority:** MAKE-OR-BREAK - Client feasibility proof due this week
> **Last Updated:** 2026-04-14
> **Working Directory:** `C:\Confer\GIT PROJECTS\StoneFactory`

---

## 1. PROJECT GIST

We are building a **code-correction sprint** based on client meeting transcriptions. The workflow is:

1. **Twelve Labs pipeline** processes meeting video recordings and produces structured transcriptions (audio + visual analysis). This step is handled externally and is already adapted for StoneFactory.
2. **We receive the transcriptions** and compare them against the StoneFactory ERP codebase.
3. **We identify gaps** -- features, entities, workflows, fields, business rules that the client discussed but are missing or incorrect in our code.
4. **We produce a single comprehensive sprint** of concrete code-change tasks that OpenClaw autonomous agents can pick up and execute to bring the codebase into alignment with what the client wants.

**This is NOT a validation tool.** We are not building software. We are producing a sprint plan with exact file paths, code changes, and implementation tasks. The sprint goes into `requirements/` and agents execute it against the stonefactory repo.

**Why this matters:** The client (Global Impex / Stone Factory) is evaluating whether to proceed with Confer. We must prove that after one meeting, we can automatically identify every gap and dispatch agents to fix the codebase. This is the "make or break" deliverable.

---

## 2. KEY STAKEHOLDERS

| Name | Role | Context |
|------|------|---------|
| **Alok** | Primary Client Contact (Global Impex) | Business decisions, approvals, +91 9825079206 |
| **Uday Sawant** | IT Contact (Global Impex) | it@stonefactory.in, infrastructure liaison |
| **Yatin** | Confer Team - Project Lead | Drives architecture decisions, client-facing |
| **Tanmay** | Confer Team - Technical Lead | Implementation, sprint coordination |
| **Shrikanth** | Confer Team - Data/AI Engineer | You (the operator running these agents) |

---

## 3. TWO-REPO ARCHITECTURE

### Repo 1: Twelve Labs Transcription Pipeline (EXTERNAL - already built)
- **GitHub:** `https://github.com/ConferInc/Twelve-Labs-Transcription-.git`
- **Purpose:** Takes raw video files (MP4) and produces detailed transcriptions using Twelve Labs AI
- **Pipeline:** 5 Python scripts run sequentially:
  1. `1_split_video.py` - Splits video into 15-min chunks via FFmpeg
  2. `2_upload_assets.py` - Uploads chunks to Twelve Labs cloud
  3. `3_index_assets.py` - Indexes with Marengo 2.7 + Pegasus 1.2 AI models
  4. `4_analyze_video.py` - Generates structured analysis per chunk (the "Nuclear Prompt")
  5. `5_format_report.py` - Stitches chunks into a final Markdown SOP document
- **Output format:** `data/raw_sop_output.json` (per-chunk analysis) and final `Moxi_Master_SOP.md`
- **Config:** `config.py` with API key, index ID, chunk duration, rate limiting (60s between calls)
- **Critical note:** The analysis prompt is currently mortgage-specific (Encompass/Moxi). For StoneFactory, the prompt in `4_analyze_video.py` MUST be adapted to focus on ERP features, master data, workflows, and business processes instead of mortgage SOP clicks.

### Repo 2: StoneFactory ERP (the codebase being validated against)
- **GitHub:** `https://github.com/ConferInc/stonefactory.git`
- **Local path:** `C:\Confer\GIT PROJECTS\StoneFactory\stonefactory\`
- **Tech stack:** Next.js 14 (App Router) + Fastify + PostgreSQL + Drizzle ORM + Temporal + Redis
- **Monorepo structure (Turborepo + pnpm):**
  - `repo/apps/api/` - Fastify backend (TypeScript)
  - `repo/apps/web/` - Next.js frontend (39 pages built)
  - `repo/packages/database/` - Drizzle ORM schema (55+ tables, 2,767 lines)
  - `repo/packages/shared/` - Shared types, GST engine, utilities
- **Deployed at:** `https://stonefactory.confer.today` (VPS: 176.57.184.163)
- **Current state:** Sprint 2, Phase A 95% complete. MVP with Quote-to-PI flow + Approvals working.
- **Git checkout note:** 16 JPG files with trailing-space paths are excluded (`core.protectNTFS false`). These are UI mockup screenshots only -- no code is missing.

### This Workspace (validation pipeline - what we're building)
- **Local path:** `C:\Confer\GIT PROJECTS\StoneFactory\` (parent directory)
- **Contains:**
  - `stonefactory/` - The cloned ERP repo (read-only reference for validation)
  - `Confer Solutions Meetings Recording/` - Two MP4 recordings to process
  - `Dashboard/`, `Master Data/`, `Report and Print Format List/`, etc. - Client drive documents
  - `requirements/` - Validation pipeline requirements (we create these)
  - `CLAUDE.md` - This file

---

## 4. THE MEETING RECORDINGS (Input Data)

Two Microsoft Teams recordings from client sessions:

| File | Size | Date |
|------|------|------|
| `MicrosoftTeams-video 13-Apr-26.mp4` | 372 MB | April 13, 2026 |
| `MicrosoftTeams-video 14-Apr-26.mp4` | 317 MB | April 14, 2026 |

These contain Yatin, Tanmay, Shrikanth, and client stakeholders (Alok, Uday) discussing:
- ERP feature requirements and priorities
- Master data structure (stone types, colors, shapes, dimensions, UOM)
- Business process flows (Sales, Purchase, Inventory, Production)
- Dashboard and reporting needs
- Mobile application requirements
- Approval workflows
- GST/tax compliance
- Shipping/logistics/crate management

---

## 5. TWELVE LABS OUTPUT FORMAT

When the transcription pipeline processes a video, it produces:

### `data/raw_sop_output.json` (primary structured output)
```json
[
  {
    "filename": "part_000.mp4",
    "raw_text": "### [00:12] Feature Discussion\n- **Screen**: ...\n- **Action**: ...",
    "chunk_index": 0
  }
]
```

### Final Markdown report (stitched output)
```markdown
# STONEFACTORY MEETING ANALYSIS

## SECTION 1: part_000.mp4 (0m - 15m)
### [00:12] Discussion Topic
- **Context**: What was being discussed
- **Feature**: Specific ERP feature mentioned
- **Requirement**: What the client wants
- **Speaker**: Name ("verbatim quote")
```

---

## 6. STONEFACTORY ERP - WHAT EXISTS TO VALIDATE AGAINST

### Database Schema (55+ tables in Drizzle ORM)
**Location:** `stonefactory/repo/packages/database/src/schema/`
- `masters.ts` (895 lines) - 42 master tables: stoneTypes, colors, shapes, lengths, breadths, thicknesses, topSurfaces, bottomSurfaces, edges, ports, warehouses, items, businessPartners, etc.
- `sales.ts` (1,038 lines) - 13 sales tables: leads, opportunities, salesEnquiries, salesQuotes, salesPIs, salesInvoices, packingLists, commercialInvoices
- `enums.ts` (430 lines) - All enum types (statuses, UOM types, currencies, container sizes, etc.)
- `customers.ts`, `containers.ts`, `suppliers.ts`, `quarries.ts`

### API Endpoints
**Location:** `stonefactory/repo/apps/api/src/routes/`
- Auth routes (`/api/auth/*`)
- Master data CRUD (`/api/masters/*`, `/api/sf-core/*`)
- Sales workflow (`/api/sales/*`)
- Dashboard KPIs (`/api/dashboard/*`)
- GST calculations (`/api/gst/*`)

### Frontend Pages (39 pages)
**Location:** `stonefactory/repo/apps/web/src/app/`
- Dashboard, Sales (quotes, PIs, orders, invoices), Purchase, Inventory, Logistics, Production, Masters, Approvals, Settings

### Business Logic
**Location:** `stonefactory/repo/apps/api/src/services/` (20+ service classes)
- GST calculation engine (`packages/shared/src/gst/`)
- UOM conversion logic
- Approval workflow system
- PI-centric document flow (Quote -> PI -> Invoice)

### Requirement Documents (already analyzed)
**Location:** `stonefactory/requirements/`
- `sales-module-requirements.md` (71 KB)
- `purchase-module-requirements.md` (63 KB)
- `inventory-module-requirements.md` (47 KB)
- `production-module-requirements.md` (21 KB)
- `finance-module-requirements.md` (18 KB)
- `dashboard-mobile-requirements.md` (42 KB)
- `uom-datamodel-requirements.md` (33 KB)

---

## 7. CLIENT DRIVE DOCUMENTS (Reference Material)

These are downloaded from the client's shared drive and provide ground-truth business context:

| Path | Content |
|------|---------|
| `Master Data/ItemMasterData/` | 16 Excel files with all master data (stone types, colors, shapes, dimensions, UOM, ports, items) |
| `Master Data/Other SubMaster Data/` | Country (247), State (69), Destination Port (225), Packing UOM (9) |
| `Dashboard/` | Dashboard requirements and templates |
| `UOM Conversion Formula & Data/` | UOM conversion formulas, density factors, calculation sheets |
| `Report and Print Format List/` | 70+ report templates across Sales, Purchase, Inventory, Production |
| `RequirementSummary.docx` | Complete business requirements |
| `Flow Chart.docx` | Process flows (CRM, Sales Enquiry, Quote-to-Order) |
| `SAPDBModel.xlsx` | Legacy SAP database model (40+ entity sheets) |
| `Mobile Application.docx` | Mobile app requirements |

---

## 8. VALIDATION PIPELINE ARCHITECTURE (What We're Building)

```
Meeting Recordings (MP4)
        |
        v
[Twelve Labs Pipeline]  <-- External repo, runs separately
        |
        v
Transcription Output (JSON + MD)
        |
        v
[PARSER MODULE]  <-- This repo
  - Extract feature claims
  - Extract entity mentions
  - Extract workflow descriptions
  - Extract requirement statements
        |
        v
[CODE ANALYZER MODULE]  <-- This repo
  - Scan DB schema for entities
  - Scan API routes for endpoints
  - Scan frontend pages for UI features
  - Scan services for business logic
        |
        v
[VALIDATION ENGINE]  <-- This repo
  - Compare claims vs code evidence
  - Score alignment (match/partial/missing)
  - Identify gaps
        |
        v
[REPORT GENERATOR]  <-- This repo
  - Produce validation report
  - Show what's implemented vs discussed
  - Highlight gaps and recommendations
```

---

## 9. SUCCESS METRICS FOR THIS WEEK

1. **Transcription quality:** Can we get meaningful feature-level transcriptions from the meeting videos?
2. **Parse accuracy:** Can we extract discrete, verifiable claims from the transcriptions?
3. **Code coverage:** Can our code analyzer find the right files/tables/routes for each claim?
4. **Validation accuracy:** Does the match/miss classification actually reflect reality?
5. **Report clarity:** Is the output report clear enough for non-technical stakeholders?

**Minimum viable proof:** Process at least ONE meeting video through the full pipeline and produce a validation report that correctly identifies 3+ features as "implemented" and 3+ features as "not yet implemented."

---

## 10. TECH CONSTRAINTS & DECISIONS

- **Twelve Labs API costs money per video minute** - be strategic about which videos to process
- **Rate limiting:** 60-second sleep between Twelve Labs API calls is mandatory to avoid 429 errors
- **The Twelve Labs analysis prompt must be customized** - current prompt is mortgage-specific, needs ERP/stone industry adaptation
- **Python for transcription pipeline** (existing), **TypeScript for validation pipeline** (matches ERP stack)
- **No new infrastructure needed** - validation runs locally or as a script, not a deployed service
- **Git LFS is NOT set up** - video files are stored locally, not in git

---

## 11. AGENT INSTRUCTIONS

If you are an AI agent working on this project:

1. **Read this file first** - it is the single source of truth for project context
2. **Check `requirements/project_requirements.md`** for detailed validation pipeline requirements
3. **Check `requirements/sprint_tasks/`** for your specific task assignment
4. **The StoneFactory ERP code is at `stonefactory/`** - read it but don't modify it
5. **The Twelve Labs pipeline is external** - you may need to reference its output format
6. **Focus on the validation logic** - that's what we're building here
7. **Test against real data** when transcription output becomes available

---

## 12. DIRECTORY STRUCTURE (This Workspace)

```
C:\Confer\GIT PROJECTS\StoneFactory\
|
|-- CLAUDE.md                              # THIS FILE - master context
|-- requirements/
|   |-- project_requirements.md            # Detailed validation pipeline requirements
|   |-- sprint_tasks/                      # Individual agent task files
|       |-- task_01_*.md
|       |-- task_02_*.md
|       |-- ...
|
|-- stonefactory/                          # [GIT REPO] StoneFactory ERP codebase
|   |-- repo/                             # Monorepo with apps/ and packages/
|   |-- requirements/                     # ERP business requirements
|   |-- analysis/                         # Deep-dive analysis documents
|   |-- sprints/                          # Sprint planning
|   |-- notes/                            # Architecture notes
|   |-- ...
|
|-- Confer Solutions Meetings Recording/   # MP4 files to be transcribed
|-- Dashboard/                            # Client dashboard docs
|-- Master Data/                          # Client master data (Excel files)
|-- Report and Print Format List/         # Report templates
|-- UOM Conversion Formula & Data/        # UOM conversion reference
|-- RequirementNotes/                     # Additional requirement notes
|-- RequirementSummary.docx              # Full requirements document
|-- Flow Chart.docx                       # Business process flows
|-- SAPDBModel.xlsx                       # Legacy SAP data model
|-- Mobile Application.docx              # Mobile app specs
|-- QuestionsByAIAgent.xlsx              # AI-generated clarification questions
```
