# -*- coding: utf-8 -*-

import os
import json
import cv2
import numpy as np
import mediapipe as mp
import gradio as gr

EYE_R_LID = [33, 161, 160, 159, 158, 157, 173, 133]
EYE_L_LID = [362, 384, 385, 386, 387, 388, 466, 263]
EYE_R_CREASE = [130, 247, 30, 29, 27, 28, 56, 190]
EYE_L_CREASE = [359, 467, 260, 259, 257, 258, 286, 414]
BROW_R_BONE = [70, 63, 105, 66, 107]
BROW_L_BONE = [300, 293, 334, 296, 336]
EYE_R_LOWER = [33, 7, 163, 144, 145, 153, 154, 155, 133]
EYE_L_LOWER = [362, 382, 381, 380, 374, 373, 390, 249, 263]

RIGHT_PUPIL_EXC = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161]
LEFT_PUPIL_EXC = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384]

RIGHT_EYE_LANDMARKS = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
LEFT_EYE_LANDMARKS = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]

def hex_to_bgr(hex_str):
    hex_str = str(hex_str).lstrip('#')
    if len(hex_str) == 6:
        r, g, b = int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16)
        return (b, g, r)
    return (128, 128, 128)

def parse_color(hex_str):
    return hex_to_bgr(hex_str)

def get_lm(lm_list, landmarks, w, h):
    return np.array([(int(landmarks[i].x * w), int(landmarks[i].y * h)) for i in lm_list], dtype=np.int32)

def generate_mask(shape, pts, blur_k, is_closed=True, thickness=5):
    h, w = shape[:2]
    mask = np.zeros((h, w), dtype=np.float32)
    poly_pts = pts.astype(np.int32)
    
    if is_closed:
        if len(poly_pts) >= 3:
            poly_pts = cv2.convexHull(poly_pts)
            cv2.fillPoly(mask, [poly_pts], 1.0)
    else:
        cv2.polylines(mask, [poly_pts], isClosed=False, color=1.0, thickness=thickness)
        
    ksize = int(blur_k) | 1
    if ksize > 1:
        mask = cv2.GaussianBlur(mask, (ksize, ksize), 0)
    return np.clip(mask, 0.0, 1.0)

def generate_blush_mask(shape, center_pt, axes, angle, blur_k):
    h, w = shape[:2]
    raw_mask = np.zeros((h, w), dtype=np.float32)
    cv2.ellipse(raw_mask, center=(int(center_pt[0]), int(center_pt[1])),
                axes=(int(axes[0]), int(axes[1])), angle=angle,
                startAngle=0, endAngle=360, color=1.0, thickness=-1)
    ksize = int(blur_k) | 1
    return cv2.GaussianBlur(raw_mask, (ksize, ksize), 0)

def create_pupil_exclusion(shape, landmarks, w, h):
    mask = np.zeros((h, w), dtype=np.float32)
    pts_r = get_lm(RIGHT_PUPIL_EXC, landmarks, w, h)
    pts_l = get_lm(LEFT_PUPIL_EXC, landmarks, w, h)
    
    if len(pts_r) > 0:
        cv2.fillPoly(mask, [pts_r], 1.0)
    if len(pts_l) > 0:
        cv2.fillPoly(mask, [pts_l], 1.0)
        
    mask = cv2.GaussianBlur(mask, (7, 7), 0)
    return 1.0 - np.clip(mask, 0.0, 1.0)

def apply_advanced_blend(base_img, mask, exclusion_mask, color_bgr, opacity=0.7, is_shimmer=False):
    h, w, _ = base_img.shape
    eff_mask = (mask * opacity * exclusion_mask)[:, :, np.newaxis]
    
    base_f = base_img.astype(np.float32) / 255.0
    color_f = np.array([color_bgr[0]/255.0, color_bgr[1]/255.0, color_bgr[2]/255.0], dtype=np.float32)
    
    overlay = np.where(base_f < 0.5, 2.0 * base_f * color_f, 1.0 - 2.0 * (1.0 - base_f) * (1.0 - color_f))
    
    if is_shimmer:
        screen = 1.0 - (1.0 - base_f) * (1.0 - color_f * 0.9)
        blended = overlay * 0.30 + screen * 0.70
    else:
        multiply = base_f * color_f
        blended = overlay * 0.45 + multiply * 0.55
        
    result_f = base_f * (1.0 - eff_mask) + blended * eff_mask
    return np.clip(result_f * 255.0, 0, 255).astype(np.uint8)

def generate_strategic_masks(shape, landmarks, w, h, face_scale, goal_text, style_text):
    g_text = goal_text.lower()
    s_text = style_text.lower()
    
    blur_sharp = max(5, int(face_scale * 0.020))
    blur_soft = max(11, int(face_scale * 0.055))
    
    masks = {
        "Base": np.zeros((h, w), dtype=np.float32),
        "Sculpt": np.zeros((h, w), dtype=np.float32),
        "Accent": np.zeros((h, w), dtype=np.float32),
        "Highlight": np.zeros((h, w), dtype=np.float32)
    }
    
    r_lid = get_lm(EYE_R_LID, landmarks, w, h)
    l_lid = get_lm(EYE_L_LID, landmarks, w, h)
    r_crease = get_lm(EYE_R_CREASE, landmarks, w, h)
    l_crease = get_lm(EYE_L_CREASE, landmarks, w, h)
    r_brow = get_lm(BROW_R_BONE, landmarks, w, h)
    l_brow = get_lm(BROW_L_BONE, landmarks, w, h)
    r_lower = get_lm(EYE_R_LOWER, landmarks, w, h)
    l_lower = get_lm(EYE_L_LOWER, landmarks, w, h)

    if "floating" in g_text or "cut crease" in s_text:
        lift = int(face_scale * 0.025)
        r_crease_lift = r_crease - [0, lift]
        l_crease_lift = l_crease - [0, lift]
        
        masks["Base"] = np.maximum(
            generate_mask(shape, r_lid, blur_sharp*1.5, is_closed=True),
            generate_mask(shape, l_lid, blur_sharp*1.5, is_closed=True)
        )
        line_soft = np.maximum(
            generate_mask(shape, r_crease_lift, blur_soft*0.8, is_closed=False, thickness=int(face_scale*0.03)),
            generate_mask(shape, l_crease_lift, blur_soft*0.8, is_closed=False, thickness=int(face_scale*0.03))
        )
        fade_up = np.maximum(
            generate_mask(shape, r_crease_lift - [0, int(face_scale*0.015)], blur_soft*1.6, is_closed=False, thickness=int(face_scale*0.07)),
            generate_mask(shape, l_crease_lift - [0, int(face_scale*0.015)], blur_soft*1.6, is_closed=False, thickness=int(face_scale*0.07))
        )
        masks["Sculpt"] = np.clip(line_soft * 0.5 + fade_up * 0.8, 0.0, 1.0)

    elif "smoky" in g_text or "smokey" in s_text:
        masks["Sculpt"] = np.maximum(
            generate_mask(shape, r_lid, blur_soft*0.7, is_closed=True),
            generate_mask(shape, l_lid, blur_soft*0.7, is_closed=True)
        )
        masks["Base"] = np.maximum(
            generate_mask(shape, r_crease, blur_soft*1.4, is_closed=False, thickness=int(face_scale*0.12)),
            generate_mask(shape, l_crease, blur_soft*1.4, is_closed=False, thickness=int(face_scale*0.12))
        )

    elif "banana" in g_text or "banana" in s_text:
        masks["Base"] = np.maximum(
            generate_mask(shape, r_lid, blur_sharp*1.5, is_closed=True),
            generate_mask(shape, l_lid, blur_sharp*1.5, is_closed=True)
        )
        banana_arc = np.maximum(
            generate_mask(shape, r_crease, blur_soft*0.9, is_closed=False, thickness=int(face_scale*0.04)),
            generate_mask(shape, l_crease, blur_soft*0.9, is_closed=False, thickness=int(face_scale*0.04))
        )
        masks["Sculpt"] = np.clip(banana_arc - masks["Base"]*0.5, 0.0, 1.0)

    elif "lifting" in g_text or "wing" in s_text or "droopy" in g_text or "foxy" in s_text:
        r_base = generate_mask(shape, r_lid, blur_soft * 0.75, is_closed=True)
        l_base = generate_mask(shape, l_lid, blur_soft * 0.75, is_closed=True)
        masks["Base"] = np.maximum(r_base, l_base)
        
        def create_lift_wing(lid_pts, crease_pts, brow_pts, side):
            if side == "right":
                outer = lid_pts[np.argmin(lid_pts[:, 0])]
                brow_tail = brow_pts[np.argmax(brow_pts[:, 0])]
                outer_lid_pts = lid_pts[np.argsort(lid_pts[:, 0])[:3]]
                outer_crease_pts = crease_pts[np.argsort(crease_pts[:, 0])[:3]]
            else:
                outer = lid_pts[np.argmax(lid_pts[:, 0])]
                brow_tail = brow_pts[np.argmin(brow_pts[:, 0])]
                outer_lid_pts = lid_pts[np.argsort(lid_pts[:, 0])[-3:]]
                outer_crease_pts = crease_pts[np.argsort(crease_pts[:, 0])[-3:]]
                
            direction = brow_tail.astype(np.float32) - outer.astype(np.float32)
            if side == "right":
                direction[0] = -abs(direction[0])
            else:
                direction[0] = abs(direction[0])
            direction[1] = -abs(direction[1])
            
            norm = np.linalg.norm(direction)
            if norm < 1e-5:
                return np.zeros(shape[:2], dtype=np.float32)
            direction /= norm
            
            start = outer.astype(np.float32)
            wing_length = face_scale * 0.12
            tip = start + direction * wing_length
            lift_amount = face_scale * 0.02
            tip[1] -= lift_amount
            
            wing_width = face_scale * 0.028
            perpendicular = np.array([-direction[1], direction[0]], dtype=np.float32)
            
            p3 = tip - perpendicular * (wing_width * 0.3)
            p4 = tip + perpendicular * (wing_width * 0.3)
            
            poly_pts = list(outer_lid_pts) + list(outer_crease_pts) + [p4, p3]
            wing_poly = np.array(poly_pts, dtype=np.float32).astype(np.int32)
            
            return generate_mask(shape, wing_poly, max(11, int(face_scale * 0.045)), is_closed=True)

        right_wing = create_lift_wing(r_lid, r_crease, r_brow, "right")
        left_wing = create_lift_wing(l_lid, l_crease, l_brow, "left")
        wing_mask = np.maximum(right_wing, left_wing)
        
        r_outer_v = generate_mask(shape, r_crease, blur_soft, is_closed=False, thickness=int(face_scale*0.04))
        l_outer_v = generate_mask(shape, l_crease, blur_soft, is_closed=False, thickness=int(face_scale*0.04))
        crease_outer = np.maximum(r_outer_v, l_outer_v)
        
        masks["Sculpt"] = np.clip(wing_mask * 0.85 + crease_outer * 0.35, 0.0, 1.0)
        masks["Accent"] = np.maximum(masks["Accent"], wing_mask * 0.25)

    elif "spotlight" in s_text or "سبوت لايت" in s_text or "deep-set" in g_text or "halo" in s_text:
        r_lid_m = generate_mask(shape, r_lid, blur_soft * 0.85, is_closed=True)
        l_lid_m = generate_mask(shape, l_lid, blur_soft * 0.85, is_closed=True)
        r_crease_m = generate_mask(shape, r_crease, blur_soft * 1.0, is_closed=False, thickness=int(face_scale * 0.05))
        l_crease_m = generate_mask(shape, l_crease, blur_soft * 1.0, is_closed=False, thickness=int(face_scale * 0.05))
        
        masks["Base"] = np.maximum.reduce([r_lid_m, l_lid_m, r_crease_m * 0.7, l_crease_m * 0.7])

        def get_pupil_center(lid_pts, iris_indices):
            if landmarks and len(landmarks) > 477:
                pts = np.array([[int(landmarks[i].x * w), int(landmarks[i].y * h)] for i in iris_indices], dtype=np.float32)
                return np.mean(pts, axis=0)
            return np.mean(lid_pts, axis=0)

        r_center = get_pupil_center(r_lid, [468, 469, 470, 471, 472])
        l_center = get_pupil_center(l_lid, [473, 474, 475, 476, 477])

        def build_halo_eye(lid_pts, crease_pts, center_pt, lid_mask, is_right_eye):
            x_min, x_max = np.min(lid_pts[:, 0]), np.max(lid_pts[:, 0])
            y_min, y_max = np.min(lid_pts[:, 1]), np.max(lid_pts[:, 1])
            eye_w = max(1, x_max - x_min)
            eye_h = max(1, y_max - y_min)

            rx_spot = max(int(eye_w * 0.22), int(face_scale * 0.022))
            ry_spot = max(int(eye_h * 0.70), int(face_scale * 0.025))
            
            spot = generate_blush_mask(shape, center_pt, (rx_spot, ry_spot), angle=0, blur_k=max(5, int(face_scale * 0.02)))
            spot_bounded = spot * np.maximum(lid_mask, generate_mask(shape, crease_pts, blur_soft*0.6, is_closed=False, thickness=int(face_scale*0.03)))

            crease_bridge = generate_mask(shape, crease_pts, blur_soft * 0.7, is_closed=False, thickness=int(face_scale * 0.05))
            
            if is_right_eye:
                p_outer = lid_pts[np.argmin(lid_pts[:, 0])]
                p_inner = lid_pts[np.argmax(lid_pts[:, 0])]
            else:
                p_outer = lid_pts[np.argmax(lid_pts[:, 0])]
                p_inner = lid_pts[np.argmin(lid_pts[:, 0])]

            rx_corner = max(int(eye_w * 0.25), int(face_scale * 0.025))
            ry_corner = max(int(eye_h * 0.65), int(face_scale * 0.025))

            outer_center = p_outer * 0.75 + center_pt * 0.25
            inner_center = p_inner * 0.75 + center_pt * 0.25

            m_outer = generate_blush_mask(shape, outer_center, (rx_corner, ry_corner), angle=0, blur_k=max(7, int(face_scale * 0.035)))
            m_inner = generate_blush_mask(shape, inner_center, (rx_corner, ry_corner), angle=0, blur_k=max(7, int(face_scale * 0.035)))

            sculpt_halo = np.maximum.reduce([m_outer * lid_mask, m_inner * lid_mask, crease_bridge])
            sculpt_halo = sculpt_halo * (1.0 - np.clip(spot_bounded * 1.3, 0.0, 1.0))

            return spot_bounded, sculpt_halo

        r_spot, r_sculpt = build_halo_eye(r_lid, r_crease, r_center, r_lid_m, is_right_eye=True)
        l_spot, l_sculpt = build_halo_eye(l_lid, l_crease, l_center, l_lid_m, is_right_eye=False)

        masks["Highlight"] = np.clip(np.maximum(r_spot, l_spot), 0.0, 1.0)
        masks["Sculpt"] = np.clip(np.maximum(r_sculpt, l_sculpt), 0.0, 1.0)

    else:
        masks["Base"] = np.maximum(
            generate_mask(shape, r_lid, blur_soft),
            generate_mask(shape, l_lid, blur_soft)
        )
        masks["Sculpt"] = np.maximum(
            generate_mask(shape, r_crease, blur_soft, is_closed=False, thickness=int(face_scale*0.04)),
            generate_mask(shape, l_crease, blur_soft, is_closed=False, thickness=int(face_scale*0.04))
        )

    r_brow_skin = r_brow + [0, int(face_scale * 0.018)]
    l_brow_skin = l_brow + [0, int(face_scale * 0.018)]
    brow_hl = np.maximum(
        generate_mask(shape, r_brow_skin, blur_soft*1.1, is_closed=False, thickness=int(face_scale*0.012)),
        generate_mask(shape, l_brow_skin, blur_soft*1.1, is_closed=False, thickness=int(face_scale*0.012))
    )
    if not ("spotlight" in s_text or "سبوت لايت" in s_text or "deep-set" in g_text or "halo" in s_text):
        masks["Highlight"] = np.maximum(masks["Highlight"], brow_hl * 0.25)
        masks["Accent"] = np.maximum(
            generate_mask(shape, r_lower, blur_soft*0.6, is_closed=False, thickness=int(face_scale*0.02)),
            generate_mask(shape, l_lower, blur_soft*0.6, is_closed=False, thickness=int(face_scale*0.02))
        )
        
    return masks

def render_professional_makeup(image, landmarks, face_scale, recommendation_json):
    h, w, _ = image.shape
    output_img = image.copy()

    category_data = recommendation_json.get("category", {})
    goal_text = category_data.get("goal", "")
    plan_data = recommendation_json.get("plan", {})
    style_text = plan_data.get("style", "")

    opacities = {"Base": 0.50, "Sculpt": 0.85, "Highlight": 0.95, "Accent": 0.50}

    if "lifting" in goal_text.lower() or "wing" in style_text.lower() or "droopy" in goal_text.lower():
        opacities["Sculpt"] = 0.85
    elif "spotlight" in style_text.lower() or "سبوت لايت" in style_text.lower() or "deep-set" in goal_text.lower():
        opacities["Sculpt"] = 0.85
        opacities["Highlight"] = 0.95

    parsed_palette_list = {}
    if "eyeshadow_palettes" in recommendation_json:
        palettes = recommendation_json["eyeshadow_palettes"]
        if palettes:
            p_key = list(palettes.keys())[0]
            for item in palettes[p_key]:
                role = item.get("role")
                if role:
                    if role not in parsed_palette_list:
                        parsed_palette_list[role] = []
                    if "hex" in item:
                        parsed_palette_list[role].append(hex_to_bgr(item["hex"]))
                    elif "rgb" in item:
                        parsed_palette_list[role].append((item["rgb"][2], item["rgb"][1], item["rgb"][0]))

    def get_luminance(bgr):
        return 0.299 * bgr[2] + 0.587 * bgr[1] + 0.114 * bgr[0]

    parsed_palette = {}
    for role, colors in parsed_palette_list.items():
        if len(colors) == 1:
            parsed_palette[role] = colors[0]
        elif len(colors) > 1:
            colors_sorted = sorted(colors, key=get_luminance)
            if role == "Highlight":
                parsed_palette[role] = colors_sorted[-1]
            elif role == "Sculpt":
                parsed_palette[role] = colors_sorted[0]
            elif role == "Base":
                parsed_palette[role] = colors_sorted[len(colors_sorted) // 2]
            else:
                parsed_palette[role] = colors_sorted[0]

    fallback_palette = {
        "Base": (160, 180, 210),
        "Sculpt": (25, 30, 50),
        "Highlight": (220, 245, 255),
        "Accent": (80, 100, 140)
    }
    for r in fallback_palette:
        if r not in parsed_palette:
            parsed_palette[r] = fallback_palette[r]

    exclusion_mask = create_pupil_exclusion((h, w), landmarks, w, h)
    masks = generate_strategic_masks((h, w), landmarks, w, h, face_scale, goal_text, style_text)

    for role in ["Base", "Sculpt", "Highlight", "Accent"]:
        if role in masks and role in parsed_palette:
            is_shimmer = role in ["Highlight"] or ("spotlight" in style_text.lower() and role in ["Highlight"])
            output_img = apply_advanced_blend(
                output_img, masks[role], exclusion_mask, parsed_palette[role],
                opacity=opacities.get(role, 0.60), is_shimmer=is_shimmer
            )

    return output_img

def generate_strategies_grid(img_bgr, landmarks, face_scale, palette_colors, palette_name):
    strategies = [
        ("Classic Eye", "Classic", "Classic"),
        ("Smokey Eye", "smoky", "smokey"),
        ("Cut Crease", "Cut Crease", "floating cut crease"),
        ("Banana Crease", "banana", "banana"),
        ("Foxy / Wing Lift", "Illusion Lifting", "wing lifting"),
        ("Halo / Spotlight", "deep-set", "spotlight")
    ]
    
    rendered_images = []
    
    for title, goal, style in strategies:
        mock_json = {
            "category": {"goal": goal},
            "plan": {"style": style},
            "eyeshadow_palettes": {
                palette_name: [
                    {"role": "Base", "hex": palette_colors["Base"]},
                    {"role": "Sculpt", "hex": palette_colors["Sculpt"]},
                    {"role": "Highlight", "hex": palette_colors["Highlight"]},
                    {"role": "Accent", "hex": palette_colors["Accent"]}
                ]
            }
        }
        
        res_img = render_professional_makeup(img_bgr, landmarks, face_scale, mock_json)
        
        header_h = 50
        h, w, _ = res_img.shape
        banner = np.full((header_h, w, 3), (245, 225, 235), dtype=np.uint8)
        
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = max(0.6, w / 800.0)
        thickness = 2
        
        text_size = cv2.getTextSize(title, font, font_scale, thickness)[0]
        text_x = (w - text_size[0]) // 2
        text_y = (header_h + text_size[1]) // 2 - 2
        
        cv2.putText(banner, title, (text_x, text_y), font, font_scale, (147, 112, 216), thickness, cv2.LINE_AA)
        
        combined_single = np.vstack([banner, res_img])
        rendered_images.append(combined_single)
        
    row1 = np.hstack([rendered_images[0], rendered_images[1]])
    row2 = np.hstack([rendered_images[2], rendered_images[3]])
    row3 = np.hstack([rendered_images[4], rendered_images[5]])
    
    return np.vstack([row1, row2, row3])

custom_pink_css = """
body, .gradio-container {
    background: linear-gradient(135deg, #fffafc 0%, #fef5f8 100%) !important;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
}
h1 {
    color: #d87093 !important;
    text-align: center !important;
    font-weight: 800 !important;
}
p {
    text-align: center !important;
    color: #888 !important;
}
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

PRESET_PALETTES = {
    "Luxury Night 🌙": {
        "Base": "#D4AF37",      # Soft Gold
        "Sculpt": "#4B0082",    # Deep Indigo
        "Highlight": "#FFD700", # Bright Gold Shimmer
        "Accent": "#DA70D6"     # Orchid
    },
    "Rose Gold Glam 🌸": {
        "Base": "#E8A398",      # Soft Rose
        "Sculpt": "#8B3A62",    # Deep Berry
        "Highlight": "#FFD1DC", # Champagne Shimmer
        "Accent": "#C71585"     # Deep Pink
    },
    "Sunset Warmth 🌇": {
        "Base": "#E69F00",      # Warm Peach
        "Sculpt": "#A0522D",    # Sienna Brown
        "Highlight": "#FFF8DC", # Soft Cream Shimmer
        "Accent": "#D95F02"     # Burnt Orange
    },
    "Smokey Velvet 🖤": {
        "Base": "#A9A9A9",      # Soft Taupe
        "Sculpt": "#2F4F4F",    # Deep Charcoal
        "Highlight": "#F5F5F5", # Ice Silver Shimmer
        "Accent": "#1C1C1C"     # Midnight Black
    }
}

def create_palette_swatch_img(palette_dict, size=(240, 60)):
    swatch = np.zeros((size[1], size[0], 3), dtype=np.uint8)
    colors = [
        palette_dict.get("Base", "#D4AF37"),
        palette_dict.get("Sculpt", "#4B0082"),
        palette_dict.get("Highlight", "#FFD700"),
        palette_dict.get("Accent", "#DA70D6")
    ]
    step_w = size[0] // 4
    for i, c_hex in enumerate(colors):
        bgr = parse_color(c_hex)
        swatch[:, i*step_w:(i+1)*step_w] = bgr
    cv2.rectangle(swatch, (0, 0), (size[0]-1, size[1]-1), (230, 210, 220), 3)
    return cv2.cvtColor(swatch, cv2.COLOR_BGR2RGB)

def process_eyeshadow_web(input_image_rgb, selected_palette_name):
    if input_image_rgb is None:
        return None, None, None, "الرجاء رفع صورة أولاً! 🌸"
        
    img_bgr = cv2.cvtColor(input_image_rgb, cv2.COLOR_RGB2BGR)
    h, w, _ = img_bgr.shape
    palette_colors = PRESET_PALETTES.get(selected_palette_name, PRESET_PALETTES["Luxury Night 🌙"])
    
    json_path = "makeup_analysis.json"
    recommendation_json = {}
    status_text = ""
    
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                recommendation_json = json.load(f)
        except Exception as e:
            print(f"Error loading JSON: {e}")
            
    expert_output = recommendation_json.get("expert_output", {})
    eye_left = expert_output.get("eyes", {}).get("left", {})
    
    goal_text = eye_left.get("category", {}).get("goal") or recommendation_json.get("category", {}).get("goal", "")
    style_text = eye_left.get("plan", {}).get("style") or recommendation_json.get("plan", {}).get("style", "")
    eye_name = eye_left.get("category", {}).get("name_ar", "العين اللوزية")
    
    if goal_text or style_text:
        status_text = f" نوع العين: {eye_name}\n أسلوب التطبيق: {style_text}\n الهدف: {goal_text}"
    else:
        status_text = " تم تحليل ملامح الوجه وتطبيق المحاكاة بنجاح"
        
    mp_face_mesh = mp.solutions.face_mesh
    with mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, refine_landmarks=True) as face_mesh:
        results = face_mesh.process(input_image_rgb)
        if not results.multi_face_landmarks:
            return None, None, None, "لم يتم التعرف على وجه في الصورة! 🌸"
            
        landmarks = results.multi_face_landmarks[0].landmark
        pt1 = np.array([landmarks[234].x * w, landmarks[234].y * h])
        pt2 = np.array([landmarks[454].x * w, landmarks[454].y * h])
        face_scale = np.linalg.norm(pt1 - pt2)
        
        prepared_json = {
            "category": {"goal": goal_text},
            "plan": {"style": style_text},
            "eyeshadow_palettes": {}
        }
        
        if "eyeshadow_palettes" in recommendation_json and recommendation_json["eyeshadow_palettes"]:
            prepared_json["eyeshadow_palettes"] = recommendation_json["eyeshadow_palettes"]
        else:
            prepared_json["eyeshadow_palettes"] = {
                selected_palette_name: [
                    {"role": "Base", "hex": palette_colors["Base"]},
                    {"role": "Sculpt", "hex": palette_colors["Sculpt"]},
                    {"role": "Highlight", "hex": palette_colors["Highlight"]},
                    {"role": "Accent", "hex": palette_colors["Accent"]}
                ]
            }
            
        rendered_img = render_professional_makeup(
            image=img_bgr,
            landmarks=landmarks,
            face_scale=face_scale,
            recommendation_json=prepared_json
        )
        
        grid_bgr = generate_strategies_grid(
            img_bgr=img_bgr,
            landmarks=landmarks,
            face_scale=face_scale,
            palette_colors=palette_colors,
            palette_name=selected_palette_name
        )
        
        swatch_rgb = create_palette_swatch_img(palette_colors)
        rendered_rgb = cv2.cvtColor(rendered_img, cv2.COLOR_BGR2RGB)
        grid_rgb = cv2.cvtColor(grid_bgr, cv2.COLOR_BGR2RGB)
        
        return rendered_rgb, grid_rgb, swatch_rgb, status_text

with gr.Blocks(title="تطبيق مكياج الظلال", css=custom_pink_css, theme=gr.themes.Soft()) as demo:
    gr.Markdown("# تطبيق مكياج الظلال")
    gr.Markdown("<p>قومي برفع صورتك واختيار باليت ظلال العيون المفضلة لتجربة الأنماط المختلفة</p>")
    
    with gr.Row():
        with gr.Column(scale=1):
            img_input = gr.Image(type="numpy", label="رفع صورة الوجه")
            palette_dropdown = gr.Dropdown(
                choices=list(PRESET_PALETTES.keys()),
                value="Luxury Night 🌙",
                label="🌸 اختر باليت ظلال العيون"
            )
            btn_run = gr.Button("تطبيق المحاكاة", variant="primary", elem_classes=["primary-btn"])
            swatch_out = gr.Image(label="عينة ألوان الباليت", interactive=False, width=240, height=60)
            status_output = gr.Textbox(label="النتيجة والحالة", interactive=False, lines=2)
            
        with gr.Column(scale=2):
            single_out = gr.Image(label="نتيجة التوصية")
            grid_out = gr.Image(label="الاستراتيجيات الستة")
            
    btn_run.click(
        fn=process_eyeshadow_web,
        inputs=[img_input, palette_dropdown],
        outputs=[single_out, grid_out, swatch_out, status_output]
    )

if __name__ == "__main__":
    demo.launch(share=True)