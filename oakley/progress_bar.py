
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
        self.previous_print_time = -999 # we want to avoid printing too often!
        self.spirit = self.create_spirit("") # always create default spirit
        
        # keep track of the time of the last 10 steps
        self.time_of_steps = []
        
        
    # ------------------------- #
    # !-- Iterator Protocol --! #
    # ------------------------- #
        
    
    def __iter__(self) -> 'ProgressBar':
        return self
    
    def __next__(self):
        if self.max==0:
            raise StopIteration()
        
        self.time_of_steps.append(time.time())
        # keep only last 20 steps
        if len(self.time_of_steps)>20:
            self.time_of_steps.pop(0)
        
        self.show()
        self.count += 1 # update the progress
        
        try:
            return next(self.list)
        except StopIteration:
            self.spirit.kill() # remove the spirit from the print stack
            self.print(ignore_tabs=True) # go to next line
            raise(StopIteration())
        
    
    # -------------- #
    # !-- Header --! #
    # -------------- #
    
    def _get_header(self, terminal_width:int) -> str:
        """
        Returns the header part of the progress bar, which can be either
        a percentage or a spinner if the max is unknown.
        """
        progress_percent = f"{(int(self.count/self.max*100)):02d}%" if self.max>0 and self.count < self.max else "%"
        header = cstr(f"[{progress_percent}]")
        return header.red() if self.count < self.max else header.green()
    
    def _get_bar(self, terminal_width:int) -> str:
        
        if self.count == self.max:
            return ""
        
        # we assume that header + stats take 50 characters at most
        bar_width = terminal_width - 50
        
        if bar_width < 5:
            return ""
        
        bar_width = min(25, bar_width)
        bar_car = "━"
        n_bars_completed = int(bar_width * self.count / self.max)
        n_bars_remaining = bar_width - n_bars_completed
        if n_bars_completed == 0 or n_bars_remaining == 0:
            sep_char = " "
        else:
            sep_char = ""
            if n_bars_completed == 0:
                n_bars_remaining += 1
            if n_bars_remaining == 0:
                n_bars_completed += 1
            
        bar = cstr(bar_car*n_bars_completed).green() + " " + cstr(bar_car*n_bars_remaining).red()
        return bar
    
    def _get_stats(self, terminal_width:int) -> str:
        
        # 1. Compute elapsed time
        elapsed_time = self.time_of_steps[-1] - self.start_time # self.time_of_steps can never be empty here
        elapsed_time_str = ProgressBar.time(elapsed_time)
        
        # 2. Compute the average it/s (as average over last steps)
        if self.count == 0:
            it_per_s = "?"
        else:
            n_steps = len(self.time_of_steps)-1
            delta_time = self.time_of_steps[-1] - self.time_of_steps[0]
            it_per_s = it_per_time = n_steps/delta_time
            
            # choose units
            it_per_time_unit = "it/s"
            if it_per_time < 2:
                it_per_time = it_per_time * 60 # it per minute
                it_per_time_unit = "it/min"
            if it_per_time < 2:
                it_per_time = it_per_time * 60 # it per hour
                it_per_time_unit = "it/h"
            it_per_time_str = ProgressBar.number(it_per_time) + f" {it_per_time_unit}"
        
        # 3. Compute remaining time
        if self.count==0 or self.max==0:
            remaining_time_str = "?"
        else:
            n_steps_remaining = self.max - self.count
            remaining_time_sec = n_steps_remaining / it_per_s
            remaining_time_str = ProgressBar.time(remaining_time_sec)
        
        # 4. Get progress count/max
        progress_count_str = f"{ProgressBar.number(self.count)}/{ProgressBar.number(self.max)}" if self.max>0 else "?"
        
        # 5. Combine all stats
        if self.count == 0:
            return ""
        
        if terminal_width < 40:
            return f"[{elapsed_time_str} > {remaining_time_str}]" # len = 23 (including header)
        if terminal_width < 50:
            return f"[{elapsed_time_str} > {remaining_time_str}, {it_per_time_str}]" # len = 34 (including header)
        return f"[{elapsed_time_str} > {remaining_time_str}, {it_per_time_str}, {progress_count_str}]" # len = 42 (including header)
        
    
    
    # ---------------------------- #
    # !-- Progress Bar Display --! #
    # ---------------------------- #
    
    def show(self) -> None:
        """
        Displays the current progress. The progress shall be displayed as
        the combination of three parts:
         - a header ([%] for instance or [23%]) or spinner
         - a bar showing progress
         - numbers [23/100, elapsed time > remaining time, it/s]
        
        At the beginning of each call of the show function, some space 
        is allowated to each part, so that the progress bar does not
        exceed the terminal width. This space is re-evaluated at each call
        of the show function, so that if the terminal is resized, the progress
        bar still fits in the terminal.
        """
        
        # 1. Check if we should print something
        
        current_time = time.time()
        # if we have printed something less than 0.05s ago, we skip this print
        # unless this is the very last print!
        delta_time = current_time - self.previous_print_time
        if delta_time < 0.05 and self.count < self.max:
            return
        if self.count == self.max:
            time.sleep(0.05) # wait a bit to ensure the last print is after 0.05s from previous one
        
        # 2. Prepare the next print
        terminal_width = self._get_terminal_width() # between 30 and 75
        
        header = self._get_header(terminal_width)
        bar = self._get_bar(terminal_width)
        numbers = self._get_stats(terminal_width) # all separated by " "
        
        next_print = " ".join([item for item in [header, bar, numbers] if item])
        self.previous_print_time = time.time()
        
        # we are printing comething with "\r", therefore we need a spirit so that someone else doesn't interrupt us
        self.spirit.kill()  # remove the spirit from the print stack
        self._print_pb(
            next_print,
            newline=False
        )
        self.spirit = self.create_spirit("\n")
            
    
    def _print_pb(self, msg:str, newline:bool = True) -> None:
        """
        Prints if and only if the message is different from the previous one.
        Prints enough white spaces to fill the line (and erase previous content).
        
        If not newline, then the print ends with '\r' instead of '\n'.
        """
        if msg != self.previous_print:
            n_to_erase = cstr(self.previous_print).length()
            n_to_erase = min(self._get_terminal_width(min_value=0, margin=5), n_to_erase)
            self.print("\r", end="", ignore_tabs=True) # go back to the beginning of the line
            n_spaces = max(0, n_to_erase - cstr(msg).length())
            self.print(msg + n_spaces*" ", end="\n" if newline else "") # go back to the beginning of the line and erase previous content
            
            # 3. Update previous print
            self.previous_print = msg
            self.previous_print_time = time.time()
            
            #print("Number to erase:", n_to_erase)
            #print("Printed:", f"{msg:<{n_to_erase}}", f"(length = {cstr(f'{msg:<{n_to_erase}}').length()})")
            
            
            
    def _get_terminal_width(self, margin:int = 5, min_value:int=25) -> int:
        """
        Returns the current terminal width in number of characters.
        """
        import shutil
        terminal_size = shutil.get_terminal_size((999, 20)).columns
        n_tab_chars = ProgressBar.indent + 2 if ProgressBar.indent > 0 else 0
        # Also, if the terminal size is lower than 30, we set is to 30. And let's keep an additional 5 characters of margin.
        return max(min_value, terminal_size - n_tab_chars - margin)
            
        
        
    # ------------- #
    # !-- Utils --! #
    # ------------- #   
        
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
            return ProgressBar.print(msg)

        # 1. Erase the current progress bar
        ProgressBar.current_instance.spirit.kill()  # remove the spirit from the print stack
        to_print = msg
        ProgressBar.current_instance._print_pb(to_print)
        ProgressBar.current_instance.show()
        

if __name__ == '__main__':
    
    
    # 1. Test in normal conditions    
    with Message("Computing something heavy"):
        for i in ProgressBar(range(100)):
            time.sleep(0.05)
    
    # 2. Test when super fast
    with Message("Computing something super fast"):
        for i in ProgressBar(range(10_000)):
            time.sleep(5e-4)
            
    Message.par()
    
    # 3. Test whisper
    with Message("Testing whisper"):
        for i in ProgressBar(range(100)):
            time.sleep(0.03)
            if i==50:
                ProgressBar.whisper("Halfway there!")
                
    # 4. Testing other prints
    with Message("Testing normal prints"):
        for i in ProgressBar(range(100)):
            time.sleep(0.03)
            if i==50:
                print("This is a normal print.")
    
    Message.par()
    
    # 5. Testing various termial widths
    class LengthMeasuringPB(ProgressBar):
        
        
        
        def __init__(self, terminal_width:int, *args, **kwargs):
            self.terminal_width = terminal_width
            super().__init__(*args, **kwargs)
            self.print_of_max_length = ""
            
            
        def __next__(self):
            if cstr(self.previous_print).length() > cstr(self.print_of_max_length).length():
                self.print_of_max_length = self.previous_print
            
            try:
                return super().__next__()
            except StopIteration:
                with Message(f"Max print length was {cstr(cstr(self.print_of_max_length).length()):c} (max allowed {self.terminal_width})"):
                    Message.print(f"The print was: '{self.print_of_max_length}'")
                raise(StopIteration())
            
        def _get_terminal_width(self, *args, **kwargs):
            return self.terminal_width  
                
    
    for width in [40, 50, 70, 80]:
        with Message(f"Testing terminal width = {width}"):
            for i in LengthMeasuringPB(width, range(100)):
                time.sleep(0.02)
        
        
    Message.par()
    with Message("Testing changing terminal size"):
        Message.print("During the following loop, please resize your terminal window to see how the progress bar adapts.")
        for i in ProgressBar(range(1000)):
            time.sleep(0.02)
            
            
    # 6. Real cas escenario
    n_iters = 5000
    time_per_iter = 600 / n_iters # 10 minutes total
    with Message("Processing data..."):
        time_start = time.time()
        for i in ProgressBar(range(n_iters)):
            time.sleep(time_per_iter)
            
            if time.time() - time_start > 20:
                Message("Let's not go any further and exit now!", "?")
                break
            
            
            
    
