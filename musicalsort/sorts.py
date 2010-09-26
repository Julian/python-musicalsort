from musicalsort import musical, MusicalSortable

@musical
def bubble_sort(sortable):
    for i in range(len(sortable)):
        for j in range(len(sortable) - 1, i, -1):
            if sortable[j-1] > sortable[j]:
                sortable[j-1], sortable[j] = sortable[j], sortable[j-1]

@musical
def insertion_sort(sortable):
    for i in range(1, len(sortable)):
        key = sortable[i]
        j = i - 1
        while (j >= 0) and (sortable[j] > key):
            sortable[j + 1] = sortable[j]
            j -= 1
        sortable[j + 1] = key

def _merge(left, right):
    merged = MusicalSortable()
    while left and right:
        if left[0] < right[0]:
            merged.append(left.pop(0))
        else:
            merged.append(right.pop(0))
    # one of them is empty, so just extend till they both are
    merged.extend(left)
    merged.extend(right)
    return merged

@musical
def merge_sort(sortable):
    if len(sortable) < 2:
        return sortable
    middle = len(sortable) // 2
    left, right = merge_sort(sortable[:middle]), merge_sort(sortable[middle:])
    return _merge(left, right)

def _partition(sortable, pivot=None):
    raise NotImplementedError("Doesn't work yet!")
    if not pivot:
        pivot = len(sortable) // 2
    if sortable[0] > sortable[pivot]:
        sortable[0], sortable[pivot] = sortable[pivot], sortable[first]
    if sortable[0] > sortable[-1]:
        sortable[0], sortable[-1] = sortable[-1], sortable[0]
    if sortable[pivot] > sortable[-1]:
        sortable[pivot], sortable[-1] = sortable[-1], sortable[pivot]
    sortable[pivot], sortable[0] = sortable[0], sortable[pivot]

    while True:
        break

@musical
def quick_sort(sortable):
    pivot = _partition(sortable)
    quick_sort(sortable[:pivot])
    quick_sort(sortable[pivot + 1:])

@musical
def selection_sort(sortable):
    for i in range(len(sortable)):
        minimum = i
        for j in range(i+1, len(sortable)):
            if sortable[j] < sortable[minimum]:
                minimum = j
        sortable[i], sortable[minimum] = sortable[minimum], sortable[i]

@musical
def shell_sort(sortable):
    gap = len(sortable) // 2
    while gap:
        for i in range(gap, len(sortable)):
            value = sortable[i]
            j = i
            while j >= gap and sortable[j-gap] > value:
                sortable[j] = sortable[j-gap]
                j -= gap
            sortable[j] = value
        gap //= 2
