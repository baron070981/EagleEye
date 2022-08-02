import cv2
import numpy as np
from skimage import io, img_as_float
import datetime

import camera
import framesprocessing
import files
import datestimes as dt


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
    
    frame = framesprocessing.Frame(50)
    cam = camera.Camera(800, camera_id=2)
    
    GET_POINTS = True
    points1 = []
    last_means = []
    changed = []
    
    while True:
        
        origin = cam.get_frame(resize=True)
        gray = cv2.cvtColor(origin, cv2.COLOR_BGR2GRAY)
        cv2.putText(origin, dt.get_timestr(), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 3)
        
        if cam.is_key(27, t=1):
            break
        
        if GET_POINTS:
            points1 = frame.get_rand_checkpoints_coords(gray.shape[:2])
            points2 = frame.get_rand_checkpoints_coords(gray.shape[:2])
            GET_POINTS = False
        
        current_means = frame.get_means(gray, 'points')
        
        last_means = current_means.copy()
        cv2.imshow('video', origin)
    
    
    
    cam.close()
















