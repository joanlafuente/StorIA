import turtle
from tkinter import *

from PIL import Image
import os


# In order to save the image requires Ghostscript to be installed
# https://www.ghostscript.com/releases/gsdnld.html
# Add the path to the Ghostscript bin folder to the system path

OUTPUT_FILENAME = "Sketches/sketch.png"
SIZE_PEN = 7


# Functions needed to draw
def erase():
    t.speed(0)
    t.pencolor("white")
    t.pensize(30)
    t.shape("circle")
    t.shapesize(2)

def clear():
    t.clear()

def pen():
    t.speed(0)
    t.color("black")
    t.pensize(SIZE_PEN)
    t.shape("circle")
    t.shapesize(.7)

def undo():
    t.undo()

def save():
    global OUTPUT_FILENAME
    t.speed(0)
    t.hideturtle()
    t.getcanvas().postscript(file="tmp.ps")
    t.showturtle()

    image = Image.open("tmp.ps")
    image.save(OUTPUT_FILENAME, "PNG")
    image.close()
    os.remove("tmp.ps")

def increase_size():
    global SIZE_PEN
    previous_size = SIZE_PEN
    SIZE_PEN += 4
    if SIZE_PEN < 25:
        t.pensize(SIZE_PEN)
    else:
        SIZE_PEN = 25
        print("Pen size cannot be more than 25")
        if previous_size != 25:
            t.pensize(SIZE_PEN)

def decrease_size():
    global SIZE_PEN
    previous_size = SIZE_PEN
    SIZE_PEN -= 4
    if SIZE_PEN >= 1:
        t.pensize(SIZE_PEN)
    else:
        SIZE_PEN = 1
        print("Pen size cannot be less than 1")
        if previous_size != 1:
            t.pensize(SIZE_PEN)

def quit():
    t.bye()
    try:
        instructions.destroy()
    except TclError:
        pass
    


if "__main__" == __name__:
    # Instructions window
    root = turtle.Screen()._root
    instructions = Tk()
    instructions.title("Instructions")
    instructions.geometry("300x230")
    instructions_label = Label(instructions, text="Instructions:\n\n"
                                "- Click on the screen to start drawing\n"
                                "- Drag the circle to draw\n"
                                "- Press 'u' to undo\n"
                                "- Press '+' to increase pen size\n"
                                "- Press '-' to decrease pen size\n"
                                "- Press 'c' to clear the screen\n"
                                "- Press 'e' to enter in erase mode\n"
                                "- Press 'p' to go back to pen mode\n"
                                "- Press 's' to save the sketch\n"
                                "- Press 'q' to quit\n",
                                font=("Arial", 12),
                                justify=LEFT)
    instructions_label.pack()

    # Sketch window
    t=turtle
    t.setup(684, 684)
    t.shape("circle")
    t.shapesize(.7)
    t.pu()
    t.color("black")
    t.bgcolor("white")
    t.pencolor("black")
    t.pensize(SIZE_PEN)
    t.speed(0)

    def skc(x,y):
        t.pu()
        t.goto(x,y)
        def sketch(x,y):
            t.pd()
            t.goto(x,y)
        t.ondrag(sketch)

    t.onscreenclick(skc)

    t.onkeypress(undo,"u")
    t.onkey(increase_size,"+")
    t.onkey(decrease_size,"-")
    t.onkey(pen,"p")
    t.onkey(clear,"c")
    t.onkey(erase,"e")
    t.onkey(save,"s")
    t.onkey(quit,"q")
    t.listen()
    t.title("Sketch Board")

    t.mainloop()
    instructions.mainloop()