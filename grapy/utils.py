def safe_get(dct, keys):
    _dct = dct
    for key in keys:
        try:
            _dct = _dct[key]
        except KeyError:
            return None
    return _dct


def num_remaining(total, batch_size):
    return max(0, total - batch_size)


def num_updated(total, batch_size):
    return min(batch_size, total)
