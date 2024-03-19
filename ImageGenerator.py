from diffusers import DiffusionPipeline, StableDiffusionXLControlNetPipeline, StableDiffusionXLImg2ImgPipeline, ControlNetModel, AutoencoderKL
from diffusers.utils import load_image
import numpy as np
import torch
import cv2
from PIL import Image
import gradio as gr
import os 

os.environ["GRADIO_TEMP_DIR"] = r"C:\Users\Joan\Desktop\Story-Generation\Downloads"
positive_prompt = ", realistic picture, best quality, 4k, 8k, ultra highres, raw photo in hdr, sharp focus"
negative_prompt = "worst quality, low quality, normal quality, child, painting, drawing, sketch, cartoon, anime, render, blurry"
PATH_SKETCH = "Sketches/sketch.png"


def sketch_2_image(init_prompt, positive_prompt, negative_prompt, strength, steps_slider_image):
    prompt = str(init_prompt) + str(positive_prompt)
    print('prompt', prompt)
    negative_prompt = str(negative_prompt)
    print('negative_prompt', negative_prompt)
    image = cv2.imread(PATH_SKETCH)
    controlnet_conditioning_scale = 0.5  # recommended for good generalization
    
    image = np.array(image)
    image = cv2.Canny(image, 100, 200)
    image = image[:, :, None]
    image = np.concatenate([image, image, image], axis=2)
    canny_image = Image.fromarray(image)
    image = pipe(prompt, controlnet_conditioning_scale=controlnet_conditioning_scale, image=canny_image, num_inference_steps=steps_slider_image).images[0]
    image = pipe_refiner(prompt, image=image, negative_prompt=negative_prompt, strength=strength).images[0]
    #image.save("tmp/img.png")
    return image

def load_new_sketch():
    return cv2.imread(PATH_SKETCH)

with gr.Blocks() as demo:
    text = gr.Textbox(label = 'Write the text to condition the image generation', placeholder = "Write the text here" )

    with gr.Row():
        sketch = gr.Image(label = 'Sketch')
        image = gr.Image(label = 'Final generated image.')

    b_new_sketch = gr.Button("Update Sketch")
    b_new_sketch.click(load_new_sketch, outputs=sketch)

    with gr.Accordion("Advanced", open=False):
        strength = gr.Slider(
            label="Strength refiner",
            interactive=True,
            minimum=0,
            maximum=1,
            value=0.2,
            step=0.1,
        )
        additional_positive = gr.Textbox(
            value = ", realistic image, best quality, 4k, 8k, ultra highres, raw photo in hdr, sharp focus",
            label="Additional positive",
            info="Use this to insert custom styles or elements to the background",
            interactive=True,
        )
        additional_negative = gr.Textbox(
            value="worst quality, low quality, normal quality, sketch, anime, render, blurry",
            label="Additional negative",
            info="Use this to specify additional elements or styles that "
                    "you don't want to appear in the image",
            interactive=True,
        )
        steps_slider_image = gr.Slider(
            label="Generation steps",
            info="Control the trade-off between quality and speed. Higher "
                 "values means more quality but more processing time",
            interactive=True,
            minimum=10,
            maximum=100,
            value=50,
            step=1,
        )

    with gr.Row():
        b_principal = gr.Button("Generate Image")
        b_principal.click(sketch_2_image, inputs=[text, additional_positive, additional_negative, strength, steps_slider_image], outputs=image)

if __name__ == "__main__":
    controlnet = ControlNetModel.from_pretrained("diffusers/controlnet-canny-sdxl-1.0", torch_dtype=torch.float16)
    vae = AutoencoderKL.from_pretrained("madebyollin/sdxl-vae-fp16-fix", torch_dtype=torch.float16)
    pipe = StableDiffusionXLControlNetPipeline.from_pretrained("stabilityai/stable-diffusion-xl-base-1.0", controlnet=controlnet, vae=vae, torch_dtype=torch.float16)
    pipe.enable_model_cpu_offload()

    pipe_refiner = StableDiffusionXLImg2ImgPipeline.from_pretrained("stabilityai/stable-diffusion-xl-refiner-1.0", torch_dtype=torch.float16, variant="fp16", use_safetensors=True)
    pipe_refiner.to("cuda")

    demo.launch(share=True)