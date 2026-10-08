import sys
from pathlib import Path
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
import torch

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

processor = TrOCRProcessor.from_pretrained("models/trocr/repaired_tokenizer")
print("=== TOKENIZER SPECIAL TOKENS ===")
print("bos_token:", processor.tokenizer.bos_token, processor.tokenizer.bos_token_id)
print("eos_token:", processor.tokenizer.eos_token, processor.tokenizer.eos_token_id)
print("cls_token:", processor.tokenizer.cls_token, processor.tokenizer.cls_token_id)
print("sep_token:", processor.tokenizer.sep_token, processor.tokenizer.sep_token_id)
print("pad_token:", processor.tokenizer.pad_token, processor.tokenizer.pad_token_id)
print("unk_token:", processor.tokenizer.unk_token, processor.tokenizer.unk_token_id)

sample_text = "ಸ್ವಸ್ತಿ ಶ್ರೀ"
encoded = processor.tokenizer(sample_text)
print("\nSample text:", sample_text)
print("Encoded IDs:", encoded.input_ids)
print("Decoded full:", processor.tokenizer.decode(encoded.input_ids))
print("Decoded skip_special:", processor.tokenizer.decode(encoded.input_ids, skip_special_tokens=True))

model = VisionEncoderDecoderModel.from_pretrained("models/trocr/best_model")
print("\n=== MODEL CONFIG ===")
print("model.config.decoder_start_token_id:", getattr(model.config, "decoder_start_token_id", None))
print("model.decoder.config.bos_token_id:", getattr(model.decoder.config, "bos_token_id", None))
print("model.decoder.config.eos_token_id:", getattr(model.decoder.config, "eos_token_id", None))
print("model.decoder.config.pad_token_id:", getattr(model.decoder.config, "pad_token_id", None))
print("model.config.eos_token_id:", getattr(model.config, "eos_token_id", None))
print("model.config.pad_token_id:", getattr(model.config, "pad_token_id", None))

if hasattr(model, "generation_config") and model.generation_config is not None:
    print("\n=== GENERATION CONFIG ===")
    print("gen.decoder_start_token_id:", getattr(model.generation_config, "decoder_start_token_id", None))
    print("gen.bos_token_id:", getattr(model.generation_config, "bos_token_id", None))
    print("gen.eos_token_id:", getattr(model.generation_config, "eos_token_id", None))
    print("gen.pad_token_id:", getattr(model.generation_config, "pad_token_id", None))
    print("gen.forced_bos_token_id:", getattr(model.generation_config, "forced_bos_token_id", None))
    print("gen.forced_eos_token_id:", getattr(model.generation_config, "forced_eos_token_id", None))


# Test running generation on a blank / dummy image or a real crop
from PIL import Image
test_crop_path = Path("data/trocr/test")
crops = list(test_crop_path.glob("*.png"))
if crops:
    img = Image.open(crops[0]).convert("RGB")
    pixel_values = processor(img, return_tensors="pt").pixel_values
    
    print("\n=== TEST GENERATE ON CROP ===", crops[0].name)
    with torch.no_grad():
        gen_out = model.generate(pixel_values, max_length=64, num_beams=1)
        print("Generated raw token IDs:", gen_out.tolist())
        decoded = processor.batch_decode(gen_out, skip_special_tokens=False)
        print("Decoded with special:", decoded)
        decoded_skip = processor.batch_decode(gen_out, skip_special_tokens=True)
        print("Decoded without special:", decoded_skip)

        # Check decoder logits directly with teacher forcing (first 5 tokens of sample)
        labels = torch.tensor([[processor.tokenizer.cls_token_id, 64000, 64001]]).long()
        outputs = model(pixel_values=pixel_values, labels=labels)
        print("Teacher forcing loss:", outputs.loss.item())
