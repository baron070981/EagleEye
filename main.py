import sys
from pathlib import Path
import datetime
from random import randint
import time
import subprocess as sp

import tkinter as tk
from tkinter import ttk
import cv2
import numpy as np
from rich import print, inspect

from eagleeye import frameproc as fp
from eagleeye import camera
from eagleeye import times
from eagleeye import files
from tbot import tbot


def get_percent_diff(val1, val2):
    val1, val2 = sorted([val1, val2])
    if val2 == 0: return 0
    return 100 - val1 / val2 * 100


def get_text_rectangle(text, text_coords, font_scale=1, font=cv2.FONT_HERSHEY_PLAIN, thickness=1):
    text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
    text_coords = (text_coords[0], text_size[1]+text_coords[1])
    top_left_point = (text_coords[0]-3, text_coords[1]-text_size[1]-3)
    bottom_right_point = (text_coords[0]+text_size[0]+3, text_coords[1]+3)
    return top_left_point, bottom_right_point, text_coords


def stringvar2int(value: str|tk.StringVar, default_var: str|int|tk.StringVar, default: int=0):
    if isinstance(value, tk.StringVar):
        value = value.get()
    if isinstance(default_var, tk.StringVar):
        default_var = default_var.get()
    if isinstance(default_var, int):
        default_var = str(default_var)
    if not default_var.isdigit(): default_var = default
    if not value.strip() or not value.isdigit():
        value = default_var
    return int(value)
    


class MainWindow(tk.Tk):
    # главное окно
    def __init__(self):
        super().__init__()
        self.bind('<Escape>', self.press_escape)
        self.geometry(f'{self.winfo_screenwidth()}x{self.winfo_screenheight()}')
        self.width = self.winfo_screenmmwidth()
        self.height = self.winfo_screenmmheight()
        self.ESCAPE = False
    
    def press_escape(self, event):
        self.ESCAPE = True
    
    def close(self):
        self.destroy()

ROOT = Path(__file__).parent
SAVES_DIR = ROOT / 'saving'
SAVES_DIR.mkdir(exist_ok=True)

class Widgets:
    def __init__(self, window:MainWindow):
        self.__window = window
        self.__window['bg'] = '#222222'

        self.window_bg = '#222222'
        self.main_fg = '#ffffff'
        self.default_font = lambda x: f'TkDefaultFont {x}'
        self.main_font = 'TkDefaultFont 14'
        self.color_orange1 = '#ffaa00'
        self.color_orange2 = '#FEF389'
        self.color_text = '#7698DF'
        self.not_active_btn = '#212E3A'
        self.active_btn = '#DB4842'
        self.active_bot_color = '#DB4842'

        # список камер
        self.camera = camera.Camera(['save image'])
        self.cam_ids = self.camera.ids

        # variables
        self.time_between_saves_var = tk.DoubleVar(value=0.5)
        self.camera_id_var = tk.IntVar(value=self.cam_ids[0])
        self.number_sect_var = tk.StringVar(value=30)
        self.sleep_var = tk.StringVar(value='5')
        self.num_saves_var = tk.StringVar(value=5)
        self.num_diff_sect_var = tk.StringVar(value=8)
        self.diff_between_sect_var = tk.StringVar(value=20)

        self.set_hour_on_var = tk.StringVar(value='0')
        self.set_min_on_var = tk.StringVar(value='0')
        self.set_hour_off_var = tk.StringVar(value='0')
        self.set_min_off_var = tk.StringVar(value='0')

        self.dur_hour_on_var = tk.StringVar(value='0')
        self.dur_min_on_var = tk.StringVar(value='1')
        self.dur_hour_off_var = tk.StringVar(value='0')
        self.dur_min_off_var = tk.StringVar(value='1')

        self.active_timer_var = tk.BooleanVar(value=False)
        self.timer_mode_var = tk.IntVar(value=0)

        self.info_text_save_var = tk.StringVar()

        text = '99:99:99'
        self.__font = cv2.FONT_HERSHEY_PLAIN
        self.__font_scale = 1.3
        self.__thickness = 1
        self.__text_color = (255, 255, 255)
        self.__text_bg = (20, 20, 20)

        self.__rect_poin1, self.__rect_point2, self.__text_coords = get_text_rectangle(text, text_coords=(5, 5), 
                                                                                       font_scale=1.3, thickness=2)
        

        self.out_text = []

        self.START_BTN_PRESSED = False
        self.START_BOT_BTN_PRESSED = False
        self.STOP_BOT_BTN_PRESSED = True
        self.PAUSE_BOT_BTN_PRESSED = False
        self.CAMERA_IS_RUN = False
        self.BOT_START = False
        self.BOT_PAUSE = False
        self.BOT_STOP = True

        self.TIME_CONTROL = False
        self.TIME_CONTROL_CLOCK = False
        self.TIME_CONTROL_INTERVAL = False

        self.TIMER_BETWEEN_SAVES_RUNNING = False
        self.TIMER_SLEEP_RUNNING = False

        self.COUNTER_SAVES = 0
        self.ALLOWED_SAVE = True

        self.counter_all_saves = 0
        self.last_means = []
        self.out_save_image = np.zeros((10, 10), dtype='uint8')
        self.saves_stack = dict()

        self.time_between_saves = times.Timer(self.time_between_saves_var.get())
        self.time_sleep = times.Timer(int(self.sleep_var.get()))
        self.timer_control_interval_on = times.Timer(60)
        self.timer_control_interval_off = times.Timer(60)
        t = stringvar2int(self.set_hour_on_var, 0, 0), stringvar2int(self.set_min_on_var, 0, 0)
        self.clock_control = times.Clock(t)

    
    def create_frames(self):
        border = {'relief':'groove', 'borderwidth':2}

        self.label_for_frame_camera = tk.Label(text='настройка камеры', font=self.main_font, padx=25,
                                               bg='#ffaa00', relief='groove', borderwidth=2)
        self.camera_frame = tk.LabelFrame(self.__window, borderwidth=2, 
                                          relief='groove', padx=5, pady=5,
                                          background=self.window_bg, labelanchor='n', 
                                          labelwidget=self.label_for_frame_camera, name='camera_frame')
        
        self.label_for_timer_frame = tk.Label(text='таймер вкл/выкл', font=self.main_font, padx=25,
                                              bg='#ffaa00', relief='groove', borderwidth=2)
        self.timer_frame = tk.LabelFrame(self.__window, borderwidth=2, 
                                         relief='groove', padx=5, pady=5,
                                         background=self.window_bg, labelanchor='n',  
                                         labelwidget=self.label_for_timer_frame)

        self.label_for_frame_bot = tk.Label(text='управление ботом', font=self.main_font, padx=25,
                                            bg='#ffaa00', relief='groove', borderwidth=2)
        self.bot_frame = tk.LabelFrame(self.__window, borderwidth=2, 
                                       relief='groove', padx=5, pady=5,
                                       background=self.window_bg, labelanchor='n', 
                                       labelwidget=self.label_for_frame_bot)

        self.label_for_out_saves = tk.Label(text='вывод сохранений', font=self.main_font, padx=25,
                                            bg='#ffaa00', relief='groove', borderwidth=2)
        self.out_saves_frame = tk.LabelFrame(self.__window, borderwidth=2, 
                                       relief='groove', padx=5, pady=5,
                                       background=self.window_bg, labelanchor='n',  
                                       labelwidget=self.label_for_out_saves)

        self.label_for_out_bot = tk.Label(text='вывод бота', font=self.main_font, padx=25,
                                            bg='#ffaa00', relief='groove', borderwidth=2)
        self.out_bot_frame = tk.LabelFrame(self.__window, borderwidth=2, 
                                       relief='groove', padx=5, pady=5,
                                       background=self.window_bg, labelanchor='n',  
                                       labelwidget=self.label_for_out_bot)
        
        self.camera_frame.rowconfigure(index=[*range(15)], weight=1)
        self.camera_frame.columnconfigure(index=[*range(2)], weight=1)
    
    def create_camera_widgets(self, master):
        width, height = master.winfo_width(), master.winfo_height()
        self.scale_time_between_save = tk.Scale(master, orient=tk.HORIZONTAL, from_=0.1, 
                                       to=3.0, length=width - width//3, font=self.default_font(11),
                                       tickinterval=0.4, resolution=0.1,
                                       background=self.window_bg, foreground=self.color_text, 
                                       variable=self.time_between_saves_var, label='время между сохр.')
        
        self.label_camera_id = tk.Label(master, text='ID камеры', font=self.default_font(11),
                                        bg=self.window_bg, fg=self.color_text)
        self.check_camera_id = ttk.Combobox(master, values=self.cam_ids, width=4, justify='center',
                                            textvariable=self.camera_id_var, font=self.default_font(11),
                                            background=self.color_orange1)
        
        self.label_num_sect = tk.Label(master, text='Кол-во секций (по меньшей стороне)', 
                                       font=self.default_font(11),bg=self.window_bg, fg=self.color_text)
        self.entry_num_sect = tk.Entry(master, font=self.default_font(11), width=5, 
                                       justify='center', textvariable=self.number_sect_var,
                                       bg=self.color_orange2)

        self.label_num_saves = tk.Label(master, text='Кол-во сохранений подряд', 
                                        font=self.default_font(11),bg=self.window_bg, fg=self.color_text)
        self.entry_num_saves = tk.Entry(master, font=self.default_font(11), width=5, 
                                        justify='center', textvariable=self.num_saves_var,
                                        bg=self.color_orange2)
        
        self.label_sleep = tk.Label(master, text='Время блокировки сохранений (сек.)', 
                                    font=self.default_font(11),bg=self.window_bg, fg=self.color_text)
        self.entry_sleep = tk.Entry(master, font=self.default_font(11), width=5, 
                                    justify='center', textvariable=self.sleep_var,
                                    bg=self.color_orange2)

        self.label_num_diff_sect = tk.Label(master, text='Разность секций между стар кадром и тек (%)', 
                                    font=self.default_font(11),bg=self.window_bg, fg=self.color_text)
        self.entry_num_diff_sect = tk.Entry(master, font=self.default_font(11), width=5, 
                                    justify='center', textvariable=self.num_diff_sect_var,
                                    bg=self.color_orange2)

        self.label_diff_between_sect = tk.Label(master, text='Кол-во отличающичся секций в кадре (%)', 
                                    font=self.default_font(11),bg=self.window_bg, fg=self.color_text)
        self.entry_diff_between_sect = tk.Entry(master, font=self.default_font(11), width=5,
                                    justify='center', textvariable=self.diff_between_sect_var,
                                    bg=self.color_orange2)

        self.btn_camera_start = tk.Button(master, text='начать', bg=self.not_active_btn,
                                          borderwidth=4, fg='#FBD653', font=self.default_font(16),
                                          relief='groove', width=15, command=self.start_camera, name='btn_camera_start')

    def create_timer_widgets(self, master):
        ...
        self.check_activate_timer = tk.Checkbutton(master, variable=self.active_timer_var, text='включить таймер',
                                                   bg=self.window_bg, font=self.default_font(11), fg=self.color_orange1,
                                                   anchor='w', highlightbackground=self.window_bg,
                                                   activebackground=self.window_bg, activeforeground=self.color_orange2,
                                                   command=self.on_off_timer)


        self.selector_timer_mode_shedule = tk.Radiobutton(master, variable=self.timer_mode_var, anchor='w',
                                                          value=0, text='включение и выключение в заданное время',
                                                          bg=self.window_bg, fg=self.color_orange1, borderwidth=0,
                                                          padx=1, pady=1, highlightbackground=self.window_bg,
                                                          activebackground=self.window_bg, activeforeground=self.color_orange2,
                                                          font=self.default_font(11), command=self.on_off_timer)
        
        self.label_time_on = tk.Label(master, text='время включения', 
                                      font=self.default_font(11),bg=self.window_bg, fg=self.color_text)
        self.entry_hour_on = tk.Entry(master, font=self.default_font(11), width=4, 
                                       justify='center', textvariable=self.set_hour_on_var,
                                       bg=self.color_orange2)
        self.label_hour_on = tk.Label(master, text='ч.', 
                                       font=self.default_font(11),bg=self.window_bg, fg=self.color_text)
        self.entry_min_on = tk.Entry(master, font=self.default_font(11), width=4, 
                                       justify='center', textvariable=self.set_min_on_var,
                                       bg=self.color_orange2)
        self.label_min_on = tk.Label(master, text='мин.', 
                                       font=self.default_font(11),bg=self.window_bg, fg=self.color_text)
        
        self.label_time_off = tk.Label(master, text='время выключения', 
                                       font=self.default_font(11),bg=self.window_bg, fg=self.color_text)
        self.entry_hour_off = tk.Entry(master, font=self.default_font(11), width=4, 
                                       justify='center', textvariable=self.set_hour_off_var,
                                       bg=self.color_orange2)
        self.label_hour_off = tk.Label(master, text='ч.', 
                                       font=self.default_font(11),bg=self.window_bg, fg=self.color_text)
        self.entry_min_off = tk.Entry(master, font=self.default_font(11), width=4, 
                                       justify='center', textvariable=self.set_min_off_var,
                                       bg=self.color_orange2)
        self.label_min_off = tk.Label(master, text='мин.', 
                                       font=self.default_font(11),bg=self.window_bg, fg=self.color_text)


        self.selector_timer_mode_interval = tk.Radiobutton(master, variable=self.timer_mode_var, anchor='w',
                                                           value=1, text='включение и выключение через заданные интервалы',
                                                           bg=self.window_bg, fg=self.color_orange1,borderwidth=0,
                                                           padx=1, pady=1, highlightbackground=self.window_bg,
                                                           activebackground=self.window_bg, activeforeground=self.color_orange2,
                                                           font=self.default_font(11), command=self.on_off_timer)
        
        self.label_duration_on = tk.Label(master, text='время работы', 
                                          font=self.default_font(11),bg=self.window_bg, fg=self.color_text)
        self.entry_dur_hour_on = tk.Entry(master, font=self.default_font(11), width=4, 
                                          justify='center', textvariable=self.dur_hour_on_var,
                                          bg=self.color_orange2)
        self.label_dur_hour_on = tk.Label(master, text='ч.', 
                                          font=self.default_font(11),bg=self.window_bg, fg=self.color_text)
        self.entry_dur_min_on = tk.Entry(master, font=self.default_font(11), width=4, 
                                         justify='center', textvariable=self.dur_min_on_var,
                                         bg=self.color_orange2)
        self.label_dur_min_on = tk.Label(master, text='мин.', 
                                         font=self.default_font(11),bg=self.window_bg, fg=self.color_text)
        
        self.label_duration_off = tk.Label(master, text='время паузы', 
                                          font=self.default_font(11),bg=self.window_bg, fg=self.color_text)
        self.entry_dur_hour_off = tk.Entry(master, font=self.default_font(11), width=4, 
                                          justify='center', textvariable=self.dur_hour_off_var,
                                          bg=self.color_orange2)
        self.label_dur_hour_off = tk.Label(master, text='ч.', 
                                          font=self.default_font(11),bg=self.window_bg, fg=self.color_text)
        self.entry_dur_min_off = tk.Entry(master, font=self.default_font(11), width=4, 
                                         justify='center', textvariable=self.dur_min_off_var,
                                         bg=self.color_orange2)
        self.label_dur_min_off = tk.Label(master, text='мин.', 
                                         font=self.default_font(11),bg=self.window_bg, fg=self.color_text)
        
    def create_bot_widgets(self, master):
        ...
        self.btn_stop_bot = tk.Button(master, text='stop', width=10, font=self.default_font(16),
                                      bg=self.not_active_btn, fg=self.color_orange2, command=self.stop_bot)
        self.btn_pause_bot = tk.Button(master, text='pause', width=10, font=self.default_font(16),
                                      bg=self.not_active_btn, fg=self.color_orange2)
        self.btn_start_bot = tk.Button(master, text='start', width=10, font=self.default_font(16),
                                      bg=self.not_active_btn, fg=self.color_orange2, command=self.start_bot)
    
    def create_output_widgets(self, master):
        self.info_text_saves = tk.Label(master, textvariable=self.info_text_save_var, bg=self.window_bg,
                                        fg='#22ff22', text='test', justify='left', anchor='nw',
                                        padx=10, pady=10, font=self.default_font(11))

    def placement_frame(self):
        ...
        width, height = ..., ...
        self.camera_frame.place(relx=0.01, rely=0.01, relwidth=0.32, relheight=0.97)
        self.timer_frame.place(relx=0.339, rely=0.01, relwidth=0.32, relheight=0.62)
        self.bot_frame.place(relx=0.339, rely=0.64, relwidth=0.32, relheight=0.34)
        self.out_saves_frame.place(relx=0.668, rely=0.01, relwidth=0.32, relheight=0.485)
        self.out_bot_frame.place(relx=0.668, rely=0.505, relwidth=0.32, relheight=0.475)

        self.camera_frame.update()

        # self.camera_frame.columnconfigure(index=0, weight=1)
        # self.camera_frame.columnconfigure(index=1, weight=1)

    def placement_widgets(self):
        self.scale_time_between_save.grid(row=0, column=0, columnspan=2, pady=35)
        width = self.camera_frame.winfo_width()
        self.scale_time_between_save.update()
        pad = (width - self.scale_time_between_save.winfo_width()) // 2
        self.scale_time_between_save.grid_configure(padx=pad)

        pad = dict({'pady':7, 'padx':[1, 45]})

        self.label_camera_id.grid(row=1, column=0,  sticky='e', **pad)
        self.check_camera_id.grid(row=1, column=1, sticky='e', **pad)

        self.label_num_sect.grid(row=2, column=0, sticky='e', **pad)
        self.entry_num_sect.grid(row=2, column=1, sticky='e', **pad)

        self.label_num_saves.grid(row=3, column=0, sticky='e', **pad)
        self.entry_num_saves.grid(row=3, column=1, sticky='e', **pad)

        self.label_sleep.grid(row=5, column=0, sticky='e', **pad)
        self.entry_sleep.grid(row=5, column=1, sticky='e', **pad)

        self.label_num_diff_sect.grid(row=6, column=0, sticky='e', **pad)
        self.entry_num_diff_sect.grid(row=6, column=1, sticky='e', **pad)

        self.label_diff_between_sect.grid(row=7, column=0, sticky='e', **pad)
        self.entry_diff_between_sect.grid(row=7, column=1, sticky='e', **pad)

        self.btn_camera_start.grid(row=8, column=0, columnspan=4, sticky='es', padx=30, pady=[60, 1])
        # self.btn_camera_start.place(relx=.6, rely=0.86, relwidth=0.3)

        # виджеты для таймера
        self.check_activate_timer.grid(row=0, column=0, columnspan=2, padx=2, pady=[30, 1], sticky='ew')

        self.selector_timer_mode_shedule.grid(row=1, column=0, columnspan=2, pady=[5, 10], padx=10, sticky='ew')

        self.label_time_on.grid(row=2, column=0, columnspan=4, sticky='w', padx=40, pady=[1, 15])
        self.entry_hour_on.grid(row=3, column=0, sticky='e')
        self.label_hour_on.grid(row=3, column=1, sticky='w', padx=4)
        self.entry_min_on.grid(row=3, column=2, sticky='w')
        self.label_min_on.grid(row=3, column=3, sticky='w', padx=4)

        self.label_time_off.grid(row=4, column=0, columnspan=4, sticky='w', padx=40, pady=[10, 15])
        self.entry_hour_off.grid(row=5, column=0, sticky='e')
        self.label_hour_off.grid(row=5, column=1, sticky='w', padx=4)
        self.entry_min_off.grid(row=5, column=2, sticky='w')
        self.label_min_off.grid(row=5, column=3, sticky='w', padx=4)

        self.selector_timer_mode_interval.grid(row=6, column=0, columnspan=4, pady=20, padx=10, sticky='ew')

        self.label_duration_on.grid(row=7, column=0, columnspan=4, sticky='w', padx=40, pady=[1, 15])
        self.entry_dur_hour_on.grid(row=8, column=0, sticky='e')
        self.label_dur_hour_on.grid(row=8, column=1, sticky='w', padx=4)
        self.entry_dur_min_on.grid(row=8, column=2, sticky='w')
        self.label_dur_min_on.grid(row=8, column=3, sticky='w', padx=4)

        self.label_duration_off.grid(row=9, column=0, columnspan=4, sticky='w', padx=40, pady=[10, 15])
        self.entry_dur_hour_off.grid(row=10, column=0, sticky='e')
        self.label_dur_hour_off.grid(row=10, column=1, sticky='w', padx=4)
        self.entry_dur_min_off.grid(row=10, column=2, sticky='w')
        self.label_dur_min_off.grid(row=10, column=3, sticky='w', padx=4)

        self.on_off_timer()

        # виджеты бота
        self.bot_frame.columnconfigure([0,1,2], weight=1)
        self.bot_frame.rowconfigure([0,1,2], weight=1)
        self.btn_stop_bot.grid(row=0, column=0, pady=100)
        self.btn_pause_bot.grid(row=0, column=1)
        self.btn_start_bot.grid(row=0, column=2)

        w, h = self.out_saves_frame.winfo_width(), self.out_saves_frame.winfo_height()
        self.info_text_saves.configure(width=w-20, height=h-20, bg='#505050')
        self.info_text_saves.pack(padx=10, pady=10, ipadx=10, ipady=10)
    
    def on_off_timer(self):
        timer_widgets = [self.entry_hour_on, self.entry_hour_off, self.entry_min_on,
                         self.entry_min_off, self.entry_dur_hour_on, self.entry_dur_hour_off,
                         self.entry_dur_min_on, self.entry_dur_min_off, 
                         self.selector_timer_mode_shedule, self.selector_timer_mode_interval]
        shedule_widgets = [self.entry_hour_on, self.entry_hour_off, 
                           self.entry_min_on, self.entry_min_off]
        interval_widgets = [self.entry_dur_hour_on, self.entry_dur_hour_off,
                            self.entry_dur_min_on, self.entry_dur_min_off]
        timer_state = self.active_timer_var.get()
        if not timer_state:
            [x.configure(state='disabled') for x in timer_widgets]
        else:
            [x.configure(state='normal') for x in timer_widgets]
            timer_mode_state = self.timer_mode_var.get()
            print(timer_mode_state)
            match timer_mode_state:
                case 0:
                    [x.configure(state='disabled') for x in interval_widgets]
                    [x.configure(state='normal') for x in shedule_widgets]
                case 1:
                    [x.configure(state='disabled') for x in shedule_widgets]
                    [x.configure(state='normal') for x in interval_widgets]

    def widgets(self):
        widgets.create_frames()
        widgets.placement_frame()
        widgets.create_camera_widgets(self.camera_frame)
        widgets.create_timer_widgets(self.timer_frame)
        widgets.create_bot_widgets(self.bot_frame)
        widgets.create_output_widgets(self.out_saves_frame)
        widgets.placement_widgets()
    
    def enabled_camera_widgets(self, *exclude, state=False):
        ...
        '''
        Если state == True, то виджеты tk.NORMAL
        '''
        widgets = self.camera_frame.children
        for w in widgets.values():
            if w.winfo_name in exclude: continue
            if w['state'] == 'disabled' and not state:
                w.configure(state=tk.NORMAL)
            elif w['state'] == 'normal' and state:
                w.configure(state=tk.DISABLED)
        widgets = self.timer_frame.children
        for w in widgets.values():
            if w.winfo_name in exclude: continue
            if w['state'] == 'disabled' and not state:
                w.configure(state=tk.NORMAL)
            elif w['state'] == 'normal' and state:
                w.configure(state=tk.DISABLED)

    def start_camera(self):
        self.START_BTN_PRESSED = not self.START_BTN_PRESSED
        if not self.START_BTN_PRESSED:
            self.btn_camera_start['bg'] = self.not_active_btn
        else:
            self.btn_camera_start['bg'] = self.active_btn
        # self.CAMERA_IS_RUN = not self.CAMERA_IS_RUN
        self.enabled_camera_widgets('btn_camera_start', state=self.START_BTN_PRESSED)

    def update_text(self):
        if self.__window.ESCAPE:
            self.__window.close()
        if self.CAMERA_IS_RUN:
            text = '\n'.join(self.out_text[:15])
            self.info_text_save_var.set('')
            self.info_text_save_var.set(str(randint(100, 10000)))
            # self.info_text_saves.update()
        self.info_text_saves.after(30, self.update_text)

    def start_bot(self):
        if not self.START_BOT_BTN_PRESSED:
            ...
            sp.run(['python', '/home/baron/coding/Python/EagleEye/tbot/tbot.py'])
            self.START_BOT_BTN_PRESSED = True
            self.STOP_BOT_BTN_PRESSED = False

    def stop_bot(self):
        if self.START_BOT_BTN_PRESSED:
            self.START_BOT_BTN_PRESSED = False
            self.STOP_BOT_BTN_PRESSED = True

    def run(self):
        self.out_text = self.out_text[:20]
        self.info_text_save_var.set('\n'.join(self.out_text))

        if self.START_BOT_BTN_PRESSED and not self.STOP_BOT_BTN_PRESSED:
            ...
        elif not self.START_BOT_BTN_PRESSED and self.STOP_BOT_BTN_PRESSED:
            ...

        if self.START_BTN_PRESSED:
            if self.TIME_CONTROL:
                if self.TIME_CONTROL_INTERVAL:
                    timer_on = self.timer_control_interval_on.is_start
                    timer_off = self.timer_control_interval_off.is_start
                    sig_on = self.timer_control_interval_on.signal()
                    sig_off = self.timer_control_interval_off.signal()

                    if not timer_on and not timer_off:
                        self.timer_control_interval_on.start()
                        self.CAMERA_IS_RUN = True
                    elif not timer_on and timer_off:
                        if sig_off:
                            self.timer_control_interval_on.start()
                            self.timer_control_interval_off.stop()
                            self.CAMERA_IS_RUN = True
                    elif timer_on and not timer_off:
                        if sig_on:
                            self.timer_control_interval_on.stop()
                            self.timer_control_interval_off.start()
                            self.CAMERA_IS_RUN = False
                elif self.TIME_CONTROL_CLOCK:
                    if not self.clock_control.is_active():
                        self.clock_control.start()
                    status = self.clock_control.signal()
                    if status and status == 1:
                        self.CAMERA_IS_RUN = True
                    elif status and status == 2:
                        self.CAMERA_IS_RUN = False
            else:
                self.CAMERA_IS_RUN = True
        
        else:
            self.CAMERA_IS_RUN = False
            self.timer_control_interval_on.stop()
            self.timer_control_interval_off.stop()
            self.clock_control.stop()

        # если камера запущена
        if self.CAMERA_IS_RUN:
            ret, frame = self.camera.read() # получение кадра
            if not ret: 
                self.camera.destroy()
                sys.exit(-1)
            
            # подготовка обрабатываемоего кадра
            proc_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            size = fp.get_new_size(proc_frame, width=300)
            num_sect_var = stringvar2int(self.number_sect_var, '', 30)
            size, numsections, sect_size = fp.calculate_sections(size, num_sections=num_sect_var)
            proc_frame = cv2.resize(proc_frame, size)
            proc_frame = cv2.GaussianBlur(proc_frame, (21, 21), 0)

            # текущее время для отображения на кадре
            current_time = times.get_timestr()
            cv2.rectangle(frame, self.__rect_poin1, self.__rect_point2, self.__text_bg, -1, cv2.LINE_AA)
            cv2.putText(frame, current_time, self.__text_coords, self.__font, 
                        self.__font_scale, self.__text_color, self.__thickness, cv2.LINE_AA)

            # координаты секций
            coords_sect = fp.coord_sections(proc_frame, numsections[0], numsections[1], sect_size)

            current_means = [] # массив с текущими средними значениями секций
            diff_percents = [0] # массив с процентной разницей между предыдущими и текущими средними значениями

            # заполнение массива с процентной разницей
            for i, (x1, y1, x2, y2) in enumerate(coords_sect):
                # текущее среднее значение секции
                current_mean_value = proc_frame[y1:y2, x1:x2].mean()
                current_means.append(current_mean_value)
                # если мвссив с предыдущими значениями существует и не пустой
                if self.last_means:
                    last_mean_value = self.last_means[i]
                    # расчет процентной разницы между старым и новым значением
                    diff = get_percent_diff(last_mean_value, current_mean_value)
                    diff_percents.append(diff)

            # массив из значений которые превышают или равны заданному
            num_diff_sect = stringvar2int(self.num_diff_sect_var, '8', 8)
            only_limit_diffs = list(filter(lambda x: x >= num_diff_sect, diff_percents))
            # расчет сколько процентов отличающихся секций от их общего числа
            percent_sections = len(only_limit_diffs) / len(diff_percents) * 100
            self.last_means = current_means.copy()

            # ===============================================================================================
            # ============== проверка условий для сохранения и сохранение изображений =======================
            # ===============================================================================================
            
            diff_between_sect = stringvar2int(self.diff_between_sect_var, '20', 20)
            is_percent_limit = percent_sections >= diff_between_sect

            if not self.ALLOWED_SAVE and is_percent_limit and not self.TIMER_BETWEEN_SAVES_RUNNING and not self.TIMER_SLEEP_RUNNING:
                self.ALLOWED_SAVE = True
            
            if self.ALLOWED_SAVE:
                if not self.time_between_saves.is_start:
                    self.TIMER_BETWEEN_SAVES_RUNNING = True
                    self.counter_all_saves += 1
                    self.COUNTER_SAVES += 1
                    self.time_between_saves.start()
                    filename = files.get_file_name(self.counter_all_saves, SAVES_DIR)
                    self.out_text.insert(0, str(filename))
                    save_image_size = fp.get_new_size(frame, width=1280)
                    save_image = cv2.resize(frame, save_image_size, cv2.INTER_NEAREST)
                    cv2.imwrite(filename, save_image)
                    self.out_save_image = fp.resize_frame(frame, 420)
                if self.time_between_saves.signal():
                    self.counter_all_saves += 1
                    self.COUNTER_SAVES += 1
                    filename = files.get_file_name(self.counter_all_saves, SAVES_DIR)
                    self.out_text.insert(0, str(filename))
                    save_image_size = fp.get_new_size(frame, width=1280)
                    save_image = cv2.resize(frame, save_image_size, cv2.INTER_NEAREST)
                    cv2.imwrite(filename, save_image)
                    self.out_save_image = fp.resize_frame(frame, 420)
            num_saves = stringvar2int(self.num_saves_var, '5', 5)
            if self.COUNTER_SAVES >= num_saves:
                print('Включение таймера ожидания', round(time.time() % 100, 2))
                self.COUNTER_SAVES = 0
                self.time_between_saves.stop()
                self.ALLOWED_SAVE = False
                self.time_sleep.start()
                self.TIMER_SLEEP_RUNNING = True
                self.TIMER_BETWEEN_SAVES_RUNNING = False
                self.last_means = []
            
            if self.time_sleep.signal():
                print('Снова готова к работе', round(time.time() % 100, 2))
                print(f'Время ожидания: в таймере - {self.time_sleep.interval}, в видж - {self.sleep_var.get()}')
                self.time_sleep.stop()
                self.TIMER_SLEEP_RUNNING = False
                

            # ===============================================================================================
            # ===============================================================================================

            cv2.waitKey(1)
            self.camera.show(frame)
            self.camera.show(self.out_save_image, 'save image')
        elif not self.CAMERA_IS_RUN and self.START_BTN_PRESSED:
            self.camera.close()
            if self.camera.cam_id != int(self.check_camera_id.get()):
                self.camera.set_camera_id(int(self.check_camera_id.get()))
            self.time_between_saves.stop()
            self.time_between_saves.interval = self.time_between_saves_var.get()
        
        elif not self.CAMERA_IS_RUN and not self.START_BTN_PRESSED:
            self.camera.close()
            self.last_means = []
            if self.camera.cam_id != int(self.check_camera_id.get()):
                self.camera.set_camera_id(int(self.check_camera_id.get()))
            self.time_between_saves.stop()

            self.time_between_saves.interval = self.time_between_saves_var.get()

            interval = stringvar2int(self.sleep_var, self.time_sleep.interval, 1)
            self.time_sleep.interval = interval

            self.TIME_CONTROL = self.active_timer_var.get()
            if self.TIME_CONTROL:
                temp_timer_mode = self.timer_mode_var.get()
                match temp_timer_mode:
                    case 0: self.TIME_CONTROL_CLOCK = True; self.TIME_CONTROL_INTERVAL = False
                    case 1: self.TIME_CONTROL_CLOCK = False; self.TIME_CONTROL_INTERVAL = True
                hour_on = stringvar2int(self.dur_hour_on_var, 0, 0)
                min_on = stringvar2int(self.dur_min_on_var, 1, 1)
                self.timer_control_interval_on.interval = hour_on*3600 + min_on*60
                hour_off = stringvar2int(self.dur_hour_off_var, 0, 0)
                min_off = stringvar2int(self.dur_min_off_var, 1, 1)
                self.timer_control_interval_off.interval = hour_off*3600 + min_off*60

                clock_hour_on = stringvar2int(self.set_hour_on_var, 0, 0)
                clock_hour_off = stringvar2int(self.set_hour_off_var, 0, 0)
                clock_min_on = stringvar2int(self.set_min_on_var, 0, 0)
                clock_min_off = stringvar2int(self.set_min_off_var, 1, 1)
                self.clock_control.time1 = clock_hour_on, clock_min_on
                self.clock_control.time2 = clock_hour_off, clock_min_off

            else:
                self.TIME_CONTROL_CLOCK = False
                self.TIME_CONTROL_INTERVAL = False




        self.__window.after(1, self.run)



if __name__ == '__main__':
    ...
    window = MainWindow()
    widgets = Widgets(window)
    widgets.widgets()
    widgets.run()

    window.mainloop()








