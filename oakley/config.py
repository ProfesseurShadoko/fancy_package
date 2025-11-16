
import json
import os

_default_config = {
    "terminal_width": -1, # if -1, auto-detect,
    "spinner": [],
}

# 1. Load the config.json file if it exists.
_config_path = os.path.join(os.path.dirname(__file__), 'config.json')

if not os.path.exists(_config_path):
    # if not exist create it with default settings # should not happen!
    with open(_config_path, 'w') as f:
        json.dump(_default_config, f, indent=4)

with open(_config_path, 'r') as f:
    file_config = json.load(f)
_default_config.update(file_config)


class ConfigDict(dict):

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        # directly update the config file on every change
        with open(_config_path, 'w') as f:
            json.dump(self, f, indent=4)
        
        print("[C] Config updated:", key, "=", value)


config = ConfigDict(_default_config) # put the dictionnary inside. default config contains the loaded file already.