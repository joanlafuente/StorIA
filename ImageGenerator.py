from diffusers import DiffusionPipeline, StableDiffusionXLControlNetPipeline, StableDiffusionXLImg2ImgPipeline, ControlNetModel, AutoencoderKL
from diffusers.utils import load_image
from transformers import Blip2Processor, Blip2ForConditionalGeneration, pipeline
import numpy as np
import torch
import cv2
from PIL import Image
import os 

os.environ["GRADIO_TEMP_DIR"] = r"C:\Users\Joan\Desktop\Story-Generation\Out"
positive_prompt = ", realistic picture, best quality, 4k, 8k, ultra highres, raw photo in hdr, sharp focus"
negative_prompt = "worst quality, low quality, normal quality, child, painting, drawing, sketch, cartoon, anime, render, blurry"
PATH_SKETCH = "Sketches/sketch.png"


def sketch_2_image(init_prompt, positive_prompt, negative_prompt, strength, steps_slider_image):
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

def describe_img(image, tokens_max_lenght=50):
    print("Loading models...")
    blip2_processor = Blip2Processor.from_pretrained("Salesforce/blip2-opt-2.7b")
    print("Blip2 processor loaded")

    blip2 = Blip2ForConditionalGeneration.from_pretrained(
        "Salesforce/blip2-opt-2.7b", load_in_8bit=True, device_map={"": 0}, torch_dtype=torch.float16)
    print("Blip2 model loaded")

    prompt = f"Question: Describe the image for a kid with enough details. Answer:"
    inputs = blip2_processor(images=image, text=prompt, return_tensors="pt").to(device="cuda", dtype=torch.bfloat16)
    inputs["max_new_tokens"] = tokens_max_lenght
    generated_ids = blip2.generate(**inputs)
    generated_text = blip2_processor.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()
    return generated_text


def image2text(image):
    text = describe_img(image)
    prompt = f"Context: The story should talk about {text}. Story: Once upon a time, "

    print("Loading models...")
    mistral_pipe = pipeline("text-generation", model="mistralai/Mistral-7B-v0.1", device="cuda")
    print("Mistral model loaded")
    text = mistral_pipe(prompt, max_length=100)[0]["generated_text"]
    return text


def gen_img_and_text(prompt, positive_prompt, negative_prompt, strength, steps_slider_image):
    image = sketch_2_image(prompt, positive_prompt, negative_prompt, strength, steps_slider_image)
    text = image2text(image)
    return image, text 

def load_new_sketch():
    return cv2.imread(PATH_SKETCH)

with gr.Blocks() as demo:
    text = gr.Textbox(label = 'Write the text to condition the image generation', placeholder = "Write the text here" )

    with gr.Row():
        sketch = gr.Image(label = 'Sketch')
        image = gr.Image(label = 'Final generated image.')

    with gr.Row():
        gen_text = gr.Textbox(label = 'Generated text', placeholder = "Generated text will appear here")

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
            value=10,
            step=1,
        )

    with gr.Row():
        b_principal = gr.Button("Generate Image")
        b_principal.click(sketch_2_image, inputs=[text, additional_positive, additional_negative, strength, steps_slider_image], outputs=image)

        b2 = gr.Button("Generate Text")
        b2.click(image2text, inputs=image, outputs=gen_text)

        b3 = gr.Button("Generate All")
        b3.click(gen_img_and_text, inputs=[text, additional_positive, additional_negative, strength, steps_slider_image], outputs=[image, gen_text])


if __name__ == "__main__":
    demo.launch(share=True)