def safe_get(dct, keys):
    _dct = dct
    for key in keys:
        try:
            _dct = _dct[key]
        except KeyError:
            return None
    return _dct
