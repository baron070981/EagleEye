import os, os.path
from pathlib import Path
import shutil
from typing import Union
import csv


settings_filename = Path(Path(__file__).resolve().parent, 'settings.csv')
print(settings_filename)

class SettingsFile:
    
    def __init__(self, path_to_file: Union[Path, str], filename: str, data: dict):
        self.fullfilename = settings_filename
        self.keys = list(data.keys())
        self.values = list(data.values())
        self.data = data
    
    
    def read(self):
        ...
    
    
    def write(self, key, val=None, mode='w', new_key=False):
        ...
        
    
    
    def update(self, data: dict):
        ...






if __name__ == "__main__":
    ...





