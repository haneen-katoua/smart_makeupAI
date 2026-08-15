import os
import cv2
import json
import numpy as np
import mediapipe as mp
from scipy.interpolate import splprep, splev

def smooth_contour(pts, num_points=200):
    pts = np.array(pts)
    _, idx = np.unique(pts, axis=0, return_index=True)
    pts = pts[np.sort(idx)]
    if len(pts) < 4:
        return pts
    x, y = pts[:, 0], pts[:, 1]
    x = np.append(x, x[0])
    y = np.append(y, y[0])
    try:
        tck, u = splprep([x, y], s=0.5, per=True)
        u_new = np.linspace(0, 1, num_points)
        x_new, y_new = splev(u_new, tck)
        return np.int32(np.vstack((x_new, y_new)).T)
    except Exception:
        return pts

def apply_realistic_lipstick_layer(image, mask_blurred, lip_bgr, opacity=0.85):
    h, w, _ = image.shape
    img_lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB).astype(np.float32)
    color_layer = np.full((h, w, 3), lip_bgr, dtype=np.uint8)
    color_lab = cv2.cvtColor(color_layer, cv2.COLOR_BGR2LAB).astype(np.float32)
    l_orig, a_orig, b_orig = cv2.split(img_lab)
    l_color, a_color, b_color = cv2.split(color_lab)
    alpha = (mask_blurred.astype(np.float32) / 255.0) * opacity
    a_new = a_orig * (1.0 - alpha) + a_color * alpha
    b_new = b_orig * (1.0 - alpha) + b_color * alpha
    l_new = l_orig * (1.0 - alpha * 0.15) + l_color * (alpha * 0.15)
    merged_lab = cv2.merge([l_new, a_new, b_new])
    lipstick_bgr = cv2.cvtColor(np.clip(merged_lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR)
    alpha_3d = np.dstack([alpha] * 3)
    output = image.astype(np.float32) * (1.0 - alpha_3d) + lipstick_bgr.astype(np.float32) * alpha_3d
    return np.clip(output, 0, 255).astype(np.uint8)

def apply_pro_lip_liner(image, outer_pts, inner_pts, liner_bgr, face_scale, opacity=0.85):
    h, w, _ = image.shape
    liner_mask = np.zeros((h, w), dtype=np.uint8)
    thickness = max(2, int(face_scale * 0.014))
    cv2.polylines(liner_mask, [outer_pts], isClosed=True, color=255, thickness=thickness)
    blur_k = max(3, int(face_scale * 0.007) | 1)
    liner_mask_blurred = cv2.GaussianBlur(liner_mask, (blur_k, blur_k), 0)
    return apply_realistic_lipstick_layer(image, liner_mask_blurred, liner_bgr, opacity=opacity)

# def apply_realism_gloss(image, base_mask, landmarks, face_scale, intensity=0.30):
#     h, w, _ = image.shape
#     cx_bottom, cy_bottom = int(landmarks[17].x * w), int(landmarks[17].y * h)
#     rx = int(face_scale * 0.040)
#     ry = int(face_scale * 0.018)
#     gloss_map = np.zeros((h, w), dtype=np.float32)
#     cv2.ellipse(gloss_map, (cx_bottom, cy_bottom), (rx, ry), 0, 0, 360, 255, -1)
#     blur_k = max(21, int(face_scale * 0.06) | 1)
#     gloss_map = cv2.GaussianBlur(gloss_map, (blur_k, blur_k), 0)
#     mask_f = base_mask.astype(np.float32) / 255.0
#     gloss_map = (gloss_map / 255.0) * mask_f
#     img_f = image.astype(np.float32)
#     highlight = img_f + (255.0 - img_f) * (gloss_map[:, :, np.newaxis] * intensity)
#     return np.clip(highlight, 0, 255).astype(np.uint8)

def render_lips_engine(image, landmarks, shape_category, lip_bgr, face_scale, opacity=0.82, liner_info=None, is_glossy=False):
    h, w, _ = image.shape
    mask = np.zeros((h, w), dtype=np.uint8)
    LIPS_TOP_OUTER = [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291]
    LIPS_BOTTOM_OUTER = [291, 375, 321, 405, 314, 17, 84, 181, 91, 146, 61]
    LIPS_INNER = [78, 191, 80, 81, 82, 13, 312, 311, 310, 415, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95]
    base_offset = face_scale * 0.035
    is_overline_full = shape_category in ["Thin", "Overline Full", "شفاه رقيقة"]
    is_upper_overline = shape_category in ["Upper Thin", "Upper Overline", "شفة علوية رقيقة", "شفة علوية أرق نسبياً"]
    is_lower_overline = shape_category in ["Lower Thin", "Lower Overline", "شفة سفلى رقيقة", "شفة سفلى أرق نسبياً"]
    is_inline_minimizing = shape_category in ["Very Large", "Inline", "Inline (Minimizing)", "شفاه كبيرة جداً"]
    
    pts_top = []
    n_top = len(LIPS_TOP_OUTER)
    for i, idx in enumerate(LIPS_TOP_OUTER):
        x, y = landmarks[idx].x * w, landmarks[idx].y * h
        if idx not in [61, 291]:
            factor = np.sin((i / (n_top - 1)) * np.pi) ** 1.35
            if is_overline_full or is_upper_overline:
                y -= base_offset * 1.10 * factor
            elif is_inline_minimizing:
                y += base_offset * 0.50 * factor
        pts_top.append([int(x), int(y)])
        
    pts_bottom = []
    n_bottom = len(LIPS_BOTTOM_OUTER)
    for i, idx in enumerate(LIPS_BOTTOM_OUTER):
        x, y = landmarks[idx].x * w, landmarks[idx].y * h
        if idx not in [61, 291]:
            factor = np.sin((i / (n_bottom - 1)) * np.pi) ** 1.35
            if is_overline_full or is_lower_overline:
                y += base_offset * 1.10 * factor
            elif is_inline_minimizing:
                y -= base_offset * 0.50 * factor
        pts_bottom.append([int(x), int(y)])
        
    pts_outer_full = pts_top + pts_bottom[1:-1]
    pts_inner_full = [(int(landmarks[idx].x * w), int(landmarks[idx].y * h)) for idx in LIPS_INNER]
    smooth_outer = smooth_contour(pts_outer_full, num_points=200)
    smooth_inner = smooth_contour(pts_inner_full, num_points=120)
    
    cv2.fillPoly(mask, [smooth_outer], 255)
    cv2.fillPoly(mask, [smooth_inner], 0)
    blur_k = max(3, int(face_scale * 0.0070) | 1)
    mask_blurred = cv2.GaussianBlur(mask, (blur_k, blur_k), 0)
    
    rendered_img = apply_realistic_lipstick_layer(image, mask_blurred, lip_bgr, opacity=opacity)
    
    if liner_info:
        liner_rgb = liner_info.get("rgb", [160, 60, 60])
        liner_bgr = (liner_rgb[2], liner_rgb[1], liner_rgb[0])
        rendered_img = apply_pro_lip_liner(
            image=rendered_img, outer_pts=smooth_outer, inner_pts=smooth_inner, liner_bgr=liner_bgr, face_scale=face_scale, opacity=0.85
        )
        
    # if is_glossy or opacity > 0.75:
      #  rendered_img = apply_realism_gloss(rendered_img, mask, landmarks, face_scale, intensity=0.32)
        
    return rendered_img

def apply_recommended_lip_makeup(image, landmarks, face_scale, recommendation_json, shade_index=None):
    if "expert_recommendations" in recommendation_json:
        lips_data = recommendation_json["expert_recommendations"].get("lips", {})
    elif "lips" in recommendation_json:
        lips_data = recommendation_json["lips"]
    else:
        lips_data = recommendation_json

    shape_obj = lips_data.get("shape", {})
    shape_category = shape_obj.get("category", "Full & Balanced") if isinstance(shape_obj, dict) else str(shape_obj)

    occasion_obj = lips_data.get("occasion", {})
    if isinstance(occasion_obj, dict):
        json_opacity = occasion_obj.get("opacity", None)
        occasion_type = str(occasion_obj.get("occasion", "")).lower()
    else:
        json_opacity = None
        occasion_type = str(occasion_obj).lower()

    if json_opacity is not None:
        opacity = float(json_opacity) / 100.0 if float(json_opacity) > 1.0 else float(json_opacity)
    else:
        opacity = 0.82

    color_obj = lips_data.get("color", {}) if isinstance(lips_data.get("color"), dict) else {}
    shades = color_obj.get("lipstick_shades", [])
    liners = color_obj.get("lip_liners", [])

    if shade_index is None:
        if occasion_type in ["wedding", "party", "night_out", "evening"]:
            shade_index = 1 if len(shades) > 1 else 0
        elif occasion_type in ["graduation", "formal", "interview", "photo"]:
            shade_index = 2 if len(shades) > 2 else 0
        else:
            shade_index = 0

    if shades and shade_index < len(shades):
        rgb = shades[shade_index].get("rgb", [255, 127, 80])
    elif shades:
        rgb = shades[0].get("rgb", [255, 127, 80])
    else:
        rgb = [255, 127, 80]

    if liners:
        liner_idx = min(shade_index, len(liners) - 1)
        liner_info = liners[liner_idx]
    else:
        liner_info = None

    finish_type = str(color_obj.get("texture", color_obj.get("finish", "Satin"))).lower()
    is_glossy = "gloss" in finish_type or "لامع" in finish_type or "سائل" in finish_type

    lip_bgr = (rgb[2], rgb[1], rgb[0])

    return render_lips_engine(
        image=image,
        landmarks=landmarks,
        shape_category=shape_category,
        lip_bgr=lip_bgr,
        face_scale=face_scale,
        opacity=opacity,
        liner_info=liner_info,
        is_glossy=is_glossy
    )

if __name__ == "__main__":
    image_path = "test2.jpg"
    json_path = "makeup_analysis.json"
    if os.path.exists(image_path) and os.path.exists(json_path):
        img = cv2.imread(image_path)
        h, w, _ = img.shape
        with open(json_path, 'r', encoding='utf-8') as f:
            input_json = json.load(f)
        mp_face_mesh = mp.solutions.face_mesh
        with mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1) as face_mesh:
            results = face_mesh.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            if results.multi_face_landmarks:
                face_landmarks = results.multi_face_landmarks[0].landmark
                pt1 = np.array([face_landmarks[234].x * w, face_landmarks[234].y * h])
                pt2 = np.array([face_landmarks[454].x * w, face_landmarks[454].y * h])
                face_scale = np.linalg.norm(pt1 - pt2)
                output = apply_recommended_lip_makeup(
                    image=img, landmarks=face_landmarks, face_scale=face_scale, recommendation_json=input_json
                )
                cv2.imwrite("output_lips.jpg", output)