import json
import torch
from transformers import WhisperForConditionalGeneration, WhisperTokenizer, Trainer, TrainingArguments
from datasets import load_dataset


class PromptDataset(torch.utils.data.Dataset):
    def __init__(self, dataset, tokenizer, prompts):
        self.dataset = dataset
        self.tokenizer = tokenizer
        self.prompts = prompts

    def __getitem__(self, idx):
        example = self.dataset[idx]
        prompt = self.prompts[idx % len(self.prompts)]
        inputs = self.tokenizer(prompt, return_tensors='pt', max_length=100, truncation=True)
        labels = self.tokenizer(example['text'], return_tensors='pt', max_length=100, truncation=True)
        return {
            'input_ids': inputs['input_ids'].flatten(),
            'attention_mask': inputs['attention_mask'].flatten(),
            'labels': labels['input_ids'].flatten()
        }

    def __len__(self):
        return len(self.dataset)


def compute_metrics(pred):
    metric = evaluate.load('accuracy')
    predictions, labels = pred
    metric.add_batch(predictions=predictions, references=labels)
    return metric.compute()


def main():
    model_name = 'whisper-base'
    prompts = ['This is a test prompt.', 'Another test prompt.']
    dataset = load_dataset('hf-internal-testing/whisper-sample', split='train')
    tokenizer = WhisperTokenizer.from_pretrained(model_name)
    model = WhisperForConditionalGeneration.from_pretrained(model_name)

    dataset = PromptDataset(dataset, tokenizer, prompts)

    training_args = TrainingArguments(
        output_dir='./results',
        num_train_epochs=3,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=64,
        warmup_steps=500,
        weight_decay=0.01,
        logging_dir='./logs',
        load_best_model_at_end=True,
        metric_for_best_model='accuracy',
        greater_is_better=True,
        save_total_limit=2,
        save_steps=500,
        evaluation_strategy='epoch'
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        compute_metrics=compute_metrics
    )

    try:
        trainer.train()
    except Exception as e:
        print(f'An error occurred: {e}')


if __name__ == '__main__':
    main()