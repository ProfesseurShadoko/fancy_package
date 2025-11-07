

from .fancy_string import cstr
from .mutable_class import MutableClass
from typing import Literal
import os




class Message(MutableClass):
    """
    Inherits from MutableClass.
    
    Methods:
        __init__(...): Constructor. Displays the message.
        listen(cls, ...): Defines which messages should be displayed, depending on their importance.
    
    Parent Methods:
        mute: Mutes the class
        unmute: Unmutes the class
        tab: Adds a tabulation to all upcoming messages. Can be used as a context manager.
        silence: Mutes the class for the duration of the context manager. At the exit of the cm, the class will be automatically unmuted.
    """
    
    _active = ['i', '#', '?', '!']
    
    def __init__(self, msg:str, type:Literal['#', '?', '!', 'i'] = 'i') -> None:
        
        assert isinstance(msg, str), f"msg must be a string, not {msg.__class__}"
        assert type in ['#', '?', '!', 'i'], f"type must be one of '#', '?', '!', 'i', not {type}"
        self.msg = msg
        self.type = type
        
        self._display()
    
    
    def _display(self) -> None:
        if not self.type in self._active:
            return
        
        self.print(
            self._get_prefix(), self.msg
        )
        
    def _get_prefix(self) -> str:
        return {
            '#': cstr('[#]').green(),
            'i': cstr('[i]').cyan(),
            '?': cstr('[?]').yellow(),
            '!': cstr('[!]').red()
        }[self.type]
    
    @classmethod
    def listen(cls:type, lvl:int=0) -> None:
        """
        Defines which messages should be displayed, depending on their importance.
        
        Args:
            lvl (int): The level of importance of the message. 0 lets all messages be displayed, 1 only warnings and errors, 2 only errors.
        """
        cls._active = {
            0: ['i', '#', '?', '!'],
            1: ['?', '!'],
            2: ['!']
        }[lvl]
        
    @staticmethod
    def cwd() -> None:
        """
        Prints the current working directory.
        """
        Message(f"Current working directory: {cstr(os.getcwd()):g}", "#")
        
    def list(self, collection:list|dict) -> None:
        """
        Displays the content of the list by printing them one by one. If the object is a dictionary, it prints the keys and values.
        """
        color = {
            "#": "g",
            "?": "y",
            "i": "c",
            "!": "r"
        }[self.type]
        with Message.tab():
            
            n_digits = None
            if not isinstance(collection, dict):
                # check that colleciton is iterable
                try:
                    iter(collection)
                except TypeError:
                    Message.print(collection) # just print out the object
                
                # transform into a dictionary idx --> value
                collection = {i: value for i, value in enumerate(collection)}
                n_digits = len(str(len(collection)-1)) # optimized computation of log10 here
                
            if len(collection) == 0:
                Message.print(f"{cstr('empty'):ri}")
            
            # find the longest key in the collection
            max_key_length = max([len(str(key)) for key in collection]) if n_digits is None else n_digits
            
            for key, value in collection.items():
                
                if n_digits is None:
                    key = f"{cstr(key):{color}}:" + " " * (max_key_length - len(str(key)))
                else:
                    key = f"{cstr(key, f'0{n_digits}d'):{color}}:"
                
                Message.print(f"{key} {value}")
            



if __name__ == '__main__':
    Message("This is a success message", "#")
    Message("This is an info message", "i")
    Message("This is a warning message", "?")
    Message("This is an error message", "!")
    Message.par()
    Message.listen(1)
    Message("This is a success message. It should not be displayed.", "#")
    Message("This is a warning. It should be displayed.", "?")
    
    Message.listen()
    Message.par()
    
    with Message.tab():
        Message("This message should be indented.")
    Message("This message should not be indented.")
    Message.par()
    
    
    my_array = [1, 2, 0, 0, 89, 1]
    my_dict = {
        "name": "Bob",
        "age": 21
    }
    
    Message("My Array:", "?").list(my_array)
    Message("Information:").list(my_dict)
    
    
    
    
    
    
    
