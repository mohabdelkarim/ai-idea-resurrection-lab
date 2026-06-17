import json
import os
import requests
from transformers import AutoModelForCausalLM, AutoTokenizer

class ERNIE45VLA3BThinking:
    def __init__(self, model_path, tokenizer_path):
        self.model_path = model_path
        self.tokenizer_path = tokenizer_path
        self.model = None
        self.tokenizer = None

    def load_model(self):
        try:
            self.model = AutoModelForCausalLM.from_pretrained(self.model_path)
            self.tokenizer = AutoTokenizer.from_pretrained(self.tokenizer_path)
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
        return True

    def generate_text(self, input_text, max_length=100):
        if not self.model or not self.tokenizer:
            print("Model or tokenizer not loaded")
            return None

        inputs = self.tokenizer(input_text, return_tensors="pt")
        outputs = self.model.generate(**inputs, max_length=max_length)
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return generated_text

def main():
    model_path = "./ERNIE-4.5-VL-28B-A3B-Thinking"
    tokenizer_path = "./ERNIE-4.5-VL-28B-A3B-Thinking"

    ernie_model = ERNIE45VLA3BThinking(model_path, tokenizer_path)
    if ernie_model.load_model():
        input_text = "Hello, how are you?"
        generated_text = ernie_model.generate_text(input_text)
        print(f"Generated text: {generated_text}")
    else:
        print("Failed to load model")

if __name__ == '__main__':
    main()