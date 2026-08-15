# -*- coding: utf-8 -*-

import json
import cv2
import numpy as np
import mediapipe as mp
import matplotlib.pyplot as plt
from scipy.interpolate import splprep, splev

NOSE_LEFT_CONTOUR = [193, 245, 122, 174]
NOSE_RIGHT_CONTOUR = [417, 465, 351, 399]
NOSE_BRIDGE_HIGHLIGHT = [168, 6, 197, 195]

COLOR_MAP = {
    "بيج ذهبي فاتح": "#D2B48C",
    "بني دافئ (Warm Brown)": "#5A3E2D",
    "برونزي": "#8B5A2B",
    "بني تاوب رمادي فاتح": "#8B7D7B",
    "موف": "#705353",
    "بني رمادي غامق": "#3D312A",
    "عاجي": "#FFF8DC",
    "وردي لؤلؤي": "#FFE4E1",
    "أبيض": "#FFFFFF"
}

def parse_color(hex_str, default_bgr=(43, 67, 115)):
    if isinstance(hex_str, str) and hex_str.startswith("#"):
        hex_s = hex_str.lstrip('#')
        rgb = tuple(int(hex_s[i:i + 2], 16) for i in (0, 2, 4))
        return (rgb[2], rgb[1], rgb[0])
    return default_bgr

def resolve_color(color_name_or_hex, default_hex="#5A3E2D"):
    if not color_name_or_hex:
        return parse_color(default_hex)
    hex_code = COLOR_MAP.get(color_name_or_hex, color_name_or_hex)
    return parse_color(hex_code, default_bgr=parse_color(default_hex))

def generate_spline_contour_mask(shape, pts, max_thickness, blur_k):
    h, w = shape[:2]
    if len(pts) < 2:
        return np.zeros((h, w), dtype=np.float32)
    pts = np.array(pts)
    _, idx = np.unique(pts, axis=0, return_index=True)
    pts = pts[np.sort(idx)]
    if len(pts) >= 3:
        try:
            tck, _ = splprep([pts[:, 0], pts[:, 1]], s=2, k=min(2, len(pts) - 1))
            u_new = np.linspace(0, 1, 100)
            x_new, y_new = splev(u_new, tck)
            smooth_pts = np.column_stack((x_new, y_new))
        except Exception:
            smooth_pts = pts
    else:
        smooth_pts = pts
    raw_mask = np.zeros((h, w), dtype=np.uint8)
    num_pts = len(smooth_pts)
    for i in range(num_pts - 1):
        progress = i / float(num_pts)
        thickness_factor = np.sin(progress * np.pi) * 0.5 + 0.5
        current_thick = max(1, int(max_thickness * thickness_factor * 0.7))
        p1 = tuple(np.int32(smooth_pts[i]))
        p2 = tuple(np.int32(smooth_pts[i + 1]))
        cv2.line(raw_mask, p1, p2, 255, current_thick, cv2.LINE_AA)
    ksize = int(blur_k * 1.0) | 1
    soft_mask = cv2.GaussianBlur(raw_mask.astype(np.float32) / 255.0, (ksize, ksize), 0)
    return np.clip(soft_mask, 0, 1.0)

def apply_realistic_contour_blend(base_img, mask, shadow_bgr, opacity=0.7):
    img_float = base_img.astype(np.float32) / 255.0
    color_patch = np.zeros_like(img_float)
    color_patch[:] = [shadow_bgr[0] / 255.0, shadow_bgr[1] / 255.0, shadow_bgr[2] / 255.0]
    soft_light = np.where(
        color_patch <= 0.5,
        2 * img_float * color_patch + (img_float ** 2) * (1 - 2 * color_patch),
        2 * img_float * (1 - color_patch) + np.sqrt(np.maximum(img_float, 1e-5)) * (2 * color_patch - 1)
    )
    blend_mix = 0.9 * soft_light + 0.1 * color_patch
    final_weight = (mask * opacity)[:, :, np.newaxis]
    result = (1.0 - final_weight) * img_float + final_weight * blend_mix
    return np.clip(result * 255.0, 0, 255).astype(np.uint8)

def render_nose_contour_advanced(image, landmarks, face_scale, expert_results=None, shape_style=None, contour_bgr=None, highlight_bgr=None):
    h, w, _ = image.shape
    output_img = image.copy()
    map_info = {}

    if expert_results:
        if shape_style is None and 'shape' in expert_results and expert_results['shape']:
            shape_style = expert_results['shape'].get('shape', 'Balanced')
        if contour_bgr is None and 'contour' in expert_results and expert_results['contour']:
            contour_bgr = resolve_color(expert_results['contour'].get('product'), "#5A3E2D")
        if highlight_bgr is None and 'highlight' in expert_results and expert_results['highlight']:
            highlight_bgr = resolve_color(expert_results['highlight'].get('tone'), "#FFF8DC")
        if 'map' in expert_results and expert_results['map']:
            map_info = expert_results['map']

    if shape_style is None:
        shape_style = "Balanced"

    c_color = contour_bgr if contour_bgr is not None else parse_color("#5A3E2D")
    h_color = highlight_bgr if highlight_bgr is not None else parse_color("#FFF8DC")

    bridge_top_y = int(landmarks[168].y * h)
    bridge_mid_y = int(landmarks[6].y * h)
    bridge_bottom_y = int(landmarks[197].y * h)
    tip_pt = (int(landmarks[1].x * w), int(landmarks[1].y * h))
    center_x = int(landmarks[6].x * w)

    c_thick = max(2, int(face_scale * 0.02))
    c_blur = max(5, int(face_scale * 0.035))
    base_width = int(face_scale * 0.024)

    extra_masks = []
    if shape_style == "Wide":
        w_offset = int(base_width * 0.55) 
        l_pts = [(center_x - w_offset, bridge_top_y), (center_x - w_offset, bridge_bottom_y)]
        r_pts = [(center_x + w_offset, bridge_top_y), (center_x + w_offset, bridge_bottom_y)]

        u_mask = np.zeros((h, w), dtype=np.uint8)
        cv2.ellipse(u_mask, (tip_pt[0], tip_pt[1] + int(face_scale*0.005)), 
                    (int(face_scale * 0.022), int(face_scale * 0.012)), 0, 0, 180, 255, c_thick)
        extra_masks.append(cv2.GaussianBlur(u_mask.astype(np.float32) / 255.0, (c_blur | 1, c_blur | 1), 0))

    elif shape_style == "Long":
        w_offset = base_width
        l_pts = [(center_x - w_offset, bridge_mid_y), (center_x - w_offset, bridge_bottom_y)]
        r_pts = [(center_x + w_offset, bridge_mid_y), (center_x + w_offset, bridge_bottom_y)]

    elif shape_style == "Short":

        w_offset = base_width
        top_y_ext = bridge_top_y - int(face_scale * 0.02)
        l_pts = [(center_x - w_offset, top_y_ext), (center_x - w_offset, bridge_bottom_y)]
        r_pts = [(center_x + w_offset, top_y_ext), (center_x + w_offset, bridge_bottom_y)]

    elif shape_style == "Drooping":
    
        w_offset = base_width
        l_pts = [(center_x - w_offset, bridge_top_y), (center_x - w_offset, bridge_bottom_y)]
        r_pts = [(center_x + w_offset, bridge_top_y), (center_x + w_offset, bridge_bottom_y)]
        
        lift_mask = np.zeros((h, w), dtype=np.uint8)
        cv2.circle(lift_mask, (tip_pt[0], tip_pt[1] + int(face_scale * 0.012)), int(face_scale * 0.02), 255, -1)
        extra_masks.append(cv2.GaussianBlur(lift_mask.astype(np.float32) / 255.0, (c_blur | 1, c_blur | 1), 0))

    elif shape_style == "Crooked":
    
        w_offset = int(base_width * 0.85)
        l_pts = [(center_x - w_offset, bridge_top_y), (center_x - w_offset, bridge_bottom_y)]
        r_pts = [(center_x + w_offset, bridge_top_y), (center_x + w_offset, bridge_bottom_y)]

    else:  
        w_offset = base_width
        l_pts = [(center_x - w_offset, bridge_top_y), (center_x - w_offset, bridge_bottom_y)]
        r_pts = [(center_x + w_offset, bridge_top_y), (center_x + w_offset, bridge_bottom_y)]


    mask_l = generate_spline_contour_mask((h, w), l_pts, c_thick, c_blur)
    mask_r = generate_spline_contour_mask((h, w), r_pts, c_thick, c_blur)
    contour_mask = np.maximum(mask_l, mask_r)

    for ex_m in extra_masks:
        contour_mask = np.maximum(contour_mask, ex_m)

    output_img = apply_realistic_contour_blend(output_img, contour_mask, c_color, opacity=0.65)


    tip_shading_str = map_info.get('tip_shading', '')
    if shape_style == "Long" or "ظل دائري" in tip_shading_str:
       
        shading_mask = np.zeros((h, w), dtype=np.uint8)
        cv2.circle(shading_mask, tip_pt, int(face_scale * 0.026), 255, -1)
        soft_shading = cv2.GaussianBlur(shading_mask.astype(np.float32) / 255.0, (c_blur | 1, c_blur | 1), 0)
        output_img = apply_realistic_contour_blend(output_img, soft_shading, c_color, opacity=0.7)

 
    highlight_str = map_info.get('highlight', '')
    h_thick = max(1, int(face_scale * 0.015))
    h_blur = max(4, int(face_scale * 0.03))
    bridge_pts = [(int(landmarks[i].x * w), int(landmarks[i].y * h)) for i in NOSE_BRIDGE_HIGHLIGHT]

    if shape_style == "Long" or "يتوقف قبل الطرف" in highlight_str:
      
        short_bridge = bridge_pts[:len(bridge_pts)//2 + 1]
        b_mask = generate_spline_contour_mask((h, w), short_bridge, h_thick, h_blur)
        output_img = apply_realistic_contour_blend(output_img, b_mask, h_color, opacity=0.55)

    elif shape_style == "Short" or "على طرف الأنف" in highlight_str:

        b_mask = generate_spline_contour_mask((h, w), bridge_pts, h_thick, h_blur)
        tip_mask = np.zeros((h, w), dtype=np.uint8)
        cv2.circle(tip_mask, tip_pt, max(1, int(face_scale * 0.014)), 255, -1)
        soft_tip = cv2.GaussianBlur(tip_mask.astype(np.float32) / 255.0, (h_blur | 1, h_blur | 1), 0)
        combined_hl = np.maximum(b_mask, soft_tip)
        output_img = apply_realistic_contour_blend(output_img, combined_hl, h_color, opacity=0.6)

    elif shape_style == "Drooping":

        b_mask = generate_spline_contour_mask((h, w), bridge_pts[:-1], h_thick, h_blur)
        tip_target = (tip_pt[0], tip_pt[1] - int(face_scale * 0.01))
        tip_mask = np.zeros((h, w), dtype=np.uint8)
        cv2.circle(tip_mask, tip_target, max(1, int(face_scale * 0.012)), 255, -1)
        soft_tip = cv2.GaussianBlur(tip_mask.astype(np.float32) / 255.0, (h_blur | 1, h_blur | 1), 0)
        combined_hl = np.maximum(b_mask, soft_tip)
        output_img = apply_realistic_contour_blend(output_img, combined_hl, h_color, opacity=0.6)

    else:

        b_mask = generate_spline_contour_mask((h, w), bridge_pts, h_thick, h_blur)
        output_img = apply_realistic_contour_blend(output_img, b_mask, h_color, opacity=0.5)

    return output_img

def apply_nose_makeup_from_json(json_path: str, image_path: str, save_output_path: str = None):

    try:

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        nose_expert_results = data.get("expert_output", {}).get("nose", {})
        if not nose_expert_results:
            print("تحذير: لم يتم العثور على قسم 'nose' في 'expert_output' داخل ملف JSON.")
            return None

        img = cv2.imread(image_path)
        if img is None:
            print(f"خطأ: تعذر قراءة الصورة من المسار: {image_path}")
            return None

        h, w, _ = img.shape

        mp_face_mesh = mp.solutions.face_mesh
        with mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, refine_landmarks=True) as face_mesh:
            results = face_mesh.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            
            if not results.multi_face_landmarks:
                print("خطأ: لم يتم اكتشاف أي وجه في الصورة")
                return None

            landmarks = results.multi_face_landmarks[0].landmark
            pt1 = np.array([landmarks[234].x * w, landmarks[234].y * h])
            pt2 = np.array([landmarks[454].x * w, landmarks[454].y * h])
            face_scale = np.linalg.norm(pt1 - pt2)

            output_image = render_nose_contour_advanced(
                image=img,
                landmarks=landmarks,
                face_scale=face_scale,
                expert_results=nose_expert_results
            )

            if save_output_path:
                cv2.imwrite(save_output_path, output_image)
                print(f"تم حفظ الصورة المعالجة بنجاح في: {save_output_path}")

            return output_image

    except Exception as e:
        print(f"حدث خطأ أثناء تنفيذ الدالة: {e}")
        return None


if __name__ == "__main__":
    json_file = "makeup_analysis.json"
    img_file = "test3.jpg"

    result_img = apply_nose_makeup_from_json(
        json_path=json_file,
        image_path=img_file,
        save_output_path="output_nose_makeup.jpg"
    )

    if result_img is not None:
        plt.figure(figsize=(6, 6))
        plt.imshow(cv2.cvtColor(result_img, cv2.COLOR_BGR2RGB))
        plt.title("Nose Makeup Applied From JSON", fontsize=11, fontweight='bold')
        plt.axis('off')
        plt.show()

if __name__ == "__main__":
    image_path = "test3.jpg"
    img = cv2.imread(image_path)
    if img is not None:
        h, w, _ = img.shape
        mp_face_mesh = mp.solutions.face_mesh
        with mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, refine_landmarks=True) as face_mesh:
            results = face_mesh.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            if results.multi_face_landmarks:
                landmarks = results.multi_face_landmarks[0].landmark
                pt1 = np.array([landmarks[234].x * w, landmarks[234].y * h])
                pt2 = np.array([landmarks[454].x * w, landmarks[454].y * h])
                face_scale = np.linalg.norm(pt1 - pt2)

                styles = ["Wide", "Long", "Drooping", "Crooked", "Short", "Balanced"]
                fig, axes = plt.subplots(2, 3, figsize=(15, 9))
                axes = axes.ravel()

                for idx, st in enumerate(styles):
                 
                    res = render_nose_contour_advanced(img, landmarks, face_scale, shape_style=st)
                    axes[idx].imshow(cv2.cvtColor(res, cv2.COLOR_BGR2RGB))
                    axes[idx].set_title(f"Nose Shape Strategy: {st}", fontsize=11, fontweight='bold')
                    axes[idx].axis('off')

                plt.tight_layout()
                plt.show()
            else:
                print("لم يتم العثور على وجه.")
    else:
        print(f"تعذر العثور على الصورة: {image_path}")