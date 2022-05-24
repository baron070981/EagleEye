
# Подключение камеры, получение кадра и его небольшая обработка

import cv2




class Camera:
    
    def __init__(self, width, color_mode='BGR', camera_id=0):
        self.__width = width # ширина до котрой масштабируется кадр
        self.__color_mode = color_mode 
        self.__cap = cv2.VideoCapture(camera_id) 

    def set_size(self, width):
        # установка новой ширины кадра
        self.__width = width
    
    def __resize(self, frame):
        # маштабируемое изминение размера кадра из заданой ширины
        h, w = frame.shape[:2]
        k = w/h
        size = self.__width, int(self.__width/k)
        return size
    
    
    def get_frame(self, resize=False, flip=False):
        # получение кадра
        ret, frame = self.__cap.read()
        if resize:
            # изминение размера кадра
            frame = cv2.resize(frame, self.__resize(frame), interpolation=cv2.INTER_AREA)
        if flip:
            # отражение кадра
            frame = cv2.flip(frame, 1)
        return frame


    def is_key(self, *args, t=1):
        # проверка нажатой клавиши
        if not args:
            raise Exception('Пустой args')
        k = cv2.waitKey(t)
        return k in args


    def close(self):
        # закрытие камеры и окон
        self.__cap.release()
        cv2.destroyAllWindows()
    





if __name__ == "__main__":
    cam = Camera(300)
    while True:
        frame = cam.get_frame()
        if cam.is_key(27, 13):
            cam.close()
            break
        cv2.imshow('video', frame)











 
