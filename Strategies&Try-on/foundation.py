# -*- coding: utf-8 -*-

import collections
import collections.abc
import os
import sys

if not hasattr(collections, "Mapping"):
    collections.Mapping = collections.abc.Mapping

import cv2
import json
import numpy as np
import mediapipe as mp
import gradio as gr

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
try:
    from foundation_makeup_rules import FoundationEngine
except ImportError:
    class FoundationEngine:
        def analyze_foundation(self, analysis_data):
            return {
                "shade": {"hex": "#C68C64", "rgb": [198, 140, 100]},
                "formula": {"texture": "ساتان", "coverage": "متوسطة"}
            }

REAL_FOUNDATION_SWATCHES = {
    "1N": "#F6E7DA", "2N": "#F3E2D3", "2W": "#F2D8C4", "3C": "#E8C8B8", "3N": "#E4BEA8",
    "4N": "#E0B396", "4W": "#D9A784", "5N": "#D39A74", "6C": "#C98C67", "6N": "#C0825C",
    "7C": "#B77752", "7N": "#AE6D48", "7W": "#A5633F", "8N": "#9C5A38", "8W": "#934F30",
    "9N": "#87462B", "9W": "#7D3E25", "10N": "#733720", "10W": "#6A311C", "11N": "#612C18",
    "11W": "#592715", "12N": "#512312", "13W": "#49200F", "14C": "#3F1C0D", "14N": "#37180B",
    "15N": "#2F150A", "16C": "#281208", "17C": "#221006", "17N": "#1C0D05"
}

def parse_color(text_or_hex, default_bgr=(180, 200, 230)):
    if not text_or_hex:
        return default_bgr
    if isinstance(text_or_hex, str) and text_or_hex.startswith("#"):
        hex_str = text_or_hex.lstrip('#')
        rgb = tuple(int(hex_str[i:i + 2], 16) for i in (0, 2, 4))
        return (rgb[2], rgb[1], rgb[0])
    return default_bgr


def create_foundation_swatch(hex_code, size=(200, 200)):
    if not hex_code:
        hex_code = "#CE9166"
    
    hex_str = hex_code.lstrip('#')
    rgb = tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))
    bgr = (rgb[2], rgb[1], rgb[0])
    
    swatch = np.full((size[1], size[0], 3), bgr, dtype=np.uint8)
    cv2.rectangle(swatch, (0, 0), (size[0]-1, size[1]-1), (230, 210, 220), 4)
    return cv2.cvtColor(swatch, cv2.COLOR_BGR2RGB)

def get_skin_mask(landmarks, image):
    h, w, _ = image.shape

    pt_left = np.array([landmarks[234].x * w, landmarks[234].y * h])
    pt_right = np.array([landmarks[454].x * w, landmarks[454].y * h])
    face_width = np.linalg.norm(pt_left - pt_right)

    OVAL_ORDERED = [
        10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365,
        379, 378, 400, 377, 152, 148, 176, 149, 150, 136, 172, 58, 132, 93,
        234, 127, 162, 21, 54, 103, 67, 109
    ]

    FOREHEAD_TOP_INDICES = {10, 338, 297, 332, 284, 251, 109, 67, 103, 54, 21}

    mid_brows_y = landmarks[9].y * h
    top_mesh_y = landmarks[10].y * h
    forehead_height = max(10, abs(mid_brows_y - top_mesh_y))

    pts = []
    for idx in OVAL_ORDERED:
        cx = int(landmarks[idx].x * w)
        cy = int(landmarks[idx].y * h)
        if idx in FOREHEAD_TOP_INDICES:
            offset = int(forehead_height * 0.48)
            cy = max(0, cy - offset)

        pts.append((cx, cy))

    poly_pts = np.array(pts, dtype=np.int32)

    raw_mask = np.zeros((h, w), dtype=np.uint8)
    cv2.fillPoly(raw_mask, [poly_pts], 255)

    protect = np.zeros((h, w), dtype=np.uint8)
    FEATURES = [
        [33, 161, 160, 159, 158, 157, 173, 133, 155, 154, 153, 145, 144, 163, 7],
        [362, 384, 385, 386, 387, 388, 466, 263, 249, 390, 373, 374, 380, 381, 382],
        [70, 63, 105, 66, 107, 55, 65, 52, 53, 46],
        [300, 293, 334, 296, 336, 285, 295, 282, 283, 276],
        [78, 95, 88, 178, 87, 14, 317, 402, 318, 324, 308, 415, 310, 311, 312, 13, 82, 81, 80, 191]
    ]

    for feature in FEATURES:
        feat_pts = np.array([(int(landmarks[idx].x * w), int(landmarks[idx].y * h)) for idx in feature], dtype=np.int32)
        cv2.fillPoly(protect, [feat_pts], 255)

    protect_blur = max(5, int(face_width * 0.02) | 1)
    protect = cv2.GaussianBlur(protect, (protect_blur, protect_blur), 0)

    raw_mask = cv2.bitwise_and(raw_mask, cv2.bitwise_not(protect))

    erode_size = max(3, int(face_width * 0.008) | 1)
    erode_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (erode_size, erode_size))
    eroded_mask = cv2.erode(raw_mask, erode_kernel)
    blur_k = max(15, int(face_width * 0.04) | 1)
    if blur_k % 2 == 0:
        blur_k += 1
    final_mask = cv2.GaussianBlur(eroded_mask, (blur_k, blur_k), 0)

    return final_mask, protect

def render_foundation_engine_direct(image, landmarks, foundation_json, face_scale, override_bgr=None):

    formula_info = foundation_json.get("formula", {})
    texture = formula_info.get("texture", "ساتان")
    coverage = formula_info.get("coverage", "متوسطة")

    if override_bgr is not None:
        foundation_bgr = override_bgr
    else:
        shade_hex = foundation_json.get("shade", {}).get("hex") or foundation_json.get("shade_hex", "#D8A47F")
        foundation_bgr = parse_color(shade_hex, default_bgr=(127, 164, 216))

    skin_mask, _ = get_skin_mask(landmarks, image)
    if np.count_nonzero(skin_mask) == 0:
        return image

    mask_f = (skin_mask.astype(np.float32) / 255.0)[:, :, np.newaxis]

    if "خفيفة" in coverage or "Light" in coverage:
        alpha_color = 0.32       
        alpha_smooth = 0.25     
        detail_keep = 0.85      
        freckle_factor = 0.80    
        d_val, sig_c, sig_s = 5, 15, 15
    elif "كاملة" in coverage or "Full" in coverage:
        alpha_color = 0.65
        alpha_smooth = 0.70
        detail_keep = 0.40
        freckle_factor = 0.15  
        d_val, sig_c, sig_s = 13, 45, 45
    else:  
        alpha_color = 0.48
        alpha_smooth = 0.45
        detail_keep = 0.65
        freckle_factor = 0.45  
        d_val, sig_c, sig_s = 9, 30, 30

    smooth_k = int(face_scale * 0.04) | 1
    if smooth_k < 3: 
        smooth_k = 3


    orig_float = image.astype(np.float32)
    smooth_base = cv2.GaussianBlur(image, (smooth_k, smooth_k), 0)
    bilateral_smooth = cv2.bilateralFilter(smooth_base, d=d_val, sigmaColor=sig_c, sigmaSpace=sig_s)
    
    texture_detail = orig_float - smooth_base.astype(np.float32)

    pos_detail = np.maximum(0.0, texture_detail) 
    neg_detail = np.minimum(0.0, texture_detail)

    adjusted_detail = (pos_detail * detail_keep) + (neg_detail * freckle_factor)

    smoothed_img = cv2.addWeighted(orig_float, (1.0 - alpha_smooth), bilateral_smooth.astype(np.float32), alpha_smooth, 0)

    smoothed_uint8 = np.clip(smoothed_img, 0, 255).astype(np.uint8)
    img_lab = cv2.cvtColor(smoothed_uint8, cv2.COLOR_BGR2LAB).astype(np.float32)
    orig_lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB).astype(np.float32)

    target_pixel = np.uint8([[foundation_bgr]])
    target_lab = cv2.cvtColor(target_pixel, cv2.COLOR_BGR2LAB).astype(np.float32)[0, 0]
    target_L, target_A, target_B = target_lab[0], target_lab[1], target_lab[2]

    skin_pixels = skin_mask > 0
    mean_skin_L = np.mean(orig_lab[:, :, 0][skin_pixels])
    mean_skin_A = np.mean(orig_lab[:, :, 1][skin_pixels])
    mean_skin_B = np.mean(orig_lab[:, :, 2][skin_pixels])

    delta_L = (target_L - mean_skin_L) * alpha_color * 0.5
    delta_A = (target_A - mean_skin_A) * alpha_color * 0.65
    delta_B = (target_B - mean_skin_B) * alpha_color * 0.65

    L_orig = img_lab[:, :, 0]
    A_orig = img_lab[:, :, 1]
    B_orig = img_lab[:, :, 2]

    L_new = L_orig + delta_L
    A_new = A_orig + delta_A
    B_new = B_orig + delta_B

    if "مطفأ" in texture or "Matte" in texture:
        specular_mask = np.maximum(0.0, L_orig - mean_skin_L)
        L_new = L_new - (specular_mask * 0.25)
    elif "نضر" in texture or "لامع" in texture or "Dewy" in texture or "Glow" in texture:
        specular = np.maximum(0.0, L_orig - mean_skin_L)
        glow_boost = (specular / 255.0) * 16.0 * alpha_color
        L_new = L_new + glow_boost

    L_new = np.clip(L_new, 0, 255)
    A_new = np.clip(A_new, 0, 255)
    B_new = np.clip(B_new, 0, 255)

    lab_merged = cv2.merge([L_new, A_new, B_new]).astype(np.uint8)
    bgr_color_shifted = cv2.cvtColor(lab_merged, cv2.COLOR_LAB2BGR).astype(np.float32)

    final_processed = bgr_color_shifted + adjusted_detail
    final_processed = np.clip(final_processed, 0, 255)

    out_bgr = orig_float * (1.0 - mask_f) + final_processed * mask_f
    return np.clip(out_bgr, 0, 255).astype(np.uint8)

def process_foundation_web(input_image_rgb, selected_shade, json_path="makeup_analysis.json"):
    if input_image_rgb is None:
        return None, None, "الرجاء رفع صورة أولاً!"

    img_bgr = cv2.cvtColor(input_image_rgb, cv2.COLOR_RGB2BGR)
    h, w, _ = img_bgr.shape

    shade_hex = REAL_FOUNDATION_SWATCHES.get(selected_shade, "#C68C64")
    selected_bgr = parse_color(shade_hex)

    rec_hex = shade_hex
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                js_data = json.load(f)
                rec_hex = js_data.get("expert_output", {}).get("foundation", {}).get("shade", {}).get("hex", shade_hex)
        except Exception:
            pass

    recommended_swatch_img = create_foundation_swatch(rec_hex)

    sample_analysis = {
        "success": True, "skin_depth": "Medium", "undertone": "Warm",
        "skin_type": "Normal", "color_lab": {"L": 63.137, "a": 17.0, "b": 30.0},
        "color_rgb": [198, 140, 100], "color_hex": shade_hex, "confidence": 0.85
    }
    engine = FoundationEngine()
    expert_results = engine.analyze_foundation(sample_analysis)

    mp_face_mesh = mp.solutions.face_mesh
    with mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1) as face_mesh:
        results = face_mesh.process(input_image_rgb)
        if not results.multi_face_landmarks:
            return None, None, "لم يتم التعرف على وجه في الصورة!"

        face_landmarks = results.multi_face_landmarks[0].landmark
        pt1 = np.array([face_landmarks[234].x * w, face_landmarks[234].y * h])
        pt2 = np.array([face_landmarks[454].x * w, face_landmarks[454].y * h])
        face_scale = np.linalg.norm(pt1 - pt2)

        rec_formula = expert_results.get("formula", {})
        rec_tex = rec_formula.get("texture", "ساتان")
        rec_cov = rec_formula.get("coverage", "متوسطة")

        if "مطفأ" in rec_tex:
            rec_title = "1. Matte Finish"
        elif "نضر" in rec_tex or "لامع" in rec_tex:
            rec_title = "1. Dewy Glow"
        elif "كاملة" in rec_cov:
            rec_title = "1. Full Coverage"
        elif "خفيفة" in rec_cov:
            rec_title = "1. Light Coverage"
        else:
            rec_title = "1. Satin Finish"  

        strategies = [
            ("0. Original Image", None),
            (rec_title, rec_formula),
            ("2. Matte Finish", {"texture": "مطفأ", "coverage": "متوسطة"}),
            ("3. Dewy Glow", {"texture": "نضر ولامع بلطف", "coverage": "خفيفة"}),
            ("4. Full Coverage", {"texture": "ساتان", "coverage": "كاملة"}),
            ("5. Light Coverage", {"texture": "ساتان", "coverage": "خفيفة"})
        ]

        grid_imgs = []
        for title, strat in strategies:
            if strat is None:
                res_img = img_bgr.copy()
            else:
                temp_json = {"formula": strat}
                res_img = render_foundation_engine_direct(
                    img_bgr.copy(), face_landmarks, temp_json, face_scale, override_bgr=selected_bgr
                )
            
            cv2.putText(res_img, f"{title} [{selected_shade}]", (15, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (216, 112, 147), 2, cv2.LINE_AA)
                
            grid_imgs.append(cv2.cvtColor(res_img, cv2.COLOR_BGR2RGB))

        row1 = np.hstack(grid_imgs[:3])
        row2 = np.hstack(grid_imgs[3:])
        final_grid = np.vstack([row1, row2])

        info_msg = (
            f" تم تطبيق الدرجة المختارة: {selected_shade} ({shade_hex})\n"
            f" الاستراتيجية الموصى بها: {rec_tex} بتغطية {rec_cov}\n"
            f" الدرجة الموصى بها في التقرير: {rec_hex}"
        )
        return final_grid, recommended_swatch_img, info_msg

def generate_pink_swatch_css(swatches_dict):
    css_rules = """
    /* خلفية الصفحة كاملة بالأبيض الناعم والوردي الخفيف */
    body, .gradio-container {
        background: linear-gradient(135deg, #fffafc 0%, #fef5f8 100%) !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
    }
    
    /* تنسيق العناوين والـ Markdown */
    h1 {
        color: #d87093 !important;
        text-align: center !important;
        font-weight: 800 !important;
    }
    
    /* شبكة خيارات الألوان */
    .swatch-radio .wrap {
        display: grid !important;
        grid-template-columns: repeat(7, 1fr) !important;
        gap: 6px !important;
    }
    
    /* أزرار الألوان المصممة بالوردي والأبيض */
    .swatch-radio label {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        font-weight: bold !important;
        font-size: 11px !important;
        border-radius: 10px !important;
        padding: 8px 2px !important;
        background-color: #ffffff !important;
        color: #555555 !important;
        border: 1.5px solid #f3d5e0 !important;
        cursor: pointer !important;
        box-shadow: 0 2px 5px rgba(216, 112, 147, 0.08) !important;
        transition: all 0.25s ease-in-out !important;
    }
    
    .swatch-radio label:hover {
        border-color: #d87093 !important;
        background-color: #fff0f5 !important;
        transform: translateY(-2px) !important;
    }
    
    .swatch-radio label.selected {
        border: 2px solid #d87093 !important;
        background-color: #ffe6ee !important;
        color: #b03060 !important;
        box-shadow: 0 3px 8px rgba(216, 112, 147, 0.25) !important;
    }
    
    .swatch-radio label input {
        display: none !important;
    }

    /* زر المحاكاة البينك الوردي الجذاب */
    button.primary-btn, .primary {
        background: linear-gradient(45deg, #ff8da1, #d87093) !important;
        border: none !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 12px rgba(216, 112, 147, 0.3) !important;
        transition: all 0.3s ease !important;
    }

    button.primary-btn:hover, .primary:hover {
        background: linear-gradient(45deg, #d87093, #ff8da1) !important;
        box-shadow: 0 6px 15px rgba(216, 112, 147, 0.45) !important;
        transform: scale(1.01) !important;
    }
    """
    
    for idx, (code, hex_val) in enumerate(swatches_dict.items(), start=1):
        css_rules += f"""
        .swatch-radio .wrap label:nth-child({idx})::before {{
            content: '';
            display: block;
            width: 15px;
            height: 15px;
            border-radius: 50%;
            background-color: {hex_val};
            margin-bottom: 4px;
            border: 1.5px solid #ffffff;
            box-shadow: 0 0 4px rgba(0,0,0,0.15);
        }}
        """
    return css_rules


custom_pink_css = generate_pink_swatch_css(REAL_FOUNDATION_SWATCHES)

with gr.Blocks(title="Real Foundation Swatches Engine", css=custom_pink_css, theme=gr.themes.Soft()) as demo:
    gr.Markdown("#  Foundation Swatches Engine")
    gr.Markdown("<p style='text-align: center; color: #888;'>قومي برفع صورتك واختيار درجة الفاونديشن المفضلة من اللوحة التفاعلية </p>")

    with gr.Row():
        with gr.Column(scale=1):
            img_input = gr.Image(type="numpy", label=" رفع صورة الوجه")
            
            shade_radio = gr.Radio(
                choices=list(REAL_FOUNDATION_SWATCHES.keys()),
                value="2N",
                label="🌸 Foundation Swatches (Dior Palette)",
                elem_classes=["swatch-radio"]
            )
            
            btn_run = gr.Button("تطبيق المحاكاة ", variant="primary", elem_classes=["primary-btn"])
            
            recommended_swatch_display = gr.Image(
                label="عينة التوصية (JSON Swatch)",
                interactive=False,
                width=160,
                height=160
            )
            
            status_output = gr.Textbox(label="  النتيجة والاستراتيجية", interactive=False, lines=3)

        with gr.Column(scale=2):
            img_output = gr.Image(label=" شبكة الاستراتيجيات")

    btn_run.click(
        fn=process_foundation_web,
        inputs=[img_input, shade_radio],
        outputs=[img_output, recommended_swatch_display, status_output]
    )

if __name__ == "__main__":
   demo.launch(server_name="127.0.0.1", server_port=7861, share=True)