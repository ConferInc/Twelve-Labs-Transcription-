# StoneFactory ERP - Codebase Index (for gap analysis)

> This file is the ground truth of what EXISTS in code as of 2026-04-14.
> Used to compare against client meeting transcriptions.

---

## DATABASE: 55+ Tables

### Enums (40 enums)
businessPartnerTypeEnum, businessPartnerEntityTypeEnum, addressTypeEnum, contactTypeEnum, bankAccountTypeEnum, itemTypeEnum, dimensionUomEnum, quantityUomTypeEnum, uomCategoryEnum, warehouseTypeEnum, locationZoneEnum, packagingTypeEnum, containerSizeEnum, containerLoadTypeEnum, currencyCodeEnum, incotermEnum, materialCostBasisEnum, commissionTypeEnum, documentStatusEnum, salesDocStatusEnum, purchaseDocStatusEnum, invoiceStatusEnum, grnStatusEnum, packingListStatusEnum, commercialInvoiceStatusEnum, leadStatusEnum, leadLevelEnum, leadSourceTypeEnum, opportunityStageEnum, communicationTypeEnum, communicationDirectionEnum, approvalStatusEnum, approvalActionEnum, paymentModeEnum, paymentStatusEnum, tdsTypeEnum, agentAutonomyLevelEnum, agentStatusEnum, taskStatusEnum, taskPriorityEnum

### Master Tables (sf_core schema)
- branches, departments, employees, users
- businessPartners, bpAddresses, bpContacts, bpBanks, bpGroups, leadSources
- items, itemPackagings, stoneTypes, colors, shapes, lengths, breadths, thicknesses
- topSurfaces, bottomSurfaces, edges, typeThicknessShapes, typeColors
- warehouses, locations, ports, destinationPorts, portRegions
- dimensionUoms, itemUoms, quantityUomTypes
- suppliers, quarries, packagings, paymentTerms
- shippingContainers, currencies, itemGroups

### Sales Tables (sf_sales schema)
- leads, opportunities, communications
- salesEnquiries, salesEnquiryLines
- salesQuotes, salesQuoteLines
- salesPIs, salesPILines
- salesOrders, salesOrderLines, orderStatusHistory
- salesInvoices, salesInvoiceLines, paymentRecords
- packingLists, packingListLines
- commercialInvoices, commercialInvoiceLines

### MISSING from schema (not yet built)
- Purchase Orders (purchaseOrders, purchaseOrderLines)
- GRN / Goods Receipt Notes
- Inventory transactions / stock ledger
- Production / Job Cards / Work Orders / BOM
- Crate tracking / QR codes
- Financial ledger / Tally integration
- TDS calculations
- ECGC insurance tracking
- Vehicle register
- Contractor ledger / billing

---

## API: 150+ Endpoints

### FULLY IMPLEMENTED
- Auth: login, logout, refresh, me, register
- Health: health, live, ready
- GST: 12 endpoints (calculate, validate, invoice-calc, HSN lookup, state info, bulk validate)
- Dashboard: overview, sales, inventory
- Customers: CRUD + dropdown + seed (7 endpoints)
- Containers: CRUD + seed (6 endpoints)
- Business Partners: CRUD + addresses + contacts + GSTIN validation
- Items: CRUD + type filter + search
- Stone Types: CRUD
- Colors, Shapes, Surfaces, Edges: CRUD each
- Locations/Warehouses: CRUD
- Ports, Port Regions, Quarries: CRUD
- Quotes: CRUD + status + convert-to-PI
- PIs: CRUD + status + approve + convert-to-order
- Orders: CRUD + status workflow + history
- Invoices: CRUD + record-payment + payment-history
- Commercial Invoices: CRUD + issue + record-payment
- Packing Lists: CRUD + from-PI + status + utilization
- Agent routes: email/parse, sales/quote, orchestrator (placeholders)

### NOT IMPLEMENTED (no API routes)
- Purchase Orders
- GRN / Goods Receipts
- Inventory stock management
- Stock transfers / adjustments
- Production / Work Orders / Job Cards / BOM
- Shipment tracking (only Zustand store, no real API)
- Financial reports
- Crate management
- TDS calculations
- Tally integration
- ECGC
- Mobile-specific endpoints

---

## FRONTEND: 61 Pages

### REAL (13 pages with API/data)
Dashboard, Login, Sales Quotes (list+detail), Sales Orders, Sales PIs, Commercial Invoices, Items Master, Packing Lists, Shipments, Approvals (list+detail), Settings/Company

### COMING SOON STUBS (32 pages)
Profile, Sales Invoices, Sales Returns, Purchase Orders/Receipts/Returns, Inventory Stock/Stocktake/Transfers/Adjustments, Production Work Orders/Job Cards/BOM, Finance Receivables/Payables/Payments/Reports, Logistics Tracking, Agents

### MASTERS PAGES (16 pages - likely real with EditableDataGrid)
Categories, Colors, Containers, Customers, Dimension UOMs, Edges, Item UOMs, Ports, Quarries, Shapes, Stone Types, Suppliers, Thicknesses, Top Surfaces, Bottom Surfaces, Type-Thickness-Shapes, Warehouses

---

## SERVICES: 14 Service Classes, 200+ Methods

Fully implemented: Customers, Items, Containers, Quotes, PIs, Orders, Invoices, Packing Lists, Commercial Invoices, Business Partners, Locations, Stone Types, User/Auth, GST

NOT implemented: Purchase, Inventory, Production, Shipments (real API), Finance/Accounting, Mobile, Crate Tracking, Reports/Analytics

---

## KEY GAPS TO WATCH FOR IN TRANSCRIPTIONS

1. Purchase module (PO, GRN, supplier follow-up) - NO code
2. Inventory management (stock, transfers, aging) - NO code
3. Production (job cards, BOM, contractor billing) - NO code
4. Crate tracking / QR codes - NO code
5. Tally accounting integration - NO code
6. TDS / tax deduction - NO code
7. ECGC insurance - NO code
8. Mobile app - NO code
9. Report generation (70+ reports mentioned in docs) - NO code
10. Dashboard (real data, not placeholders) - PARTIAL
11. Shipment tracking (real API vs Zustand) - PARTIAL
12. Approval workflow (Zustand only, not persisted) - PARTIAL
13. UOM conversion logic (service exists but limited) - PARTIAL
14. Multi-branch/multi-GST - PARTIAL (schema exists, limited use)
