


from .mutable_class import MutableClass
from .message import Message
from .fancy_string import cstr

import os
import gc
import sys


class MemoryView(MutableClass):
    
    def __init__(self):
        tot_ram = self.get_memory_available() + self.get_memory_usage()
        memory_usage = self.get_memory_usage()/tot_ram
        color_letter = 'g' if memory_usage < 0.5 else 'y' if memory_usage < 0.8 else 'r'
        memory_usage_percent = f"{cstr(f'{memory_usage:.0%}'):{color_letter}}"
        
        self.print(
            f"{cstr('[M]').blue()} Current memory usage: {self.get_memory_usage():.2f} GB / {tot_ram:.2f} GB ({memory_usage_percent})"
        )
    
    
    def get_memory_usage(self) -> float:
        """
        Returns the current memory usage of the process in MB.
        """
        import psutil
        process = psutil.Process(os.getpid())
        memory = process.memory_info().rss / (1024 ** 3)  # in GB
        return memory
    
    def get_memory(self) -> float:
        """
        Returns the available memory in GB.
        """
        import psutil
        memory = psutil.virtual_memory().total / (1024 ** 3)  # in GB
        return memory
    
    def get_memory_available(self) -> float:
        """
        Returns the available memory in GB.
        """
        import psutil
        memory = psutil.virtual_memory().available / (1024 ** 3)  # in GB
        return memory
    
    @staticmethod
    def show(top:int=5):
        """
        Shows the memory usage of the top <top> memory-consuming processes.
        """
        gc.collect()
        all_objects = gc.get_objects()
        
        # get all individual types and their total memory usage
        type_memory = {}
        for obj in all_objects:
            obj_type = type(obj)
            try:
                obj_size = sys.getsizeof(obj)
            except TypeError:
                obj_size = 0
            type_memory[obj_type] = type_memory.get(obj_type, 0) + obj_size
        
        # sort by memory usage
        sorted_types = sorted(type_memory.items(), key=lambda x: x[1], reverse=True)
        
        # dispaly the 10 first
        with MemoryView():
            for i, (obj_type, total_size) in enumerate(sorted_types[:top], 1):
                size_mb = total_size / (1024 ** 2)
                print(f"{i}. Type: {cstr(obj_type.__name__):bb}, Total Size: {size_mb:.2f} MB")
    
    
    
    
class TODO(MutableClass):
    def __init__(self, message: str, complete:bool = False):
        prefix = '[x]' if complete else '[ ]'
        color = 'g' if complete else 'r'
        
        self.print(
            f"{cstr(prefix):{color}} TODO: {message}"
        )
        

class DateTime(MutableClass):
    def __init__(self):
        self.print(f"{cstr('[D]').magenta()} {self.time_date()}")
        

if __name__ == "__main__":
    from .message import Message
    
    with Message("Displaying memory usage:"):
        MemoryView()
        
    Message.par()
    with Message("Making TODO list:"):
        TODO("This is a test TODO item.")
        TODO("This is a completed TODO item.", complete=True)
        
    Message.par()
    with Message("Displaying current date and time:"):
        DateTime()