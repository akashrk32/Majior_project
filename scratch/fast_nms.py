def mask_nms_ios(masks, scores, bboxes, ios_threshold=0.75):
    """
    Ultra-fast NMS using bounding-box pre-filtering and localized intersection.
    Reduces O(N^2 * H * W) pixel operations from billions down to microseconds.
    """
    if not masks or len(masks) == 0:
        return []
    
    order = np.argsort(scores)[::-1]
    keep = []
    suppressed = np.zeros(len(masks), dtype=bool)

    # Pre-calculate areas
    areas = [np.sum(m > 0) for m in masks]

    for i in order:
        if suppressed[i]:
            continue
        keep.append(i)
        area_i = areas[i]
        if area_i == 0:
            continue
            
        bx1_i, by1_i, bx2_i, by2_i = bboxes[i]
        mask_i = masks[i]

        for j in order:
            if i == j or suppressed[j]:
                continue
            
            bx1_j, by1_j, bx2_j, by2_j = bboxes[j]
            
            # Fast Bounding Box check: do they overlap?
            ix1 = max(bx1_i, bx1_j)
            iy1 = max(by1_i, by1_j)
            ix2 = min(bx2_i, bx2_j)
            iy2 = min(by2_i, by2_j)
            
            if ix1 >= ix2 or iy1 >= iy2:
                # No bounding box overlap -> zero mask intersection
                continue
            
            area_j = areas[j]
            smaller_area = min(area_i, area_j)
            if smaller_area == 0:
                continue

            # Compute intersection ONLY within the overlapping bounding box window
            sub_i = mask_i[iy1:iy2, ix1:ix2]
            sub_j = masks[j][iy1:iy2, ix1:ix2]
            intersection = np.count_nonzero((sub_i > 0) & (sub_j > 0))
            
            ios = intersection / (smaller_area + 1e-6)
            if ios > ios_threshold:
                suppressed[j] = True

    return keep
