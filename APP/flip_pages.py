from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.lang import Builder
from kivy.config import Config
from kivy.core.window import Window

Window.clearcolor = (1, 1, 1, 1)

kv = """
#:import Window kivy.core.window.Window
FloatLayout:
    Label:
        pos_hint: {'center_x': 0.5, 'center_y': 0.1}
        size: 100, 50
        text: '0'
        color: 0, 0, 0, 1
        font_size: 32
    Image:
        source: 'cover.jpg'  # your image here
        size: Window.size
        size_hint: None, None       
    Button:
        pos_hint: {'center_x': 0.15, 'center_y': 0.5}
        size: 50, 50
        size_hint: None, None
        text: '<<'
    Button:
        pos_hint: {'center_x': 0.85, 'center_y': 0.5}
        size: 50, 50
        size_hint: None, None
        text: '>>'
"""

class VisualizerApp(App):
    def build(self):
        self.pages = ["cover.jpg", "book.jpg"]  # List of pages
        self.num_pages = 25
        self.current_page_index = 0  # Index of the current page
        
        self.image = Image(source=self.pages[self.current_page_index])  # Initial image
        
        # Navigation buttons
        self.prev_button = Button(text="<<")
        self.prev_button.bind(on_press=self.prev_page)
        self.next_button = Button(text=">>")
        self.next_button.bind(on_press=self.next_page)
        
        # Page name label
        
        # Layout
        layout = BoxLayout(orientation='vertical')
        
        layout2 = Builder.load_string(kv)
        layout.add_widget(layout2)
        
        print(layout2.children)
        layout2.children[1].bind(on_press=self.prev_page)
        layout2.children[0].bind(on_press=self.next_page)
        self.image = layout2.children[2]
        self.page_name_label = layout2.children[3]
        
        Config.set('graphics', 'background_color', '1,1,1,1')
        return layout

    def next_page(self, instance):
        if self.current_page_index < self.num_pages:
            self.current_page_index += 1
            self.update_page()

    def prev_page(self, instance):
        if self.current_page_index > 0:
            self.current_page_index -= 1
            self.update_page()
        
    def update_page(self):
        if self.current_page_index == 0:
            self.image.source = "cover.jpg"
            self.page_name_label.text = "0"
        else:
            self.image.source = "book.jpg"
            self.page_name_label.text = str(self.current_page_index)


if __name__ == '__main__':
    VisualizerApp().run()
