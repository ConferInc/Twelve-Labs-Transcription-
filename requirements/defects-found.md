# StoneFactory ERP - Defects & Status Found via Live Testing

> **Tested:** 2026-04-14
> **App URL:** http://luhtqpm4bhfdq7gcnp1qb7fw.176.57.184.163.sslip.io
> **API URL:** http://a1213yf7bycunkbmosengvpp.176.57.184.163.sslip.io
> **Method:** Playwright automated tests (headless Chromium)
> **Credentials:** admin@stonefactory.com / admin123

---

## SUMMARY

| Status | Count |
|--------|-------|
| Working (OK) | 45 pages + 24 deep checks |
| Coming Soon / Stub | 18 pages |
| Hard Defects | 13 |
| Total Tested | 54 pages + 48 deep checks |

---

## HARD DEFECTS (must fix)

### D1: Masters - Stone attribute pages return 404
**Severity:** P0 - Critical (core master data inaccessible)
**Pages affected:**
- `/masters/stone-types` - 404
- `/masters/colors` - 404
- `/masters/shapes` - 404
- `/masters/edges` - 404
- `/masters/top-surfaces` - 404
- `/masters/bottom-surfaces` - 404
- `/masters/thicknesses` - 404

**Note:** The API endpoints for these work fine (`/api/sf-core/stone-types` returns 200 with data). The frontend routing is broken -- these pages either don't exist at the expected paths or Next.js routing isn't matching.

**API evidence:** `GET /api/sf-core/stone-types` -> 200, returns 24 stone types (BAS, GRAS, etc.)

### D2: Packing Lists page - Application Error
**Severity:** P1 - High
**Page:** `/logistics/packing-lists`
**Error:** Application error on page load
**Note:** The API endpoint works (`/api/sales/packing-lists` returns 200 with demo data). The frontend page itself crashes.

### D3: API - Quarries endpoint returns 500
**Severity:** P1 - High
**Endpoint:** `GET /api/sf-core/quarries`
**Error:** `{"statusCode":500,"error":"PostgresError","message":"Internal Server Error"}`
**Note:** Database query error. Likely a schema mismatch or missing migration for the quarries table.

### D4: API - Suppliers endpoint returns 500
**Severity:** P1 - High
**Endpoint:** `GET /api/sf-core/suppliers`
**Error:** `{"statusCode":500,"error":"PostgresError","message":"Internal Server Error"}`
**Note:** Same as quarries -- database query error.

### D5: API - Surfaces endpoint returns 404
**Severity:** P2 - Medium
**Endpoint:** `GET /api/sf-core/surfaces`
**Error:** 404 Not Found
**Note:** The route may be registered under a different path (e.g., `/api/sf-core/top-surfaces` instead of `/api/sf-core/surfaces`).

### D6: API - Auth /me endpoint routing issue
**Severity:** P2 - Medium
**Endpoint:** `GET /auth/me` (without /api prefix)
**Error:** 404
**Note:** Route may be at `/api/auth/me` instead. The web app's Next.js proxy may not be forwarding auth routes correctly.

### D7: API /health not accessible through web proxy
**Severity:** P3 - Low
**Detail:** `/api/health` through the web app returns 404 (hits Next.js not Fastify). Direct API at `a1213yf...sslip.io/health` returns 200 healthy.

---

## COMING SOON / STUB PAGES (18 pages - no functionality)

These pages load but have no tables, forms, or real UI -- just placeholder content:

### Sales (2)
- `/sales/invoices` - Stub
- `/sales/returns` - Stub

### Purchase (3) - ENTIRE MODULE IS STUB
- `/purchase/orders` - Stub
- `/purchase/receipts` - Stub
- `/purchase/returns` - Stub

### Inventory (4) - ENTIRE MODULE IS STUB
- `/inventory/stock` - Stub
- `/inventory/adjustments` - Stub
- `/inventory/stocktake` - Stub
- `/inventory/transfers` - Stub

### Production (3) - ENTIRE MODULE IS STUB
- `/production/work-orders` - Stub
- `/production/job-cards` - Stub
- `/production/bom` - Stub

### Finance (4) - ENTIRE MODULE IS STUB
- `/finance/receivables` - Stub
- `/finance/payables` - Stub
- `/finance/payments` - Stub
- `/finance/reports` - Stub

### Other (2)
- `/logistics/tracking` - Stub
- `/profile` - Stub

---

## WORKING PAGES (functional with data)

### Fully Functional (API-backed with real data)
- `/login` - Auth works, redirects to dashboard
- `/` (Dashboard) - Stats cards + activity feed load
- `/sales/quotes` - List page works (currently 0 quotes, but API returns 200)
- `/sales/quotes/new` - Create form loads
- `/sales/orders` - List page works (currently 0 orders)
- `/sales/pi` - List works (4 demo PIs exist including PI/DEMO/REJECTED)
- `/sales/pi/new` - Create form loads
- `/sales/commercial-invoices` - List works (0 invoices)
- `/sales/commercial-invoices/new` - Create form loads
- `/logistics/packing-lists/new` - Create form loads
- `/logistics/shipments` - Page loads (Zustand store, not real API)
- `/approvals` - Page loads
- `/settings/company` - Page loads

### Masters - Working
- `/masters/items` - Full CRUD with API (10 items exist: GRAN-BLU-TILE-20, etc.)
- `/masters/customers` - Works (5 customers: CUST001, etc.)
- `/masters/suppliers` - Page loads
- `/masters/dimension-uoms` - Works
- `/masters/item-uoms` - Works
- `/masters/ports` - Works (CHENNAI, etc.)
- `/masters/warehouses` - Works
- `/masters/containers` - Works (20FT, 40FT, 40HC)
- `/masters/categories` - Works
- `/masters/type-thickness-shapes` - Works
- `/masters/quarries` - Page loads (but API 500 - see D3)

---

## API ENDPOINT STATUS

### Working (200)
- `GET /health` - healthy, v0.1.0
- `GET /api/masters/customers` - 5 customers
- `GET /api/masters/items` - 10 items
- `GET /api/sf-core/stone-types` - 24 types
- `GET /api/sf-core/colors` - Has data (AGW, etc.)
- `GET /api/sf-core/shapes` - Has data (ARTFAC, etc.)
- `GET /api/sf-core/dimension-uoms` - Has data (CM, etc.)
- `GET /api/sf-core/item-uoms` - Has data (CONT, etc.)
- `GET /api/sf-core/ports` - Has data (CHENNAI, etc.)
- `GET /api/sf-core/containers` - 3 containers (20FT, 40FT, 40HC)
- `GET /api/sales/quotes` - 0 quotes
- `GET /api/sales/pis` - 4 PIs (demo data)
- `GET /api/sales/proforma-invoices` - Same as /pis (dual route)
- `GET /api/sales/orders` - 0 orders
- `GET /api/sales/invoices` - 0 invoices
- `GET /api/sales/commercial-invoices` - 0 CIs
- `GET /api/sales/packing-lists` - Has demo data
- `GET /api/dashboard/overview` - 5 customers, 10 items, 4 PIs
- `GET /api/dashboard/sales` - 4 PIs, total $28,000
- `GET /api/dashboard/inventory` - 10 items, 24 stone types
- `GET /api/gst/states` - All Indian states
- `GET /api/gst/default-rate` - 18%

### Broken
- `GET /api/sf-core/quarries` - 500 PostgresError
- `GET /api/sf-core/suppliers` - 500 PostgresError
- `GET /api/sf-core/surfaces` - 404 (wrong path?)
- `GET /auth/me` - 404 (routing issue)

---

## DATA STATUS

| Entity | Count | Source |
|--------|-------|--------|
| Customers | 5 | Database |
| Items | 10 | Database |
| Stone Types | 24 | Database (seeded) |
| Colors | Many | Database (seeded) |
| Shapes | Many | Database (seeded) |
| Dimension UOMs | Several | Database (seeded) |
| Item UOMs | Several | Database (seeded) |
| Ports | Several | Database (seeded) |
| Containers | 3 | Database (20FT, 40FT, 40HC) |
| Proforma Invoices | 4 | Database (demo) |
| Packing Lists | 1+ | Database (demo) |
| Quotes | 0 | Empty |
| Orders | 0 | Empty |
| Invoices | 0 | Empty |
| Commercial Invoices | 0 | Empty |

---

## NOTES FOR SPRINT PLANNING

1. **The 7 stone attribute master pages (D1) are the highest priority fix** -- these are core to the Item Master and the client discussed them extensively in the April 14 meeting.

2. **18 stub pages** need real implementations -- the entire Purchase, Inventory, Production, and Finance modules are empty shells.

3. **API is mostly healthy** -- 22 of 26 endpoints return 200. The 2 PostgresErrors (quarries, suppliers) suggest missing DB migrations.

4. **Data exists for demo** -- customers, items, PIs, packing lists are all seeded. But no real transactional flow (0 quotes, 0 orders, 0 invoices).

5. **The packing lists page crash (D2)** needs a frontend fix before that feature can be demonstrated.
