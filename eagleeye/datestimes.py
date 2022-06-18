import datetime
import time
from typing import Union



def get_timestr() -> str:
    offset = datetime.timedelta(hours=3)
    dt = datetime.datetime.now(tz=datetime.timezone(offset, 'MSC'))
    dt = list(map(str, dt.timetuple()[3:6]))
    dt = list(map(lambda x: f'0{x}' if len(x) == 1 else x, dt))
    return ':'.join(dt)



class Timer:
    def __init__(self, interval: Union[float, int]) -> None:
        self.interval = interval
        self.start_time = 0
        self.__ACTIVE = False
    
    @property
    def state(self) -> bool:
        return self.__ACTIVE
    
    @property
    def start(self) -> bool:
        if not self.__ACTIVE:
            self.start_time = time.time()
            self.__ACTIVE = True
            return True
        return False
    
    @property
    def stop(self) -> bool:
        if self.__ACTIVE:
            current_time = time.time()
            if current_time-self.start_time >= self.interval:
                self.__ACTIVE = False
                return True
        return False
    










