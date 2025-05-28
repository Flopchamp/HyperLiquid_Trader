import pytest
from core.copy_trading import CopyTradingManager
from core.trader import TraderAccount
from utils.validators import validate_splits, validate_tp_values, validate_sl_value
from utils.config_loader import load_api_keys

class DummyAccount:
    def __init__(self):
        self.orders = []
    async def place_order(self, **kwargs):
        self.orders.append(kwargs)
        return 'ok'

def test_validate_splits():
    assert validate_splits('limit', 100)
    assert not validate_splits('limit', 101)
    assert validate_splits('market', 30)
    assert not validate_splits('market', 31)

def test_validate_tp_values():
    assert validate_tp_values([1, 2, 3])
    assert not validate_tp_values([3, 2, 1])
    assert not validate_tp_values([1, 1, 2])
    assert not validate_tp_values([-1, 2, 3])

def test_validate_sl_value():
    assert validate_sl_value(1)
    assert not validate_sl_value(0)
    assert not validate_sl_value(-5)

def test_load_api_keys():
    # Should not raise, even if no keys are present
    keys = load_api_keys()
    assert isinstance(keys, list)

def test_trader_account_position_size():
    trader = TraderAccount('key', 'secret', 1)
    size = trader.calculate_position_size(1000, 2, 1)
    assert abs(size - 2000) < 1e-6

def test_copy_trading_manager_mirrors_orders():
    master = DummyAccount()
    subs = [DummyAccount(), DummyAccount()]
    manager = CopyTradingManager(master, subs)
    order_data = {'symbol': 'BTCUSDT', 'side': 'buy', 'order_type': 'market', 'size': 1, 'price': None, 'sl': 100, 'tps': [110, 120]}
    manager.mirror_order(order_data)
    import time; time.sleep(0.1)  # Allow async tasks to run
    for sub in subs:
        assert sub.orders and sub.orders[0]['symbol'] == 'BTCUSDT'

def test_trader_account_error_handling(monkeypatch):
    trader = TraderAccount('key', 'secret', 1)
    async def fail_create_order(**kwargs):
        raise Exception('fail')
    trader.client = type('C', (), {'create_order': fail_create_order})()
    trader.connected = True
    import asyncio
    result = asyncio.run(trader.place_order('BTCUSDT', 'buy', 'market', 1))
    assert 'API error' in result
