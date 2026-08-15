# -*- coding: utf-8 -*-

import os
import sys

import cv2
import numpy as np
import mediapipe as mp
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from scipy.interpolate import splprep, splev

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from eye_makeup_rules import EyeMakeupEngine
except ImportError:
    EyeMakeupEngine = None

try:
    import compat_fix
except ImportError:
    import collections
    import collections.abc
    for item in ['MutableMapping', 'MutableSequence', 'MutableSet', 'Mapping', 'Sequence', 'Set']:
        if not hasattr(collections, item) and hasattr(collections.abc, item):
            setattr(collections, item, getattr(collections.abc, item))

from experta import *
import json


LEFT_TOP_LASH = [362, 398, 384, 385, 386, 387, 388, 466, 263]
RIGHT_TOP_LASH = [133, 173, 157, 158, 159, 160, 161, 246, 33]

LEFT_EYE_FULL_CONTOUR = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
RIGHT_EYE_FULL_CONTOUR = [263, 249, 390, 373, 374, 380, 381, 382, 362, 398, 384, 385, 386, 387, 388, 466]


def get_smooth_polyline(pts, num_samples=50):

    if len(pts) < 3:
        return pts
    pts_arr = np.array(pts, dtype=np.float32)
    
    _, idx = np.unique(pts_arr, axis=0, return_index=True)
    pts_arr = pts_arr[np.sort(idx)]

    try:
        tck, _ = splprep([pts_arr[:, 0], pts_arr[:, 1]], s=0.5, k=min(2, len(pts_arr)-1))
        u_new = np.linspace(0, 1, num_samples)
        x_new, y_new = splev(u_new, tck)
        return np.column_stack((x_new, y_new)).astype(np.int32)
    except Exception:
        return pts_arr.astype(np.int32)


def get_eye_exclusion_mask(image_shape, landmarks):
 
    h, w = image_shape[:2]
    eye_mask = np.zeros((h, w), dtype=np.uint8)

    for contour_indices in [LEFT_EYE_FULL_CONTOUR, RIGHT_EYE_FULL_CONTOUR]:
        pts = np.array([[int(landmarks[i].x * w), int(landmarks[i].y * h)] for i in contour_indices], dtype=np.int32)
        cv2.fillPoly(eye_mask, [pts], 255)

    return eye_mask


def generate_eyeliner_mask_advanced(image_shape, landmarks, style="Classic_Wing", scale=100.0):
    h, w = image_shape[:2]
    mask = np.zeros((h, w), dtype=np.float32)

    eyes_data = [
        (LEFT_TOP_LASH, 263, 362, True),  
        (RIGHT_TOP_LASH, 33, 133, False)  
    ]

    base_thickness = max(1, int(scale * 0.010))

    for lash_indices, outer_idx, inner_idx, is_left in eyes_data:
        lash_pts = np.array([[int(landmarks[i].x * w), int(landmarks[i].y * h)] for i in lash_indices])
        
        outer_pt = np.array([landmarks[outer_idx].x * w, landmarks[outer_idx].y * h])
        inner_pt = np.array([landmarks[inner_idx].x * w, landmarks[inner_idx].y * h])

        eye_dir = outer_pt - inner_pt
        eye_len = np.linalg.norm(eye_dir)
        unit_dir = eye_dir / (eye_len + 1e-6)
        
        perp_up = np.array([-unit_dir[1], unit_dir[0]]) if is_left else np.array([unit_dir[1], -unit_dir[0]])
        if perp_up[1] > 0:
            perp_up = -perp_up

        smooth_lash = get_smooth_polyline(lash_pts, num_samples=60)
        single_eye_mask = np.zeros((h, w), dtype=np.uint8)

        if style == "Soft_Smudged":

            smudge_thickness = max(5, int(base_thickness * 4.5))
            cv2.polylines(single_eye_mask, [smooth_lash], isClosed=False, color=255, thickness=smudge_thickness)

            wing_len = eye_len * 0.35
            wing_tip = outer_pt + (unit_dir * wing_len) + (perp_up * (wing_len * 0.30))
            smudge_top = outer_pt + (perp_up * (wing_len * 0.40))
            connect_pt = lash_pts[-5]

            poly = np.array([outer_pt, smudge_top, wing_tip, connect_pt], dtype=np.int32)
            cv2.fillPoly(single_eye_mask, [poly], 255)

        else:
       
            cv2.polylines(single_eye_mask, [smooth_lash], isClosed=False, color=255, thickness=base_thickness)

            if style == "Battenberg_Hooded":
                wing_len = eye_len * 0.28
                wing_tip = outer_pt + (unit_dir * wing_len) + (perp_up * (wing_len * 0.12))
                elbow_pt = outer_pt + (unit_dir * (wing_len * 0.55)) + (perp_up * (wing_len * 0.38))
                connect_pt = lash_pts[-3]
                poly = np.array([outer_pt, wing_tip, elbow_pt, connect_pt], dtype=np.int32)
                cv2.fillPoly(single_eye_mask, [poly], 255)

            elif style == "Siren_Puppy":
                wing_len = eye_len * 0.40
                wing_tip = outer_pt + (unit_dir * wing_len) + (perp_up * (wing_len * 0.05))
                connect_pt = lash_pts[-4]
                poly = np.array([outer_pt, wing_tip, connect_pt], dtype=np.int32)
                cv2.fillPoly(single_eye_mask, [poly], 255)

            elif style == "Fox_Inner_Corner":
                wing_len = eye_len * 0.32
                wing_tip = outer_pt + (unit_dir * wing_len) + (perp_up * (wing_len * 0.28))
                connect_pt = lash_pts[-4]
                poly_outer = np.array([outer_pt, wing_tip, connect_pt], dtype=np.int32)
                cv2.fillPoly(single_eye_mask, [poly_outer], 255)

                inner_dir = -unit_dir
                inner_wing_tip = inner_pt + (inner_dir * (eye_len * 0.10))
                inner_connect_top = lash_pts[0]
                poly_inner = np.array([inner_pt, inner_wing_tip, inner_connect_top], dtype=np.int32)
                cv2.fillPoly(single_eye_mask, [poly_inner], 255)

            elif style == "Dramatic_Cat":
                wing_len = eye_len * 0.48
                wing_tip = outer_pt + (unit_dir * wing_len) + (perp_up * (wing_len * 0.45))
                connect_pt = lash_pts[-5]
                poly = np.array([outer_pt, wing_tip, connect_pt], dtype=np.int32)
                cv2.fillPoly(single_eye_mask, [poly], 255)

            elif style == "Natural_Tightline":
                cv2.polylines(single_eye_mask, [smooth_lash], isClosed=False, color=255, thickness=max(1, base_thickness // 2))

            elif style == "Classic_Wing":
                wing_len = eye_len * 0.30
                wing_tip = outer_pt + (unit_dir * wing_len) + (perp_up * (wing_len * 0.35))
                connect_pt = lash_pts[-4]
                poly = np.array([outer_pt, wing_tip, connect_pt], dtype=np.int32)
                cv2.fillPoly(single_eye_mask, [poly], 255)

        if style == "Soft_Smudged":
            blur_k = max(17, int(scale * 0.070) | 1) 
        else:
            blur_k = max(3, int(scale * 0.012) | 1)

        soft_mask = cv2.GaussianBlur(single_eye_mask.astype(np.float32) / 255.0, (blur_k, blur_k), 0)
        mask = np.maximum(mask, soft_mask)

    eye_exclusion = get_eye_exclusion_mask(image_shape, landmarks)
    mask[eye_exclusion > 0] = 0.0

    return np.clip(mask, 0, 1.0)



def apply_photorealistic_eyeliner(image, mask, color_bgr=(15, 15, 15), opacity=0.88):
    base = image.astype(np.float32) / 255.0
    pigment = np.full_like(base, np.array(color_bgr, dtype=np.float32) / 255.0)

    blended = base * pigment * 1.15
    alpha = (mask * opacity)[:, :, np.newaxis]
    result = (1.0 - alpha) * base + alpha * blended

    return np.clip(result * 255.0, 0, 255).astype(np.uint8)


def apply_experta_eyeliner_recommendation(image, landmarks, face_scale, experta_result, input_data=None):
    plan = {}
    category_data = {}
    
    if "expert_output" in experta_result:
        eyes = experta_result.get("expert_output", {}).get("eyes", {})
    
        eye_info = eyes.get("left") or eyes.get("right") or {}
        plan = eye_info.get("plan", {})
        category_data = eye_info.get("category", {})
    else:
        plan = experta_result.get('plan', {})
        category_data = experta_result.get('category', {})

    eyeliner_rec = plan.get('eyeliner', '').strip()
    eye_category = category_data.get('category', 'Almond').strip()
    
    occasion = "work"
    if input_data and "occasion" in input_data:
        occasion = str(input_data["occasion"]).strip().lower()

    chosen_style = None
    if "حريري" in eyeliner_rec or "سائل" in eyeliner_rec:
        if eye_category == "Hooded":
            chosen_style = "Battenberg_Hooded"
        elif eye_category == "Droopy":
            chosen_style = "Siren_Puppy"
        else:
            chosen_style = "Classic_Wing" if occasion in ["work", "university"] else "Dramatic_Cat"
    elif "مدمج" in eyeliner_rec:
        chosen_style = "Soft_Smudged"
    elif "بني" in eyeliner_rec or "جاف" in eyeliner_rec:
        chosen_style = "Natural_Tightline"

    if not chosen_style:
        style_map = {
            "Hooded": {"work": "Battenberg_Hooded", "university": "Battenberg_Hooded", "evening": "Dramatic_Cat", "party": "Dramatic_Cat", "photo": "Battenberg_Hooded", "wedding": "Battenberg_Hooded"},
            "Protruding": {"work": "Soft_Smudged", "university": "Soft_Smudged", "evening": "Dramatic_Cat", "party": "Dramatic_Cat", "photo": "Soft_Smudged", "wedding": "Soft_Smudged"},
            "Droopy": {"work": "Siren_Puppy", "university": "Siren_Puppy", "evening": "Dramatic_Cat", "party": "Dramatic_Cat", "photo": "Siren_Puppy", "wedding": "Dramatic_Cat"},
            "Deep-set": {"work": "Natural_Tightline", "university": "Natural_Tightline", "evening": "Soft_Smudged", "party": "Soft_Smudged", "photo": "Soft_Smudged", "wedding": "Soft_Smudged"},
            "Almond": {"work": "Natural_Tightline", "university": "Natural_Tightline", "evening": "Dramatic_Cat", "party": "Dramatic_Cat", "photo": "Classic_Wing", "wedding": "Classic_Wing"},
            "Round": {"work": "Classic_Wing", "university": "Classic_Wing", "evening": "Dramatic_Cat", "party": "Dramatic_Cat", "photo": "Classic_Wing", "wedding": "Classic_Wing"},
        }
        chosen_style = style_map.get(eye_category, style_map["Almond"]).get(occasion, "Classic_Wing")

    if chosen_style == "Soft_Smudged":
        color_bgr = (20, 20, 25)
        opacity = 0.65
    elif "بني" in eyeliner_rec or chosen_style == "Natural_Tightline":
        color_bgr = (25, 38, 55)  
        opacity = 0.70
    elif "حريري" in eyeliner_rec or "سائل" in eyeliner_rec or chosen_style in ["Dramatic_Cat", "Classic_Wing"]:
        color_bgr = (5, 5, 5)    
        opacity = 0.92
    else:
        color_bgr = (15, 15, 15)
        opacity = 0.80

    print(f" [Experta Eyeliner Bridge] النص من القواعد: '{eyeliner_rec}' | النمط المطبق: '{chosen_style}'")

    mask = generate_eyeliner_mask_advanced(image.shape, landmarks, style=chosen_style, scale=face_scale)
    result = apply_photorealistic_eyeliner(image, mask, color_bgr=color_bgr, opacity=opacity)
    return result, chosen_style


if __name__ == "__main__":
    try:
        with open("makeup_analysis.json", "r", encoding="utf-8") as f:
            input_data = json.load(f)
    except Exception as e:
        print(f" خطأ في قراءة ملف JSON: {e}")
        input_data = {
            'geo_shape': 'Almond',
            'eye_type': 'Hooded',
            'inter_eye_ratio': 0.35,
            'occasion': 'evening'
        }

    try:
        if EyeMakeupEngine is not None:
            engine = EyeMakeupEngine()
            experta_result = engine.analyze_eye(input_data)
            print(" تم الحصول على نتيجة Experta بنجاح:")
        else:
            raise ImportError("EyeMakeupEngine غير متاح")
    except Exception as e:
        print(f" يتعذر تحميل Experta مباشرة، يتم توليد خرج محاكاة ديناميكي: {e}")
        
        eye_type = input_data.get('eye_type', 'Default')
        ratio = input_data.get('inter_eye_ratio', 0.46)
        spacing_cls = 'Close-set' if ratio < 0.45 else ('Wide-set' if ratio > 0.48 else 'Normal')
        
        experta_result = {
            'category': {
                'category': eye_type,
                'name_ar': f"العين ({eye_type})"
            },
            'plan': {
                'style': 'سموكي درامي' if input_data.get('occasion') == 'evening' else 'مكياج ناعم يومي',
                'eyeliner': 'آيلاينر مدمج' if input_data.get('occasion') == 'evening' else 'آيلاينر رفيع'
            },
            'spacing': {
                'classification': spacing_cls
            }
        }

    print(f"الفئة: {experta_result['category']['name_ar']}")
    print(f"الأسلوب الموصى به: {experta_result['plan']['style']}")
    print(f"الآيلاينر الموصى به: {experta_result['plan']['eyeliner']}")
    print(f"تصنيف المسافة: {experta_result['spacing']['classification']}")

    image_path = "test5.jpg"
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
                scale = np.linalg.norm(pt1 - pt2)

                output_img, applied_style = apply_experta_eyeliner_recommendation(
                    img, 
                    landmarks, 
                    scale, 
                    experta_result, 
                    input_data=input_data
                )
                cv2.imwrite("experta_eyeliner_output.jpg", output_img)
                print(f" تم رسم وتطبيق الآيلاينر الموصى به ({applied_style}) وحفظه في: experta_eyeliner_output.jpg")

                styles = [
                    "Classic_Wing", 
                    "Battenberg_Hooded", 
                    "Siren_Puppy", 
                    "Fox_Inner_Corner", 
                    "Soft_Smudged", 
                    "Dramatic_Cat"
                ]

                fig, axes = plt.subplots(2, 3, figsize=(15, 9))
                axes = axes.ravel()

                for idx, st in enumerate(styles):
                    mask = generate_eyeliner_mask_advanced(img.shape, landmarks, style=st, scale=scale)
                    opacity = 0.65 if st == "Soft_Smudged" else 0.90
                    res = apply_photorealistic_eyeliner(img, mask, color_bgr=(10, 10, 10), opacity=opacity)
                    
                    axes[idx].imshow(cv2.cvtColor(res, cv2.COLOR_BGR2RGB))
                    axes[idx].set_title(f"Style: {st}", fontsize=11, fontweight='bold')
                    axes[idx].axis("off")

                plt.tight_layout()
                plt.show()

            else:
                print(" لم يتم العثور على وجه في الصورة.")
    else:
        print(f" لم يتم العثور على الصورة: {image_path}")