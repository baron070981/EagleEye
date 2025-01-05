from pathlib import Path 
from abc import ABC
from datetime import datetime
import time
from dataclasses import dataclass


from rich import print, inspect


# переменные с путями к базе и архиву
# удаление из базы и архива
# перенос из базы в архив
# удаление с конца
# полное удаление из базы и из архива

@dataclass
class DefaultsValues:
    num_get_photos:int = 5
    num_del_photos:int = 5
    num_arch_photos:int = 5


class BaseDirectory(ABC):
    def __init__(self, path):
        # super().__init__()
        self.path = Path(path)


class Directory(BaseDirectory):

    def __init__(self, path: str|Path):
        self.__path = Path(path)
    
    def __find(self, *ext) -> filter:
        if not ext: return filter(lambda x: x, self.__path.iterdir())
        files = filter(lambda x: x.is_file(), self.__path.iterdir())
        files = filter(lambda x: x.suffix in ext, files)
        return files
    
    @property
    def stat(self):
        files = list(self.__find())
        return f'Files num: {len(files)}'
    
    @property
    def count_files(self):
        files = list(self.__find())
        return len(files)
    
    def files(self, *exts):
        return sorted(self.__find(*exts), key=lambda x: x.stat().st_ctime, reverse=False)

    @property
    def path(self):
        return self.__path

    # def delete(self, *exts, num_del:int|None=None):
    #     files = sorted(self.__find(), key=lambda x: x.stat().st_ctime)
    #     if not files: return
    #     if num_del is None or num_del <= 0:
    #         for f in files:
    #             f.unlink(missing_ok=True)
    #         return
    #     files = files[:num_del]
    #     for f in files:
    #         f.unlink(missing_ok=True)
        
    def moves(self, new_dir:BaseDirectory|str|Path, *exts, move_num:int=0):
        if move_num <= 0: return
        if isinstance(new_dir, str):
            new_dir = Path(new_dir)
        elif isinstance(new_dir, BaseDirectory):
            new_dir = new_dir.path
        files = sorted(self.__find(*exts), key=lambda x: x.stat().st_ctime)[:move_num]
        for f in files:
            print('In mioves:', f)
            f.rename(new_dir/f.name)
    
    @staticmethod
    def moves_files(new_dir:BaseDirectory|str|Path, files:list|None=None):
        if not files: return
        if isinstance(new_dir, str):
            new_dir = Path(new_dir)
        elif isinstance(new_dir, BaseDirectory):
            new_dir = new_dir.path
        for f in files:
            if isinstance(f, str):
                f = Path(f)
            f.rename(new_dir/f.name)
    
    @staticmethod
    def delete(files:list):
        for f in files:
            if isinstance(f, str):
                f = Path(f)
            f.unlink(missing_ok=True)
    
    def clear(self, *exts, num_files:int|None=None, side:int=0):
        exts = ['.jpg', '.jpeg'] + list(exts)
        if num_files:
            files = self.files(*exts)[:num_files] if side == 0 else self.files(*exts)[-num_files:]
            [f.unlink() for f in files]
            return
        files = self.files(*exts)
        [f.unlink() for f in files]

        











if __name__ == "__main__":
    ...
    base = '/home/baron/coding/Python/EagleEye/tbot/test_save'
    archive = '/home/baron/coding/Python/EagleEye/tbot/test_archive'
    
    save_dir = Directory(base)
    archive_dir = Directory(archive)

    
    


