from PIL import ImageTk, Image
import numpy as np 
import cv2


def valedate_str_to_float(string, min_val=0.1, max_val=10):
    num = float(min_val)
    if string.count('.') == 0 and string.isdigit():
        num = float(string)
    elif string.count('.') == 1:
        numbers = string.split('.')
        num = float(numbers) if all(map(str.isdigit, numbers)) else float(min_val)
    if num < min_val:
        num = float(min_val)
    elif num > max_val:
        num = float(max_val)
    return num


def valedate_str_to_int(string, min_val=0, max_val=10):
    try:
        num = int(string)
        return num
    except:
        return min_val


def convert_np2photoimage(image, size: tuple=None) -> ImageTk.PhotoImage:
    bgra = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
    rgba = cv2.cvtColor(bgra, cv2.COLOR_BGRA2RGBA)
    if size is not None:
        rgba = cv2.resize(rgba, size, interpolation=cv2.INTER_AREA)
    image = Image.fromarray(rgba.astype('uint8')).convert('RGBA')
    return ImageTk.PhotoImage(image)


def get_relative_size(size: int, perc: float) -> int:
    perc = 1 if perc > 1 else perc
    perc = 0 if perc < 0 else perc
    
    perc = perc*100
    one = size/100
    return int(one*perc)
























