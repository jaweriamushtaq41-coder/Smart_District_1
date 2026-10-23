"""Algorithms from scratch (Day 4): binary search."""


def binary_search(sorted_items, target, key=lambda x: x):
    """Return index of target in a list sorted by `key`, or -1. O(log n)."""
    low, high = 0, len(sorted_items) - 1
    while low <= high:
        mid = (low + high) // 2
        value = key(sorted_items[mid])
        if value == target:
            return mid
        if value < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1
