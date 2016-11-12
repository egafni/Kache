Kache
======

A simple decorator that both supports caching calls to functions in memory and persisting the cache to disk.

.. code-block:: python

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


The following will persist the cache to a shelf stored at **/tmp/db**.  It will behave identically as above, but persist across interpreter sessions.

.. code-block:: python

    @cache(db='/tmp/db', hash=lambda params: params['b'])
    def x(a,b=2):
        return a*b

The following will **only** use the value of **b** to as they hash key in the cache.
So a call to x(a=1,b=3) after calling x(a=0,b=3) will return the same (but incorrect) result.

The default hashing function for the cache key is sorted(str(**params**.items())), which can break down for complex parameters.  In these instances,
you'll want to create your own hashing function.


.. code-block:: python

    @cache(db='/tmp/db', hash=lambda params: params['b'])
    def x(a,b=2):
        return a*b

    # or, if you know it will only be executed once in this session...
    @cache(db='/tmp/db', hash=None)
    def x(a,b=2):
        return a*b
