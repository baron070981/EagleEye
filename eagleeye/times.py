import datetime
import time

from rich import print, inspect


class mTime:

    def __init__(self, hour=0, minute=0):
        self.hour = hour
        self.minute = minute
    
    def __str__(self):
        return f'mTime({self.hour} {self.minute})'

    @property
    def time(self):
        return self

    @time.setter
    def time(self, value:tuple):
        self.hour = value[0]
        self.minute = value[1]
    
    def __eq__(self, other):
        """
        other: mTime or tuple
        """
        if isinstance(other, tuple):
            return self.hour == other[0] and self.minute == other[1]
        return self.hour == other.hour and self.minute == other.minute
    
    def __ne__(self, other):
        """
        other: mTime or tuple
        """
        if isinstance(other, tuple):
            return self.hour != other[0] or self.minute != other[1]
        return self.hour != other.hour or self.minute != other.minute

    def __lt__(self, other):
        ...


class Timer:

    def __init__(self, interval=0.1):
        self.__interval = interval
        self.last_time = None
        self.__start = False

    @property
    def interval(self):
        return self.__interval
    
    @interval.setter
    def interval(self, value):
        self.__interval = value

    @property
    def is_start(self):
        return self.__start


    def start(self):
        self.__start = True
        return self.__start
    
    
    def stop(self):
        self.__start = False
        self.last_time = None
        return self.__start

    def signal(self):
        if not self.__start:
            return False
        if not self.last_time:
            self.last_time = time.monotonic()
        t = time.monotonic()
        if t - self.last_time >= self.__interval:
            self.last_time = t
            return True
        return False


class Clock:

    def __init__(self, time1: tuple, time2: tuple|None=None):
        self.__time1 = time1
        if time2 is None:
            m = time1[1]+1 if time1[1] < 59 else 0
            self.__time2 = (time1[0], m)
        else: self.__time2 = time2
        self.__time_state = 0
        self.__active = False
    
    @property
    def time1(self):
        return self.__time1

    @time1.setter
    def time1(self, t:tuple):
        self.__time1 = t
    
    @property
    def time2(self):
        return self.__time2

    @time2.setter
    def time2(self, t:tuple):
        self.__time2 = t
    
    def start(self):
        self.__active = True
    
    def stop(self):
        self.__active = False
        self.__time_state = 0
    
    def is_active(self):
        return self.__active
    
    def signal(self, stop: bool=False):
        if self.__active:
            sec = time.time()
            tm = time.localtime(sec)
            ch, cm = tm.tm_hour, tm.tm_min
            h1, m1 = self.__time1
            h2, m2 = self.__time2
            hours_1 = []
            if h2 < h1:
                hours_1 = list(range(h1+1, 24)) + list(range(0, h2))
            else:
                hours_1 = list(range(h1+1, h2))
            if ch in hours_1:
                return 1
            elif ch == h1 and cm >= m1 and cm < m2:
                return 1
            elif ch == h2 and cm >= m2:
                return 2
        return 2
            

    
    


def get_datetimestr():
    """
    получение строки с датой и временем
    формата дд.мм.гггг чч:мм:сс
    """
    dt = datetime.datetime.today()
    return datetime.datetime.strftime(dt, '%d-%m-%Y %H:%M:%S')

def get_timestr() -> str:
    """
    получение строки с временем
    формата чч:мм:сс
    """
    dt = datetime.datetime.today()
    return datetime.datetime.strftime(dt, '%H:%M:%S')


if __name__ == "__main__":
    cnt = 1

    c = Clock((18, 37), (18, 38))
    c.start()
    while True:
        if c.signal() == 2:
            print('Putoff, break')
            break
        elif c.signal() == 1:
            print('On', end='\t')
        time.sleep(1)
        print(time.time() % 100)



