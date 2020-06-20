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


home = os.path.abspath(os.path.dirname(__file__)) # путь к скрипту


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


# создание имени файла
def create_filename(path_to_dir, additive, extention = '.jpg'):
    # path_to_dir - путь к месту сохранения
    # additive - дополнение к имени файла, добавляется в конец имени
    # extention - расширение файла
    now = datetime.today()
    filename = now.strftime('%d%m%y_%H%M%S_')+str(additive)+extention
    return path_to_dir+'/'+filename
    



if __name__ == '__main__':
    img_dir = home+'/images' # путь к папке сохранения
    
    try:
        print('Директория удалена')
        shutil.rmtree(img_dir)
    except:
        print('Директория не найдена')
    
    # создание директории для сохранения изображений
    os.makedirs(img_dir, exist_ok=True)
    
    # создается экземпляр класса обработки кадров
    # задаются параметры - число строк, число столбцов
    fp = FramesProcessing.FramesProcess(3,15)
    
    # экземпляр класса для построения и отображения графиков
    vd = DataVisualization.VisualData()
    
    vd.set_config(300,550,[0,0,0]) # параметры изображения графиков
    histo = vd.set_bgimage() # "холст" для рисования графиков
    
    
# ======================================================================
    limit_ignore = 20 # число игнорируемых кадров
    ignore_count = 0  # счетчик игнорируемых кадров
    cnt_image = 0     # счетчик сделаных снимков
    write_ok = False  # флаг разрешения записи файла
    framescnt = 0     # счетчик кадров
    old_array = [0]   # предыдущий массив
    new_array = [0]   # новый массив
    
    cap = cv2.VideoCapture(-1)
    cv2.namedWindow('histo')
    
    while True:
        framescnt += 1 # счет кадров
        ignore_count += 1 # счет игнорируемых кадров
        
        ret, frame = cap.read()
        frame = cv2.flip(frame, 1)
        histo = vd.set_bgimage() # "холст" для рисования графиков
        
        key = cv2.waitKey(10)
        
        if key == 13:
            cap.release()
            cv2.destroyAllWindows()
            break
        
        # получается копия кадра в оттенках серого
        image = fp.create_image_gray(frame)
        y, x = image.shape 
        
        # проверка изминения размеров кадра
        # если размеры отличны от начальных
        # расчитываются новые размеры серого кадра
        # и координаты секций
        # используется в дальнейшем, если не изменятся размеры изображения
        if not fp.issizes(y, x):
            print('Issizes False')
            fp.t__get_new_sizes(480, 640)
            fp.t__get_size_to_sections(480, 640)
            fp.get_coords()
        
        # изминение размера согласно расчетам
        image_rc = fp.resize(image, 'rc')
        
        # получение массивов секций
        sections_col = fp.get_sections_quad(image_rc, fp.coord_array_col)
        sections_row = fp.get_sections_quad(image_rc, fp.coord_array_row)
        
        # получение массивов средних значений секций
        aver_col = fp.average(sections_col)
        aver_row = fp.average(sections_row)
        
        # первый массив для сравнения
        new_array = aver_col
        
        # создание графика массивов
        histo = vd.bar_graph_image2( frame, [aver_col, aver_row], 
                                     [[250,10,0],[20,250,5]], rotate=0  )
        
        # если прошло N кадров сбрасывается счетчик кадров
        if framescnt >= 80:
            print('Сброс счетчика кадров и управляющего счетчика...')
            framescnt = 0
        
        # если число игнорируеммых кадров больше N,
        # сбросить счетчик игнорируемых кадров на ноль
        # и произвести сравнения массивов
        if ignore_count > limit_ignore:
            write_ok = True # разрешить запись файла
            
            # если разница массивов соответствует заданным параметрам
            if fp.get_diff_arrays_bool(new_array, old_array, 7, 10):
                print('Сравнение массивов, массивы не равны')
                cnt_image += 1 # счет сделаных изображений
                filename = create_filename(img_dir, cnt_image, '.jpg')
                cnt_image, write_ok = write_frame(histo, filename, 3, cnt_image, write_ok)
                if write_ok == False:
                    ignore_count = 0
                    framescnt = 0
            else:
                print('   Движений нет')
        else:
            print('  Игнорируемый кадр')
        
        # второй массив
        old_array = new_array.copy()
        
        cv2.imshow('histo', histo)
        
    
    
    
    
# ======================================================================
    
    cv2.waitKey(0)
    cv2.destroyAllWindows()











