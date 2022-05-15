import cv2
import numpy as np


def get_coords_split_image(frame: np.array, num_frames: int) -> (list, list):
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
    return [h, w], coords














if __name__ == "__main__":
    img = cv2.imread('ship.png')
    tmp = img[:int(img.shape[0]/2), :int(img.shape[1]/2)]
    r = tmp[:,:,0].mean()
    g = tmp[:,:,1].mean()
    b = tmp[:,:,2].mean()
    img[:int(img.shape[0]/2), :int(img.shape[1]/2)] = [b,g,r]
    cv2.imshow('i', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()












