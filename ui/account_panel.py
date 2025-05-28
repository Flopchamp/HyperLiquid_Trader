# ui/account_panel.py
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGroupBox, QListWidget, QListWidgetItem
from ui.status_log import StatusLog
from core.trader import TraderAccount

class AccountPanel(QWidget):
    def __init__(self, account_id=1, trader_account=None, parent=None):
        super().__init__(parent)
        self.trader_account = trader_account
        layout = QVBoxLayout(self)
        label = QLabel(f"Account Panel {account_id}")
        layout.addWidget(label)
        self.status_log = StatusLog()
        layout.addWidget(self.status_log)
        # Trade Analytics & History Section
        self.positions_group = QGroupBox("Active Positions")
        self.positions_list = QListWidget()
        pos_layout = QVBoxLayout()
        pos_layout.addWidget(self.positions_list)
        self.positions_group.setLayout(pos_layout)
        layout.addWidget(self.positions_group)
        self.history_group = QGroupBox("Order History")
        self.history_list = QListWidget()
        hist_layout = QVBoxLayout()
        hist_layout.addWidget(self.history_list)
        self.history_group.setLayout(hist_layout)
        layout.addWidget(self.history_group)
        # Demo: Log a status message on creation
        self.log_status(f"Account {account_id} panel initialized.")
        # Demo button to test backend connection
        if self.trader_account:
            from PyQt6.QtWidgets import QPushButton
            self.test_btn = QPushButton("Test Connect")
            self.test_btn.clicked.connect(self.test_connect)
            layout.addWidget(self.test_btn)
            # Start real-time order updates
            import asyncio
            async def listen_updates():
                def on_update(update):
                    self.log_status(f"Order update: {update}")
                await self.trader_account.listen_order_updates(on_update)
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            loop.create_task(listen_updates())

    def log_status(self, message: str):
        self.status_log.append(message)

    def update_positions(self, positions):
        self.positions_list.clear()
        for pos in positions:
            item = QListWidgetItem(
                f"{pos['symbol']} {pos['side'].upper()} | Size: {pos['size']} | Entry: {pos['entry']} | "
                f"Leverage: {pos['leverage']}x | PnL: {pos['pnl']:+.2f}"
            )
            self.positions_list.addItem(item)

    def log_trade(self, trade_info: str):
        self.history_list.addItem(trade_info)

    def set_sl_tp(self, sl, tps):
        if self.trader_account:
            self.trader_account.set_stop_loss(sl)
            self.trader_account.set_take_profits(tps)
            self.log_status(f"SL set to {sl}, TPs set to {tps}")

    def trigger_order(self, symbol, side, order_type, size, price=None):
        if self.trader_account:
            import asyncio
            async def do_order():
                try:
                    result = await self.trader_account.place_order(symbol, side, order_type, size, price)
                    self.log_status(f"Order result: {result}")
                    self.log_trade(f"Order: {order_type} {side} {symbol} {size} @ {price if price else 'MKT'} | Result: {result}")
                except Exception as e:
                    self.log_status(f"Order error: {e}")
            asyncio.create_task(do_order())

    def test_connect(self):
        if self.trader_account:
            import asyncio
            async def do_connect():
                try:
                    await self.trader_account.connect()
                    self.log_status("Connected to Hyperliquid API!")
                except Exception as e:
                    self.log_status(f"Connection error: {e}")
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            loop.create_task(do_connect())
