# -*- coding: utf-8 -*-


def int_or_none(value):
    res = None
    try:
        res = int(float(value))
    except TypeError:
        pass
    except ValueError:
        pass
    return res


def float_or_none(value):
    res = None
    try:
        res = float(value)
    except TypeError:
        pass
    except ValueError:
        pass
    return res
