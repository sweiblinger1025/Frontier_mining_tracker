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

### Budget Planner Tab
- Plan future purchases
- Equipment upgrade paths
- ROI projections

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
