import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.core.text import LabelBase
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line
from kivy.clock import Clock
from kivy.uix.scrollview import ScrollView
import os
import numpy as np

import time
import cv2
from pathlib import Path
from utils_cluster import receive_image, send_image, execute_ssh_command
import dotenv
dotenv.load_dotenv()

HOSTNAME = os.getenv('HOSTNAME')
PORT     = os.getenv('PORT')
USERNAME = os.getenv('USERNAME')
PASWORD  = os.getenv('PASWORD')

import dotenv
#Read a the .env file
dotenv.load_dotenv()


# Folder from which we are going to send the images of the wacom output to the cluster
FOLDER_SENDING_FROM_LOCAL = Path('Outputs/Wacom/Png_final_results')

# Folder in which we are going to save the image of the text2Sketch model in the cluster
FOLDER_SAVING_TO_LOCAL = Path('Outputs/Sketch2image')

# Folder from which we are going to retrieve the images from the text2Sketch model
FOLDER_GETTING_FROM_CLUSTER = Path('/hhome/nlp2_g05/social_inovation/Generated_imgs')

# Set a white background
Window.clearcolor = (1, 1, 1, 1)

LabelBase.register(name='DownloadedFont', 
                   fn_regular='benton-sans-bold.ttf')

class LogIN(FloatLayout):
    def __init__(self, **kwargs):
        super(LogIN, self).__init__(**kwargs)

    def when_pressed(self):
        print("Login button pressed")


class Home(FloatLayout):
    def __init__(self, **kwargs):
        super(Home, self).__init__(**kwargs)

    def when_pressed(self):
        manager.switch_to(main_window, direction='down')

def save_function(curr_book, curr_page):
    drawing.export_to_png(f'./Books/{curr_book}/{curr_page}/tmp.png')

    white_img = np.array([[[255, 255, 255]]*500]*500, dtype=np.uint8)
    img = cv2.imread(f'./Books/{curr_book}/{curr_page}/tmp.png', cv2.IMREAD_UNCHANGED)
    img = cv2.resize(img, (500, 500))
    mask = img[:, :, 3]
    img = img[:, :, 0:3]
    white_img[mask == 0] = img[mask == 0]
    white_img = cv2.bitwise_not(white_img)
    cv2.imwrite(f'./Books/{curr_book}/{curr_page}/sketch.png', white_img)
    # Delete the temporary image

    # Update the sketch image
    sketch.reload()
    manager.switch_to(window_story, direction='down')
    os.remove(f'./Books/{curr_book}/{curr_page}/tmp.png')

     
class Drawing(FloatLayout):
    def __init__(self, **kwargs):
        super(Drawing, self).__init__(**kwargs)

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            with self.canvas:
                Color(0, 0, 0)
                touch.ud['line'] = Line(points=(touch.x, touch.y))

    def on_touch_move(self, touch):
        if self.collide_point(touch.x, touch.y):
            if 'line' in touch.ud:
                touch.ud['line'].points += (touch.x, touch.y)
            else:
                with self.canvas:
                    Color(0, 0, 0)
                    touch.ud['line'] = Line(points=(touch.x, touch.y))
        
def create_layout_draw(curr_book, curr_page):
    print("Window drawing", flush=True)
    background = Image(source='background_story_gen.jpg', fit_mode='fill')
    logo = Image(source='logo.png', size_hint=(0.25, 0.25), pos_hint={"x": 0.74, "y": 0.82})
    home = Home()

    # Create the whiteboard (White square where the user can draw)
    whiteboard = FloatLayout()
    whiteboard.add_widget(Image(source='whiteboard.png', size_hint=(0.8, 0.8), pos_hint={"x": 0.125, "y": 0.1}))
    global drawing
    drawing = Drawing(size_hint=(0.39, 0.8), pos_hint={"x": 0.33, "y": 0.1})
    whiteboard.add_widget(drawing)

    layout = BoxLayout(orientation='vertical')
    layout.add_widget(whiteboard)

    
    layout_buttons = BoxLayout(orientation='horizontal', size_hint=(0.35, 0.1), pos_hint={"x":0.325 ,"y": 0.3})
    no_changes = Button(text='No changes', font_name='DownloadedFont', font_size=22)

    no_changes.bind(on_press=lambda *args:manager.switch_to(window_story, direction='down'))


    button_save = Button(text='Save', font_name='DownloadedFont', font_size=22)
    button_save.bind(on_press=lambda *args:save_function(curr_book, curr_page))
    button_clear = Button(text='Clear', font_name='DownloadedFont', font_size=22)
    button_clear.bind(on_press=lambda *args:drawing.canvas.clear())
    layout_buttons.add_widget(button_save)
    layout_buttons.add_widget(no_changes)
    layout_buttons.add_widget(button_clear)
    layout.add_widget(layout_buttons)

    final_layout = FloatLayout()
    final_layout.add_widget(background)
    final_layout.add_widget(layout)
    final_layout.add_widget(logo)
    final_layout.add_widget(home)
    return final_layout

def next_page_function(curr_book, curr_page):
    curr_page_int = int(curr_page)
    window_story.clear_widgets()
    window_story.add_widget(create_layout_story_gen(curr_book, str(curr_page_int + 1)))
    manager.switch_to(window_story, direction='left')

def prev_page_function(curr_book, curr_page):
    curr_page_int = int(curr_page)
    if curr_page_int > 1:
        new_page = curr_page_int - 1
    
    window_story.clear_widgets()
    window_story.add_widget(create_layout_story_gen(curr_book, str(new_page)))
    manager.switch_to(window_story, direction='right')

def sketch2img(curr_book, curr_page):
    # Load the sketch
    print("\n\ncurrent book:", curr_book, curr_page)
    send_image(f'./Books/{curr_book}/{curr_page}/sketch.png', 
           '/hhome/nlp2_g05/social_inovation/Sketches', 
           HOSTNAME, 
           PORT,
           USERNAME, 
           PASWORD)
    
    time.sleep(1)
    
    execute_ssh_command(HOSTNAME, PORT, USERNAME, PASWORD, "bash /hhome/nlp2_g05/social_inovation/bash_script.sh")
    
    time.sleep(1)
    receive_image(remote_image_path = FOLDER_GETTING_FROM_CLUSTER / "image.png",
                  local_path        = f'./Books/{curr_book}/{curr_page}/image.png',
                  hostname          = HOSTNAME,
                  port              = PORT,
                  username          = USERNAME,
                  password          = PASWORD)
    
    time.sleep(1)
    print("\n\nAttribute ", gen_Image.source)
    gen_Image.reload()
    # Call the function that will generate the image

def create_layout_story_gen(curr_book, curr_page):
    # Check if the folder exists, if not create it
    if not os.path.exists(f'./Books/{curr_book}/{curr_page}'):
        os.mkdir(f'./Books/{curr_book}/{curr_page}')

    # Add the current page and book to the layout in black color
    book = Label(text=f'BOOK: {curr_book}',
                pos_hint={"x": -0.4, "y": 0.443}, 
                color=(0, 0, 0, 1),
                font_name='DownloadedFont',
                font_size=30)

    page = Label(text=f'MODIFING PAGE {curr_page}',
                        pos_hint={"y": 0.443}, 
                        color=(0, 0, 0, 1),
                        font_name='DownloadedFont',
                        font_size=30)

    background = Image(source='background_story_gen.jpg', fit_mode='fill')
    logo = Image(source='logo.png', size_hint=(0.25, 0.25), pos_hint={"x": 0.74, "y": 0.82})
    home = Home()

    sketch_layout = BoxLayout(orientation='vertical')
    buttons_sketch = BoxLayout(orientation='horizontal', size_hint=(0.8, 0.1), pos_hint={"x": 0.1})
    button1 = Button(text='Update the skecth', font_name='DownloadedFont', font_size=22)

    # Delete all widets on window_drawing 
    window_drawing.clear_widgets()
    window_drawing.add_widget(create_layout_draw(curr_book, curr_page))

    button1.bind(on_press=lambda *args:manager.switch_to(window_drawing, direction='up'))
    # Widget to input the text to condition the image generation, textinput.text is the text entered
    textinput = TextInput(text='Text to condition image generation', font_name='DownloadedFont', font_size=17)
    buttons_sketch.add_widget(button1)
    buttons_sketch.add_widget(textinput)
    
    # If the sketch does not exist, create a white sketch of 500x500 pixels
    if not os.path.exists(f'./Books/{curr_book}/{curr_page}/sketch.png'):
        white_img = np.array([[[255, 255, 255]]*500]*500, dtype=np.uint8)
        cv2.imwrite(f'./Books/{curr_book}/{curr_page}/sketch.png', white_img)

    global sketch
    sketch = Image(source=f'./Books/{curr_book}/{curr_page}/sketch.png', size_hint=(1, 1))

    sketch_layout.add_widget(sketch)
    sketch_layout.add_widget(buttons_sketch)

    gen_Image_layout = BoxLayout(orientation='vertical')
    
    global gen_Image
    gen_Image = Image(source=f'/home/nbiescas/Desktop/Story-Generation-1/Books/{curr_book}/{curr_page}/image.png', size_hint=(1, 1))
    
    genText = Button(text='Generate the text for this page',  size_hint=(0.8, 0.1), pos_hint={"x": 0.1}, font_name='DownloadedFont', font_size=22)
    gen_Image_layout.add_widget(gen_Image)
    gen_Image_layout.add_widget(genText)

    sketchAndGen = BoxLayout(orientation='horizontal', size_hint=(1, 0.8), pos_hint={"y": 0.15})
    sketchAndGen.add_widget(sketch_layout)
    sketchAndGen.add_widget(gen_Image_layout)

    layout = FloatLayout()
    layout.add_widget(background)
    layout.add_widget(sketchAndGen)
    layout.add_widget(logo)
    layout.add_widget(home)

    next_page = Button(text='->', size_hint=(0.05, 0.05), pos_hint={"x": 0.94, "y": 0.475})
    next_page.bind(on_press=lambda *args:next_page_function(curr_book, curr_page))

    imgGeneration_button = Button(text='Generate\nImage', size_hint=(0.1, 0.1), pos_hint={"x": 0.45, "y": 0.5}, font_name='DownloadedFont', font_size=22)
    imgGeneration_button.bind(on_press=lambda *args:sketch2img(curr_book, curr_page))

    
    if int(curr_page) > 1:
        prev_page = Button(text='<-', size_hint=(0.05, 0.05), pos_hint={"x": 0.01, "y": 0.475}) 
        prev_page.bind(on_press=lambda *args:prev_page_function(curr_book, curr_page))
        layout.add_widget(prev_page)

    layout.add_widget(imgGeneration_button)
    layout.add_widget(next_page)
    layout.add_widget(book)
    layout.add_widget(page)
    return layout

def load_collection():
    window_collection.clear_widgets()
    window_collection.add_widget(create_layout_collection())
    manager.switch_to(window_collection, direction='up')

def create_story(curr_book):
    window_story.clear_widgets()
    window_story.add_widget(create_layout_story_gen(curr_book, '1'))
    manager.switch_to(window_story, direction='up')

def create_layout_menu():
    background = Image(source='backgorund_menu.png', fit_mode='fill')
    logo = Image(source='logo.png', pos_hint={"y": 0.1})
    
    # Layout buttons
    layout_b = BoxLayout(orientation='horizontal', size_hint=(0.8, 0.2), pos_hint={"x": 0.1})
    button1 = Button(text='CREATE A NEW STORY', font_name='DownloadedFont', font_size=25)


    # Look at folder Books to see the number of books and pages
    # Create a new book with the number of books + 1
    books = os.listdir('./Books')
    curr_book = str(len(books) + 1)
    os.mkdir(f'./Books/{curr_book}')

    button1.bind(on_press=lambda *args:create_story(curr_book))

    button2 = Button(text='VISUALIZE A STORY', font_name='DownloadedFont', font_size=25)
    button2.bind(on_press=lambda *args: manager.switch_to(window_visualizer, direction='up'))

    button3 = Button(text='COLLECTION OF STORIES', font_name='DownloadedFont', font_size=25)
    button3.bind(on_press=lambda *args: load_collection())
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


def create_layout_visualizer():
    background = Image(source='background_story_gen.jpg', fit_mode='fill')
    logo = Image(source='logo.png', size_hint=(0.25, 0.25), pos_hint={"x": 0.74, "y": 0.82})
    home = Home()

    book_layout = BoxLayout(orientation='vertical')
    page1_text = Label(text='Page 1 Text\n\nExample text for page 1', halign='center', valign='middle')
    page2_text = Label(text='Page 2 Text\n\nExample text for page 2', halign='center', valign='middle')
    # Add more pages as needed

    page1 = BoxLayout(orientation='vertical')
    page1.add_widget(page1_text)

    page2 = BoxLayout(orientation='vertical')
    page2.add_widget(page2_text)

    # Add more pages as needed

    pages = [page1, page2]  # Add more pages as needed

    current_page_index = 0
    current_page = pages[current_page_index]

    def next_page():
        nonlocal current_page_index
        current_page_index = min(current_page_index + 1, len(pages) - 1)
        update_page()

    def previous_page():
        nonlocal current_page_index
        current_page_index = max(current_page_index - 1, 0)
        update_page()

    def update_page():
        nonlocal current_page
        current_page = pages[current_page_index]
        book_layout.remove_widget(book_layout.children[0])
        book_layout.add_widget(current_page)

    next_button = Button(text='Next Page')
    next_button.bind(on_press=lambda *args: next_page())

    prev_button = Button(text='Previous Page')
    prev_button.bind(on_press=lambda *args: previous_page())

    buttons_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))
    buttons_layout.add_widget(prev_button)
    buttons_layout.add_widget(next_button)

    book_layout.add_widget(current_page)
    book_layout.add_widget(buttons_layout)

    layout = FloatLayout()
    layout.add_widget(background)
    layout.add_widget(book_layout)
    layout.add_widget(logo)
    layout.add_widget(home)

    return layout

def edit_book(book):
    pages = os.listdir(f'./Books/{book}')
    pages = sorted(pages, key=lambda x: int(x))
    window_story.clear_widgets()
    for page in pages:
        window_story.add_widget(create_layout_story_gen(book, 1))
    manager.switch_to(window_story, direction='up')

def vis_book(book):
    pass

def create_layout_collection():
    background = Image(source='backgorund_menu.png', fit_mode='fill')
    logo = Image(source='logo.png', size_hint=(0.25, 0.25), pos_hint={"x": 0.74, "y": 0.82})
    title = Label(text=f'STORY COLLECTION',
                        pos_hint={"y": 0.443}, 
                        color=(0, 0, 0, 1),
                        font_name='DownloadedFont',
                        font_size=30)
    home = Home()

    books = os.listdir('./Books')
    books = sorted(books, key=lambda x: int(x))
    books_layouts = BoxLayout(orientation='vertical', size_hint_y=None, spacing=3)
    books_layouts.bind(minimum_height=books_layouts.setter('height'))

    for book in books:
        num_pages = len(os.listdir(f'./Books/{book}'))
        book_layout = BoxLayout(orientation='horizontal', size_hint=(0.8, None), height=50)
        book_layout.add_widget(Label(text=f'Book {book}, number of pages {num_pages}', 
                                     font_name='DownloadedFont', font_size=22,
                                     color=(0, 0, 0, 1)))
        book_layout.add_widget(Button(text='Edit', font_name='DownloadedFont', 
                                      font_size=22, size_hint=(0.5, 1),
                                      on_press=lambda *args, book=book: edit_book(book)))
        book_layout.add_widget(Button(text='Visualize', font_name='DownloadedFont', 
                                      font_size=22, size_hint=(0.5, 1),
                                      on_press=lambda *args, book=book: vis_book(book)))
        
        books_layouts.add_widget(book_layout)

    books_layout = ScrollView(size_hint=(1, 0.8), pos_hint={"x":0.05, "y": 0.06})
    books_layout.add_widget(books_layouts)

    layout = FloatLayout()
    layout.add_widget(background)
    layout.add_widget(logo)
    layout.add_widget(home)
    layout.add_widget(books_layout)
    layout.add_widget(title)
    return layout


class MenuApp(App):
    def build(self):
        global manager, main_window, window_story, window_drawing, window_visualizer, window_collection

        if not os.path.exists('./Books'):
            os.mkdir('./Books')

        app_box = BoxLayout(orientation='vertical')
        manager = ScreenManager()
        app_box.add_widget(manager)

        main_window = Screen(name='main')
        window_story = Screen(name='Story generator')
        window_drawing = Screen(name='Drawing')
        window_visualizer = Screen(name='Visualizer')
        window_collection = Screen(name='Collection')

        main_window.add_widget(create_layout_menu())
        window_visualizer.add_widget(create_layout_visualizer())

        manager.add_widget(main_window)
        manager.add_widget(window_story)
        manager.add_widget(window_drawing)
        manager.add_widget(window_visualizer)
        manager.add_widget(window_collection)

        return app_box




if __name__ == '__main__':
    """
    Thinks that we might change:
    - Put all the images of the desing of the app in folders
    """
    app = MenuApp()
    app.run()




    
