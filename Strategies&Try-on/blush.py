# -*- coding: utf-8 -*-

import json
import cv2
import numpy as np
import mediapipe as mp
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from face_makeup_rules import FaceContourEngine, get_blush_palette_shades

RIGHT_EYE_LANDMARKS = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
LEFT_EYE_LANDMARKS = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
RIGHT_CHEEK, LEFT_CHEEK = 117, 346
RIGHT_TEMPLE, LEFT_TEMPLE = 162, 389
RIGHT_UNDER_EYE, LEFT_UNDER_EYE = 111, 340
NOSE_BRIDGE, NOSE_TIP = 6, 1

def parse_color(hex_str):
    hex_s = hex_str.lstrip('#')
    rgb = tuple(int(hex_s[i:i + 2], 16) for i in (0, 2, 4))
    return (rgb[2], rgb[1], rgb[0])

def create_eye_exclusion_mask(shape, landmarks):
    h, w = shape[:2]
    eye_mask = np.ones((h, w), dtype=np.float32)
    r_eye_pts = np.array([[int(landmarks[idx].x * w), int(landmarks[idx].y * h)] for idx in RIGHT_EYE_LANDMARKS], dtype=np.int32)
    l_eye_pts = np.array([[int(landmarks[idx].x * w), int(landmarks[idx].y * h)] for idx in LEFT_EYE_LANDMARKS], dtype=np.int32)
    cv2.fillPoly(eye_mask, [r_eye_pts], 0.0)
    cv2.fillPoly(eye_mask, [l_eye_pts], 0.0)
    return cv2.GaussianBlur(eye_mask, (7, 7), 0)

def generate_blush_mask(shape, center_pt, axes, angle, blur_k):
    h, w = shape[:2]
    raw_mask = np.zeros((h, w), dtype=np.float32)
    cv2.ellipse(raw_mask, center=(int(center_pt[0]), int(center_pt[1])),
                axes=(int(axes[0]), int(axes[1])), angle=angle,
                startAngle=0, endAngle=360, color=1.0, thickness=-1)
    ksize = int(blur_k) | 1
    return cv2.GaussianBlur(raw_mask, (ksize, ksize), 0)

def apply_blush_blend_balanced(base_img, mask, blush_bgr, opacity=0.52):
    img_float = base_img.astype(np.float32) / 255.0
    color_patch = np.zeros_like(img_float)
    color_patch[:] = [blush_bgr[0] / 255.0, blush_bgr[1] / 255.0, blush_bgr[2] / 255.0]

    soft_light = np.where(
        color_patch <= 0.5,
        2 * img_float * color_patch + (img_float ** 2) * (1 - 2 * color_patch),
        2 * img_float * (1 - color_patch) + np.sqrt(np.maximum(img_float, 1e-5)) * (2 * color_patch - 1)
    )

    blended_color = 0.70 * soft_light + 0.30 * (img_float * 0.2 + color_patch * 0.8)
    final_weight = (mask * opacity)[:, :, np.newaxis]
    result = (1.0 - final_weight) * img_float + final_weight * blended_color
    return np.clip(result * 255.0, 0, 255).astype(np.uint8)

def render_blush_engine_perfect(image, landmarks, face_scale, strategy="Lifted_Temple", override_bgr=None, opacity=0.52):
    h, w, _ = image.shape
    output_img = image.copy()
    bgr_color = override_bgr if override_bgr is not None else parse_color("#C86D7C")

    r_cheek = np.array([landmarks[RIGHT_CHEEK].x * w, landmarks[RIGHT_CHEEK].y * h])
    l_cheek = np.array([landmarks[LEFT_CHEEK].x * w, landmarks[LEFT_CHEEK].y * h])
    r_temple = np.array([landmarks[RIGHT_TEMPLE].x * w, landmarks[RIGHT_TEMPLE].y * h])
    l_temple = np.array([landmarks[LEFT_TEMPLE].x * w, landmarks[LEFT_TEMPLE].y * h])
    r_under = np.array([landmarks[RIGHT_UNDER_EYE].x * w, landmarks[RIGHT_UNDER_EYE].y * h])
    l_under = np.array([landmarks[LEFT_UNDER_EYE].x * w, landmarks[LEFT_UNDER_EYE].y * h])
    nose_bridge = np.array([landmarks[NOSE_BRIDGE].x * w, landmarks[NOSE_BRIDGE].y * h])
    nose_tip = np.array([landmarks[NOSE_TIP].x * w, landmarks[NOSE_TIP].y * h])

    full_mask = np.zeros((h, w), dtype=np.float32)

    if strategy == "Lifted_Temple":
        blur_k = max(17, int(face_scale * 0.22))
        rc = r_cheek - np.array([face_scale * 0.03, face_scale * 0.04])
        lc = l_cheek + np.array([face_scale * 0.03, -face_scale * 0.04])
        m_r = generate_blush_mask((h, w), rc, (face_scale * 0.16, face_scale * 0.07), angle=-35, blur_k=blur_k)
        m_l = generate_blush_mask((h, w), lc, (face_scale * 0.16, face_scale * 0.07), angle=35, blur_k=blur_k)
        full_mask = np.maximum(m_r, m_l)

    elif strategy == "Apples_Classic":
        blur_k = max(21, int(face_scale * 0.28))
        rc = r_cheek + np.array([0, face_scale * 0.03])
        lc = l_cheek + np.array([0, face_scale * 0.03])
        m_r = generate_blush_mask((h, w), rc, (face_scale * 0.12, face_scale * 0.11), angle=0, blur_k=blur_k)
        m_l = generate_blush_mask((h, w), lc, (face_scale * 0.12, face_scale * 0.11), angle=0, blur_k=blur_k)
        full_mask = np.maximum(m_r, m_l)

    elif strategy == "Draping_C_Shape":
        blur_k = max(15, int(face_scale * 0.20))
        m_r1 = generate_blush_mask((h, w), r_temple, (face_scale * 0.11, face_scale * 0.05), angle=-45, blur_k=blur_k)
        m_r2 = generate_blush_mask((h, w), r_cheek, (face_scale * 0.13, face_scale * 0.06), angle=-20, blur_k=blur_k)
        m_l1 = generate_blush_mask((h, w), l_temple, (face_scale * 0.11, face_scale * 0.05), angle=45, blur_k=blur_k)
        m_l2 = generate_blush_mask((h, w), l_cheek, (face_scale * 0.13, face_scale * 0.06), angle=20, blur_k=blur_k)
        full_mask = np.maximum.reduce([m_r1, m_r2, m_l1, m_l2])

    elif strategy == "Igari_UnderEye":
        blur_k = max(13, int(face_scale * 0.18))
        m_r = generate_blush_mask((h, w), r_under + [0, face_scale*0.01], (face_scale * 0.13, face_scale * 0.05), angle=0, blur_k=blur_k)
        m_l = generate_blush_mask((h, w), l_under + [0, face_scale*0.01], (face_scale * 0.13, face_scale * 0.05), angle=0, blur_k=blur_k)
        m_nose = generate_blush_mask((h, w), nose_tip, (face_scale * 0.05, face_scale * 0.05), angle=0, blur_k=blur_k)
        full_mask = np.maximum.reduce([m_r, m_l, m_nose])

    elif strategy == "Douyin_VLift":
        blur_k = max(11, int(face_scale * 0.16))
        rc = r_cheek + np.array([face_scale * 0.03, -face_scale * 0.04])
        lc = l_cheek + np.array([-face_scale * 0.03, -face_scale * 0.04])
        m_r = generate_blush_mask((h, w), rc, (face_scale * 0.15, face_scale * 0.04), angle=-50, blur_k=blur_k)
        m_l = generate_blush_mask((h, w), lc, (face_scale * 0.15, face_scale * 0.04), angle=50, blur_k=blur_k)
        full_mask = np.maximum(m_r, m_l)

    elif strategy == "Sunkissed_W_Shape":
        blur_k = max(21, int(face_scale * 0.26))
        m_r = generate_blush_mask((h, w), r_cheek, (face_scale * 0.14, face_scale * 0.07), angle=-10, blur_k=blur_k)
        m_l = generate_blush_mask((h, w), l_cheek, (face_scale * 0.14, face_scale * 0.07), angle=10, blur_k=blur_k)
        m_b = generate_blush_mask((h, w), nose_bridge, (face_scale * 0.12, face_scale * 0.06), angle=0, blur_k=blur_k)
        full_mask = np.maximum.reduce([m_r, m_l, m_b])

    elif strategy == "Contour_Sculpt_Hybrid":
        blur_k = max(19, int(face_scale * 0.24))
        rc = r_cheek + np.array([0, face_scale * 0.06])
        lc = l_cheek + np.array([0, face_scale * 0.06])
        m_r = generate_blush_mask((h, w), rc, (face_scale * 0.15, face_scale * 0.05), angle=-15, blur_k=blur_k)
        m_l = generate_blush_mask((h, w), lc, (face_scale * 0.15, face_scale * 0.05), angle=15, blur_k=blur_k)
        full_mask = np.maximum(m_r, m_l)

    elif strategy == "Nose_Bridge_Only":
        blur_k = max(11, int(face_scale * 0.14))
        m_b = generate_blush_mask((h, w), nose_bridge + [0, face_scale * 0.02], (face_scale * 0.08, face_scale * 0.04), angle=0, blur_k=blur_k)
        m_t = generate_blush_mask((h, w), nose_tip, (face_scale * 0.04, face_scale * 0.04), angle=0, blur_k=blur_k)
        full_mask = np.maximum(m_b, m_t)

    elif strategy == "Halo_Center_Focus":
        blur_k = max(25, int(face_scale * 0.30))
        m_r = generate_blush_mask((h, w), r_cheek, (face_scale * 0.09, face_scale * 0.09), angle=0, blur_k=blur_k)
        m_l = generate_blush_mask((h, w), l_cheek, (face_scale * 0.09, face_scale * 0.09), angle=0, blur_k=blur_k)
        full_mask = np.maximum(m_r, m_l)

    else: 
        blur_k = max(17, int(face_scale * 0.22))
        rc = r_cheek - np.array([face_scale * 0.03, face_scale * 0.04])
        lc = l_cheek + np.array([face_scale * 0.03, -face_scale * 0.04])
        m_r = generate_blush_mask((h, w), rc, (face_scale * 0.16, face_scale * 0.07), angle=-35, blur_k=blur_k)
        m_l = generate_blush_mask((h, w), lc, (face_scale * 0.16, face_scale * 0.07), angle=35, blur_k=blur_k)
        full_mask = np.maximum(m_r, m_l)

    eye_exclusion = create_eye_exclusion_mask((h, w), landmarks)
    clean_mask = full_mask * eye_exclusion
    return apply_blush_blend_balanced(output_img, clean_mask, bgr_color, opacity=opacity)

def map_shape_to_strategy(face_shape, fullness="Full"):
    """دالة ربط شكل الوجه بالاستراتيجية المناسبة"""
    shape_map = {
        ("Round", "Full"): "Contour_Sculpt_Hybrid",
        ("Round", "Thin"): "Lifted_Temple",
        ("Oval", "Full"): "Douyin_VLift",
        ("Oval", "Thin"): "Halo_Center_Focus",
        ("Square", "Full"): "Apples_Classic",
        ("Square", "Thin"): "Lifted_Temple",
        ("Long", "Full"): "Sunkissed_W_Shape",
        ("Long", "Thin"): "Igari_UnderEye",
        ("Heart", "Full"): "Draping_C_Shape",
        ("Heart", "Thin"): "Apples_Classic"
    }
    return shape_map.get((face_shape, fullness), "Lifted_Temple")

def parse_strategy_from_json(face_data, expert_out):
    blush_info = expert_out.get('face', {}).get('blush', {}) or expert_out.get('blush', {})
    blush_placement = blush_info.get('placement', '')
    
    if any(k in blush_placement for k in ["تحت العين", "Igari"]):
        return "Igari_UnderEye"
    elif any(k in blush_placement for k in ["تفاحتي الخد", "مركز الخد", "حجم حيوي"]):
        return "Halo_Center_Focus" if "نحيفة" in blush_placement else "Apples_Classic"
    elif any(k in blush_placement for k in ["مسحوب للأعلى", "الأذن", "سحبة"]):
        return "Lifted_Temple"
    elif any(k in blush_placement for k in ["أنف", "جسر الأنف", "شمس"]):
        return "Sunkissed_W_Shape"

    face_analysis = face_data.get('face_analysis', {})
    shape = face_analysis.get('shape') or face_data.get('face_shape', {}).get('shape', 'Oval')
    ratios = face_analysis.get('face_shape', {}).get('ratios', {})
    
    length_to_width = ratios.get('face_length_to_width', 1.3)
    
    fullness = "Thin" if length_to_width > 1.35 else "Full"
    
    return map_shape_to_strategy(shape, fullness)

def parse_strategy_from_json(face_data, expert_out):
    # حماية الدخل الأساسي من القيمة None
    face_data = face_data or {}
    expert_out = expert_out or {}

    # جلب معلومات البلاشر بأمان
    face_section = expert_out.get('face') or {}
    blush_info = face_section.get('blush') or expert_out.get('blush') or {}
    
    blush_placement = blush_info.get('placement', '') or ''
    
    if any(k in blush_placement for k in ["تحت العين", "Igari"]):
        return "Igari_UnderEye"
    elif any(k in blush_placement for k in ["تفاحتي الخد", "مركز الخد", "حجم حيوي"]):
        return "Halo_Center_Focus" if "نحيفة" in blush_placement else "Apples_Classic"
    elif any(k in blush_placement for k in ["مسحوب للأعلى", "الأذن", "سحبة"]):
        return "Lifted_Temple"
    elif any(k in blush_placement for k in ["أنف", "جسر الأنف", "شمس"]):
        return "Sunkissed_W_Shape"

    # جلب تحليلات الوجه بأمان
    face_analysis = face_data.get('face_analysis') or {}
    shape_section = face_data.get('face_shape') or {}
    
    shape = face_analysis.get('shape') or shape_section.get('shape', 'Oval')
    
    ratios = (face_analysis.get('face_shape') or {}).get('ratios') or {}
    length_to_width = ratios.get('face_length_to_width', 1.3)
    
    fullness = "Thin" if length_to_width > 1.35 else "Full"
    
    return map_shape_to_strategy(shape, fullness)


def process_pipeline(json_path, image_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        face_data = json.load(f) or {}

    engine = FaceContourEngine()
    results = engine.analyze_face(face_data) or {}

    expert_out = face_data.get('expert_output') or results.get('expert_output') or {}
    face_expert = expert_out.get('face') or {}
    blush_info = face_expert.get('blush') or {}
    
    opacity_pct = blush_info.get('opacity', 52)

    rec_hex = None
    color_details = blush_info.get('color_details') or {}
    if color_details:
        primary_color = color_details.get('primary') or {}
        rec_hex = primary_color.get('hex')

    if not rec_hex:
        base_color_ar = 'مرجاني'
        res_color = results.get('color') or {}
        if isinstance(res_color, dict):
            base_color_ar = res_color.get('base_color', 'مرجاني')
        
        hex_color_info = get_blush_palette_shades(base_color_ar) or {}
        primary_hex_info = hex_color_info.get('primary') or {}
        rec_hex = primary_hex_info.get('hex', '#F2A68D') 

    strategy = parse_strategy_from_json(face_data, expert_out)

    print(f" الاستراتيجية المحددة تلقائياً: {strategy}")
    print(f" اللون المقترح (HEX): {rec_hex}")
    print(f" الشفافية: {opacity_pct}%")

    img = cv2.imread(image_path)
    if img is None:
        print(f" تعذر تحميل الصورة: {image_path}")
        return

    h, w, _ = img.shape
    mp_face_mesh = mp.solutions.face_mesh

    with mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, refine_landmarks=True) as face_mesh:
        res = face_mesh.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        if res.multi_face_landmarks:
            landmarks = res.multi_face_landmarks[0].landmark
            pt1 = np.array([landmarks[234].x * w, landmarks[234].y * h])
            pt2 = np.array([landmarks[454].x * w, landmarks[454].y * h])
            scale = np.linalg.norm(pt1 - pt2)

            rendered_img = render_blush_engine_perfect(
                image=img,
                landmarks=landmarks,
                face_scale=scale,
                strategy=strategy,
                override_bgr=parse_color(rec_hex),
                opacity=opacity_pct / 100.0
            )

            cv2.imwrite("final_output.png", rendered_img)
            print(" تم الحفظ بنجاح باسم final_output.png")
            
            cv2.imshow("Result", rendered_img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        else:
            print(" لم يتم الكشف عن وجه.")

if __name__ == "__main__":
    process_pipeline("makeup_analysis.json", "test3.jpg")