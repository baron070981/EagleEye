import cv2
import numpy as np
from skimage import io, img_as_float
import datetime

import camera
import framesprocessing
import files


def get_mean_colors(array):
    b = array[:, :, 0].mean()
    g = array[:, :, 1].mean()
    r = array[:, :, 2].mean()
    return b, g, r


def get_timestr():
    offset = datetime.timedelta(hours=3)
    dt = datetime.datetime.now(tz=datetime.timezone(offset, 'MSC'))
    dt = list(map(str, dt.timetuple()[3:6]))
    dt = list(map(lambda x: f'0{x}' if len(x) == 1 else x, dt))
    return ':'.join(dt)


def get_perc(image_mean):
    if image_mean < 15:
        return 5
    elif 15 <= image_mean < 30:
        return 10
    elif 30 <= image_mean < 45:
        return 15
    elif 45 <= image_mean < 60:
        return 20
    elif 60 <= image_mean < 90:
        return 25
    elif 90 <= image_mean < 150:
        return 40
    else:
        return 60



if __name__ == "__main__":
    ID = 2
    # 
    frame = framesprocessing.Frame(21)
    f = files.Files('images', 1000, waiting_time=10, num_save=3)
    # 
    cam = camera.Camera(800, camera_id=ID)
    # 
    timer = files.Timer(5)
    CLEAR = False  # флаг очистки экрана от вывода движения
    last_means = None  # предыдущий кадр
    CHANGED = []
    cv2.namedWindow('img')
    while True:
        
        origin = cam.get_frame(flip=True, resize=True)
        new_frame = frame.resize(origin)
        means = frame.get_means_color(new_frame)
        cv2.putText(origin, get_timestr(), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,50,250), 2)
        if last_means:
            for i, m in enumerate(means):
                if frame.get_percentege3(m, last_means[i]) >= 19:
                    CHANGED.append(frame.coords[i])
        if len(CHANGED)/(len(means)/100) >= 8 and not CLEAR:
            cv2.imshow('img', origin)
            f.save(origin)
            if f.is_interval():
                timer.start
        if timer.stop:
            f.reset_times
                    
        last_means = means
        CLEAR = not CLEAR
        CHANGED = []
        key = cv2.waitKey(1)
        if key in (27, 13):
            cam.close()
            break
        
        # cv2.imshow('video', origin)
        
    
    cam.close()
















