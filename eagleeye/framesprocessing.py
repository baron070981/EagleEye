import cv2
import numpy as np

# обработка кадра или его части





def get_coords_split_image(frame: np.array, num_frames: int) -> (list, list):
    '''Разделение '''
    coords = []
    # исходные размеры изображения
    h, w = frame.shape[:2]
    # размер подизображения
    size = int(h/num_frames) if h < w else int(w/num_frames)
    # кол-во подизображений которые вместятся в ширину и в высоту
    num_y_section = int(h/size)
    num_x_section = int(w/size)
    # новые размеры изображения
    h = num_y_section*size
    w = num_x_section*size
    # начальные координаты
    y = x = 0
    # получение координат подизображений
    for i in range(num_y_section):
        for j in range(num_x_section):
            coords.append((y, y+size, x, x+size))
            x += size
        x = 0
        y += size
    return [h, w], [num_y_section, num_x_section], coords


def get_mean_colors(array):
    '''получение средних значений из массива(трехканального изображения) по каждому цвету'''
    if len(array.shape) != 3:
        raise Exception('Не подходящая структура массива')
    b = array[:, :, 0].mean()
    g = array[:, :, 1].mean()
    r = array[:, :, 2].mean()
    return b, g, r


def get_mean_sections(arr, size, coords):
    '''Получение массива средних значений подмассивов из массива
    coords - (y1, y2, x1, x2)
    arr - двумерный массив(серое изображение)
    size - [секций по вертикали, секций по горизонтали]
    '''
    means = np.zeros(size, dtype='uint8')
    i = 0
    for vert in range(size[0]):
        for hor in range(size[1]):
            y1, y2, x1, x2 = coords[i]
            m = arr[y1:y2, x1:x2].mean()
            means[vert][hor] = m
            i += 1
    return means


def is_changed(arr1, arr2, perc=25):
    m1 = arr1.mean()
    m2 = arr2.mean()
    dif = abs(m1-m2)
    return max([m1, m2])/100*dif >= perc





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
            print('Getting new size and num sections...', self.__size, size)
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
    
    
    def get_means_color(self, frame):
        ysec, xsec = self.__sections
        means = []
        for y1,y2,x1,x2 in self.coords:
            tmp = frame[y1:y2, x1:x2]
            means.append([tmp[:,:,0].mean(), tmp[:,:,1].mean(), tmp[:,:,2].mean()])
        return means
    
    
    def __percentege(self, num1, num2):
        dif = abs(float(num1)-float(num2))
        return max([num1, num2])/100*dif
    
    
    def get_percentege3(self, arr1, arr2):
        arr1 = np.array(arr1).ravel()
        arr2 = np.array(arr2).ravel()
        p = list(map(lambda x, y: self.__percentege(x, y), arr1, arr2))
        return max(p)




def show(img):
    cv2.imshow('...', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()





if __name__ == "__main__":
    frame = Frame(3)
    image = cv2.imread('pri.jpg')
    print(image.shape)
    coords = frame.get_means_color(image)
    print(coords)
    show(image)





