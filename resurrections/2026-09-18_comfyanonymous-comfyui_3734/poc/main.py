import logging
import os
import json
import torch
import torch.nn as nn
import requests
from typing import Any, Dict, List, Optional

# Simple base node class mimicking ComfyUI's node system
class ComfyNode:
    def __init__(self):
        self.inputs: Dict[str, Any] = {}
        self.outputs: Dict[str, Any] = {}
        self.logger = logging.getLogger(self.__class__.__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('[%(levelname)s] %(name)s: %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.DEBUG)

    def set_input(self, name: str, value: Any):
        self.inputs[name] = value
        self.logger.debug(f"Input set: {name} = {type(value)}")

    def get_output(self, name: str) -> Any:
        return self.outputs.get(name)

    def execute(self) -> None:
        raise NotImplementedError

# Mock of the SD3ControlNetPipeline (since diffusers is not in manifest)
class MockSD3ControlNetPipeline(nn.Module):
    def __init__(self, model_id: str, controlnet_type: str):
        super().__init__()
        self.model_id = model_id
        self.controlnet_type = controlnet_type
        self.logger = logging.getLogger('MockSD3ControlNetPipeline')
        self.logger.debug(f"Initialized mock pipeline for {model_id} with {controlnet_type}")

    def forward(self, prompt: str, conditioning: torch.Tensor, strength: float = 1.0) -> torch.Tensor:
        # Produce a dummy latent tensor based on input shapes
        batch = conditioning.shape[0]
        latent = torch.randn(batch, 4, 64, 64) * strength
        self.logger.debug(f"Generated latent with shape {latent.shape} for prompt '{prompt}'")
        return latent

# The new ControlNet node
class ControlNetNode(ComfyNode):
    def __init__(self, model_id: str = "stabilityai/sd3-medium", controlnet_type: str = "canny"):
        super().__init__()
        self.model_id = model_id
        self.controlnet_type = controlnet_type.lower()
        self.pipeline: Optional[MockSD3ControlNetPipeline] = None
        self._load_pipeline()

    def _load_pipeline(self) -> None:
        try:
            # In a real implementation we would download weights from HuggingFace Hub
            # Here we just instantiate the mock pipeline
            self.pipeline = MockSD3ControlNetPipeline(self.model_id, self.controlnet_type)
            self.logger.info(f"Loaded ControlNet pipeline: {self.model_id} [{self.controlnet_type}]")
        except Exception as e:
            self.logger.error(f"Failed to load pipeline: {e}")
            raise

    def execute(self) -> None:
        if self.pipeline is None:
            self.logger.error("Pipeline not initialized")
            raise RuntimeError("Pipeline not initialized")
        # Expected inputs
        prompt: str = self.inputs.get('prompt', '')
        conditioning: torch.Tensor = self.inputs.get('conditioning')
        strength: float = self.inputs.get('strength', 1.0)
        if conditioning is None or not isinstance(conditioning, torch.Tensor):
            self.logger.error("Missing or invalid conditioning tensor")
            raise ValueError("conditioning must be a torch.Tensor")
        # Run the mock pipeline
        try:
            latent = self.pipeline(prompt, conditioning, strength)
            self.outputs['latent'] = latent
            self.logger.info("Execution completed, latent stored in outputs")
        except Exception as e:
            self.logger.exception(f"Pipeline execution failed: {e}")
            raise

# Unit test for the node (mocked, no GPU required)
if __name__ == "__main__":
    import unittest
    from unittest.mock import patch

    class TestControlNetNode(unittest.TestCase):
        def setUp(self):
            self.node = ControlNetNode(model_id="test-model", controlnet_type="pose")
            dummy_tensor = torch.randn(2, 3, 256, 256)  # batch of 2 conditioning images
            self.node.set_input('prompt', 'A scenic landscape')
            self.node.set_input('conditioning', dummy_tensor)
            self.node.set_input('strength', 0.8)

        @patch.object(MockSD3ControlNetPipeline, 'forward')
        def test_execute_calls_pipeline(self, mock_forward):
            mock_forward.return_value = torch.zeros(2, 4, 64, 64)
            self.node.execute()
            mock_forward.assert_called_once()
            out = self.node.get_output('latent')
            self.assertIsNotNone(out)
            self.assertEqual(out.shape, (2, 4, 64, 64))

        def test_missing_conditioning(self):
            self.node.inputs.pop('conditioning')
            with self.assertRaises(ValueError):
                self.node.execute()

    unittest.main(argv=['first-arg-is-ignored'], exit=False)