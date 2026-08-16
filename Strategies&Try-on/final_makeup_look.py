# -*- coding: utf-8 -*-

import collections
import collections.abc
import os
import json
import sys
import tempfile
import traceback

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from complete_makeup_pipline import analyze_image

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

if not hasattr(collections, "Mapping"):
    collections.Mapping = collections.abc.Mapping
 
import cv2
import numpy as np
import mediapipe as mp
import gradio as gr

import pandas as pd
import re
from urllib.parse import urlparse
from product_recommender import *

from shadow_palette_rules import NEUTRAL_12_COOL, NEUTRAL_12_WARM, generate_strategy_palettes
 
def _safe_import(module_name, names):
    out = {}
    try:
        mod = __import__(module_name, fromlist=names)
        for n in names:
            out[n] = getattr(mod, n)
    except Exception as e:
        print(f"  تعذر استيراد ({', '.join(names)}) من {module_name}.py: {e}")
        for n in names:
            out[n] = None
    return out
 
_foundation = _safe_import("foundation", ["render_foundation_engine_direct", "parse_color"])
render_foundation_engine_direct = _foundation["render_foundation_engine_direct"]
parse_foundation_color = _foundation["parse_color"]
 
_concealer = _safe_import("concealer", ["apply_concealer_layer"])
apply_concealer_layer = _concealer["apply_concealer_layer"]
 
_contour = _safe_import("contour", [
    "generate_contour_mask_realistic", "apply_realistic_contour", "parse_color"
])
generate_contour_mask_realistic = _contour["generate_contour_mask_realistic"]
apply_realistic_contour = _contour["apply_realistic_contour"]
parse_contour_color = _contour["parse_color"]
 
_highlight = _safe_import("highlight", ["render_expert_highlight_pipeline"])
render_expert_highlight_pipeline = _highlight["render_expert_highlight_pipeline"]
 
_nose = _safe_import("nose", ["render_nose_contour_advanced"])
render_nose_contour_advanced = _nose["render_nose_contour_advanced"]
 
_blush = _safe_import("blush", ["render_blush_engine_perfect", "parse_strategy_from_json"])
render_blush_engine_perfect = _blush["render_blush_engine_perfect"]
parse_strategy_from_json = _blush["parse_strategy_from_json"]
 
_brow = _safe_import("brow", [
    "render_brow_engine_v13_2", "map_kb_color_to_swatch", "map_color_intensity_to_strength"
])
render_brow_engine_v13_2 = _brow["render_brow_engine_v13_2"]
map_kb_color_to_swatch = _brow["map_kb_color_to_swatch"]
map_color_intensity_to_strength = _brow["map_color_intensity_to_strength"]
 
_shadow = _safe_import("shadow", ["render_professional_makeup", "PRESET_PALETTES"])
render_professional_makeup = _shadow["render_professional_makeup"]
SHADOW_PRESET_PALETTES = _shadow["PRESET_PALETTES"] or {}
 
_eyeliner = _safe_import("eyeliner", [
    "apply_experta_eyeliner_recommendation", "generate_eyeliner_mask_advanced",
    "apply_photorealistic_eyeliner"
])
apply_experta_eyeliner_recommendation = _eyeliner["apply_experta_eyeliner_recommendation"]
generate_eyeliner_mask_advanced = _eyeliner["generate_eyeliner_mask_advanced"]
apply_photorealistic_eyeliner = _eyeliner["apply_photorealistic_eyeliner"]
 
_lashes = _safe_import("lashes", [
    "apply_experta_lashes_recommendation", "generate_lashes_overlay_rgba",
    "apply_photorealistic_lashes_correct"
])
apply_experta_lashes_recommendation = _lashes["apply_experta_lashes_recommendation"]
generate_lashes_overlay_rgba = _lashes["generate_lashes_overlay_rgba"]
apply_photorealistic_lashes_correct = _lashes["apply_photorealistic_lashes_correct"]
 
_lips = _safe_import("lips", ["apply_recommended_lip_makeup", "render_lips_engine"])
apply_recommended_lip_makeup = _lips["apply_recommended_lip_makeup"]
render_lips_engine = _lips["render_lips_engine"]
 

def hex_to_bgr(hex_str, default_bgr=(180, 150, 200)):
    if not hex_str or not isinstance(hex_str, str) or not hex_str.startswith("#"):
        return default_bgr
    try:
        h = hex_str.lstrip("#")
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return (b, g, r)
    except Exception:
        return default_bgr
 
 
def get_landmarks(img_bgr):
    h, w, _ = img_bgr.shape
    mp_face_mesh = mp.solutions.face_mesh
    with mp_face_mesh.FaceMesh(
        static_image_mode=True, max_num_faces=1, refine_landmarks=True
    ) as fm:
        results = fm.process(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))
        if not results.multi_face_landmarks:
            return None, None, h, w
        landmarks = results.multi_face_landmarks[0].landmark
        p1 = np.array([landmarks[234].x * w, landmarks[234].y * h])
        p2 = np.array([landmarks[454].x * w, landmarks[454].y * h])
        face_scale = np.linalg.norm(p1 - p2)
    return landmarks, face_scale, h, w
 
 
def make_tile(img_bgr, title, target_w=340, banner_h=42,
              banner_bg=(239, 205, 219), text_color=(147, 20, 84)):
    h, w = img_bgr.shape[:2]
    scale = target_w / float(w)
    target_h = max(1, int(h * scale))
    resized = cv2.resize(img_bgr, (target_w, target_h))
 
    banner = np.full((banner_h, target_w, 3), banner_bg, dtype=np.uint8)
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.55
    thickness = 1
    text_size = cv2.getTextSize(title, font, font_scale, thickness)[0]
    tx = max(6, (target_w - text_size[0]) // 2)
    ty = (banner_h + text_size[1]) // 2 - 2
    cv2.putText(banner, title, (tx, ty), font, font_scale, text_color, thickness, cv2.LINE_AA)
 
    return np.vstack([banner, resized])
 
 
def build_grid(tiles, cols=3):
    if not tiles:
        blank = np.full((200, 200, 3), 245, dtype=np.uint8)
        return cv2.cvtColor(blank, cv2.COLOR_BGR2RGB)
    rendered = [make_tile(img, title) for title, img in tiles]
    rows = []
    for i in range(0, len(rendered), cols):
        row_tiles = rendered[i:i + cols]
        while len(row_tiles) < cols:
            row_tiles.append(np.full_like(row_tiles[0], 255))
        rows.append(np.hstack(row_tiles))
    grid = np.vstack(rows)
    return cv2.cvtColor(grid, cv2.COLOR_BGR2RGB)
 
 
def _safe(title, fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except Exception as e:
        print(f"⚠️  فشل توليد '{title}': {e}")
        traceback.print_exc()
        return None
 
def hsv_to_hex(hsv_tuple):
    h, s, v = hsv_tuple
    hsv_img = np.uint8([[[h, s, v]]])
    rgb = cv2.cvtColor(hsv_img, cv2.COLOR_HSV2RGB)[0][0]
    return "#{:02X}{:02X}{:02X}".format(rgb[0], rgb[1], rgb[2])

def extract_hex_palette_from_expert(expert_engine_output, skin_undertone="Cool"):
    path_type = getattr(expert_engine_output, 'path_type', 'neutral_12')
    cloth_hue = getattr(expert_engine_output, 'cloth_hue', 0)
    
    if path_type == "colored_palettes":
        strategies = generate_strategy_palettes(cloth_hue, skin_undertone)
        selected_strat = strategies.get("Monochromatic", list(strategies.values())[0])
        
        return [
            {"role": "Base", "hex": hsv_to_hex(selected_strat["Base"])},
            {"role": "Sculpt", "hex": hsv_to_hex(selected_strat["Sculpt"])},
            {"role": "Highlight", "hex": hsv_to_hex(selected_strat["Highlight"])},
            {"role": "Accent", "hex": hsv_to_hex(selected_strat.get("Accent", selected_strat["Base"]))}
        ]
    else:
        neutral_colors = NEUTRAL_12_WARM if skin_undertone == "Warm" else NEUTRAL_12_COOL
        return [
            {"role": "Base", "hex": hsv_to_hex(neutral_colors["Base"][0])},
            {"role": "Sculpt", "hex": hsv_to_hex(neutral_colors["Sculpt"][0])},
            {"role": "Highlight", "hex": hsv_to_hex(neutral_colors["Highlight"][0])},
            {"role": "Accent", "hex": hsv_to_hex(neutral_colors["Accent"][0])}
        ]

def apply_eyeshadow_bridge(img, landmarks, face_scale, full_json_data, palette_expert_engine=None):
    if render_professional_makeup is None:
        return img
    
    full_json_data = full_json_data or {}
    expert_output = full_json_data.get("expert_output") or full_json_data or {}
    eyes_data = expert_output.get("eyes") or {}
    
    eye_info = {}
    if isinstance(eyes_data, dict):
        eye_info = eyes_data.get("left") or eyes_data.get("right") or {}
        
    goal_text = (eye_info.get("category") or {}).get("goal", "") if isinstance(eye_info, dict) else ""
    style_text = (eye_info.get("plan") or {}).get("style", "") if isinstance(eye_info, dict) else ""

    mapped_goal = goal_text
    mapped_style = style_text

    if "كت كريز" in style_text or "قطع" in style_text:
        mapped_style += " floating cut crease"
    if "جناح" in style_text or "رفع" in style_text:
        mapped_style += " wing lifting"
        mapped_goal += " lifting"
    if "سموكي" in style_text:
        mapped_style += " smoky"
    if "سبوت لايت" in style_text:
        mapped_style += " spotlight"

    if full_json_data.get("eyeshadow_palettes"):
        palettes = full_json_data["eyeshadow_palettes"]
    elif palette_expert_engine:
        skin_ut = (full_json_data.get("skin_profile") or {}).get("undertone", "Cool")
        palettes = {
            "Generated_Palette": extract_hex_palette_from_expert(palette_expert_engine, skin_ut)
        }
    else:
        palettes = {
            "Default": [
                {"role": "Base", "hex": "#C8A48C"},
                {"role": "Sculpt", "hex": "#5C4033"},
                {"role": "Highlight", "hex": "#FFF3E0"},
                {"role": "Accent", "hex": "#8B5E3C"},
            ]
        }

    prepared_data = {
        "category": {"goal": mapped_goal},
        "plan": {"style": mapped_style},
        "eyeshadow_palettes": palettes
    }

    try:
        return render_professional_makeup(img, landmarks, face_scale, prepared_data)
    except Exception as e:
        print(f"⚠️ Error applying eyeshadow: {e}")
        return img


def apply_foundation_from_json(img, landmarks, face_scale, foundation_json):
    if render_foundation_engine_direct is None:
        print("⚠️  تخطينا الفاونديشن (foundation.py غير متاح).")
        return img

    foundation_json = foundation_json or {}
    shade_data = foundation_json.get("shade") or {}
    rgb = shade_data.get("rgb") if isinstance(shade_data, dict) else None
    target_bgr = (rgb[2], rgb[1], rgb[0]) if rgb and len(rgb) == 3 else None

    formula_data = foundation_json.get("formula") or {}

    payload = {
        "shade_hex": shade_data.get("hex", "#D8A47F") if isinstance(shade_data, dict) else "#D8A47F",
        "formula": formula_data,
    }

    result = render_foundation_engine_direct(
        image=img, landmarks=landmarks, foundation_json=payload, face_scale=face_scale, override_bgr=target_bgr,
    )
    print(f"✅ الفاونديشن -> Shade: {payload['shade_hex']} "
          f"| Texture: {formula_data.get('texture')} "
          f"| Coverage: {formula_data.get('coverage')}")
    return result


def _infer_concealer_depth_and_coverage(foundation_json):
    foundation_json = foundation_json or {}
    concealer_data = foundation_json.get("concealer") or {}
    formula_data = foundation_json.get("formula") or {}

    descriptor = str(concealer_data.get("descriptor", "") if isinstance(concealer_data, dict) else "").strip()

    if "درجة أفتح من الأساس بدرجة واحدة" in descriptor:
        depth = "Fair"
    elif "درجة أفتح بدرجة إلى درجة ونصف" in descriptor:
        depth = "Medium"
    elif ("أندرتون دافئ" in descriptor or "برتقالي" in descriptor or "خوخي" in descriptor):
        depth = "Dark"
    else:
        depth = "Medium"

    foundation_coverage = str(formula_data.get("coverage", "متوسطة") if isinstance(formula_data, dict) else "متوسطة")
    if "خفيفة" in foundation_coverage:
        coverage = "Light"
    elif "كاملة" in foundation_coverage:
        coverage = "Full"
    else:
        coverage = "Medium"

    return depth, coverage


def apply_concealer_from_json(img, landmarks, face_scale, foundation_json):
    if apply_concealer_layer is None:
        print("⚠️  تخطينا الكونسيلر (concealer.py غير متاح).")
        return img

    foundation_json = foundation_json or {}
    concealer_data = foundation_json.get("concealer") or {}
    if not concealer_data or not isinstance(concealer_data, dict):
        print(" ما في قسم concealer بالجيسون، تخطينا هالخطوة.")
        return img

    depth, coverage = _infer_concealer_depth_and_coverage(foundation_json)

    target_rgb = concealer_data.get("rgb")
    if target_rgb and isinstance(target_rgb, (list, tuple)) and len(target_rgb) == 3:
        target_rgb = tuple(target_rgb)
    else:
        target_rgb = None

    result = apply_concealer_layer(
        image=img, landmarks=landmarks, face_scale=face_scale, depth=depth, coverage=coverage, target_rgb=target_rgb
    )
    print(f"✅ الكونسيلر -> Depth: {depth} | Coverage: {coverage} | RGB Used: {target_rgb}")
    return result


def apply_face_sculpt_from_json(img, landmarks, face_scale, face_json):
    if generate_contour_mask_realistic is None or apply_realistic_contour is None:
        print("⚠️ تخطينا نحت الوجه (contour.py غير متاح).")
        return img

    face_json = face_json or {}
    sculpt_data = face_json.get("sculpt") or {}
    if not sculpt_data or not isinstance(sculpt_data, dict):
        print(" ما في قسم sculpt بالجيسون، تخطينا هالخطوة.")
        return img

    shape_data = face_json.get("shape") or {}
    if isinstance(shape_data, dict):
        shape_type = shape_data.get("shape", "Oval")
    elif isinstance(shape_data, str):
        shape_type = shape_data
    else:
        shape_type = "Oval"

    fullness = face_json.get("fullness") or "Full"
    hex_color = sculpt_data.get("hex") or "#6E5D53"
    raw_opacity = sculpt_data.get("opacity", 60)
    opacity = raw_opacity / 100.0 if raw_opacity > 1.0 else raw_opacity

    contour_mask = generate_contour_mask_realistic(
        img, landmarks, face_scale, shape_type=shape_type, fullness=fullness, sculpt_json=sculpt_data,
    )
    c_bgr = (
        parse_contour_color(hex_color) if parse_contour_color else hex_to_bgr(hex_color)
    )
    result = apply_realistic_contour(
        img, contour_mask, c_bgr, opacity=opacity
    )
    print(
        f"✅ نحت الوجه -> Shape: {shape_type} | Color: {hex_color} | Opacity: {opacity}"
    )
    return result


def apply_face_highlight_from_json(img, landmarks, face_scale, face_json):
    if render_expert_highlight_pipeline is None:
        print("⚠️ تخطينا الهايلايتر (highlight.py غير متاح).")
        return img

    face_json = face_json or {}
    highlight_data = face_json.get("highlight") or {}
    if not highlight_data or not isinstance(highlight_data, dict):
        print(" ما في قسم highlight بالجيسون، تخطينا هالخطوة.")
        return img

    highlight_data_prepared = highlight_data.copy()
    if "hex" not in highlight_data_prepared:
        highlight_data_prepared["hex"] = "#FFF8DC"
    if "opacity" not in highlight_data_prepared:
        highlight_data_prepared["opacity"] = 50

    texture_data = face_json.get("texture") or {"finish": "ساتان / لامع"}

    expert_results = {
        "highlight": highlight_data_prepared,
        "texture": texture_data,
    }
    result = render_expert_highlight_pipeline(
        img, landmarks, expert_results, face_scale
    )
    print(
        f"✅ الهايلايتر -> Placement: {highlight_data_prepared.get('placement', '')}"
    )
    return result


def apply_nose_from_json(img, landmarks, face_scale, nose_json):
    if render_nose_contour_advanced is None:
        print("⚠️  تخطينا نحت الأنف (nose.py غير متاح).")
        return img

    nose_json = nose_json or {}
    if not nose_json:
        print(" ما في قسم nose بالجيسون، تخطينا هالخطوة.")
        return img

    result = render_nose_contour_advanced(
        image=img, landmarks=landmarks, face_scale=face_scale, expert_results=nose_json,
    )
    
    shape_val = ""
    shape_sec = nose_json.get("shape") or {}
    if isinstance(shape_sec, dict):
        shape_val = shape_sec.get("shape", "")
    elif isinstance(shape_sec, str):
        shape_val = shape_sec

    print(f"✅ نحت الأنف -> Shape: {shape_val}")
    return result


def extract_blush_color_and_opacity(full_json_data, expert_output, face_json):
    face_json = face_json or {}
    blush_data = face_json.get("blush") or {}
    rgb = None

    if isinstance(blush_data, dict) and "color_details" in blush_data:
        color_details = blush_data.get("color_details") or {}
        if isinstance(color_details, dict):
            primary = color_details.get("primary") or {}
            if isinstance(primary, dict):
                rgb = primary.get("rgb")

    if not rgb or not isinstance(rgb, (list, tuple)) or len(rgb) < 3:
        rgb = [224, 122, 95]

    blush_bgr = (rgb[2], rgb[1], rgb[0])
    opacity_pct = blush_data.get("opacity", 52) if isinstance(blush_data, dict) else 52
    opacity = float(opacity_pct) / 100.0 if opacity_pct > 1 else float(opacity_pct)

    return blush_bgr, opacity


def apply_blush_from_json(img, landmarks, face_scale, full_json_data, expert_output, face_json):
    if render_blush_engine_perfect is None:
        print("⚠️ تخطينا البلاش (blush.py غير متاح).")
        return img

    face_json = face_json or {}
    blush_data = face_json.get("blush") or {}
    if not blush_data:
        print(" ما في قسم blush بالجيسون، تخطينا هالخطوة.")
        return img

    blush_bgr, opacity = extract_blush_color_and_opacity(full_json_data, expert_output, face_json)

    strategy = (
        parse_strategy_from_json(full_json_data, expert_output)
        if parse_strategy_from_json else "Lifted_Temple"
    )

    result = render_blush_engine_perfect(
        image=img, landmarks=landmarks, face_scale=face_scale,
        strategy=strategy, override_bgr=blush_bgr, opacity=opacity,
    )
    print(f"✅ البلاش -> Strategy: {strategy} | Opacity: {opacity}")
    return result


def apply_brows_from_json(img, landmarks, face_scale, brows_json, face_json, occasion):
    if render_brow_engine_v13_2 is None:
        print("⚠️ تخطينا الحواجب (brow.py غير متاح).")
        return img

    brows_json = brows_json or {}
    if not brows_json:
        print("⚠️ ما في قسم brows بالجيسون، تخطينا هالخطوة.")
        return img

    face_json = face_json or {}
    shape_type = "Oval"

    shape_section = face_json.get("shape") or {}
    if isinstance(shape_section, dict):
        shape_type = shape_section.get("shape") or face_json.get("face_shape") or "Oval"
    elif isinstance(shape_section, str):
        shape_type = shape_section
    else:
        shape_type = face_json.get("face_shape") or "Oval"

    if shape_type == "Oval" and isinstance(brows_json, dict):
        rec = brows_json.get("recommendation") or {}
        if isinstance(rec, dict) and rec.get("face_shape"):
            shape_type = rec.get("face_shape")

    color_info = brows_json.get("color")
    undertone = brows_json.get("undertone", "warm") or "warm"
    depth = brows_json.get("depth", "medium") or "medium"

    if map_kb_color_to_swatch:
        swatch_name, target_bgr = map_kb_color_to_swatch(color_info, fallback_undertone=undertone, fallback_depth=depth)
    else:
        swatch_name, target_bgr = None, None

    style_info = brows_json.get("style") or {}
    color_intensity = "طبيعي"
    if isinstance(style_info, dict):
        color_intensity = style_info.get("color_intensity") or "طبيعي"

    tint_strength = (
        map_color_intensity_to_strength(color_intensity)
        if map_color_intensity_to_strength else 0.28
    )

    result = render_brow_engine_v13_2(
        image=img,
        landmarks=landmarks,
        face_scale=face_scale,
        shape_type=shape_type,
        occasion=occasion,
        override_bgr=target_bgr,
        tint_strength=tint_strength,
    )

    print(f"✅ الحواجب تم تطبيقها -> Shape: {shape_type} | Occasion: {occasion} | Swatch: {swatch_name} | Strength: {tint_strength}")
    return result


def apply_eyeliner_from_json(img, landmarks, face_scale, eyes_payload, occasion):
    if apply_experta_eyeliner_recommendation is None:
        print("⚠️  تخطينا الآيلاينر (eyeliner.py غير متاح).")
        return img

    eyes_payload = eyes_payload or {}
    result, chosen_style = apply_experta_eyeliner_recommendation(
        image=img, landmarks=landmarks, face_scale=face_scale,
        experta_result=eyes_payload, input_data={"occasion": occasion},
    )
    print(f"✅ الآيلاينر -> Style: {chosen_style}")
    return result


def apply_lashes_from_json(img, landmarks, face_scale, eyes_payload, occasion):
    if apply_experta_lashes_recommendation is None:
        print("⚠️  تخطينا الرموش (lashes.py غير متاح).")
        return img

    eyes_payload = eyes_payload or {}
    result, chosen_style = apply_experta_lashes_recommendation(
        image=img, landmarks=landmarks, face_scale=face_scale,
        experta_result=eyes_payload, input_data={"occasion": occasion},
    )
    print(f"✅ الرموش -> Style: {chosen_style}")
    return result


def apply_lips_from_json(img, landmarks, face_scale, lips_json, shade_index=None):
    if apply_recommended_lip_makeup is None:
        print("⚠️ تخطينا الشفاه (lips.py غير متاح).")
        return img

    lips_json = lips_json or {}
    result = apply_recommended_lip_makeup(
        image=img, landmarks=landmarks, face_scale=face_scale,
        recommendation_json=lips_json, shade_index=shade_index
    )
    print("✅ الشفاه -> تم التطبيق بنجاح")
    return result
 
 
def make_it_realistic(original_img, makeup_img, detail_intensity=1.3, blend_mode="soft_light"):
  
    if original_img is None or makeup_img is None:
        return makeup_img
 
    orig_lab = cv2.cvtColor(original_img, cv2.COLOR_BGR2LAB)
    mkup_lab = cv2.cvtColor(makeup_img, cv2.COLOR_BGR2LAB)
 
    orig_l, orig_a, orig_b = cv2.split(orig_lab)
    mkup_l, mkup_a, mkup_b = cv2.split(mkup_lab)
 
    blurred_orig_l = cv2.GaussianBlur(orig_l, (7, 7), 0)
    high_pass_details = cv2.subtract(orig_l, blurred_orig_l)
    enhanced_l = cv2.addWeighted(mkup_l, 1.0, high_pass_details, detail_intensity, 0)
 
    realistic_lab = cv2.merge([enhanced_l, mkup_a, mkup_b])
    realistic_bgr = cv2.cvtColor(realistic_lab, cv2.COLOR_LAB2BGR)
 
    base_f = original_img.astype(float) / 255.0
    mkup_f = realistic_bgr.astype(float) / 255.0
 
    res = np.where(
        mkup_f <= 0.5,
        base_f - (1.0 - 2.0 * mkup_f) * base_f * (1.0 - base_f),
        base_f + (2.0 * mkup_f - 1.0) * (np.sqrt(base_f) - base_f),
    )
    soft_blended = np.uint8(np.clip(res * 255.0, 0, 255))
    final_magic = cv2.addWeighted(realistic_bgr, 0.65, soft_blended, 0.35, 0)
    return final_magic
 
 
def run_full_makeup(img_bgr, makeup_json_data):
    landmarks, face_scale, h, w = get_landmarks(img_bgr)
    if landmarks is None:
        return None, None, None, " لم يتم التعرف على وجه بالصورة! جربي صورة أوضح وواجهة كاملة للوجه."
 
    expert_output = (
        makeup_json_data.get("expert_output")
        or makeup_json_data.get("expert_recommendations")
        or makeup_json_data
    )
    foundation_json = expert_output.get("foundation", {})
    nose_json = expert_output.get("nose", {})
    face_json = expert_output.get("face", {})
    brows_json = expert_output.get("brows", {})
    lips_json = expert_output.get("lips", {})
    eyes_expert = expert_output.get("eyes", {})
    eyes_payload = {"expert_output": {"eyes": eyes_expert}}
    occasion = makeup_json_data.get("occasion", "work")
 
    img_cur = img_bgr.copy()
    try:
        img_cur = apply_foundation_from_json(img_cur, landmarks, face_scale, foundation_json)
        img_cur = apply_concealer_from_json(img_cur, landmarks, face_scale, foundation_json)
        img_cur = apply_face_sculpt_from_json(img_cur, landmarks, face_scale, face_json)
        img_cur = apply_face_highlight_from_json(img_cur, landmarks, face_scale, face_json)
        img_cur = apply_nose_from_json(img_cur, landmarks, face_scale, nose_json)
        img_cur = apply_blush_from_json(img_cur, landmarks, face_scale, makeup_json_data, expert_output, face_json)
        img_cur = apply_brows_from_json(img_cur, landmarks, face_scale, brows_json, face_json, occasion)
        img_cur = apply_eyeshadow_bridge(img_cur, landmarks, face_scale, makeup_json_data)
        img_cur = apply_eyeliner_from_json(img_cur, landmarks, face_scale, eyes_payload, occasion)
        img_cur = apply_lashes_from_json(img_cur, landmarks, face_scale, eyes_payload, occasion)
        img_cur = apply_lips_from_json(img_cur, landmarks, face_scale, lips_json)

    except Exception as e:
        print(f"  error: {e}")
        traceback.print_exc()
 
    final_realistic = make_it_realistic(img_bgr, img_cur)
 
    return final_realistic, landmarks, face_scale, "The step of putting makeup on your photo was successful"
 
 
 
def catalog_foundation(img, landmarks, face_scale, foundation_json):
    if render_foundation_engine_direct is None:
        return None
    shade_hex = (foundation_json.get("shade", {}) or {}).get("hex", "#C68C64")
    override_bgr = parse_foundation_color(shade_hex) if parse_foundation_color else hex_to_bgr(shade_hex)
    strategies = [
        ("Original", None),
        ("Satin / Medium", {"texture": "ساتان", "coverage": "متوسطة"}),
        ("Matte Finish", {"texture": "مطفأ", "coverage": "متوسطة"}),
        ("Dewy Glow", {"texture": "نضر ولامع بلطف", "coverage": "خفيفة"}),
        ("Full Coverage", {"texture": "ساتان", "coverage": "كاملة"}),
        ("Light Coverage", {"texture": "ساتان", "coverage": "خفيفة"}),
    ]
    tiles = []
    for title, strat in strategies:
        if strat is None:
            res = img.copy()
        else:
            res = _safe(title, render_foundation_engine_direct, img.copy(), landmarks,
                        {"formula": strat}, face_scale, override_bgr=override_bgr)
        tiles.append((title, res if res is not None else img.copy()))
    return build_grid(tiles, cols=3)
 
 
def catalog_concealer(img, landmarks, face_scale):
    if apply_concealer_layer is None:
        return None
    strategies = [
        ("Original", None),
        ("Fair - Light", ("Fair", "Light")),
        ("Fair - Full", ("Fair", "Full")),
        ("Medium - Light", ("Medium", "Light")),
        ("Medium - Full", ("Medium", "Full")),
        ("Peach Corrector", ("Dark", "Full")),
    ]
    tiles = []
    for title, strat in strategies:
        if strat is None:
            res = img.copy()
        else:
            depth, coverage = strat
            res = _safe(title, apply_concealer_layer, img.copy(), landmarks, face_scale,
                        depth=depth, coverage=coverage)
        tiles.append((title, res if res is not None else img.copy()))
    return build_grid(tiles, cols=3)
 
 
def catalog_contour(img, landmarks, face_scale, sculpt_json):
    if generate_contour_mask_realistic is None or apply_realistic_contour is None:
        return None
    sculpt_json = sculpt_json or {}
    hex_color = sculpt_json.get("hex", "#6E5D53")
    c_bgr = parse_contour_color(hex_color) if parse_contour_color else hex_to_bgr(hex_color)
    shapes = ["Oval", "Round", "Square", "Rectangular", "Heart"]
    tiles = [("Original", img.copy())]
    for shp in shapes:
        mask = _safe(shp, generate_contour_mask_realistic, img, landmarks, face_scale,
                     shape_type=shp, fullness="Full", sculpt_json=sculpt_json)
        if mask is None:
            tiles.append((shp, img.copy()))
            continue
        res = _safe(shp, apply_realistic_contour, img.copy(), mask, c_bgr, opacity=0.6)
        tiles.append((shp, res if res is not None else img.copy()))
    return build_grid(tiles, cols=3)
 
 
def catalog_highlight(img, landmarks, face_scale, highlight_json):
    if render_expert_highlight_pipeline is None:
        return None
    highlight_json = highlight_json or {}
    hex_color = highlight_json.get("hex", "#FFF8DC")
    variants = [
        ("Original", None, None),
        ("Cheekbones Only", "عظمة الخد", 50),
        ("Nose+Chin+Forehead", "الأنف الذقن الجبهة", 50),
        ("Subtle 30%", "عظمة الخد الأنف الذقن الجبهة", 30),
        ("Medium 65%", "عظمة الخد الأنف الذقن الجبهة", 65),
        ("Strong Glow 90%", "عظمة الخد الأنف الذقن الجبهة", 90),
    ]
    tiles = []
    for title, placement, op in variants:
        if placement is None:
            tiles.append((title, img.copy()))
            continue
        expert = {"highlight": {"placement": placement, "hex": hex_color, "opacity": op},
                  "texture": {"finish": "لامع"}}
        res = _safe(title, render_expert_highlight_pipeline, img.copy(), landmarks, expert, face_scale)
        tiles.append((title, res if res is not None else img.copy()))
    return build_grid(tiles, cols=3)
 
 
def catalog_nose(img, landmarks, face_scale):
    if render_nose_contour_advanced is None:
        return None
    styles = ["Wide", "Long", "Drooping", "Short", "Crooked"]
    tiles = [("Original", img.copy())]
    for st in styles:
        res = _safe(st, render_nose_contour_advanced, img.copy(), landmarks, face_scale, shape_style=st)
        tiles.append((st, res if res is not None else img.copy()))
    return build_grid(tiles, cols=3)
 
 
def catalog_blush(img, landmarks, face_scale):
    if render_blush_engine_perfect is None:
        return None
    strategies = ["Lifted_Temple", "Apples_Classic", "Draping_C_Shape", "Igari_UnderEye", "Sunkissed_W_Shape"]
    tiles = [("Original", img.copy())]
    for s in strategies:
        res = _safe(s, render_blush_engine_perfect, img.copy(), landmarks, face_scale, strategy=s)
        tiles.append((s.replace("_", " "), res if res is not None else img.copy()))
    return build_grid(tiles, cols=3)
 
 
def catalog_brows(img, landmarks, face_scale):
    if render_brow_engine_v13_2 is None:
        return None
    shapes = ["Round", "Square", "Oval", "Heart", "Rectangular"]
    tiles = [("Original", img.copy())]
    for shp in shapes:
        res = _safe(shp, render_brow_engine_v13_2, img.copy(), landmarks, face_scale,
                    shape_type=shp, occasion="work")
        tiles.append((shp, res if res is not None else img.copy()))
    return build_grid(tiles, cols=3)
 
 
def catalog_eyeshadow(img, landmarks, face_scale, full_json_data):
    if render_professional_makeup is None:
        return None
    palette_colors = None
    if full_json_data and full_json_data.get("eyeshadow_palettes"):
        pal = full_json_data["eyeshadow_palettes"]
        p_key = list(pal.keys())[0]
        palette_colors = {}
        for item in pal[p_key]:
            role = item.get("role")
            if "hex" in item:
                palette_colors[role] = item["hex"]
    if not palette_colors:
        default_name = list(SHADOW_PRESET_PALETTES.keys())[0] if SHADOW_PRESET_PALETTES else None
        palette_colors = SHADOW_PRESET_PALETTES.get(default_name, {
            "Base": "#E8A398", "Sculpt": "#8B3A62", "Highlight": "#FFD1DC", "Accent": "#C71585"
        })
    strategies = [
        ("Classic Eye", "Classic", "Classic"),
        ("Cut Crease", "Cut Crease", "floating cut crease"),
        ("Foxy / Wing Lift", "Illusion Lifting", "wing lifting"),
        ("Halo / Spotlight", "deep-set", "spotlight"),
    ]
    tiles = []
    for title, goal, style in strategies:
        mock_json = {
            "category": {"goal": goal},
            "plan": {"style": style},
            "eyeshadow_palettes": {"P": [
                {"role": "Base", "hex": palette_colors.get("Base", "#C8A48C")},
                {"role": "Sculpt", "hex": palette_colors.get("Sculpt", "#5C4033")},
                {"role": "Highlight", "hex": palette_colors.get("Highlight", "#FFF3E0")},
                {"role": "Accent", "hex": palette_colors.get("Accent", "#8B5E3C")},
            ]},
        }
        res = _safe(title, render_professional_makeup, img.copy(), landmarks, face_scale, mock_json)
        tiles.append((title, res if res is not None else img.copy()))
    return build_grid(tiles, cols=2)
 
 
def catalog_eyeliner(img, landmarks, face_scale):
    if generate_eyeliner_mask_advanced is None or apply_photorealistic_eyeliner is None:
        return None
    styles = ["Classic_Wing", "Battenberg_Hooded", "Siren_Puppy",
              "Fox_Inner_Corner", "Soft_Smudged", "Dramatic_Cat"]
    tiles = []
    for st in styles:
        mask = _safe(st, generate_eyeliner_mask_advanced, img.shape, landmarks, style=st, scale=face_scale)
        if mask is None:
            tiles.append((st.replace("_", " "), img.copy()))
            continue
        opacity = 0.65 if st == "Soft_Smudged" else 0.90
        res = _safe(st, apply_photorealistic_eyeliner, img.copy(), mask, color_bgr=(10, 10, 10), opacity=opacity)
        tiles.append((st.replace("_", " "), res if res is not None else img.copy()))
    return build_grid(tiles, cols=3)
 
 
def catalog_lashes(img, landmarks, face_scale):
    if generate_lashes_overlay_rgba is None or apply_photorealistic_lashes_correct is None:
        return None
    styles = ["Natural_Everyday", "Cat_Eye_Outer_Volume", "Doll_Center_Volume",
              "Dramatic_3D_Volume", "Wispy_Manga"]
    tiles = [("Original", img.copy())]
    for st in styles:
        overlay = _safe(st, generate_lashes_overlay_rgba, img.shape, landmarks, style=st, scale=face_scale)
        if overlay is None:
            tiles.append((st.replace("_", " "), img.copy()))
            continue
        res = _safe(st, apply_photorealistic_lashes_correct, img.copy(), overlay)
        tiles.append((st.replace("_", " "), res if res is not None else img.copy()))
    return build_grid(tiles, cols=3)
 
import re

def clean_title(text):
    if not text:
        return "Style"
    english_part = re.sub(r'[^\x00-\x7F]+', '', str(text)).strip()
    return english_part if english_part else "Option"

def catalog_lips(img, landmarks, face_scale, lips_json):
    if render_lips_engine is None:
        return None

    lips_json = lips_json or {}

    if "expert_recommendations" in lips_json:
        lips_data = lips_json["expert_recommendations"].get("lips", {})
    elif "lips" in lips_json:
        lips_data = lips_json["lips"]
    else:
        lips_data = lips_json

    color_obj = lips_data.get("color", {}) if isinstance(lips_data.get("color"), dict) else {}
    shades = color_obj.get("lipstick_shades", [])
    
    if shades and "rgb" in shades[0]:
        rgb = shades[0]["rgb"]
    else:
        rgb = [255, 127, 80]
        
    lip_bgr = (rgb[2], rgb[1], rgb[0])
    
    liners = color_obj.get("lip_liners", [])
    liner_info = liners[0] if liners else None

    lip_strategies = [
        ("Full & Balanced", "Full & Balanced"),
        ("Overline Full", "Overline Full"),
        ("Upper Overline", "Upper Overline"),
        ("Lower Overline", "Lower Overline"),
        ("Inline Minimizing", "Inline (Minimizing)")
    ]

    tiles = [("Original", img.copy())]

    for display_title, shape_category in lip_strategies:
        safe_title = clean_title(display_title)
        
        res = _safe(
            safe_title, 
            render_lips_engine, 
            image=img.copy(), 
            landmarks=landmarks, 
            shape_category=shape_category, 
            lip_bgr=lip_bgr, 
            face_scale=face_scale, 
            opacity=0.85,
            liner_info=liner_info,
            is_glossy=True
        )
        
        tiles.append((safe_title, res if res is not None else img.copy()))

    return build_grid(tiles, cols=3)
 
CATEGORY_LABELS = [
    " فاونديشن",
    " كونسيلر",
    " نحت الوجه",
    " هايلايتر",
    " الأنف",
    " بلاش",
    " حواجب",
    " ظلال العيون",
    " آيلاينر",
    " رموش",
    " شفاه",
]


def generate_recommendations_html(results):
    if not results:
        return "<p style='text-align:center; color:#888;'>لا توجد توصيات متاحة حالياً.</p>"
    html = '<div class="product-scroll-container">'
    for category, products in results.items():
        if not products:
            continue
        for prod in products:
            if not prod or not isinstance(prod, dict):
                continue
            brand_val = prod.get("brand") or ""
            brand = brand_val.upper()
            name = prod.get("name") or "منتج مكياج"
            price = prod.get("price") or ""
            shade_name = (
                prod.get("matched_shade_name")
                or prod.get("recommended_shade_target")
                or ""
            )
            shade_hex = prod.get("matched_shade_hex") or "#ffffff"
            img_src = (
                prod.get("image_link")
                or "https://via.placeholder.com/150?text=No+Image"
            )
            buy_link = prod.get("product_link") or "#"
            html += f"""
            <div class="product-card">
                <img src="{img_src}" class="product-img" alt="{name}" onerror="this.src='https://via.placeholder.com/150?text=No+Image'">
                <div class="product-info-body">
                    <span class="product-brand">{brand}</span>
                    <div class="product-title" title="{name}">{name}</div>
                    {f'<div class="product-shade"><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background-color:{shade_hex};margin-right:4px;"></span>{shade_name}</div>' if shade_name else ''}
                    <div class="product-price">{price}</div>
                </div>
                <a href="{buy_link}" target="_blank" class="buy-btn">عرض المنتج 🛍️</a>
            </div>
            """
    html += "</div>"
    return html



import os
import tempfile
import cv2
import gradio as gr

CATEGORY_LABELS = [
    "Foundation",
    "Concealer",
    "Contour",
    "Highlighter",
    "Nose",
    "Blush",
    "Brows",
    "Eyeshadow",
    "Eyeliner",
    "Lashes",
    "Lips",
]

def generate_recommendations_html(results):
    if not results:
        return "<p style='text-align:center; color:#888;'>No recommendations available at the moment.</p>"
    
    html = '<div class="product-scroll-container">'
    for category, products in results.items():
        if not products:
            continue
        for prod in products:
            if not prod or not isinstance(prod, dict):
                continue
            brand_val = prod.get("brand") or ""
            brand = brand_val.upper()
            name = prod.get("name") or "Makeup Product"
            price = prod.get("price") or ""
            shade_name = (
                prod.get("matched_shade_name") or prod.get("recommended_shade_target") or ""
            )
            shade_hex = prod.get("matched_shade_hex") or "#ffffff"
            img_src = (
                prod.get("image_link") or "https://via.placeholder.com/150?text=No+Image"
            )
            buy_link = prod.get("product_link") or "#"
            
            html += f"""
            <div class="product-card">
                <img src="{img_src}" class="product-img" alt="{name}" onerror="this.src='https://via.placeholder.com/150?text=No+Image'">
                <div class="product-info-body">
                    <span class="product-brand">{brand}</span>
                    <div class="product-title" title="{name}">{name}</div>
                    {f'<div class="product-shade"><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background-color:{shade_hex};margin-right:4px;"></span>{shade_name}</div>' if shade_name else ''}
                    <div class="product-price">{price}</div>
                </div>
                <a href="{buy_link}" target="_blank" class="buy-btn">View Product 🛍️</a>
            </div>
            """
    html += "</div>"
    return html

CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&display=swap');

body, .gradio-container {
    background: linear-gradient(135deg, #fffafc 0%, #fef5f8 100%) !important;
    font-family: 'Poppins', 'Segoe UI', Tahoma, sans-serif !important;
}

h1, h2 {
    color: #d87093 !important;
    text-align: center !important;
    font-weight: 800 !important;
}

p {
    color: #888 !important;
}

/* ===== Catalog Tabs Color Adjustment ===== */
div.tabs button, .gradio-container .tabs button, .tabs button {
    color: #d87093 !important; /* Pink Color */
    opacity: 0.85 !important;
    font-size: 14px !important;
    font-weight: 600 !important;
}

div.tabs button.selected, .gradio-container .tabs button.selected, .tabs button.selected {
    color: #d87093 !important; /* Vibrant Pink on Active Selection */
    opacity: 1 !important;
    border-bottom: 3px solid #d87093 !important;
    font-weight: 800 !important;
}

button.primary-btn, .primary {
    background: linear-gradient(45deg, #ff8da1, #d87093) !important;
    border: none !important;
    color: white !important;
    font-weight: bold !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 12px rgba(216, 112, 147, 0.3) !important;
    transition: all 0.25s ease !important;
}

button.primary-btn:hover, .primary:hover {
    background: linear-gradient(45deg, #d87093, #ff8da1) !important;
    box-shadow: 0 6px 16px rgba(216, 112, 147, 0.45) !important;
    transform: translateY(-1px) scale(1.01) !important;
}

/* ===== Notebook Style ===== */
.notebook-page {
    position: relative !important;
    background: repeating-linear-gradient(#fffdfb 0px, #fffdfb 33px, #ffeef3 34px) !important;
    border: 1px solid #f3d5e0 !important;
    border-radius: 4px 18px 18px 4px !important;
    padding: 22px 26px 26px 42px !important;
    margin-top: 16px !important;
    box-shadow: 0 10px 30px rgba(216, 112, 147, 0.18), 0 2px 6px rgba(0,0,0,0.04) !important;
}

.notebook-page::before {
    content: "" !important;
    position: absolute !important;
    top: 14px;
    bottom: 14px;
    left: 10px !important;
    width: 14px !important;
    background-image: radial-gradient(circle, #f6c3d3 3px, transparent 3.5px) !important;
    background-size: 14px 22px !important;
    background-repeat: repeat-y !important;
    opacity: 0.9 !important;
}

/* ===== Product Cards (Horizontal Scroll) ===== */
.product-scroll-container {
    display: flex !important;
    gap: 16px !important;
    overflow-x: auto !important;
    padding: 8px 4px 16px 4px !important;
    scroll-behavior: smooth !important;
}

.product-card {
    min-width: 195px !important;
    max-width: 195px !important;
    background: #ffffff !important;
    border: 1px solid #f3d5e0 !important;
    border-radius: 14px !important;
    padding: 12px !important;
    text-align: center !important;
    box-shadow: 0 4px 12px rgba(216, 112, 147, 0.08) !important;
    transition: transform 0.25s ease, box-shadow 0.25s ease !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: space-between !important;
}

.product-card:hover {
    transform: translateY(-4px) !important;
    box-shadow: 0 8px 20px rgba(216, 112, 147, 0.2) !important;
}

.product-img {
    width: 100% !important;
    height: 120px !important;
    object-fit: contain !important;
    border-radius: 8px !important;
    margin-bottom: 8px !important;
    background-color: #fafafa !important;
}

.product-info-body {
    flex-grow: 1 !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
}

.product-brand {
    font-size: 11px !important;
    color: #d87093 !important;
    font-weight: 800 !important;
    letter-spacing: 0.5px !important;
}

.product-title {
    font-size: 12px !important;
    font-weight: 700 !important;
    color: #333 !important;
    margin: 4px 0 !important;
    line-height: 1.3 !important;
    height: 32px !important;
    overflow: hidden !important;
    display: -webkit-box !important;
    -webkit-line-clamp: 2 !important;
    -webkit-box-orient: vertical !important;
}

.product-shade {
    font-size: 11px !important;
    color: #666 !important;
    background: #fff0f5 !important;
    padding: 3px 8px !important;
    border-radius: 6px !important;
    display: inline-block !important;
    margin: 4px auto !important;
}

.product-price {
    font-weight: 800 !important;
    color: #2e7d32 !important;
    font-size: 13px !important;
    margin: 4px 0 !important;
}

.buy-btn {
    display: block !important;
    background: linear-gradient(45deg, #ff8da1, #d87093) !important;
    color: white !important;
    text-decoration: none !important;
    padding: 7px 10px !important;
    border-radius: 8px !important;
    font-size: 12px !important;
    font-weight: bold !important;
    margin-top: 8px !important;
    transition: opacity 0.2s !important;
}

.buy-btn:hover {
    opacity: 0.9 !important;
}

footer {
    display: none !important;
}
"""

def process_new_inputs_and_get_json(face_image_rgb, clothes_image_rgb, occasion):
    temp_dir = tempfile.gettempdir()
    
    # 1. Save temporary face image
    temp_face_path = os.path.join(temp_dir, "temp_face_input.jpg")
    img_face_bgr = cv2.cvtColor(face_image_rgb, cv2.COLOR_RGB2BGR)
    cv2.imwrite(temp_face_path, img_face_bgr)
    
    # 2. Save temporary clothing image
    temp_clothes_path = None
    if clothes_image_rgb is not None:
        temp_clothes_path = os.path.join(temp_dir, "temp_clothes_input.jpg")
        img_clothes_bgr = cv2.cvtColor(clothes_image_rgb, cv2.COLOR_RGB2BGR)
        cv2.imwrite(temp_clothes_path, img_clothes_bgr)
        
    # 3. Run analysis script
    output_json_path = os.path.join(temp_dir, "temp_makeup_analysis.json")
    results = analyze_image(
        face_image_path=temp_face_path,
        clothing_image_path=temp_clothes_path,
        occasion=occasion,
        output_json=output_json_path,
        print_report=False
    )
    return results, output_json_path

def handle_apply(face_image_rgb, clothes_image_rgb, occasion_input):
    if face_image_rgb is None:
        return (
            None, None, "Please upload a face image first! 🌸", None, None, "", gr.update(visible=False)
        )
    try:
        makeup_json_data, json_path = process_new_inputs_and_get_json(
            face_image_rgb, clothes_image_rgb, occasion_input
        )
        if not makeup_json_data:
            return (
                face_image_rgb, None, "❌ Face analysis failed! Ensure the face is clearly visible in the photo.", None, None, "", gr.update(visible=False)
            )
        json_msg = f"✓ Face & outfit image successfully analyzed for occasion: ({occasion_input})!"
    except Exception as e:
        return (
            face_image_rgb, None, f"❌ Error during execution: {str(e)}", None, None, "", gr.update(visible=False)
        )
        
    img_bgr = cv2.cvtColor(face_image_rgb, cv2.COLOR_RGB2BGR)
    final_bgr, landmarks, face_scale, status = run_full_makeup(
        img_bgr, makeup_json_data
    )
    if final_bgr is None:
        return face_image_rgb, None, status, None, None, "", gr.update(visible=False)
        
    before_rgb = face_image_rgb
    after_rgb = cv2.cvtColor(final_bgr, cv2.COLOR_BGR2RGB)
    full_status = f"{status}\n{json_msg}"
    
    try:
        matcher = DynamicMakeupMatcher(
            analysis_json_path=json_path, dataset_json_path="makeup_data.json"
        )
        results = matcher.get_recommendations(top_n_per_category=3)
        recom_html = generate_recommendations_html(results)
    except Exception as e:
        recom_html = f"<p>Unable to load recommendations: {e}</p>"
        
    return (
        before_rgb,
        after_rgb,
        full_status,
        img_bgr,
        makeup_json_data,
        recom_html,
        gr.update(visible=True),
    )

def handle_catalog(img_bgr_state, json_state):
    n = len(CATEGORY_LABELS)
    if img_bgr_state is None:
        yield (
            gr.update(visible=True),
            *[gr.update() for _ in range(n)],
            "🌸 Please upload your photo and apply makeup first!",
        )
        return
        
    makeup_json_data = json_state or {}
    landmarks, face_scale, h, w = get_landmarks(img_bgr_state)
    if landmarks is None:
        yield (
            gr.update(visible=True),
            *[gr.update() for _ in range(n)],
            "❌ Facial landmarks could not be detected to generate the catalog.",
        )
        return
        
    expert_output = (
        makeup_json_data.get("expert_output") or makeup_json_data.get("expert_recommendations") or makeup_json_data
    )
    foundation_json = expert_output.get("foundation", {})
    face_json = expert_output.get("face", {})
    lips_json = expert_output.get("lips", {})
    
    generators = [
        ("Foundation", lambda: catalog_foundation(img_bgr_state, landmarks, face_scale, foundation_json)),
        ("Concealer", lambda: catalog_concealer(img_bgr_state, landmarks, face_scale)),
        ("Contour", lambda: catalog_contour(img_bgr_state, landmarks, face_scale, face_json.get("sculpt", {}))),
        ("Highlighter", lambda: catalog_highlight(img_bgr_state, landmarks, face_scale, face_json.get("highlight", {}))),
        ("Nose", lambda: catalog_nose(img_bgr_state, landmarks, face_scale)),
        ("Blush", lambda: catalog_blush(img_bgr_state, landmarks, face_scale)),
        ("Brows", lambda: catalog_brows(img_bgr_state, landmarks, face_scale)),
        ("Eyeshadow", lambda: catalog_eyeshadow(img_bgr_state, landmarks, face_scale, makeup_json_data)),
        ("Eyeliner", lambda: catalog_eyeliner(img_bgr_state, landmarks, face_scale)),
        ("Lashes", lambda: catalog_lashes(img_bgr_state, landmarks, face_scale)),
        ("Lips", lambda: catalog_lips(img_bgr_state, landmarks, face_scale, lips_json)),
    ]
    
    results = [gr.update() for _ in range(n)]
    yield (
        gr.update(visible=True),
        *results,
        "⏳ Preparing the complete educational catalog...",
    )
    
    for idx, (name, fn) in enumerate(generators):
        grid = fn()
        results[idx] = gr.update(value=grid) if grid is not None else gr.update()
        status_msg = f"⏳ Generated: {name} ({idx + 1}/{n})..."
        yield (gr.update(visible=True), *results, status_msg)
        
    yield (gr.update(visible=True), *results, "✨ Catalog is fully generated and ready to view!")

with gr.Blocks(title="AI Makeup Application & Recommendations", css=CUSTOM_CSS) as demo:
    gr.Markdown("<h1>Smart Makeup Application & Personalized Recommendations</h1>")
    gr.Markdown(
        "<p style='text-align:center; color:#666;'>"
        "Upload your face and outfit photo, and select an occasion to get a custom analysis and personalized makeup!"
        "</p>"
    )
    
    img_state = gr.State(None)
    json_state = gr.State(None)
    
    with gr.Row():
        with gr.Column(scale=1):
            img_input = gr.Image(type="numpy", label="📷 Face Photo")
            clothes_input = gr.Image(type="numpy", label="👗 Outfit Photo (Optional)")
            occasion_dropdown = gr.Dropdown(
                choices=[
                    ("Evening / Dinner", "evening"),
                    ("University / Study", "university"),
                    ("Work / Office", "work"),
                    ("Party", "party"),
                    ("Wedding", "wedding"),
                    ("Photo Shoot", "photo"),
                ],
                value="evening",
                label="🎉 Occasion",
                interactive=True
            )
            btn_apply = gr.Button(
                "✨ Apply Full Makeup", variant="primary", elem_classes=["primary-btn"]
            )
            status_box = gr.Textbox(label="Status", interactive=False, lines=3)
            btn_catalog = gr.Button("📖 Open Educational Catalog", elem_classes=["primary-btn"])
            
        with gr.Column(scale=2):
            with gr.Row():
                img_before = gr.Image(label="Before")
                img_after = gr.Image(label="After")
                
            with gr.Column(visible=False, elem_classes=["notebook-page"]) as recom_section:
                gr.Markdown("## 🛍️ Recommended Products For Your Look")
                recom_html_box = gr.HTML()
                
            with gr.Column(visible=False, elem_classes=["notebook-page"]) as catalog_section:
                gr.Markdown("## 📖 Educational Catalog — Strategies Breakdown")
                catalog_status = gr.Textbox(label="", interactive=False, show_label=False)
                
                with gr.Tabs():
                    with gr.Tab(CATEGORY_LABELS[0]):
                        grid_foundation = gr.Image(label="Foundation Strategies")
                    with gr.Tab(CATEGORY_LABELS[1]):
                        grid_concealer = gr.Image(label="Concealer Strategies")
                    with gr.Tab(CATEGORY_LABELS[2]):
                        grid_contour = gr.Image(label="Contour / Sculpt Strategies")
                    with gr.Tab(CATEGORY_LABELS[3]):
                        grid_highlight = gr.Image(label="Highlight Strategies")
                    with gr.Tab(CATEGORY_LABELS[4]):
                        grid_nose = gr.Image(label="Nose Contour Strategies")
                    with gr.Tab(CATEGORY_LABELS[5]):
                        grid_blush = gr.Image(label="Blush Strategies")
                    with gr.Tab(CATEGORY_LABELS[6]):
                        grid_brows = gr.Image(label="Brow Strategies")
                    with gr.Tab(CATEGORY_LABELS[7]):
                        grid_eyeshadow = gr.Image(label="Eyeshadow Strategies")
                    with gr.Tab(CATEGORY_LABELS[8]):
                        grid_eyeliner = gr.Image(label="Eyeliner Strategies")
                    with gr.Tab(CATEGORY_LABELS[9]):
                        grid_lashes = gr.Image(label="Lashes Strategies")
                    with gr.Tab(CATEGORY_LABELS[10]):
                        grid_lips = gr.Image(label="Lips Strategies")

    btn_apply.click(
        fn=handle_apply,
        inputs=[img_input, clothes_input, occasion_dropdown],
        outputs=[
            img_before,
            img_after,
            status_box,
            img_state,
            json_state,
            recom_html_box,
            recom_section,
        ],
    )
    
    btn_catalog.click(
        fn=handle_catalog,
        inputs=[img_state, json_state],
        outputs=[
            catalog_section,
            grid_foundation,
            grid_concealer,
            grid_contour,
            grid_highlight,
            grid_nose,
            grid_blush,
            grid_brows,
            grid_eyeshadow,
            grid_eyeliner,
            grid_lashes,
            grid_lips,
            catalog_status,
        ],
    )

if __name__ == "__main__":
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        inbrowser=True,
        show_error=True,
        theme=gr.themes.Soft()
    )