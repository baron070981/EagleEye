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
import sys
from threading import Thread

from eagleeye import camera
from eagleeye import framesprocessing
from eagleeye import files
from eagleeye import textprocessing as tp
from eagleeye import datestimes as dt
import utils
import settings



class RunCameraWindow(tk.Tk):
    
    def __init__(self):
        super().__init__()
        self.bind('<Escape>', self.press_escape)
        self.geometry(f'{self.winfo_screenwidth()}x{self.winfo_screenheight()}')
        # self.geometry(f'{640}x{480}')
        self.ESCAPE = False
    
    
    def press_escape(self, event):
        self.ESCAPE = True
    
    
    def close(self):
        self.destroy()



class WidgetsRunCamera:
    
    def __init__(self, master):
        
        self.TYPE_SIZE = 'mb'
        self.MAX_FILES = 300
        self.NUM_SECTIONS = 31
        self.BETWEEN_SAVE_INTERVAL = 1.1
        self.CAM_ID = 0
        self.NUM_SAVE = 3
        self.THRESHOLD = 16
        self.DIFFERENCE_PERC = 8
        self.SLEEP_TIME = 4.0
        
        self.master = master
        # текущая директория
        self.current = Path(__file__).resolve().parent
        # директория с ресурсными изображениями и т.п.
        self.src_dir = self.current / 'src'
        
        self.NO_VIDEO_IMAGE = cv2.imread(str(self.src_dir/'novideo.png')) # изображение отображаемое если видео не воспроизводится
        # изображение отображаемое если нет вывода сохраненного излбражения
        self.NO_PHOTO_IMAGE = cv2.imread(str(self.src_dir/'noimage.png')) 
        
        self.cam = None # объект камеры
        self.ALLOW_PHOTO_DISPLAY = False # флаг разрешающий выводить фото
        self.last_means = None # предыдущие среднии значения секций
        self.CHANGED = [] # для сохранения соордтнат отличных секций
        self.CLEAR = False # 
        self.START = False # флаг запущена камера или нет
        
        self.origin = None # оригинальное изображение с камеры
        self.video_image = None # кадры выводимые в окне видео
        self.photo_image = None # изображение выводимое в окно фото
        self.process_frame = None # кадры над которыми производятся расчеты
        self.save_image = None # изображение для сохранения
        
        self.count_frame = 0
        
        
        self.frameproc = framesprocessing.Frame(num_sections=self.NUM_SECTIONS)
        self.timer = dt.Timer(self.SLEEP_TIME)
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
        self.time_sleep_var = tk.StringVar()
        self.time_sleep_var.set('5')
        self.num_saved_var = tk.StringVar()
        self.num_saved_var.set('3')
        self.num_sections_var = tk.StringVar()
        self.num_sections_var.set('21')
        self.threshold_var = tk.StringVar()
        self.threshold_var.set(str(self.THRESHOLD))
        self.diff_perc_var = tk.StringVar()
        self.diff_perc_var.set(str(self.DIFFERENCE_PERC))
        
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
        self.video_w = int((self.master_w-w)/2-utils.get_relative_size(self.master_w, .01))
        self.video_h = int(self.video_w/(self.master_w/self.master_h))
        self.video_size = (self.video_w, self.video_h)
        
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
        
        self.interval_label = tk.Label(self.control_frame, 
                                       height=1, 
                                       text='Время между кадрами:')
        
        self.interval_scale = tk.Scale(self.control_frame, orient=tk.HORIZONTAL,
                                       length=utils.get_relative_size(self.master_w, 0.2),
                                       from_=0.3, to=3.0, 
                                       tickinterval=0.3,
                                       resolution=0.1)
        self.interval_scale.set(self.BETWEEN_SAVE_INTERVAL)
        self.saving.update_interval(self.interval_scale.get())
        
        self.sleep_entry = tk.Entry(self.control_frame, 
                                    textvariable=self.time_sleep_var,
                                    justify=tk.CENTER,
                                    width=10)
        
        self.sleep_label = tk.Label(self.control_frame,
                                    height=1, 
                                    text='Время ожидания:')
        
        self.num_saved_img_label = tk.Label(self.control_frame,
                                            height=1,
                                            text='Кол-во сохр. подряд:')
        
        self.num_saved_img_entry = tk.Entry(self.control_frame,
                                            textvariable=self.num_saved_var,
                                            justify=tk.CENTER,
                                            width=10)
        
        self.num_sect_label = tk.Label(self.control_frame,
                                       height=1,
                                       text='Кол-во секций:')
        
        self.num_sect_entry = tk.Entry(self.control_frame, 
                                       textvariable=self.num_sections_var,
                                       justify=tk.CENTER,
                                       width=10)
        self.NUM_SECTIONS = int(self.num_sect_entry.get())
        
        self.threshold_label = tk.Label(self.control_frame,
                                       height=1,
                                       text='Порог(проц): ')
        
        self.threshold_entry = tk.Entry(self.control_frame, 
                                       textvariable=self.threshold_var,
                                       justify=tk.CENTER,
                                       width=10)
        
        self.diff_perc_label = tk.Label(self.control_frame,
                                       height=1,
                                       text='Разница секций:')
        
        self.diff_perc_entry = tk.Entry(self.control_frame, 
                                       textvariable=self.diff_perc_var,
                                       justify=tk.CENTER,
                                       width=10)
        
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
        
        self.btn.place(x=self.master_w-utils.get_relative_size(self.master_w, 0.1),
                       y=self.master_h-utils.get_relative_size(self.master_h, 0.1))
        
        self.control_frame.place(x=utils.get_relative_size(self.master_w, 0.02),
                                 y=self.video_h+utils.get_relative_size(self.master_h, 0.1))
        
        
        self.interval_label.grid(row=0, column=0, sticky='nw', pady=20)
        self.interval_scale.grid(row=0, column=1, sticky='nw')
        self.sleep_label.grid(row=1, column=0, sticky='nw')
        self.sleep_entry.grid(row=1, column=1, sticky='nw')
        self.num_saved_img_label.grid(row=2, column=0, sticky='nw')
        self.num_saved_img_entry.grid(row=2, column=1, sticky='nw')
        self.num_sect_label.grid(row=3, column=0, sticky='nw')
        self.num_sect_entry.grid(row=3, column=1, sticky='nw')
        self.threshold_label.grid(row=4, column=0, sticky='nw')
        self.threshold_entry.grid(row=4, column=1, sticky='nw')
        self.diff_perc_label.grid(row=5, column=0, sticky='nw')
        self.diff_perc_entry.grid(row=5, column=1, sticky='nw')
        
        
        
        # загрузка изображения для выводва вместо сохраненного фото
        # если вывод фото отключен
        self.NO_PHOTO_IMAGE = utils.convert_np2photoimage(self.NO_PHOTO_IMAGE, (self.video_w, self.video_h))
        self.photo.create_image((self.video_w//2, self.video_h//2), image=self.NO_PHOTO_IMAGE)
        self.photo.image = self.NO_PHOTO_IMAGE
        
        # загрузка изображения для выводва вместо видео
        # если вывод видео отключен
        self.NO_VIDEO_IMAGE = utils.convert_np2photoimage(self.NO_VIDEO_IMAGE, (self.video_w, self.video_h))
        self.video.create_image((self.video_w//2, self.video_h//2), image=self.NO_VIDEO_IMAGE)
        self.video.image = self.NO_VIDEO_IMAGE
    
    
    def convert_np2pil(self, image, size: tuple=None):
        bgra = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
        rgba = cv2.cvtColor(bgra, cv2.COLOR_BGRA2RGBA)
        if size is not None:
            rgba = cv2.resize(rgba, size, interpolation=cv2.INTER_AREA)
        image = Image.fromarray(rgba.astype('uint8')).convert('RGBA')
        return ImageTk.PhotoImage(image)
    
    
    def update_settings(self):
        setting_save = self.saving.update_interval(self.interval_scale.get())
        
        sleep = self.sleep_entry.get()
        sleep = utils.valedate_str_to_float(sleep,min_val=1, max_val=900)
        if sleep != self.SLEEP_TIME:
            setting_save = True
            self.SLEEP_TIME = sleep
            self.timer.interval = sleep
        
        num_saved = self.num_saved_img_entry.get()
        num_saved = utils.valedate_str_to_int(num_saved,min_val=2, max_val=20)
        self.saving.num_save = num_saved
        
        num_sections = self.num_sect_entry.get()
        num_sections = utils.valedate_str_to_int(num_sections,min_val=2, max_val=100)
        self.frameproc.update(num_sections)
        
        diff_perc = self.diff_perc_entry.get()
        self.DIFFERENCE_PERC = utils.valedate_str_to_int(diff_perc, min_val=1, max_val=100)
        
        thresh = self.threshold_entry.get()
        self.THRESHOLD = utils.valedate_str_to_int(thresh, min_val=1, max_val=100)
        
    
    
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
        # обновление кадров в self.video
        # ===============================
        # создание объекта камеры
        if self.cam is None:
            try:
                self.cam = camera.Camera(800, camera_id=self.CAM_ID)
            except CameraException:
                print(CameraException)
                return
            except Exception as err:
                print(err)
                return
        
        self.update_settings()
        
        # оригинальное изображение
        self.origin = self.cam.get_frame(resize=True, flip=False) 
        # монохромное изображение которое будет обрабатываться
        # и по которому будут проводиться вычисления
        self.process_frame = cv2.cvtColor(self.origin, cv2.COLOR_BGR2GRAY)
        self.process_frame = self.frameproc.resize(self.process_frame)
        # текст на оригинальном изображении с текущим временем
        cv2.putText(self.origin, dt.get_timestr(), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (250,130,125), 2)
        
        # временное изображение
        tmp_image = utils.convert_np2photoimage(self.origin, self.video_size)
        # изображения для вывода в виджетах video и photo
        # если чекбоксы установлены, то выводится уменьшеное изображение с камеры
        # если не установлены, выводится изображение заглушка
        self.video_image = np.copy(tmp_image) if self.visible_video.get() else self.NO_VIDEO_IMAGE
        
        # текущие средние значения секций
        current_means = self.frameproc.get_means(self.process_frame)
        # если уже есть предыдущие средние значения
        if self.last_means:
            # сравнение значний и получение списка отличий по порогу
            perc = self.frameproc.get_threshold_diff_percenteg(current_means, self.last_means, self.THRESHOLD)
            self.CHANGED = list(filter(lambda x: x == True, perc))
            
        # сохранение текущих значений как предыдущих
        self.last_means = current_means.copy()
        
        # если процентное кол-во изменившихся секций больше заданного
        if len(self.CHANGED)/(len(current_means)/100) >= self.DIFFERENCE_PERC and not self.CLEAR and self.START:
            if self.saving.is_interval():
                self.ALLOW_PHOTO_DISPLAY = True
                self.photo_image = np.copy(tmp_image) if self.visible_photo.get() else self.NO_PHOTO_IMAGE
                self.saving.add_stack(self.origin)
            else:
                tp.TextInfo.add(f'Запуск таймера задержки')
                self.timer.start
                self.ALLOW_PHOTO_DISPLAY = False
        if self.timer.stop:
            tp.TextInfo.add(f'Остановка таймера')
            self.saving.reset_times
        
        self.CHANGED = []
        self.CLEAR = not self.CLEAR
        self.video.create_image((self.video_w//2, self.video_h//2), image=self.video_image)
        self.video.image = self.video_image
        
        # если была нажата клавиша привязанная к главному окну
        if self.master.ESCAPE:
            while self.saving.len_stack > 0:
                self.saving.save_from_stack()
            self.cam.close() 
            self.master.close()
        
        self.video.after(1, self.video_update)
    
    
    def photo_update(self):
        if self.photo_image is not None and self.ALLOW_PHOTO_DISPLAY:
            self.ALLOW_PHOTO_DISPLAY = False
            while self.saving.len_stack > 0:
                self.saving.save_from_stack()
            self.photo.create_image((self.video_w//2, self.video_h//2), image=self.photo_image)
            self.photo.image = self.photo_image
        self.photo.after(1, self.photo_update)
    
    









if __name__ == "__main__":
    root = RunCameraWindow()
    wid = WidgetsRunCamera(root)
    
    wid.update_text()
    
    wid.video_update()
    wid.photo_update()
    
    root.mainloop()
















