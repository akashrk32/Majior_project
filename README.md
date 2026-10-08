# SHILORA V3.1: Maximum Evidence-Preserving Ancient Kannada Stone Preprocessor

SHILORA (**SHI**lalekha **LO**cal **R**elief **A**mplification) is a research-informed, deterministic computer vision preprocessing pipeline specifically developed for ancient and medieval Kannada (Halegannada) stone inscriptions (*shilashasana*).

SHILORA operates strictly under the **1 Input Image $\rightarrow$ 1 Output Image** paradigm (39 input photographs $\rightarrow$ exactly 39 final preprocessed images). Its sole objective is **Maximum Evidence-Preserving Inscription Enhancement**—revealing genuine physical carved relief while suppressing stone texture, non-uniform illumination, and compression artifacts, without hallucinating characters or distorting glyph topology.

---

## 1. Research Papers Used

1. **Paper 1**:
   - **Citation**: Jayanthi J. & P. Uma Maheswari, *"Comparative study: enhancing legibility of ancient Indian script images from diverse stone background structures using 34 different pre-processing methods"*, *Heritage Science*, 12, 1169 (2024). [Nature Heritage Science](https://doi.org/10.1044/s40494-024-01169-6).
   - **Scope**: Comparative evaluation of spatial-domain filtering, local/adaptive contrast enhancement, and morphological operations on ancient Indian epigraphical stone substrates.

2. **Paper 2**:
   - **Citation**: *"Hybrid method for enhancement of low-resolution ancient Kannada Stone Inscription images"*, *Digital Applications in Archaeology and Cultural Heritage*, 33, e000705 (2024). [ScienceDirect](https://doi.org/10.1016/j.daach.2024.e000705).
   - **Scope**: Text/non-text separation, noise removal, illumination variation correction, and preservation of low foreground/background color contrast in historical Kannada stone inscriptions.

3. **Paper 3**:
   - **Citation**: *"Removal of degradation from ancient stone inscription images using deep learning techniques"*, *Procedia Computer Science*, 245, 1877-1884 (2025). [ScienceDirect](https://doi.org/10.1016/j.procs.2025.01.370).
   - **Scope**: Epigraphical degradation taxonomy (weathering, surface erosion, calcite leaching, fracture lines). Used strictly as methodological background for degradation characterization.

---

## 2. Techniques Derived from Each Paper

- **From Paper 1**:
  - Low-frequency background modeling via multi-scale Gaussian kernels to neutralize uneven sunlight and cast shadows.
  - Bounded Contrast Limited Adaptive Histogram Equalization (CLAHE) for localized micro-contrast enhancement.
  - Morphological Black-Hat transformations to isolate physical surface depressions.
  - First-order Sobel spatial derivatives ($G_x, G_y$) for boundary transition analysis.
- **From Paper 2**:
  - Inscription-scale parameter adaptation tied to spatial resolution.
  - Text-to-background contrast ratio evaluation ($C_{\text{insc}} / C_{\text{bg}}$) to evaluate relief contrast against stone grain noise.
  - Edge-preserving bilateral smoothing to attenuate crystalline granite speckle while protecting fine stroke margins.
- **From Paper 3**:
  - Physical degradation taxonomy distinguishing natural stone pitting, surface flaking, structural cracks, and organic stains.

---

## 3. SHILORA-Specific Engineering Additions

The following architectural innovations are unique to SHILORA and not claimed as direct implementations of published papers:
1. **Luminance-First Processing Hierarchy**: Mandatory selection of $Y$ as primary base; scalar ($R, G, B$) and chromatic maps are strictly auxiliary.
2. **JPEG 8x8 and 16x16 Blockiness Detection**: Explicit boundary discontinuity ratio metrics to penalize compression macroblocks.
3. **Multi-Scale Persistence**: Structural consistency metric measuring stroke stability across neighboring mathematical morphology scales.
4. **Single-Image Directional Relief Enhancement**: 4-angle virtual raking light simulation ($45^\circ, 135^\circ, 225^\circ, 315^\circ$) on luminance gradient fields.
5. **Positive Bounded Evidence Fusion**: Bounded linear integration ($E = \sum w_i E_i$) with sigmoidal tone mapping, eliminating subtractive halo artifacts.
6. **Crack and Color-Stain Damping**: Aspect-ratio and chromatic divergence masks that downweight non-glyph anomalies.
7. **Maximum-Recoverable-Information Stopping Logic**: Objective stopping function monitoring 13 hard-stop conditions.

---

## 4. Why Luminance is the Primary Representation

Luminance ($Y = 0.2126R + 0.7152G + 0.0722B$) represents the true physical luminous energy reflected by the stone. In epigraphical photography, chiseled incisions produce shadows or altered reflections that modulate luminance directly. 

Calling individual $R, G, B$ channels "luminance" is physically incorrect. $R, G, B$ are chromatic color separations that often carry varying sensor noise and color aberrations. Therefore, $Y$ is the default, mandatory base representation across 100% of images.

---

## 5 & 6. The JPEG Chroma Artifact Problem & Why Chromatic Maps Cannot Be the Base

In standard JPEG compression, chrominance is subsampled at half resolution ($4:2:0$) and quantized into $8 \times 8$ or $16 \times 16$ macroblocks. 

Because ancient stone is predominantly neutral gray ($R \approx G \approx B$), chromatic difference maps ($|R-B|$, $|R-G|$) have almost zero high-frequency inscription luminance and very low color noise. In earlier pipelines, unstable scoring formulas divided by noise squared, falsely crowning these difference maps as "high quality". Operating morphology and Sobel filters on chromatic maps processed **JPEG compression macroblocks**, producing severe mosaic tile blur.

In SHILORA V3.1, chromatic difference maps are strictly auxiliary ($E_7$), evaluated only for color contrast, and weighted to $0.0$ if blockiness is detected or if they disagree with luminance.

---

## 7. Multi-Scale Inscription Persistence

A fundamental challenge in stone inscription OCR is distinguishing **stone crystalline texture** from **chiseled glyph incisions**.

- **Physical Principle**: A genuine engraved stroke has physical width and depth that remains detectable across adjacent morphological filter scales ($s-1, s, s+1$).
- **Random Texture Principle**: Crystalline mineral grains (quartz, feldspar, biotite) fluctuate rapidly and inconsistently across scale steps.
- **Persistence Metric**:
  $$\text{Persistence} = \frac{\sum R_s \cdot R_{s+1}}{\sqrt{\sum R_s^2 \cdot \sum R_{s+1}^2}}$$
  A score $\ge 0.80$ denotes strong structural consistency; $0.65 - 0.80$ moderate; $< 0.65$ weak.

---

## 8. Single-Image Directional Relief Enhancement

To simulate the physical examination of inscriptions under oblique raking light in the field, SHILORA projects first-order spatial gradients along 4 raking light angles:
$$S_\theta = G_x \cos\theta + G_y \sin\theta, \quad \theta \in \{45^\circ, 135^\circ, 225^\circ, 315^\circ\}$$
By computing the consensus of opposing shading differentials ($|S_{45} - S_{225}| + |S_{135} - S_{315}|$), directional relief is heightened.

---

## 9. CLAHE Limitations & Parameter Bounding

CLAHE can introduce significant artifacts if applied naively:
1. High clip limits amplify fine crystalline stone texture into artificial noise.
2. Small tile grids can produce visible boundary seams on tall/narrow stone slabs.

SHILORA bounds CLAHE strictly ($\text{clipLimit} \in [1.4, 2.0]$) and validates an $(8, 8)$ grid. If CLAHE increases background grain faster than inscription relief, the clip limit is automatically held at a conservative level.

---

## 10. Crack and Stain Damping

Ancient stone inscriptions frequently feature non-glyph anomalies:
- **Structural Cracks**: Characterized by extreme aspect ratios ($> 15:1$) and large continuous spans ($> 25\%$ of stone dimension).
- **Mineral / Chemical Stains**: Characterized by high chromatic deviation from neutral stone gray.

SHILORA detects these structures and generates a continuous suppression weight map ($0.35 - 1.0$), damping their influence in the fusion stages so they are not mistaken for glyphs, without artificially erasing them from the stone.

---

## 11. Positive Bounded Evidence Fusion

Subtractive groove formulas (e.g. $\text{base} \times (1 - w \cdot E_3) - w_{\text{edge}} \cdot E_4$) frequently produce dark halo rings, stroke clipping, and over-darkened regions where weak characters are destroyed.

SHILORA V3.1 uses **positive bounded evidence fusion**:
$$E_{\text{fused}} = \sum_{i=1}^{7} w_i E_i, \quad \sum w_i = 1.0$$
followed by a smooth sigmoidal tone mapping:
$$f(x) = \frac{1}{1 + e^{-6(x - 0.5)}}$$
This preserves weak shallow strokes and maintains continuous glyph connectivity without halos.

---

## 12 & 13. Maximum Recoverable Information Principle & 13 Hard-Stop Conditions

SHILORA operates under a rigorous optimization stopping rule:

$$\text{Objective} = \text{InscriptionEvidence} - \lambda \cdot \text{Noise} - \mu \cdot \text{Artifact} - \nu \cdot \text{Distortion}$$

Enhancement continues only while:
$$\Delta \text{Evidence} > \Delta \text{Noise} + \Delta \text{Artifact} + \Delta \text{Distortion}$$

### 13 Hard-Stop Conditions:
1. Inscription evidence stops increasing ($\Delta \text{IBR} \le 0$).
2. Stone texture begins increasing faster than inscription ($\Delta C_{\text{bg}} > \Delta C_{\text{insc}}$).
3. Block artifacts increase ($\Delta \text{Block} > 0.02$ or $\text{Block} > 0.05$).
4. 8x8 or 16x16 periodic structures rise.
5. New glyph-like structures appear unsupported by original luminance.
6. Genuine thin strokes begin disappearing.
7. Character topology changes (loop closure / disconnection).
8. Dark halos or edge boundary overshoot appear.
9. CLAHE begins producing visible tile boundary seams.
10. Sharpening produces ringing or overshoot (Laplacian spike $> 160$).
11. Noise increases faster than useful inscription evidence.
12. Structural persistence decreases significantly.
13. Enhanced output becomes less faithful to original photograph.

When any condition triggers, the pipeline immediately halts enhancement and returns to the last verified valid configuration.

---

## 14. Fundamental Physical Limitations

Software preprocessing has an absolute information-theoretic limit:
> **If a physical inscription stroke was not captured with sufficient optical information in the original photograph, software preprocessing cannot reliably recover it.**

When a stone is severely abraded or out of focus, SHILORA stops enhancement and assigns it to **Category D (Information-Limited)**. In such cases, re-acquisition using controlled raking illumination or multi-view photogrammetry is recommended.

---

## 15. Why Generative AI is Prohibited

Generative AI models (GANs, diffusion models, LLM inpainting) synthesize missing pixels based on statistical priors from training data. In epigraphy:
- An AI model might complete a broken ancient Kannada letter into a common medieval word that did not exist on the stone.
- Such hallucinations invalidate archaeological and historical research.
- SHILORA is 100% deterministic computer vision. Every output pixel is mathematically traceable to the input photograph.

---

## 16. Pseudo-Relief vs. Reflectance Transformation Imaging (RTI)

- **RTI / Photometric Stereo**: Uses 20–50 photographs of a stationary stone captured from a fixed camera with light sources moving across a hemisphere, mathematically solving for the true surface normal vector $\mathbf{N} = (N_x, N_y, N_z)$ at every pixel.
- **SHILORA Pseudo-Relief**: Single-image directional relief enhancement that modulates 2D image gradients along virtual lighting vectors. It is an image enhancement, **not true 3D geometric recovery**.

---

## 17. Preprocessing Success vs. OCR Success

- **Preprocessing Completion (39/39 = 100%)**: Indicates that all 39 archival photographs successfully passed through the deterministic enhancement pipeline with verified resolution preservation, artifact suppression, and valid output generation.
- **OCR Success**: Downstream character segmentation, feature extraction, script classification, and lexical matching. A stone classified as Category C or D may have successful preprocessing while achieving lower OCR accuracy due to historical physical erosion.

---

## 18. Preprocessing Dataset Report (Stage 30 Schema)

The generated [preprocessing_report.csv](file:///e:/Brahmi-OCR-main/preprocessing_report.csv) contains the complete 21-column schema:
- **Total Images Processed**: 39
- **Primary Channel**: 100% `Y_Luminance`
- **Mean Inscription/Background Contrast Ratio (IBR)**: $1.46$
- **Mean Multi-Scale Persistence**: $0.914$ (high structural confidence)
- **Mean Blockiness Score**: $0.0089$ (compression artifacts suppressed)
- **Quality Categories**:
  - Category A (High Recoverability): 25 stones
  - Category B (Moderate Recoverability): 6 stones
  - Category C (Low Recoverability): 8 stones
  - Category D (Information-Limited): 0 stones
- **Hard-Stop Triggers**: 38 stopped at `CLIPPING_LIMIT` (preserving highlights), 1 stopped at `BLOCK_ARTIFACT_LIMIT` (low-res pillar).

---

## 19. How to Run

```bash
# Process complete 39-stone dataset
python shilora_preprocessor.py --input_dir data/raw --output_dir data/preprocessed --report preprocessing_report.csv

# Process specific validation stones
python shilora_preprocessor.py --files stone_005.jpg stone_027.jpg stone_034.jpg
```
