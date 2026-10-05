import cv2
import numpy as np

def clean_image_noise(image_bgr, min_dot_area=None):
    """
    Robustly removes small dots and granite grain noise from an inscription image.
    Works seamlessly on binary, grayscale, or color stone images.
    Preserves fine character strokes while eliminating background texture.
    """
    if image_bgr is None:
        raise ValueError("Invalid image input for clean_image_noise")

    h, w = image_bgr.shape[:2]
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY) if len(image_bgr.shape) == 3 else image_bgr.copy()

    # Determine if already high-contrast black-and-white
    is_already_binary = (np.mean((gray == 0) | (gray == 255)) > 0.85)

    if is_already_binary:
        thresh = (gray < 128).astype(np.uint8) * 255
    else:
        # 1. Bilateral filter to smooth grain while keeping sharp stroke boundaries
        smoothed = cv2.bilateralFilter(gray, d=5, sigmaColor=40, sigmaSpace=40)
        # 2. Adaptive thresholding with resolution-scaled block size
        block_sz = int(max(h, w) * 0.03) | 1
        block_sz = max(13, min(block_sz, 45))
        thresh = cv2.adaptiveThreshold(
            smoothed, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, block_sz, 3
        )

    # Morphological closing to join micro-gaps in weathered strokes
    k_close = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, k_close)

    # Resolution-adaptive minimum dot threshold
    if min_dot_area is None:
        min_dot_area = max(20, int((h * w) * 0.00008))

    # Connected Components filtering with fast vectorized LUT
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(thresh, connectivity=8)

    valid_labels = [i for i in range(1, num_labels)
                    if stats[i, cv2.CC_STAT_AREA] >= min_dot_area
                    and stats[i, cv2.CC_STAT_WIDTH] < (0.95 * w)
                    and stats[i, cv2.CC_STAT_HEIGHT] < (0.95 * h)]

    lut = np.zeros(num_labels, dtype=np.uint8)
    if valid_labels:
        lut[valid_labels] = 255
    stroke_mask = lut[labels]

    clean_bgr = np.full((h, w, 3), 255, dtype=np.uint8)
    clean_bgr[stroke_mask == 255] = [0, 0, 0]

    return clean_bgr


def remove_background_noise(image_bgr, min_dot_area=None):
    """
    Advanced epigraphical background noise and texture remover:
    1. Illumination correction via background division (flattens sun/shadow gradients).
    2. CLAHE (Contrast Limited Adaptive Histogram Equalization) for faint grooves.
    3. Bilateral smoothing for granite crystallization.
    4. Adaptive local thresholding (not naive global Otsu).
    5. Structural proximity algorithm: preserves grammatical dots/accents (Visarga/Anusvara)
       near core characters while purging floating rock pitting in the background.
    """
    if image_bgr is None:
        raise ValueError("Invalid image input for remove_background_noise")

    h, w = image_bgr.shape[:2]
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY) if len(image_bgr.shape) == 3 else image_bgr.copy()

    # If image is already clean black on white, pass directly to clean_image_noise
    is_already_binary = (np.mean((gray == 0) | (gray == 255)) > 0.85)
    if is_already_binary:
        return clean_image_noise(image_bgr, min_dot_area=min_dot_area)

    # 1. Illumination Flattening (estimates lighting field via large Gaussian)
    bg_k = int(max(h, w) * 0.08) | 1
    bg_k = max(31, min(bg_k, 151))
    background = cv2.GaussianBlur(gray, (bg_k, bg_k), 0)
    flat_gray = np.clip((gray.astype(np.float32) / (background.astype(np.float32) + 1e-5)) * 200, 0, 255).astype(np.uint8)

    # 2. CLAHE enhancement
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    enhanced = clahe.apply(flat_gray)

    # 3. Bilateral filter
    smoothed = cv2.bilateralFilter(enhanced, d=7, sigmaColor=50, sigmaSpace=50)

    # 4. Adaptive thresholding
    block_sz = int(max(h, w) * 0.035) | 1
    block_sz = max(15, min(block_sz, 51))
    thresh = cv2.adaptiveThreshold(
        smoothed, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, block_sz, 4
    )

    # Morphological close to join slightly disjoint strokes
    k_close = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, k_close)

    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(thresh, connectivity=8)

    # Resolution-proportional thresholds
    if min_dot_area is None:
        min_dot_area = max(20, int((h * w) * 0.0001))
    core_min_area = max(100, int((h * w) * 0.0004))

    large_mask = np.zeros_like(thresh)
    small_labels = []

    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        bw   = stats[i, cv2.CC_STAT_WIDTH]
        bh   = stats[i, cv2.CC_STAT_HEIGHT]

        # Ignore perimeter frames
        if bw > 0.9 * w or bh > 0.9 * h:
            continue

        if area >= core_min_area or max(bw, bh) >= int(min(h, w) * 0.04):
            large_mask[labels == i] = 255
        else:
            small_labels.append((i, area))

    # Adaptive safe zone dilation proportional to character line spacing
    safe_radius = max(15, int(min(h, w) * 0.035)) | 1
    safe_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (safe_radius, safe_radius))
    safe_zone   = cv2.dilate(large_mask, safe_kernel)

    # Evaluate small dots: keep if within proximity safe zone of a character
    cleaned_mask = large_mask.copy()
    for i, area in small_labels:
        if area < min_dot_area:
            continue
        cx, cy = int(centroids[i][0]), int(centroids[i][1])
        cy = max(0, min(cy, safe_zone.shape[0] - 1))
        cx = max(0, min(cx, safe_zone.shape[1] - 1))
        if safe_zone[cy, cx] == 255:
            cleaned_mask[labels == i] = 255

    # Output clean black-on-white image
    cleaned_bgr = np.full((h, w, 3), 255, dtype=np.uint8)
    cleaned_bgr[cleaned_mask == 255] = [0, 0, 0]

    return cleaned_bgr


def merge_nested_boxes(boxes):
    """
    If a box is completely inside another box, discard the inner one.
    Uses area-descending pruning: smaller boxes are only checked against
    already-accepted larger parent boxes (runs in milliseconds).
    """
    if not boxes or len(boxes) <= 1:
        return boxes

    # Sort boxes by area descending: largest boxes first
    sorted_by_area = sorted(boxes, key=lambda b: b[2] * b[3], reverse=True)
    kept = []

    for box in sorted_by_area:
        x1, y1, w1, h1 = box
        is_nested = False
        for k_box in kept:
            x2, y2, w2, h2 = k_box
            # If current box is completely contained within an already-kept larger box
            if (x1 >= x2 and y1 >= y2 and (x1 + w1) <= (x2 + w2) and (y1 + h1) <= (y2 + h2)):
                is_nested = True
                break
        if not is_nested:
            kept.append(box)

    return kept


# Target aspect ratio: balanced for ancient inscriptions (0.85 - 1.05 supports both Brahmi and rounded Kannada/Devanagari)
TARGET_ASPECT_RATIO = 0.95  # width / height (near-square for rounded scripts)


def normalize_box_aspect_ratio(x, y, w, h, img_width, img_height,
                                target_ar=TARGET_ASPECT_RATIO,
                                min_natural_ar=0.65,
                                max_natural_ar=1.35,
                                max_expand_ratio=1.4):
    """
    Adjusts a bounding box so its width/height ratio approaches a balanced ratio.
    If the box already has a natural aspect ratio (min_natural_ar <= ar <= max_natural_ar),
    it is preserved with minimal padding to avoid distorting authentic glyphs.

    Expands the shorter dimension (keeping the box centred) rather than shrinking,
    so we never clip character pixels. Result is clamped to image boundaries.
    """
    current_ar = w / h if h > 0 else target_ar

    # If within reasonable natural character proportions, don't over-force
    if min_natural_ar <= current_ar <= max_natural_ar:
        return int(max(0, x)), int(max(0, y)), int(min(img_width - x, w)), int(min(img_height - y, h))

    if current_ar < target_ar:
        # Box is too tall — widen it gently
        new_w  = int(round(h * target_ar))
        delta  = new_w - w
        x      = x - delta // 2
        w      = new_w
    else:
        # Box is too wide — cap the height growth to avoid bleeding into adjacent lines
        new_h   = int(round(w / target_ar))
        max_h   = int(h * max_expand_ratio)
        new_h   = min(new_h, max_h)
        delta   = new_h - h
        y       = y - delta // 2
        h       = new_h

    # Clamp to image boundaries
    x = max(0, x)
    y = max(0, y)
    w = min(img_width  - x, w)
    h = min(img_height - y, h)

    return int(x), int(y), int(w), int(h)


def detect_characters(image_input, min_area=80, padding_ratio=0.12):
    """
    Detects characters with resolution-adaptive thresholding and robust contour filtering.
    Merging logic handles nested boxes and vertical subscript conjuncts.
    """
    if isinstance(image_input, str):
        img = cv2.imread(image_input)
        if img is None:
            raise ValueError(f"Could not read image at {image_input}")
    else:
        img = image_input

    if img is None:
        raise ValueError("Invalid image input")

    height, width = img.shape[:2]

    # Preprocessing
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img.copy()

    # Check if image is already binarized (e.g. output from official EpiSAM binarizer)
    if np.mean((gray <= 25) | (gray >= 230)) > 0.85:
        thresh = (gray < 128).astype(np.uint8) * 255
    else:
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        # Resolution-adaptive block size for adaptive thresholding
        # Scales smoothly from small 200px crops to 3000px high-res stone scans
        adaptive_block = int(max(height, width) * 0.025)
        if adaptive_block % 2 == 0:
            adaptive_block += 1
        adaptive_block = max(11, min(adaptive_block, 45))

        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, adaptive_block, 3
        )

    # Morphological Closing to connect delicate strokes
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    morph  = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=1)

    # Find Contours using RETR_LIST so we catch characters inside drawn frames
    contours, _ = cv2.findContours(morph, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    # Dynamic minimum area based on image resolution
    dynamic_min_area = max(min_area, int((height * width) * 0.00015))

    initial_boxes = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > dynamic_min_area:
            x, y, w, h = cv2.boundingRect(cnt)
            # Ignore full-image borders or giant panels (>85% of image)
            if w > 0.85 * width or h > 0.85 * height:
                continue
            # Ignore thin 1px slivers
            if w < 6 or h < 6:
                continue
            initial_boxes.append((x, y, w, h))

    # Filter Nested Boxes
    initial_boxes = merge_nested_boxes(initial_boxes)

    # Apply padding and balanced AR normalization
    final_boxes = []
    for (x, y, w, h) in initial_boxes:
        pad   = int(max(w, h) * padding_ratio)
        x_pad = max(0, x - pad)
        y_pad = max(0, y - pad)
        w_pad = min(width  - x_pad, w + 2 * pad)
        h_pad = min(height - y_pad, h + 2 * pad)

        x_pad, y_pad, w_pad, h_pad = normalize_box_aspect_ratio(
            x_pad, y_pad, w_pad, h_pad, width, height
        )
        final_boxes.append((x_pad, y_pad, w_pad, h_pad))

    return final_boxes, img


def sort_boxes(boxes):
    """
    Sorts bounding boxes from top-to-bottom, left-to-right using
    robust center-Y clustering for line grouping.

    WHY THE OLD APPROACH FAILED
    ───────────────────────────
    The old algorithm relied on top-Y sorting and a sequential greedy overlap.
    If a character from a lower line had a tall ascender (small top-Y), it was 
    sorted before the rest of its line, and its large bounding box would heavily 
    overlap with the line above it. This caused characters from below lines to 
    get "jumbled upon" and grouped into the above lines.

    NEW APPROACH: CENTER-Y CLUSTERING
    ─────────────────────────────────
    1. Sort all boxes by their center Y coordinate. Center Y is much more robust
       than top Y against tall ascenders or long descenders.
    2. Dynamically calculate the global median height to use as a threshold basis.
    3. Group boxes into lines: if a box's center Y is within `0.7 * median_h` of 
       the current line's median center Y, it belongs to that line.
    4. Sort left-to-right within each clustered line.
    """
    if not boxes:
        return []

    # 1. Calculate center Y for all boxes
    boxes_with_cy = [(b, b[1] + b[3] / 2.0) for b in boxes]
    
    # 2. Sort top-to-bottom by center Y
    boxes_with_cy.sort(key=lambda item: item[1])
    
    # 3. Calculate global median height to use as a dynamic threshold
    # This ensures the grouping adapts to the text size in the image
    median_h = np.median([b[3] for b in boxes])
    
    # Threshold for grouping: if center Y is within this distance of the line's median center Y
    # 0.7 * median_h provides a robust margin for grouping characters on the same line
    # while strictly preventing characters from different lines from mixing.
    threshold = max(10, median_h * 0.7)
    
    lines = []
    current_line = [boxes_with_cy[0][0]]
    current_cys = [boxes_with_cy[0][1]]
    
    for b, cy in boxes_with_cy[1:]:
        # Current line's representative center Y (median of its members)
        line_cy = np.median(current_cys)
        
        # If the box's center is close to the line's center, it belongs to this line
        if abs(cy - line_cy) <= threshold:
            current_line.append(b)
            current_cys.append(cy)
        else:
            # Start a new line
            lines.append(current_line)
            current_line = [b]
            current_cys = [cy]
            
    if current_line:
        lines.append(current_line)
        
    # 4. Within each line: sort left-to-right by x
    result = []
    for line in lines:
        line.sort(key=lambda b: b[0])
        result.extend(line)
        
    return result