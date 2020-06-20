# !/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
import cv2
import os
import sys
import numpy as np
from PIL import Image
from pprint import pprint
import time
from random import randint
import shutil

import FramesProcessing
import DataVisualization


'''
1. при запуске сделать n снимков с интервалом 10 сек.
2. после интервал между сниками увеличивается до т1, проверяется есть ли лицо
3. при обнаружении лица делается несколько снимков с меньшим интервалом т2
4. интервал снова увеличивается до т1

'''


home = os.path.abspath(os.path.dirname(__file__)) # путь к скрипту
data_dir = home+'/imgs' # путь к изображениям


def write_frame(frame, filename, limit_image = 1, cnt_image = 0, flag = False):
    # frame - кадр
    # filename - полное имя файла
    # limit_image - какое число изображений подряд сохранить
    # cnt_frames - счетчик сохраненных изображений
    # flag - разрешение для записи, если True, то запись разрешена
    cnt = cnt_image
    if flag:
        cnt += 1
        cv2.imwrite(filename, frame)
        print('Сохранение файла:', filename)
        if cnt >= limit_image:
            print('...Сброс флага в False')
            cnt = 0
            flag = False
    return cnt, flag


def create_filename(path_to_dir, additive, execut = '.jpg'):
    now = datetime.today()
    filename = now.strftime('%d%m%y_%H%M%S_')+str(additive)+'.jpg'
    return path_to_dir+'/'+filename
    



if __name__ == '__main__':
    img_dir = 'images'
    
    try:
        print('Директория удалена')
        shutil.rmtree(img_dir)
    except:
        print('Директория не найдена')
    
    os.makedirs(img_dir, exist_ok=True)
    fp = FramesProcessing.FramesProcess(3,15) # создаю экземпляр класса
    vd = DataVisualization.VisualData()
    
    vd.set_config(300,550,[0,0,0])
    histo = vd.set_bgimage()
    
    
# ======================================================================
    cnt_image = 0
    frames_ok = False
    framescnt = 0 # счетчик кадров
    cap = cv2.VideoCapture(-1)
    #cv2.namedWindow('camera')
    cv2.namedWindow('histo')
    t2 = 0
    old_array = [0]
    new_array = [0]
    while True:
        ret, frame = cap.read()
        frame = cv2.flip(frame, 1)
        histo = vd.set_bgimage()
        
        framescnt += 1 # подсчет кадров
        key = cv2.waitKey(10)
        
        if key == 13:
            cap.release()
            cv2.destroyAllWindows()
            break
        
        image = fp.create_image_gray(frame) # gray frame
        y, x = image.shape 
        
        if not fp.issizes(y, x):
            print('Issizes False')
            fp.t__get_new_sizes(480, 640)
            fp.t__get_size_to_sections(480, 640)
            fp.get_coords()
        
        image_rc = fp.resize(image, 'rc')
        sections_col = fp.get_sections_quad(image_rc, fp.coord_array_col)
        sections_row = fp.get_sections_quad(image_rc, fp.coord_array_row)
        aver_col = fp.average(sections_col)
        aver_row = fp.average(sections_row)
        new_array = aver_col
        
        histo = vd.bar_graph_image2( frame, [aver_col, aver_row], 
                                     [[250,10,0],[20,250,5]], rotate=0  )
        
        if framescnt >= 30:
            print('Сброс счетчика кадров и установка флага в True')
            frames_ok = True
            framescnt = 0
        
        # проверка  движения
        if fp.get_diff_arrays_bool(new_array, old_array, 30, 30):
            filename = create_filename('images', cnt_image)
            cnt_image, frames_ok = write_frame(histo, filename, 3, cnt_image, frames_ok)
            
        
        #cv2.imshow('camera', image)
        cv2.imshow('histo', histo)
        
    
    
    
    
# ======================================================================
    
    cv2.waitKey(0)
    cv2.destroyAllWindows()











