# Sorting aur searching khud likhi hui (from scratch). Teeno sorts O(n^2) hain, binary search O(log n).


def bubble_sort(items, key=lambda x: x):
    data = list(items)
    n = len(data)
    for i in range(n):
        swapped = False
        for j in range(n - i - 1):
            if key(data[j]) > key(data[j + 1]):
                data[j], data[j + 1] = data[j + 1], data[j]
                swapped = True
        if not swapped:
            break
    return data


def selection_sort(items, key=lambda x: x):
    data = list(items)
    for i in range(len(data)):
        smallest = i
        for j in range(i + 1, len(data)):
            if key(data[j]) < key(data[smallest]):
                smallest = j
        data[i], data[smallest] = data[smallest], data[i]
    return data


def insertion_sort(items, key=lambda x: x):
    data = list(items)
    for i in range(1, len(data)):
        current = data[i]
        j = i - 1
        while j >= 0 and key(data[j]) > key(current):
            data[j + 1] = data[j]
            j -= 1
        data[j + 1] = current
    return data


def binary_search(sorted_items, target, key=lambda x: x):
    """target ka index dega, na mile to -1. List key ke hisaab se sorted honi chahiye."""
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
