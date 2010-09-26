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
            """
            Just a bit more complicated. We need to make sure our tone has
            stopped playing if execution is interrupted.
            """
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
        """
        winsound seems the easiest of the bunch to do simple tone outputting,
        but its duration expects time in milliseconds, so we take that into
        account.
        """
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
    # TODO: get rid of the closure, or provide an alternative
    try:
        interval_length = (max_freq - min_freq) // length
    except ZeroDivisionError:
        interval_length = max_freq - min_freq
    def play_note(interval, duration=DEFAULT_DURATION):
        frequency = min_freq + interval * interval_length
        return play_sound(frequency, duration)
    return play_note

class MusicalSortable(collections.MutableSequence):
    """
    Where the magic happens.

    All this class does is basically just wraps insertion and assignment with
    arbitrary method calls before and after.

    You can do whatever you'd like. Just redefine `pre_assignment` and
    `post_assignment` to affect assigns, and `pre_insertion` and
    `post_insertion` for inserts (and everything else that is implemented via
    each. See _abcoll.py). If for any reason you need to bypass your method,
    you can access the internal list via `self.data` on your instance (à la
    `collections`).

    The only other out-of-the-box method that you get at the moment is
    scaled_play, which is slow because it has to check len(self) and get a new
    function from the factory each time, but basically scales your frequency
    range to the len of your list.
    """
    def __init__(self, *args):
        # we don't want to call our musical methods on __init__
        self.data = list(*args)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, i):
        return self.data[i]

    def __delitem__(self, i):
        del self.data[i]

    def __setitem__(self, index, value):
        self.pre_assignment(index, value)
        self.data[index] = value
        self.post_assignment(index, value)

    def __repr__(self):
        return repr(self.data)

    def __str__(self):
        return str(self.data)

    def insert(self, index, value):
        self.pre_insertion(index, value)
        self.data.insert(index, value)
        self.post_insertion(index, value)

    def pre_insertion(self, index, value):
        # self.scaled_play(index)
        # self.scaled_play(value)
        pass

    def post_insertion(self, index, value):
        pass

    def pre_assignment(self, index, value):
        """\
        Defines the function that will be called when an assignment is made.
        Defaults to playing the (scaled) note corresponding to the index,
        followed by the value.

        Note: This assumes you're sorting a list of (strictly) ints or floats.
        If you're sorting strings or some other objects, you need to either
        redefine this function to do casting beforehand or define some other
        function for your tastes.
        """
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
        try:
            sortable.pre_assignment
        except AttributeError:
            sortable = MusicalSortable(sortable)
        sorted = sort_fn(sortable, *args, **kwargs)
        if sorted:
            # not an in place sort?
            return sorted
        return sortable
    return musical_sorter
