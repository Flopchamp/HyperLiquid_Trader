# ui/main_window.py
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QFrame, QScrollArea, QSpacerItem, QSizePolicy, QHBoxLayout, QPushButton, QComboBox, QStatusBar, QDialog, QFormLayout, QLineEdit
)
from PyQt6.QtCore import Qt
from ui.account_panel import AccountPanel
import json
from core.trader import TraderAccount
import sys
from utils.config_loader import load_api_keys

from ui.controls_panel import ControlsPanel
from ui.chart_view import ChartView
from core.copy_trading import CopyTradingManager



# Add one or more account panels (support multiple later)
# Account panels will be added in the initUI method



class PairMappingDialog(QDialog):
    def __init__(self, account_panels, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Pair Mapping for Subscribers")
        self.account_panels = account_panels
        self.inputs = {}
        layout = QFormLayout(self)
        for panel in account_panels:
            label = f"Account {panel.trader_account.account_id} Symbol"
            inp = QLineEdit()
            inp.setText("BTCUSDT")
            layout.addRow(label, inp)
            self.inputs[panel.trader_account.account_id] = inp
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.accept)
        layout.addRow(self.save_btn)

    def get_pair_map(self):
        return {aid: inp.text().strip() for aid, inp in self.inputs.items() if inp.text().strip()}



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hyperliquid Multi-Account Trader")
        self.setGeometry(100, 100, 1200, 800)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
        self.initUI()

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Header
        header = QLabel("🔹 Hyperliquid Multi-Account Trading Dashboard")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        layout.addWidget(header)

        # Scrollable Account Panels
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        account_container = QWidget()
        account_layout = QVBoxLayout(account_container)

        # Load account configs securely
        accounts_config = load_api_keys()
        if not accounts_config:
            print("No API keys found. Please set them in .env or config/settings.json.")
            sys.exit(1)
        self.account_panels = []
        for i, acc_cfg in enumerate(accounts_config):
            trader = TraderAccount(**acc_cfg)
            panel = AccountPanel(account_id=acc_cfg["account_id"], trader_account=trader)
            self.account_panels.append(panel)
            account_layout.addWidget(panel)
        account_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        scroll_area.setWidget(account_container)
        layout.addWidget(scroll_area)

        # TradingView Chart
        chart_view = ChartView()
        layout.addWidget(chart_view)
        # Connect chart click events to a handler
        chart_view.bridge.on_chart_event = self.handle_chart_event
        self.chart_view = chart_view

        # Controls panel
        self.controls_panel = ControlsPanel()
        layout.addWidget(self.controls_panel)

        # Add Close All and Cancel All buttons
        button_layout = QHBoxLayout()
        self.close_all_btn = QPushButton("Close All")
        self.cancel_all_btn = QPushButton("Cancel All")
        button_layout.addWidget(self.close_all_btn)
        button_layout.addWidget(self.cancel_all_btn)
        layout.addLayout(button_layout)
        # Connect button signals to stub methods
        self.close_all_btn.clicked.connect(self.close_all_positions)
        self.cancel_all_btn.clicked.connect(self.cancel_all_orders)

        # Master account selection
        self.master_selector = QComboBox()
        for panel in self.account_panels:
            self.master_selector.addItem(f"Account {panel.trader_account.account_id}")
        layout.addWidget(QLabel("Master Account:"))
        layout.addWidget(self.master_selector)
        self.master_selector.currentIndexChanged.connect(self.update_copy_trading_manager)
        self.copy_trading_manager = None

        # Pair mapping button
        self.pair_map_btn = QPushButton("Configure Pair Mapping")
        self.pair_map_btn.clicked.connect(self.open_pair_mapping_dialog)
        layout.addWidget(self.pair_map_btn)
        self.pair_map = {}

        self.update_copy_trading_manager()

        # Add status bar for notifications
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.controls_panel.set_status_bar(self.status_bar)

    def open_pair_mapping_dialog(self):
        dlg = PairMappingDialog(self.account_panels, self)
        if dlg.exec():
            self.pair_map = dlg.get_pair_map()
            self.update_copy_trading_manager()

    def update_copy_trading_manager(self):
        master_idx = self.master_selector.currentIndex()
        master = self.account_panels[master_idx].trader_account
        subscribers = [p.trader_account for i, p in enumerate(self.account_panels) if i != master_idx]
        self.copy_trading_manager = CopyTradingManager(master, subscribers, pair_map=self.pair_map)

    def handle_chart_event(self, marker_type, price):
        # Update controls based on marker_type
        if marker_type == 'entry':
            self.controls_panel.set_entry_price(price)
        elif marker_type == 'sl':
            self.controls_panel.set_sl_price(price)
        elif marker_type.startswith('tp'):
            try:
                tp_index = int(marker_type[2:]) - 1
                self.controls_panel.set_tp_price(tp_index, price)
            except Exception:
                pass
        # Log to all account panels
        for panel in self.account_panels:
            panel.log_status(f"Chart click: {marker_type} at price {price:.2f}")
        # TODO: Update controls or backend with entry/SL/TP as needed
        # Optionally, update backend for copy trading
        pass

    def close_all_positions(self):
        print("Close All clicked")
        # TODO: Implement logic to close all positions for all accounts

    def cancel_all_orders(self):
        print("Cancel All clicked")
        # TODO: Implement logic to cancel all orders for all accounts

