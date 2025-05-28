import logging
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QLineEdit,
    QCheckBox, QSpinBox, QDoubleSpinBox, QGroupBox, QPushButton
)
from PyQt6.QtCore import Qt

# Setup logging
log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'trader.log')
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)

class ControlsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        group_box = QGroupBox("Trading Controls")
        group_layout = QVBoxLayout()

        # Order Type and Direction
        order_layout = QHBoxLayout()
        self.order_type = QComboBox()
        self.order_type.addItems(["Market", "Limit"])
        self.direction = QComboBox()
        self.direction.addItems(["Long", "Short"])
        order_layout.addWidget(QLabel("Order Type:"))
        order_layout.addWidget(self.order_type)
        order_layout.addWidget(QLabel("Direction:"))
        order_layout.addWidget(self.direction)

        # SL %, Leverage, Position Size
        sl_layout = QHBoxLayout()
        self.sl_input = QDoubleSpinBox()
        self.sl_input.setSuffix(" %")
        self.sl_input.setDecimals(2)
        self.sl_input.setRange(0.01, 100.0)
        self.sl_input.setValue(1.5)

        self.leverage_input = QSpinBox()
        self.leverage_input.setRange(1, 100)
        self.leverage_input.setValue(10)

        self.position_size_input = QDoubleSpinBox()
        self.position_size_input.setSuffix(" %")
        self.position_size_input.setRange(1, 100)
        self.position_size_input.setValue(10)

        sl_layout.addWidget(QLabel("SL %:"))
        sl_layout.addWidget(self.sl_input)
        sl_layout.addWidget(QLabel("Leverage:"))
        sl_layout.addWidget(self.leverage_input)
        sl_layout.addWidget(QLabel("Position Size:"))
        sl_layout.addWidget(self.position_size_input)

        # Margin Mode
        self.margin_mode = QComboBox()
        self.margin_mode.addItems(["Isolated", "Cross"])

        # TP Inputs and PnL Labels
        tp_layout = QHBoxLayout()
        self.tp_inputs = []
        self.tp_pnl_labels = []
        for i in range(5):
            tp_input = QDoubleSpinBox()
            tp_input.setSuffix(" %")
            tp_input.setRange(0.1, 100)
            tp_input.setSingleStep(0.5)
            tp_input.valueChanged.connect(self.update_tp_pnls)
            self.tp_inputs.append(tp_input)
            tp_layout.addWidget(QLabel(f"TP{i+1}:"))
            tp_layout.addWidget(tp_input)
            pnl_label = QLabel("PnL: -")
            self.tp_pnl_labels.append(pnl_label)
            tp_layout.addWidget(pnl_label)

        # Range Entry Toggle
        range_layout = QVBoxLayout()
        self.range_checkbox = QCheckBox("Enable Range Entry")
        self.range_checkbox.stateChanged.connect(self.toggle_range_inputs)

        self.range_inputs = QHBoxLayout()
        self.range_percent = QDoubleSpinBox()
        self.range_percent.setSuffix(" %")
        self.range_percent.setRange(0.1, 5.0)
        self.range_percent.setValue(0.25)

        self.split_count = QSpinBox()
        self.split_count.setRange(1, 100)
        self.split_count.setValue(5)

        self.range_inputs.addWidget(QLabel("Range ±:"))
        self.range_inputs.addWidget(self.range_percent)
        self.range_inputs.addWidget(QLabel("Splits:"))
        self.range_inputs.addWidget(self.split_count)

        range_layout.addWidget(self.range_checkbox)
        range_layout.addLayout(self.range_inputs)

        # Hide range inputs initially
        self.toggle_range_inputs(0)

        # Add to group layout
        group_layout.addLayout(order_layout)
        group_layout.addLayout(sl_layout)
        group_layout.addWidget(QLabel("Margin Mode:"))
        group_layout.addWidget(self.margin_mode)
        group_layout.addLayout(tp_layout)
        group_layout.addLayout(range_layout)

        group_box.setLayout(group_layout)
        layout.addWidget(group_box)

        # Add Place Order button
        self.place_order_btn = QPushButton("Place Order")
        layout.addWidget(self.place_order_btn)
        self.place_order_btn.clicked.connect(self.on_place_order)

        # Add Cancel/Reset TP and Add-to-Position buttons
        self.cancel_tp_btn = QPushButton("Cancel TPs")
        self.reset_tp_btn = QPushButton("Reset TPs")
        self.add_to_position_btn = QPushButton("Add to Position")
        layout.addWidget(self.cancel_tp_btn)
        layout.addWidget(self.reset_tp_btn)
        layout.addWidget(self.add_to_position_btn)
        self.cancel_tp_btn.clicked.connect(self.on_cancel_tps)
        self.reset_tp_btn.clicked.connect(self.on_reset_tps)
        self.add_to_position_btn.clicked.connect(self.on_add_to_position)

        # Add price context dropdown
        self.price_context = QComboBox()
        self.price_context.addItems(["At Market", "Above Market", "Below Market"])
        layout.addWidget(QLabel("Price Context:"))
        layout.addWidget(self.price_context)

        # Tooltips
        self.order_type.setToolTip("Select order type: Market or Limit")
        self.direction.setToolTip("Select trade direction: Long or Short")
        self.sl_input.setToolTip("Set stop loss percentage")
        self.leverage_input.setToolTip("Set leverage for the trade")
        self.position_size_input.setToolTip("Set position size as a percentage of account balance")
        self.margin_mode.setToolTip("Select margin mode: Isolated or Cross")
        for i, tp_input in enumerate(self.tp_inputs):
            tp_input.setToolTip(f"Set Take Profit {i+1} percentage")
            self.tp_pnl_labels[i].setToolTip(f"Estimated PnL for TP{i+1}")
        self.range_checkbox.setToolTip("Enable range entry for split orders")
        self.range_percent.setToolTip("Set range percentage for split orders")
        self.split_count.setToolTip("Set number of splits for range entry")
        self.place_order_btn.setToolTip("Place the order with the current settings")
        self.cancel_tp_btn.setToolTip("Cancel all Take Profits for all accounts")
        self.reset_tp_btn.setToolTip("Reset all Take Profits for all accounts")
        self.add_to_position_btn.setToolTip("Add to the current position (capped at 100%)")
        self.price_context.setToolTip("Set price context: At Market, Above Market, or Below Market")

        # Default values
        self.entry_price = 20000.0  # Default entry price, can be set from chart click
        self.position_size = 1.0    # Default position size, can be set from input

    def toggle_range_inputs(self, state):
        is_enabled = state == Qt.CheckState.Checked.value
        for i in range(self.range_inputs.count()):
            self.range_inputs.itemAt(i).widget().setVisible(is_enabled)

    def set_status_bar(self, status_bar):
        self.status_bar = status_bar

    def show_notification(self, message):
        if hasattr(self, 'status_bar') and self.status_bar:
            self.status_bar.showMessage(message, 5000)  # Show for 5 seconds

    def on_place_order(self):
        try:
            order_type = self.order_type.currentText().lower()
            direction = self.direction.currentText().lower()
            sl = self.sl_input.value()
            leverage = self.leverage_input.value()
            position_size = self.position_size_input.value()
            margin_mode = self.margin_mode.currentText().lower()
            tps = [tp.value() for tp in self.tp_inputs if tp.value() > 0]
            symbol = "BTCUSDT"
            size = position_size
            price = None
            use_range = self.range_checkbox.isChecked()
            range_percent = self.range_percent.value()
            split_count = self.split_count.value()
            price_context = self.price_context.currentText().lower()
            # Input validation
            from utils.validators import validate_splits, validate_tp_values, validate_sl_value
            if use_range and not validate_splits(order_type, split_count):
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Invalid Input", f"Split count exceeds allowed limit for {order_type} orders.")
                return
            if not validate_tp_values(tps):
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Invalid Input", "TP values must be positive and in ascending order.")
                return
            if not validate_sl_value(sl):
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Invalid Input", "SL value must be positive.")
                return

            parent = self.parent()
            while parent and not hasattr(parent, "account_panels"):
                parent = parent.parent()
            # Copy trading: use CopyTradingManager if available
            if parent and hasattr(parent, "copy_trading_manager") and parent.copy_trading_manager:
                # Build order_data dict for mirroring
                order_data = {
                    'symbol': symbol,
                    'side': direction,
                    'order_type': order_type,
                    'size': size,
                    'price': price,
                    'sl': sl,
                    'tps': tps
                }
                parent.copy_trading_manager.mirror_order(order_data)
                return
            self.show_notification("Order placed successfully.")
            logging.info(f"Order placed: {order_type} {direction} {size}")
            # ...existing code for non-copy trading...
        except Exception as e:
            self.log_and_show_error(f"Order error: {e}")

    def update_tp_pnls(self):
        try:
            entry = getattr(self, 'entry_price', 20000.0)
            size = self.position_size_input.value()
            for i, tp_input in enumerate(self.tp_inputs):
                tp = tp_input.value()
                if tp > 0:
                    pnl = (tp - entry) * size
                    self.tp_pnl_labels[i].setText(f"PnL: {pnl:.2f}")
                else:
                    self.tp_pnl_labels[i].setText("PnL: -")
        except Exception:
            for label in self.tp_pnl_labels:
                label.setText("PnL: -")

    def on_cancel_tps(self):
        try:
            parent = self.parent()
            while parent and not hasattr(parent, "account_panels"):
                parent = parent.parent()
            if parent and hasattr(parent, "account_panels"):
                for panel in parent.account_panels:
                    if hasattr(panel.trader_account, 'cancel_tps'):
                        panel.trader_account.cancel_tps()
                    panel.log_status("TPs cancelled.")
            self.show_notification("TPs cancelled.")
        except Exception as e:
            self.log_and_show_error(f"Cancel TPs error: {e}")

    def on_reset_tps(self):
        try:
            parent = self.parent()
            while parent and not hasattr(parent, "account_panels"):
                parent = parent.parent()
            if parent and hasattr(parent, "account_panels"):
                for panel in parent.account_panels:
                    if hasattr(panel.trader_account, 'reset_tps'):
                        panel.trader_account.reset_tps()
                    panel.log_status("TPs reset.")
            self.show_notification("TPs reset.")
        except Exception as e:
            self.log_and_show_error(f"Reset TPs error: {e}")

    def on_add_to_position(self):
        try:
            parent = self.parent()
            while parent and not hasattr(parent, "account_panels"):
                parent = parent.parent()
            if parent and hasattr(parent, "account_panels"):
                for panel in parent.account_panels:
                    if hasattr(panel.trader_account, 'add_to_position'):
                        import asyncio
                        async def do_add():
                            try:
                                await panel.trader_account.add_to_position(self.position_size_input.value())
                                panel.log_status("Added to position (capped at 100%).")
                            except Exception as e:
                                panel.log_status(f"Add to position error: {e}")
                        try:
                            loop = asyncio.get_running_loop()
                        except RuntimeError:
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                        loop.create_task(do_add())
            self.show_notification("Added to position (capped at 100%).")
        except Exception as e:
            self.log_and_show_error(f"Add to position error: {e}")

    def show_error(self, message):
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.critical(self, "Error", message)

    def log_and_show_error(self, message):
        import logging
        logging.error(message)
        self.show_error(message)
        # Optionally log to a status bar or file
