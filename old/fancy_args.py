if __name__ == "__main__":
    import os
    import sys
    
    while not os.path.exists("utils"):
        os.chdir("..")
    print("Current working directory:", os.getcwd())
    sys.path.append(os.getcwd())



from argparse import ArgumentParser
from utils.fancy_print import *
import sys
import os
import subprocess
import runpy




class FancyArg:
    parser:ArgumentParser = None
    fancy_args:list['FancyArg'] = []
    out_list:list = None
    out_dict:dict = None
    last_return = None
    
    def __init__(self, varname:str, help:str = "", type:type=str, choices:list=None, default=None):
        """
        Adds a new argument to the parser initialized with FancyArg.set_description(description:str). And argument
        is required if and only if the default value is not None.
        
        Args:
            varname (str): The name of the variable to add to the parser. The argument will be '--varname'.
            help (str): The help message to display when using the --help flag.
            typ (type): The type of the argument. Can be str, int, float, bool, list, or None.
            choices (list): A list of possible choices for the argument. If provided, the argument must be in this list, the types should match, the default value mustbe one of the values.
            default: The default value of the argument. If not provided, the argument is required.
        """
        
        
        assert FancyArg.parser is not None, "Call FancyArg.set_desription('...') before creating any FancyArg objects"
        
        self.varname = varname
        self.required = (default==None)
        self.typ = type
        self.choices = choices
        self.default = default
        self.help = help
        
        self.is_bool = (self.typ == bool)
        self._modify_for_bool_typ()
        
        self.is_list = (self.typ == list)
        self._modify_for_list_typ()
        
        self._check_arg_compatible()
        self._update_help()
        
        self._add()
    
    
    ##################
    ### initialize ###
    ##################
    
    def _modify_for_bool_typ(self):
        """
        Called by __init__ function. Modifies the attribute so that bool type besome 1 or 0.
        """
        if not self.is_bool:
            return # no need to do anything
        
        # choices are 1 and 0 for False or True
        if self.choices is not None:
            Message("Warning: choices are ignored for boolean arguments, since boolean arguments correspond to 1 or 0.", "!")

        self.choices = None # we want to allow 1, 0, but also True and False
        
        # typ will now be an integer
        self.typ = str # this can be either an integer (1) or a string ("True")
        
        # default becomes an integer
        if self.default is not None:
            assert type(self.default) == bool, f"Default value {self.default!r} is not of type bool!"
            self.default = str(int(self.default))
    
    def _modify_for_list_typ(self) -> None:
        """
        Called by __init__ function. Modifies the attribute so that list type becomes a comma-separated string.
        """
        if self.typ != list:
            return
        
        assert self.default is None or isinstance(self.default, list), f"Default value {self.default} should by of type list, not {type(self.default).__name__!r}"
        assert self.default is None or len(self.default) == 0 or isinstance(self.default[0], str), f"Default value should be a list of strings, not a list of {type(self.default[0]).__name__!r}"
        
        self.default = ",".join(self.default) if self.default is not None else None
        self.typ = str
        
            
    def _update_help(self) -> None:
        """
        Called by __init__ function to add additionnal information to 'help' depending on arguments of __init__
        """
        
        # required of not
        if self.required:
            self.help = cstr("[!] ").red() + self.help
        else:
            self.help = cstr("[#] ").green() + self.help
            
        # additionnal help depending on type
        if self.is_bool:
            self.help += f" ({cstr('1=True'):b}, {cstr('0=False'):b})"
        
        if self.is_list:
            self.help += f" ({cstr('comma-separated'):b}, {cstr('no spaces'):b}, eg. '--varname=val1,val2' or '--varname=val1')"
        
        
        
        self.help += f" ({cstr(f'{self.typ.__name__}'):b})"
        
        # default value
        if self.default is not None:
            self.help += f" [default: {cstr(f'{self.default!r}'):c}]"
        
         
    def _check_arg_compatible(self) -> None:
        """
        Called by __init__ function to check if the arguments are compatible with each other.
        """
        
        # typ is valid type
        assert self.typ in [str, int, float, bool, list, None], f"Invalid type {self.typ}. Must be one of [str, int, float, bool, list, None]"
        
        # make conversion int to float if necessary
        if self.typ == float and isinstance(self.default, int):
            self.default = float(self.default)
        
        # default and choices match typ
        if self.typ != None:
            assert self.default is None or \
                isinstance(self.default, self.typ), f"Default value {self.default!r} is not of type {self.typ.__name__!r}, but {type(self.default).__name__!r}"
            assert self.choices is None or \
                all(isinstance(choice, self.typ) for choice in self.choices), f"Choices {self.choices} are not of type {self.typ.__name__!r}, but [{', '.join([repr(type(choice).__name__) for choice in self.choices])}]"
            
        # default is in choices or is None
        assert self.choices is None or self.default is None or \
            self.default in self.choices, f"Default value {self.default!r} is not in choices: {self.choices}"
            
        
        
    def __str__(self) -> str:
        return f"--{self.varname}"

    def __repr__(self) -> str:
        return f"<FancyArg(varname:{self.varname}; required:{self.required})>"
    
    def _add(self) -> None:
        """
        Called by __init__. Add self to the argument parser initialized by FancyArg.set_description(description:str)
        """
        
        args = {
            "required": self.required,
        }
        
        args["type"] = self.typ
            
        if self.choices is not None:
            args["choices"] = self.choices
        
        if self.default is not None:
            args["default"] = self.default
        
        args["help"] = self.help
            
        FancyArg.parser.add_argument(
            str(self),
            **args
        )
        
        FancyArg.fancy_args.append(self)
        
    
    ##############
    ### PARSER ###
    ##############
    
    @staticmethod
    def reset() -> None:
        """
        Resets the parser, usefull when running subprocess without changing global namespace.
        """
        FancyArg.parser = None
        FancyArg.fancy_args = []
        FancyArg.out_list = None
        FancyArg.out_dict = None
        FancyArg.last_return = None
        Message("Parser reset.", "#")
    
    @staticmethod
    def create(description:str, show_help:bool = True):
        """
        Initializes the parser with a description.
        
        Returns:
            context manager that runs the parser at the end of the block.
        """
        assert FancyArg.parser is None, "FancyArg parser already initalized. Cannot initialize it twice! Call FancyArg.reset() toerase previous FancyArg instances."
        FancyArg.parser = ArgumentParser(description=description)
        
        # provide help message
        if show_help:
            Message("Argument parser initialized.", "#")
            with Message.tab():
                Message.print(f"Run {cstr('python ' + os.path.basename(sys.argv[0]) + ' -h'):g} for more information.")
                cmd1 = '--varname=-1'
                cmd2 = '--varname=-300,300,601'
                Message.print(f"When working with negative numbers, '-' signs in front of numbers can raise exceptions. Use equal signs: {cstr(cmd1):g} or {cstr(cmd2):g} for lists.")
            Message.par()
        
        class FancyArgContextManager:
            def __enter__(self):
                pass
            
            # handel exceptions
            def __exit__(self, exc_type, exc_value, traceback):
                if exc_type is not None:
                    raise(exc_type(exc_value))
                FancyArg.print()
        
        return FancyArgContextManager()

    
    @staticmethod
    def parse(return_list:bool = True) -> ArgumentParser:
        """
        If called mutliple times, will returned the results stored on the first call.
        
        Args:
            return_list (bool): If True, returns a list of values. If False, returns a dictionary of values (with keys being the names of the variables).
        
        Returns:
            in case of a list, the arguments in order of creation of the fancyargs. In case of a dictionary, the arguments with the names of the variables as keys.
        """
        if FancyArg.out_list is not None: # has already been computed
            return FancyArg.out_list if return_list else FancyArg.out_dict
        
        assert FancyArg.parser is not None, "FancyArg parser not initialized, call FancyArg.set_description('...') first"
        
        args = FancyArg.parser.parse_args()
                
        # let's update the parser argument
        out_list = []
        out_dict = {}
        
        for fancy_arg in FancyArg.fancy_args:
            varname = fancy_arg.varname
            value = getattr(args, varname)
            
            if fancy_arg.is_bool:
                assert value in ["0", "1", "True", "False"], f"Unexpected value for boolean argument {varname!r}: {value!r}"
                if value in ["0", "False"]:
                    value = False
                else:
                    value = True
                
            if fancy_arg.is_list:
                value = value.split(",") if value != "" else []
                
            out_list.append(value)
            out_dict[varname] = value
            
        FancyArg.out_list = out_list
        FancyArg.out_dict = out_dict
        
        return out_list if return_list else out_dict

    @staticmethod
    def get() -> list:
        """
        Returns the arguments parsed by FancyArg.parse() as a list. The output is in the order of creation of the arguments.
        If only one argument, return the argument and not a list.
        
        Example:
            >>> A,B,C = FancyArg.get() # use if threee arguments
            >>> A = FancyArg.get() # use if only one argument
        """
        out = FancyArg.parse(return_list=True)
        return out[0] if len(out) == 1 else out
    
    @staticmethod
    def print() -> None:
        """
        Show the arguments once parsed. If not already parsed, FancyArg.parse() is called.
        """
        if FancyArg.out_list is None:
            FancyArg.parse()
        
        Message(f"Arguments parsed ({cstr(os.path.basename(sys.argv[0])):g}):","#")
        with Message.tab():
            for fancy_arg, value in zip(FancyArg.fancy_args, FancyArg.out_list):
                Message(
                    f"{fancy_arg.varname}: {cstr(repr(value)):c} ({type(value).__name__})"
                )
    
    @staticmethod
    def subprocess(pythonfile:str, args:dict = {}, mute:bool=False):
        """
        Runs a subprocess with the given arguments. The arguments are passed to subprocess with the following format:
        python filepath --{key}={value}. All values will be converted tostrings first.
        Lists are passed as comma-separated strings, without spaces.
        
        Args:
            pythonfile (str): Path to the python file to run.
            args (dict): The arguments to pass to the python file. Will all be converted to strings before being passed to subprocess.
            mute (bool): If True, mutes the messages and tasks while running the subprocess. Once the subprocess is done, the messages and tasks are unmuted.
        """
        assert os.path.isfile(pythonfile), f"File {cstr(pythonfile):r} does not exist."
        assert pythonfile.endswith(".py"), f"File {os.path.basename(cstr(pythonfile)):r} is not a python file."
        FancyArg.reset() # we are about to launch a nw script with new arguments and a new parser
        
        for key in list(args.keys()): # parse the types
            if isinstance(args[key], list):
                args[key] = [str(val) for val in args[key]]
                args[key] = ",".join(args[key])
            elif isinstance(args[key], bool):
                args[key] = str(int(args[key]))
            elif isinstance(args[key], int) or isinstance(args[key], float):
                args[key] = str(args[key])
        
        cmd = f"python {cstr(pythonfile):c} " + " ".join([f"--{key}={value}" for key, value in args.items()])
        Message("Running command:")
        with Message.tab():
            Message.print(cmd)
        Message.par()
            
        #subprocess.run([
        #    "python", pythonfile,
        #    *[f"--{key}={value}" for key, value in args.items()]
        #], check=True) # we don't want to run subprocess anymore, because doing the improts all the time takes time, with runpy we can run in the same namespace and avoid that
        
        # first we have to reset the parser since we are calling a new script, that will probably contain a parser itself
        
        
        # now we pass on the arguments to argv
        
        original_argv = sys.argv
        try:
            if mute:
                Message.mute()
                Task.mute()
                FancyIterator.mute()
                
            sys.argv = [pythonfile] + [f"--{key}={value}" for key, value in args.items()]
            
            with Task("Running subprocess with the same namespace...", new_line=True):
                try:
                    runpy.run_path(pythonfile, run_name='__main__')
                except SystemExit as e:
                    if e.code != 0 and e.code is not None:
                        raise RuntimeError(f"Error while running subprocess {cstr(pythonfile):r}.")
                
        except Exception as e:
            raise RuntimeError(f"Error while running subprocess {cstr(pythonfile):r}:\n{e}")
        finally:
            # restore the original one, just in case it is important
            sys.argv = original_argv
            
            if mute:
                Message.unmute()
                Task.unmute()
                FancyIterator.unmute()
    
    @staticmethod
    def set_return(value) -> None:
        """
        When running subprocess, it might be usefull, inside the subprocess, to return something. You can do this by calling this function.
        
        Args:
            value: The value to return. Can be anything. Will set the FancyArg.last_return attribute. This value can be accessed from the parent script by method get_return().
        """
        Message(f"Return value set from subprocess {cstr(sys.argv[0]):c}", "i")
        FancyArg.last_return = value
    
    @staticmethod
    def pop_return():
        """
        Returns the value set by FancyArg.set_return(value) in the subprocess. Raise an exception if no value has been set.
        Once this function is called, the value is reset to None.
        """
        assert not FancyArg.last_return is None, "No return value set by subprocess!"
        out, FancyArg.last_return = FancyArg.last_return, None
        return out
        
        
    


if __name__ == "__main__":
    
    # 1. Initialize the parser
    
    with FancyArg.create("Model the atmosphere of a planet (test)"):
        FancyArg("planet", help="The planet to model", type=str, choices=["b", "c"])
        FancyArg("T", help="Temperature to use (K)", type=int)
        FancyArg("species", help="Species to model", type=list, default=["H2O"])
        FancyArg("log_g", help="Log(g) to use", type=float, default=4.18)
        FancyArg("show", help="Show plots or not", type=bool, default=False)
    
    
    
        
    
        