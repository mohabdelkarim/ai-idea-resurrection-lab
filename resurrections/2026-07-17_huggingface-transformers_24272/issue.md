# Finetuning Whisper with prompts

**Repository:** [huggingface/transformers](https://github.com/huggingface/transformers)
**Issue:** [huggingface/transformers#24272](https://github.com/huggingface/transformers/issues/24272)
**Reactions:** 7 👍
**Created:** 2023-06-14T10:36:04Z
**Last Activity:** 2026-07-16T20:29:12Z
**Labels:** Feature request

---

## Original Description

### Feature request

Training code implementation for finetuning Whisper using prompts. 


Hi All,
I’m trying to finetune Whisper by resuming its pre-training task and adding initial prompts as part of the model’s forward pass. I saw this [amazing tutorial](https://huggingface.co/blog/fine-tune-whisper), however, it does not contain a section about using prompts as part of the fine-tuning dataset.

### Motivation

We witness that Whisper is not acting as expected when transcribing with prompts. Sometimes the output is blank text and on other occasions the output text contains reoccurrence. We want to solve such behaviors by fine-tuning Whisper with prompts. 

### Your contribution

Open for ideas.

---

*Resurrected by Resurrection Bot 🧬*
