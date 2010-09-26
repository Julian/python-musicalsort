from __future__ import division
from functools import wraps
from random import shuffle

import platform
import collections

DEFAULT_DURATION = .05    # in seconds
BASE_FREQUENCY = 200      # A = 440 hz
MAXIMUM_FREQUENCY = 2000

class NoAudioLibraryFound(Exception):
    def __str__(self):
        if platform.system() == "Windows":
            return "winsound module not found. Check your python distribution!"
        else:
            return "No audio library found. pyAudiere is recommended."""

# Set up tone producing (First try winsound -> pyAudiere -> tkSnack)
try:
    # windows
    import winsound
except ImportError:
    try:
        import audiere
    except ImportError:
        try:
            import Tkinter
            import tkSnack
        except ImportError:
            raise NoAudioLibraryFound()
        else:
            root = Tkinter.Tk()
            tkSnack.initializeSnack(root)

            def _play_sound(frequency, duration):
                sound = tkSnack.Sound()
                filter = tkSnack.Filter('generator', frequency, 30000, 0.0,
                                         'sine', int(11500 * duration))
                sound.stop()
                sound.play(filter=filter, blocking=1)
    else:
        import time
        dev = audiere.open_device()

        def _play_sound(frequency, duration):
            tone = dev.create_tone(frequency)
            tone.pan = 0
            try:
                tone.play()
                time.sleep(duration)
                # TODO: there has to be a way to spec duration without sleep()
                tone.stop()
            except KeyboardInterrupt:
                tone.stop()
                raise KeyboardInterrupt
else:
    def _play_sound(frequency, duration):
        winsound.Beep(frequency, int(duration * 1000))

def play_sound(frequency, duration=DEFAULT_DURATION):
    return _play_sound(int(frequency), duration)

def play_note(interval, duration=DEFAULT_DURATION):
    """
    Plays the note at `interval` steps away from the base frequency (usually
    A=440hz).

    Assumes (uses) equal temperament.
    """
    frequency = BASE_FREQUENCY * (2 ** (1/12)) ** interval
    return play_sound(frequency, duration)

def scaled_play(length, min_freq=BASE_FREQUENCY, max_freq=MAXIMUM_FREQUENCY):
    """
    Plays a note not by a standard interval but by dividing up the length of
    the sortable within the interval (e.g. a list of length 20 will divide the
    interval from BASE_FREQUENCY to MAXIMUM_FREQUENCY into 20 intervals).
    """
    try:
        interval_length = (max_freq - min_freq) // length
    except ZeroDivisionError:
        interval_length = max_freq - min_freq
    def play_note(interval, duration=DEFAULT_DURATION):
        frequency = min_freq + interval * interval_length
        return play_sound(frequency, duration)
    return play_note

class MusicalSortable(collections.MutableSequence):
    def __init__(self, *args):
        self.list = []
        self.extend(list(*args))

    def __len__(self):
        return len(self.list)

    def __getitem__(self, i):
        return self.list[i]

    def __delitem__(self, i):
        del self.list[i]

    def __setitem__(self, index, new_value):
        self.pre_assignment(index, new_value)
        self.list[index] = new_value
        self.post_assignment(index, new_value)

    def __repr__(self):
        return repr(self.list)

    def __str__(self):
        return str(self.list)

    def insert(self, index, value):
        self.pre_insertion(index, value)
        self.list.insert(index, value)
        self.post_insertion(index, value)

    def pre_insertion(self, index, value):
        self.scaled_play(index)
        self.scaled_play(value)

    def post_insertion(self, index, value):
        pass

    def pre_assignment(self, index, value):
        self.scaled_play(index)
        self.scaled_play(value)
        # play_note(index)
        # play_note(value)

    def post_assignment(self, index, value):
        pass

    def scaled_play(self, *args, **kwargs):
        return scaled_play(len(self))(*args, **kwargs)

def musical(sort_fn):
    """
    Does automatic musical sorting for any sort that takes a sortable as its
    first parameter.

    For any other sort, you will need to manually create a MusicalSortable class
    object from your sortable object.
    """
    @wraps(sort_fn)
    def musical_sorter(sortable, *args, **kwargs):
        s = MusicalSortable(sortable)
        sorted = sort_fn(s, *args, **kwargs)
        if sorted:
            # not an in place sort?
            return sorted
        return s
    return musical_sorter

### Sample Sorts

@musical
def selection_sort(sortable):
    for i in range(len(sortable)):
        minimum = i
        for j in range(i+1, len(sortable)):
            if sortable[j] < sortable[minimum]:
                minimum = j
        sortable[i], sortable[minimum] = sortable[minimum], sortable[i]

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

def quick_sort(sortable):
    pivot = _partition(sortable)
    quick_sort(sortable[:pivot])
    quick_sort(sortable[pivot + 1:])
