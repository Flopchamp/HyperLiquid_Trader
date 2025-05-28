import random
from typing import List, Tuple

def generate_splits(entry_price: float, range_percent: float, split_count: int, total_size: float, order_type: str = 'limit') -> List[Tuple[float, float]]:
    """
    Generate split orders within a range around the entry price.
    Returns a list of (price, size) tuples.
    For 'limit': randomize price and size within range.
    For 'market': sequential splits at entry price.
    """
    splits = []
    if split_count < 1:
        return splits
    if order_type == 'market':
        split_size = total_size / split_count
        for _ in range(split_count):
            splits.append((entry_price, split_size))
    else:  # limit
        min_price = entry_price * (1 - range_percent / 100)
        max_price = entry_price * (1 + range_percent / 100)
        remaining = total_size
        for i in range(split_count):
            # Random price within range
            price = random.uniform(min_price, max_price)
            # Random size, but ensure total adds up
            if i == split_count - 1:
                size = remaining
            else:
                max_split = remaining - (split_count - i - 1) * (total_size / split_count) * 0.5
                size = random.uniform(total_size / split_count * 0.5, max_split)
                size = min(size, remaining)
            splits.append((price, size))
            remaining -= size
    return splits
