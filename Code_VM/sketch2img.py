from diffusers import DiffusionPipeline, StableDiffusionXLControlNetPipeline, StableDiffusionXLImg2ImgPipeline, ControlNetModel, AutoencoderKL
from diffusers.utils import load_image
from transformers import Blip2Processor, Blip2ForConditionalGeneration, pipeline
import numpy as np
import torch
import cv2
from PIL import Image
import os 
import sys

#os.environ["GRADIO_TEMP_DIR"] = r"C:\Users\Joan\Desktop\Story-Generation\Out"

def sketch_2_image(init_prompt, strength = 0.5, steps_slider_image = 100):
    
    positive_prompt = ", realistic picture, best quality, 4k, 8k, ultra highres, raw photo in hdr, sharp focus"
    negative_prompt = "worst quality, low quality, normal quality, child, painting, drawing, sketch, cartoon, anime, render, blurry"
    PATH_SKETCH = "/hhome/nlp2_g05/social_inovation/Sketches/sketch.png"

    print("Loading models...")
    controlnet = ControlNetModel.from_pretrained("diffusers/controlnet-canny-sdxl-1.0", torch_dtype=torch.float16)
    print("Controlnet loaded")

    vae = AutoencoderKL.from_pretrained("madebyollin/sdxl-vae-fp16-fix", torch_dtype=torch.float16)
    print("VAE loaded")

    pipe = StableDiffusionXLControlNetPipeline.from_pretrained("stabilityai/stable-diffusion-xl-base-1.0", controlnet=controlnet, vae=vae, torch_dtype=torch.float16)
    pipe.enable_model_cpu_offload()
    print("Stable diffusion pipeline loaded")

    pipe_refiner = StableDiffusionXLImg2ImgPipeline.from_pretrained("stabilityai/stable-diffusion-xl-refiner-1.0", torch_dtype=torch.float16, variant="fp16", use_safetensors=True)
    pipe_refiner.to("cuda")
    print("Stable diffusion refiner pipeline loaded")

    prompt = str(init_prompt) + str(positive_prompt)
    print('prompt', prompt)
    negative_prompt = str(negative_prompt)
    print('negative_prompt', negative_prompt)
    controlnet_conditioning_scale = 0.5  # recommended for good generalization

    image = cv2.imread(PATH_SKETCH)
    
    image = cv2.resize(image, (512, 512))
    image = np.array(image)
    image = cv2.Canny(image, 100, 200)
    image = image[:, :, None]
    image = np.concatenate([image, image, image], axis=2)
    canny_image = Image.fromarray(image)
    image = pipe(prompt, controlnet_conditioning_scale=controlnet_conditioning_scale, image=canny_image, num_inference_steps=steps_slider_image).images[0]
    image = pipe_refiner(prompt, image=image, negative_prompt=negative_prompt, strength=strength).images[0]
    return image


# /hhome/nlp2_g05/social_inovation/promts_send.txt
# Open the file and append a line
with open("/hhome/nlp2_g05/social_inovation/promts_send.txt", "a") as file:
    file.write(str(sys.argv) + "\n")

prompt = " ".join(sys.argv[1:])
sketch_2_image(prompt).save("/hhome/nlp2_g05/social_inovation/Generated_imgs/image.png")