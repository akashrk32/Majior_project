import sys
import torch
import pandas as pd
from PIL import Image
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from torch.optim import AdamW

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

processor = TrOCRProcessor.from_pretrained("models/trocr/repaired_tokenizer")
model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-small-stage1")
model.decoder.resize_token_embeddings(len(processor.tokenizer))

for p in model.encoder.parameters():
    p.requires_grad = False

model.config.decoder_start_token_id = processor.tokenizer.cls_token_id
model.config.pad_token_id = processor.tokenizer.pad_token_id
model.config.eos_token_id = processor.tokenizer.sep_token_id
model.generation_config.decoder_start_token_id = processor.tokenizer.cls_token_id
model.generation_config.pad_token_id = processor.tokenizer.pad_token_id
model.generation_config.eos_token_id = processor.tokenizer.sep_token_id
model.generation_config.max_length = 64
model.generation_config.early_stopping = True

# Load 2 sample training lines
df = pd.read_csv("data/trocr/metadata.csv")
train_rows = df[df["split"] == "train"].head(2)

images = []
labels_list = []
texts = []
for _, row in train_rows.iterrows():
    img = Image.open(row["image_path"]).convert("RGB")
    images.append(img)
    texts.append(row["text"])
    
    tokens = processor.tokenizer(row["text"], add_special_tokens=False).input_ids + [processor.tokenizer.sep_token_id]
    if len(tokens) > 64:
        tokens = tokens[:63] + [processor.tokenizer.sep_token_id]
    tokens = tokens + [processor.tokenizer.pad_token_id] * (64 - len(tokens))
    lbl = torch.tensor(tokens).long()
    lbl[lbl == processor.tokenizer.pad_token_id] = -100
    labels_list.append(lbl)

pixel_values = processor(images, return_tensors="pt").pixel_values
labels = torch.stack(labels_list)

optimizer = AdamW(filter(lambda p: p.requires_grad, model.parameters()), lr=5e-4)

print("Ground Truth texts:")
for t in texts:
    print(" ", repr(t))

print("\nInitial Generation (Before Training):")
with torch.no_grad():
    gen = model.generate(pixel_values, max_length=64, num_beams=1)
    preds = processor.batch_decode(gen, skip_special_tokens=True)
    for p in preds:
        print("  Pred:", repr(p))

print("\nOverfitting on 2 samples for 15 steps...")
model.train()
for step in range(15):
    optimizer.zero_grad()
    outputs = model(pixel_values=pixel_values, labels=labels)
    loss = outputs.loss
    loss.backward()
    optimizer.step()
    if (step + 1) % 5 == 0:
        print(f"  Step {step+1}/15, Loss: {loss.item():.4f}")

model.eval()
print("\nGeneration After 15 Steps of Training:")
with torch.no_grad():
    gen = model.generate(pixel_values, max_length=64, num_beams=1)
    preds = processor.batch_decode(gen, skip_special_tokens=True)
    for p in preds:
        print("  Pred:", repr(p))
