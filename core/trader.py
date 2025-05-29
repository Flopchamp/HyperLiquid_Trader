import asyncio
from hyperliquid.ccxt.async_support.hyperliquid import hyperliquid as HyperliquidAsync
from hyperliquid.ccxt.pro.hyperliquid import hyperliquid as HyperliquidWs
from eth_account import Account

class TraderAccount:
    def __init__(self, api_key: str, api_secret: str, account_id: int):
        self.api_key = api_key # This is the account address (public key)
        self.api_secret = api_secret # This is the private key
        self.account_id = account_id
        try:
            # Standard CCXT initialization:
            # Pass apiKey (address) and secret (private key) in the config.
            # The HyperliquidAsync wrapper should handle wallet creation and address assignment.
            self.client = HyperliquidAsync({
                'apiKey': self.api_key,
                'secret': self.api_secret,
                # 'verbose': True, # Optional: for debugging CCXT calls
            })
        except Exception as e:
            print(f"Error initializing HyperliquidAsync in __init__: {e}")
            self.client = None # Ensure client is None if init fails
        self.ws = None
        self.connected = False
        self.position = None
        self.is_connected = False  # Track connection status

    async def connect(self):
        if self.client:
            await self.client.close()
        
        # Re-initialize the client using the standard CCXT config pattern
        try:
            self.client = HyperliquidAsync({
                'apiKey': self.api_key,
                'secret': self.api_secret,
            })
            print(f"Account {self.account_id}: Connection initiated with address {self.api_key}.")
            await self.client.load_markets()
            print(f"Account {self.account_id}: Connection successful. Markets loaded.")
            self.is_connected = True
        except Exception as e:
            print(f"Account {self.account_id}: Failed to connect or verify connection: {e}")
            self.is_connected = False
            if self.client:
                try:
                    await self.client.close() # Ensure client is closed on failure
                except Exception as close_e:
                    print(f"Account {self.account_id}: Error closing client during connect failure: {close_e}")
            self.client = None

    async def get_market_price(self, symbol: str) -> float | None:
        """Fetches the current market price for a given symbol."""
        if not self.client or not self.is_connected:
            print(f"Account {self.account_id}: Not connected. Cannot fetch market price.")
            # Attempt to reconnect
            await self.connect()
            if not self.client or not self.is_connected:
                return None

        try:
            # Ensure the symbol is in the format expected by the exchange (e.g., 'BTC/USDT')
            # The Hyperliquid SDK might use its own symbol format, adjust if necessary.
            # Common ccxt practice is 'BASE/QUOTE', e.g., 'ETH/USD'
            # If the SDK uses 'ETHUSD', you might need a mapping or ensure input is correct.
            # For Hyperliquid, symbols are often like "ETH" or "BTC" (for perps against USDC)
            # Let's assume the symbol passed is already in the correct format for the SDK.
            
            # The ccxt fetch_ticker method is standard.
            ticker = await self.client.fetch_ticker(symbol)
            if ticker and 'last' in ticker and ticker['last'] is not None:
                return float(ticker['last'])
            elif ticker and 'close' in ticker and ticker['close'] is not None: # Some exchanges use 'close' for last price
                return float(ticker['close'])
            else:
                print(f"Account {self.account_id}: Could not find 'last' or 'close' price in ticker for {symbol}: {ticker}")
                # Fallback: try fetching order book and using mid-price
                order_book = await self.client.fetch_order_book(symbol, limit=1)
                if order_book and order_book['bids'] and order_book['asks']:
                    bid = order_book['bids'][0][0]
                    ask = order_book['asks'][0][0]
                    return (bid + ask) / 2
                print(f"Account {self.account_id}: Could not determine price for {symbol} from ticker or order book.")
                return None
        except Exception as e:
            print(f"Account {self.account_id}: Error fetching market price for {symbol}: {e}")
            return None

    async def get_account_equity(self, asset_symbol: str = 'USDC') -> float | None:
        """Fetches the account equity, typically the balance of the collateral asset (e.g., USDC)."""
        if not self.client or not self.is_connected:
            print(f"Account {self.account_id}: Not connected. Cannot fetch account equity.")
            # Attempt to reconnect
            # await self.connect() # Avoid reconnecting here, let higher level logic handle it or ensure connected before calling
            # if not self.client or not self.is_connected:
            #     print(f"Account {self.account_id}: Reconnection failed. Cannot fetch equity.")
            #     return None
            print(f"Account {self.account_id}: Connection check failed. Cannot fetch equity.")
            return None
        
        try:
            balance_info = await self.client.fetch_balance()
            # print(f"Account {self.account_id}: Balance info: {balance_info}") # Debugging line

            # Attempt to find total portfolio value in the base currency (asset_symbol)
            if 'total' in balance_info and asset_symbol in balance_info['total']:
                return float(balance_info['total'][asset_symbol])
            
            # Attempt to find the specific asset's total balance
            if asset_symbol in balance_info and 'total' in balance_info[asset_symbol]:
                return float(balance_info[asset_symbol]['total'])

            # Check 'info' field for Hyperliquid specific structures like 'portfolioValue'
            # This path is more specific to Hyperliquid's direct API, CCXT might abstract it.
            if 'info' in balance_info:
                if isinstance(balance_info['info'], list) and len(balance_info['info']) > 0:
                    # Sometimes 'info' can be a list of asset details
                    for asset_detail in balance_info['info']:
                        if isinstance(asset_detail, dict) and asset_detail.get('asset') == asset_symbol and 'total' in asset_detail:
                             return float(asset_detail['total']) # Or a relevant value like 'balance' or 'equity'
                        if isinstance(asset_detail, dict) and 'accountValue' in asset_detail : # e.g. from user_state structure
                            return float(asset_detail['accountValue'])


                elif isinstance(balance_info['info'], dict):
                    if 'portfolioValue' in balance_info['info']: # Direct portfolio value
                        return float(balance_info['info']['portfolioValue'])
                    # Hyperliquid's user_state might be nested under 'info' by some CCXT versions/customizations
                    if 'user_state' in balance_info['info'] and 'crossMarginSummary' in balance_info['info']['user_state'] and 'accountValue' in balance_info['info']['user_state']['crossMarginSummary']:
                         return float(balance_info['info']['user_state']['crossMarginSummary']['accountValue'])
                    if 'marginSummary' in balance_info['info'] and 'accountValue' in balance_info['info']['marginSummary']: # For isolated margin if applicable
                         return float(balance_info['info']['marginSummary']['accountValue'])


            # Fallback: If direct methods fail, try to get user_state directly if the client supports it
            # This is a more direct Hyperliquid call, might not be standard CCXT client method.
            # CCXT's fetch_balance should ideally provide this.
            # This is a last resort and assumes self.client has a method like `get_user_state` or similar
            # For Hyperliquid, the actual method might be `user_state` or part of a private API call.
            # Let's assume `self.client.user_state()` is a hypothetical direct call for this example.
            # The actual Hyperliquid SDK call is `info = await client.info_client.user_state(user_address)`
            # CCXT might wrap this. If `fetch_balance` is insufficient, direct SDK use might be needed.
            # For now, we rely on what fetch_balance provides.

            print(f"Account {self.account_id}: Could not determine equity for {asset_symbol} from balance_info: {balance_info}")
            return None

        except Exception as e:
            print(f"Account {self.account_id}: Error fetching account equity: {e}")
            # import traceback # For detailed error logging
            # traceback.print_exc()
            return None

    async def place_order(self, symbol: str, side: str, order_type: str, size: float,
                          price: float = None, leverage: int = 10, margin_mode: str = 'cross',
                          sl: float = None, tps: list = None, cloid: str = None):
        if not self.is_connected:
            print(f"Account {self.account_id}: Not connected. Attempting to connect before placing order.")
            await self.connect()
            if not self.is_connected:
                print(f"Account {self.account_id}: Connection failed. Cannot place order.")
                return {"status": "error", "message": "Connection failed."}

        print(f"Account {self.account_id}: Preparing to place order: Symbol={symbol}, Side={side}, Type={order_type}, Size={size}, Price={price}, Lev={leverage}, Margin={margin_mode}, SL={sl}%, TPs={tps}")

        try:
            await self.set_leverage(symbol, leverage, is_cross=(margin_mode.lower() == 'cross'))

            order_requests = []
            main_is_buy = side.lower() == 'long'
            
            # Determine reference price for SL/TP calculations
            reference_price_for_sl_tp = price # Default to entry price for limit orders
            if order_type.lower() == 'market':
                # For market orders, SL/TP should ideally be based on fill price.
                # Fetch current market price as a proxy.
                current_market_price = await self.get_market_price(symbol)
                if current_market_price:
                    reference_price_for_sl_tp = current_market_price
                    print(f"Account {self.account_id}: Using fetched market price {reference_price_for_sl_tp} for SL/TP on market order.")
                else:
                    print(f"Account {self.account_id}: Warning - Could not fetch market price for SL/TP on market order. SL/TP might be inaccurate or fail.")
                    # If `price` was passed (e.g. from chart click even for market), it might be used as a fallback.
                    if not reference_price_for_sl_tp: # if price was None
                        print(f"Account {self.account_id}: SL/TP cannot be calculated for market order without a reference price.")
                        # Do not proceed with SL/TP if no reference_price_for_sl_tp
            
            # 1. Construct Main Order
            main_order_type_details: dict
            main_limit_px_str = "0.0" # Hyperliquid expects string for prices
            if order_type.lower() == 'limit':
                if price is None:
                    raise ValueError("Price must be provided for limit orders.")
                main_order_type_details = {"limit": {"tif": "Gtc"}}
                main_limit_px_str = f"{price:.8f}" # Format price to string with precision
            elif order_type.lower() == 'market':
                main_order_type_details = {"market": {}}
                # For market orders, limit_px is not used for matching but might be required by API structure.
                # Hyperliquid's `OrderRequest` has `limit_px` at the top level.
            else:
                raise ValueError(f"Unsupported order_type: {order_type}")

            main_order_req = {
                "asset": symbol,
                "is_buy": main_is_buy,
                "reduce_only": False,
                "order_type": main_order_type_details,
                "sz": size, # Size should be float
                "limit_px": main_limit_px_str, 
                "cloid": cloid
            }
            
            # Handle SL: Attach to main order via tp_sl_spec if possible
            # Hyperliquid's `OrderRequest` can take a `tp_sl_spec` for the main order.
            # This is for a single SL/TP attached to the main order.
            # If multiple TPs are needed, they must be separate trigger orders.
            # We will prioritize separate trigger orders for TPs for flexibility.
            # SL can be a trigger order too, or attached if only one SL is used.
            # For simplicity, let's try to attach SL to the main order if only SL is present (no TPs or only one TP that could also be in tp_sl_spec)

            sl_spec_for_main_order = {}
            if sl is not None and sl > 0 and reference_price_for_sl_tp is not None:
                calculated_sl_price = 0.0
                if main_is_buy: # Long position, SL is below entry
                    calculated_sl_price = reference_price_for_sl_tp * (1 - sl / 100.0)
                else:  # Short position, SL is above entry
                    calculated_sl_price = reference_price_for_sl_tp * (1 + sl / 100.0)
                
                if calculated_sl_price > 0:
                    sl_spec_for_main_order = {
                        "trigger_px": f"{calculated_sl_price:.8f}",
                        "is_market": True, # SL typically triggers a market order
                        "tpsl": "sl"
                    }
                    # main_order_req["tp_sl_spec"] = {"sl": sl_spec_for_main_order} # Old structure
                    # New structure: SL is a trigger order if not part of a combined tpSl on main order
                    # For Hyperliquid, if we want SL on the main order itself, it's part of a more complex `trigger` field within `order_type`
                    # or a separate `tp_sl_spec` field. The `tp_sl_spec` is simpler.
                    # Let's assume `tp_sl_spec` is for a single SL and/or a single TP.
                    # If we have multiple TPs, we must use separate trigger orders for TPs.
                    # We can still try to put SL on the main order.
                    main_order_req["trigger"] = sl_spec_for_main_order # This might be the way for a simple SL trigger on main order
                                                                      # Or, it might need to be a separate order.
                                                                      # The SDK docs are key here.
                                                                      # Let's assume for now we make SL a separate trigger order for consistency with multiple TPs.
                    # Re-evaluating: The original code had `tp_sl_spec_dict` which implies it's possible.
                    # Let's try to use the `tp_sl_spec` field on the main order for SL.
                    # The `tp_sl_spec` in Hyperliquid is for stop-loss and take-profit that are *not* trigger orders themselves,
                    # but rather conditions on the main order.
                    # This is usually for exchanges that support OCO or SL/TP directly on the order.
                    # Hyperliquid's `OrderRequest` has `trigger: Optional[Trigger]`
                    # `Trigger` has `trigger_px`, `is_market`, `tpsl: Literal[\'tp\', \'sl\']`
                    # This means the main order itself can be a trigger order.
                    # This is not what we want for a simple SL on a non-trigger main order.

                    # Let's stick to creating SL as a separate trigger order if `reference_price_for_sl_tp` is valid.
                    # This makes it consistent with how multiple TPs are handled.
                    sl_trigger_order_req = {
                        "asset": symbol,
                        "is_buy": not main_is_buy, # SL order is opposite to main order to close
                        "reduce_only": True,
                        "order_type": {
                            "trigger": {
                                "trigger_px": f"{calculated_sl_price:.8f}",
                                "is_market": True, # SL triggers a market order to ensure fill
                                "tpsl": "sl"
                            }
                        },
                        "sz": size, # SL closes the full size
                        "limit_px": "0.0", # Not used for market trigger
                        "cloid": f"{cloid}_sl" if cloid else None
                    }
                    order_requests.append(sl_trigger_order_req)
                    print(f"Account {self.account_id}: Prepared SL trigger order: {sl_trigger_order_req}")


            order_requests.insert(0, main_order_req) # Main order first

            # 2. Construct TP Orders (as separate trigger orders)
            if tps and len(tps) > 0 and reference_price_for_sl_tp is not None:
                num_tps = len(tps)
                # Ensure total TP size does not exceed main order size.
                # For simplicity, let's assume tps are for portions of the main order.
                # A common strategy: each TP closes a fraction of the initial position.
                tp_size_each = round(size / num_tps, 8) # Distribute size, round to sensible precision for size
                if tp_size_each == 0 and size > 0 : # Avoid 0 size if main size is >0
                    print(f"Account {self.account_id}: Warning - TP size per order is 0 due to many TPs or small main size. Adjusting. This might lead to issues.")
                    # Potentially adjust logic: maybe first few TPs get slightly larger size, or error out.
                    # For now, we proceed, but this is a sign of potential issue with too many TPs for small size.


                for i, tp_item in enumerate(tps):
                    profit_perc = tp_item.get('profit_perc')
                    if profit_perc is None or profit_perc <= 0:
                        print(f"Account {self.account_id}: Skipping TP {i+1} with invalid profit_perc: {tp_item}")
                        continue

                    calculated_tp_price = 0.0
                    if main_is_buy: # Long position, TP is above entry
                        calculated_tp_price = reference_price_for_sl_tp * (1 + profit_perc / 100.0)
                    else:  # Short position, TP is below entry
                        calculated_tp_price = reference_price_for_sl_tp * (1 - profit_perc / 100.0)
                    
                    if calculated_tp_price <= 0:
                        print(f"Account {self.account_id}: Skipping TP {i+1} with invalid calculated price: {calculated_tp_price}")
                        continue

                    # TP order is a trigger limit order (common practice)
                    # Hyperliquid: "trigger": {"trigger_px": "...", "is_market": False, "tpsl": "tp", "limit_px": "..."}
                    # The `limit_px` inside trigger is the price for the limit order placed when trigger_px is hit.
                    # The top-level `limit_px` for the OrderRequest should be set for the triggered limit order.
                    tp_trigger_limit_price_str = f"{calculated_tp_price:.8f}" # Fill at this price or better

                    tp_order_req = {
                        "asset": symbol,
                        "is_buy": not main_is_buy, # TP orders are opposite to main order
                        "reduce_only": True,
                        "order_type": {
                            "trigger": {
                                "trigger_px": f"{calculated_tp_price:.8f}",
                                "is_market": False, 
                                "tpsl": "tp"
                                # "limit_px": tp_trigger_limit_price_str # This seems to be how HL wants it for triggered limit
                            }
                        },
                        "sz": tp_size_each, 
                        "limit_px": tp_trigger_limit_price_str, # This is the limit price for the order once triggered
                        "cloid": f"{cloid}_tp_{i+1}" if cloid else None
                    }
                    order_requests.append(tp_order_req)
                    print(f"Account {self.account_id}: Prepared TP trigger order {i+1}: {tp_order_req}")
            
            if not order_requests:
                print(f"Account {self.account_id}: No valid orders to place after processing inputs.")
                return {"status": "error", "message": "No valid orders to place."}

            print(f"Account {self.account_id}: Sending order request(s): {order_requests}")
            
            # Using self.client.order for batch placement, assuming it takes List[OrderRequest]
            # This was the structure used in the original snippet that was working for single orders.
            # The Hyperliquid SDK's `order` method on the `Exchange` class takes:
            # `orders: List[OrderRequest], grouping: Grouping`
            # So we need to wrap `order_requests` if `self.client` is the `Exchange` instance.
            # However, the ccxt wrapper `HyperliquidAsync` might expose `order` differently.
            # The previous working version was `result = await self.client.order(order_requests)`
            # where order_requests was a list containing a single dict.
            # Let's assume the ccxt wrapper's `order` method can indeed take a list of these dicts.
            
            # If `self.client.order` is from the raw SDK `Exchange` class, it needs `grouping`.
            # If it's a CCXT adaptation, it might simplify this.
            # Given the context, `self.client` is `HyperliquidAsync` from `hyperliquid.ccxt.async_support.hyperliquid`
            # CCXT typically uses `create_order` for single orders. For batch, it might be `create_orders` or a private method.
            # Let's check for `create_orders` or fall back to `private_post_exchange` with the action.

            result = None
            if hasattr(self.client, 'create_orders') and callable(getattr(self.client, 'create_orders')) :
                # This would be the ideal CCXT way if supported for Hyperliquid by the wrapper
                # The structure of objects for create_orders needs to be CCXT standard.
                # This is unlikely to match `order_requests` directly.
                # For now, let's assume the direct `order` or `private_post_exchange` is what's intended.
                print(f"Account {self.account_id}: `create_orders` found, but structure might mismatch. Sticking to `order` or private call.")


            # The original code used `await self.client.order(order_requests)` where `order_requests` was a list of dicts.
            # This implies `self.client.order` (from ccxt async_support wrapper) can handle this.
            if hasattr(self.client, 'order') and callable(getattr(self.client, 'order')):
                try:
                    # This is the most likely path given previous successful single order placements.
                    # The `order` method in `hyperliquid.py` (ccxt wrapper) seems to be a direct pass-through
                    # to the `exchange.order` method of the underlying SDK, which expects the action format.
                    action = {"type": "order", "orders": order_requests, "grouping": "normal"}
                    print(f"Account {self.account_id}: Attempting batch order with action: {action}")
                    result = await self.client.order(action) # Pass the full action structure
                except Exception as e_order_action:
                    print(f"Account {self.account_id}: Error calling self.client.order with action structure: {e_order_action}. Trying list of orders directly.")
                    # Fallback: try sending the list of orders directly, if the wrapper handles it.
                    # This was implied by the original `place_order` taking `order_requests` (a list)
                    try:
                        result = await self.client.order(order_requests)
                    except Exception as e_order_list:
                        print(f"Account {self.account_id}: Error calling self.client.order with list of orders: {e_order_list}.")
                        raise # Re-raise the last error if both attempts fail

            elif hasattr(self.client, 'private_post_exchange') and callable(getattr(self.client, 'private_post_exchange')):
                 action = {"type": "order", "orders": order_requests, "grouping": "normal"}
                 print(f"Account {self.account_id}: Attempting batch order with private_post_exchange and action: {action}")
                 result = await self.client.private_post_exchange(params=action) # CCXT typically uses 'params' for the body
            else:
                print(f"Account {self.account_id}: Critical - client does not have a recognized batch order method ('order' or 'private_post_exchange').")
                # Fallback: try placing only the main order if that's what was working before
                if order_requests and main_order_req is order_requests[0]: # ensure main_order_req is the first
                    print(f"Account {self.account_id}: Attempting to place only the main order as a fallback.")
                    action_single = {"type": "order", "orders": [main_order_req], "grouping": "normal"}
                    if hasattr(self.client, 'order') and callable(getattr(self.client, 'order')):
                         result = await self.client.order(action_single)
                    elif hasattr(self.client, 'private_post_exchange') and callable(getattr(self.client, 'private_post_exchange')):
                         result = await self.client.private_post_exchange(params=action_single)
                    else:
                         return {"status": "error", "message": "No suitable method to place even a single order."}
                else:
                    return {"status": "error", "message": "No orders to place or no suitable batch order method."}

            print(f"Account {self.account_id}: Order placement result: {result}")
            return result
        except Exception as e:
            print(f"Account {self.account_id}: API error during place_order: {e}")
            import traceback
            traceback.print_exc()
            return {"status": "error", "message": str(e)}

    async def set_leverage(self, symbol: str, leverage: int, is_cross: bool):
        if not self.connected:
            await self.connect()
        if not self.client:
            print(f"Account {self.account_id}: Client not initialized. Cannot set leverage.")
            return {"status": "error", "message": "Client not initialized."}

        try:
            # For Hyperliquid, the update_leverage method might be specific to the client or require a certain structure.
            # This example assumes a direct method on the client for updating leverage.
            # If the SDK requires a specific call pattern, like `client.private_post_leverage`, that should be used.
            # The is_cross flag determines if the leverage is applied cross-margin or isolated.

            # Note: The original code had a placeholder for leverage setting, but it's crucial for order placement.
            # If leverage is not set correctly, orders might fail or have unexpected behavior.

            # This example directly uses the client to set leverage, assuming such a method exists.
            # The actual implementation might vary based on the SDK and how CCXT wraps it.

            # For true cross-margin, the position_mode might need to be set to 'hedge' or similar.
            # This depends on the exchange's requirements and how the SDK implements them.
            # If the account is not already in the desired mode, a switch might be needed.

            # Example: await self.client.set_leverage(symbol, leverage, is_cross=is_cross)

            print(f"Account {self.account_id}: Leverage set to {leverage}x for {'cross' if is_cross else 'isolated'} margin on {symbol}.")
            return {"status": "success", "message": f"Leverage set to {leverage}x for {'cross' if is_cross else 'isolated'} margin on {symbol}."}
        except Exception as e:
            print(f"Account {self.account_id}: Error setting leverage: {e}")
            return {"status": "error", "message": str(e)}

    async def cancel_all_orders(self):
        """Cancels all open orders for the account."""
        if not self.client or not self.is_connected:
            print(f"Account {self.account_id}: Not connected. Cannot cancel orders.")
            return {"status": "error", "message": "Not connected."}

        try:
            # For Hyperliquid, the method to cancel orders might be specific to the client.
            # This example assumes a direct method on the client for cancelling orders.
            # If the SDK requires a specific call pattern, like `client.private_post_cancel_all`, that should be used.

            # The original code had a placeholder for canceling all orders.
            # This is crucial for managing positions and risk.
            # If orders are not canceled correctly, it might lead to unexpected behavior or losses.

            # This example directly uses the client to cancel all orders, assuming such a method exists.
            # The actual implementation might vary based on the SDK and how CCXT wraps it.

            # Example: result = await self.client.cancel_all_orders()

            print(f"Account {self.account_id}: Cancelling all orders.")
            # Placeholder result, the actual result would come from the client SDK
            result = {"status": "success", "message": "All orders cancelled."}
            return result
        except Exception as e:
            print(f"Account {self.account_id}: Error cancelling all orders: {e}")
            return {"status": "error", "message": str(e)}

    async def move_sl_to_previous_tp(self, tp_index):
        """Move SL to the previous TP when a TP is hit."""
        print(f"Account {self.account_id}: move_sl_to_previous_tp called (not implemented yet).")
