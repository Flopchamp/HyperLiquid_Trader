class CopyTradingManager:
    def __init__(self, master_account, subscriber_accounts, pair_map=None):
        self.master = master_account
        self.subscribers = subscriber_accounts
        self.pair_map = pair_map or {}  # {subscriber_account_id: symbol}

    def mirror_order(self, order_data):
        """
        Mirror the master order to all subscribers.
        order_data: dict with keys like symbol, side, order_type, size, price, sl, tps, etc.
        """
        for sub in self.subscribers:
            sub_order = order_data.copy()
            # Map symbol if a mapping exists for this subscriber
            mapped_symbol = self.pair_map.get(getattr(sub, 'account_id', None))
            if mapped_symbol:
                sub_order['symbol'] = mapped_symbol
            # Place order for subscriber
            import asyncio
            async def do_order():
                await sub.place_order(**sub_order)
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            loop.create_task(do_order())
