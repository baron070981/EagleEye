
# Подключение камеры, получение кадра и его небольшая обработка

import cv2




class Camera:
    
    def __init__(self, width, color_mode='BGR', camera_id=0):
        self.__width = width
        self.__color_mode = color_mode
        self.__cap = cv2.VideoCapture(camera_id)

    def set_size(self, width):
        self.__width = width
    
    def __resize(self, frame):
        h, w = frame.shape[:2]
        k = w/h
        res = self.__width, int(self.__width/k)
        return res
    
    
    def get_frame(self, resize=False, color=None):
        ret, frame = self.__cap.read()
        if resize:
            frame = cv2.resize(frame, self.__resize(frame), interpolation=cv2.INTER_AREA)
        if color is not None:
            frame = cv2.cvtColor(frame, color)
        frame = cv2.flip(frame, 1)
        return frame


    def is_key(self, *args, t=1):
        if not args:
            raise Exception('Пустой args')
        k = cv2.waitKey(t)
        return k in args


    def close(self):
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











 
