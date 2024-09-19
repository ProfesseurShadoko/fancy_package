

# Personal Library imports
from .fancy_print import Message, Task, FancyIterator as FancyIter, cstr, TempFolder
from .fancy_args import FancyArg


# Classic imports
import os
import sys
import shutil
import numpy as np
import scipy as sp
import pandas as pd
import matplotlib.pyplot as plt
import time

pd.set_option('future.no_silent_downcasting', True)
plt.rcParams['font.size'] = 14

# AstroPy
import astropy.units as u
import astropy.constants as astro_const
from astropy.io import fits


# PRT
from petitRADTRANS.radtrans import Radtrans
from petitRADTRANS import physical_constants as prt_const
from petitRADTRANS.physics import temperature_profile_function_guillot_global
from petitRADTRANS.chemistry.utils import volume_mixing_ratios2mass_fractions


# Utils functions
from .cross_correlation_tools import cross_correlate, plot_ccf, ccf_mask, weighted_correlation
from .velocity_correction import Velocity
from .rotational_broadening import intRotBroad, rotBroad, fastRotBroad, instrGaussBroad
from pybaselines import Baseline


def hash_fname(filepath:str) -> int:
    """
    Transforms a filename (or any string) into a 'unique' integer.
    """
    length = len(filepath)
    slash_count = filepath.count('/')
    letter_count = filepath.count('b')
    charsum = sum([ord(c) for c in filepath])
    return (length * 31 + slash_count * 41 + letter_count * 59 + charsum * 26)%535


import pyperclip

def suggest_next_command(pythonfile:str, args:dict) -> None:
    """
    Creates next command to run and copies to clipboard. Arguments are formatted depending on their types. List are joined with commas, booleans are converted to 0 or 1, and ints and floats are converted to strings.
    """
    
    # first lets format the right command
    for key in list(args.keys()): # parse the types
            if isinstance(args[key], list):
                args[key] = [str(val) for val in args[key]]
                args[key] = ",".join(args[key])
            elif isinstance(args[key], bool):
                args[key] = str(int(args[key]))
            elif isinstance(args[key], int) or isinstance(args[key], float):
                args[key] = str(args[key])
        
    cmd = f"python {pythonfile} " + " ".join([f"--{key}={value}" for key, value in args.items()])
    
    Message(f"Suggested next command ({cstr(pythonfile):c}):")
    with Message.tab():
        Message.print(cmd)
        
    pyperclip.copy(cmd)
    Message("This command has been copied to your clipboard.", "#")
    
   
