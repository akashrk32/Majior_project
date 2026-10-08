from transformers import TrOCRProcessor
from transformers.models.vision_encoder_decoder.modeling_vision_encoder_decoder import shift_tokens_right
import torch
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


processor = TrOCRProcessor.from_pretrained("models/trocr/repaired_tokenizer")
sample_text = "ಸ್ವಸ್ತಿ ಶ್ರೀ"

# 1. Without leading bos token, but with eos token:
tokens = processor.tokenizer(sample_text, add_special_tokens=False).input_ids
labels_list = tokens + [processor.tokenizer.eos_token_id]
labels = torch.tensor([labels_list])

shifted = shift_tokens_right(labels, pad_token_id=processor.tokenizer.pad_token_id, decoder_start_token_id=processor.tokenizer.cls_token_id)

print("Text:                     ", sample_text)
print("Tokens (no special):      ", tokens)
print("Labels:                   ", labels.tolist())
print("Shifted decoder_input_ids:", shifted.tolist())
print("Input at step 0:          ", shifted[0][0].item(), "-> Decodes to:", processor.tokenizer.decode([shifted[0][0].item()]))
print("Target to predict at step 0:", labels[0][0].item(), "-> Decodes to:", processor.tokenizer.decode([labels[0][0].item()]))
print("Target at last step:      ", labels[0][-1].item(), "-> Decodes to:", processor.tokenizer.decode([labels[0][-1].item()]))
