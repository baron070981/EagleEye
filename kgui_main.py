from kivy.config import Config
Config.set('graphics','width','1200')
Config.set('graphics','height','700')

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




class ScreenManag(ScreenManager):
    mainrunwindow = ObjectProperty(None)




class MainApp(MDApp):
    
    def build(self):
        Builder.load_file('kv/main.kv')
        # self.theme_cls.primary_palette =  "Blue"
        # self.theme_cls.primary_hue =  "900"
        # self.theme_cls.theme_style = "Dark" 
        return ScreenManag()
    


if __name__ == '__main__':
    app = MainApp()
    app.run()




















