import json
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from ggml import GGMLModel

class ModelLoader:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelLoader, cls).__new__(cls)
        return cls._instance

    def load_model(self, model_name):
        try:
            model = AutoModelForCausalLM.from_pretrained(model_name)
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            return model, tokenizer
        except Exception as e:
            print(f"Error loading model: {e}")
            return None, None

class ModelInferencer:
    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer
        self.ggml_model = GGMLModel()

    def infer(self, input_text):
        try:
            inputs = self.tokenizer(input_text, return_tensors='pt')
            outputs = self.model.generate(**inputs)
            result = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return result
        except Exception as e:
            print(f"Error inferencing model: {e}")
            return None

class APIWrapper:
    def __init__(self, model_loader):
        self.model_loader = model_loader
        self.model = None
        self.tokenizer = None

    def load_model(self, model_name):
        self.model, self.tokenizer = self.model_loader.load_model(model_name)

    def infer(self, input_text):
        if self.model is None or self.tokenizer is None:
            return "Model not loaded"
        inferencer = ModelInferencer(self.model, self.tokenizer)
        return inferencer.infer(input_text)

def main():
    model_loader = ModelLoader()
    api_wrapper = APIWrapper(model_loader)
    model_name = "Qwen/Qwen3-Omni-30B-A3B-Instruct"
    api_wrapper.load_model(model_name)
    input_text = "Hello, world!"
    result = api_wrapper.infer(input_text)
    print(result)

if __name__ == '__main__':
    main()