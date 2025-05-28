import pytest
from core.order_splitter import generate_splits

def test_generate_splits_limit():
    entry = 100.0
    range_percent = 1.0
    split_count = 5
    total_size = 10.0
    splits = generate_splits(entry, range_percent, split_count, total_size, order_type='limit')
    assert len(splits) == split_count
    assert abs(sum(size for _, size in splits) - total_size) < 1e-6
    for price, size in splits:
        assert entry * 0.99 <= price <= entry * 1.01
        assert size > 0

def test_generate_splits_market():
    entry = 100.0
    split_count = 3
    total_size = 6.0
    splits = generate_splits(entry, 0, split_count, total_size, order_type='market')
    assert len(splits) == split_count
    assert all(price == entry for price, _ in splits)
    assert abs(sum(size for _, size in splits) - total_size) < 1e-6
