  
# StorIA
![Sketh2Image](https://github.com/joanlafuente/Story-Generation/assets/126601914/fa8ecb83-d1f4-49b1-bc03-2debf560e3d4)


## Project overview

<div align="justify">  
StorIA is an app for tablets that will use children's drawing and brief textual prompts and offer a story fitting for it. The child will draw a sketch (and optionally input a prompt), from which the app will offer an improved version of the drawing, painted and colored, and a description narrating it. The amount of text can be selected accordingly knowing the age of the target audience. 
Since our device will use multiple drawings, it can be made together by different kids to create a story made by all of them, in a way that each kid contributes by adding a new page to the story. One of the main objectives is to have the children do stories in groups so they can play with their friends or arrive to meet new ones.  

Lastly, StorIA will have the option to share your story on an internal social page. This network will have a collection of stories created by kids from all around the world. This way, even if a kid doesn't want to draw, they could read all of the posted stories, and connect with children abroad through those. The internal network will also implement a ranking system where kids can rank the stories they have read and StorIA will award the best stories of the month with some sort of prize, yet to be decided.

More details on StorIA project can be found at the [project report](link.com).
</div>

## Example page generation:
In the left image you can see an example of a posible sketch, and in the right the image generated by our application, conditioned with the text  "A horse in a field"

 <div align="center">
  <figure style="display: inline-block; text-align: center;">
    <img src="https://github.com/joanlafuente/Story-Generation/blob/main/Examples/Example%201/sketch.png" alt="Sketch" width="400"/>
  </figure>
  <figure style="display: inline-block; text-align: center;">
    <img src="https://github.com/joanlafuente/Story-Generation/blob/main/Examples/Example%201/gen_image.png" alt="Generated image" width="400"/>
  </figure>
</div>

#### The text generator make the following story: 

- ***Generated story***: Once upon a time, 100 horses were in a field. They were all happy and healthy. One day, a farmer came and took 99 of the horses away. The last horse was left alone in the field. The horse was sad and lonely. 

## Repository Structure

The repository has the following structure:
- `/APP`: This directory contains the code of StorIA application.
- `/Code_VM`: This directory contains the neccessary files, which must be copied into a virtual machine,  to use StorIA AI capabilities.
- `/Design APP`: This directory contains an overview of the application initial desing.
- `/Examples`: Contains a folder with the original sketch and the image generated from it.
- `/Sketches`: Some example sketches that can be used with the ImageGenerator script.
- `DrawSketch.py`: File with the source code for the Tkinter interface, which enables a user to draw and save a sketch using a simple toolbox.
- `ImageGenerator.py`: Main file that contains the logic of the application. It defines the code necessary for creating the Gradio application and contains the functions that call the auxiliary models, namely: Sketch2Image, Image2History.
- `TextGenerator.ipynb`: Testing of BLIP-2 to describe the image.
- `environment.yml`: The environment required to execute the code of the different files.
- `Mistral-7B.py`: File that takes an image, runs it through BLIP-2 to describe it, and then uses Mistral-7B to create the history.

## Models used

The different pretrained models that we use for the generative tasks of StorIA are the following:
- **Sketch2Image**: [StableDiffusionXL](https://huggingface.co/docs/diffusers/api/pipelines/controlnet_sdxl) with [ControlNet](https://huggingface.co/docs/diffusers/using-diffusers/controlnet) and a [Variational Auto-Encoder](https://huggingface.co/docs/diffusers/api/models/autoencoderkl)
  - Combination of models which are used to transform the skecth into an image taking into account the text provided to condition the generation.
- **Image2Text**: [Blip2](https://huggingface.co/docs/transformers/model_doc/blip-2)
  - Model used to provide a description of the generated image.
- **Text2Text**: [Mistral](https://huggingface.co/mistralai/Mistral-7B-v0.1)
  - Model used to generate the text of a story page.

## Installation and Usage

Before starting clone the repository:

```
git clone https://github.com/joanlafuente/Story-Generation/tree/main
```
And then create a conda environment with the following command:
```
conda env create -f environment.yml
```

To be able to use StorIA is required to add a .env file in the /APP folder. This file provides the configuration to connect through ssh to a linux virtual machine, which will must contain files and folders of /Code_VM and it will execute the generative AI models. The path on the virtual machine containing /Code_VM files has to be updated using HOME_CLUSTER variable at /APP/main.py file. The virtual machine also requires the instalation of the conda environment.

If you do not have any machine available create the .env file as in the following example, in this way the application will work but it will not have the generative AI capabilities.

This .env file must have the following structure:

```
HOSTNAME = '<Host IP>'
PORT = '<Host port>'
USERNAME_CLUSTER = '<Username>'
PASWORD = '<Password>'
```

### Executing StorIA

Execute /APP/main.py and the application will be automatically launched on the main page. There you will have the options to generate a new story or acces previouslly created ones. If you have any proble do not hesitate to contact us.

The application is develoved in a way that allows you to export it and be used in IOS or Andorid devices, this process has to be done using Kivy.

### Executing the gradio interface

Execute /Imagegenerator.py which will launch the gradio interface, in which you are able to generate one image from a sketch, as well as the start of a story from that drawing. The interface will be hosted in your local machine. The IP will be printed in the command line.

### Contributors

Nil Biescas Rue nilbiescas3@gmail.com

