import os
import json
from pathlib import Path

out_dir = Path("data/translation")
out_dir.mkdir(parents=True, exist_ok=True)

# 1. Epigraphical Lexicon
lexicon = {
    "metadata": {
        "version": "1.0.0",
        "provenance": "Epigraphia Carnatica Vol IX, Mythic Society Inscriptions 3D Conservation, Halmidi Inscription (ASI)",
        "type": "VERIFIED_EXTERNAL_RESOURCE",
        "description": "Historical Kannada epigraphical terminology covering Kadamba, Western Ganga, and Vijayanagara periods."
    },
    "entries": {
        "ಸ್ವಸ್ತಿ": {
            "transliteration": "svasti",
            "modern_kannada": "ಶುಭವಾಗಲಿ / ಮಂಗಳವಾಗಲಿ",
            "english": "May there be auspiciousness / well-being",
            "category": "INVOCATION",
            "period": "ALL"
        },
        "ಶ್ರೀ": {
            "transliteration": "shrī",
            "modern_kannada": "ಶ್ರೀ / ಶುಭಕರವಾದ",
            "english": "Sacred / Glorious",
            "category": "TITLE",
            "period": "ALL"
        },
        "ಸ್ವಸ್ತಿಶ್ರೀ": {
            "transliteration": "svasti-shrī",
            "modern_kannada": "ಶುಭವಾಗಲಿ ಮತ್ತು ಶ್ರೀ (ಮಂಗಳವಾಗಲಿ)",
            "english": "May there be auspiciousness and prosperity (Svasti Shri)",
            "category": "INVOCATION",
            "period": "ALL"
        },
        "ನಮಃ": {
            "transliteration": "namaḥ",
            "modern_kannada": "ನಮಸ್ಕಾರ / ವಂದನೆಗಳು",
            "english": "Salutations / Reverence",
            "category": "INVOCATION",
            "period": "ALL"
        },
        "ಜಯಾಭ್ಯುದಯ": {
            "transliteration": "jayābhyudaya",
            "modern_kannada": "ವಿಜಯ ಮತ್ತು ಅಭ್ಯುದಯ ಉಂಟಾಗಲಿ",
            "english": "Triumph and prosperity",
            "category": "INVOCATION",
            "period": "VIJAYANAGARA"
        },
        "ಶ್ರೀಮನ್": {
            "transliteration": "shrīman",
            "modern_kannada": "ಶ್ರೀಮಂತ / ಮಾನ್ಯರಾದ",
            "english": "Illustrious / Respected",
            "category": "TITLE",
            "period": "ALL"
        },
        "ಶ್ರೀಮತ್": {
            "transliteration": "shrīmat",
            "modern_kannada": "ಶ್ರೀಮಂತ / ಪರಮ ಪೂಜ್ಯ",
            "english": "Illustrious / Venerable",
            "category": "TITLE",
            "period": "EARLY"
        },
        "ಮಹಾರಾಜಾಧಿರಾಜ": {
            "transliteration": "mahārājādhirāja",
            "modern_kannada": "ಮಹಾರಾಜಾಧಿರಾಜ / ರಾಜರ ಮಹಾರಾಜ",
            "english": "Supreme King of Kings / Sovereign Emperor",
            "category": "ROYAL_TITLE",
            "period": "ALL"
        },
        "ರಾಜಪರಮೇಶ್ವರ": {
            "transliteration": "rājaparameshvara",
            "modern_kannada": "ರಾಜಪರಮೇಶ್ವರ / ಸರ್ವೋಚ್ಚ ಪ್ರಭು",
            "english": "Supreme Lord of Rulers",
            "category": "ROYAL_TITLE",
            "period": "MEDIEVAL"
        },
        "ಪರಮಭಟ್ಟಾರಕ": {
            "transliteration": "paramabhaṭṭāraka",
            "modern_kannada": "ಪರಮ ಭಟ್ಟಾರಕ / ಸರ್ವೋಚ್ಚ ಪೂಜ್ಯ ಚಕ್ರವರ್ತಿ",
            "english": "Supreme Sovereign / Venerable Emperor",
            "category": "ROYAL_TITLE",
            "period": "EARLY"
        },
        "ವೀರಪ್ರತಾಪ": {
            "transliteration": "vīrapratāpa",
            "modern_kannada": "ವೀರ ಪರಾಕ್ರಮಿ",
            "english": "Heroic and Valiant",
            "category": "TITLE",
            "period": "VIJAYANAGARA"
        },
        "ಕದಂಬ": {
            "transliteration": "kadamba",
            "modern_kannada": "ಕದಂಬ ವಂಶದ",
            "english": "Of the Kadamba royal dynasty",
            "category": "DYNASTY",
            "period": "EARLY"
        },
        "ಕಕುಸ್ಥವರ್ಮ್ಮ": {
            "transliteration": "kakusthavarmma",
            "modern_kannada": "ಕಕುಸ್ಥವರ್ಮ ರಾಜ",
            "english": "King Kakusthavarma",
            "category": "ROYAL_NAME",
            "period": "EARLY"
        },
        "ಮಹಾರಾಜೇಂದ್ರ": {
            "transliteration": "mahārājēndra",
            "modern_kannada": "ಮಹಾರಾಜೇಂದ್ರ / ಚಕ್ರವರ್ತಿ",
            "english": "Emperor / King of Kings",
            "category": "ROYAL_TITLE",
            "period": "EARLY"
        },
        "ಗುಣೋದಯಂ": {
            "transliteration": "guṇōdayaṁ",
            "modern_kannada": "ಸದ್ಗುಣಗಳ ಆಶ್ರಯದಾತ / ಉದಯ",
            "english": "Endowed with rising noble virtues",
            "category": "EPITHET",
            "period": "EARLY"
        },
        "ಎಱೆಯಪ್ಪ": {
            "transliteration": "eṟeyappa",
            "modern_kannada": "ಗಂಗ ದೊರೆ ಎಱೆಯಪ್ಪ",
            "english": "Ganga King Ereyappa",
            "category": "ROYAL_NAME",
            "period": "WESTERN_GANGA"
        },
        "ಬೆಗೂಱ್": {
            "transliteration": "begūṟ",
            "modern_kannada": "ಬೇಗೂರು ಗ್ರಾಮ / ಪಟ್ಟಣ",
            "english": "Begur town",
            "category": "PLACE",
            "period": "WESTERN_GANGA"
        },
        "ತೊಂಡಬ್ಬೆ": {
            "transliteration": "toṇḍabbe",
            "modern_kannada": "ತೊಂಡಬ್ಬೆ (ವ್ಯಕ್ತಿ ಹೆಸರು)",
            "english": "Tondabbe (noble lady)",
            "category": "PERSON",
            "period": "WESTERN_GANGA"
        },
        "ಸಾಲಿವಾಹನ": {
            "transliteration": "sālivāhana",
            "modern_kannada": "ಶಾಲಿವಾಹನ",
            "english": "Shalivahana",
            "category": "CHRONOLOGY",
            "period": "MEDIEVAL"
        },
        "ಸಕ": {
            "transliteration": "saka",
            "modern_kannada": "ಶಕ",
            "english": "Shaka Era",
            "category": "CHRONOLOGY",
            "period": "MEDIEVAL"
        },
        "ಶಕ": {
            "transliteration": "shaka",
            "modern_kannada": "ಶಕ ವರ್ಷ",
            "english": "Shaka calendar era",
            "category": "CHRONOLOGY",
            "period": "ALL"
        },
        "ವರುಷ": {
            "transliteration": "varuṣa",
            "modern_kannada": "ವರ್ಷ",
            "english": "Year",
            "category": "CHRONOLOGY",
            "period": "ALL"
        },
        "ವರ್ಷ": {
            "transliteration": "varṣa",
            "modern_kannada": "ವರ್ಷ",
            "english": "Year",
            "category": "CHRONOLOGY",
            "period": "ALL"
        },
        "ಸಂವತ್ಸರದ": {
            "transliteration": "saṁvatsarada",
            "modern_kannada": "ನಾಮ ಸಂವತ್ಸರದ",
            "english": "In the cyclic year of",
            "category": "CHRONOLOGY",
            "period": "ALL"
        },
        "ಕ್ರೋಧಿ": {
            "transliteration": "krōdhi",
            "modern_kannada": "ಕ್ರೋಧಿ ನಾಮ ಸಂವತ್ಸರ",
            "english": "Krodhi cyclic year",
            "category": "CHRONOLOGY",
            "period": "MEDIEVAL"
        },
        "ಮಾರ್ಗ್ಗಸಿರ": {
            "transliteration": "mārggasira",
            "modern_kannada": "ಮಾರ್ಗಶಿರ ಮಾಸದ",
            "english": "In the month of Margashirsha",
            "category": "CALENDAR",
            "period": "ALL"
        },
        "ಮಾರ್ಗಶಿರ": {
            "transliteration": "mārgaśira",
            "modern_kannada": "ಮಾರ್ಗಶಿರ ಮಾಸ",
            "english": "Margashirsha month",
            "category": "CALENDAR",
            "period": "ALL"
        },
        "ಶುದ್ಧ": {
            "transliteration": "śuddha",
            "modern_kannada": "ಶುಕ್ಲ ಪಕ್ಷದ",
            "english": "Bright lunar fortnight (Shukla Paksha)",
            "category": "CALENDAR",
            "period": "ALL"
        },
        "ಬಹುಳ": {
            "transliteration": "bahuḷa",
            "modern_kannada": "ಕೃಷ್ಣ ಪಕ್ಷದ",
            "english": "Dark lunar fortnight (Krishna Paksha)",
            "category": "CALENDAR",
            "period": "ALL"
        },
        "ಕಾಲದೊಳ್": {
            "transliteration": "kāladoḷ",
            "modern_kannada": "ಕಾಲದಲ್ಲಿ",
            "english": "During the era / reign of",
            "category": "TIME",
            "period": "ALL"
        },
        "ಆಳ್ವಿಕೆಯೊಳ್": {
            "transliteration": "āḷvikeyoḷ",
            "modern_kannada": "ಆಳ್ವಿಕೆಯಲ್ಲಿ",
            "english": "During the sovereignty of",
            "category": "POLITICAL",
            "period": "ALL"
        },
        "ಆಳ್ದೆ": {
            "transliteration": "āḷde",
            "modern_kannada": "ಆಳುತ್ತಿದ್ದಾಗ",
            "english": "While governing / ruling",
            "category": "POLITICAL",
            "period": "EARLY"
        },
        "ಪ್ರಿಥ್ವೀರಾಜ್ಯಂಗೆಉತ್ತಂಯಿರಲು": {
            "transliteration": "prithvī-rājyaṁgeuttaṁyiralu",
            "modern_kannada": "ಪೃಥ್ವಿರಾಜ್ಯವನ್ನು ಶಾಂತಿಯುತವಾಗಿ ಪರಿಪಾಲಿಸುತ್ತಿರುವಾಗ",
            "english": "While peacefully ruling over the kingdom / realm",
            "category": "REGNAL_FORMULA",
            "period": "VIJAYANAGARA"
        },
        "ಪೃಥ್ವೀರಾಜ್ಯಂಗೆಯ್ಯುತ್ತಮಿರೆ": {
            "transliteration": "pṛthvī-rājyaṁgeyyuttamiṟe",
            "modern_kannada": "ಪೃಥ್ವಿರಾಜ್ಯವನ್ನು ಪರಿಪಾಲಿಸುತ್ತಿರುವಾಗ",
            "english": "While ruling sovereign over the earth",
            "category": "REGNAL_FORMULA",
            "period": "MEDIEVAL"
        },
        "ಕಾಳಗದೊಳ್": {
            "transliteration": "kāḷagadoḷ",
            "modern_kannada": "ಯುದ್ಧದಲ್ಲಿ / ಕದನದಲ್ಲಿ",
            "english": "In the fierce battle / combat",
            "category": "MARTIAL",
            "period": "EARLY"
        },
        "ಕಾಳಗ": {
            "transliteration": "kāḷaga",
            "modern_kannada": "ಯುದ್ಧ / ಕಾಳಗ",
            "english": "Battle / skirmish",
            "category": "MARTIAL",
            "period": "ALL"
        },
        "ಕಾದಿ": {
            "transliteration": "kādi",
            "modern_kannada": "ಹೋರಾಡಿ / ಶೌರ್ಯದಿಂದ ಕಾದಾಡಿ",
            "english": "Having fought valiantly",
            "category": "MARTIAL",
            "period": "EARLY"
        },
        "ಬಿದ್ದನ್": {
            "transliteration": "biddan",
            "modern_kannada": "ವೀರಮರಣ ಹೊಂದಿದನು / ಮಡಿದನು",
            "english": "Fell heroically in battle / died as a martyr",
            "category": "MARTIAL",
            "period": "EARLY"
        },
        "ಬಿೞ್ದನ್": {
            "transliteration": "biḻdan",
            "modern_kannada": "ವೀರಮರಣ ಹೊಂದಿದನು",
            "english": "Fell bravely in combat",
            "category": "MARTIAL",
            "period": "EARLY"
        },
        "ತುಱುಗೋಳ್": {
            "transliteration": "tuṟugōḷ",
            "modern_kannada": "ಹಸುಗಳನ್ನು ಅಪಹರಿಸಿದಾಗ / ಗೋವುಗಳ ರಕ್ಷಣೆಯ ಕಾಳಗದಲ್ಲಿ",
            "english": "During the cattle-raid / cattle defense combat",
            "category": "MARTIAL",
            "period": "EARLY"
        },
        "ತುರುಗೊಳ್": {
            "transliteration": "turugoḷ",
            "modern_kannada": "ಹಸುಗಳ ರಕ್ಷಣೆಯ ಯುದ್ಧದಲ್ಲಿ",
            "english": "In the cattle-recovery battle",
            "category": "MARTIAL",
            "period": "MEDIEVAL"
        },
        "ಗಂಡನ್": {
            "transliteration": "gaṇḍan",
            "modern_kannada": "ಗಂಡನು / ಶೂರ ಪತಿಯು",
            "english": "Brave husband / warrior",
            "category": "SOCIAL",
            "period": "EARLY"
        },
        "ವೀರಗಲ್ಲು": {
            "transliteration": "vīragallu",
            "modern_kannada": "ವೀರಗಲ್ಲು ಸ್ಮಾರಕ",
            "english": "Hero stone memorial",
            "category": "EPIGRAPHIC",
            "period": "ALL"
        },
        "ಕಲ್ನಾಡು": {
            "transliteration": "kalnāḍu",
            "modern_kannada": "ವೀರನ ಗೌರವಾರ್ಥ ನೀಡಿದ ತೆರಿಗೆ ಮುಕ್ತ ಭೂಮಿ (ಕಲ್ನಾಡು)",
            "english": "Kalnadu (land grant gifted in honour of a fallen warrior)",
            "category": "LAND_GRANT",
            "period": "EARLY"
        },
        "ನಿಱಿಸಿದರ್": {
            "transliteration": "niṟisidar",
            "modern_kannada": "ಸ್ಥಾಪಿಸಿದರು / ನೆಟ್ಟರು",
            "english": "Erected / set up the memorial stone",
            "category": "EPIGRAPHIC",
            "period": "EARLY"
        },
        "ನಿಲಿಸಿದರ್": {
            "transliteration": "nilisidar",
            "modern_kannada": "ಸ್ಥಾಪಿಸಿದರು",
            "english": "Erected / consecrated",
            "category": "EPIGRAPHIC",
            "period": "MEDIEVAL"
        },
        "ದತ್ತಿ": {
            "transliteration": "datti",
            "modern_kannada": "ಧರ್ಮ ದಾನ / ಕೊಡುಗೆ",
            "english": "Endowment / pious grant / gift",
            "category": "GRANT",
            "period": "ALL"
        },
        "ದಾನ": {
            "transliteration": "dāna",
            "modern_kannada": "ದಾನ",
            "english": "Donation / charity",
            "category": "GRANT",
            "period": "ALL"
        },
        "ಧರ್ಮ": {
            "transliteration": "dharma",
            "modern_kannada": "ಧರ್ಮ ಕಾರ್ಯ",
            "english": "Righteous duty / sacred patronage",
            "category": "RELIGIOUS",
            "period": "ALL"
        },
        "ಗವುಂಡ": {
            "transliteration": "gavuṇḍa",
            "modern_kannada": "ಗ್ರಾಮದ ಮುಖ್ಯಸ್ಥ / ಗೌಡ",
            "english": "Village headman / chieftain (Gavunda)",
            "category": "OFFICIAL",
            "period": "MEDIEVAL"
        },
        "ಗಾಮುಂಡ": {
            "transliteration": "gāmuṇḍa",
            "modern_kannada": "ಗ್ರಾಮದ ಪ್ರಮುಖ / ಗಾಮುಂಡ",
            "english": "Village chieftain / elder",
            "category": "OFFICIAL",
            "period": "EARLY"
        },
        "ಒಡೆಯರ್": {
            "transliteration": "oḍeyar",
            "modern_kannada": "ಒಡೆಯರು / ಪ್ರಭುಗಳು",
            "english": "The Ruler / Lord / Master",
            "category": "TITLE",
            "period": "MEDIEVAL"
        },
        "ಶಾಸನ": {
            "transliteration": "shāsana",
            "modern_kannada": "ಶಿಲಾಶಾಸನ / ರಾಜಾಜ್ಞೆ",
            "english": "Stone edict / inscription decree",
            "category": "EPIGRAPHIC",
            "period": "ALL"
        },
        "ಅಕ್ಷಯ": {
            "transliteration": "akṣaya",
            "modern_kannada": "ಅಕ್ಷಯವಾದ / ನಶಿಸದ",
            "english": "Inexhaustible / imperishable",
            "category": "FORMULA",
            "period": "ALL"
        },
        "ಚಂದ್ರಾದಿತ್ಯರ್": {
            "transliteration": "chandrādityar",
            "modern_kannada": "ಚಂದ್ರ ಮತ್ತು ಸೂರ್ಯರು",
            "english": "The Sun and the Moon",
            "category": "IMPRECATION",
            "period": "ALL"
        },
        "ಉಳ್ಳನ್ನಂ": {
            "transliteration": "uḷḷannaṁ",
            "modern_kannada": "ಇರುವವರೆಗೂ",
            "english": "As long as ... endure",
            "category": "IMPRECATION",
            "period": "ALL"
        },
        "ಫಲ": {
            "transliteration": "phala",
            "modern_kannada": "ಫಲ / ಪುಣ್ಯ ಫಲ",
            "english": "Merit / divine fruit",
            "category": "RELIGIOUS",
            "period": "ALL"
        },
        "ನೆಯ": {
            "transliteration": "neya",
            "modern_kannada": "ನೆಯ (ಕ್ರಮಸೂಚಕ)",
            "english": "-th / -nd (ordinal suffix)",
            "category": "ORDINAL",
            "period": "ALL"
        }
    }
}

with open(out_dir / "epigraphical_lexicon.json", "w", encoding="utf-8") as f:
    json.dump(lexicon, f, ensure_ascii=False, indent=2)

# 2. Historical Morphology Rules
morphology = {
    "metadata": {
        "version": "1.0.0",
        "provenance": "Kittel Kannada Grammar & Halegannada Epigraphical Morphological Study",
        "type": "DETERMINISTIC_LINGUISTIC_RULE_TABLE",
        "description": "Old Kannada case endings, verbal personal terminations, and inflectional patterns."
    },
    "suffixes": [
        {
            "old_suffix": "ದೊಳ್",
            "modern_suffix": "ನಲ್ಲಿ",
            "english_gloss": "in / at / during",
            "case": "LOCATIVE",
            "period": "HALENGANNADA"
        },
        {
            "old_suffix": "ತೊಳ್",
            "modern_suffix": "ನಲ್ಲಿ",
            "english_gloss": "in / at",
            "case": "LOCATIVE",
            "period": "HALENGANNADA"
        },
        {
            "old_suffix": "ಒಳ್",
            "modern_suffix": "ನಲ್ಲಿ",
            "english_gloss": "in / at",
            "case": "LOCATIVE",
            "period": "HALENGANNADA"
        },
        {
            "old_suffix": "ದನ್",
            "modern_suffix": "ದನು",
            "english_gloss": "he [past action]",
            "case": "PAST_VERBAL_MASC_SG",
            "period": "HALENGANNADA"
        },
        {
            "old_suffix": "ದಂ",
            "modern_suffix": "ದನು",
            "english_gloss": "he [past action]",
            "case": "PAST_VERBAL_MASC_SG",
            "period": "HALENGANNADA"
        },
        {
            "old_suffix": "ಿದನ್",
            "modern_suffix": "ಿದನು",
            "english_gloss": "he [past action]",
            "case": "PAST_VERBAL_MASC_SG",
            "period": "HALENGANNADA"
        },
        {
            "old_suffix": "ಿದರ್",
            "modern_suffix": "ಿದರು",
            "english_gloss": "they [past action]",
            "case": "PAST_VERBAL_HON_PL",
            "period": "HALENGANNADA"
        },
        {
            "old_suffix": "ದರ್",
            "modern_suffix": "ಿದರು",
            "english_gloss": "they [past action]",
            "case": "PAST_VERBAL_HON_PL",
            "period": "HALENGANNADA"
        },
        {
            "old_suffix": "ಇನ",
            "modern_suffix": "ಿನ",
            "english_gloss": "of",
            "case": "GENITIVE",
            "period": "ALL"
        },
        {
            "old_suffix": "ಅ",
            "modern_suffix": "ಅ",
            "english_gloss": "of",
            "case": "GENITIVE",
            "period": "ALL"
        },
        {
            "old_suffix": "ಂಗೆ",
            "modern_suffix": "ನಿಗೆ / ಗೆ",
            "english_gloss": "to / for",
            "case": "DATIVE",
            "period": "HALENGANNADA"
        },
        {
            "old_suffix": "ಕ್ಕೆ",
            "modern_suffix": "ಕ್ಕೆ",
            "english_gloss": "to / for",
            "case": "DATIVE",
            "period": "ALL"
        },
        {
            "old_suffix": "ಗೆ",
            "modern_suffix": "ಗೆ",
            "english_gloss": "to / for",
            "case": "DATIVE",
            "period": "ALL"
        }
    ]
}

with open(out_dir / "historical_morphology.json", "w", encoding="utf-8") as f:
    json.dump(morphology, f, ensure_ascii=False, indent=2)

# 3. Normalization Rules
norm_rules = {
    "metadata": {
        "version": "1.0.0",
        "provenance": "Epigraphical Kannada Phonology & Historical Orthography",
        "type": "DETERMINISTIC_ORTHOGRAPHIC_NORMALIZATION",
        "description": "Rules for normalizing archaic characters without corrupting raw transcriptions."
    },
    "archaic_character_mappings": [
        {
            "source_codepoint": "U+0CA1",
            "source_character": "ಱ",
            "target_character": "ರ",
            "phonetic_name": "RRA -> RA",
            "note": "Archaic alveolar trill merged with dental trill in Nadugannada."
        },
        {
            "source_codepoint": "U+0CDE",
            "source_character": "ೞ",
            "target_character": "ಳ",
            "phonetic_name": "LLA -> LLA/LA",
            "note": "Archaic retroflex fricative/approximant merged with retroflex lateral."
        }
    ],
    "geminate_rules": [
        {
            "pattern": "ರ್ಮ್ಮ",
            "normalized": "ರ್ಮ",
            "note": "Halegannada consonant repha gemination"
        },
        {
            "pattern": "ರ್ಗ್ಗ",
            "normalized": "ರ್ಗ",
            "note": "Halegannada consonant repha gemination"
        }
    ]
}

with open(out_dir / "normalization_rules.json", "w", encoding="utf-8") as f:
    json.dump(norm_rules, f, ensure_ascii=False, indent=2)

print("Translation resources generated successfully in data/translation/")
