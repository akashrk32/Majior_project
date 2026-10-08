import sys
import torch
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

tok_dir = "models/trocr/repaired_tokenizer"
model_dir = "models/trocr/best_model"

processor = TrOCRProcessor.from_pretrained(tok_dir)
tokenizer = processor.tokenizer
model = VisionEncoderDecoderModel.from_pretrained(model_dir)

print("--- TOKENIZER SPECIAL TOKENS ---")
print("bos_token_id        :", tokenizer.bos_token_id, repr(tokenizer.bos_token))
print("eos_token_id        :", tokenizer.eos_token_id, repr(tokenizer.eos_token))
print("sep_token_id        :", tokenizer.sep_token_id, repr(tokenizer.sep_token))
print("cls_token_id        :", tokenizer.cls_token_id, repr(tokenizer.cls_token))
print("pad_token_id        :", tokenizer.pad_token_id, repr(tokenizer.pad_token))
print("unk_token_id        :", tokenizer.unk_token_id, repr(tokenizer.unk_token))

print("\n--- MODEL CONFIG SPECIAL TOKENS ---")
print("decoder_start_token_id:", model.config.decoder_start_token_id)
print("eos_token_id          :", model.config.eos_token_id)
print("pad_token_id          :", model.config.pad_token_id)
print("decoder.bos_token_id  :", model.decoder.config.bos_token_id)
print("decoder.eos_token_id  :", model.decoder.config.eos_token_id)
print("decoder.pad_token_id  :", model.decoder.config.pad_token_id)

# Test a single forward pass and manual decoding of logits
text = "ಎೞುತತುಮಪುಣರುತತಾಣ್ಮಲೈಯ"
tokens_no_spec = tokenizer(text, add_special_tokens=False).input_ids
print("\nTokens without special:", tokens_no_spec)
print("Decoded back:", tokenizer.decode(tokens_no_spec))

# When labels have eos_token_id:
labels_list = tokens_no_spec + [tokenizer.eos_token_id]
labels = torch.tensor([labels_list])

# Load image
img_path = Path("data/trocr_verified/train/arachalur300cetevanchataninscription_line_001.png")
image = Image.open(img_path).convert("RGB")

pixel_values = processor(image, return_tensors="pt").pixel_values

model.eval()
with torch.no_grad():
    out = model(pixel_values=pixel_values, labels=labels)
    print("\nForward pass loss:", out.loss.item())
    logits = out.logits # (1, seq_len, vocab_size)
    pred_token_ids = logits.argmax(dim=-1)[0].tolist()
    print("Teacher forcing argmax token IDs:", pred_token_ids)
    print("Teacher forcing decoded:", tokenizer.decode(pred_token_ids))

    # Now generate autoregressively
    gen_out = model.generate(pixel_values, max_length=64, eos_token_id=tokenizer.eos_token_id)
    print("\nAutoregressive generated token IDs:", gen_out[0].tolist())
    print("Autoregressive generated decoded:", tokenizer.decode(gen_out[0].tolist(), skip_special_tokens=False))
