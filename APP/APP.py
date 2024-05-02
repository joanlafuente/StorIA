import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen


class LogIN(FloatLayout):
    def __init__(self, **kwargs):
        super(LogIN, self).__init__(**kwargs)

    def when_pressed(self):
        print("Login button pressed")

def create_layout_story_gen():
    background = Image(source='backgorund_menu.png', fit_mode='fill')
    logo = Image(source='logo.png', size_hint=(0.25, 0.25), pos_hint={"x": 0.74, "y": 0.82})
    
    
    layout = FloatLayout()
    layout.add_widget(background)
    layout.add_widget(logo)
    return layout

def create_layout_menu():
    background = Image(source='backgorund_menu.png', fit_mode='fill')
    logo = Image(source='logo.png', pos_hint={"y": 0.15})
    
    # Layout buttons
    layout_b = BoxLayout(orientation='horizontal', size_hint=(1, 0.2))
    button1 = Button(text='Create a new story')
    button1.bind(on_press=lambda *args:manager.switch_to(window_story, direction='up'))

    button2 = Button(text='Stories in creation')
    button3 = Button(text='Collection of stories')
    layout_b.add_widget(button1)
    layout_b.add_widget(button2)
    layout_b.add_widget(button3)     
    
    login = LogIN()
    
    # Join all layouts
    layout = FloatLayout()
    layout.add_widget(background)
    layout.add_widget(login)
    layout.add_widget(logo)
    layout.add_widget(layout_b)
    return layout



class MenuApp(App):
    def build(self):
        global manager, main_window, window_story

        app_box = BoxLayout(orientation='vertical')
        manager = ScreenManager()
        app_box.add_widget(manager) 
            
        main_window = Screen(name='main')
        window_story = Screen(name='Story generator')

        main_window.add_widget(create_layout_menu())
        window_story.add_widget(create_layout_story_gen())
        
        manager.add_widget(main_window)
        manager.add_widget(window_story)
        return app_box





# Run the App
app = MenuApp()
app.run()

    