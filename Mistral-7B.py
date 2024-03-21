
from PIL import Image
import requests
from transformers import Blip2Processor, Blip2ForConditionalGeneration
import torch

device = ("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using {device} device")


processor = Blip2Processor.from_pretrained("Salesforce/blip2-opt-2.7b")
model = Blip2ForConditionalGeneration.from_pretrained(
    "Salesforce/blip2-opt-2.7b", load_in_8bit=True, device_map={"": 0}, torch_dtype=torch.float16
)

def gen_text(model, processor, image, tokens_max_lenght=100):
    prompt = f"Question: Describe the image for a kid with enough details. Answer:"
    inputs = processor(images=image, text=prompt, return_tensors="pt").to(device="cuda", dtype=torch.bfloat16)
    inputs["max_new_tokens"] = tokens_max_lenght
    generated_ids = model.generate(**inputs)
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()
    return generated_text


url = "/ghome/mpilligua/Story-Generation/Examples/Example 1/gen_image.png"
image = Image.open(url)
text = gen_text(model, processor, image)
print(text)


# Use a pipeline as a high-level helper
from transformers import pipeline

pipe = pipeline("text-generation", model="mistralai/Mistral-7B-v0.1", device = "cuda")

# Generate text
prompt = f"Context: The story should talk about {text}. Story: Once upon a time, "
print(pipe(prompt, max_length=100)[0]["generated_text"])