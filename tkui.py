import tkinter as tk
from tkinter import ttk
import random
import time
from PIL import ImageTk, Image
import cv2
import datetime
import numpy as np
from pathlib import Path
from typing import Union

from eagleeye import camera
from eagleeye import framesprocessing
from eagleeye import files
from eagleeye import textprocessing as tp
from eagleeye import datestimes as dt



def get_relative_size(size: int, perc: float) -> int:
    perc = 1 if perc > 1 else perc
    perc = 0 if perc < 0 else perc
    
    perc = perc*100
    one = size/100
    return int(one*perc)
    


class RunCameraWndow(tk.Tk):
    
    def __init__(self):
        super().__init__()
        self.bind('<Escape>', self.close)
        self.geometry(f'{self.winfo_screenwidth()}x{self.winfo_screenheight()}')
        # self.geometry(f'{640}x{480}')
    
    
    def close(self, event):
        self.destroy()



class MyScaleWidget:
    
    def __init__(self, master, fg, text, pos, **kwargs):
        self.scale = tk.Scale(master, kwargs)
        self.label = tk.Label(master, text)
        
        self.label.place()
        self.scale.place()



class WidgetsRunCamera:
    
    
    
    def __init__(self, master):
        
        
        self.TYPE_SIZE = 'mb'
        self.MAX_FILES = 300
        self.NUM_SECTIONS = 21
        self.BETWEEN_SAVE_INTERVAL = 1.1
        self.CAM_ID = 0
        self.NUM_SAVE = 4
        self.FRAME_SIZE = 800
        
        # текущая директория
        self.current = Path(__file__).resolve().parent
        # директория с ресурсными изображениями и т.п.
        self.src_dir = self.current / 'src'
        
        self.NO_VIDEO = cv2.imread(str(self.src_dir/'novideo.png')) # изображение отображаемое если видео не воспроизводится
        self.NO_PHOTO = cv2.imread(str(self.src_dir/'noimage.png')) # изображение отображаемое если нет вывода сохраненного излбражения
        
        
        self.cam = None # объект камеры
        self.image = None 
        self.PHOTO = False # флаг разрешающий выводить фото
        self.save_image_show = None # для отображения сохраненного изображения
        self.save_image = None # для сохраненного изображения
        self.last_means = None # предыдущие среднии значения секций
        self.CHANGED = [] # для сохранения соордтнат отличных секций
        self.CLEAR = False # 
        self.START = False # флаг запущена камера или нет
        self.count_frame = 0
        
        
        self.frameproc = framesprocessing.Frame(num_sections=self.NUM_SECTIONS)
        self.timer = dt.Timer(4)
        self.saving = files.SaveFrames('images', 
                                       max_files=self.MAX_FILES, 
                                       type_size=self.TYPE_SIZE, 
                                       interval=self.BETWEEN_SAVE_INTERVAL,
                                       num_save=self.NUM_SAVE)
        
        
        self.info_text = tk.StringVar() # для хранения текста выводимого в info_out_text
        self.visible_video = tk.BooleanVar() # выводить или нет видео
        self.visible_photo = tk.BooleanVar() # выводить или нет фото
        self.visible_photo.set(True)
        self.visible_video.set(True)
        
        # размер родительскокго окна
        self.master_w, self.master_h = self.__get_master_size(master)
        
        self.info_frame = tk.Frame(master, width=self.master_w)
        self.control_frame = tk.Frame(master, width=self.master_w)
        
        # для вывода информации
        self.info_out_text = tk.Label(self.info_frame, 
                                        textvariable=self.info_text,
                                        width=40, bd=1,
                                        height=20,
                                        fg='#44ff44',
                                        anchor='nw')
        
        self.info_out_text.grid(row=0, rowspan=2, column=0, sticky='n')
        
        # получение размеров info_out_text
        self.info_out_text.update()
        w, h = self.info_out_text.winfo_width(), self.info_out_text.winfo_height()
        # получение размеров виджетов для фото/видео исходя из высоты info_out_text
        self.video_w = int((self.master_w-w)/2-get_relative_size(self.master_w, .01))
        self.video_h = int(self.video_w/(self.master_w/self.master_h))
        
        # виджеты для отображения фото и видео
        self.video = tk.Canvas(self.info_frame, height=self.video_h, width=self.video_w)
        self.photo = tk.Canvas(self.info_frame, height=self.video_h, width=self.video_w)
        
        # чекбоксы устанавливающие выводить или нет фото/видео
        self.visible_video_check = tk.Checkbutton(self.info_frame, 
                                                  text='Выводить видео',
                                                  variable=self.visible_video,
                                                  fg='#ff0000')
        self.visible_photo_check = tk.Checkbutton(self.info_frame, 
                                                  text='Выводить фото',
                                                  variable=self.visible_photo,
                                                  fg='#ff0000')
        
        
        self.interval_scale = tk.Scale(master, orient=tk.HORIZONTAL,
                                       length=get_relative_size(self.master_w, 0.2),
                                       from_=0.3, to=2.0, 
                                       tickinterval=0.2,
                                       resolution=0.1)
        
        
        self.timer_scale = tk.Scale(master, orient=tk.HORIZONTAL,
                                       length=get_relative_size(self.master_w, 0.2),
                                       from_=1, to=20, 
                                       tickinterval=2,
                                       resolution=1)
        self.interval_scale.set(1.1)
        self.saving.interval = self.interval_scale.get()
        
        # кнопка запуска и остановки приложения, но не выхода из него.
        self.btn = tk.Button(master, 
                             command=self.run, 
                             text='запуск камеры', 
                             bg='#4444ff', 
                             fg='#ffffff')
        
        
        
        # =======================================================
        # =============== размещение виджетов ===================
        # =======================================================
        
        self.info_frame.grid(row=0, column=0)
        # self.control_frame.grid(row=1, column=0)
        
        self.video.grid(row=0, column=1)
        self.photo.grid(row=0, column=2)
        self.visible_video_check.grid(row=1, column=1, sticky='sw')
        self.visible_photo_check.grid(row=1, column=2, sticky='sw')
        
        self.btn.place(x=self.master_w-get_relative_size(self.master_w, 0.1),
                       y=self.master_h-get_relative_size(self.master_h, 0.1))
        
        self.interval_scale.place(x=get_relative_size(self.master_w, 0.02),
                                  y=self.video_h+get_relative_size(self.master_h, 0.1))
        
        
        # загрузка изображения для выводва вместо сохраненного фото
        # если вывод фото отключен
        self.NO_PHOTO = cv2.cvtColor(self.NO_PHOTO, cv2.COLOR_BGR2BGRA)
        self.NO_PHOTO = cv2.cvtColor(self.NO_PHOTO, cv2.COLOR_BGRA2RGBA)
        self.NO_PHOTO = cv2.resize(self.NO_PHOTO, (self.video_w, self.video_h), interpolation=cv2.INTER_AREA)
        _no_photo = Image.fromarray(self.NO_PHOTO.astype('uint8')).convert('RGBA')
        _no_photo = ImageTk.PhotoImage(_no_photo)
        self.photo.create_image((self.video_w//2, self.video_h//2), image=_no_photo)
        self.photo.image = _no_photo
        
        # загрузка изображения для выводва вместо видео
        # если вывод видео отключен
        self.NO_VIDEO = cv2.cvtColor(self.NO_VIDEO, cv2.COLOR_BGR2BGRA)
        self.NO_VIDEO = cv2.cvtColor(self.NO_VIDEO, cv2.COLOR_BGRA2RGBA)
        self.NO_VIDEO = cv2.resize(self.NO_VIDEO, (self.video_w, self.video_h), interpolation=cv2.INTER_AREA)
        _no_photo = Image.fromarray(self.NO_VIDEO.astype('uint8')).convert('RGBA')
        _no_photo = ImageTk.PhotoImage(_no_photo)
        self.video.create_image((self.video_w//2, self.video_h//2), image=_no_photo)
        self.video.image = _no_photo
    
    
    def update_scale_interval(self):
        self.saving.update_interval(self.interval_scale.get())
    
    
    def update_settings(self):
        self.saving.interval = self.interval_scale.get()
        
    
    
    def frame_count(self):
        self.count_frame += 1
        if self.count_frame >= 100:
            self.count_frame = 0
    
    
    def run(self):
        self.START = not self.START
        self.btn['text'] = 'остановить' if self.START else 'запуск камеры'
        self.btn['bg'] = '#ff4444' if self.START else '#4444ff'
    
    
    def __get_master_size(self, master):
        master.update_idletasks()
        sizestr = master.geometry().split('+')[0].split('x')
        size = list(map(int, sizestr))
        return size
    
    
    def update_text(self):
        text = tp.TextInfo.text()
        self.info_text.set(text)
        self.info_out_text.after(100, self.update_text)
    
    
    def video_update(self):
        # создание обекта камеры если он еще не создан
        if self.cam is None:
            self.cam = camera.Camera(self.FRAME_SIZE, camera_id=self.CAM_ID)
        
        
        self.update_scale_interval()
        
        
        # кадр для обработки, расчетов и сохранения
        origin_frame = self.cam.get_frame(flip=True, resize=True)
        origin_frame = cv2.cvtColor(origin_frame, cv2.COLOR_BGR2BGRA)
        origin_frame = cv2.cvtColor(origin_frame, cv2.COLOR_BGRA2RGBA)
        origin_frame = self.frameproc.resize(origin_frame)
        
        # кадр для отображения
        saved_frame =  cv2.resize(origin_frame, (self.video_w, self.video_h), 
                                      interpolation=cv2.INTER_AREA)
        
        if self.visible_video.get():
            self.frame_count()
            displayed_frame = np.copy(saved_frame)
            cv2.putText(displayed_frame, dt.get_timestr(), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (250,130,125), 2)
            cv2.putText(displayed_frame, f'{self.count_frame}', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (50,30,225), 2)
        else:
            displayed_frame = self.NO_VIDEO
        # получение средних значений секций кадра
        means = self.frameproc.get_means_color(origin_frame)
        
        # если есть предыдущие расчеты средних значений
        if self.last_means:
            # прохожу по списку текущих средних значений
            for i, m in enumerate(means):
                # и сравниваю их с предыдущими
                # если отличаются на равное или большее число в процентах
                if self.frameproc.get_percentege3(m, self.last_means[i]) >= 15:
                    # сохраняются координаты отличающихся секций
                    self.CHANGED.append(self.frameproc.coords[i])
        
        
        # сравнение длины списка координат в процентах к длине списка
        # средних значений секций текущего кадра
        if len(self.CHANGED)/(len(means)/100) >= 8 and not self.CLEAR and self.START:
            self.PHOTO = True # разрешение на отображение кадра как фото и его сохранение
            cv2.putText(origin_frame, dt.get_timestr(), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (250,130,125), 2)
            if self.saving.is_interval():
                self.save_image = cv2.cvtColor(origin_frame, cv2.COLOR_RGBA2BGR)
                self.save_image_show = np.copy(saved_frame) if self.visible_photo.get() else self.NO_PHOTO
            else:
                tp.TextInfo.add(f'Запуск таймера задержки')
                self.timer.start
                self.PHOTO = False
        # проверка прошедшего времени и выключение таймера
        if self.timer.stop:
            # сброс списка времен
            tp.TextInfo.add(f'Остановка таймера')
            self.saving.reset_times
        
        # создание копии текущих средних значений которые станут предыдущими для следующего кадра
        self.last_means = means.copy()
        self.CLEAR = not self.CLEAR
        self.CHANGED = [] # очистка списка координат
        
        # если чекбокс установлен в True выводить кадр в виджет self.video
        self.cam.is_key(13, 27)
        displayed_frame = Image.fromarray(displayed_frame.astype('uint8')).convert('RGB')
        displayed_frame = ImageTk.PhotoImage(displayed_frame)
        self.video.create_image((self.video_w//2, self.video_h//2), image=displayed_frame)
        self.video.image = displayed_frame
        self.video.after(1, self.video_update)

    
    def photo_update(self):
        if self.save_image_show is not None and self.PHOTO:
            self.saving.save(self.save_image)
            self.PHOTO = False
            _displayed_frame = Image.fromarray(self.save_image_show.astype('uint8')).convert('RGB')
            _displayed_frame = ImageTk.PhotoImage(_displayed_frame)
            self.photo.create_image((self.video_w//2, self.video_h//2), image=_displayed_frame)
            self.photo.image = _displayed_frame
        self.photo.after(1, self.photo_update)
    
    









if __name__ == "__main__":
    root = RunCameraWndow()
    wid = WidgetsRunCamera(root)
    
    wid.update_text()
    
    wid.video_update()
    wid.photo_update()
    
    root.mainloop()
















