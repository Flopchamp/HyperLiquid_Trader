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
        self.entry_price = None # Initialize entry_price, to be set by chart click

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

        # Symbol Input
        symbol_layout = QHBoxLayout()
        self.symbol_input = QLineEdit("BTC") # Default to BTC
        self.symbol_input.setPlaceholderText("E.g., BTC, ETH")
        symbol_layout.addWidget(QLabel("Symbol:"))
        symbol_layout.addWidget(self.symbol_input)

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
        group_layout.addLayout(symbol_layout) # Add symbol layout here
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
        self.symbol_input.setToolTip("Enter the trading symbol (e.g., BTC, ETH)")


    def set_entry_price(self, price: float):
        """Sets the entry price, typically from a chart click."""
        self.entry_price = price
        # Optionally, update a UI field if you have one for entry price display
        logging.info(f"ControlsPanel: Entry price set to {price}")
        self.show_notification(f"Chart entry price updated: {price:.2f}")

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
        # Wrap the core logic in an async function to allow await calls
        async def determine_and_place_order():
            # Get symbol from the new input field
            symbol = self.symbol_input.text().upper().strip()
            if not symbol:
                self.log_and_show_error("Symbol cannot be empty. Please enter a trading symbol.")
                return
            
            # 1. Get UI inputs
            # Clicked chart price is now self.entry_price, set by set_entry_price via handle_chart_event
            if self.entry_price is None and self.order_type.currentText().lower() == 'limit':
                self.log_and_show_error("Limit order selected, but no entry price set from chart.")
                return

            clicked_chart_price = self.entry_price if self.entry_price is not None else 0.0 # Default if not set, for safety

            ui_order_type = self.order_type.currentText().lower()
            ui_direction = self.direction.currentText().lower()
            ui_price_context = self.price_context.currentText() # "At Market", "Above Market", "Below Market"

            sl_percent = self.sl_input.value()
            leverage_val = self.leverage_input.value()
            position_size_percent = self.position_size_input.value()
            margin_mode = self.margin_mode.currentText().lower()
            tps_percents = [tp.value() for tp in self.tp_inputs if tp.value() > 0]
            
            # Validators (already present in original code, ensure they are called)
            from utils.validators import validate_splits, validate_tp_values, validate_sl_value # Assuming these are available
            use_range = self.range_checkbox.isChecked()
            split_count = self.split_count.value()
            if use_range and not validate_splits(ui_order_type, split_count):
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Invalid Input", f"Split count exceeds allowed limit for {ui_order_type} orders.")
                return
            if not validate_tp_values(tps_percents): # Pass the list of values
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Invalid Input", "TP values must be positive and in ascending order.")
                return
            if sl_percent > 0 and not validate_sl_value(sl_percent): # SL can be 0 if not used
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Invalid Input", "SL value must be positive if set.")
                return


            # 2. Get active trader account for operations
            main_window = self.parent()
            while main_window and not hasattr(main_window, "account_panels"):
                main_window = main_window.parent()
            
            active_trader = None
            if main_window:
                if hasattr(main_window, "copy_trading_manager") and main_window.copy_trading_manager:
                    active_trader = main_window.copy_trading_manager.master
                elif hasattr(main_window, "account_panels") and main_window.account_panels:
                    active_trader = main_window.account_panels[0].trader_account # Fallback
            
            if not active_trader:
                self.log_and_show_error("No active trader account available.")
                return

            # 3. Fetch current market price
            current_market_price = await active_trader.get_market_price(symbol)
            if current_market_price is None:
                self.log_and_show_error(f"Could not fetch market price for {symbol}.")
                return

            # 4. Determine final order parameters
            final_order_type = ui_order_type
            final_side = ui_direction
            final_price = None

            if ui_order_type == 'market' or ui_price_context == "At Market":
                final_order_type = 'market'
                final_side = ui_direction
                final_price = None # Market order price is None
                self.show_notification(f"Preparing {final_side.upper()} MARKET order for {symbol}.")
            else: # ui_order_type is 'limit' and ui_price_context is "Above Market" or "Below Market"
                if self.entry_price is None: # Should have been caught earlier, but double check
                    self.log_and_show_error("Limit order requires an entry price from the chart.")
                    return
                final_order_type = 'limit'
                final_price = clicked_chart_price # Price is from chart click

                if clicked_chart_price > current_market_price:
                    if ui_direction == 'long':
                        final_side = 'long'
                        self.show_notification(f"Intending LONG, click {clicked_chart_price:.2f} > market {current_market_price:.2f}. LIMIT BUY.")
                    else: # ui_direction == 'short'
                        final_side = 'short'
                        self.show_notification(f"Intending SHORT, click {clicked_chart_price:.2f} > market {current_market_price:.2f}. LIMIT SELL.")
                elif clicked_chart_price < current_market_price:
                    if ui_direction == 'long':
                        final_side = 'long'
                        self.show_notification(f"Intending LONG, click {clicked_chart_price:.2f} < market {current_market_price:.2f}. LIMIT BUY.")
                    else: # ui_direction == 'short'
                        final_side = 'short'
                        self.show_notification(f"Intending SHORT, click {clicked_chart_price:.2f} < market {current_market_price:.2f}. LIMIT SELL.")
                else: # clicked_chart_price == current_market_price
                    final_side = ui_direction
                    self.show_notification(f"Click {clicked_chart_price:.2f} == market {current_market_price:.2f}. LIMIT {final_side.upper()}.")
            
            # 5. Calculate asset size
            calculated_asset_size = 0
            price_for_size_calc = final_price if final_order_type == 'limit' else current_market_price

            if price_for_size_calc is not None and price_for_size_calc > 0:
                account_equity = await active_trader.get_account_equity()
                if account_equity is not None and account_equity > 0:
                    margin_to_allocate = account_equity * (position_size_percent / 100.0)
                    calculated_asset_size = (margin_to_allocate * leverage_val) / price_for_size_calc
                    logging.info(f"Calculated asset size: {calculated_asset_size} (Equity: {account_equity}, %Size: {position_size_percent}%, Leverage: {leverage_val}, Price: {price_for_size_calc})")
                else:
                    self.log_and_show_error("Could not calculate asset size: Invalid account equity.")
                    return
            else:
                self.log_and_show_error("Could not calculate asset size: Invalid price for calculation.")
                return

            if calculated_asset_size <= 0:
                self.log_and_show_error(f"Calculated asset size is not positive: {calculated_asset_size}. Check inputs.")
                return

            # 6. Construct order_data
            order_data = {
                'symbol': symbol,
                'side': final_side,
                'order_type': final_order_type,
                'size': calculated_asset_size,
                'price': final_price,
                'leverage': leverage_val,
                'margin_mode': margin_mode,
                'sl': sl_percent if sl_percent > 0 else None,
                'tps': [{'profit_perc': tp_val} for tp_val in tps_percents] if tps_percents else None,
            }
            logging.info(f"Intelligent Chart Trading decision: Clicked={clicked_chart_price}, Market={current_market_price}, UI Direction={ui_direction}, UI Context={ui_price_context} -> Order: {order_data}")

            # 7. Place order (via copy trading manager or directly)
            if main_window and hasattr(main_window, "copy_trading_manager") and main_window.copy_trading_manager:
                main_window.copy_trading_manager.mirror_order(order_data)
                self.show_notification(f"Order mirrored: {final_side.upper()} {final_order_type.upper()} for {symbol}")
            elif active_trader: # Fallback to direct placement on active_trader
                try:
                    result = await active_trader.place_order(**order_data)
                    self.show_notification(f"Order placed on Acct {active_trader.account_id}: {result.get('status', 'Unknown status') if isinstance(result, dict) else result}")
                    logging.info(f"Direct order placement result: {result}")
                except Exception as e_place:
                    self.log_and_show_error(f"Error placing order directly: {e_place}")
            else:
                self.log_and_show_error("No mechanism to place order (no copy manager or active trader).")

        # Run the async function
        try:
            import asyncio
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            loop.create_task(determine_and_place_order())
        except Exception as e:
            self.log_and_show_error(f"Error initiating order placement: {e}")

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
