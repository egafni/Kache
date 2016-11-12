import functools
import shelve
import funcsigs


def get_params(func, args, kwargs):
    """
    Given a func, it's args, and its kwargs return a dictionary of all of its parameters, including defaults that were not set.

    >>> get_params(lambda x, y, z=1: x+y, [1], {'y':2})
    {'x': 1, 'y': 2, 'z': 1}
    """
    sig = funcsigs.signature(func)

    def g():
        for i, (hash, param) in enumerate(sig.parameters.iteritems()):
            if i < len(args):
                yield hash, args[i]
            else:
                val = kwargs.get(hash, param.default)
                if val == funcsigs._empty:
                    raise AttributeError('`%s` requires the parameter `%s`' % (func, hash))
                yield hash, val

    return dict(g())


def cache(orig_func=None, db=None, hash=lambda params: str(sorted(params.iteritems()))):
    """
    Decorate a function so that identical calls are cached
    :param callable orig_func: function to decorate
    :param str db: if None, uses an in memory dict.  Otherwise, uses a path to a :mod:`shelve` database.
    :param callable hash: a callable that takes the parameters of the decorated function and returns a hash.

    :rtype: callable

    >>> from kache import cache
    ...
    ... @cache
    ... def x(a,b=2):
    ...     return a*b
    ...
    ... print x(1), x._stats, x._info
    ... print x(1), x._stats, x._info
    ... print x(2), x._stats, x._info
    ... print x(3), x._stats, x._info
    ... print x(3), x._stats, x._info
    ...
    2 {'computed': 1} {'last_hash': "[('a', 1), ('b', 2)]"}
    2 {'cached': 1, 'computed': 1} {'last_hash': "[('a', 1), ('b', 2)]"}
    4 {'cached': 1, 'computed': 2} {'last_hash': "[('a', 2), ('b', 2)]"}
    6 {'cached': 1, 'computed': 3} {'last_hash': "[('a', 3), ('b', 2)]"}
    6 {'cached': 2, 'computed': 3} {'last_hash': "[('a', 3), ('b', 2)]"}
    """
    if hash is None:
        hash = lambda params: ''

    if orig_func is None:
        # `orig_func` was called with optional arguments
        # Return this decorator which has no optional arguments
        return functools.partial(cache, db=db, hash=hash)

    stats = dict(cached=0, computed=0)
    info = dict()
    mem_cache = dict()

    @functools.wraps(orig_func)
    def decorated(*args, **kwargs):
        params = get_params(orig_func, args, kwargs)

        hash_ = orig_func.__name__ + '__' + hash(params)
        info['last_hash'] = hash_

        cache = shelve.open(db) if db is not None else mem_cache
        try:
            if hash_ in cache:
                stats['cached'] += 1
            else:
                stats['computed'] += 1
                cache[hash_] = orig_func(**params)

            r = cache[hash_]
        finally:
            if hasattr(cache, 'close'):
                cache.close()
        return r

    decorated._stats = stats
    decorated._info = info
    return decorated
