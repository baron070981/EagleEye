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



def write_frame(frame, filename, cnt, limit, num_frame = 1):
    if cnt <= num_frame-1:
        print('Write image:', filename)
        cv2.imwrite(filename, frame)
    cnt = cnt + 1
    if cnt >= limit:
        return 0
    return cnt




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
    cnt = 0
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
        
        if fp.get_diff_arrays_bool(new_array, old_array, 10, 7):
            filename = img_dir+'/'+str(randint(1000, 100001))+'.jpg'
            cnt = write_frame(histo, filename, cnt, 100, 3)
            old_array = new_array.copy()
            print(' Заданная разница определена...', cnt)
        cnt += 1
        
        
        #cv2.imshow('camera', image)
        cv2.imshow('histo', histo)
        
    
    
    
    
# ======================================================================
    
    cv2.waitKey(0)
    cv2.destroyAllWindows()











