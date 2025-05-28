def validate_splits(order_type: str, split_count: int) -> bool:
    """
    Validate split count based on order type.
    Limit: up to 100 splits, Market: up to 30 splits.
    """
    if order_type == 'limit' and split_count > 100:
        return False
    if order_type == 'market' and split_count > 30:
        return False
    return True

def validate_tp_values(tp_values):
    """
    Ensure TP values are positive and in ascending order.
    """
    last = 0
    for tp in tp_values:
        if tp <= 0 or tp <= last:
            return False
        last = tp
    return True

def validate_sl_value(sl_value):
    """
    Ensure SL value is positive.
    """
    return sl_value > 0
