import numpy as np
from rich import print, inspect
import cv2
import sys
from pathlib import Path
import datetime

import frameproc
import defaults as dfl
import times
import file


def get_percent_diff(val1, val2):
    val1, val2 = sorted([val1, val2])
    if val2 == 0: return 0
    return 100 - val1 / val2 * 100




ROOT = Path(__file__).parent

SAVES = ROOT / 'saving'

SAVES.mkdir(exist_ok=True)

coords = []
w, h, hs, vs, sect_size = None, None, None, None, None
num_sections = None
current_means = []
last_means = []
diff_percents = []
text = '0.0'

limnit_diff_sections = 10
limit_count_diffs = 8

vars = dfl.DefVals()

timer_between_save = times.Timer(vars.INTERVAL_BETWEEN_SAVES)
timer_sleep = times.Timer(vars.SLEEP)

COUNT_SAVES = 0

IS_SIGNAL = False
SLEEP_SIGNAL_COUNT = 0

camera = cv2.VideoCapture(2)
cv2.namedWindow('видеопоток')
cv2.namedWindow('save')

frame_out = None
proc_image = None
save_image = None
save_image_out = None

frame_out_size = None
save_image_size = None
save_image_out_size = None
proc_image_size = None



while True:
    is_frame, frame = camera.read()
    if not is_frame:
        break
    frame = cv2.flip(frame, 1)

    if frame_out is None:
        frame_out_size = frameproc.get_new_size(frame, *vars.FRAME_OUT_SIZE)
    frame_out = cv2.resize(frame, frame_out_size)
    text = times.get_datetimestr()
    cv2.putText(frame_out, text, (10, frame_out.shape[0]-20), cv2.FONT_HERSHEY_PLAIN, 1.7, (50, 50, 255), 2)

    if save_image is None:
        save_image_size = frameproc.get_new_size(frame, *vars.SIZE_SAVE_IMAGE)

    if save_image_out is None:
        save_image_out_size = frameproc.get_new_size(frame, *vars.OUT_SAVE_FRAME_SIZE)
        save_image_out = np.zeros(save_image_out_size[::-1], dtype='uint8')
    
# ==========================================
    # если орбрабатываемое изображение еще не создано
    if proc_image is None: 
        proc_image_size = frameproc.get_new_size(frame, *vars.PROC_FRAME_SIZE)
        proc_image_size, num_sections, sect_size = frameproc.calculate_sections(proc_image_size, num_sections=vars.NUM_SECT)
        coords = frameproc.coord_sections(proc_image_size, num_sections[0], num_sections[1], sect_size)
    
    proc_image = cv2.resize(frame, proc_image_size)
    proc_image = cv2.cvtColor(proc_image, cv2.COLOR_BGR2GRAY)
    proc_image = cv2.GaussianBlur(proc_image, vars.GAUSIAN_KERNEL, 0)
    

    current_means = []
    diff_percents = [0]

    for i, (x1, y1, x2, y2) in enumerate(coords):
        # cv2.rectangle(proc_image, (x1, y1), (x2, y2), (50, 50, 50), 1)
        current_mean_value = proc_image[y1:y2, x1:x2].mean()
        current_means.append(current_mean_value)
        if last_means:
            last_mean_value = last_means[i]
            diff = get_percent_diff(last_mean_value, current_mean_value)
            diff_percents.append(diff)

    only_limit_diffs = list(filter(lambda x: x >= vars.DIFF_PERC_SECT, diff_percents))
    percent_sections = len(only_limit_diffs) / len(diff_percents) * 100
    last_means = current_means.copy()


    if percent_sections > vars.PERC_COUNT_DIFFS and not timer_between_save.is_start and not timer_sleep.is_start:
        save_image_out = cv2.resize(frame_out, save_image_out_size)
        save_image = cv2.resize(frame_out, save_image_size)
        filename = SAVES / file.get_file_name(COUNT_SAVES, SAVES)
        cv2.imwrite(filename, save_image)
        COUNT_SAVES += 1
        timer_between_save.start()
    
    is_save = timer_between_save.signal()
    if is_save:
        save_image_out = cv2.resize(frame_out, save_image_out_size)
        save_image = cv2.resize(frame_out, save_image_size)
        filename = SAVES / file.get_file_name(COUNT_SAVES, SAVES)
        cv2.imwrite(filename, save_image)
        COUNT_SAVES += 1

    if COUNT_SAVES >= vars.NUM_SAVE_IMAGES:
        timer_between_save.stop()
        COUNT_SAVES = 0
        timer_sleep.start()
    
    SLEEP_SIGNAL_COUNT += timer_sleep.signal()

    if SLEEP_SIGNAL_COUNT >= vars.INTERVAL_BETWEEN_SAVES:
        timer_sleep.stop()
        SLEEP_SIGNAL_COUNT = 0
    


    


# ==========================================

    cv2.putText(frame_out, f'{round(percent_sections,3)}', (10, 100), cv2.FONT_HERSHEY_PLAIN, 1.5, (55, 55, 255), 2)

    cv2.imshow('видеопоток', frame_out)
    cv2.imshow('save', save_image_out)
    if cv2.waitKey(1) & 0xFF == 27:
        break



cv2.destroyAllWindows()

sys.exit(0)














