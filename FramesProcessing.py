# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import cv2
import os
import sys
import numpy as np
from PIL import Image
from pprint import pprint
import time





class FramesProcess:

# получаю на вход изображение +
# преобразую его в оттенки серого +
# получаю размеры исходного изображения +
# произвожу расчет новых размеров из заданных параметров +
#


    
    def __init__(self, rows = 1, columns = 1):
        
        self.__sections       = rows     # число секций по большей стороне кадра
        self.__sections_row   = rows     # число строк
        self.__sections_col   = columns  # число столбцов
        self.__x_num_sections = 1        # число секций по оси X
        self.__y_num_sections = 1        # число секций по оси Y
        self.__len_sections   = 1        # длина секции
        self.__row_len        = 1        # высота строки
        self.__col_len        = 1        # ширина стобца
        self.__xsize          = 0        # новый размер изображения
        self.__ysize          = 0        # новый размер изображения
        self.__row_size       = 0        # новый размер изображения (row, rc)
        self.__col_size       = 0        # новый размер изображения (column, rc)
        self.__origin_x       = 0
        self.__origin_y       = 0
        
        
        self.coord_array_x    = None     # 
        self.coord_array_y    = None     # 
        self.coord_array_row  = None     # 
        self.coord_array_col  = None     # 
        self.newsize          = 320
        self.coord_state      = False
    
    
    
    # создание кадра в оттенках серого(серого кадра)
    # используется для дальнейшей обработки
    def create_image_gray(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        #self.__origin_y, self.__origin_x = frame.shape
        return frame
    
    
    def issizes(self, y,x):
        if self.__origin_y != y or self.__origin_x != x:
            self.__origin_y = y
            self.__origin_x = x
            return False
        return True
    
    
    def resize(self, frame, mode = ''):
        if mode == 'grid':
            return cv2.resize(frame, (self.__xsize, self.__ysize))
        elif mode == 'rc':
            return cv2.resize(frame, (self.__col_size, self.__row_size))
        else:
            return frame
    
    
    def t__get_new_sizes(self, y, x):
        lst_size = [y, x]
        division_ratio = int(max(lst_size)/self.newsize)
        second_size = int(min(lst_size)/division_ratio)
        if x > y:
            self.__ysize = second_size
            self.__xsize = self.newsize
        elif y > x:
            self.__xsize = second_size
            self.__ysize = self.newsize
        else:
            self.__ysize = self.newsize
            self.__xsize = self.newsize
        return self.__ysize, self.__xsize
    
    
    def t__get_size_to_sections(self, ysize, xsize):
        # подгонка размеров X и Y под число секций большей оси
        # и расчет числа секций меньшей оси и подгонка ее размера
        if ysize > xsize:
            print( '|-+- Y > X')
            self.__len_sections   = int(ysize/self.__sections)
            self.__ysize          = self.__sections * self.__len_sections
            self.__y_num_sections = self.__sections
            self.__x_num_sections = int(xsize/self.__len_sections)
            self.__xsize          = self.__x_num_sections*self.__len_sections
        elif xsize > ysize:
            print( '|-+- X > Y')
            self.__len_sections   = int( xsize / self.__sections )
            self.__xsize          = self.__sections * self.__len_sections
            self.__x_num_sections = self.__sections
            self.__y_num_sections = int( ysize / self.__len_sections )
            self.__ysize          = self.__y_num_sections * self.__len_sections
        else:
            print('|-+- X == Y')
            self.__len_sections = int(xsize/self.__sections)
            self.__xsize = xsize*self.__len_sections
            self.__ysize = self.__xsize
            self.__x_num_sections  = self.__sections
            self.__y_num_sections  = self.__sections
        
        # подгонка размера оси Y под число строк
        self.__row_len  = int(ysize / self.__sections_row) # высота строки
        self.__row_size = self.__sections_row * self.__row_len # новый размер Y
        
        # подгонка размера оси X под число столбцов
        self.__col_len = int( xsize / self.__sections_col )
        self.__col_size = self.__sections_col * self.__col_len
        
        # массивы размеров для всех вариантов
        # для строк
        row_sizes = np.array([self.__row_size, xsize], dtype=np.uint32)
        
        # для столбцов
        column_sizes = np.array([ysize, self.__col_size], dtype=np.uint32)
        
        # для строк и столбцов
        rc_size = np.array([self.__row_size, self.__col_size], dtype=np.uint32)
        
        # для сетки
        grid_size = np.array([self.__ysize, self.__xsize], dtype=np.uint32)
        return grid_size, rc_size, row_sizes, column_sizes
    
    def __determine_coordinatesX(self):
        coord_array = list()
        xbegin = 0
        ybegin = 0
        xend = self.__len_sections
        yend = self.__len_sections
        temp = [ybegin,yend,xbegin,xend]
        if not self.coord_state:
            for ysect in range(self.__y_num_sections):
                for xsect in range(self.__x_num_sections):
                    if xend > self.__xsize:
                        xbegin = 0
                        xend = self.__len_sections
                    temp[0] = ybegin
                    temp[1] = yend
                    temp[2] = xbegin
                    temp[3] = xend
                    coord_array.append(list(temp))
                    xbegin += self.__len_sections
                    xend += self.__len_sections
                yend += self.__len_sections
                ybegin += self.__len_sections
        return np.array(coord_array)
    
    
    def __determine_coordinatesY(self):
        coord_array = list()
        xbegin = 0
        ybegin = 0
        xend = self.__len_sections
        yend = self.__len_sections
        temp = [ybegin,yend,xbegin,xend]
        if not self.coord_state:
            for xsect in range(self.__x_num_sections):
                for ysect in range(self.__y_num_sections):
                    if yend > self.__ysize:
                        ybegin = 0
                        yend = self.__len_sections
                    temp[0] = ybegin
                    temp[1] = yend
                    temp[2] = xbegin
                    temp[3] = xend
                    coord_array.append(list(temp))
                    ybegin += self.__len_sections
                    yend += self.__len_sections
                xend += self.__len_sections
                xbegin += self.__len_sections
        return np.array(coord_array)
    
    
    def __determine_coordinates_RC(self):
        xbegin = 0
        ybegin = 0
        xend = self.__col_size
        yend = self.__row_len
        coord_row = list()
        coord_row.append(list([ybegin, yend, xbegin, xend]))
        for ysect in range(self.__sections_row-1):
            ybegin += self.__row_len
            yend += self.__row_len
            coord_row.append(list([ybegin, yend, xbegin, xend]))
        
        xbegin    = 0
        ybegin    = 0
        xend      = self.__col_len
        yend      = self.__row_size
        coord_col = list()
        coord_col.append(list([ybegin, yend, xbegin, xend]))
        for xsect in range(self.__sections_col-1):
            xbegin += self.__col_len
            xend   += self.__col_len
            coord_col.append(list([ybegin, yend, xbegin, xend]))
        return np.array(coord_row, dtype=np.uint32), np.array(coord_col, dtype=np.uint32)
    
    
    def get_coords(self):
        # расчет координат секций для grid по оси X
        self.coord_array_x = self.__determine_coordinatesX()
        # расчет координат секций для grid по оси Y
        self.coord_array_y = self.__determine_coordinatesY()
        # расчет координат для RC
        #     для  row              для column
        self.coord_array_row, self.coord_array_col = self.__determine_coordinates_RC()
    
    
    def get_sections_quad(self, frame, coord_array, dtype='uint8'):
        sections_list = list()
        for c in coord_array:
            y1 = c[0]
            y2 = c[1]
            x1 = c[2]
            x2 = c[3]
            sections_list.append(frame[y1:y2, x1:x2])
        return np.array(sections_list, dtype=dtype)
    
    
    def get_sections_ravel(self, frame, coord_array, dtype = 'uint8'):
        sections_list = list()
        for c in coord_array:
            y1 = c[0]
            y2 = c[1]
            x1 = c[2]
            x2 = c[3]
            sections_list.append(frame[y1:y2, x1:x2].ravel())
        return np.array(sections_list, dtype=dtype)
    
    
    def __average(self, array1):
        array1 = np.array(array1)
        return array1.sum()/array1.size
    
    
    def average(self, array1):
        return list(map(self.__average, array1))
    
    
    def __aligns_arrays(self, array_arrays):
        max_len = 0
        # определение максимальной длинны массива
        for arr in array_arrays:
            if len(arr) > max_len:
                max_len = len(arr)
        # привидение массивов к полученной максимальной длинне
        # путем заполнения не достающей длины последним значением
        # соответствующего массива
        for arr in array_arrays:
            div = max_len - len(arr)
            m = [arr[-1] for i in range(div)]
            arr.extend(m) # добавление массива заполненого последним значением
    
    
    # если разница равная или более чем у N элементов на значение Z
    # вывод True
    # изменения освещоннсти расчитывается из относительной разницы
    # всех соответствующих значений обоих массивов
    
    
    def __dif_nums_percent(self, num1, num2):
        diff = abs(num1-num2)
        if num1 > num2:
            # расчет разницы в процентах по отношению к num1
            return round( 100 / (num1 / diff), 3 )
        elif num1 < num2:
            # расчет разницы в процентах по отношению к num2
            return round( 100 / (num2 / diff), 3 )
        else:
            return 0.0

    
    def __get_diff_arrays(self, array1, array2):
        len_arr = len(array1)
        res = list( map( self.__dif_nums_percent, array1, array2 ) )
        return res
    
    
    def get_diff_arrays_bool(self, array1, array2, nums_elems = 1, diff_val_perc = 1):
        self.__aligns_arrays([array1, array2])
        cnt = 0
        p = 0
        diff = self.__get_diff_arrays(array1, array2)
        
        for num in diff:
            if num >= diff_val_perc:
                cnt += 1
        
        if cnt > 0:
            p = round( 100 / (len(diff) / cnt), 3 )
        
        if p >= nums_elems:
            return True
        return False




if __name__ == '__main__':
    
    image = cv2.imread('control_images/peoples2.jpg')
    
    fp = FramesProcess(5,7)
    image = fp.create_image_gray(image)
    y, x = image.shape
    print(y, x, 5, 7)
    
    
    sizes = fp.t__get_size_to_sections(y,x)
    fp.get_coords()
    image2 = cv2.resize(image, (sizes[1][1], sizes[1][0]))
    sections1 = fp.get_sections_quad(image2, fp.coord_array_row)
    sections2 = fp.get_sections_ravel(image2, fp.coord_array_col)
    
    a = [1,10,15,23,12,1,10,15,23,12,1,10,15,23,12]
    b = [2,1,5,23,3432]
    c = fp.get_diff_arrays_bool(a,b, 50, 50)
    # print(a)
    # print(b)
    print(c)
    
    
    cv2.imshow('original', image2)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
