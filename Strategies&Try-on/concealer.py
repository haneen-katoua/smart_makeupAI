# -*- coding: utf-8 -*-

import os
import cv2
import json
import numpy as np
import mediapipe as mp
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

LEFT_UNDER_EYE = [330, 347, 346, 352, 374, 373, 380, 381, 382, 362, 466, 388]
RIGHT_UNDER_EYE = [101, 118, 117, 123, 145, 144, 153, 154, 155, 133, 246, 161]
LEFT_EYEBALL = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
RIGHT_EYEBALL = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]

def generate_under_eye_mask(image, landmarks, face_scale):
    h, w, _ = image.shape
    pts_l = np.array([(int(landmarks[idx].x * w), int(landmarks[idx].y * h)) for idx in LEFT_UNDER_EYE], dtype=np.int32)
    pts_r = np.array([(int(landmarks[idx].x * w), int(landmarks[idx].y * h)) for idx in RIGHT_UNDER_EYE], dtype=np.int32)
    
    under_eye_mask = np.zeros((h, w), dtype=np.uint8)
    cv2.fillConvexPoly(under_eye_mask, cv2.convexHull(pts_l), 255)
    cv2.fillConvexPoly(under_eye_mask, cv2.convexHull(pts_r), 255)
    
    eye_protect_mask = np.zeros((h, w), dtype=np.uint8)
    pts_e1 = np.array([(int(landmarks[idx].x * w), int(landmarks[idx].y * h)) for idx in LEFT_EYEBALL], dtype=np.int32)
    pts_e2 = np.array([(int(landmarks[idx].x * w), int(landmarks[idx].y * h)) for idx in RIGHT_EYEBALL], dtype=np.int32)
    cv2.fillConvexPoly(eye_protect_mask, cv2.convexHull(pts_e1), 255)
    cv2.fillConvexPoly(eye_protect_mask, cv2.convexHull(pts_e2), 255)
    
    concealer_mask = cv2.subtract(under_eye_mask, eye_protect_mask)
    blur_k = max(15, int(face_scale * 0.12) | 1)
    blurred_mask = cv2.GaussianBlur(concealer_mask, (blur_k, blur_k), 0, borderType=cv2.BORDER_REFLECT)
    soft_mask = (blurred_mask.astype(np.float32) / 255.0)[:, :, np.newaxis]
    return soft_mask

def extract_skin_tone_lab(image, landmarks):
    h, w, _ = image.shape
    cheek_pts = np.array([(int(landmarks[idx].x * w), int(landmarks[idx].y * h)) for idx in [50, 205, 280, 425]], dtype=np.int32)
    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.fillConvexPoly(mask, cv2.convexHull(cheek_pts), 255)
    lab_img = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    mean_lab = cv2.mean(lab_img, mask=mask)[:3]
    return mean_lab

def apply_concealer_layer(image, landmarks, face_scale, depth="Medium", coverage="Medium", target_rgb=None):
    soft_mask = generate_under_eye_mask(image, landmarks, face_scale)
    cheek_lab = extract_skin_tone_lab(image, landmarks)
    lab_img = cv2.cvtColor(image, cv2.COLOR_BGR2LAB).astype(np.float32)
    L, A, B = cv2.split(lab_img)
    
    cov_factor = 0.45 if coverage == "Light" else 0.75
    d_val, sig = (7, 15) if coverage == "Light" else (11, 30)
    L_smooth = cv2.bilateralFilter(L.astype(np.uint8), d=d_val, sigmaColor=sig, sigmaSpace=sig).astype(np.float32)
    
    if target_rgb is not None:
       
        target_bgr = np.uint8([[[target_rgb[2], target_rgb[1], target_rgb[0]]]])
        target_lab = cv2.cvtColor(target_bgr, cv2.COLOR_BGR2LAB).astype(np.float32)[0, 0]

        L_target = np.clip(np.maximum(L_smooth, target_lab[0]), 0, 255)
        A_target = np.full_like(A, target_lab[1])
        B_target = np.full_like(B, target_lab[2])
    else:
        target_cheek_L = cheek_lab[0]
        if depth == "Fair":
            L_target = np.clip(np.maximum(L_smooth + 15.0, target_cheek_L + 5.0), 0, 255)
            A_target, B_target = A, B
        elif depth == "Medium":
            L_target = np.clip(np.maximum(L_smooth + 8.0, target_cheek_L), 0, 255)
            A_target, B_target = A, B
        else: 
            L_target = np.clip(L_smooth + 6.0, 0, 255)
            A_target = np.clip(A + 4.0, 0, 255)
            B_target = np.clip(B + 6.0, 0, 255)
            
    eff_mask = soft_mask[:, :, 0] * cov_factor
    L_final = L * (1.0 - eff_mask) + L_target * eff_mask
    A_final = A * (1.0 - eff_mask) + A_target * eff_mask
    B_final = B * (1.0 - eff_mask) + B_target * eff_mask
    
    merged_lab = cv2.merge([
        np.clip(L_final, 0, 255).astype(np.uint8),
        np.clip(A_final, 0, 255).astype(np.uint8),
        np.clip(B_final, 0, 255).astype(np.uint8)
    ])
    return cv2.cvtColor(merged_lab, cv2.COLOR_LAB2BGR)

def render_concealer_from_json_file(image_path, json_file_path="makeup_analysis.json"):

    if not os.path.exists(json_file_path):
        raise FileNotFoundError(f"لم يتم العثور على ملف الجيسون المطلوب: {json_file_path}")
        
    with open(json_file_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
        
    expert_out = config.get("expert_output", {})
    foundation_info = expert_out.get("foundation", {})
    
    concealer_info = foundation_info.get("concealer", {}) or {}
    formula_info = foundation_info.get("formula", {}) or {}
    
    descriptor = str(concealer_info.get("descriptor", "")).strip()
    reason_text = concealer_info.get("reason", "تطبيق بناءً على القواعد")
    suggested_rgb = concealer_info.get("rgb")
    suggested_hex = concealer_info.get("hex")
    
    if any(k in descriptor for k in ["أندرتون دافئ", "برتقالي", "خوخي"]):
        rec_depth = "Corrector"
    elif "أفتح" in descriptor:
        rec_depth = "Fair"
    else:
        rec_depth = "Medium"
        
    rec_coverage = formula_info.get("coverage", "Medium")
    rec_rgb = tuple(int(np.clip(v, 0, 255)) for v in suggested_rgb) if isinstance(suggested_rgb, (list, tuple)) and len(suggested_rgb) == 3 else None
    
    print("\n [READING DIRECTLY FROM makeup_analysis.json]")
    print(f"   Depth mode : {rec_depth}")
    print(f"   Coverage   : {rec_coverage}")
    print(f"   Descriptor : {descriptor}")
    print(f"   RGB        : {rec_rgb}")
    print(f"   HEX        : {suggested_hex}")
  
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"لم يتم العثور على صورة الوجه: {image_path}")
        
    h, w, _ = img.shape
    
    mp_face_mesh = mp.solutions.face_mesh
    with mp_face_mesh.FaceMesh(
        static_image_mode=True, 
        max_num_faces=1, 
        refine_landmarks=False
    ) as face_mesh:
        results = face_mesh.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        
        if not results.multi_face_landmarks:
            print("لم يتم العثور على وجه في الصورة.")
            return
            
        landmarks = results.multi_face_landmarks[0].landmark
        
    pt1 = np.array([landmarks[234].x * w, landmarks[234].y * h])
    pt2 = np.array([landmarks[454].x * w, landmarks[454].y * h])
    face_scale = np.linalg.norm(pt1 - pt2)
    
    strategies = [
        ("0. Original Image", None),
        ("1. Fair - Light Coverage", {"depth": "Fair", "coverage": "Light"}),
        ("2. Fair - Full Coverage", {"depth": "Fair", "coverage": "Full"}),
        ("3. Medium - Light Coverage", {"depth": "Medium", "coverage": "Light"}),
        ("4. Medium - Full Coverage", {"depth": "Medium", "coverage": "Full"}),
        ("5. Peach Corrector", {"depth": "Corrector", "coverage": "Full"})
    ]
    
    grid_imgs = []
    for title, strat in strategies:
        is_recommended = False
        
        if strat is None:
            res_img = img.copy()
        else:
            is_recommended = (
    (rec_depth == "Corrector" and strat["depth"] == "Corrector") or
    (strat["depth"] == rec_depth and (
        strat["coverage"] == rec_coverage or 
        (rec_coverage in ["Medium", "متوسطة"] and strat["coverage"] == "Full")
    ))
)
            res_img = apply_concealer_layer(
                img.copy(), landmarks, face_scale, 
                depth=strat["depth"], coverage=strat["coverage"], 
                target_rgb=rec_rgb if is_recommended else None
            )
            
        banner_color = (0, 160, 0) if is_recommended else (0, 0, 0)
        banner_text = f"★ JSON CHOICE: {title}" if is_recommended else title
        
        cv2.rectangle(res_img, (0, 0), (res_img.shape[1], 45), banner_color, -1)
        cv2.putText(res_img, banner_text, (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2, cv2.LINE_AA)
        grid_imgs.append(cv2.cvtColor(res_img, cv2.COLOR_BGR2RGB))
        
    row1 = np.hstack(grid_imgs[:3])
    row2 = np.hstack(grid_imgs[3:])
    full_grid = np.vstack([row1, row2])
    
    fig = plt.figure(figsize=(15, 9))
    fig.canvas.manager.set_window_title("Concealer Visualizer (Read directly from JSON)")
    
    ax_grid = plt.subplot2grid((10, 1), (0, 0), rowspan=9)
    ax_grid.imshow(full_grid)
    title_display = f"JSON Output -> Depth: [{rec_depth}] | Coverage: [{rec_coverage}]\nReason: {reason_text}"
    ax_grid.set_title(title_display, fontsize=12, fontweight='bold', color='darkgreen', pad=12)
    ax_grid.axis('off')
    
    ax_button = plt.subplot2grid((10, 1), (9, 0))
    btn_save = Button(ax_button, ' Save Render Grid', color='lightgrey', hovercolor='honeydew')
    
    def save_callback(event):
        cv2.imwrite("rendered_concealer_result.png", cv2.cvtColor(full_grid, cv2.COLOR_RGB2BGR))
        print("تم حفظ صورة شبكة العرض بنجاح: rendered_concealer_result.png")
        
    btn_save.on_clicked(save_callback)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":

    render_concealer_from_json_file(
        image_path="test2.jpg",
        json_file_path="makeup_analysis.json"
    )

if __name__ == "__main__":

    sample_experta_json = {
        "concealer": {
            "depth": "Medium",
            "descriptor": "درجة أفتح بدرجة إلى درجة ونصف من الأساس",
            "reason": "لتفتيح متوازن دون ظهور طبقة رمادية تحت العين",
            "hex": "#da9e78",
            "rgb": [218, 158, 120]
        },
        "formula": {
            "coverage": "Medium",
            "texture": "ساتان"
        }
    }
