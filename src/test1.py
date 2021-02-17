"""This is the "example" module.
The example module supplies one function, factorial().  For example,
>>> factorial(5)


120
"""
def function_foo(x, y, z):
    """function foo ...

    Args:
        x (int): bla x
        y (float): bla y

        z (int): bla z

    Returns:
        float: sum
    """
    return x + y + z

def factorial(n_n, m_m):
    """Return the factorial of n, an exact integer >= 0.
    Parameters
    ----------
    m_m : array_like
        Array_like means all those objects -- lists, nested lists, etc. --
        that can be converted to an array.  We can also refer to
        variables like `var1`.
    n_n : array_like
        Array_like means all those objects -- lists, nested lists, etc. --
        that can be converted to an array.  We can also refer to
        variables like `var1`.


    >>> [factorial(n) for n in range(6)]
    [1, 1, 2, 6, 24, 120]
    >>> factorial(30)
    265252859812191058636308480000000
    >>> factorial(-1)
    Traceback (most recent call last):
        ...
    ValueError: n must be >= 0

    Factorials of floats are OK, but the float must be an exact integer:
    >>> factorial(30.1)
    Traceback (most recent call last):
        ...
    ValueError: n must be exact integer
    >>> factorial(30.0)
    265252859812191058636308480000000

    It must also not be ridiculously large:
    >>> factorial(1e100)
    Traceback (most recent call last):
        ...
    OverflowError: n too large
    """

    import math
    n = n_n
    m = m_m
#     Sample inline comment TEST1
    if not n >= 0:
        raise ValueError("n must be >= 0")
    if math.floor(n) != n:
        raise ValueError("n must be exact integer")
    if n+1 == n:  # catch a value like 1e300
        raise OverflowError("n too large")
    result = 1
    factor = 2
    while factor <= n:
        result *= factor
        factor += 1
    return result


if __name__ == "__main__":
    #     Sample inline comment TEST1
    print(factorial(100,101)) #     Sample inline comment TEST1
