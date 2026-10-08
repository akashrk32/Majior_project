import sys
import torch
from transformers import TrOCRProcessor, VisionEncoderDecoderModel

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

processor = TrOCRProcessor.from_pretrained("microsoft/trocr-small-stage1")
tokenizer = processor.tokenizer

print("Old vocab size:", len(tokenizer))
# Add 132 tokens
extra_chars = [chr(cp) for cp in range(0x0C80, 0x0D00)] + ["ಱ", "ೞ", "಼", "ಽ", "ೠ", "ೡ", "ೲ", "ೱ", "॥", "।"]
added = tokenizer.add_tokens(list(set(extra_chars)))
print("Added tokens:", added)
print("New vocab size:", len(tokenizer))

model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-small-stage1")
print("Old decoder vocab size:", model.decoder.config.vocab_size)
print("Old embedding weight shape:", model.decoder.get_input_embeddings().weight.shape)

# Resize token embeddings
model.decoder.resize_token_embeddings(len(tokenizer))
print("New decoder vocab size:", model.decoder.config.vocab_size)
print("New embedding weight shape:", model.decoder.get_input_embeddings().weight.shape)
print("Model config vocab size:", model.config.vocab_size if hasattr(model.config, "vocab_size") else "N/A")

model.config.decoder_start_token_id = processor.tokenizer.cls_token_id
model.config.pad_token_id = processor.tokenizer.pad_token_id
model.config.eos_token_id = processor.tokenizer.sep_token_id

# Test a forward pass with dummy image and tokens
dummy_pixel_values = torch.randn(1, 3, 384, 384)
dummy_labels = tokenizer("ಸ್ವಸ್ತಿ ಶ್ರೀ", return_tensors="pt")["input_ids"]
outputs = model(pixel_values=dummy_pixel_values, labels=dummy_labels)
print("Forward pass successful! Loss:", outputs.loss.item())
