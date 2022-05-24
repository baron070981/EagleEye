from pathlib import Path
import datetime
import time
import os.path, os
import cv2
import random



class Files:
    
    def __init__(self, files_dir, max_files=100, waiting_time=5, num_save=3):
        self.max_files = max_files
        self.dirs = Path(Path(__file__).resolve().parent, files_dir)
        self.__create_dir(self.dirs)
        self.filenames = self.__add_files()
        self.waiting_time = waiting_time
        self.start_time = int(time.time())
        self.num_save = num_save
        self.count_save = 0
        self.save_times = []
        self.TIMER = False
        self.count = self.get_count()
    
    
    def get_count(self):
        if not self.filenames:
            return 0
        filenames = list(map(lambda x: x.stem, self.filenames))
        filenames = sorted(filenames, key=lambda x: int(x.split('_')[-1]))
        name = filenames[-1]
        try:
            count = name.split('_')[-1]
            print(count)
            return int(count)
        except Exception as err:
            print('In Files.get_count:\n  ', err)
    
    
    def correct_length(self, arr, max_len=3):
        if len(arr) > max_len:
            print(f'Уменьшение размера массива до размера {max_len}')
            arr.pop(0)
    
    
    def __create_dir(self, dirname):
        if not dirname.is_dir():
            print('Create Directory')
            dirname.mkdir()
    
    
    def __add_files(self):
        filenames = os.listdir(self.dirs)
        return list(map(Path, filenames))
    
    
    def get_filename(self, ext='.jpg'):
        offset = datetime.timedelta(hours=3)
        dt = datetime.datetime.now(tz=datetime.timezone(offset, 'MSC'))
        dt = list(map(str, dt.timetuple()[:6]))
        dt = list(map(lambda x: f'0{x}' if len(x) == 1 else x, dt))
        self.count += 1
        return self.dirs.joinpath(''.join(dt)+'_'+str(self.count)+ext)
    
    
    def sum_deff(self, arr):
        deffs = []
        for i in range(1, len(arr)):
            deffs.append(arr[i]-arr[i-1])
        return sum(deffs)
    
    
    def start_timer(self):
        if len(self.save_times) >= self.num_save and not self.TIMER:
            print(f'Вход в футкцию start_timer')
            self.correct_length(self.save_times, self.num_save)
            if self.sum_deff(self.save_times) <= self.num_save*0.8:
                print('  Включение таймера задержки')
                self.TIMER = True
    
    
    def is_interval(self):
        if len(self.save_times) >= self.num_save and  not self.TIMER:
            self.correct_length(self.save_times, self.num_save)
            interval = (self.num_save - 1)*0.8 if self.num_save > 1 else 0.8
            if self.sum_deff(self.save_times) <= interval:
                self.TIMER = True
                print('Is interval == True')
                return True
        return False
    
    
    @property
    def reset_times(self):
        print('Reset save_times')
        self.save_times = []
        self.TIMER = False
    
    
    
    def stop_timer(self):
        if self.TIMER and int(time.time()) - int(self.save_times[-1]) >= self.waiting_time:
            self.TIMER = False
            self.save_times = [self.save_times[-1]] if self.save_times else self.save_times
            print('Таймер задержки остановлен')
    
    
    def save(self, image, filename=None):
        if len(self.filenames) > self.max_files:
            self.filenames[0].unlink()
            self.filenames.pop(0)
            print('Удаление первого файла. Превышен лимит кол-ва сохраненных файлов.')
        if not self.TIMER:
            print('Save image...', random.randint(1, 100))
            filename = self.get_filename() if filename is None else Path(filename)
            cv2.imwrite(str(filename), image)
            self.save_times.append(time.time())
            self.filenames.append(filename)
            return True
        if len(self.save_times) > self.num_save:
            self.save_times = self.save_times[-self.num_save:]
        return False


class Timer:
    def __init__(self, interval):
        self.interval = interval
        self.start_time = 0
        self.__STATE = False
    
    @property
    def state(self):
        return self.__STATE
    
    @property
    def start(self):
        if not self.__STATE:
            print('Start timer')
            self.start_time = time.time()
            self.__STATE = True
            return True
        return False
    
    @property
    def stop(self):
        if self.__STATE:
            current_time = time.time()
            if current_time-self.start_time >= self.interval:
                print('Stop timer')
                self.__STATE = False
                return True
        return False






if __name__ == "__main__":
    fl  = Files('/home/baron/Coding/MyPython/EagleEye/images/')
    f = Path('/home/baron/Coding/MyPython/EagleEye/images/', 'test.png')
    fl.get_count(f)











