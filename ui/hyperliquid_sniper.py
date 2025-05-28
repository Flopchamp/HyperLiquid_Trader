import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QComboBox, QSlider, QLineEdit, QGroupBox, QTextEdit,
    QScrollArea, QGridLayout, QCheckBox, QSizePolicy, QFrame, QSpacerItem,
    QTabWidget
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPalette
from PyQt6.QtWebEngineWidgets import QWebEngineView


class HyperliquidSniper(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("⚡ HyperLiquid Sniper")
        self.setGeometry(50, 50, 1800, 1000)
        self.setStyleSheet(self.get_main_stylesheet())
        self.initUI()

    def get_main_stylesheet(self):
        return """
        QMainWindow {
            background-color: #0a0b0f;
            color: #ffffff;
        }
        QWidget {
            background-color: #0a0b0f;
            color: #ffffff;
            font-family: 'Segoe UI', sans-serif;
            font-size: 12px;
        }
        QGroupBox {
            border: 1px solid #2a2d35;
            border-radius: 6px;
            margin-top: 15px;
            padding-top: 10px;
            background-color: #12141a;
            font-weight: bold;
            color: #ffffff;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
            color: #ffffff;
        }
        QLineEdit {
            background-color: #1a1d25;
            border: 1px solid #2a2d35;
            border-radius: 4px;
            padding: 6px;
            color: #ffffff;
        }
        QLineEdit:focus {
            border: 1px solid #4a9eff;
        }
        QComboBox {
            background-color: #1a1d25;
            border: 1px solid #2a2d35;
            border-radius: 4px;
            padding: 6px;
            color: #ffffff;
        }
        QComboBox::drop-down {
            border: none;
        }
        QComboBox::down-arrow {
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 4px solid #ffffff;
        }
        QCheckBox {
            color: #ffffff;
            spacing: 8px;
        }
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
            border: 1px solid #2a2d35;
            border-radius: 3px;
            background-color: #1a1d25;
        }
        QCheckBox::indicator:checked {
            background-color: #4a9eff;
            border: 1px solid #4a9eff;
        }
        QSlider::groove:horizontal {
            height: 6px;
            background: #2a2d35;
            border-radius: 3px;
        }
        QSlider::handle:horizontal {
            background: #ffd700;
            border: none;
            width: 16px;
            height: 16px;
            border-radius: 8px;
            margin: -5px 0;
        }
        QSlider::sub-page:horizontal {
            background: #4a9eff;
            border-radius: 3px;
        }
        QTextEdit {
            background-color: #12141a;
            border: 1px solid #2a2d35;
            border-radius: 6px;
            color: #ffffff;
            padding: 8px;
        }
        QTabWidget::pane {
            border: 1px solid #2a2d35;
            background-color: #12141a;
        }
        QTabBar::tab {
            background-color: #1a1d25;
            color: #888;
            padding: 8px 16px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        QTabBar::tab:selected {
            background-color: #12141a;
            color: #ffffff;
        }
        """

    def initUI(self):
        from utils.config_loader import load_api_keys
        from core.trader import TraderAccount
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_container = QVBoxLayout(central_widget)
        main_container.setSpacing(0)
        main_container.setContentsMargins(0, 0, 0, 0)
        header_bar = self.create_header_bar()
        main_container.addWidget(header_bar)
        # Content area in a scroll area for responsiveness
        content_widget = QWidget()
        main_layout = QHBoxLayout(content_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        # Load accounts from config
        self.accounts_config = load_api_keys()[:10]
        self.trader_accounts = [TraderAccount(**cfg) for cfg in self.accounts_config]
        # Wrap each panel in its own scroll area for small screens
        left_panel_scroll = QScrollArea()
        left_panel_scroll.setWidgetResizable(True)
        left_panel_widget = QWidget()
        left_panel_layout = self.create_left_panel()
        left_panel_widget.setLayout(left_panel_layout)
        left_panel_scroll.setWidget(left_panel_widget)
        center_panel_scroll = QScrollArea()
        center_panel_scroll.setWidgetResizable(True)
        center_panel_widget = QWidget()
        center_panel_layout = self.create_center_panel()
        center_panel_widget.setLayout(center_panel_layout)
        center_panel_scroll.setWidget(center_panel_widget)
        right_panel_scroll = QScrollArea()
        right_panel_scroll.setWidgetResizable(True)
        right_panel_widget = QWidget()
        right_panel_layout = self.create_right_panel()
        right_panel_widget.setLayout(right_panel_layout)
        right_panel_scroll.setWidget(right_panel_widget)
        main_layout.addWidget(left_panel_scroll, 2)  # 20% width
        main_layout.addWidget(center_panel_scroll, 5)  # 50% width
        main_layout.addWidget(right_panel_scroll, 3)  # 30% width
        # Wrap content_widget in a scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(content_widget)
        main_container.addWidget(scroll_area)
        # Set minimum sizes for better small screen support
        content_widget.setMinimumWidth(900)
        content_widget.setMinimumHeight(600)

    def create_header_bar(self):
        """Create the top header bar"""
        header_widget = QWidget()
        header_widget.setStyleSheet("""
            QWidget {
                background-color: #1a1d25;
                border-bottom: 1px solid #2a2d35;
                padding: 8px;
            }
        """)
        header_widget.setFixedHeight(40)
        
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(15, 5, 15, 5)
        
        # Left side - App title with lightning icon
        title_layout = QHBoxLayout()
        title_label = QLabel("⚡ HyperLiquid Sniper")
        title_label.setStyleSheet("color: #ffd700; font-weight: bold; font-size: 16px;")
        title_layout.addWidget(title_label)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        # Right side - Status indicators
        status_layout = QHBoxLayout()
        
        # Connected status
        connected_label = QLabel("● Connected")
        connected_label.setStyleSheet("color: #00ff7f; font-size: 12px; font-weight: bold;")
        status_layout.addWidget(connected_label)
        
        # Separator
        sep1 = QLabel("|")
        sep1.setStyleSheet("color: #555; margin: 0 10px;")
        status_layout.addWidget(sep1)
        
        # Active Orders
        orders_label = QLabel("Active Orders: 23")
        orders_label.setStyleSheet("color: #ffffff; font-size: 12px;")
        status_layout.addWidget(orders_label)
        
        # Separator
        sep2 = QLabel("|")
        sep2.setStyleSheet("color: #555; margin: 0 10px;")
        status_layout.addWidget(sep2)
        
        # Total PnL
        pnl_label = QLabel("Total PnL: +$1,247.83")
        pnl_label.setStyleSheet("color: #00ff7f; font-size: 12px; font-weight: bold;")
        status_layout.addWidget(pnl_label)
        
        # Separator
        sep3 = QLabel("|")
        sep3.setStyleSheet("color: #555; margin: 0 10px;")
        status_layout.addWidget(sep3)
        
        # Accounts
        accounts_label = QLabel("Accounts: 7/10")
        accounts_label.setStyleSheet("color: #ffffff; font-size: 12px;")
        status_layout.addWidget(accounts_label)
        
        header_layout.addLayout(status_layout)
        
        return header_widget

    def create_left_panel(self):
        """Create the accounts management panel"""
        left_layout = QVBoxLayout()
        
        header = QLabel("ACCOUNTS MANAGEMENT")
        header.setStyleSheet("font-weight: bold; font-size: 14px; color: #ffd700; margin-bottom: 10px;")
        left_layout.addWidget(header)

        # Dynamically create account groups from loaded accounts
        self.account_groups = []
        for i, trader in enumerate(getattr(self, 'trader_accounts', [])):
            account_group = self.create_account_group(i+1, trader)
            left_layout.addWidget(account_group)
            self.account_groups.append(account_group)

        left_layout.addStretch()
        return left_layout

    def create_account_group(self, account_num, trader=None):
        """Create individual account group, optionally with trader info"""
        group = QGroupBox(f"Account {account_num}")
        layout = QVBoxLayout()

        # Status and balance info
        status_layout = QHBoxLayout()
        
        # Checkbox for account selection
        checkbox = QCheckBox()
        status_layout.addWidget(checkbox)
        
        # Status label
        status = QLabel("ACTIVE" if trader else "INACTIVE")
        status.setStyleSheet("color: #00ff7f; font-weight: bold;" if trader else "color: #ff4757; font-weight: bold;")
        status_layout.addWidget(status)
        
        status_layout.addStretch()
        layout.addLayout(status_layout)

        # Pair selection
        pair_combo = QComboBox()
        pair_combo.addItems(["BTC/USDT", "ETH/USDT", "SOL/USDT"])
        layout.addWidget(pair_combo)

        # Leverage and balance info
        leverage_label = QLabel(f"20x Leverage")
        leverage_label.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(leverage_label)

        balance_label = QLabel("Balance: $--" if not trader else f"Balance: $5,247.83")
        balance_label.setStyleSheet("color: #ffffff; font-size: 11px;")
        layout.addWidget(balance_label)

        pnl_label = QLabel("PnL: --" if not trader else "PnL: +$147.83")
        pnl_label.setStyleSheet("color: #00ff7f; font-size: 11px;")
        layout.addWidget(pnl_label)

        # API Keys section
        api_label = QLabel("API Keys")
        api_label.setStyleSheet("color: #888; font-size: 11px; margin-top: 8px;")
        layout.addWidget(api_label)

        pub_key = QLineEdit()
        pub_key.setPlaceholderText("Public key")
        pub_key.setText(trader.api_key[:6] + "..." if trader else "")
        layout.addWidget(pub_key)

        priv_key = QLineEdit()
        priv_key.setPlaceholderText("Private key")
        priv_key.setEchoMode(QLineEdit.EchoMode.Password)
        priv_key.setText("********" if trader else "")
        layout.addWidget(priv_key)

        # Master/Subscriber checkboxes
        master_cb = QCheckBox("MASTER PAIR")
        subscriber_cb = QCheckBox("SUBSCRIBER PAIR")
        layout.addWidget(master_cb)
        layout.addWidget(subscriber_cb)

        # Trading pair dropdown
        pair_dropdown = QComboBox()
        pair_dropdown.addItems(["BTC/USDT", "ETH/USDT", "SOL/USDT"])
        layout.addWidget(pair_dropdown)

        group.setLayout(layout)
        return group

    def create_center_panel(self):
        """Create the center panel with chart and info"""
        center_layout = QVBoxLayout()

        # Price header
        price_header = QHBoxLayout()
        price_label = QLabel("BTC/USDT - $43,251.47 (+2.34%)")
        price_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #00ff7f; margin-bottom: 10px;")
        price_header.addWidget(price_label)
        
        # Timeframe buttons
        timeframes = ["1m", "5m", "15m", "1h", "4h", "1d"]
        for tf in timeframes:
            btn = QPushButton(tf)
            if tf == "15m":
                btn.setStyleSheet("background-color: #ffd700; color: #000; padding: 4px 8px; border-radius: 3px; font-weight: bold;")
            else:
                btn.setStyleSheet("background-color: #2a2d35; color: #888; padding: 4px 8px; border-radius: 3px;")
            price_header.addWidget(btn)
        
        price_header.addStretch()
        center_layout.addLayout(price_header)

        # Chart
        self.chart = QWebEngineView()
        self.chart.setHtml(self.get_tradingview_html())
        center_layout.addWidget(self.chart, 3)

        # Bottom info panel with tabs
        info_tabs = QTabWidget()
        info_tabs.setMaximumHeight(250)
        
        # Balances tab
        balances_widget = QWidget()
        balances_layout = QVBoxLayout()
        balances_text = QTextEdit()
        balances_text.setPlainText("No balance yet")
        balances_text.setReadOnly(True)
        balances_text.setMaximumHeight(200)
        balances_layout.addWidget(balances_text)
        balances_widget.setLayout(balances_layout)
        info_tabs.addTab(balances_widget, "Balances")
        
        # Other tabs
        for tab_name in ["Positions", "Open Orders", "Trade History", "Funding History", "Order History"]:
            tab_widget = QWidget()
            tab_layout = QVBoxLayout()
            tab_text = QTextEdit()
            tab_text.setPlainText(f"{tab_name} data will appear here")
            tab_text.setReadOnly(True)
            tab_text.setMaximumHeight(200)
            tab_layout.addWidget(tab_text)
            tab_widget.setLayout(tab_layout)
            info_tabs.addTab(tab_widget, tab_name)

        center_layout.addWidget(info_tabs, 1)
        return center_layout

    def create_right_panel(self):
        """Create the trading controls panel"""
        right_layout = QVBoxLayout()

        # Header with connection status (removed since it's now in top bar)
        header_label = QLabel("TRADING CONTROLS")
        header_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #ffd700; margin-bottom: 10px;")
        right_layout.addWidget(header_label)

        # Order type buttons
        order_type_layout = QHBoxLayout()
        self.market_btn = QPushButton("Market")
        self.limit_btn = QPushButton("Limit")
        
        self.market_btn.setCheckable(True)
        self.limit_btn.setCheckable(True)
        self.market_btn.setChecked(True)
        
        self.market_btn.clicked.connect(self.toggle_order_type)
        self.limit_btn.clicked.connect(self.toggle_order_type)
        
        self.update_order_buttons()
        
        order_type_layout.addWidget(self.market_btn)
        order_type_layout.addWidget(self.limit_btn)
        right_layout.addLayout(order_type_layout)

        # Leverage section
        leverage_layout = QHBoxLayout()
        leverage_label = QLabel("Leverage")
        leverage_label.setStyleSheet("color: #ffffff; font-weight: bold;")
        leverage_layout.addWidget(leverage_label)
        
        # Cross/Isolated toggle
        cross_btn = QPushButton("Cross")
        isolated_btn = QPushButton("Isolated")
        cross_btn.setStyleSheet("background-color: #2a2d35; color: #ffffff; padding: 4px 8px; border-radius: 3px;")
        isolated_btn.setStyleSheet("background-color: #2a2d35; color: #888; padding: 4px 8px; border-radius: 3px;")
        
        leverage_layout.addWidget(cross_btn)
        leverage_layout.addWidget(isolated_btn)
        right_layout.addLayout(leverage_layout)

        # Leverage slider
        leverage_slider_layout = QHBoxLayout()
        leverage_slider_layout.addWidget(QLabel("0x"))
        
        leverage_slider = QSlider(Qt.Orientation.Horizontal)
        leverage_slider.setRange(0, 100)
        leverage_slider.setValue(50)
        leverage_slider_layout.addWidget(leverage_slider)
        
        leverage_slider_layout.addWidget(QLabel("100x"))
        right_layout.addLayout(leverage_slider_layout)

        # Take profits section
        tp_label = QLabel("Take profits (7 max)")
        tp_label.setStyleSheet("color: #00ff7f; font-weight: bold; margin-top: 15px;")
        right_layout.addWidget(tp_label)

        # Take profit rows
        for i in range(7):
            tp_layout = QHBoxLayout()
            
            cb = QCheckBox()
            if i == 0:  # First one checked
                cb.setChecked(True)
            
            size_input = QLineEdit()
            size_input.setPlaceholderText("Enter size")
            if i == 0:
                size_input.setText("10.0")
            
            profit_input = QLineEdit()
            profit_input.setPlaceholderText("Enter profit")
            if i == 0:
                profit_input.setText("15%")
            
            reset_btn = QPushButton("Reset")
            reset_btn.setStyleSheet("background-color: #ffd700; color: #000; padding: 4px 8px; border-radius: 3px; font-weight: bold;")
            reset_btn.setFixedWidth(60)
            
            tp_layout.addWidget(cb)
            tp_layout.addWidget(size_input)
            tp_layout.addWidget(profit_input)
            tp_layout.addWidget(reset_btn)
            
            right_layout.addLayout(tp_layout)

        # Limit order section
        limit_label = QLabel("Limit order")
        limit_label.setStyleSheet("color: #ffffff; font-weight: bold; margin-top: 15px;")
        right_layout.addWidget(limit_label)

        entry_price = QLineEdit()
        entry_price.setPlaceholderText("Enter price")
        right_layout.addWidget(entry_price)

        # Position size
        pos_size_label = QLabel("Position Size: +$1000")
        pos_size_label.setStyleSheet("color: #888;")
        right_layout.addWidget(pos_size_label)

        pos_slider = QSlider(Qt.Orientation.Horizontal)
        pos_slider.setRange(0, 100)
        pos_slider.setValue(50)
        right_layout.addWidget(pos_slider)

        # Stop loss
        stop_loss_layout = QHBoxLayout()
        stop_loss_label = QLabel("Stop Loss: 2.5%")
        stop_loss_label.setStyleSheet("color: #888;")
        stop_loss_layout.addWidget(stop_loss_label)
        stop_loss_layout.addWidget(QLabel("or"))
        
        stop_input = QLineEdit()
        stop_input.setPlaceholderText("Enter %")
        stop_input.setFixedWidth(80)
        stop_loss_layout.addWidget(stop_input)
        
        right_layout.addLayout(stop_loss_layout)

        stop_slider = QSlider(Qt.Orientation.Horizontal)
        stop_slider.setRange(0, 100)
        stop_slider.setValue(25)
        right_layout.addWidget(stop_slider)

        # Long/Short buttons
        trade_buttons_layout = QHBoxLayout()
        self.long_btn = QPushButton("LONG")
        self.long_btn.setStyleSheet("background-color: #00ff7f; color: #000000; font-weight: bold; padding: 12px; border-radius: 6px; font-size: 14px;")
        self.short_btn = QPushButton("SHORT")
        self.short_btn.setStyleSheet("background-color: #ff4757; color: #FFFFFF; font-weight: bold; padding: 12px; border-radius: 6px; font-size: 14px;")
        trade_buttons_layout.addWidget(self.long_btn)
        trade_buttons_layout.addWidget(self.short_btn)
        right_layout.addLayout(trade_buttons_layout)

        # Connect trading buttons to backend
        self.long_btn.clicked.connect(self.place_long_order)
        self.short_btn.clicked.connect(self.place_short_order)

        # Order split section
        split_cb = QCheckBox("Order split")
        right_layout.addWidget(split_cb)

        split_layout = QHBoxLayout()
        split_layout.addWidget(QLabel("min:"))
        min_input = QLineEdit()
        min_input.setPlaceholderText("Enter %")
        min_input.setFixedWidth(60)
        split_layout.addWidget(min_input)
        
        split_layout.addWidget(QLabel("max:"))
        max_input = QLineEdit()
        max_input.setPlaceholderText("Enter %")
        max_input.setFixedWidth(60)
        split_layout.addWidget(max_input)
        
        right_layout.addLayout(split_layout)

        # Split slider with labels
        split_slider_layout = QHBoxLayout()
        split_slider_layout.addWidget(QLabel("0"))
        
        split_slider = QSlider(Qt.Orientation.Horizontal)
        split_slider.setRange(0, 100)
        split_slider.setValue(10)
        split_slider_layout.addWidget(split_slider)
        
        split_slider_layout.addWidget(QLabel("100"))
        right_layout.addLayout(split_slider_layout)

        # Action buttons
        close_all_btn = QPushButton("Close All Positions")
        close_all_btn.setStyleSheet("background-color: #ff1744; color: #fff; font-weight: bold; padding: 8px; border-radius: 4px; margin-top: 10px;")
        right_layout.addWidget(close_all_btn)

        cancel_all_btn = QPushButton("Cancel All Orders")
        cancel_all_btn.setStyleSheet("background-color: #ffa726; color: #000; font-weight: bold; padding: 8px; border-radius: 4px;")
        right_layout.addWidget(cancel_all_btn)

        right_layout.addStretch()
        return right_layout

    def toggle_order_type(self):
        """Toggle between Market and Limit order types"""
        sender = self.sender()
        if sender == self.market_btn:
            self.market_btn.setChecked(True)
            self.limit_btn.setChecked(False)
        else:
            self.limit_btn.setChecked(True)
            self.market_btn.setChecked(False)
        self.update_order_buttons()

    def update_order_buttons(self):
        """Update the styling of order type buttons"""
        if self.market_btn.isChecked():
            self.market_btn.setStyleSheet("background-color: #4a9eff; color: #fff; font-weight: bold; padding: 8px; border-radius: 4px;")
            self.limit_btn.setStyleSheet("background-color: #2a2d35; color: #888; padding: 8px; border-radius: 4px;")
        else:
            self.limit_btn.setStyleSheet("background-color: #4a9eff; color: #fff; font-weight: bold; padding: 8px; border-radius: 4px;")
            self.market_btn.setStyleSheet("background-color: #2a2d35; color: #888; padding: 8px; border-radius: 4px;")

    def get_tradingview_html(self):
        """Generate TradingView chart HTML"""
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
            <style>
                body { margin: 0; padding: 0; background: #0a0b0f; }
                #tradingview_chart { background: #0a0b0f; }
            </style>
        </head>
        <body>
            <div id="tradingview_chart"></div>
            <script type="text/javascript">
                new TradingView.widget({
                    "width": "100%",
                    "height": 600,
                    "symbol": "BINANCE:BTCUSDT",
                    "interval": "15",
                    "timezone": "Etc/UTC",
                    "theme": "dark",
                    "style": "1",
                    "locale": "en",
                    "toolbar_bg": "#0a0b0f",
                    "enable_publishing": false,
                    "backgroundColor": "#0a0b0f",
                    "gridColor": "#1a1d25",
                    "hide_top_toolbar": false,
                    "hide_legend": false,
                    "save_image": false,
                    "container_id": "tradingview_chart",
                    "studies": ["MASimple@tv-basicstudies"],
                    "overrides": {
                        "paneProperties.background": "#0a0b0f",
                        "paneProperties.vertGridProperties.color": "#1a1d25",
                        "paneProperties.horzGridProperties.color": "#1a1d25",
                        "symbolWatermarkProperties.transparency": 90,
                        "scalesProperties.textColor": "#888888"
                    }
                });
            </script>
        </body>
        </html>
        '''

    def place_long_order(self):
        self.place_order(direction="buy")

    def place_short_order(self):
        self.place_order(direction="sell")

    def place_order(self, direction):
        # Example: place order for all loaded accounts (can be refined for per-account)
        from core.order_splitter import generate_splits
        import asyncio
        order_type = "market" if self.market_btn.isChecked() else "limit"
        size = 1.0  # TODO: get from UI
        price = None  # TODO: get from UI if limit
        symbol = "BTCUSDT"  # TODO: get from UI
        for trader in getattr(self, 'trader_accounts', []):
            async def do_order(trader=trader):
                await trader.place_order(symbol, direction, order_type, size, price)
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            loop.create_task(do_order())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    window = HyperliquidSniper()
    window.show()
    sys.exit(app.exec())