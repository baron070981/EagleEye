import cv2
import numpy as np
import sys





class Camera:

    def __init__(self, winnames:list=None):
        self.ids = self.get_camera_ids()
        if not self.ids:
            raise Exception('Подключеннной камеры не найдено')
        self.captures = dict()
        self.__set_captures()
        self.cam_id = self.ids[0]
        self.cap = self.captures[self.cam_id]
        self.winnames = ['video']
        if winnames is not None:
            self.winnames.extend(winnames)
        self.windows = None


    def get_camera_ids(self):
        """
        проверка какие камеры подключены
        возвращает список id
        """
        ids = []
        for i in range(10):
            cap = cv2.VideoCapture(i)
            status, data = cap.read()
            if status:
                ids.append(i)
            cap.release()
        return ids
    

    def __set_captures(self):
        for _id in self.ids:
            self.captures[_id] = cv2.VideoCapture(_id)


    def set_camera_id(self, cam_id):
        if cam_id in self.ids:
            self.cap = self.captures[cam_id]
            self.cam_id = cam_id


    def read(self):
        if self.windows is None:
            self.windows = [cv2.namedWindow(name) for name in self.winnames]
        return self.cap.read()
    

    def show(self, frame, win_name=None):
        if win_name is not None and win_name not in self.winnames:
            return
        if win_name is None: win_name = 'video'
        cv2.imshow(win_name, frame)
    

    def destroy(self):
        self.cap.release()
        cv2.destroyAllWindows()
    

    def close(self, winnames=None):
        if winnames is None:
            cv2.destroyAllWindows()
            self.windows = None
        else:
            for name in winnames:
                if name in self.winnames:
                    cv2.destroyWindow(name)
                






if __name__ == "__main__":
    ...
    camera = Camera()
    cv2.namedWindow('video')
    while True:
        stat, frame = camera.read()
        if not stat:
            camera.close()
        if cv2.waitKey(1) == 27:
            camera.close()
            break
        camera.show('video', frame)











