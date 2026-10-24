"""Chhota helper module: multiprocessing wali functions yahan rakhi hain.

Multiprocessing mein function pickle hota hai, isliye notebook ke andar likhne ke bajaye
alag .py file mein rakha taake har operating system par chale.
"""


def heavy_sum(n):
    """CPU wala kaam: 1 se n tak ke squares ka jama."""
    total = 0
    for i in range(1, n + 1):
        total += i * i
    return total
