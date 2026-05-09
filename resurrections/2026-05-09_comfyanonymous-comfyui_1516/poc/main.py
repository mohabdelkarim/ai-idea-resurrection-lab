import os
import torch
from diffusers import WuerstchenPipeline, WuerstchenModel
from comfyui_node import ComfyNode
from typing import Dict, Any

class WuerstchenNode(ComfyNode):
    def __init__(self, model_id: str, torch_dtype: torch.dtype = torch.float16):
        super().__init__()
        self.model_id = model_id
        self.torch_dtype = torch_dtype
        self.pipeline = None

    def load_pipeline(self):
        try:
            self.pipeline = WuerstchenPipeline.from_pretrained(self.model_id, torch_dtype=self.torch_dtype)
        except Exception as e:
            print(f"Error loading pipeline: {e}")
            return False
        return True

    def process(self, inputs: Dict[str, Any]):
        if not self.pipeline:
            if not self.load_pipeline():
                return {"error": "Failed to load pipeline"}
        try:
            prompt = inputs.get("prompt", "")
            negative_prompt = inputs.get("negative_prompt", "")
            num_steps = inputs.get("num_steps", 50)
            guidance_scale = inputs.get("guidance_scale", 7.5)
            output = self.pipeline(prompt, negative_prompt=negative_prompt, num_inference_steps=num_steps, guidance_scale=guidance_scale)
            return {"output": output.images[0]}
        except Exception as e:
            print(f"Error processing: {e}")
            return {"error": "Failed to process"}

    def save(self):
        return {"model_id": self.model_id, "torch_dtype": str(self.torch_dtype)}

    def load(self, data: Dict[str, Any]):
        self.model_id = data.get("model_id", "")
        self.torch_dtype = torch.float16 if data.get("torch_dtype", "torch.float16") == "torch.float16" else torch.float32

def main():
    node = WuerstchenNode("warp-ai/wuerstchen")
    inputs = {
        "prompt": "An astronaut riding a dragon",
        "negative_prompt": "",
        "num_steps": 50,
        "guidance_scale": 7.5
    }
    output = node.process(inputs)
    if "error" in output:
        print(output["error"])
    else:
        print("Image generated successfully")
if __name__ == "__main__":
    main()