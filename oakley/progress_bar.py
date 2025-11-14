
from .fancy_string import cstr
from .mutable_class import MutableClass
import time
from .task import Task
from .message import Message
from .status import MemoryView, TODO # TODO: create an function 'mute_all' to mute all children of MutableClass


class ProgressBar(MutableClass):
    """
    Lightweight iterator wrapper that prints a dynamic progress bar with
    estimated remaining time.

    `ProgressBar` is designed to be used directly in iteration loops:

    >>> for x in ProgressBar(range(100)):
    ...     ...

    The bar updates in-place by printing partial lines (using ``end='\\r'``),
    meaning that the current line is overwritten continuously instead of
    producing new lines. To avoid interference from other printing functions
    during the update, the progress bar registers a `Spirit` that ensures
    the terminal state is kept consistent (see the documentation of
    :meth:`MutableClass.create_spirit` for details).

    Parameters
    ----------
    lst : iterable
        The iterable or iterator over which to loop.
    size : int, optional
        Length of the iterable. Only required when ``lst`` does not
        implement ``__len__`` (e.g., when it is a generator). If omitted,
        the progress bar will attempt to convert the iterable to a list.

    Notes
    -----
    - The progress bar prints at most every 0.05 seconds to avoid excessive
      terminal updates.
    - Printing occurs on a single line using carriage returns (``'\\r'``).
    - A `Spirit` is always active during iteration to prevent unrelated
      printing from corrupting the progress bar display.

    Examples
    --------
    Basic usage:

    >>> for _ in ProgressBar(range(50)):
    ...     time.sleep(0.01)

    Using `whisper` to print a message without breaking the bar:

    >>> for i in ProgressBar(range(100)):
    ...     if i == 50:
    ...         ProgressBar.whisper("Halfway there!")
    """
    
    
    current_instance = None

    
    def __init__(self, lst, size:int=None) -> None:
        """
        Initialize a new progress bar over the given iterable.

        Parameters
        ----------
        lst : iterable
            The iterable or iterator object (e.g., list, range, enumerate,
            zip, numpy array).
        size : int, optional
            Length of the iterable. Required only if `lst` does not implement
            ``__len__``. If omitted and length cannot be determined, the
            iterable is converted to a list, which may be expensive.

        Raises
        ------
        AssertionError
            If the provided object is not iterable.
        """
        super().__init__()
        ProgressBar.current_instance = self
        
        if size is None:
            if not hasattr(lst,'__len__'):
                ProgressBar.print(cstr("[!]").red(),"Warning: unable to iterate over the object of type {type(lst)}. This may be because it is an iterator without a __len__ magic method. In this case, you can provide an argument 'size'.")
                ProgressBar.print(cstr("[!]").red(),"Trying to convert to list (which might be time and memory consuming)...")
                lst = list(lst)
                
            self.max = len(lst)
        else:
            self.max = size
        
            
        assert hasattr(lst,'__iter__'), "The object provided is not iterable."
        self.list = lst.__iter__()
        
        self.count = 0
        self.start_time = time.time()
        
        self.previous_print = ""
        self.previous_print_time = -999
        self.spirit = self.create_spirit("") # always create default spirit
        
    
    def __iter__(self) -> 'ProgressBar':
        return self
    
    def __next__(self):
        if self.max==0:
            raise StopIteration()
        
        self.show()
        self.count += 1 # update the progress
        
        try:
            return next(self.list)
        except StopIteration:
            self.spirit.kill() # remove the spirit from the print stack
            self.print(
                f'{cstr("[%]").magenta() + " Done!":<50}'
            )
            raise(StopIteration())
    
    def show(self) -> None:
        next_print = cstr(
            f"[{round(self.count/self.max * 100):02d}%] "
        ).magenta()
        
        if self.count == 0:
            next_print += "Time remaining: \\"
        else:
            time_of_one_iteration = (time.time()-self.start_time)/self.count
            remaining_time = time_of_one_iteration * (self.max-self.count)
            next_print += f"Time remaining: {self.time(remaining_time)}"
        
        delta_time = time.time() - self.previous_print_time
        
        if next_print != self.previous_print and delta_time > 0.05:
            self.previous_print = next_print
            self.previous_print_time = time.time()
            
            # we are printing comething with "\r", therefore we need a spirit so that someone else doesn't interrupt us
            self.spirit.kill()  # remove the spirit from the print stack
            self.print(
                next_print + " "*10,
                end="\r"
            )
            self.spirit = self.create_spirit("\n")
            
            
        
    @staticmethod
    def whisper(msg:str):
        """
        Print a short message without disrupting the progress bar display.

        A whisper temporarily clears the displayed progress bar, prints the
        message aligned to the same width, and then restores the bar.

        Parameters
        ----------
        msg : str
            The message to display.

        Notes
        -----
        Whispered messages are intended for transient feedback (“Halfway
        there!”, “Loading…”, etc.) that does not break the flow of the bar.

        Examples
        --------
        >>> for i in ProgressBar(range(100)):
        ...     if i == 50:
        ...         ProgressBar.whisper("Halfway there!")
        """
        if ProgressBar.current_instance is None: # should not happen, I guess whisper is always inside a progressbar loop
            return ProgressBar.print(cstr("[%]").magenta(), msg)

        # 1. Erase the current progress bar
        ProgressBar.current_instance.spirit.kill()  # remove the spirit from the print stack
        to_print = cstr("[%]").magenta() + " " + msg
        ProgressBar.current_instance.print("\r", end="")
        ProgressBar.current_instance.print(f"{to_print:<{len(ProgressBar.current_instance.previous_print)}}")
        ProgressBar.current_instance.show()
        

if __name__ == '__main__':
    
    with Task("Computing something heavy", new_line=True):
        for i in ProgressBar(range(100), size=100):
            time.sleep(0.05)
            if i==50:
                ProgressBar.whisper("Halfway there!")
        
    with Task("Computing something heavy again"):
        for i in ProgressBar(range(3)):
            time.sleep(1)
            if i==1:
                ProgressBar.whisper("Halfway there!")
                
    with Task("Computing something fast, no every step is printed!"):
        for i in ProgressBar(range(10_000), size=10000):
            time.sleep(0.0001)
            
    
    Message("Success!", "#")
