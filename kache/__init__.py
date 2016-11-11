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
        for i, (key, param) in enumerate(sig.parameters.iteritems()):
            if i < len(args):
                yield key, args[i]
            else:
                val = kwargs.get(key, param.default)
                if val == funcsigs._empty:
                    raise AttributeError('`%s` requires the parameter `%s`' % (func, key))
                yield key, val

    return dict(g())


def cache(orig_func=None, db_path=None, key=lambda params: str(sorted(params.iteritems()))):
    """
    Decorate a function so that identical calls are cached
    :param callable orig_func: function to decorate
    :param str db_path: if None, uses an in memory dict.  Otherwise, uses a path to a :mod:`shelve` database.
    :param callable key: a callable that takes the parameters of the decorated function and returns a key.
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
    2 {'computed': 1} {'last_key': "[('a', 1), ('b', 2)]"}
    2 {'cached': 1, 'computed': 1} {'last_key': "[('a', 1), ('b', 2)]"}
    4 {'cached': 1, 'computed': 2} {'last_key': "[('a', 2), ('b', 2)]"}
    6 {'cached': 1, 'computed': 3} {'last_key': "[('a', 3), ('b', 2)]"}
    6 {'cached': 2, 'computed': 3} {'last_key': "[('a', 3), ('b', 2)]"}
    """
    if orig_func is None:
        # `orig_func` was called with optional arguments
        # Return this decorator which has no optional arguments
        return functools.partial(cache, db_path=db_path, key=key)

    stats = dict(cached=0, computed=0)
    info = dict()
    mem_cache = dict()

    @functools.wraps(orig_func)
    def decorated(*args, **kwargs):
        params = get_params(orig_func, args, kwargs)

        key_ = key(params)
        info['last_key'] = key_

        cache = shelve.open(db_path) if db_path is not None else mem_cache
        try:
            if key_ in cache:
                stats['cached'] += 1
            else:
                stats['computed'] += 1
                cache[key_] = orig_func(**params)

            r = cache[key_]
        finally:
            if hasattr(cache, 'close'):
                cache.close()
        return r

    decorated._stats = stats
    decorated._info = info
    return decorated
