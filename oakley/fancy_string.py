
from typing import Literal


class Cstr(str):
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
    
    _COLORS = {
        'green': '\033[92m',
        'blue': '\033[94m',
        'red': '\033[91m',
        'yellow': '\033[93m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'reset': '\033[0m',
        
        'bold': '\033[1m',
        'underline': '\033[4m',
        'italic': '\033[3m',
        'strikethrough': '\033[9m',
        'highlight': '\033[7m',
    }
    
    def __init__(self,string:str):
        """
        Args:
            string (str): The string to be printed in color (can also be anything that can be converted to a string using str() function)
        """
        super().__init__() # how the hell does this work???
        
    
    ##############
    ### COLORS ###
    ##############
    
    def green(self) -> 'Cstr':
        return self.__class__(
            self._COLORS["green"] + self + self._COLORS["reset"]
        )
    
    def blue(self) -> 'Cstr':
        return self.__class__(
            self._COLORS["blue"] + self + self._COLORS["reset"]
        )
    
    def red(self) -> 'Cstr':
        return self.__class__(
            self._COLORS["red"] + self + self._COLORS["reset"]
        )
    
    def yellow(self) -> 'Cstr':
        return self.__class__(
            self._COLORS["yellow"] + self + self._COLORS["reset"]
        )
    
    def magenta(self) -> 'Cstr':
        return self.__class__(
            self._COLORS["magenta"] + self + self._COLORS["reset"]
        )
        
    def cyan(self) -> 'Cstr':
        return self.__class__(
            self._COLORS["cyan"] + self + self._COLORS["reset"]
        )
        
    def white(self) -> 'Cstr':
        return self
    
    
    #############
    ### FONTS ###
    #############
    
    def bold(self) -> 'Cstr':
        return self.__class__(
            self._COLORS["bold"] + self + self._COLORS["reset"]
        )
    
    def underline(self) -> 'Cstr':
        return self.__class__(
            self._COLORS["underline"] + self + self._COLORS["reset"]
        )
    
    def italic(self) -> 'Cstr':
        return self.__class__(
            self._COLORS["italic"] + self + self._COLORS["reset"]
        )
    
    def strikethrough(self) -> 'Cstr':
        return self.__class__(
            self._COLORS["strikethrough"] + self + self._COLORS["reset"]
        )
    
    def highlight(self) -> 'Cstr':
        return self.__class__(
            self._COLORS["highlight"] + self + self._COLORS["reset"]
        )
    
    
    ##############
    ### FORMAT ###
    ##############
    
    def __format__(self, format_spec:str) -> 'Cstr':
        if not format_spec:
            return self
    
        colors = [
            'green', 'blue', 'red', 'yellow', 'magenta', 'cyan', 'white'
        ]
        fonts = [
            'bold', 'underline', 'italic', 'strikethrough', 'highlight'
        ]
        
        color_spec = format_spec[0]
        if len(format_spec) > 1:
            font_spec = format_spec[1:]
        else:
            font_spec = ''
        assert len(format_spec) <= 2, f"Invalid format specifier: {format_spec}. Must be one or two characters long."
        
        allowed_color_specs = [c[0] for c in colors]
        allowed_font_specs = [f[0] for f in fonts] + ['']
        
        assert color_spec in allowed_color_specs, f"Invalid format specifier: {format_spec}. Must be one of {allowed_color_specs}."
        assert font_spec in allowed_font_specs, f"Invalid format specifier: {format_spec}. Must be one of {allowed_font_specs}."
        
        out = self
        
        # 1. Add the color to the string
        color = [c for c in colors if c.startswith(color_spec)][0] # there is only one anyway
        out = getattr(out, color)()
        
        # 2. Add the font to the string
        if font_spec:
            font = [f for f in fonts if f.startswith(font_spec)][0]
            out = getattr(out, font)()
            
        return out


def cstr(obj:object, format_spec:str='') -> 'Cstr':
    """
    A Cstr (Colored String) is an object that inherits from str with possibility to add ANSI color codes to the string (see examples below).
    Any object can be converted to a Cstr object using this function. The possibility to use a format specifier, for floats for example, is possible. The format will be applied before converting the object into a string.
    
    Example:
        >>> x = 3.1416
        >>> print(cstr(x, '.2f').green())
        3.14 # in green
    """
    return Cstr(format(obj, format_spec))



if __name__ == '__main__':
    x = 3.1416
    print(cstr(x, '.2f').green().bold())
    print(f"This was the number PI in {cstr('green'):g} color.")
    
