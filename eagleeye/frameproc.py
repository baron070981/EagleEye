import cv2
import numpy as np



def resize_frame(image, size:int):
    """
    изминение размера изображения
    возыращает уменьшеное или увеличенное изображение
    """
    h, w = image.shape[:2]
    if h > w:
        ...
    if w > h:
        k = w / size
        w = size
        h = h / k
        w = int(w)
        h = int(h)
        return cv2.resize(image, (w, h), cv2.INTER_NEAREST)


def get_new_size(src, width=None, height=None):
    w, h = 0, 0
    if isinstance(src, np.ndarray):
        h, w = src.shape[:2]
    elif isinstance(src, (tuple, list)):
        w, h = src[:2]
    if width and not height:
        k = w / width
        w = width
        h = int(h / k)
    elif height and not width:
        k = h / height
        w = int(w / k)
        h = height
    elif width and height:
        w, h = width, height
    return w, h



def calculate_sections(src:np.ndarray|tuple, size:tuple|None=None, 
                       num_sections:int=1) -> tuple[tuple, tuple, int]:
    """
    расчет размера секции, кол-во секций и нового размера изображения
    исходя из размера и кол-ва секций
    """

    h, w = None, None
    if isinstance(src, np.ndarray):
        h, w = src.shape[:2]
    elif isinstance(src, (tuple, list)):
        w, h = src[:2]
    if h > w:
        ...
    else:
        if size is None: 
            size = w
        else:
            k = w / size
            w = size
            h = int(h / k)

        num_vert_sections = num_sections
        section_size = int(h / num_sections)
        num_hor_sections = int(w / section_size)
        h = section_size * num_vert_sections
        w = section_size * num_hor_sections
        size = w, h
        num_sections = num_hor_sections, num_vert_sections
        return size, num_sections, section_size


def coord_sections(src, hor_sections, vert_sections, section_size):
    """
    
    """
    w, h = None, None
    if isinstance(src, (tuple, list)):
        w, h = src
    elif isinstance(src, np.ndarray):
        h, w = src.shape[:2]
    hor = range(0, w, section_size)
    vert = range(0, h, section_size)
    coords = []
    for hr in hor:
        for vr in vert:
            coords.append((hr, vr, hr+section_size, vr+section_size))
    return coords














