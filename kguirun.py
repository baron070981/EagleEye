from kivymd.app import MDApp
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
from kivy.properties import BooleanProperty, ObjectProperty
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.lang import Builder

import cv2

from eagleeye import camera



class RunScreen(Screen):
    
    frame = ObjectProperty(None)
    
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.video_state = False
        self.frame = None


    def on_run_camera(self):
        ...


from kivy.app import App
from kivy.uix.image import Image 
from kivy.clock import Clock 
from kivy.graphics.texture import Texture 
import cv2 
from kivy.uix.boxlayout import BoxLayout 
from kivy.uix.gridlayout import GridLayout 
from kivy.uix.widget import Widget 
from kivy.uix.button import Button 






if __name__ == "__main__":
    
    class Test(MDApp):
        #generaldataview = ObjectProperty(None)
        Builder.load_file('kv/kguirunscreen.kv')
        def __init__(self):
            super(Test,self).__init__()
        
        def build(self):
            return RunScreen()
    Test().run()




