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
from kivy.uix.checkbox import CheckBox
from kivy.uix.switch import Switch
import os
import numpy as np
from blend_modes import darken_only
import threading

from PIL import Image as PILImage
import time
import cv2
from pathlib import Path
from myapp.utils_cluster import receive_image, send_image, execute_ssh_command
import dotenv
dotenv.load_dotenv()

global loged_in
loged_in = False

HOSTNAME = os.getenv('HOSTNAME')
PORT     = os.getenv('PORT')
USERNAME = os.getenv('USERNAME_CLUSTER')
PASWORD  = os.getenv('PASWORD')

import dotenv
#Read a the .env file
dotenv.load_dotenv()

# Get the entire path to ./Books folder
BOOKS = "./Books"

# Folder from which we are going to retrieve the images from the text2Sketch model
#FOLDER_GETTING_FROM_CLUSTER = Path('/hhome/nlp2_g05/social_inovation/Generated_imgs')
FOLDER_GETTING_FROM_CLUSTER = '/hhome/nlp2_g05/social_inovation/Generated_imgs'
FOLDER_GETTING_FROM_CLUSTER_TXT = '/hhome/nlp2_g05/social_inovation/Generated_txt'# Set a white background
Window.clearcolor = (1, 1, 1, 1)

LabelBase.register(name='DownloadedFont', 
                   fn_regular='./myapp/assets/benton-sans-bold.ttf')

class PasswordInput(TextInput):
    def __init__(self, **kwargs):
        super(PasswordInput, self).__init__(**kwargs)
        self.password = True
        
    # write *** instead of the text
    def _get_text(self):
        return '*' * len(self.text)

class Home(FloatLayout):
    def __init__(self, **kwargs):
        super(Home, self).__init__(**kwargs)
        
        # Create the home button from the image home.png
        home = Button(size_hint=(0.075, 0.1), pos_hint={"x": 0.01, "y": 0.88}, background_normal = './myapp/assets/home.png') 
        home.bind(on_press=lambda *args:manager.switch_to(main_window, direction='down'))
                
        self.add_widget(home)


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

    # Draw image
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

class Colors(FloatLayout):
    def __init__(self, **kwargs):
        super(Colors, self).__init__(**kwargs)

        self.colors = [(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0), (1, 0, 1), (0, 1, 1)]
        self.current_color = self.colors[0]

        self.color_buttons = []
        for i, color in enumerate(self.colors):
            button = Button(size_hint=(0.3, 0.1), pos_hint={"x": 0.1, "y": 0.1 + i*0.1}, background_color=color)
            button.bind(on_press=lambda *args:self.change_color(color))
            self.color_buttons.append(button)
            self.add_widget(button)

    def change_color(self, color):
        drawing.canvas.add(Color(*color))
        self.current_color = color
        
class brush_size(FloatLayout):
    def __init__(self, **kwargs):
        super(brush_size, self).__init__(**kwargs)
        self.brush_sizes = [1, 2]
        self.current_size = self.brush_sizes[0]

        imagen = Image(source='./myapp/assets/brush_size.png', size_hint=(0.3, 0.7), pos_hint={"x": 0.1, "y": 0})
        self.add_widget(imagen)

        for i in range(5): 
            button = Button(size_hint=(0.1, 0.1), pos_hint={"x": 0.1 + i*0.1, "y": 0.1}, background_color=(0, 0, 0, 0))
            button.bind(on_press=lambda *args:self.change_size(i+1))
            self.add_widget(button)

        # factor = 0.02
        # self.size_buttons = []
        # prev_y = 0.1
        # prev_x = 0.15 + (factor*5/2)*0.3
        # for i, size in enumerate(self.brush_sizes):
        #     print(factor*size, factor*size, prev_x, prev_y)
        #     button = Button(size_hint=(0.1 + factor*size, 0.1 +factor*size), pos_hint={"x": prev_x, "y": prev_y}, background_normal = './myapp/assets/brush.png')
        #     button.bind(on_press=lambda *args:self.change_size(size))
        #     self.size_buttons.append(button)
        #     self.add_widget(button)
        #     prev_y += size*factor + 0.05
        #     prev_x -= ((0.1 + (size*factor))/2)*0.3

    def change_size(self, size):
        drawing.canvas.add(Line(width=size))
        
def create_layout_draw(curr_book, curr_page):
    print("Window drawing", flush=True)
    background = Image(source='./myapp/assets/background_story_gen.jpg', fit_mode='fill')
    logo = Image(source='./myapp/assets/logo.png', size_hint=(0.25, 0.25), pos_hint={"x": 0.74, "y": 0.82})
    home = Home()

    # Create the whiteboard (White square where the user can draw)
    whiteboard = FloatLayout()
    whiteboard.add_widget(Image(source='./myapp/assets/whiteboard.png', size_hint=(0.8, 0.8), pos_hint={"x": 0.125, "y": 0.1}))
    global drawing
    drawing = Drawing(size_hint=(0.39, 0.8), pos_hint={"x": 0.33, "y": 0.1})
    whiteboard.add_widget(drawing)

    colors = Colors(size_hint=(0.3, 0.5), pos_hint={"x": 0.07, "y": 0.20})
    whiteboard.add_widget(colors)
    
    brush = brush_size(size_hint=(0.3, 0.5), pos_hint={"x": 0.07, "y": 0.55})
    whiteboard.add_widget(brush)
    
    no_changes = Button(text='x', font_name='DownloadedFont', font_size=22, size_hint=(0.1, 0.1), pos_hint={"x": 0.8, "y": 0.8})
    no_changes.bind(on_press=lambda *args:manager.switch_to(window_story, direction='down'))
    whiteboard.add_widget(no_changes)

    layout = BoxLayout(orientation='vertical')
    layout.add_widget(whiteboard)
    
    layout_buttons = BoxLayout(orientation='horizontal', size_hint=(0.35, 0.1), pos_hint={"x":0.325 ,"y": 0.3})


    button_save = Button(text='Save', font_name='DownloadedFont', font_size=22)
    button_save.bind(on_press=lambda *args:save_function(curr_book, curr_page))
    button_clear = Button(text='Clear', font_name='DownloadedFont', font_size=22)
    button_clear.bind(on_press=lambda *args:drawing.canvas.clear())
    layout_buttons.add_widget(button_save)
    layout_buttons.add_widget(button_clear)
    layout.add_widget(layout_buttons)

    final_layout = FloatLayout()
    final_layout.add_widget(background)
    final_layout.add_widget(layout)
    final_layout.add_widget(logo)
    final_layout.add_widget(home)
    return final_layout

def create_layout_edit_text(curr_book, curr_page):
    layout = FloatLayout()
    background = Image(source='./myapp/assets/background_story_gen.jpg', fit_mode='fill')
    logo = Image(source='./myapp/assets/logo.png', size_hint=(0.25, 0.25), pos_hint={"x": 0.74, "y": 0.82})
    home = Home()

    if not os.path.exists(f'./Books/{curr_book}/{curr_page}/text.txt'):
        with open(f'./Books/{curr_book}/{curr_page}/text.txt', 'w') as f:
            f.write('')
    
    with open(f'./Books/{curr_book}/{curr_page}/text.txt', 'r') as f:
        text = f.read()

    global text_page_editor
    text_page_editor = TextInput(text=text, font_name='DownloadedFont', font_size=34, size_hint=(0.6, 0.6), pos_hint={"x": 0.2, "y": 0.25}, background_color=(0, 0, 0, 0), foreground_color=(0, 0, 0, 0.60), halign='center')

    return_editor = Button(text='Return to the story generator', font_name='DownloadedFont', font_size=22, size_hint=(0.6, 0.1), pos_hint={"x": 0.2, "y": 0.05})
    return_editor.bind(on_press=lambda *args:return_to_story_generator(curr_book, curr_page))

    layout.add_widget(background)
    layout.add_widget(logo)
    layout.add_widget(text_page_editor)
    layout.add_widget(return_editor)
    layout.add_widget(home)

    return layout

def return_to_story_generator(curr_book, curr_page):
    with open(f'./Books/{curr_book}/{curr_page}/text.txt', 'w') as f:
        f.write(text_page_editor.text)
    manager.switch_to(window_story, direction='down')

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

def edit_text(curr_book, curr_page):
    window_text_editor.clear_widgets()
    window_text_editor.add_widget(create_layout_edit_text(curr_book, curr_page))
    manager.switch_to(window_text_editor, direction='up')

def text2history(curr_book, curr_page, amount_pages=5):  
    book_dir = BOOKS + f'/{curr_book}'
    list_books = os.listdir(book_dir)
    try: 
        list_books.remove('title.txt')
    except:
        pass
    sorted_dirs = sorted(list_books, key=lambda x: int(x))
    books_paths = [os.path.join(book_dir, book) for book in sorted_dirs[int(curr_page)-1-amount_pages:int(curr_page)-1]]
    # Load the texts in each folder
    prompt = ""
    if int(curr_page) == 1:
        prompt = "Story: Once upon a time, "
    else:
        for book in books_paths:
            file = os.path.join(book, 'text.txt')
            with open(file, 'r') as f:
                text = f.read()
                if not text.startswith("This page has no generated text yet."):
                    prompt += text
                else:
                    pass
    print("Using prompt: ", prompt)
    if prompt != "":
        with open(f'./Books/{curr_book}/{curr_page}/Text2ConditionGen.txt', 'r') as f:
            textinput_text = f.read()
        execute_ssh_command(HOSTNAME, PORT, USERNAME, PASWORD, f"bash /hhome/nlp2_g05/social_inovation/text2history.sh '{prompt}' '|{textinput_text}'") 
        receive_image(remote_image_path = FOLDER_GETTING_FROM_CLUSTER_TXT + "/text.txt",
                  local_path        = f'./Books/{curr_book}/{curr_page}/text.txt',
                  hostname          = HOSTNAME,
                  port              = PORT,
                  username          = USERNAME,
                  password          = PASWORD)
        
        crop2lastpoint(f'./Books/{curr_book}/{curr_page}/text.txt')
        
    else:
        print("No text to generate the image")

def crop2lastpoint(file):
    with open(file, 'r') as f:
        text = f.read()
    text = text.split(".")
    if len(text) > 1:
        text = ".".join(text[:-1]) + "."
    
    with open(file, 'w') as f:
        f.write(text)
    

def thread_function(curr_book, curr_page):
    sketch2img(curr_book, curr_page)
    text2history(curr_book, curr_page)
    

def call_cluster(curr_book, curr_page):
    # loading_layout.opacity = 1

    def cluster_thread():
        thread_function(curr_book, curr_page)
        # finally:
            # Hide loading elements
            # loading_layout.opacity = 0

    threading.Thread(target=cluster_thread).start()
    
    
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

    with open(f'./Books/{curr_book}/{curr_page}/Text2ConditionGen.txt', 'w') as f:
        f.write(textinput.text)
    
    execute_ssh_command(HOSTNAME, PORT, USERNAME, PASWORD, f"bash /hhome/nlp2_g05/social_inovation/bash_script.sh '{textinput.text}'")
    
    time.sleep(1)
    receive_image(remote_image_path = FOLDER_GETTING_FROM_CLUSTER + "/image.png",
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

    title_path = f'./Books/{curr_book}/title.txt'
    if os.path.exists(title_path):
        with open(title_path, 'r') as f:
            book_title = f.read()
    else:
        book_title = f'BOOK: {curr_book}'

    # Add the current page and book to the layout in black color
    book = Label(text=f'{book_title}',
                pos_hint={"x": -0.4, "y": 0.443}, 
                color=(0, 0, 0, 1),
                font_name='DownloadedFont',
                font_size=30)

    page = Label(text=f'PAGE {curr_page}',
                        pos_hint={"y": 0.443}, 
                        color=(0, 0, 0, 1),
                        font_name='DownloadedFont',
                        font_size=30)

    background = Image(source='./myapp/assets/background_story_gen.jpg', fit_mode='fill')
    logo = Image(source='./myapp/assets/logo.png', size_hint=(0.25, 0.25), pos_hint={"x": 0.74, "y": 0.82})
    home = Home()

    sketch_layout = BoxLayout(orientation='vertical')
    buttons_sketch = BoxLayout(orientation='horizontal', size_hint=(0.8, 0.1), pos_hint={"x": 0.1})
    button1 = Button(text='Draw', font_name='DownloadedFont', font_size=22)

    # Delete all widets on window_drawing 
    window_drawing.clear_widgets()
    window_drawing.add_widget(create_layout_draw(curr_book, curr_page))

    button1.bind(on_press=lambda *args:manager.switch_to(window_drawing, direction='up'))
    # Widget to input the text to condition the image generation, textinput.text is the text entered
    global textinput
    if os.path.exists(f'./Books/{curr_book}/{curr_page}/Text2ConditionGen.txt'):
        textinput_text = open(f'./Books/{curr_book}/{curr_page}/Text2ConditionGen.txt', 'r').read()
        textinput = TextInput(text=textinput_text, hint_text='What did you draw?', font_name='DownloadedFont', font_size=17, foreground_color=(0, 0, 0, 1))
    else:
        textinput = TextInput(hint_text='What did you draw?', font_name='DownloadedFont', font_size=17, foreground_color=(0, 0, 0, 1))
    
    buttons_sketch.add_widget(button1)
    buttons_sketch.add_widget(textinput)
    
    # If the sketch does not exist, create a white sketch of 500x500 pixels
    if not os.path.exists(f'./Books/{curr_book}/{curr_page}/sketch.png'):
        white_img = np.array([[[255, 255, 255]]*500]*500, dtype=np.uint8)
        cv2.imwrite(f'./Books/{curr_book}/{curr_page}/sketch.png', white_img)
    if not os.path.exists(f'./Books/{curr_book}/{curr_page}/text.txt'):
        with open(f'./Books/{curr_book}/{curr_page}/text.txt', 'w') as f:
            f.write('This page has no generated text yet.')
    
    global sketch
    sketch = Image(source=f'./Books/{curr_book}/{curr_page}/sketch.png', size_hint=(1, 1))

    sketch_layout.add_widget(sketch)
    sketch_layout.add_widget(buttons_sketch)

    gen_Image_layout = BoxLayout(orientation='vertical')
    
    global gen_Image
    if not os.path.exists(f'./Books/{curr_book}/{curr_page}/image.png'):
        white_img = np.array([[[255, 255, 255]]*500]*500, dtype=np.uint8)
        cv2.imwrite(f'./Books/{curr_book}/{curr_page}/image.png', white_img)

    gen_Image = Image(source=f'./Books/{curr_book}/{curr_page}/image.png', size_hint=(1, 1))
    
    # Create loading elements
    # global loading_layout
    # loading_circle = Image(source='./myapp/assets/loading_circle2.gif', size_hint=(None, None), size=(50, 50))
    # loading_label = Label(text='Generating...', font_name='DownloadedFont', font_size=22, color=(0, 0, 0, 1))
    # loading_layout = BoxLayout(orientation='vertical', size_hint=(None, None), size=(100, 100), pos_hint={"center_x": 0.5, "center_y": 0.5})
    # loading_layout.add_widget(loading_circle)
    # loading_layout.add_widget(loading_label)
    # loading_layout.opacity = 0  # Initially hide the loading elements
    
    image_buttons = BoxLayout(orientation='horizontal', size_hint=(0.8, 0.1), pos_hint={"x": 0.1})

    genButton = Button(text='Generate!', font_name='DownloadedFont', font_size=22)
    genButton.bind(on_press=lambda *args:call_cluster(curr_book, curr_page))
    text_editor_button = Button(text='See text', font_name='DownloadedFont', font_size=22)
    text_editor_button.bind(on_press=lambda *args:edit_text(curr_book, curr_page))

    image_buttons.add_widget(genButton)
    image_buttons.add_widget(text_editor_button)


    gen_Image_layout.add_widget(gen_Image)
    gen_Image_layout.add_widget(image_buttons)

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

    
    if int(curr_page) > 1:
        prev_page = Button(text='<-', size_hint=(0.05, 0.05), pos_hint={"x": 0.01, "y": 0.475}) 
        prev_page.bind(on_press=lambda *args:prev_page_function(curr_book, curr_page))
        layout.add_widget(prev_page)

    layout.add_widget(next_page)
    layout.add_widget(book)
    layout.add_widget(page)
    return layout

def load_collection():
    window_collection.clear_widgets()
    window_collection.add_widget(create_layout_collection())
    manager.switch_to(window_collection, direction='up')

def create_story():
    def save_title(instance):
        curr_book = str(len(os.listdir('./Books')) + 1)
        os.mkdir(f'./Books/{curr_book}')
        with open(f'./Books/{curr_book}/title.txt', 'w') as f:
            f.write(title_input.text)
        window_story.clear_widgets()
        window_story.add_widget(create_layout_story_gen(curr_book, '1'))
        manager.switch_to(window_story, direction='up')

    # Prompt for the title
    layout = FloatLayout()
    background = Image(source='./myapp/assets/backgorund_menu.png', fit_mode='fill')
    # logo = Image(source='./myapp/assets/logo.png', pos_hint={"y": 0.1})
    home = Home()
    
    title_label = Label(text="Enter the book title:", font_name='DownloadedFont', font_size=25, pos_hint={"x": 0.2, "y": 0.6}, size_hint=(0.6, 0.1))
    
    title_input = TextInput(font_name='DownloadedFont', font_size=30, size_hint=(0.6, 0.1), pos_hint={"x": 0.2, "y": 0.5}, halign='center', padding_y=[15, 15])
    save_button = Button(text="Save Title", font_name='DownloadedFont', font_size=25, size_hint=(0.6, 0.1), pos_hint={"x": 0.2, "y": 0.4})
    save_button.bind(on_press=save_title)

    layout.add_widget(background)
    # layout.add_widget(logo)
    layout.add_widget(title_label)
    layout.add_widget(title_input)
    layout.add_widget(save_button)
    layout.add_widget(home)

    window_story.clear_widgets()
    window_story.add_widget(layout)
    manager.switch_to(window_story, direction='up')


def create_layout_menu():
    background = Image(source='./myapp/assets/backgorund_menu.png', fit_mode='fill')
    logo = Image(source='./myapp/assets/logo.png', pos_hint={"y": 0.1})
    
    # Layout buttons
    layout_b = BoxLayout(orientation='horizontal', size_hint=(0.8, 0.2), pos_hint={"x": 0.1})
    button1 = Button(text='CREATE A NEW STORY', font_name='DownloadedFont', font_size=25)

    button1.bind(on_press=lambda *args:create_story())

    # button2 = Button(text='VISUALIZE A STORY', font_name='DownloadedFont', font_size=25)
    # button2.bind(on_press=lambda *args: manager.switch_to(window_visualizer, direction='up'))

    button3 = Button(text='COLLECTION OF STORIES', font_name='DownloadedFont', font_size=25)
    button3.bind(on_press=lambda *args: load_collection())
    layout_b.add_widget(button1)
    # layout_b.add_widget(button2)
    layout_b.add_widget(button3)     
    
    global login_button
    login_button = LogIN()
    
    # Join all layouts
    layout = FloatLayout()
    layout.add_widget(background)
    layout.add_widget(login_button)
    layout.add_widget(logo)
    layout.add_widget(layout_b)
    return layout


def next_page_function_vis(book, page):
    if page != '0':
        with open(f'./Books/{book}/{page}/text.txt', 'w') as f:
            for child in window_visualizer.children[0].children:
                print(child)
                if "TextInput" in str(child):
                    text = child.text
                    f.write(text)
                    break
        
    page = int(page) + 1 
    window_visualizer.clear_widgets()
    window_visualizer.add_widget(create_layout_visualizer(book, str(page)))
    manager.switch_to(window_visualizer, direction='left')

def prev_page_function_vis(book, page):
    # Save the xhanges made in the text
    with open(f'./Books/{book}/{page}/text.txt', 'w') as f:
        for child in window_visualizer.children[0].children:
            print(child)
            if "TextInput" in str(child):
                text = child.text
                f.write(text)
                break
    page = int(page) - 1
    window_visualizer.clear_widgets()
    window_visualizer.add_widget(create_layout_visualizer(book, str(page)))
    manager.switch_to(window_visualizer, direction='right')

def create_layout_visualizer(book, page):
    background = Image(source='./myapp/assets/background_story_gen.jpg', fit_mode='fill')
    logo = Image(source='./myapp/assets/logo.png', size_hint=(0.25, 0.25), pos_hint={"x": 0.74, "y": 0.82})
    home = Home()
    layout = FloatLayout()
    layout.add_widget(background)
    
    title_path = f'./Books/{book}/title.txt'
    if os.path.exists(title_path):
        with open(title_path, 'r') as f:
            book_title = f.read()
    else:
        book_title = f'BOOK: {book}'

    if page == '0':
        # header = Label(text=f"Visualizing {book_title}", pos_hint={"y": 0.443}, color=(0, 0, 0, 1), font_name='DownloadedFont', font_size=30)
        cover = Image(source=f'./myapp/assets/cover.jpg', fit_mode='contain', size_hint=(1, 0.9))
        layout.add_widget(cover)
        
        # Add the title of the book
        # Handle long titles by adding line breaks between words
        words = book_title.split()
        book_title = ''
        for i, word in enumerate(words):
            book_title += word
            if i % 1 == 0 and i != 0:
                book_title += '\n'
            else:
                book_title += ' '
        title = Label(text=book_title, pos_hint={"y": 0.1}, color=(0, 0, 0, 1), font_name='DownloadedFont', font_size=70, halign='center')
        layout.add_widget(title)
        
    else:
        book_back = Image(source='./myapp/assets/book.jpg', fit_mode='fill')
        layout.add_widget(book_back)
        if not os.path.exists(f'./Books/{book}/{page}/image.png'):
            gen_Image = Image(source=f'./Books/{book}/{page}/sketch.png', pos_hint={"x": -0.15}, size_hint=(1, 1))
        else:  
            # If the gen image is a white image, load the sketch instead
            image = cv2.imread(f'./Books/{book}/{page}/image.png')
            if np.all(image == 255):
                gen_Image = Image(source=f'./Books/{book}/{page}/sketch.png', pos_hint={"x": -0.15}, size_hint=(1, 1))
            else:
                create_merged_image(book, page)
                # get window width 
                gen_Image = Image(source=f'./Books/{book}/{page}/merged.png', pos_hint={"x": -0.11, "y":0.08}, size_hint=(Window.width/2150, Window.width/2150))

        if not os.path.exists(f'./Books/{book}/{page}/text.txt'):
            with open(f'./Books/{book}/{page}/text.txt', 'w') as f:
                f.write('This page has no generated text yet.')

        with open(f'./Books/{book}/{page}/text.txt', 'r') as f:
            txt_page = f.read()
        header = Label(text=f"Visualizing page {page} of book {book}", pos_hint={"y": 0.443}, color=(0, 0, 0, 1), font_name='DownloadedFont', font_size=30)

        # Add text to the layout within a bounding box
        text = TextInput(text=txt_page, font_name='DownloadedFont', font_size=40, size_hint=(0.3, 0.7), pos_hint={"x": 0.56, "y": 0.16}, background_color=(0, 0, 0, 0), foreground_color=(0, 0, 0, 0.60), halign='center')
        layout.add_widget(gen_Image)
        layout.add_widget(text)
        layout.add_widget(header)

    if (int(page) + 1) <= len(os.listdir(f'./Books/{book}')):
        next_page = Button(text='->', size_hint=(0.05, 0.05), pos_hint={"x": 0.94, "y": 0.475})
        next_page.bind(on_press=lambda *args:next_page_function_vis(book, page))
        layout.add_widget(next_page)

    if int(page) > 0:
        prev_page = Button(text='<-', size_hint=(0.05, 0.05), pos_hint={"x": 0.01, "y": 0.475}) 
        prev_page.bind(on_press=lambda *args:prev_page_function_vis(book, page))
        layout.add_widget(prev_page)

    layout.add_widget(logo)
    layout.add_widget(home)

    return layout

def edit_book(book):
    pages = os.listdir(f'./Books/{book}')
    try: 
        pages.remove('title.txt')
    except:
        pass
    pages = sorted(pages, key=lambda x: int(x))
    window_story.clear_widgets()
    for page in pages:
        window_story.add_widget(create_layout_story_gen(book, 1))
    manager.switch_to(window_story, direction='up')

def vis_book(book):
    window_visualizer.clear_widgets()
    window_visualizer.add_widget(create_layout_visualizer(book, '0'))
    manager.switch_to(window_visualizer, direction='up')

def create_layout_collection():
    background = Image(source='./myapp/assets/backgorund_menu.png', fit_mode='fill')
    logo = Image(source='./myapp/assets/logo.png', size_hint=(0.25, 0.25), pos_hint={"x": 0.74, "y": 0.82})
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
        title_path = f'./Books/{book}/title.txt'
        if os.path.exists(title_path):
            with open(title_path, 'r') as f:
                book_title = f.read()
        else:
            book_title = f'BOOK: {book}'
            
        num_pages = len(os.listdir(f'./Books/{book}'))
        book_layout = BoxLayout(orientation='horizontal', size_hint=(0.8, None), height=50)
        book_layout.add_widget(Label(text=f'{book_title} - Number of pages: {num_pages}', 
                                     font_name='DownloadedFont', font_size=20))
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


def create_merged_image(book, page):
    # Import foreground image
    foreground_img_raw = PILImage.open('./Books/' + book + '/' + page + '/image.png')  # RGBA image
    foreground_img_raw = foreground_img_raw.convert("RGBA")
    foreground_img = np.array(foreground_img_raw)  # Inputs to blend_modes need to be numpy arrays.
    foreground_img_float = foreground_img.astype(float)  # Inputs to blend_modes need to be floats.

    # Import background image
    background_img_raw = PILImage.open('./myapp/assets/crop_book.jpg')  # RGBA image
    background_img_raw = background_img_raw.convert("RGBA")
    background_img_raw = background_img_raw.resize(foreground_img_raw.size)
    background_img = np.array(background_img_raw)  # Inputs to blend_modes need to be numpy arrays.
    background_img_float = background_img.astype(float)  # Inputs to blend_modes need to be floats.

    # create a white image with the same size as the background and put the foreground image in the middle
    blank = PILImage.new('RGBA', (background_img_raw.width, background_img_raw.height), (255, 255, 255, 255))
    blank.paste(foreground_img_raw, (0, 0), foreground_img_raw)
    foreground_img_float = np.array(blank).astype(float)

    # Blend images
    opacity = 0.7  # The opacity of the foreground that is blended onto the background is 70 %.
    blended_img_float = darken_only(background_img_float, foreground_img_float, opacity)

    # Convert blended image back into PIL image
    blended_img = np.uint8(blended_img_float)  # Image needs to be converted back to uint8 type for PIL handling.
    blended_img_raw = PILImage.fromarray(blended_img)  # Note that alpha channels are displayed in black by PIL by default.
                                                    # This behavior is difficult to change (although possible).
                                                    # If you have alpha channels in your images, then you should give
                                                    # OpenCV a try.

    # crop the blended image to the size of the foreground image
    # blended_img_raw = blended_img_raw.crop((115, 87, 265, 237))

    # Save the image in the folder of the book and page with the name merged.png
    blended_img_raw.save('./Books/' + book + '/' + page + '/merged.png')

    return blended_img_raw

class LogIN(FloatLayout):
    def __init__(self, **kwargs):
        super(LogIN, self).__init__(**kwargs)
        
        login = Button(size_hint=(0.1, 0.13), pos_hint={"x": 0.90, "y": 0.88}, background_normal = './myapp/assets/user.png', text = 'Log In                    ', font_name='DownloadedFont', font_size=20, color=(0, 0, 0, 1))
        login.bind(on_press=lambda *args:go2login())
        self.add_widget(login)
            
    def update(self, loged_in):
        self.clear_widgets()
        if not loged_in:
            login = Button(size_hint=(0.1, 0.13), pos_hint={"x": 0.90, "y": 0.88}, background_normal = './myapp/assets/user.png', text = 'Log In                    ', font_name='DownloadedFont', font_size=20, color=(0, 0, 0, 1))
            login.bind(on_press=lambda *args:go2login())
            self.add_widget(login)
        else: 
            config = Button(size_hint=(0.08, 0.08), pos_hint={"x": 0.90, "y": 0.88}, background_normal = './myapp/assets/config.png', text = 'Config                           ', font_name='DownloadedFont', font_size=20, color=(0, 0, 0, 1))
            config.bind(on_press=lambda *args:go2config())
            self.add_widget(config)
        
def go2login(): 
    window_login.clear_widgets()
    window_login.add_widget(create_login_layout())
    manager.switch_to(window_login, direction='down')
    
def go2config():
    window_config.clear_widgets()
    window_config.add_widget(create_config_layout())
    manager.switch_to(window_config, direction='down')

def create_login_layout():
    background = Image(source='./myapp/assets/backgorund_menu.png', fit_mode='fill')
    logo = Image(source='./myapp/assets/logo.png', size_hint=(0.25, 0.25), pos_hint={"x": 0.74, "y": 0.82})
    home = Home()
    
    layout = FloatLayout()
    layout.add_widget(background)
    layout.add_widget(logo)
    layout.add_widget(home)
    
    username = TextInput(hint_text='Username', font_name='DownloadedFont', font_size=20, size_hint=(0.3, 0.1), pos_hint={"x": 0.35, "y": 0.70}, halign='center', padding_y=[15, 15])
    # password = TextInput(hint_text='Password', font_name='DownloadedFont', font_size=20, size_hint=(0.3, 0.1), pos_hint={"x": 0.35, "y": 0.47}, halign='center', padding_y=[15, 15])
    password = PasswordInput(hint_text='Password', font_name='DownloadedFont', font_size=20, size_hint=(0.3, 0.1), pos_hint={"x": 0.35, "y": 0.58}, halign='center', padding_y=[15, 15])
    repeat_password = PasswordInput(hint_text='Repeat Password', font_name='DownloadedFont', font_size=20, size_hint=(0.3, 0.1), pos_hint={"x": 0.35, "y": 0.46}, halign='center', padding_y=[15, 15])
    age = TextInput(hint_text='Age', font_name='DownloadedFont', font_size=20, size_hint=(0.3, 0.1), pos_hint={"x": 0.35, "y": 0.34}, halign='center', padding_y=[15, 15])
    login_button = Button(text='Login', font_name='DownloadedFont', font_size=20, size_hint=(0.3, 0.1), pos_hint={"x": 0.35, "y": 0.22})
    login_button.bind(on_press=lambda *args:actions_when_login())
    
    layout.add_widget(username)
    layout.add_widget(password)
    layout.add_widget(repeat_password)
    layout.add_widget(age)
    layout.add_widget(login_button)
    
    return layout

def actions_when_login():
    global login_button
    login_button.update(loged_in=True)
    manager.switch_to(main_window, direction='down')
    

def create_config_layout():
    background = Image(source='./myapp/assets/backgorund_menu.png', fit_mode='fill')
    logo = Image(source='./myapp/assets/logo.png', size_hint=(0.25, 0.25), pos_hint={"x": 0.74, "y": 0.82})
    home = Home()
    
    layout = FloatLayout()
    layout.add_widget(background)
    layout.add_widget(logo)
    layout.add_widget(home)
    
    # no se perque no s'afegeixen :/
    label = Label(text='Allow explicit content', font_name='DownloadedFont', font_size=20, pos_hint={"x": 0.35, "y": 0.70})
    switch = Switch(active=False, pos_hint={"x": 0.35, "y": 0.60})
    
    layout.add_widget(label)
    layout.add_widget(switch)
    
    return layout

class MenuApp(App):
    def build(self):
        global manager, main_window, window_story, window_drawing, window_visualizer, window_collection, window_text_editor, window_login, window_config

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
        window_text_editor = Screen(name='Text editor')
        window_login = Screen(name='Login window')
        window_config = Screen(name='Config window')

        main_window.add_widget(create_layout_menu())

        manager.add_widget(main_window)
        manager.add_widget(window_story)
        manager.add_widget(window_drawing)
        manager.add_widget(window_visualizer)
        manager.add_widget(window_collection)
        manager.add_widget(window_text_editor)
        manager.add_widget(window_login)
        manager.add_widget(window_config)

        return app_box




if __name__ == '__main__':
    """
    Thinks that we might change:
    - Put all the images of the desing of the app in folders
    """
    app = MenuApp()
    app.run()


    