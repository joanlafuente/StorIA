from PIL import Image
from transformers import Blip2Processor, Blip2ForConditionalGeneration, pipeline
import torch

device = ("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using {device} device")

processor_blip2 = Blip2Processor.from_pretrained("Salesforce/blip2-opt-2.7b")
blip2 = Blip2ForConditionalGeneration.from_pretrained(
    "Salesforce/blip2-opt-2.7b", load_in_8bit=True, device_map={"": 0}, torch_dtype=torch.float16
)
pipe_mistral = pipeline("text-generation", model="mistralai/Mistral-7B-v0.1", device = "cuda")

def describe_img(blip2, processor, image, tokens_max_lenght=100):
    prompt = f"Question: Describe the image for a kid with enough details. Answer:"
    inputs = processor(images=image, text=prompt, return_tensors="pt").to(device="cuda", dtype=torch.bfloat16)
    inputs["max_new_tokens"] = tokens_max_lenght
    generated_ids = blip2.generate(**inputs)
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()
    return generated_text

def gen_text(image, blip2, blip2_processor, mistral_pipe):
    text = describe_img(blip2=blip2, processor=blip2_processor, image=image)
    prompt = f"Context: The story should talk about {text}. Story: Once upon a time, "
    return mistral_pipe(prompt, max_length=100)[0]["generated_text"]

url = "/ghome/mpilligua/Story-Generation/Examples/Example 1/gen_image.png"
image = Image.open(url)

print(gen_text(image, blip2, processor_blip2, pipe_mistral))