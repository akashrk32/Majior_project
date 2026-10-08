from transformers import VisionEncoderDecoderModel, TrOCRProcessor
import torch

processor = TrOCRProcessor.from_pretrained("models/trocr/repaired_tokenizer")
sample_text = "ಸ್ವಸ್ತಿ ಶ್ರೀ"
tokenized = processor.tokenizer(sample_text)
print("input_ids:", tokenized.input_ids)

# Let's inspect shift_tokens_right implementation in transformers
from transformers.models.vision_encoder_decoder.modeling_vision_encoder_decoder import shift_tokens_right

labels = torch.tensor([tokenized.input_ids])
pad_token_id = processor.tokenizer.pad_token_id
decoder_start_token_id = 0 # or processor.tokenizer.cls_token_id

shifted = shift_tokens_right(labels, pad_token_id, decoder_start_token_id)
print("\nShifted decoder_input_ids:", shifted.tolist())
print("Labels to predict:       ", labels.tolist())
print("\nNotice:")
print("First token to predict is labels[0][0]:", labels[0][0].item(), "(which is", processor.tokenizer.decode([labels[0][0].item()]), ")")
print("First input fed to decoder is:        ", shifted[0][0].item(), "(which is", processor.tokenizer.decode([shifted[0][0].item()]), ")")
