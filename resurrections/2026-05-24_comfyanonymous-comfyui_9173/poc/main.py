import torch
from transformers import AutoModelForVision2Seq, AutoProcessor
from PIL import Image
import numpy as np
from tqdm import tqdm
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QwenImageNode:
    def __init__(self, model_id="Qwen/Qwen-Image"):
        self.model_id = model_id
        self.model = AutoModelForVision2Seq.from_pretrained(model_id)
        self.processor = AutoProcessor.from_pretrained(model_id)

    def process_image(self, image_path):
        try:
            image = Image.open(image_path)
            inputs = self.processor(images=image, return_tensors="pt")
            output = self.model.generate(**inputs)
            return self.processor.decode(output[0], skip_special_tokens=True)
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            return None

    def run(self, image_path):
        logger.info(f"Processing image: {image_path}")
        output = self.process_image(image_path)
        logger.info(f"Output: {output}")
        return output

if __name__ == "__main__":
    node = QwenImageNode()
    image_path = "path_to_your_image.jpg"
    output = node.run(image_path)
    print(output)