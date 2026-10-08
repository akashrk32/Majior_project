import sys
import json
from transformers import TrOCRProcessor, VisionEncoderDecoderModel

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

processor = TrOCRProcessor.from_pretrained("microsoft/trocr-small-stage1")
tokenizer = processor.tokenizer

print("Tokenizer type:", type(tokenizer))
print("Vocab size before:", len(tokenizer))
print("unk_token_id:", tokenizer.unk_token_id)

sample_text = "ಸ್ವಸ್ತಿ ಶ್ರೀ ಪೃಥ್ವೀರಾಜ್ಯಂಗೆಯ್ಯುತ್ತಮಿರೆ ೧೨೩೪೫ ಱ ೞ"
tokens = tokenizer(sample_text)["input_ids"]
print("Token IDs before:", tokens)
print("Unk count before:", tokens.count(tokenizer.unk_token_id))
print("Decoded before:", tokenizer.decode(tokens, skip_special_tokens=True))
