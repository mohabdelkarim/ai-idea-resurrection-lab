"""
PoC: Würstchen support in ComfyUI (comfyanonymous/ComfyUI#1516)

This script shows the correct architecture for adding a new model
family to ComfyUI: a standalone custom node implemented as a plain
Python class with CATEGORY / INPUT_TYPES / RETURN_TYPES / FUNCTION
class attributes — the ComfyUI node contract.

Requirements: none (simulation only; no ComfyUI or diffusers install needed)
To run:  python poc/main.py

For a real ComfyUI integration, place this file in:
  ComfyUI/custom_nodes/comfyui_wuerstchen.py
ComfyUI auto-discovers custom_nodes/ on startup via __init__.py.
"""

# ---------------------------------------------------------------------------
# ComfyUI node contract (stub — matches the real interface)
# ---------------------------------------------------------------------------

class NodeBase:
    """Minimal stub of the ComfyUI node base class."""
    pass


# ---------------------------------------------------------------------------
# Würstchen node implementation
# ---------------------------------------------------------------------------

class WuerstchenSampler(NodeBase):
    """
    Custom ComfyUI node for Würstchen text-to-image.

    In a real installation, ComfyUI discovers this via:
      NODE_CLASS_MAPPINGS = {"WuerstchenSampler": WuerstchenSampler}
      NODE_DISPLAY_NAME_MAPPINGS = {"WuerstchenSampler": "Würstchen Sampler"}
    """

    CATEGORY = "image/generation"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "sample"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model_id": ("STRING", {"default": "warp-ai/wuerstchen"}),
                "prompt": ("STRING", {"multiline": True}),
                "negative_prompt": ("STRING", {"multiline": True, "default": ""}),
                "steps": ("INT", {"default": 30, "min": 1, "max": 200}),
                "guidance_scale": ("FLOAT", {"default": 8.0, "min": 0.0, "max": 30.0}),
                "prior_steps": ("INT", {"default": 30, "min": 1, "max": 200}),
                "prior_guidance_scale": ("FLOAT", {"default": 4.0, "min": 0.0, "max": 30.0}),
            }
        }

    def sample(self, model_id, prompt, negative_prompt, steps,
               guidance_scale, prior_steps, prior_guidance_scale):
        """
        Real implementation would call:
            from diffusers import WuerstchenCombinedPipeline
            pipe = WuerstchenCombinedPipeline.from_pretrained(
                model_id, torch_dtype=torch.float16
            ).to("cuda")
            output = pipe(
                prompt=prompt,
                negative_prompt=negative_prompt,
                num_inference_steps=steps,
                decoder_guidance_scale=guidance_scale,
                prior_num_inference_steps=prior_steps,
                prior_guidance_scale=prior_guidance_scale,
            )
            return (output.images[0],)
        """
        # Simulation: return a placeholder tensor shape
        print(f"[WuerstchenSampler] prompt={prompt!r}")
        print(f"  model_id={model_id}, steps={steps}, guidance={guidance_scale}")
        print(f"  prior_steps={prior_steps}, prior_guidance={prior_guidance_scale}")
        simulated_image = [[0.5] * 512] * 512  # 512x512 placeholder
        print(f"  -> image shape: 512x512 (simulated)")
        return (simulated_image,)


# ---------------------------------------------------------------------------
# ComfyUI registration (required in __init__.py of a real custom node)
# ---------------------------------------------------------------------------

NODE_CLASS_MAPPINGS = {
    "WuerstchenSampler": WuerstchenSampler,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "WuerstchenSampler": "Würstchen Sampler",
}


# ---------------------------------------------------------------------------
# Demo (simulates ComfyUI calling the node)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== Simulation: ComfyUI executing WuerstchenSampler node ===")
    print()

    node_cls = NODE_CLASS_MAPPINGS["WuerstchenSampler"]
    print(f"Node category : {node_cls.CATEGORY}")
    print(f"Return types  : {node_cls.RETURN_TYPES}")
    print(f"Input spec    : {list(node_cls.INPUT_TYPES()['required'].keys())}")
    print()

    node = node_cls()
    result = node.sample(
        model_id="warp-ai/wuerstchen",
        prompt="A futuristic city at dusk, highly detailed",
        negative_prompt="blurry, low quality",
        steps=30,
        guidance_scale=8.0,
        prior_steps=30,
        prior_guidance_scale=4.0,
    )
    print(f"\nNode returned: tuple of length {len(result)}, image shape: {len(result[0])}x{len(result[0][0])}")
