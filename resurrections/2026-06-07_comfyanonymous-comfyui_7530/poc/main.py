import torch
import torch.nn as nn
from transformers import AutoModelForCausalLM, AutoTokenizer
import numpy as np
from PIL import Image
import tkinter as tk
from tkinter import filedialog
from tqdm import tqdm

class HiDreamI1FullModel:
    def __init__(self, model_name="HiDream-ai/HiDream-I1-Full"):
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)

    def generate_text(self, input_text, max_length=100):
        try:
            inputs = self.tokenizer(input_text, return_tensors="pt")
            outputs = self.model.generate(**inputs, max_length=max_length)
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return generated_text
        except Exception as e:
            print(f"Error generating text: {e}")
            return ""

class ComfyUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ComfyUI")
        self.model = HiDreamI1FullModel()
        self.input_label = tk.Label(root, text="Input Text:")
        self.input_label.pack()
        self.input_entry = tk.Text(root, height=10, width=50)
        self.input_entry.pack()
        self.generate_button = tk.Button(root, text="Generate Text", command=self.generate_text)
        self.generate_button.pack()
        self.output_label = tk.Label(root, text="Generated Text:")
        self.output_label.pack()
        self.output_text = tk.Text(root, height=10, width=50)
        self.output_text.pack()

    def generate_text(self):
        input_text = self.input_entry.get("1.0", tk.END)
        generated_text = self.model.generate_text(input_text)
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, generated_text)

def main():
    root = tk.Tk()
    app = ComfyUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()