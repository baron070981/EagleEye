
# Подключение камеры, получение кадра и его небольшая обработка

import cv2
import numpy as np
# import textprocessing



class CameraException(Exception):
    pass


class Camera:
    
    def __init__(self, width, color_mode='BGR', camera_id=0):
        self.__width = width # ширина до котрой масштабируется кадр
        self.__color_mode = color_mode
        self.__cam_ids = self.__get_cams_ids()
        if self.__cam_ids:
            camid = camera_id if camera_id in self.__cam_ids else self.__cam_ids[0]
            self.__cap = cv2.VideoCapture(camid)
        else:
            raise CameraException('Нет доступной камеры...')
    
    
    def __get_cams_ids(self):
        ids = []
        for i in range(10):
            cap = cv2.VideoCapture(i)
            status, data = cap.read()
            if status:
                ids.append(i)
            cap.release()
        return ids
    
    
    def set_size(self, width: int) -> None:
        # установка новой ширины кадра
        self.__width = width
    
    def __resize(self, frame: np.array) -> tuple:
        # маштабируемое изминение размера кадра из заданой ширины
        h, w = frame.shape[:2]
        k = w/h
        size = self.__width, int(self.__width/k)
        return size
    
    
    def get_frame(self, resize: bool=False, flip: bool=False) -> np.array:
        # получение кадра
        ret, frame = self.__cap.read()
        if resize:
            # изминение размера кадра
            frame = cv2.resize(frame, self.__resize(frame), interpolation=cv2.INTER_AREA)
        if flip:
            # отражение кадра
            frame = cv2.flip(frame, 1)
        return frame


    def is_key(self, *args, t: int=1) -> bool:
        # проверка нажатой клавиши
        if not args:
            raise Exception('Пустой args')
        k = cv2.waitKey(t)
        return k in args


    def close(self) -> None:
        # закрытие камеры и окон
        self.__cap.release()
        cv2.destroyAllWindows()
    





if __name__ == "__main__":
    cam = Camera(1000, camera_id=2)
    while True:
        frame = cam.get_frame(flip=True, resize=True)
        print(frame.shape)
        if cam.is_key(27, 13):
            cam.close()
            break
        cv2.imshow('video', frame)











 
