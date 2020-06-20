# -*- coding: utf-8 -*-
# !/usr/bin/env python3

from datetime import datetime
import cv2
import os
import sys
import numpy as np
from pprint import pprint
import time

# создвние фона, обработка входных данных, вывод данных
# создать изображение размером Ybg x Xbg
# пересчитать координаты данных Yc и Xc для полного заполнения фона
# если Yc > Ybg масштабировать во столько раз, во сколько Ybg меньше Yc
# тоже и с другой осью


class VisualData:
    def __init__(self):
        self.bgimage = None # фоновое изображение для графиков
        self.__bgcolor = [0,0,0] # цвет фона
        self.linecolor = [255,255,255]
        self.__xsize = 100 # размер фонового изображения
        self.__ysize = 100 # размер фонового изображения
        self.len_axis = 100 # размер большей стороны изображения
        self.bgstate = False
    
    
    # свойство вывода инфо о параметрах
    @property
    def configdict(self):
        pass
    
    
    # установка параметров
    def set_config(self, ysize = 100, xsize = 100, bgcolor = [0,0,0]):
        self.__xsize = xsize
        self.__ysize = ysize
        self.__bgcolor = bgcolor
    
    
    # изменение размеров фонового изображения
    @property
    def resize_image(self):
        image_shape = self.bgimage.shape
        y, x = image_shape[0], image_shape[1]
        self.bgimage = cv2.resize(self.bgimage, (self.x_size, self.y_size))
    
    
    # установка фонового изображения
    # color-список или numpy массив из трех целых чисел
    # image - сове фоновое изображение
    def set_bgimage(self, image = None):
        if image is None:
            # создается матрица m x n x 3
            bgimage = np.uint8(np.zeros((self.__ysize, self.__xsize, 3), np.uint8)+self.__bgcolor)
            return bgimage
        # если загружено внешнеее изображение, возвращается его копия
        return image.copy()
    
    
    def clear_bg(self, bgimage):
        bgimage = self.bgimage.copy()
    
    
    def bar_graph_image( self, image,one_dimensional_array, color=[255,255,255], rotate = 0 ):
        #self.bgimage_update()
        _x = 1
        if self.__xsize >= len(one_dimensional_array):
            _x = self.__xsize // len(one_dimensional_array)
        odarray = np.array(one_dimensional_array, dtype='int32')
        axis_x = np.arange(0, len(odarray)*_x, _x, dtype='int32')
        pts = np.column_stack((axis_x, odarray)).reshape(-1,1,2)
        # print(odarray)
        # print(axis_x)
        cv2.polylines(image, [pts], False, color, 1)
        if rotate != 0:
            return np.flipud( image )
        return image
    
    
    def get_max_len(self, arrays):
        max_len = 0
        for arg in arrays:
            if len(arg) > max_len:
                max_len = len(arg)
        return max_len
    
    
    def fill_zeros(self, len_num, array1):
        if len(array1) > len_num:
            raise Exception('Размер массива больше заданого размера.')
        div = len_num - len(array1)
        zeros = [0 for i in range(div)]
        array1.extend(zeros)
    
    
    def foo(self, *args):
        num = self.get_max_len(*args)
        for arg in args:
            self.fill_zeros(num, arg)
    
    
    
    # сделать массивы одинаковой длинны
    # получить координаты для каждого массива
    # 
    # 
    # 
    
    
    def bar_graph_image2(self, image, array_arrays, array_colors=[[255,0,0],[0,255,0]], rotate=1):
        
        for ch, col in enumerate(array_colors):
            _x = 1
            if self.__xsize >= len(array_arrays[ch]):
                _x = self.__xsize // len(array_arrays[ch])
            odarray = np.array(array_arrays[ch], dtype='int32')
            axis_x = np.arange(0, len(odarray)*_x, _x, dtype='int32')
            pts = np.column_stack((axis_x, odarray)).reshape(-1,1,2)
            cv2.polylines(image, [pts], False, col, 2) 
        if rotate != 0:
            return np.flipud( image )
        return image
    


if __name__ == '__main__':
    print()
    vd = VisualData()
    
    vd.get_max_len([[23,23,12],[1,2,3,4,5]])
    
    
    
    
    
    
    
    
    
    
    
    


