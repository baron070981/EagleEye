import cv2
import numpy as np

from typing import Union

# обработка кадра или его части




class Frame:
    
    def __init__(self, num_sections: int):
        # кол-во равных частей по меньшей стороне, по другой вычисляется
        self.num_sections = num_sections
        self.__size = None
        self.__sections = None
        self.__coords = []
        self.__origin_size = None
    
    
    def __get_num_sections(self, size: tuple):
        # вычисление количества секций и нового размера изображения
        # размер меняется чтоб секции влезли без остатка
        h, w = size
        if self.__origin_size is None or self.__origin_size != size:
            self.__origin_size = size
            # размер секции
            section_size = int(min(size)/self.num_sections)
            # кол-во секций
            section_hor = int(w/section_size)
            section_ver = int(h/section_size)
            # новые размеры
            new_h = section_ver*section_size
            new_w = section_hor*section_size
            
            self.__sections = section_ver, section_hor
            self.__size = new_h, new_w
            print(f'Get num sect... Size: {self.__size}, secton_size: {self.__sections}', end=', ')
            print(f'total sections: {section_ver*section_hor}, size 1 sect: {section_size}')
        return self.__size, self.__sections
    
    
    def __get_coords(self, size, sections):
        # получение списка координат секций(подизображений)
        # size - tuple(h, w)
        # sections - tuple(кол-во секций по вертикали, кол-во секций по горизонтали)
        size = tuple(size)
        sections = tuple(sections)
        if self.__size is not None and self.__size != size or not self.__coords:
            print('Get coords')
            h, w = size
            y_sect, x_sect = sections
            section_size = int(h/y_sect)
            hor_idx_beg = list(range(0, w, section_size))
            hor_idx_end = list(range(section_size, w+section_size, section_size))
            ver_idx_beg = list(range(0, h, section_size))
            ver_idx_end = list(range(section_size, h+section_size, section_size))
            hor_idx = list(zip(hor_idx_beg, hor_idx_end))
            ver_idx = list(zip(ver_idx_beg, ver_idx_end))
            self.__coords = []
            [self.__coords.extend(list(map(lambda x: (y[0], y[1], x[0], x[1]), hor_idx))) for y in ver_idx]
        return self.__coords
    
    
    def resize(self, image):
        self.__get_num_sections(image.shape[:2])
        self.__get_coords(self.__size, self.__sections)
        h, w = self.__size
        return cv2.resize(image, (w, h), interpolation=cv2.INTER_AREA)
    
    @property
    def coords(self):
        return self.__coords
    
    
    def get_means_color(self, frame: np.array) -> list:
        # средние значения каждой секции по каждому каналу
        ysec, xsec = self.__sections
        means = []
        for y1,y2,x1,x2 in self.coords:
            tmp = frame[y1:y2, x1:x2]
            means.append([tmp[:,:,0].mean(), tmp[:,:,1].mean(), tmp[:,:,2].mean()])
        return means
    
    
    def get_means(self, gray: np.array) -> list:
        # среднее значение каждой секции
        ysec, xsec = self.__sections
        means = []
        for y1,y2,x1,x2 in self.coords:
            tmp = gray[y1:y2, x1:x2]
            means.append(tmp.mean())
        return means
    
    
    def __diff_percentege(self, num1, num2):
        pr = self.__percentege(num1, num2)
        return 100-pr
    
    
    def __percentege(self, num1, num2):
        num1 = num1 if num1 > 0 else 0.01
        num2 = num2 if num2 > 0 else 0.01
        k = max([num1, num2])/min([num1, num2])
        return 100/k
    
    
    def get_percentege3(self, arr1, arr2):
        arr1 = np.array(arr1).ravel()
        arr2 = np.array(arr2).ravel()
        p = list(map(lambda x, y: self.__diff_percentege(x, y), arr1, arr2))
        return max(p)
    
    
    def get_diff_percentege(self, num1, num2):
        return self.__percentege(num1, num2)
    
    
    def get_percentege_threshold(self, num1, num2, threshold):
        return self.__percentege(num1, num2) >= threshold
    
    
    def get_threshold_diff_percenteg(self, array1: list, array2: list, threshold: float) -> list:
        perc = list(map(lambda x, y: self.__diff_percentege(x, y), array1, array2))
        res = list(map(lambda x: x >= threshold, perc))
        return res
    
    
    def update(self, num_sections):
        if num_sections != self.num_sections:
            self.num_sections = num_sections
            self.__origin_size = None
            self.__coords = []
            



def show(img):
    cv2.imshow('...', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()





if __name__ == "__main__":
    frame = Frame(10)
    arr1 = [1, 0]
    arr2 = [100, 100]
    print(list(map(lambda x, y: frame.get_percentege(x, y), arr1, arr2)))





