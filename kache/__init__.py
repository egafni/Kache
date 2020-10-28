import functools
import shelve

import inspect


def cache(orig_func=None, db=None, hash=lambda params: str(sorted(params.items()))):
    """
    Decorate a function so that identical calls are cached
    :param callable orig_func: function to decorate
    :param str db: if None, uses an in memory dict.  Otherwise, uses a path to a :mod:`shelve` database.
    :param callable hash: a callable that takes the parameters of the decorated function and returns a hash.

    :rtype: callable


    >>> x = lambda a,b=2: a*b
    >>> x = cache(x)
    >>> x(1)
    2
    >>> print(x._info, x._stats)
    {'last_hash': "<lambda>__[('a', 1), ('b', 2)]"} {'cached': 0, 'computed': 1}
    >>> x(2)
    4
    >>> print(x._info, x._stats)
    {'last_hash': "<lambda>__[('a', 2), ('b', 2)]"} {'cached': 0, 'computed': 2}
    >>> x(1)
    2
    >>> print(x._info, x._stats)
    {'last_hash': "<lambda>__[('a', 1), ('b', 2)]"} {'cached': 1, 'computed': 2}
    """
    if hash is None:
        hash = lambda params: ""

    if orig_func is None:
        # `orig_func` was called with optional arguments
        # Return this decorator which has no optional arguments
        return functools.partial(cache, db=db, hash=hash)

    stats = dict(cached=0, computed=0)
    info = dict()
    mem_cache = dict()

    @functools.wraps(orig_func)
    def decorated(*args, **kwargs):
        sig = inspect.signature(orig_func)
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
        params = dict(bound.arguments)

        hash_ = orig_func.__name__ + "__" + hash(params)
        info["last_hash"] = hash_

        _cache = shelve.open(db) if db is not None else mem_cache
        try:
            if hash_ in _cache:
                stats["cached"] += 1
            else:
                stats["computed"] += 1
                _cache[hash_] = orig_func(**params)

            r = _cache[hash_]
        finally:
            if hasattr(_cache, "close"):
                _cache.close()
        return r

    decorated._stats = stats
    decorated._info = info
    decorated._mem_cache = mem_cache
    return decorated
