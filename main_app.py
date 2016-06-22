from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.image import Image
from kivy.uix.scatter import Scatter
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty
from kivy.config import Config
from TestKivyImgViewer import config
Config.set('graphics', 'width', config.width)
Config.set('graphics', 'height', config.height)
from kivy.core.window import Window
import os
import sys
import json


Config.set('input', 'mouse', 'mouse,disable_multitouch')


class PopUpFileBrowser(Popup):

    def __init__(self, location=None, **kwargs):
        super(PopUpFileBrowser, self).__init__(**kwargs)
        self.drives = list()
        if location is None:
            self.cur_path = os.getcwd()
            init_path = self.get_init_path()
        else:
            self.cur_path = location
            init_path = location
        self.file_name = None
        self.browser = FileChooserIconView(path=init_path, filters=['*.png', '*.jpeg', '*.jpg'], size_hint_y=0.6,
                                           on_entries_cleared=self.on_change_dir, on_submit=self.on_submit_file)

        self.grid = GridLayout(cols=1, rows=3)

        self.cur_path_text = TextInput(text=self.cur_path, size_hint_y=0.1)
        self.drives_box = BoxLayout(orientation="horizontal", size_hint_y=0.2)
        self.get_drives()

        # add widgets
        self.grid.add_widget(self.cur_path_text)
        self.grid.add_widget(self.browser)
        self.grid.add_widget(self.drives_box)

        # add to popup
        self.add_widget(self.grid)

    def get_drives(self):
        if sys.platform == 'win32':
            import win32api
            drive = win32api.GetLogicalDriveStrings()
            drives = drive.split('\000')[:-1]
            self.drives = drives

            for i in self.drives:
                print(str(i))
                drive_btn = Button(text=i, on_press=self.on_change_drive)
                self.drives_box.add_widget(drive_btn)

    def get_init_path(self):
        if sys.platform == 'win32':
            import win32api
            drive = win32api.GetLogicalDriveStrings()
            drives = drive.split('\000')[:-1]
            return drives[0]


    def on_change_dir(self, obj):
        print(obj.path)
        self.cur_path_text.text = obj.path

    def on_change_drive(self, btn):
        self.browser.path = btn.text

    def on_submit_file(self, obj, selected, touch):
        self.file_name = selected[0]
        self.dismiss()


class MainBox(BoxLayout):
    cfg_name = "path_cfg.json"

    def __init__(self, **kwargs):
        super(MainBox, self).__init__(**kwargs)
        self.pic_path = None
        self.pic_name = ""
        self.popup = ObjectProperty(None)
        self.file_names = list()
        self.cur_file_pos = 0
        # layout
        grid = GridLayout(cols=1, rows=2)
        top_grid = BoxLayout(size_hint_y=0.8)
        bot_grid = GridLayout(cols=2, rows=1, size_hint_y=0.2)
        detail_grid = GridLayout(rows=2, cols=1, size_hint_x=0.7, padding=[0, 0, 0, 50])

        browse_btn = Button(text="Load", size_hint_x=0.3)
        browse_btn.bind(on_press=self.open_file_browser)
        self.pic_path_label = Label(text="Location", size_hint_y=0.5, text_size=(800, None))
        self.pic_label = Label(text="No pic", size_hint_y=0.5, text_size=(800, None))
        self.img = Image(source=None)

        # add widgets
        detail_grid.add_widget(self.pic_label)
        detail_grid.add_widget(self.pic_path_label)

        top_grid.add_widget(self.img)
        bot_grid.add_widget(browse_btn)
        bot_grid.add_widget(detail_grid)

        grid.add_widget(top_grid)
        grid.add_widget(bot_grid)

        # add to box
        self.add_widget(grid)

        self._keyboard = Window.request_keyboard(self._keyboard_closed, self, 'text')
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self.read_path()
        Window.bind(on_motion=self.on_motion)

    def set_detail(self):
        self.pic_label.text = self.pic_name
        self.pic_path_label.text = "Location : " + self.pic_path + "\\" + self.pic_name

    def open_file_browser(self, e):
        self.popup = PopUpFileBrowser(location=MainBox.read_path(), title="File browser", on_dismiss=self.on_selected_pic)
        self.popup.open()

    def list_image_files(self):
        self.file_names = list()
        files = os.listdir(self.pic_path)
        c = 0
        for name in files:
            pos_dot = name.rfind('.')
            ext = name[pos_dot:].replace(".", "").lower()
            if ext in config.allow_ext:
                self.file_names.append(name)
                if name == self.pic_name:
                    self.cur_file_pos = c
                    print("now ", self.cur_file_pos)
                c += 1

    def change_pic(self, dif):
        pic_amount = len(self.file_names)
        try:
            self.cur_file_pos += dif
            if self.cur_file_pos < 0:
                self.cur_file_pos = pic_amount-1
            elif self.cur_file_pos > pic_amount-1:
                self.cur_file_pos = 0
            self.pic_name = self.file_names[self.cur_file_pos]
            print(self.cur_file_pos)
            self.img.source = self.pic_path + "\\" + self.pic_name
            self.set_detail()
        except IndexError:
            pass

    def on_selected_pic(self, e):
        try:
            file = e.file_name
            e_names = file.split('\\')
            self.pic_name = e_names[len(e_names)-1]
            self.pic_label.text = e_names[len(e_names)-1]
            self.pic_path = file.replace(self.pic_name, "")
            self.pic_path_label.text = "Location : " + file
            self.img.source = file
            self.list_image_files()
            MainBox.save_path(self.pic_path)
            print(repr(self))
        except AttributeError:
            pass

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[0] == 275:  # right
            self.change_pic(1)
        elif keycode[0] == 276:  # left
            self.change_pic(-1)

    def on_motion(self, obj, etype, event):
        event_act = event.button
        if event_act == 'scrollup' or event_act == 'scrolldown':
            print(event_act)

    @staticmethod
    def save_path(pic_path):
        file = open(MainBox.cfg_name, "w")
        path = {"path": pic_path}
        data_json = json.JSONEncoder().encode(path)
        file.write(data_json)
        file.close()

    @staticmethod
    def read_path():
        try:
            file = open(MainBox.cfg_name, "r")
            data_json = json.JSONDecoder().decode(file.read())
            return data_json['path']
            file.close()
        except FileNotFoundError:
            return None


class MainApp(App):
    def build(self):
        print(os.getcwd())
        return MainBox(orientation="vertical")

MainApp().run()
