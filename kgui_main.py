from screeninfo import get_monitors

mon = get_monitors()
w = mon[0].width
h = mon[0].height


from kivy.config import Config
Config.set('graphics','width',f'{w}')
Config.set('graphics','height',f'{h}')


from kivymd.app import MDApp
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.list import OneLineListItem
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.button import MDIconButton
from kivymd.theming import ThemeManager as tm

from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.properties import BooleanProperty
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.lang import Builder


import cv2


from eagleeye import camera
from kguirun import RunScreen



class ScreenManag(ScreenManager):
    runscreen = ObjectProperty(None)




class MainApp(MDApp):
    Builder.load_file('kv/main.kv')
    def __init__(self):
        super().__init__()
        self.cam = camera.Camera(300)
    
    def build(self):
        self.theme_cls.primary_palette =  "Blue"
        self.theme_cls.primary_hue =  "900"
        self.theme_cls.theme_style = "Dark"
        
        return ScreenManag()
    


if __name__ == '__main__':
    app = MainApp()
    app.run()




















