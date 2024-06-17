from PIL import Image
from transformers import Blip2Processor, Blip2ForConditionalGeneration, pipeline
import torch
import sys
import os
# Use the following line to set the token provided by huggingface to be able to use the Mistral model
HG_TOKEN_MISTRAL = ""

device = ("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using {device} device")

processor_blip2 = Blip2Processor.from_pretrained("Salesforce/blip2-opt-2.7b")
blip2 = Blip2ForConditionalGeneration.from_pretrained(
    "Salesforce/blip2-opt-2.7b", load_in_8bit=True, device_map={"": 0}, torch_dtype=torch.float16
)
pipe_mistral = pipeline("text-generation", 
                        model="mistralai/Mistral-7B-v0.1", 
                        device="cuda",
                        token=HG_TOKEN_MISTRAL,
                        )

mistral_tokenizer = pipe_mistral.tokenizer

def describe_img(blip2, processor, image, tokens_max_lenght=100):
    prompt = f"Question: Describe the image for a kid with enough details. Answer:"
    inputs = processor(images=image, text=prompt, return_tensors="pt").to(device="cuda", dtype=torch.bfloat16)
    inputs["max_new_tokens"] = tokens_max_lenght
    generated_ids = blip2.generate(**inputs)
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()
    return generated_text

def gen_text(image, blip2, blip2_processor, mistral_pipe, prompt_mistrail=None, text2condition=None):
    text = describe_img(blip2=blip2, processor=blip2_processor, image=image)
    prompt = f"Context: The page of the story has an image of {text} and {text2condition}. Continue the following kids story taking into account the context explained. Story:" + prompt_mistrail
    
    current_length = len(mistral_tokenizer(prompt)["input_ids"])
    prompt2add = "Once upon a time," if ("Once upon a time," in prompt_mistrail) and (len(prompt_mistrail) <= len("Once upon a time,")*1.4) else ""
    
    return prompt2add + mistral_pipe(prompt, max_length=current_length+50)[0]["generated_text"].replace(prompt, "")

path_img = "/hhome/nlp2_g05/social_inovation/Generated_imgs/image.png"

image = Image.open(path_img)
text = " ".join(sys.argv[1:])

text = text.split("|")

prompt_context = text[0]
text2condition = text[1]

with open("/hhome/nlp2_g05/social_inovation/promts_send.txt", "a") as file:
    file.write(str(sys.argv) + "\n")

text = gen_text(image, blip2, processor_blip2, pipe_mistral, prompt_mistrail=prompt_context, text2condition=text2condition)

with open("/hhome/nlp2_g05/social_inovation/Generated_txt/text.txt", "w") as file:
    file.write(text)
