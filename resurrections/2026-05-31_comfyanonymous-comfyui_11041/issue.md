# Request to Support Z-Image Controlnet

**Repository:** [comfyanonymous/ComfyUI](https://github.com/Comfy-Org/ComfyUI)
**Issue:** [comfyanonymous/ComfyUI#11041](https://github.com/Comfy-Org/ComfyUI/issues/11041)
**Reactions:** 26 👍
**Created:** 2025-12-02T09:33:21Z
**Last Activity:** 2025-12-03T02:39:31Z
**Labels:** Feature

---

## Original Description

### Feature Idea

Alibaba-PAI just released a new Controlnet model for Z-Image-Turbo (https://huggingface.co/alibaba-pai/Z-Image-Turbo-Fun-Controlnet-Union). But I think ComfyUI doesn’t support it yet. When I tried to load it, I got this error:

<img width="1545" height="778" alt="Image" src="https://github.com/user-attachments/assets/4f0bf498-2387-4fc0-ae07-7d04cc4239f4" />

```
got prompt
error could not detect control model type.
error checkpoint does not contain controlnet or t2i adapter data F:\AI\Stability Matrix\Models\ControlNet\Z-Image-Turbo-Fun-Controlnet-Union.safetensors
!!! Exception during processing !!! ERROR: controlnet file is invalid and does not contain a valid controlnet model.
Traceback (most recent call last):
  File "F:\AI\ComfyUI-Nightly\ComfyUI\execution.py", line 510, in execute
    output_data, output_ui, has_subgraph, has_pending_tasks = await get_output_data(prompt_id, unique_id, obj, input_data_all, execution_block_cb=execution_block_cb, pre_execute_cb=pre_execute_cb, hidden_inputs=hidden_inputs)
                                                              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "F:\AI\ComfyUI-Nightly\ComfyUI\execution.py", line 324, in get_output_data
    return_values = await _async_map_node_over_list(prompt_id, unique_id, obj, input_data_all, obj.FUNCTION, allow_interrupt=True, execution_block_cb=execution_block_cb, pre_execute_cb=pre_execute_cb, hidden_inputs=hidden_inputs)
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "F:\AI\ComfyUI-Nightly\ComfyUI\execution.py", line 298, in _async_map_node_over_list
    await process_inputs(input_dict, i)
  File "F:\AI\ComfyUI-Nightly\ComfyUI\execution.py", line 286, in process_inputs
    result = f(**inputs)
             ^^^^^^^^^^^
  File "F:\AI\ComfyUI-Nightly\ComfyUI\nodes.py", line 815, in load_controlnet
    raise RuntimeError("ERROR: controlnet file is invalid and does not contain a valid controlnet model.")
RuntimeError: ERROR: controlnet file is invalid and does not contain a valid controlnet model.
```


### Existing Solutions

_No response_

### Other

_No response_

---

*Resurrected by Resurrection Bot 🧬*
