  
# Story-Generation

  
## Project overview

<div align="justify">  
StorIA is an app for tablets that will use children's drawing and brief textual prompts and offer a story fitting for it. The child will draw a sketch (and optionally input a prompt), from which the app will offer an improved version of the drawing, painted and colored, and a description narrating it. The amount of text can be selected accordingly knowing the age of the target audience. 

Since our device will use multiple drawings, it can be made together by different kids to create a story made by all of them, in a way that each kid contributes by adding a new page to the story. One of the main objectives is to have the children do stories in groups so they can play with their friends or arrive to meet new ones. 

Lastly, StorIA will have the option to share your story on an internal social page. This network will have a collection of stories created by kids from all around the world. This way, even if a kid doesn't want to draw, they could read all of the posted stories, and connect with children abroad through those. The internal network will also implement a ranking system where kids can rank the stories they have read and StorIA will award the best stories of the month with some sort of prize, yet to be decided.
</div>


## Repository Structure

The repository has the following structure:

- ***Design APP***: This directory contains an overview of how the application would look like.
- ***Examples***: Contains a folder with the original sketch and the image generated from it.
- ***Sketches***: Some example sketches that can be used with the ImageGenerator script.
- ***DrawSketch.py***: File with the source code for the tkinter interface, that enables a user to draw and save a sketch using a simple tool box.
- ***ImageGenerator.py***: Main file that contains the logic of the application. It defines the code necessary for creating the Gradio application and contains the functions that call the auxiliary models, namely: Sketch2Image, Image2History.
- ***TextGenerator.ipynb***: Testing of BLIP-2 to describe the image.
- ***environment.yml***: The environment required to execute the code of the different files.


### Models
***Sketch2Image***: StableDiffusionXL with ControlNet and a Variational Auto-Encoder
***Image2Text***: Blip2

## Sketch example:

Text2Text: 



Installation and Usage

Before starting with the usage, ensure Python 3.12 is installed on your system. If it is not, you can download it here. Next, clone the project from GitHub to your local machine using the command:

git clone https://github.com/joanlafuente/Story-Generation/tree/main

Then create an environment 


![image](https://github.com/joanlafuente/Story-Generation/blob/main/Examples/Example%201/sketch.png)

## Generated Image example:
Generation conditioned with the following text: "A horse on a field"

![image](https://github.com/joanlafuente/Story-Generation/blob/main/Examples/Example%201/gen_image.png)
