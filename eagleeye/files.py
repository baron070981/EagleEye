from pathlib import Path
import datetime
import time
import os.path, os
import cv2
import random
import re


try:
    from . import textprocessing as tp
    from . import datestimes as dt
except:
    import textprocessing as tp
    import datestimes as dt




class SaveDirectiory:
    
    def __init__(self, files_dir,  max_files=100, type_size='num'):
        self.files_dir = files_dir
        self.dirs = Path(Path(__file__).resolve().parent, files_dir)
        self.__create_dir(self.dirs)
        self.__filenames = self.__get_files()
        self.__count = self.__get_count()
        self.type_size = type_size
        self.__max_files = max_files
    
    
    def __create_dir(self, dirname):
        # создание папки для сохранения если ее нет
        if not dirname.is_dir():
            print('Create Directory')
            dirname.mkdir()
    
    
    def __get_files(self):
        # получение списка имен файлов из заданной папки
        filenames = os.listdir(self.dirs)
        filenames = list(map(lambda x: self.dirs/x, filenames))
        pattern = r'\w+_\d+\.\w+'
        filenames = list(filter(lambda x: re.match(pattern, x.name) is not None, filenames))
        filenames = sorted(filenames, key=lambda x: int(str(x).split('_')[-1].split('.')[0]))
        return list(map(Path, filenames))
    
    
    def __get_count(self):
        # получение максимального номера из имен файлов
        if not self.__filenames:
            return 0
        filenames = list(map(lambda x: x.stem, self.__filenames))
        filenames = sorted(filenames, key=lambda x: int(x.split('_')[-1]))
        name = filenames[-1]
        try:
            count = name.split('_')[-1]
            tp.TextInfo.add(f'Максимальный Id: {count}')
            return int(count)
        except Exception as err:
            print('In Files.get_count:\n  ', err)
            raise Exception(err)
    
    
    def create_filename(self, ext='.jpg'):
        # создание имени файла и прибавление self.__count на единицу
        offset = datetime.timedelta(hours=3)
        dt = datetime.datetime.now(tz=datetime.timezone(offset, 'MSC'))
        dt = list(map(str, dt.timetuple()[:6]))
        dt = list(map(lambda x: f'0{x}' if len(x) == 1 else x, dt))
        self.__count += 1
        return self.dirs.joinpath(''.join(dt)+'_'+str(self.__count)+ext)
    
    
    def update(self):
        self.__filenames = self.__get_files()
    
    
    @property
    def __check_size_nums(self):
        return len(self.__filenames) <= self.__max_files
    
    
    @property
    def __get_size_byte(self):
        sizes = list(map(lambda x: os.path.getsize(str(x)), self.__filenames))
        return sum(sizes)
    
    
    def correct_size_directiory(self):
        self.__filenames = self.__get_files()
        if self.type_size == 'num':
            if not self.__check_size_nums:
                self.__filenames[0].unlink()
                tp.TextInfo.add('Размер директории больше заданного. Удаление файла.')
        elif self.type_size == 'mb':
            sizes = self.__get_size_byte/1024/1000
            sum_size = 0
            del_files = []
            if sizes > self.__max_files:
                for i in range(len(self.__filenames)):
                    del_files.append(self.__filenames[i])
                    if self.__get_size_byte/1024/1000 - sum(list(map(lambda x: os.path.getsize(str(x)), del_files))):
                        tp.TextInfo.add(f'Удаление {len(del_files)} файлов.')
                        [f.unlink() for f in del_files]
                        break
        else:
            raise Exception('Неверно передан параметр type_size....')
        self.update()
    
    
    
    


class SaveFrames:
    
    def __init__(self, files_dir, max_files=100, interval=0.8, num_save=2, type_size='num'):
        # files_dir - папка для сохранения фото 
        # max_files - максимальное кол-во сохраненных фото
        #             при превышении удаляется самое старое фото
        # interval - время между двумя снимками. пока не кончится, седующий снимок не сделается
        self.f_obj = SaveDirectiory(files_dir, type_size=type_size, max_files=max_files)
        self.SAVE = True
        self.interval = interval
        self.timer = dt.Timer(interval)
        self.times = []
        self.num_save = num_save
        self.stack_saves = []
        self.time_start = None
    
    
    def __correct(self):
        # проверка и контроль чтоб длина списка времен сохранения
        # не была больше кол-ва сохраняемых файлов
        self.times = self.times if len(self.times) <= self.num_save else self.times[-self.num_save:]
    
    
    def is_interval(self) -> bool:
        # поверка интервала времени последних заданного числа сохранений
        self.__correct()
        if len(self.times) < self.num_save:
            return True
        deffs = [] # разности времен сохранения
        for i in range(1, len(self.times)):
            deffs.append(self.times[i]-self.times[i-1])
        return sum(deffs) >= (self.num_save)*self.interval
    
    
    def save(self, frame):
        # если разрешено сохранять
        if self.SAVE:
            # создание имени файла
            filename = self.f_obj.create_filename()
            # добавление строки сообщения
            tp.TextInfo.add(f'Сохранение: {filename.name}')
            # сохранение файла
            cv2.imwrite(str(filename), frame)
            # обновление списка файлов
            self.f_obj.update()
            # добавление времени сохранения
            self.times.append(time.time())
            # удаление лишних файлов если их больше заданного кол-ва
            self.f_obj.correct_size_directiory()
            self.SAVE = False
            # запуск таймера между сохраняемыми кадрами
            self.timer.start
            self.time_start = time.time()
        # проверка прошедшего времени и остановка таймера
        # разрешение на сохранение
        if self.timer.stop:
            tp.TextInfo.add(f'Прошло {time.time()-self.time_start}')
            self.SAVE = True
    
    
    def add_stack(self, frame):
        if self.SAVE:
            filename = self.f_obj.create_filename()
            self.stack_saves.append((filename, frame))
            tp.TextInfo.add(f'Добав. в стек: {filename.name}')
            self.times.append(time.time()-0.15)
            self.SAVE = False
            self.timer.start
            self.time_start = time.time()
        if self.timer.stop:
            tp.TextInfo.add(f'Прошло {time.time()-self.time_start}')
            self.SAVE = True
    
    def save_from_stack(self):
        if self.stack_saves:
            filename, frame = self.stack_saves[0]
            cv2.imwrite(str(filename), frame)
            tp.TextInfo.add(f'Сохр. из стека: {filename.name}')
            self.f_obj.correct_size_directiory()
            self.stack_saves.pop(0)
    
    @property
    def len_stack(self):
        return len(self.stack_saves)
    
    
    @property
    def reset_times(self):
        self.times = []
    
    
    def update_interval(self, interval):
        if interval != self.interval:
            self.interval = interval
            self.timer.interval = self.interval
            self.reset_times
    
    
class SettingsFile:
    
    fields = []
    
    def __new__(self):
        ...
    
    def __init__(self):
        ...
    
    
    def read(self):
        ...
    
    
    def write(self, **kwargs):
        ...
    
    
    def update(self, key, val):
        ...






if __name__ == "__main__":
    fobj = SaveFrames('test_save', interval=0.9)
    timer = Timer(5)
    for i in range(100):
        if fobj.is_interval():
            fobj.save(1)
        else:
            print('Timer start in main cycle')
            timer.start
        if timer.stop:
            print('Timer stop in main cycle')
            fobj.reset_times
        time.sleep(.100)









