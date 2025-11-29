"""
Dashboard Tab - Main overview combining data from all tabs.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QProgressBar, QAbstractItemView, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor


class DashboardTab(QWidget):
    """Main Dashboard showing overview of all mining operations."""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the dashboard interface."""
        # Use scroll area for smaller screens
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(15)
        
        # === Status Banner ===
        self._create_status_banner(layout)
        
        # === Financial Summary Cards ===
        self._create_financial_cards(layout)
        
        # === Oil Progress Section ===
        self._create_oil_progress(layout)
        
        # === Quick Actions ===
        self._create_quick_actions(layout)
        
        # === ROI Highlights ===
        self._create_roi_highlights(layout)
        
        # === Recent Activity ===
        self._create_recent_activity(layout)
        
        # Add stretch at bottom
        layout.addStretch()
        
        scroll.setWidget(content)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
    
    def _create_status_banner(self, parent_layout):
        """Create the status banner at the top."""
        self.status_frame = QFrame()
        self.status_frame.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.status_frame.setLineWidth(2)
        self.status_frame.setStyleSheet("background-color: #D5F5D5;")  # Default green
        
        status_layout = QHBoxLayout(self.status_frame)
        status_layout.setContentsMargins(15, 10, 15, 10)
        
        self.status_icon = QLabel("✅")
        self.status_icon.setFont(QFont("", 28))
        status_layout.addWidget(self.status_icon)
        
        self.status_label = QLabel("LOADING...")
        self.status_label.setFont(QFont("", 16, QFont.Weight.Bold))
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        # Day counter
        self.day_label = QLabel("Day: -")
        self.day_label.setFont(QFont("", 12))
        status_layout.addWidget(self.day_label)
        
        # Refresh button
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.refresh_dashboard)
        status_layout.addWidget(self.refresh_btn)
        
        parent_layout.addWidget(self.status_frame)
    
    def _create_financial_cards(self, parent_layout):
        """Create the financial summary cards."""
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(15)
        
        # Net Worth Card
        self.networth_card = self._create_card("💰 NET WORTH", "$0", "Combined total")
        self.networth_value = self.networth_card.findChild(QLabel, "value_label")
        self.networth_subtitle = self.networth_card.findChild(QLabel, "subtitle_label")
        cards_layout.addWidget(self.networth_card, 1)
        
        # Company Balance Card
        self.company_card = self._create_card("💼 COMPANY", "$0", "90% of sales")
        self.company_value = self.company_card.findChild(QLabel, "value_label")
        cards_layout.addWidget(self.company_card, 1)
        
        # Personal Balance Card
        self.personal_card = self._create_card("👤 PERSONAL", "$0", "10% of sales")
        self.personal_value = self.personal_card.findChild(QLabel, "value_label")
        cards_layout.addWidget(self.personal_card, 1)
        
        # Transactions Card
        self.transactions_card = self._create_card("📊 TRANSACTIONS", "0", "Total count")
        self.transactions_value = self.transactions_card.findChild(QLabel, "value_label")
        cards_layout.addWidget(self.transactions_card, 1)
        
        parent_layout.addLayout(cards_layout)
    
    def _create_card(self, title, value, subtitle, color="#E8F4FD"):
        """Create a summary card widget."""
        card = QFrame()
        card.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        card.setStyleSheet(f"background-color: {color}; border-radius: 5px;")
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 12, 15, 12)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("", 10, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setObjectName("value_label")
        value_label.setFont(QFont("", 18, QFont.Weight.Bold))
        value_label.setStyleSheet("color: #1F4E79;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(value_label)
        
        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName("subtitle_label")
        subtitle_label.setStyleSheet("color: #666666;")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle_label)
        
        return card
    
    def _create_oil_progress(self, parent_layout):
        """Create the oil lifetime progress section."""
        oil_group = QGroupBox("⛽ Oil Lifetime Progress")
        oil_layout = QVBoxLayout(oil_group)
        
        # Top row: Labels
        labels_layout = QHBoxLayout()
        
        self.oil_sold_label = QLabel("Sold: 0")
        self.oil_sold_label.setFont(QFont("", 11, QFont.Weight.Bold))
        labels_layout.addWidget(self.oil_sold_label)
        
        labels_layout.addStretch()
        
        self.oil_remaining_label = QLabel("Remaining: 10,000")
        self.oil_remaining_label.setFont(QFont("", 11))
        self.oil_remaining_label.setStyleSheet("color: #666666;")
        labels_layout.addWidget(self.oil_remaining_label)
        
        labels_layout.addStretch()
        
        self.oil_cap_label = QLabel("Cap: 10,000")
        self.oil_cap_label.setFont(QFont("", 11, QFont.Weight.Bold))
        labels_layout.addWidget(self.oil_cap_label)
        
        oil_layout.addLayout(labels_layout)
        
        # Progress bar
        self.oil_progress = QProgressBar()
        self.oil_progress.setMinimum(0)
        self.oil_progress.setMaximum(100)
        self.oil_progress.setValue(0)
        self.oil_progress.setTextVisible(True)
        self.oil_progress.setFormat("%p% of lifetime cap")
        self.oil_progress.setMinimumHeight(30)
        self.oil_progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #1F4E79;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:0.5 #2ecc71, stop:1 #27ae60);
                border-radius: 3px;
            }
        """)
        oil_layout.addWidget(self.oil_progress)
        
        # Status label
        self.oil_status_label = QLabel("✅ Within safe limits")
        self.oil_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.oil_status_label.setStyleSheet("color: #008800;")
        oil_layout.addWidget(self.oil_status_label)
        
        parent_layout.addWidget(oil_group)
    
    def _create_quick_actions(self, parent_layout):
        """Create quick action buttons."""
        actions_group = QGroupBox("⚡ Quick Actions")
        actions_layout = QHBoxLayout(actions_group)
        actions_layout.setSpacing(10)
        
        # Add Transaction button
        self.add_transaction_btn = QPushButton("➕ Add Transaction")
        self.add_transaction_btn.setStyleSheet("background-color: #D5F5D5; padding: 8px 15px;")
        self.add_transaction_btn.clicked.connect(self._go_to_ledger)
        actions_layout.addWidget(self.add_transaction_btn)
        
        # ROI Tracker button
        self.roi_btn = QPushButton("📊 ROI Tracker")
        self.roi_btn.setStyleSheet("background-color: #E8F4FD; padding: 8px 15px;")
        self.roi_btn.clicked.connect(self._go_to_roi_tracker)
        actions_layout.addWidget(self.roi_btn)
        
        # Budget Planner button
        self.budget_btn = QPushButton("📈 Budget Planner")
        self.budget_btn.setStyleSheet("background-color: #FFF2CC; padding: 8px 15px;")
        self.budget_btn.clicked.connect(self._go_to_budget_planner)
        actions_layout.addWidget(self.budget_btn)
        
        # Inventory button
        self.inventory_btn = QPushButton("📦 Inventory")
        self.inventory_btn.setStyleSheet("background-color: #E8E8E8; padding: 8px 15px;")
        self.inventory_btn.clicked.connect(self._go_to_inventory)
        actions_layout.addWidget(self.inventory_btn)
        
        actions_layout.addStretch()
        parent_layout.addWidget(actions_group)
    
    def _create_roi_highlights(self, parent_layout):
        """Create ROI performance highlights section."""
        roi_group = QGroupBox("📊 ROI Performance Highlights")
        roi_layout = QHBoxLayout(roi_group)
        roi_layout.setSpacing(15)
        
        # Top Performer Card
        self.top_performer_card = self._create_card("🏆 TOP PERFORMER", "-", "+0% ROI", "#FFF2CC")
        self.top_performer_value = self.top_performer_card.findChild(QLabel, "value_label")
        self.top_performer_subtitle = self.top_performer_card.findChild(QLabel, "subtitle_label")
        roi_layout.addWidget(self.top_performer_card, 1)
        
        # Total Profit Card
        self.total_profit_card = self._create_card("💰 TOTAL PROFIT", "$0", "From investments", "#D5F5D5")
        self.total_profit_value = self.total_profit_card.findChild(QLabel, "value_label")
        self.total_profit_subtitle = self.total_profit_card.findChild(QLabel, "subtitle_label")
        roi_layout.addWidget(self.total_profit_card, 1)
        
        # Success Rate Card
        self.success_rate_card = self._create_card("✅ SUCCESS RATE", "0%", "0 of 0 profitable", "#E8F4FD")
        self.success_rate_value = self.success_rate_card.findChild(QLabel, "value_label")
        self.success_rate_subtitle = self.success_rate_card.findChild(QLabel, "subtitle_label")
        roi_layout.addWidget(self.success_rate_card, 1)
        
        parent_layout.addWidget(roi_group)
    
    def _create_recent_activity(self, parent_layout):
        """Create recent activity table."""
        activity_group = QGroupBox("📜 Recent Activity")
        activity_layout = QVBoxLayout(activity_group)
        
        # Table
        self.activity_table = QTableWidget()
        self.activity_table.setColumnCount(5)
        self.activity_table.setHorizontalHeaderLabels([
            "Date", "Description", "Amount", "Account", "Balance"
        ])
        self.activity_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.activity_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self.activity_table.setColumnWidth(1, 250)
        self.activity_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.activity_table.setAlternatingRowColors(True)
        self.activity_table.setMaximumHeight(200)
        activity_layout.addWidget(self.activity_table)
        
        # Link to Ledger
        view_all_btn = QPushButton("View All Transactions →")
        view_all_btn.setFlat(True)
        view_all_btn.setStyleSheet("color: #1F4E79; text-align: left;")
        view_all_btn.clicked.connect(self._go_to_ledger)
        activity_layout.addWidget(view_all_btn)
        
        parent_layout.addWidget(activity_group)
    
    def refresh_dashboard(self):
        """Refresh all dashboard data."""
        self._update_financial_summary()
        self._update_oil_progress()
        self._update_roi_highlights()
        self._update_recent_activity()
        self._update_status_banner()
    
    def _update_financial_summary(self):
        """Update financial summary cards from Ledger."""
        try:
            ledger = self.main_window.ledger_tab
            balances = ledger.get_current_balances()
            
            personal = balances.get("personal", 0)
            company = balances.get("company", 0)
            total = personal + company
            
            self.networth_value.setText(f"${total:,.0f}")
            self.company_value.setText(f"${company:,.0f}")
            self.personal_value.setText(f"${personal:,.0f}")
            
            # Get transaction count
            transaction_count = ledger.table.rowCount()
            self.transactions_value.setText(str(transaction_count))
            
            # Color code net worth based on starting capital
            if total >= 100000:
                self.networth_value.setStyleSheet("color: #008800;")
            elif total >= 50000:
                self.networth_value.setStyleSheet("color: #1F4E79;")
            else:
                self.networth_value.setStyleSheet("color: #CC0000;")
                
        except Exception as e:
            print(f"Error updating financial summary: {e}")
    
    def _update_oil_progress(self):
        """Update oil lifetime progress from Inventory tab."""
        try:
            if hasattr(self.main_window, 'inventory_tab'):
                inv = self.main_window.inventory_tab
                
                # Get oil tracking values
                oil_sold = getattr(inv, 'oil_lifetime_sold', 0)
                oil_cap = getattr(inv, 'oil_cap_amount', 10000)
                oil_enabled = getattr(inv, 'oil_cap_enabled', True)
                
                # Update labels
                self.oil_sold_label.setText(f"Sold: {oil_sold:,.0f}")
                self.oil_cap_label.setText(f"Cap: {oil_cap:,.0f}")
                
                remaining = max(0, oil_cap - oil_sold)
                self.oil_remaining_label.setText(f"Remaining: {remaining:,.0f}")
                
                # Update progress bar
                if oil_cap > 0:
                    percentage = min(100, (oil_sold / oil_cap) * 100)
                    self.oil_progress.setValue(int(percentage))
                else:
                    self.oil_progress.setValue(0)
                
                # Update status and colors
                if not oil_enabled:
                    self.oil_status_label.setText("⚪ Oil cap tracking disabled")
                    self.oil_status_label.setStyleSheet("color: #666666;")
                    self.oil_progress.setStyleSheet("""
                        QProgressBar {
                            border: 2px solid #CCCCCC;
                            border-radius: 5px;
                            text-align: center;
                        }
                        QProgressBar::chunk {
                            background-color: #CCCCCC;
                            border-radius: 3px;
                        }
                    """)
                elif oil_sold >= oil_cap:
                    self.oil_status_label.setText("🚨 OIL CAP REACHED - No more sales allowed!")
                    self.oil_status_label.setStyleSheet("color: #CC0000; font-weight: bold;")
                    self.oil_progress.setStyleSheet("""
                        QProgressBar {
                            border: 2px solid #CC0000;
                            border-radius: 5px;
                            text-align: center;
                            font-weight: bold;
                        }
                        QProgressBar::chunk {
                            background-color: #CC0000;
                            border-radius: 3px;
                        }
                    """)
                elif oil_sold >= oil_cap * 0.9:
                    self.oil_status_label.setText("⚠️ WARNING: Approaching oil cap limit!")
                    self.oil_status_label.setStyleSheet("color: #CC8800; font-weight: bold;")
                    self.oil_progress.setStyleSheet("""
                        QProgressBar {
                            border: 2px solid #CC8800;
                            border-radius: 5px;
                            text-align: center;
                            font-weight: bold;
                        }
                        QProgressBar::chunk {
                            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #f39c12, stop:1 #e74c3c);
                            border-radius: 3px;
                        }
                    """)
                elif oil_sold >= oil_cap * 0.75:
                    self.oil_status_label.setText("⚠️ 75% of oil cap used")
                    self.oil_status_label.setStyleSheet("color: #CC8800;")
                    self.oil_progress.setStyleSheet("""
                        QProgressBar {
                            border: 2px solid #1F4E79;
                            border-radius: 5px;
                            text-align: center;
                            font-weight: bold;
                        }
                        QProgressBar::chunk {
                            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #3498db, stop:0.7 #f39c12, stop:1 #e67e22);
                            border-radius: 3px;
                        }
                    """)
                else:
                    self.oil_status_label.setText("✅ Within safe limits")
                    self.oil_status_label.setStyleSheet("color: #008800;")
                    self.oil_progress.setStyleSheet("""
                        QProgressBar {
                            border: 2px solid #1F4E79;
                            border-radius: 5px;
                            text-align: center;
                            font-weight: bold;
                        }
                        QProgressBar::chunk {
                            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #3498db, stop:0.5 #2ecc71, stop:1 #27ae60);
                            border-radius: 3px;
                        }
                    """)
                    
        except Exception as e:
            print(f"Error updating oil progress: {e}")
    
    def _update_roi_highlights(self):
        """Update ROI highlights from ROI Tracker."""
        try:
            if hasattr(self.main_window, 'roi_tracker_tab'):
                roi_data = self.main_window.roi_tracker_tab.get_summary_data()
                
                # Top Performer
                best_name = roi_data.get("best_performer", "-") or "-"
                best_roi = roi_data.get("best_roi", 0)
                self.top_performer_value.setText(best_name)
                self.top_performer_subtitle.setText(f"{best_roi:+.1f}% ROI")
                
                # Total Profit
                net_profit = roi_data.get("net_profit", 0)
                self.total_profit_value.setText(f"${net_profit:+,.0f}")
                if net_profit >= 0:
                    self.total_profit_value.setStyleSheet("color: #008800;")
                else:
                    self.total_profit_value.setStyleSheet("color: #CC0000;")
                
                overall_roi = roi_data.get("overall_roi", 0)
                self.total_profit_subtitle.setText(f"{overall_roi:+.1f}% overall ROI")
                
                # Success Rate
                success_rate = roi_data.get("success_rate", 0)
                profitable = roi_data.get("profitable_count", 0)
                total_count = roi_data.get("total_count", 0)
                
                self.success_rate_value.setText(f"{success_rate:.0f}%")
                self.success_rate_subtitle.setText(f"{profitable} of {total_count} profitable")
                
        except Exception as e:
            print(f"Error updating ROI highlights: {e}")
    
    def _update_recent_activity(self):
        """Update recent activity table from Ledger."""
        try:
            ledger = self.main_window.ledger_tab
            
            # Get last 5 transactions
            row_count = ledger.table.rowCount()
            display_count = min(5, row_count)
            
            self.activity_table.setRowCount(display_count)
            
            running_balance = 0
            balances = ledger.get_current_balances()
            
            for i in range(display_count):
                # Get from bottom of ledger (most recent)
                ledger_row = row_count - 1 - i
                
                # Date
                date_item = ledger.table.item(ledger_row, 0)
                date_text = date_item.text() if date_item else ""
                self.activity_table.setItem(i, 0, QTableWidgetItem(date_text))
                
                # Description
                desc_item = ledger.table.item(ledger_row, 2)
                desc_text = desc_item.text() if desc_item else ""
                self.activity_table.setItem(i, 1, QTableWidgetItem(desc_text))
                
                # Amount (Income or Expense)
                income_item = ledger.table.item(ledger_row, 5)
                expense_item = ledger.table.item(ledger_row, 6)
                
                income_text = income_item.text() if income_item else ""
                expense_text = expense_item.text() if expense_item else ""
                
                if income_text and income_text != "$0":
                    amount_item = QTableWidgetItem(income_text)
                    amount_item.setForeground(QColor("#008800"))
                elif expense_text and expense_text != "$0":
                    amount_item = QTableWidgetItem(expense_text)
                    amount_item.setForeground(QColor("#CC0000"))
                else:
                    amount_item = QTableWidgetItem("$0")
                
                amount_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.activity_table.setItem(i, 2, amount_item)
                
                # Account
                account_item = ledger.table.item(ledger_row, 4)
                account_text = account_item.text() if account_item else ""
                self.activity_table.setItem(i, 3, QTableWidgetItem(account_text))
                
                # Balance
                balance_item = ledger.table.item(ledger_row, 7)
                balance_text = balance_item.text() if balance_item else ""
                balance_cell = QTableWidgetItem(balance_text)
                balance_cell.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.activity_table.setItem(i, 4, balance_cell)
                
        except Exception as e:
            print(f"Error updating recent activity: {e}")
            self.activity_table.setRowCount(0)
    
    def _update_status_banner(self):
        """Update the status banner based on current state."""
        try:
            # Get financial data
            ledger = self.main_window.ledger_tab
            balances = ledger.get_current_balances()
            total = balances.get("personal", 0) + balances.get("company", 0)
            
            # Check budget status
            can_afford = True
            if hasattr(self.main_window, 'budget_planner_tab'):
                bp = self.main_window.budget_planner_tab
                settings = bp.get_settings()
                available = settings.get("personal_balance", 0)
                
                # Calculate total planned
                equipment_total = sum(
                    item.get("price", 0) * item.get("quantity", 1)
                    for item in bp.equipment_items
                    if isinstance(item, dict) and item.get("include", True)
                )
                
                facility_total = 0
                for setup in bp.power_setups:
                    if isinstance(setup, dict) and setup.get("include", True):
                        facility_total += setup.get("total_cost", 0)
                
                planned_total = equipment_total + facility_total
                can_afford = available >= planned_total or planned_total == 0
            
            # Determine status
            if total >= 100000 and can_afford:
                self.status_icon.setText("✅")
                self.status_label.setText("ALL SYSTEMS OPERATIONAL")
                self.status_frame.setStyleSheet("background-color: #D5F5D5;")
            elif total >= 50000 and can_afford:
                self.status_icon.setText("✅")
                self.status_label.setText("OPERATIONS NORMAL")
                self.status_frame.setStyleSheet("background-color: #D5F5D5;")
            elif not can_afford:
                self.status_icon.setText("⚠️")
                self.status_label.setText("OVER BUDGET - Review Budget Planner")
                self.status_frame.setStyleSheet("background-color: #FFF2CC;")
            elif total < 50000:
                self.status_icon.setText("⚠️")
                self.status_label.setText("LOW FUNDS - Consider selling assets")
                self.status_frame.setStyleSheet("background-color: #FFF2CC;")
            
            if total < 10000:
                self.status_icon.setText("🚨")
                self.status_label.setText("CRITICAL - Funds dangerously low!")
                self.status_frame.setStyleSheet("background-color: #F8D6D6;")
            
            # Update day counter (placeholder - could be from settings)
            self.day_label.setText("Day: 1")
            
        except Exception as e:
            print(f"Error updating status banner: {e}")
            self.status_label.setText("Dashboard Ready")
    
    def _go_to_ledger(self):
        """Navigate to Ledger tab."""
        for i in range(self.main_window.tab_widget.count()):
            if self.main_window.tab_widget.tabText(i) == "Ledger":
                self.main_window.tab_widget.setCurrentIndex(i)
                break
    
    def _go_to_roi_tracker(self):
        """Navigate to ROI Tracker tab."""
        for i in range(self.main_window.tab_widget.count()):
            if self.main_window.tab_widget.tabText(i) == "ROI Tracker":
                self.main_window.tab_widget.setCurrentIndex(i)
                break
    
    def _go_to_budget_planner(self):
        """Navigate to Budget Planner tab."""
        for i in range(self.main_window.tab_widget.count()):
            if self.main_window.tab_widget.tabText(i) == "Budget Planner":
                self.main_window.tab_widget.setCurrentIndex(i)
                break
    
    def _go_to_inventory(self):
        """Navigate to Inventory tab."""
        for i in range(self.main_window.tab_widget.count()):
            if self.main_window.tab_widget.tabText(i) == "Inventory":
                self.main_window.tab_widget.setCurrentIndex(i)
                break
    
    def showEvent(self, event):
        """Refresh dashboard when tab is shown."""
        super().showEvent(event)
        self.refresh_dashboard()
