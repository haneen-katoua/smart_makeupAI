# -*- coding: utf-8 -*-

import cv2
import numpy as np
import mediapipe as mp
import matplotlib.pyplot as plt
import os

def hex_to_bgr(hex_str: str) -> tuple:
    hex_str = str(hex_str).lstrip('#')
    if len(hex_str) == 6:
        r, g, b = int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16)
        return (b, g, r)
    return (210, 240, 255) 


def apply_professional_blend(image: np.ndarray, mask: np.ndarray, color_bgr: tuple, opacity: float, finish_type: str, face_scale: float) -> np.ndarray:

    blur_kernel = int(face_scale * 0.25) 
    if blur_kernel % 2 == 0:
        blur_kernel += 1
    blur_kernel = max(65, blur_kernel)
    soft_mask = cv2.GaussianBlur(mask, (blur_kernel, blur_kernel), 0).astype(np.float32) / 255.0
    soft_mask_3ch = np.repeat(soft_mask[:, :, np.newaxis], 3, axis=2)

    final_opacity = min(0.7, opacity * 0.9)  
    soft_mask_3ch *= final_opacity

    color_layer = np.full_like(image, color_bgr, dtype=np.float32) / 255.0
    
    img_float = image.astype(np.float32) / 255.0

    blend_layer = 2 * img_float * color_layer + (img_float * img_float) * (1 - 2 * color_layer)
    
    if "لامع" in str(finish_type):
        blend_layer = 1.0 - (1.0 - img_float) * (1.0 - color_layer * 0.6)

    final_img = (img_float * (1.0 - soft_mask_3ch)) + (blend_layer * soft_mask_3ch)
    
    return np.clip(final_img * 255.0, 0, 255).astype(np.uint8)

def generate_expert_rule_mask(image_shape: tuple, landmarks, placement_text: str, face_scale: float) -> np.ndarray:
    h, w = image_shape[:2]
    mask = np.zeros((h, w), dtype=np.uint8)
    txt = str(placement_text)

    if any(k in txt for k in ["عظمة الخد", "أعلى نقطة", "الخدين", "cheek"]):
        left_cheek = [117, 118, 101, 203, 142]
        right_cheek = [346, 347, 330, 423, 371]
        for indices in [left_cheek, right_cheek]:
            pts = np.array([[int(landmarks[idx].x * w), int(landmarks[idx].y * h)] for idx in indices], dtype=np.int32)
            cv2.fillConvexPoly(mask, cv2.convexHull(pts), 255)

    if "الأنف" in txt or "nose" in txt.lower():
        bridge_pts = np.array([
            [int(landmarks[197].x * w), int(landmarks[197].y * h)],
            [int(landmarks[195].x * w), int(landmarks[195].y * h)],
            [int(landmarks[5].x * w), int(landmarks[5].y * h)]
        ], dtype=np.int32)
        cv2.polylines(mask, [bridge_pts], isClosed=False, color=255, thickness=max(5, int(face_scale * 0.02)))
        tip_pt = (int(landmarks[1].x * w), int(landmarks[1].y * h))
        cv2.circle(mask, tip_pt, max(5, int(face_scale * 0.015)), 255, -1)

    if "الذقن" in txt or "chin" in txt.lower():
        chin_pt = (int(landmarks[152].x * w), int(landmarks[152].y * h))
        cv2.ellipse(mask, chin_pt, (int(face_scale * 0.030), int(face_scale * 0.020)), 0, 0, 360, 255, -1)

    if "الجبهة" in txt or "forehead" in txt.lower() or "T" in txt:
        forehead_pt = (int(landmarks[10].x * w), int(landmarks[10].y * h))
        cv2.ellipse(mask, forehead_pt, (int(face_scale * 0.040), int(face_scale * 0.025)), 0, 0, 360, 255, -1)

    return mask


def render_expert_highlight_pipeline(image: np.ndarray, landmarks, expert_results: dict, face_scale: float) -> np.ndarray:
 
    highlight_info = expert_results.get('highlight', {}) or expert_results.get('concealer', {}) or expert_results.get('shade', {}) or {}
    texture_info = expert_results.get('texture', {}) or expert_results.get('formula', {}) or {}

    placement = highlight_info.get('placement', 'عظمة الخد الأنف الذقن الجبهة')
    hex_color = highlight_info.get('hex', '#FFF8DC')
    
    raw_opacity = highlight_info.get('opacity', 50)
    opacity = float(raw_opacity) / 100.0 if float(raw_opacity) > 1.0 else float(raw_opacity)

    opacity = max(0.1, opacity)

    finish_type = texture_info.get('finish', 'لامع')
    color_bgr = hex_to_bgr(hex_color)

    mask = generate_expert_rule_mask(image.shape, landmarks, placement, face_scale)
    return apply_professional_blend(image, mask, color_bgr, opacity, finish_type, face_scale=face_scale)



if __name__ == "__main__":

    json_analysis_data = {
        "highlight": {
            "placement": "عظمة الخد الأنف الذقن الجبهة",
            "hex": "#FEFCE5", 
            "opacity": 75 
        },
        "texture": {
            "finish": "ساتان / لامع",
            "description": "إطلالة براقة ومتألقة تحت الإضاءة"
        }
    }

    image_path = "test2.jpg" 
    if not os.path.exists(image_path):

        print(f" {image_path} non existant, creating dummy face image.")
        img = np.full((1000, 1000, 3), 220, dtype=np.uint8)

        cv2.rectangle(img, (300, 200), (700, 800), (180, 180, 180), -1)
        image_path = "dummy_face.jpg"
        cv2.imwrite(image_path, img)

    img = cv2.imread(image_path)

    if img is not None:
        h, w, _ = img.shape
        mp_face_mesh = mp.solutions.face_mesh
        
        with mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1) as face_mesh:
            results = face_mesh.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            if results.multi_face_landmarks:
                landmarks = results.multi_face_landmarks[0].landmark
                
                pt1 = np.array([landmarks[234].x * w, landmarks[234].y * h])
                pt2 = np.array([landmarks[454].x * w, landmarks[454].y * h])
                face_scale = np.linalg.norm(pt1 - pt2)

                json_single_output = render_expert_highlight_pipeline(img.copy(), landmarks, json_analysis_data, face_scale)
                
                output_name = "json_highlight_output_FIXED.png"
                cv2.imwrite(output_name, json_single_output)
                print(f" تم تنفيذ الرسم المستخرج من JSON وحفظه في النتيجة : {output_name}")

                plt.figure(figsize=(12, 6))
                
                plt.subplot(1, 2, 1)
                plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
                plt.title("Original Image", fontsize=12)
                plt.axis('off')
                
                plt.subplot(1, 2, 2)
                plt.imshow(cv2.cvtColor(json_single_output, cv2.COLOR_BGR2RGB))
                plt.title(f"Dynamic Highlight (Opacity: {json_analysis_data['highlight']['opacity']}%)", fontsize=12)
                plt.axis('off')
                
                plt.tight_layout()

                plt.show()

            else:
                print(" لم يتم العثور على وجه في الصورة.")
    else:
        print(f" لم يتم العثور على الملف: {image_path}")