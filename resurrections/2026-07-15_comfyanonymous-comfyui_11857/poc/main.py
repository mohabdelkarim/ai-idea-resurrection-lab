import torch
import numpy as np
from PIL import Image
from transformers import AutoModelForVision2Seq, AutoProcessor
from tqdm import tqdm
import requests
from safetensors import safe_load
from filelock import FileLock

class GLMImageModel:
    def __init__(self, model_id):
        self.model_id = model_id
        self.model = AutoModelForVision2Seq.from_pretrained(model_id)
        self.processor = AutoProcessor.from_pretrained(model_id)

    def generate_image_caption(self, image_path):
        try:
            image = Image.open(image_path)
            inputs = self.processor(images=image, return_tensors="pt")
            output = self.model.generate(**inputs)
            caption = self.processor.decode(output[0], skip_special_tokens=True)
            return caption
        except Exception as e:
            print(f"Error generating caption: {e}")
            return None

def main():
    model_id = "zai-org/GLM-Image"
    glm_image_model = GLMImageModel(model_id)
    image_path = "path_to_your_image.jpg"
    caption = glm_image_model.generate_image_caption(image_path)
    if caption:
        print(f"Generated Caption: {caption}")
    else:
        print("Failed to generate caption.")

if __name__ == '__main__':
    main()