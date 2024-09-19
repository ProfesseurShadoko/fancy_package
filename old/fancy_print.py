
from typing import Literal
import time
import traceback as tb
import shutil
import os
import numpy as np


class ColoredString(str):
    """
    Class inheritting for type string, with a few additional methods for coloring the string when printed to the console.
    
    Methods:
        green: Returns the string in green color
        blue: Returns the string in blue color
        red: Returns the string in red color
        yellow: Returns the string in yellow color
        bold: Returns the string in bold font
        underline: Returns the string with underline
        italic: Returns the string in italic font
        strikethrough: Returns the string with strikethrough
        highlight: Returns the string with highlighted background
        
    Format:
        print(f'{ColoredString("This is a colored string"):green}') # prints the string in green color
        print(f'{ColoredString("This is a colored string"):g}') # prints the string in green color
        
    """
    
    def __init__(self,string:str):
        """
        Args:
            string (str): The string to be printed in color (can also be anything that can be converted to a string using str() function)
        """
        super().__init__() # how the hell does this work???
        
    
    ##############
    ### COLORS ###
    ##############
    
    def green(self)->'ColoredString':
        return self.__class__('\033[92m' + self + '\033[0m')
    
    def blue(self)->'ColoredString':
        return self.__class__('\033[94m' + self + '\033[0m')
    
    def red(self)->'ColoredString':
        return self.__class__('\033[91m' + self + '\033[0m')
    
    def yellow(self)->'ColoredString':
        return self.__class__('\033[93m' + self + '\033[0m')
    
    def magenta(self)->'ColoredString':
        return self.__class__('\033[95m' + self + '\033[0m')

    def cyan(self)->'ColoredString':
        return self.__class__('\033[96m' + self + '\033[0m')
    
    
    #############
    ### FONTS ###
    #############
    
    def bold(self)->'ColoredString':
        return self.__class__('\033[1m' + self + '\033[0m')
    
    def underline(self)->'ColoredString':
        return self.__class__('\033[4m' + self + '\033[0m')
    
    def italic(self)->'ColoredString':
        return self.__class__('\033[3m' + self + '\033[0m')
    
    def strikethrough(self)->'ColoredString':
        return self.__class__('\033[9m' + self + '\033[0m')
    
    def highlight(self)->'ColoredString':
        return self.__class__('\033[7m' + self + '\033[0m')
    
    
    ##############
    ### FORMAT ###
    ##############
    
    def __format__(self, format_spec:str) -> 'ColoredString':
        if not format_spec:
            return self
        
        methods = {
            "green": self.green(),
            "blue": self.blue(),
            "red": self.red(),
            "yellow": self.yellow(),
            "cyan": self.cyan(),
            "magenta": self.magenta(),
        }
        
        allowed_specs = list(methods.keys())
        allowed_specs += [spec[0] for spec in allowed_specs]
        
        assert format_spec in allowed_specs, f"Unknown format spec: {format_spec}. Must be one of {allowed_specs}"
        
        if len(format_spec) == 1:
            # find color that starts with this letter
            for color in methods.keys():
                if color[0] == format_spec:
                    return methods[color]
        
        return methods[format_spec]


def cstr(string:str, format_spec:str="") -> ColoredString:
    """
    A ColoredString is a string that can be printed in color in the console. It has methods to change the color of the string,
    and also supports formatting. See examples below. If a format specifier is passed in arguments, it will be applied to the string
    before transforming it into colored string.
     
    Returns:
        ColoredString object from the given string. This is a shortcut for ColoredString(string).
        
    Example:
        >>> print(
            cstr("This is a colored string").green().bold()
        )
        >>> print(
            f"Here are different colors: {cstr('yellow'):y}, {cstr('green'):g}, {cstr('blue'):b}, {cstr('red'):r}, {cstr('cyan'):c}, {cstr('magenta'):m}"
        )
    """
    return ColoredString(
        format(string, format_spec) 
    )



class FancyContextManager:
    def __enter__(self):
        pass
    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            print(
                f"Context Manager exited with error {cstr(exc_type.__name__):r}",
                f"{cstr(exc_value):r}",
                sep='\n'
            )
            tb.print_tb(traceback)
            
            
    


class MutableClass:
    """
    Implements a class that can be muted, i.e. the print function of the class can be muted. Used by Message and Task.
    
    Properties:
        - muted: Returns True if the class is muted, False otherwise
    
    Methods:
        - mute: Mutes the class
        - unmute: Unmutes the class
        - print: Prints the message if the class is not muted
    
    Static Methods:
        - cstr: Returns a ColoredString object from the given string
        - time: Transforms a number of seconds into a string 'hh:mm:ss'
        
    Context Manager:
        - see silence() method
    """
    
    mute_count = 0
    indent = 0
    
    @classmethod
    def muted(cls:type) -> bool:
        """
        Checks if the class is muted, that is if the mute() function has been called more times than the unmute() function.
        """
        return cls.mute_count > 0
    
    @classmethod
    def mute(cls:type) -> None:
        cls.mute_count += 1
        
    @classmethod
    def unmute(cls:type, force:bool = False) -> None:
        if force:
            cls.mute_count = 0
            
        cls.mute_count -= 1
        cls.mute_count = max(0,cls.mute_count)
        
    
    ###################    
    ### PRINT STUFF ###
    ###################
    
    @staticmethod
    def tab() -> None:
        """
        Increases the indent for every class inheriting from MutableClass.
        
        Returns:
            context manager that calls 'untab' when exiting the context.
        """
        MutableClass.indent += 1
        class TabContext(FancyContextManager):
            def __exit__(self, *args):
                MutableClass.untab()
                super().__exit__(*args)
                
        return TabContext()
    
    @staticmethod
    def untab() -> None:
        """
        Decreases the indent for every class inheriting from MutableClass.
        """
        MutableClass.indent -= 1
        MutableClass.indent = max(0,MutableClass.indent)
        
    @classmethod
    def par(cls:type) -> None:
        """
        New paragraph in the console.
        """
        if not cls.muted():
            print() # cannot use cls.print() or else the tab will appear
    
    @classmethod
    def print(cls:type, *args, **kwargs) -> None:
        """
        Same arguments as standard print function. Prints the message if the class is not muted.
        
        If ignore_tabs is set to True, the message will not be indented. Default is False.
        """
        if not 'flush' in kwargs:
            kwargs['flush'] = True
            
        if not cls.muted():
            if MutableClass.indent > 0 and not kwargs.get('ignore_tabs',False):
                print(" " + ">"*MutableClass.indent, end=" ")
            if 'ignore_tabs' in kwargs:
                del kwargs['ignore_tabs']
                
            print(*args, **kwargs)
    
    @staticmethod
    def cstr(msg:str) -> ColoredString:
        return ColoredString(msg)
    
    @staticmethod
    def time(seconds:float) -> str:
        """
        Transforms a number of seconds into a string 'hh:mm:ss'.
        """
        if seconds >= 60:
            seconds = int(seconds)
            hrs = seconds // 3600
            seconds %= 3600
            mins = seconds // 60
            seconds %= 60
            return f"{hrs:02d}:{mins:02d}:{seconds:02d}"
        else:
            return f"{seconds:.3f}s"
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} (mutable): idx={self.idx}>"
    
    def __eq__(self, other) -> bool:
        return type(self) == type(other) and self.idx == other.idx
    
    
    #######################
    ### CONTEXT MANAGER ###
    #######################
    
    @classmethod
    def silence(cls):
        """
        Returns:
            Context manager that mutes the class for the duration of the context.
            
        Example:
        >>> with Message.silence(): # with Message inheritting from MutableClass
        >>>     Message("This should not be printed") # not printed
        >>> Message("This should now be printed") # printed
        """
        class MuteContext(FancyContextManager):
            def __enter__(self):
                super().__enter__()
                cls.mute()
            def __exit__(self, *args):
                cls.unmute()
                super().__exit__(*args)
        return MuteContext()
    
        
        
        


class Message(MutableClass):
    """
    Prints a message to the console, with a fancy color.
    
    The different types (arg 'typ') correspond to:
        - "!" or 'danger' or 'd' : error message
        - "?" or 'warning' or 'w' : warning message
        - "#" or 'success' or 's': success message
        - "-" or 'neutral' or 'n': neutral message
    """

    def __init__(self, msg:str, typ:Literal['!', '?', '#', 'i', 'danger', 'warning', 'success', 'info', 'd', 'w', 's', 'i']='i') -> None:
        """
        Prints a message to the console, with a fancy color.
        
        The different types (arg 'typ') correspond to:
            - "!" or 'danger' or 'd' : error message
            - "?" or 'warning' or 'w' : warning message
            - "#" or 'success' or 's': success message
            - "-" or 'neutral' or 'n': neutral message
        """
        super().__init__()

        match typ:
            case '!' | 'danger' | 'd':
                prefix = self.cstr("[!]").red()
            case '?' | 'warning' | 'w':
                prefix = self.cstr("[?]").yellow()
            case '#' | 'success' | 's':
                prefix = self.cstr("[#]").green()
            case 'i' | 'info':
                prefix = self.cstr("[i]").cyan()
            case _:
                raise ValueError(f"Unknown type: {typ}. Must be one of ['!','?','#','i']")
        
        self.print(prefix, msg)   
        
    def __repr__(self) -> str:
        return "" # avoid printing the message in Jupyter cells 


class Task(MutableClass, FancyContextManager):
    """
    Fancy way of printing a task that is being executed. At the end of the Task, it prints the message and the time it took to complete the task.
    
    Example
    -------
    >>> Task("Processing data")
    >>> time.sleep(5)
    >>> Task.complete() # prints "[~] Task completed after: 00:00:05"
    
    This object can also be used as a context manager:
    >>> with Task("Processing data"):
    >>>     time.sleep(5)
    >>> # prints "[~] Task completed after: 00:00:05"
    """
    
    running_tasks = []
    last_task_runtime = None
    
    def __init__(self,*msg:str, new_line:bool = True) -> None:
        """
        Args:
            *msg: The message to be printed. If several messages, they will be concatenated with a space in between.
            new_line (bool): whether to print the progress on the same line ('') or on a new line ('\n').
        """
        super().__init__()
        self.new_line = new_line
        
        self.msg = " ".join([str(m) for m in msg])
        self.start_time = time.time()
        self.print(
            self.cstr('[~]').blue(), self.msg, end = "\n" if self.new_line else " "
        )
        
        if not self.muted():
            MutableClass.tab()
        
        self.__class__.running_tasks.append(self) # set to current task

    
    def _complete(self) -> None:
        if not self.muted():
            MutableClass.untab()
        
        Task.last_task_runtime = time.time()-self.start_time
        if self.new_line:
            self.print(
                self.cstr('[~]').blue(), "Task completed after:", self.cstr(self.time(Task.last_task_runtime)).blue()
            )
        else:
            self.print(
                f" ({self.cstr(self.time(time.time()-self.start_time)).blue()})", ignore_tabs=True
            )
        assert self.__class__.running_tasks[-1] == self, "The task that is being completed is not the last one that was started. Finish the previous tasks first."
        self.__class__.running_tasks.pop()
        
        
    def _abort(self) -> None:
        if not self.muted():
            MutableClass.untab()
            
        if not self.new_line:
            self.print() # we might still be on the line of the first print statement of the Task function, don't stay on the same line
            
        self.print(
            self.cstr('[!]').red(), "Task aborted after:", self.cstr(self.time(time.time()-self.start_time)).red()
        )
        
        assert self.__class__.running_tasks[-1] == self
        self.__class__.running_tasks.pop()
        
    @classmethod
    def complete(cls:type) -> None:
        """
        Print the message and the time it took to complete the task. The task is the last to have been created.
        """
        assert len(cls.running_tasks) > 0, "No task is currently being executed."
        cls.running_tasks[-1]._complete()
    
    @classmethod
    def abort(cls:type) -> None:
        assert len(cls.running_tasks) > 0, "No task is currenlty being executed."
        cls.running_tasks[-1]._abort()
        
    
    #######################
    ### CONTEXT MANAGER ###
    #######################
    
    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self.__class__.complete()
        else:
            self.__class__.abort()
        super().__exit__(exc_type, exc_value, traceback)
        

class FancyIterator(MutableClass):
    """
    Parameters
    ----------
    lst: iterable or iterator object (list, range, enumerate, zip, np.array, etc.)
    size: The size of the list. If the object is an iterator, it may not have a __len__ magic method. In this case, provide the size of the iterator.
    
    Returns
    -------
        iterator object that prints the progress of the iteration (and the remaining time).
        
    Example
    -------
    >>> for i in FancyIterator(range(100), size=100):
    >>>    Task("Processing item",i) # this is muted during the iteration
    >>>    time.sleep(0.1)
    >>>    Task("Item",i,"processed!") # this is muted during the iteration
    """
    
    def __init__(self, lst, size:int=None, new_line:bool = False) -> None:
        """
        Simple iterator that prints the progress of the iteration and the remaining time.
        
        Args:
            lst: iterable or iterator object (list, range, enumerate, zip, np.array, etc.)
            size: The size of the list. If the object is an iterator, it may not have a __len__ magic method. In this case, provide the size of the iterator.
            new_line: whether to print the progress on the same line ('\r') or on a new line ('\n'). If on a new line, other mutable classes wont be muted.
        
        Returns:
            iterator
        """
        super().__init__()
        
        if size is None:
            if not hasattr(lst,'__len__'):
                FancyIterator.print(self.cstr("[!]").red(),"Warning: unable to iterate over the object of type {type(lst)}. This may be because it is an iterator without a __len__ magic method. In this case, you can provide an argument 'size'.")
                FancyIterator.print(self.cstr("[!]").red(),"Trying to convert to list (which might be time and memory consuming)...")
                lst = list(lst)
                
            self.max = len(lst)
        else:
            self.max = size
        
            
        assert hasattr(lst,'__iter__'), "The object provided is not iterable."
        self.list = lst.__iter__()
        
        self.count = 0
        self.start_time = time.time()
        
        self.previous_print = ""
        
        self.new_line = new_line
        
        if not self.new_line:
            Message.mute()
            Task.mute()
        
    
    def __iter__(self) -> 'FancyIterator':
        return self
    
    def __next__(self):
        if self.max==0:
            raise StopIteration()
        
        self.show()
        self.count += 1 # update the progress
        
        try:
            return next(self.list)
        except StopIteration:
            if not self.new_line:
                Message.unmute() # unmute the classes that were muted for the execution
                Task.unmute()
            self.print(
                self.cstr("[%]").magenta(),
                " Done!" + " "*50
            )
            raise(StopIteration())
    
    def show(self) -> None:
        next_print = self.cstr(
            f"[{round(self.count/self.max * 100):02d}%] "
        ).magenta()
        
        if self.count == 0:
            next_print += "Time remaining: \\"
        else:
            time_of_one_iteration = (time.time()-self.start_time)/self.count
            remaining_time = time_of_one_iteration * (self.max-self.count)
            next_print += f"Time remaining: {self.time(remaining_time)}"
        
        if next_print != self.previous_print:
            self.previous_print = next_print
            
            self.print(
                next_print + " "*10,
                end=("\r" if not self.new_line else "\n")
            )


class TempFolder(FancyContextManager):
    
    def __init__(self):
        self.idx = np.random.randint(100, 1000)
    
    @property
    def path(self) -> str:
        return f"temp_idx-{self.idx}"
    
    def __enter__(self):
        super().__enter__()
        if os.path.exists(self.path):
            shutil.rmtree(self.path)
        os.makedirs(self.path)
        return self
    
    def __exit__(self, *args):
        super().__exit__(*args)
        shutil.rmtree(self.path)
        


if __name__ == "__main__":
    
    # 0. Testing the color print
    print(
        f"Here are different colors: {cstr('yellow'):y}, {cstr('green'):g}, {cstr('blue'):b}, {cstr('red'):r}, {cstr('cyan'):c}, {cstr('magenta'):m}"
    )
    
    Message.par()
    # 1. testing the Message class
    Message("This is a neutral message")
    Message("This is a warning message","warning")
    Message("This is a success message","success")
    Message("This is an error message","danger")
    
    Message.par()
    # 2. testing the Task class
    Task("Processing data")
    time.sleep(1)
    Task.complete()
    
    with Task("Processing data with context manager"):
        time.sleep(1)
    
    try:
        with Task("Processing data with an error occuring"):
            time.sleep(1)
            raise ValueError("An error occured")
    except ValueError as e:
        pass
    
    with Task("Processing data with nested Tasks and Messages"):
        Task("Processing subtask 1")
        time.sleep(1)
        Message("Something is happening")
        Task.complete()
        with Task("Processing subtask 2"):
            time.sleep(1)
            Message("Something else is happening","!")
    
    Message.par()
    # 3. testing the FancyIterator class
    Task("Iterating over something")
    for i in FancyIterator(range(100), size=100):
        Task("Processing item",i)
        time.sleep(0.03)
        Task.complete()
    Task.complete()
    
    Message.par()
    # 4. testing the MutableClass.silence() context manager
    with Message.silence():
        Message("This should not be printed","!")
    Message("This should now be printed","#")
    
    
    # 5. testing the Task new option
    with Task("Processing data, completion on same line", new_line=False):
        time.sleep(1)
    
    try:
        with Task("Same thing, but with and error", new_line=False):
            time.sleep(1)
            raise ValueError("An error occured")
    except ValueError as e:
        pass
    
    Message.par()
    # 6. Testing tab context
    Message("This is not indented")
    Message.tab()
    Message("This is indented")
    Message.untab()
    Message("This is not indented")
    
    with Message.tab():
        Message("This is indented, again")
    Message("This is not indented, again")
    
    
    with Task("Testing Coloredstring format specifier"):
        
        print(f"Printing in yellow: {Message.cstr('This is yellow'):y}")
    
    
    