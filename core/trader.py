import asyncio
from hyperliquid import HyperliquidAsync, HyperliquidWs

class TraderAccount:
    def __init__(self, api_key: str, api_secret: str, account_id: int):
        self.api_key = api_key
        self.api_secret = api_secret
        self.account_id = account_id
        self.client = None
        self.ws = None
        self.connected = False
        self.take_profits = []  # List of TP levels (percent or price)
        self.stop_loss = None   # SL level (percent or price)
        self.position = None    # Track open position info

    async def connect(self):
        self.client = HyperliquidAsync(self.api_key, self.api_secret)
        self.ws = HyperliquidWs(self.api_key, self.api_secret)
        # Optionally test connection here
        self.connected = True

    async def place_order(self, symbol: str, side: str, order_type: str, size: float, price: float = None, **kwargs):
        if not self.connected:
            await self.connect()
        params = {
            'symbol': symbol,
            'side': side,
            'type': order_type,
            'quantity': size
        }
        if order_type == 'limit' and price is not None:
            params['price'] = price
        # Add SL/TP logic here as needed
        try:
            result = await self.client.create_order(**params)
            return result
        except Exception as e:
            return f"API error: {e}"

    async def close_all_positions(self):
        # TODO: Implement logic to close all open positions for this account
        pass

    async def cancel_all_orders(self):
        # TODO: Implement logic to cancel all open orders for this account
        pass

    def set_take_profits(self, tp_levels):
        """Set up to 5 take profit levels."""
        self.take_profits = tp_levels[:5]

    def set_stop_loss(self, sl_level):
        self.stop_loss = sl_level

    async def move_sl_to_previous_tp(self, tp_index):
        """Move SL to the previous TP when a TP is hit."""
        if tp_index > 0 and tp_index <= len(self.take_profits):
            new_sl = self.take_profits[tp_index-1]
            self.set_stop_loss(new_sl)
            # Optionally send order to update SL on exchange

    async def on_tp_filled(self, tp_index):
        """Call this when a TP is filled to auto-move SL to previous TP."""
        await self.move_sl_to_previous_tp(tp_index)
        # Optionally, update SL order on the exchange here

    def reset_tps(self):
        self.take_profits = []
        # Optionally, cancel TP orders on the exchange here

    def cancel_tps(self):
        self.take_profits = []
        # Optionally, cancel TP orders on the exchange here

    async def add_to_position(self, additional_size):
        """Add to the current position, capped at 100%."""
        if self.position:
            max_size = self.position.get('max_size', 1.0)
            new_size = min(self.position['size'] + additional_size, max_size)
            self.position['size'] = new_size
            # Optionally, send order to add to position here

    def calculate_position_size(self, balance, risk_percent, sl_percent):
        """Auto position sizing based on balance, risk %, and SL %."""
        risk_amount = balance * (risk_percent / 100)
        position_size = risk_amount / (sl_percent / 100)
        return position_size

    async def listen_order_updates(self, on_update):
        if not self.ws:
            self.ws = HyperliquidWs(self.api_key, self.api_secret)
        async for update in self.ws.listen_orders():
            on_update(update)

    async def set_leverage(self, symbol: str, leverage: int):
        if not self.connected:
            await self.connect()
        try:
            # Replace with actual Hyperliquid API call if available
            result = await self.client.set_leverage(symbol=symbol, leverage=leverage)
            return result
        except Exception as e:
            return f"Set leverage error: {e}"

    async def set_margin_mode(self, symbol: str, mode: str):
        if not self.connected:
            await self.connect()
        try:
            # Replace with actual Hyperliquid API call if available
            result = await self.client.set_margin_mode(symbol=symbol, mode=mode)
            return result
        except Exception as e:
            return f"Set margin mode error: {e}"

class TraderManager:
    def __init__(self, accounts_config):
        self.accounts = [TraderAccount(**cfg) for cfg in accounts_config]

    async def run_all(self):
        await asyncio.gather(*(account.connect() for account in self.accounts))
        # Add more concurrent tasks as needed

# Example usage (to be called from your main async entrypoint):
# accounts_config = [
#     {'api_key': '...', 'api_secret': '...', 'account_id': 1},
#     ...
# ]
# manager = TraderManager(accounts_config)
# asyncio.run(manager.run_all())
