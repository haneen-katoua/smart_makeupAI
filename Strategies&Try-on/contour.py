# -*- coding: utf-8 -*-

import collections
import collections.abc
import json
import os
import cv2
import numpy as np
import mediapipe as mp


if not hasattr(collections, "Mapping"):
    collections.Mapping = collections.abc.Mapping

REAL_CONTOUR_SWATCHES = {
    "Cool-Amber (Fair)":      "#8C7B70",
    "Neutral-Taupe (Light)":  "#6E5D53",
    "Warm-Caramel (Medium)":  "#7A5230",
    "Deep-Espresso (Dark)":   "#4A3B32",
    "Soft-Hazelnut (Olive)":  "#5E4B3C"
}

def parse_color(hex_str, default_bgr=(50, 60, 80)):
    if isinstance(hex_str, str) and hex_str.startswith("#"):
        try:
            hex_clean = hex_str.lstrip('#')
            rgb = tuple(int(hex_clean[i:i + 2], 16) for i in (0, 2, 4))
            return (rgb[2], rgb[1], rgb[0])
        except Exception:
            return default_bgr
    return default_bgr

def calculate_robust_face_scale(landmarks, w, h):
    pt_l = np.array([landmarks[33].x * w, landmarks[33].y * h])
    pt_r = np.array([landmarks[263].x * w, landmarks[263].y * h])
    eye_dist = np.linalg.norm(pt_l - pt_r)
    return eye_dist * 2.25

def draw_line_path_mask(shape, line_pts, stroke_thick, blur_k, weight=1.0):
    h, w = shape[:2]
    if len(line_pts) < 2:
        return np.zeros((h, w), dtype=np.float32)
    
    pts = np.array(line_pts, np.int32).reshape((-1, 1, 2))
    temp_mask = np.zeros((h, w), dtype=np.uint8)
    cv2.polylines(temp_mask, [pts], isClosed=False, color=255, thickness=stroke_thick, lineType=cv2.LINE_AA)
    
    k1 = int(max(blur_k * 0.35, 9)) | 1
    k2 = int(max(blur_k * 0.85, 25)) | 1
    k3 = int(max(blur_k * 1.6, 51)) | 1
    
    f_mask = temp_mask.astype(np.float32) / 255.0
    soft1 = cv2.GaussianBlur(f_mask, (k1, k1), 0)
    soft2 = cv2.GaussianBlur(f_mask, (k2, k2), 0)
    soft3 = cv2.GaussianBlur(f_mask, (k3, k3), 0)
    
    final_mask = (soft1 * 0.25 + soft2 * 0.45 + soft3 * 0.30) * weight
    return np.clip(final_mask, 0, 1.0)

def apply_realistic_contour(base_img, mask, color_bgr, opacity=0.55):
    base_f = base_img.astype(np.float32) / 255.0
    color_target = np.array(color_bgr, dtype=np.float32) / 255.0
    color_target = color_target.reshape((1, 1, 3))
    
    multiply_layer = base_f * color_target
    alpha = np.expand_dims(np.clip(mask * opacity, 0, 1.0), axis=-1)
    
    blended = base_f * (1.0 - alpha) + multiply_layer * alpha
    return np.clip(blended * 255.0, 0, 255).astype(np.uint8)

def generate_contour_mask_realistic(image, landmarks, face_scale, shape_type="Oval", fullness="Full", sculpt_json=None, nose_json=None, context_json=None, full_json=None):
    h, w, _ = image.shape
    sculpt_placement = ""
    if isinstance(sculpt_json, dict):
        sculpt_placement = str(sculpt_json.get("placement", "")).strip()

    def get_pt(idx):
        return (int(landmarks[idx].x * w), int(landmarks[idx].y * h))

    forehead_offset = int(face_scale * 0.08)
    
    def get_forehead_pt(idx):
        pt = get_pt(idx)
        return (pt[0], max(0, pt[1] - forehead_offset))

    cheek_thick = int(face_scale * 0.085)
    jaw_thick   = int(face_scale * 0.065)
    hair_thick  = int(face_scale * 0.055)
    nose_thick  = int(face_scale * 0.018)

    blur_cheek = int(face_scale * 0.32) | 1
    blur_jaw   = int(face_scale * 0.26) | 1
    blur_hair  = int(face_scale * 0.30) | 1
    blur_nose  = int(face_scale * 0.12) | 1

    BOOST_CHEEK_JAW = 1.20

    line_n_l = [get_pt(193), get_pt(122)]
    line_n_r = [get_pt(417), get_pt(351)]
    m_nl = draw_line_path_mask((h, w), line_n_l, nose_thick, blur_nose)
    m_nr = draw_line_path_mask((h, w), line_n_r, nose_thick, blur_nose)

    shape_type = str(shape_type).strip().title()
    fullness = str(fullness).strip().title()

    if shape_type == "Oval":
        if fullness == "Full":
            line_cheek_l = [get_pt(116), get_pt(227), get_pt(127)]
            line_cheek_r = [get_pt(345), get_pt(447), get_pt(356)]
            m_cl = draw_line_path_mask((h, w), line_cheek_l, cheek_thick, blur_cheek, weight=1.0)
            m_cr = draw_line_path_mask((h, w), line_cheek_r, cheek_thick, blur_cheek, weight=1.0)
            contour_mask = np.maximum.reduce([m_nl, m_nr, m_cl, m_cr])
        else:
            line_cheek_l = [get_pt(227), get_pt(187), get_pt(216)]
            line_cheek_r = [get_pt(447), get_pt(411), get_pt(436)]
            m_cl = draw_line_path_mask((h, w), line_cheek_l, int(cheek_thick * 0.75), int(blur_cheek * 1.4) | 1, weight=0.7)
            m_cr = draw_line_path_mask((h, w), line_cheek_r, int(cheek_thick * 0.75), int(blur_cheek * 1.4) | 1, weight=0.7)
            contour_mask = np.maximum.reduce([m_nl, m_nr, m_cl, m_cr])

    elif shape_type == "Round":
        if fullness == "Full":
            line_cheek_l = [get_pt(227), get_pt(216), get_pt(186)]
            line_cheek_r = [get_pt(447), get_pt(436), get_pt(410)]
            line_jaw_l   = [get_pt(172), get_pt(136), get_pt(150)]
            line_jaw_r   = [get_pt(397), get_pt(365), get_pt(379)]
            m_cl = draw_line_path_mask((h, w), line_cheek_l, int(cheek_thick * 1.15), blur_cheek, weight=BOOST_CHEEK_JAW)
            m_cr = draw_line_path_mask((h, w), line_cheek_r, int(cheek_thick * 1.15), blur_cheek, weight=BOOST_CHEEK_JAW)
            m_jl = draw_line_path_mask((h, w), line_jaw_l, jaw_thick, blur_jaw, weight=BOOST_CHEEK_JAW)
            m_jr = draw_line_path_mask((h, w), line_jaw_r, jaw_thick, blur_jaw, weight=BOOST_CHEEK_JAW)
            contour_mask = np.maximum.reduce([m_nl, m_nr, m_cl, m_cr, m_jl, m_jr])
        else:
            line_cheek_l = [get_pt(227), get_pt(216)]
            line_cheek_r = [get_pt(447), get_pt(436)]
            m_cl = draw_line_path_mask((h, w), line_cheek_l, cheek_thick, blur_cheek, weight=0.9)
            m_cr = draw_line_path_mask((h, w), line_cheek_r, cheek_thick, blur_cheek, weight=0.9)
            contour_mask = np.maximum.reduce([m_nl, m_nr, m_cl, m_cr])

    elif shape_type == "Square":
        line_jaw_l = [get_pt(172), get_pt(136), get_pt(150)]
        line_jaw_r = [get_pt(397), get_pt(365), get_pt(379)]
        line_forehead_l = [get_pt(103), get_forehead_pt(67), get_forehead_pt(109)]
        line_forehead_r = [get_pt(332), get_forehead_pt(297), get_forehead_pt(338)]
        m_jl = draw_line_path_mask((h, w), line_jaw_l, int(jaw_thick * 1.3), blur_jaw, weight=BOOST_CHEEK_JAW)
        m_jr = draw_line_path_mask((h, w), line_jaw_r, int(jaw_thick * 1.3), blur_jaw, weight=BOOST_CHEEK_JAW)
        m_hl = draw_line_path_mask((h, w), line_forehead_l, hair_thick, blur_hair)
        m_hr = draw_line_path_mask((h, w), line_forehead_r, hair_thick, blur_hair)
        contour_mask = np.maximum.reduce([m_nl, m_nr, m_jl, m_jr, m_hl, m_hr])

    elif shape_type == "Rectangular":
        line_top_hair = [get_forehead_pt(103), get_forehead_pt(10), get_forehead_pt(332)]
        line_chin     = [get_pt(148), get_pt(152), get_pt(377)]
        m_th = draw_line_path_mask((h, w), line_top_hair, int(hair_thick * 1.2), int(blur_hair * 1.3) | 1, weight=1.1)
        m_ch = draw_line_path_mask((h, w), line_chin, int(jaw_thick * 1.2), int(blur_jaw * 1.2) | 1, weight=1.1)
        if fullness == "Full":
            line_cheek_l = [get_pt(127), get_pt(116)]
            line_cheek_r = [get_pt(356), get_pt(345)]
            m_cl = draw_line_path_mask((h, w), line_cheek_l, cheek_thick, blur_cheek, weight=0.85)
            m_cr = draw_line_path_mask((h, w), line_cheek_r, cheek_thick, blur_cheek, weight=0.85)
            contour_mask = np.maximum.reduce([m_nl, m_nr, m_th, m_ch, m_cl, m_cr])
        else:
            contour_mask = np.maximum.reduce([m_nl, m_nr, m_th, m_ch])

    elif shape_type == "Heart":
        line_forehead_l = [get_pt(21), get_pt(103), get_forehead_pt(67)]
        line_forehead_r = [get_pt(251), get_pt(332), get_forehead_pt(297)]
        line_cheek_upper_l = [get_pt(227), get_pt(116)]
        line_cheek_upper_r = [get_pt(447), get_pt(345)]
        m_hl = draw_line_path_mask((h, w), line_forehead_l, int(hair_thick * 1.15), blur_hair, weight=1.0)
        m_hr = draw_line_path_mask((h, w), line_forehead_r, int(hair_thick * 1.15), blur_hair, weight=1.0)
        m_cl = draw_line_path_mask((h, w), line_cheek_upper_l, int(cheek_thick * 0.8), blur_cheek, weight=0.8)
        m_cr = draw_line_path_mask((h, w), line_cheek_upper_r, int(cheek_thick * 0.8), blur_cheek, weight=0.8)
        contour_mask = np.maximum.reduce([m_nl, m_nr, m_hl, m_hr, m_cl, m_cr])

    elif shape_type == "Diamond":
        line_cheek_outer_l = [get_pt(227), get_pt(116), get_pt(123)]
        line_cheek_outer_r = [get_pt(447), get_pt(345), get_pt(352)]
        m_cl = draw_line_path_mask((h, w), line_cheek_outer_l, int(cheek_thick * 1.3), blur_cheek, weight=BOOST_CHEEK_JAW)
        m_cr = draw_line_path_mask((h, w), line_cheek_outer_r, int(cheek_thick * 1.3), blur_cheek, weight=BOOST_CHEEK_JAW)
        contour_mask = np.maximum.reduce([m_nl, m_nr, m_cl, m_cr])

    else:
        contour_mask = np.maximum(m_nl, m_nr)

    return np.clip(contour_mask, 0, 1.0)

def render_contour_from_json_file(image_path="test2.jpg", json_file_path="makeup_analysis.json", output_path="output_contour.jpg"):
    if not os.path.exists(json_file_path):
        print(f" لم يتم العثور على ملف الجيسون: {json_file_path}")
        return None

    with open(json_file_path, 'r', encoding='utf-8') as f:
        kb_data = json.load(f)

    expert_face = kb_data.get('expert_output', {}).get('face', {})
    sculpt_data = expert_face.get('sculpt', {}) or kb_data.get('sculpt', {})
    
    face_analysis = kb_data.get('face_analysis', {})
    shape_type = face_analysis.get('face_shape', {}).get('shape') or kb_data.get('shape', {}).get('shape', 'Oval')
    fullness = face_analysis.get('face_fullness', {}).get('fullness') or kb_data.get('input_face_data', {}).get('fullness', 'Full')

    hex_color = sculpt_data.get('hex', '#6E5D53')
    raw_opacity = sculpt_data.get('opacity', 70)
    opacity = raw_opacity / 100.0 if raw_opacity > 1.0 else raw_opacity

    print(f" تم قراءة الملف بنجاح: {json_file_path}")
    print(f" الاستراتيجية المحددة للوجه: {shape_type} ({fullness})")
    print(f" لون الكونتور المختبر (HEX): {hex_color}")
    print(f" نسبة الشفافية: {opacity * 100}%")
    print(f" Sculpt Placement: {sculpt_data.get('placement', 'N/A')}")
    print(f" Sculpt Purpose: {sculpt_data.get('purpose', 'N/A')}")

    img = cv2.imread(image_path)
    if img is None:
        print(f" لم يتم العثور على صورة الدخل: {image_path}")
        return None

    h, w, _ = img.shape
    mp_face_mesh = mp.solutions.face_mesh

    with mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, refine_landmarks=True) as face_mesh:
        results = face_mesh.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        
        if not results.multi_face_landmarks:
            print(" تعذر كشف معالم الوجه في الصورة!")
            return None

        landmarks = results.multi_face_landmarks[0].landmark
        face_scale = calculate_robust_face_scale(landmarks, w, h)

        contour_mask = generate_contour_mask_realistic(
            img, landmarks, face_scale, 
            shape_type=shape_type, 
            fullness=fullness, 
            sculpt_json=sculpt_data
        )

        c_bgr = parse_color(hex_color)
        final_img = apply_realistic_contour(img, contour_mask, c_bgr, opacity=opacity)
        
        cv2.imwrite(output_path, final_img)
        print(f" تم رسم الكونتور بنجاح وحفظ الصورة الناتجة في: {output_path}")

if __name__ == "__main__":
    render_contour_from_json_file(
        image_path="test2.jpg",
        json_file_path="makeup_analysis.json",
        output_path="result_contour.jpg"
    )