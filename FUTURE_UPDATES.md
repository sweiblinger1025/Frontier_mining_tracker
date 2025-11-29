# Future Updates - Frontier Mining Tracker

A list of planned features and enhancements for future development.

---

## 🔄 Inventory Tab - Sync from Ledger

**Priority:** Medium  
**Status:** Planned

### Description
Add a "Sync from Ledger" button to the Inventory tab that automatically finds Ore/Oil sales in the Ledger and offers to decrement inventory quantities.

### Proposed Workflow
1. Click "🔄 Sync from Ledger" button
2. System scans Ledger for Ore/Oil sale transactions since last sync
3. Confirmation dialog shows proposed changes:
   ```
   Found 3 sales since last sync:
   
   ☑ Gold Ore: -500 (sold on 11/28)
   ☑ Oil: -2000 (sold on 11/28)  
   ☑ Silver Ore: -150 (sold on 11/27)
   
   [Cancel]  [Apply Selected]
   ```
4. User reviews and selects which to apply
5. Inventory quantities decremented accordingly
6. Oil lifetime sold counter updated automatically

### Technical Notes
- Need to track "last sync timestamp" or synced transaction IDs
- Filter Ledger for: Type=Sale, Category in (Resources - Ore, Resources - Fluids)
- Handle case where inventory doesn't have enough stock (warning)
- Update Oil lifetime counter when Oil sales are synced

---

## 📊 ROI Tracker - Auto-Link from Ledger

**Priority:** Medium  
**Status:** Planned

### Description
Option to automatically create ROI tracking items from Ledger purchases and link revenue from sales.

### Proposed Workflow

**When Adding a Purchase in Ledger:**
1. User adds a purchase transaction (e.g., "Bought Drill Mk3 - $8,000")
2. Checkbox option: "☑ Track ROI for this item"
3. If checked, automatically creates entry in ROI Tracker with:
   - Item Name from transaction description
   - Initial Cost from transaction amount
   - Purchase Date from transaction date
   - Category from item lookup

**When Adding a Sale/Revenue in Ledger:**
1. User adds a sale transaction
2. Dropdown option: "Link to ROI Item: [None / Drill Mk3 / Oil Pump / ...]"
3. If linked, automatically adds revenue to the selected ROI item

### Benefits
- Reduces double-entry (no need to manually add to both Ledger and ROI Tracker)
- Keeps ROI data in sync with actual transactions
- Still allows manual ROI entries for items not in Ledger

### Technical Notes
- Add "track_roi" boolean field to Ledger transactions
- Add "roi_item_id" foreign key field for revenue linking
- ROI Tracker needs method: `add_revenue_from_ledger(item_id, amount, date)`
- Consider: What if user deletes Ledger transaction? Cascade to ROI?

---

## 📋 Other Planned Features

### Settings Tab - Rules Config
- Import rules from Challenge Tracker Excel
- Configure company/personal split percentages
- Set skill levels (Vendor Negotiation, Investment Forecasting)
- Challenge mode restrictions

### Dashboard Tab
- Summary widgets from all tabs
- Quick stats overview
- Charts/graphs for trends
- Challenge mode compliance section (when enabled)

### Database Persistence
- Save all data to SQLite database
- Load on startup
- Export/Import functionality

---

## 💡 Ideas to Consider

- Save file parser improvements (more data extraction)
- Multi-playthrough support (separate save slots)
- Dark mode theme option
- Keyboard shortcuts
- Undo/Redo for transactions
- Backup/Restore functionality
- Print reports to PDF

---

*Last Updated: November 2025*
