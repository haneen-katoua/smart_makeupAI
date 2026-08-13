# # # -*- coding: utf-8 -*-
# # """
# # skin_analysis_improved.py — Improved Skin Color Analysis with Experta Compatibility
# # ====================================================================================

# # التحسينات:
# # ✓ تحليل اللون باستخدام LAB color space
# # ✓ تحديد undertone (Warm/Cool) بناءً على الصبغات
# # ✓ تحديد depth (Fair/Medium/Dark) بناءً على brightness
# # ✓ تحديد skin_type (Oily/Dry/Combination/Sensitive/Normal)
# # ✓ معالجة أخطاء شاملة
# # ✓ نتائج موثوقة وقابلة للتكرار
# # """

# # # ✅ MUST BE FIRST: Python 3.10+ Compatibility Fix
# # import compat_fix

# # import cv2
# # import numpy as np
# # from typing import Dict, Optional, Tuple
# # from dataclasses import dataclass


# # @dataclass
# # class SkinAnalysisResult:
# #     """نتيجة تحليل البشرة"""
# #     success: bool
# #     skin_depth: Optional[str] = None      # Fair / Medium / Dark
# #     undertone: Optional[str] = None       # Warm / Cool
# #     skin_type: Optional[str] = None       # Oily / Dry / Combination / Sensitive / Normal
# #     color_lab: Optional[Dict] = None      # LAB values
# #     color_rgb: Optional[Tuple] = None     # RGB values
# #     confidence: float = 0.0
# #     error: Optional[str] = None


# # # ══════════════════════════════════════════════════════════════════
# # # COLOR EXTRACTION
# # # ══════════════════════════════════════════════════════════════════

# # def _extract_face_region(image: np.ndarray) -> Optional[np.ndarray]:
# #     """
# #     استخراج منطقة الوجه من الصورة (بسيط)
# #     يستخدم region في وسط الصورة
# #     """
# #     try:
# #         h, w = image.shape[:2]
        
# #         # المنطقة الوسطى (يفترض أن الوجه يكون في الوسط)
# #         x_start = int(w * 0.25)
# #         x_end = int(w * 0.75)
# #         y_start = int(h * 0.3)
# #         y_end = int(h * 0.7)
        
# #         face_region = image[y_start:y_end, x_start:x_end]
# #         return face_region
    
# #     except Exception as e:
# #         print(f"Error extracting face region: {e}")
# #         return None


# # def _get_skin_color_from_region(face_region: np.ndarray) -> Optional[Tuple]:
# #     """
# #     استخراج لون البشرة من منطقة الوجه
# #     يستخدم المنطقة الوسطى من الخدّ
# #     """
# #     try:
# #         h, w = face_region.shape[:2]
        
# #         # منطقة الخد (وسط الوجه بقليل إلى اليمين)
# #         cheek_x_start = int(w * 0.3)
# #         cheek_x_end = int(w * 0.6)
# #         cheek_y_start = int(h * 0.4)
# #         cheek_y_end = int(h * 0.65)
        
# #         cheek_region = face_region[cheek_y_start:cheek_y_end, cheek_x_start:cheek_x_end]
        
# #         # حساب متوسط اللون
# #         avg_color_bgr = cv2.mean(cheek_region)[:3]
        
# #         # تحويل إلى RGB
# #         avg_color_rgb = (avg_color_bgr[2], avg_color_bgr[1], avg_color_bgr[0])
        
# #         return avg_color_rgb
    
# #     except Exception as e:
# #         print(f"Error getting skin color: {e}")
# #         return None


# # # ══════════════════════════════════════════════════════════════════
# # # COLOR SPACE CONVERSIONS
# # # ══════════════════════════════════════════════════════════════════

# # def _rgb_to_lab(rgb: Tuple) -> Tuple:
# #     """تحويل RGB إلى LAB"""
# #     try:
# #         # Normalize RGB to 0-1
# #         r, g, b = [x / 255.0 for x in rgb]
        
# #         # Apply gamma correction
# #         r = r / 12.92 if r <= 0.04045 else pow((r + 0.055) / 1.055, 2.4)
# #         g = g / 12.92 if g <= 0.04045 else pow((g + 0.055) / 1.055, 2.4)
# #         b = b / 12.92 if b <= 0.04045 else pow((b + 0.055) / 1.055, 2.4)
        
# #         # Convert to XYZ
# #         x = r * 0.4124 + g * 0.3576 + b * 0.1805
# #         y = r * 0.2126 + g * 0.7152 + b * 0.0722
# #         z = r * 0.0193 + g * 0.1192 + b * 0.9505
        
# #         # Normalize using D65 illuminant
# #         x = x / 0.95047
# #         y = y / 1.00000
# #         z = z / 1.08883
        
# #         # Apply LAB transformation
# #         epsilon = 0.008856
# #         kappa = 903.3
        
# #         fx = x ** (1/3) if x > epsilon else (kappa * x + 16) / 116
# #         fy = y ** (1/3) if y > epsilon else (kappa * y + 16) / 116
# #         fz = z ** (1/3) if z > epsilon else (kappa * z + 16) / 116
        
# #         l = max(0, 116 * fy - 16)
# #         a = 500 * (fx - fy)
# #         b = 200 * (fy - fz)
        
# #         return (l, a, b)
    
# #     except Exception as e:
# #         print(f"Error converting RGB to LAB: {e}")
# #         return (50, 0, 0)  # Default


# # # ══════════════════════════════════════════════════════════════════
# # # UNDERTONE DETECTION
# # # ══════════════════════════════════════════════════════════════════

# # def _detect_undertone(rgb: Tuple, lab: Tuple) -> Tuple[str, float]:
# #     """
# #     تحديد الـ undertone (Warm/Cool)
    
# #     Logic:
# #     - Warm: أحمر عالي، أصفر عالي (a و b موجبين)
# #     - Cool: أحمر منخفض، أزرق عالي (a سالب أو b سالب)
# #     """
# #     try:
# #         r, g, b = rgb
# #         l, a_val, b_val = lab
        
# #         # اختبار رقم 1: نسبة RGB
# #         red_green_diff = r - g
# #         blue_diff = b - g
        
# #         # اختبار رقم 2: LAB values
# #         # a > 0 = warm (إلى الأحمر)
# #         # a < 0 = cool (إلى الأخضر)
# #         # b > 0 = warm (إلى الأصفر)
# #         # b < 0 = cool (إلى الأزرق)
        
# #         undertone_score = 0.0
        
# #         if a_val > 2:  # الأحمر/الدفء
# #             undertone_score += 0.4
# #         elif a_val < -2:  # الأخضر/البرودة
# #             undertone_score -= 0.4
        
# #         if b_val > 5:  # الأصفر/الدفء
# #             undertone_score += 0.3
# #         elif b_val < -5:  # الأزرق/البرودة
# #             undertone_score -= 0.3
        
# #         if red_green_diff > 10:  # الأحمر أكثر من الأخضر
# #             undertone_score += 0.3
        
# #         # تحديد النتيجة
# #         if undertone_score > 0:
# #             undertone = 'Warm'
# #             confidence = min(abs(undertone_score), 1.0)
# #         elif undertone_score < -0.2:
# #             undertone = 'Cool'
# #             confidence = min(abs(undertone_score), 1.0)
# #         else:
# #             undertone = 'Neutral'
# #             confidence = 0.5
        
# #         return (undertone, confidence)
    
# #     except Exception as e:
# #         print(f"Error detecting undertone: {e}")
# #         return ('Warm', 0.5)  # Default


# # # ══════════════════════════════════════════════════════════════════
# # # DEPTH DETECTION (Fair/Medium/Dark)
# # # ══════════════════════════════════════════════════════════════════

# # def _detect_depth(lab: Tuple) -> Tuple[str, float]:
# #     """
# #     تحديد عمق اللون (Fair/Medium/Dark)
    
# #     يستخدم قيمة L من LAB:
# #     - L > 70: Fair
# #     - 50-70: Medium
# #     - L < 50: Dark
# #     """
# #     try:
# #         l_value = lab[0]
        
# #         if l_value > 70:
# #             depth = 'Fair'
# #             confidence = (l_value - 70) / 30
# #         elif l_value > 50:
# #             depth = 'Medium'
# #             confidence = (l_value - 50) / 20
# #         else:
# #             depth = 'Dark'
# #             confidence = (50 - l_value) / 50
        
# #         confidence = min(confidence, 1.0)
        
# #         return (depth, confidence)
    
# #     except Exception as e:
# #         print(f"Error detecting depth: {e}")
# #         return ('Medium', 0.5)  # Default


# # # ══════════════════════════════════════════════════════════════════
# # # SKIN TYPE DETECTION
# # # ══════════════════════════════════════════════════════════════════

# # def _detect_skin_type(image: np.ndarray) -> Tuple[str, float]:
# #     """
# #     تحديد نوع البشرة (Oily/Dry/Combination/Sensitive/Normal)
    
# #     في هذه النسخة المحسّنة، نستخدم euristics بسيطة
# #     يمكن تحسينها لاحقاً مع تحليل ملمس البشرة
# #     """
# #     try:
# #         # استخراج منطقة الوجه
# #         face_region = _extract_face_region(image)
# #         if face_region is None:
# #             return ('Normal', 0.5)
        
# #         # تحليل Texture (بسيط)
# #         # للبشرة الدهنية: تعكس الضوء أكثر (brightness عالي في المناطق العالية)
# #         # للبشرة الجافة: ملمس أكثر خشونة
        
# #         gray = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
        
# #         # حساب standard deviation (قياس الملمس)
# #         texture_score = np.std(gray)
        
# #         # افتراضي: معظم الناس لديهم بشرة Combination أو Normal
# #         if texture_score > 30:
# #             skin_type = 'Oily'  # ملمس أكثر عدم التجانس = دهون
# #             confidence = 0.6
# #         elif texture_score < 15:
# #             skin_type = 'Dry'  # ملمس ناعم جداً = جاف
# #             confidence = 0.6
# #         else:
# #             skin_type = 'Normal'  # المتوسط
# #             confidence = 0.7
        
# #         return (skin_type, confidence)
    
# #     except Exception as e:
# #         print(f"Error detecting skin type: {e}")
# #         return ('Normal', 0.5)  # Default


# # # ══════════════════════════════════════════════════════════════════
# # # MAIN ANALYSIS FUNCTION
# # # ══════════════════════════════════════════════════════════════════

# # def analyze_skin_from_image(image_source) -> SkinAnalysisResult:
# #     """
# #     تحليل البشرة من صورة
    
# #     Args:
# #         image_source: 
# #             - مسار الملف (str)
# #             - numpy array
    
# #     Returns:
# #         SkinAnalysisResult
# #     """
# #     try:
# #         # تحميل الصورة
# #         if isinstance(image_source, str):
# #             image = cv2.imread(image_source)
# #             if image is None:
# #                 return SkinAnalysisResult(
# #                     success=False,
# #                     error=f"Cannot read image: {image_source}"
# #                 )
# #         else:
# #             image = image_source
        
# #         # استخراج منطقة الوجه
# #         face_region = _extract_face_region(image)
# #         if face_region is None:
# #             return SkinAnalysisResult(
# #                 success=False,
# #                 error="Cannot extract face region"
# #             )
        
# #         # استخراج لون البشرة
# #         skin_color_rgb = _get_skin_color_from_region(face_region)
# #         if skin_color_rgb is None:
# #             return SkinAnalysisResult(
# #                 success=False,
# #                 error="Cannot extract skin color"
# #             )
        
# #         # تحويل إلى LAB
# #         skin_color_lab = _rgb_to_lab(skin_color_rgb)
        
# #         # تحديد الـ undertone
# #         undertone, undertone_conf = _detect_undertone(skin_color_rgb, skin_color_lab)
        
# #         # تحديد العمق
# #         depth, depth_conf = _detect_depth(skin_color_lab)
        
# #         # تحديد نوع البشرة
# #         skin_type, skin_type_conf = _detect_skin_type(image)
        
# #         # متوسط الـ confidence
# #         overall_confidence = (undertone_conf + depth_conf + skin_type_conf) / 3
        
# #         return SkinAnalysisResult(
# #             success=True,
# #             skin_depth=depth,
# #             undertone=undertone,
# #             skin_type=skin_type,
# #             color_lab={
# #                 'L': float(skin_color_lab[0]),
# #                 'a': float(skin_color_lab[1]),
# #                 'b': float(skin_color_lab[2])
# #             },
# #             color_rgb=skin_color_rgb,
# #             confidence=float(overall_confidence)
# #         )
    
# #     except Exception as e:
# #         return SkinAnalysisResult(
# #             success=False,
# #             error=str(e)
# #         )


# # def analyze_skin_from_image_dict(image_source) -> Dict:
# #     """
# #     تحليل البشرة وإرجاع dict
# #     (للتوافق مع complete_makeup_pipeline)
# #     """
# #     result = analyze_skin_from_image(image_source)
    
# #     if not result.success:
# #         return {
# #             'success': False,
# #             'error': result.error
# #         }
    
# #     return {
# #         'success': True,
# #         'skin_depth': result.skin_depth,
# #         'undertone': result.undertone,
# #         'skin_type': result.skin_type,
# #         'color_lab': result.color_lab,
# #         'color_rgb': result.color_rgb,
# #         'confidence': result.confidence
# #     }


# # # ══════════════════════════════════════════════════════════════════
# # # EXAMPLE USAGE
# # # ══════════════════════════════════════════════════════════════════

# # if __name__ == "__main__":
# #     import json
    
# #     # مثال 1: تحليل من ملف
# #     print("Analyzing skin from file...")
# #     result = analyze_skin_from_image('photo.jpg')
    
# #     if result.success:
# #         print(f"✓ Analysis successful!")
# #         print(f"  Depth: {result.skin_depth}")
# #         print(f"  Undertone: {result.undertone}")
# #         print(f"  Skin Type: {result.skin_type}")
# #         print(f"  Confidence: {result.confidence:.2%}")
# #     else:
# #         print(f"✗ Error: {result.error}")
    
# #     # مثال 2: استخدام dict format
# #     print("\nUsing dict format...")
# #     result_dict = analyze_skin_from_image_dict('photo.jpg')
# #     print(json.dumps(result_dict, indent=2, ensure_ascii=False, default=str))

# # -*- coding: utf-8 -*-


# """
# skin_analysis_improved.py — Accurate Skin Color & Type Analysis with Experta Compatibility
# ===========================================================================================

# التحسينات:
# ✓ استخدام MediaPipe لعزل البشرة بدقة استثنائية (بدلاً من الاقتصاص العشوائي)
# ✓ استخراج اللون الحقيقي وفضاء ألوان LAB باستخدام K-Means
# ✓ تصنيف Fitzpatrick وزاوية ITA الدقيقة لحساب الـ Depth والـ Undertone
# ✓ خوارزمية Specular Highlights + T-Zone لتحديد نوع البشرة (Oily/Dry/Normal/Combination)
# ✓ إضافة حقل HEX Color لإتاحة استخدام لون البشرة مباشرة في الواجهات
# ✓ متوافق كلياً مع Experta و complete_makeup_pipeline عبر نتائج (dataclass & dict)
# """

# # ✅ MUST BE FIRST: Python 3.10+ Compatibility Fix
# import compat_fix

# import os
# import math
# import cv2
# import numpy as np
# from typing import Dict, Optional, Tuple
# from dataclasses import dataclass
# from sklearn.cluster import KMeans
# import mediapipe as mp
# from mediapipe.tasks import python
# from mediapipe.tasks.python import vision

# # ══════════════════════════════════════════════════════════════════
# # MEDIAPIPE INITIALIZATION
# # ══════════════════════════════════════════════════════════════════

# MODEL_PATH = 'face_landmarker_v2_with_blendshapes.task'

# base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
# options = vision.FaceLandmarkerOptions(
#     base_options=base_options,
#     output_face_blendshapes=False,
#     output_facial_transformation_matrixes=False,
#     num_faces=1
# )


# @dataclass
# class SkinAnalysisResult:
#     """نتيجة تحليل البشرة"""
#     success: bool
#     skin_depth: Optional[str] = None      # Fair / Medium / Dark
#     undertone: Optional[str] = None       # Warm / Cool / Neutral
#     skin_type: Optional[str] = None       # Oily / Dry / Combination / Normal
#     color_lab: Optional[Dict] = None      # LAB values {'L', 'a', 'b'}
#     color_rgb: Optional[Tuple] = None     # RGB values (R, G, B)
#     color_hex: Optional[str] = None       # HEX Color String e.g. "#e8c2a8"
#     confidence: float = 0.0
#     error: Optional[str] = None


# # ══════════════════════════════════════════════════════════════════
# # ADVANCED SKIN MASKING & EXTRACTION (MediaPipe)
# # ══════════════════════════════════════════════════════════════════

# def _extract_skin_mask_and_zones(img_bgr, landmarks, h, w):
#     """عزل كامل بشرة الوجه واستخراج قناع الـ T-Zone للتحليل الدقيق"""
#     face_oval = [
#         10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288,
#         397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136,
#         172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109
#     ]
#     left_eye = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
#     right_eye = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
#     left_eyebrow = [70, 63, 105, 66, 107, 55, 65, 52, 53, 46]
#     right_eyebrow = [300, 293, 334, 296, 336, 285, 295, 282, 283, 276]
#     outer_lips = [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291, 375, 321, 405, 314, 17, 84, 181, 91, 146]

#     def get_pts(indices):
#         return np.array([[int(landmarks[i].x * w), int(landmarks[i].y * h)] for i in indices], np.int32)

#     # 1. القناع الشامل للوجه
#     full_mask = np.zeros((h, w), dtype=np.uint8)
#     cv2.fillPoly(full_mask, [get_pts(face_oval)], 255)
#     full_mask = cv2.erode(full_mask, np.ones((13, 13), np.uint8), iterations=1)

#     # 2. استبعاد الملامح (عيون، حواجب، شفاه)
#     features_mask = np.zeros((h, w), dtype=np.uint8)
#     for feature in [left_eye, right_eye, outer_lips, left_eyebrow, right_eyebrow]:
#         cv2.fillPoly(features_mask, [get_pts(feature)], 255)
#     features_mask = cv2.dilate(features_mask, np.ones((7, 7), np.uint8), iterations=1)

#     skin_mask = cv2.bitwise_and(full_mask, cv2.bitwise_not(features_mask))

#     # 3. قناع الـ T-Zone
#     t_zone_indices = [10, 338, 297, 67, 109, 151, 9, 8, 168, 6, 197, 195, 5, 4, 1, 19, 94, 2, 164, 0, 11, 12, 13, 14, 15, 16, 17, 18, 200, 199, 175, 152]
#     t_mask = np.zeros((h, w), dtype=np.uint8)
#     cv2.fillPoly(t_mask, [get_pts(t_zone_indices)], 255)
#     t_mask = cv2.bitwise_and(t_mask, skin_mask)

#     # 4. قناع الـ U-Zone (الخدين والمناطق المتبقية)
#     u_mask = cv2.bitwise_and(skin_mask, cv2.bitwise_not(t_mask))

#     return skin_mask, t_mask, u_mask


# # ══════════════════════════════════════════════════════════════════
# # COLOR ACCURATE EXTRACTION (K-Means & ITA)
# # ══════════════════════════════════════════════════════════════════

# def _extract_lab_and_rgb_color(skin_pixels_bgr):
#     """استخراج لون البشرة المهيمن باستخدام K-Means وتحويله لـ LAB و RGB و HEX"""
#     pixels_lab = cv2.cvtColor(skin_pixels_bgr.reshape(-1, 1, 3), cv2.COLOR_BGR2LAB).reshape(-1, 3)
    
#     L_channel = (pixels_lab[:, 0] / 255.0) * 100.0
#     lower_bound = np.percentile(L_channel, 25)
#     upper_bound = np.percentile(L_channel, 75)

#     valid_indices = np.where((L_channel >= lower_bound) & (L_channel <= upper_bound))[0]
#     filtered_lab = pixels_lab[valid_indices] if len(valid_indices) > 500 else pixels_lab

#     sample_size = min(len(filtered_lab), 5000)
#     indices = np.random.choice(len(filtered_lab), sample_size, replace=False)
#     sample_lab = filtered_lab[indices]

#     kmeans = KMeans(n_clusters=3, n_init=10, random_state=42)
#     labels = kmeans.fit_predict(sample_lab)
#     dominant_cluster = np.argmax(np.bincount(labels))

#     median_lab = np.median(sample_lab[labels == dominant_cluster], axis=0)

#     L_star = (median_lab[0] / 255.0) * 100.0
#     a_star = median_lab[1] - 128.0
#     b_star = median_lab[2] - 128.0

#     # تحويل LAB إلى BGR لاستخراج RGB و HEX
#     lab_pixel = np.uint8([[[ (L_star / 100.0) * 255.0, a_star + 128.0, b_star + 128.0 ]]])
#     bgr_pixel = cv2.cvtColor(lab_pixel, cv2.COLOR_LAB2BGR)[0][0]
    
#     r_val, g_val, b_val = int(bgr_pixel[2]), int(bgr_pixel[1]), int(bgr_pixel[0])
#     hex_color = f"#{r_val:02x}{g_val:02x}{b_val:02x}"

#     return (L_star, a_star, b_star), (r_val, g_val, b_val), hex_color


# def _detect_depth_and_undertone(L_star, a_star, b_star):
#     """تحديد عمق البشرة والـ Undertone بالاعتماد على زاوية ITA العلمية"""
#     b_safe = b_star if abs(b_star) > 0.001 else 0.001
#     ita_angle = (math.atan2(L_star - 50.0, b_safe) / math.pi) * 180.0

#     # Depth (Fair / Medium / Dark)
#     if ita_angle > 41.0:
#         depth = "Fair"
#     elif 10.0 < ita_angle <= 41.0:
#         depth = "Medium"
#     else:
#         depth = "Dark"

#     # Undertone (Warm / Cool / Neutral)
#     hue_angle = math.degrees(math.atan2(b_star, a_star)) % 360.0
#     if hue_angle >= 50.0:
#         undertone = "Warm"
#     elif hue_angle < 35.0:
#         undertone = "Cool"
#     else:
#         undertone = "Neutral"

#     return depth, undertone, ita_angle


# # ══════════════════════════════════════════════════════════════════
# # ADVANCED SKIN TYPE DETECTION (Highlights & Zones)
# # ══════════════════════════════════════════════════════════════════

# def _detect_skin_type_advanced(img_bgr, skin_mask, t_mask, u_mask):
#     """تحديد نوع البشرة بدقة بناءً على انعكاسات الإضاءة وتباين الـ T-Zone والـ U-Zone"""
#     hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
#     gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

#     def calc_highlights_ratio(zone_mask):
#         total = np.sum(zone_mask == 255)
#         if total == 0:
#             return 0.0
#         val = hsv[:, :, 2]
#         sat = hsv[:, :, 1]
#         highlights = (val > 210) & (sat < 50) & (zone_mask == 255)
#         return (np.sum(highlights) / total) * 100.0

#     t_highlight = calc_highlights_ratio(t_mask)
#     u_highlight = calc_highlights_ratio(u_mask)
#     overall_highlight = calc_highlights_ratio(skin_mask)

#     texture_std = float(np.std(gray[skin_mask == 255])) if np.sum(skin_mask == 255) > 0 else 0.0

#     if t_highlight > 4.5 and u_highlight > 4.0:
#         skin_type = "Oily"
#         confidence = 0.85
#     elif t_highlight > 4.0 and u_highlight <= 2.5:
#         skin_type = "Combination"
#         confidence = 0.88
#     elif overall_highlight < 1.0 and texture_std < 16.0:
#         skin_type = "Dry"
#         confidence = 0.82
#     else:
#         skin_type = "Normal"
#         confidence = 0.80

#     return skin_type, confidence


# # ══════════════════════════════════════════════════════════════════
# # MAIN ANALYSIS FUNCTIONS
# # ══════════════════════════════════════════════════════════════════

# def analyze_skin_from_image(image_source) -> SkinAnalysisResult:
#     """تحليل البشرة من صورة وإرجاع كائن SkinAnalysisResult"""
#     try:
#         if isinstance(image_source, str):
#             if not os.path.exists(image_source):
#                 return SkinAnalysisResult(success=False, error=f"Cannot find image: {image_source}")
#             image = cv2.imread(image_source)
#             if image is None:
#                 return SkinAnalysisResult(success=False, error=f"Cannot read image: {image_source}")
#         else:
#             image = image_source

#         h, w, _ = image.shape
#         img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
#         mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)

#         with vision.FaceLandmarker.create_from_options(options) as landmarker:
#             detection_result = landmarker.detect(mp_image)

#         if not detection_result.face_landmarks:
#             return SkinAnalysisResult(success=False, error="No face detected in the image")

#         landmarks = detection_result.face_landmarks[0]
#         skin_mask, t_mask, u_mask = _extract_skin_mask_and_zones(image, landmarks, h, w)

#         skin_pixels = image[skin_mask == 255]
#         if len(skin_pixels) == 0:
#             return SkinAnalysisResult(success=False, error="Could not extract valid skin pixels")

#         # 1. استخراج اللون
#         lab_tuple, rgb_tuple, hex_color = _extract_lab_and_rgb_color(skin_pixels)

#         # 2. تحديد العمق والـ Undertone
#         depth, undertone, _ = _detect_depth_and_undertone(lab_tuple[0], lab_tuple[1], lab_tuple[2])

#         # 3. تحديد نوع البشرة
#         skin_type, skin_type_conf = _detect_skin_type_advanced(image, skin_mask, t_mask, u_mask)

#         # متوسط الـ confidence العام
#         overall_confidence = (0.90 + skin_type_conf) / 2

#         return SkinAnalysisResult(
#             success=True,
#             skin_depth=depth,
#             undertone=undertone,
#             skin_type=skin_type,
#             color_lab={
#                 'L': float(lab_tuple[0]),
#                 'a': float(lab_tuple[1]),
#                 'b': float(lab_tuple[2])
#             },
#             color_rgb=rgb_tuple,
#             color_hex=hex_color,
#             confidence=float(overall_confidence)
#         )

#     except Exception as e:
#         return SkinAnalysisResult(success=False, error=str(e))


# def analyze_skin_from_image_dict(image_source) -> Dict:
#     result = analyze_skin_from_image(image_source)
    
#     if not result.success:
#         return {
#             'success': False,
#             'error': result.error
#         }
    
#     return {
#         'success': True,
#         'skin_depth': result.skin_depth,
#         'undertone': result.undertone,
#         'skin_type': result.skin_type,
#         'color_lab': result.color_lab,
#         'color_rgb': result.color_rgb,
#         'color_hex': result.color_hex,
#         'confidence': result.confidence
#     }


# # ══════════════════════════════════════════════════════════════════
# # EXAMPLE USAGE
# # ══════════════════════════════════════════════════════════════════
# # ══════════════════════════════════════════════════════════════════
# # EXAMPLE USAGE
# # ══════════════════════════════════════════════════════════════════

# if __name__ == "__main__":
#     import json
    
#     # مثال 1: تحليل من ملف
#     print("Analyzing skin from file...")
#     result = analyze_skin_from_image('pictures3/warm14.jpg')

#     if result.success:
#         print(f"✓ Analysis successful!")
#         print(f"  Depth: {result.skin_depth}")
#         print(f"  Undertone: {result.undertone}")
#         print(f"  Skin Type: {result.skin_type}")
#         print(f"  Confidence: {result.confidence:.2%}")
#     else:
#         print(f"✗ Error: {result.error}")
    
#     # مثال 2: استخدام dict format
#     print("\nUsing dict format...")
#     result_dict = analyze_skin_from_image_dict('pictures3/warm14.jpg')
#     print(json.dumps(result_dict, indent=2, ensure_ascii=False, default=str))
# ✅ MUST BE FIRST: Python 3.10+ Compatibility Fix
import compat_fix

import os
import math
import cv2
import numpy as np
from pathlib import Path
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from sklearn.cluster import KMeans
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# كتم تحذيرات C++ الصادرة من MediaPipe / TensorFlow
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# ══════════════════════════════════════════════════════════════════
# MEDIAPIPE INITIALIZATION (Buffer-Based Resolution)
# ══════════════════════════════════════════════════════════════════

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / 'face_landmarker_v2_with_blendshapes.task'

if not MODEL_PATH.exists():
    raise FileNotFoundError(f"لم يتم العثور على ملف النموذج في المسار: {MODEL_PATH}")

with open(MODEL_PATH, 'rb') as f:
    model_buffer = f.read()

base_options = python.BaseOptions(model_asset_buffer=model_buffer)
options = vision.FaceLandmarkerOptions(
    base_options=base_options,
    output_face_blendshapes=False,
    output_facial_transformation_matrixes=False,
    num_faces=1
)


@dataclass
class SkinAnalysisResult:
    """نتيجة تحليل البشرة"""
    success: bool
    skin_depth: Optional[str] = None      # Fair / Medium / Dark
    undertone: Optional[str] = None       # Warm / Cool (فقط)
    skin_type: Optional[str] = None       # Oily / Dry / Combination / Normal
    color_lab: Optional[Dict] = None      # LAB values {'L', 'a', 'b'}
    color_rgb: Optional[Tuple] = None     # RGB values (R, G, B)
    color_hex: Optional[str] = None       # HEX Color String e.g. "#e8c2a8"
    confidence: float = 0.0
    error: Optional[str] = None


# ══════════════════════════════════════════════════════════════════
# ADVANCED SKIN MASKING & EXTRACTION (MediaPipe)
# ══════════════════════════════════════════════════════════════════

def _extract_skin_mask_and_zones(img_bgr, landmarks, h, w):
    """عزل كامل بشرة الوجه واستخراج قناع الـ T-Zone للتحليل الدقيق"""
    face_oval = [
        10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288,
        397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136,
        172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109
    ]
    left_eye = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
    right_eye = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
    left_eyebrow = [70, 63, 105, 66, 107, 55, 65, 52, 53, 46]
    right_eyebrow = [300, 293, 334, 296, 336, 285, 295, 282, 283, 276]
    outer_lips = [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291, 375, 321, 405, 314, 17, 84, 181, 91, 146]

    def get_pts(indices):
        return np.array([[int(landmarks[i].x * w), int(landmarks[i].y * h)] for i in indices], np.int32)

    # 1. القناع الشامل للوجه
    full_mask = np.zeros((h, w), dtype=np.uint8)
    cv2.fillPoly(full_mask, [get_pts(face_oval)], 255)
    full_mask = cv2.erode(full_mask, np.ones((13, 13), np.uint8), iterations=1)

    # 2. استبعاد الملامح
    features_mask = np.zeros((h, w), dtype=np.uint8)
    for feature in [left_eye, right_eye, outer_lips, left_eyebrow, right_eyebrow]:
        cv2.fillPoly(features_mask, [get_pts(feature)], 255)
    features_mask = cv2.dilate(features_mask, np.ones((7, 7), np.uint8), iterations=1)

    skin_mask = cv2.bitwise_and(full_mask, cv2.bitwise_not(features_mask))

    # 3. قناع الـ T-Zone
    t_zone_indices = [10, 338, 297, 67, 109, 151, 9, 8, 168, 6, 197, 195, 5, 4, 1, 19, 94, 2, 164, 0, 11, 12, 13, 14, 15, 16, 17, 18, 200, 199, 175, 152]
    t_mask = np.zeros((h, w), dtype=np.uint8)
    cv2.fillPoly(t_mask, [get_pts(t_zone_indices)], 255)
    t_mask = cv2.bitwise_and(t_mask, skin_mask)

    # 4. قناع الـ U-Zone
    u_mask = cv2.bitwise_and(skin_mask, cv2.bitwise_not(t_mask))

    return skin_mask, t_mask, u_mask


# ══════════════════════════════════════════════════════════════════
# COLOR ACCURATE EXTRACTION & BINARY UNDERTONE
# ══════════════════════════════════════════════════════════════════

def _extract_lab_and_rgb_color(skin_pixels_bgr):
    """استخراج لون البشرة المهيمن باستخدام K-Means وتحويله لـ LAB و RGB و HEX"""
    pixels_lab = cv2.cvtColor(skin_pixels_bgr.reshape(-1, 1, 3), cv2.COLOR_BGR2LAB).reshape(-1, 3)
    
    L_channel = (pixels_lab[:, 0] / 255.0) * 100.0
    lower_bound = np.percentile(L_channel, 25)
    upper_bound = np.percentile(L_channel, 75)

    valid_indices = np.where((L_channel >= lower_bound) & (L_channel <= upper_bound))[0]
    filtered_lab = pixels_lab[valid_indices] if len(valid_indices) > 500 else pixels_lab

    sample_size = min(len(filtered_lab), 5000)
    indices = np.random.choice(len(filtered_lab), sample_size, replace=False)
    sample_lab = filtered_lab[indices]

    kmeans = KMeans(n_clusters=3, n_init=10, random_state=42)
    labels = kmeans.fit_predict(sample_lab)
    dominant_cluster = np.argmax(np.bincount(labels))

    median_lab = np.median(sample_lab[labels == dominant_cluster], axis=0)

    L_star = (median_lab[0] / 255.0) * 100.0
    a_star = median_lab[1] - 128.0
    b_star = median_lab[2] - 128.0

    lab_pixel = np.uint8([[[ (L_star / 100.0) * 255.0, a_star + 128.0, b_star + 128.0 ]]])
    bgr_pixel = cv2.cvtColor(lab_pixel, cv2.COLOR_LAB2BGR)[0][0]
    
    r_val, g_val, b_val = int(bgr_pixel[2]), int(bgr_pixel[1]), int(bgr_pixel[0])
    hex_color = f"#{r_val:02x}{g_val:02x}{b_val:02x}"

    return (L_star, a_star, b_star), (r_val, g_val, b_val), hex_color


def _detect_depth_and_undertone(L_star, a_star, b_star):
    """تحديد عمق البشرة والـ Undertone ثنائي الخيار (Warm / Cool) فقط"""
    b_safe = b_star if abs(b_star) > 0.001 else 0.001
    ita_angle = (math.atan2(L_star - 50.0, b_safe) / math.pi) * 180.0

    # Depth (Fair / Medium / Dark)
    if ita_angle > 41.0:
        depth = "Fair"
    elif 10.0 < ita_angle <= 41.0:
        depth = "Medium"
    else:
        depth = "Dark"

    # Undertone ثنائي (Warm / Cool فقط)
    hue_angle = math.degrees(math.atan2(b_star, a_star)) % 360.0
    if hue_angle >= 42.5:
        undertone = "Warm"
    else:
        undertone = "Cool"

    return depth, undertone, ita_angle


# ══════════════════════════════════════════════════════════════════
# ADVANCED SKIN TYPE DETECTION
# ══════════════════════════════════════════════════════════════════

def _detect_skin_type_advanced(img_bgr, skin_mask, t_mask, u_mask):
    """تحديد نوع البشرة بناءً على انعكاسات الإضاءة وتباين الـ T-Zone والـ U-Zone"""
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    def calc_highlights_ratio(zone_mask):
        total = np.sum(zone_mask == 255)
        if total == 0:
            return 0.0
        val = hsv[:, :, 2]
        sat = hsv[:, :, 1]
        highlights = (val > 210) & (sat < 50) & (zone_mask == 255)
        return (np.sum(highlights) / total) * 100.0

    t_highlight = calc_highlights_ratio(t_mask)
    u_highlight = calc_highlights_ratio(u_mask)
    overall_highlight = calc_highlights_ratio(skin_mask)

    texture_std = float(np.std(gray[skin_mask == 255])) if np.sum(skin_mask == 255) > 0 else 0.0

    if t_highlight > 4.5 and u_highlight > 4.0:
        skin_type = "Oily"
        confidence = 0.85
    elif t_highlight > 4.0 and u_highlight <= 2.5:
        skin_type = "Combination"
        confidence = 0.88
    elif overall_highlight < 1.0 and texture_std < 16.0:
        skin_type = "Dry"
        confidence = 0.82
    else:
        skin_type = "Normal"
        confidence = 0.80

    return skin_type, confidence


# ══════════════════════════════════════════════════════════════════
# MAIN ANALYSIS FUNCTIONS
# ══════════════════════════════════════════════════════════════════

def analyze_skin_from_image(image_source) -> SkinAnalysisResult:
    """تحليل البشرة من صورة وإرجاع كائن SkinAnalysisResult"""
    try:
        if isinstance(image_source, str):
            if not os.path.exists(image_source):
                return SkinAnalysisResult(success=False, error=f"Cannot find image: {image_source}")
            image = cv2.imread(image_source)
            if image is None:
                return SkinAnalysisResult(success=False, error=f"Cannot read image: {image_source}")
        else:
            image = image_source

        h, w, _ = image.shape
        img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)

        with vision.FaceLandmarker.create_from_options(options) as landmarker:
            detection_result = landmarker.detect(mp_image)

        if not detection_result.face_landmarks:
            return SkinAnalysisResult(success=False, error="No face detected in the image")

        landmarks = detection_result.face_landmarks[0]
        skin_mask, t_mask, u_mask = _extract_skin_mask_and_zones(image, landmarks, h, w)

        skin_pixels = image[skin_mask == 255]
        if len(skin_pixels) == 0:
            return SkinAnalysisResult(success=False, error="Could not extract valid skin pixels")

        # 1. استخراج اللون
        lab_tuple, rgb_tuple, hex_color = _extract_lab_and_rgb_color(skin_pixels)

        # 2. تحديد العمق والـ Undertone (Warm / Cool)
        depth, undertone, _ = _detect_depth_and_undertone(lab_tuple[0], lab_tuple[1], lab_tuple[2])

        # 3. تحديد نوع البشرة
        skin_type, skin_type_conf = _detect_skin_type_advanced(image, skin_mask, t_mask, u_mask)

        overall_confidence = (0.90 + skin_type_conf) / 2

        return SkinAnalysisResult(
            success=True,
            skin_depth=depth,
            undertone=undertone,
            skin_type=skin_type,
            color_lab={
                'L': float(lab_tuple[0]),
                'a': float(lab_tuple[1]),
                'b': float(lab_tuple[2])
            },
            color_rgb=rgb_tuple,
            color_hex=hex_color,
            confidence=float(overall_confidence)
        )

    except Exception as e:
        return SkinAnalysisResult(success=False, error=str(e))


def analyze_skin_from_image_dict(image_source) -> Dict:
    result = analyze_skin_from_image(image_source)
    
    if not result.success:
        return {
            'success': False,
            'error': result.error
        }
    
    return {
        'success': True,
        'skin_depth': result.skin_depth,
        'undertone': result.undertone,
        'skin_type': result.skin_type,
        'color_lab': result.color_lab,
        'color_rgb': result.color_rgb,
        'color_hex': result.color_hex,
        'confidence': result.confidence
    }


# ══════════════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import json
    
    print("Analyzing skin from file...")
    result = analyze_skin_from_image('pictures3/warm14.jpg')

    if result.success:
        print(f"✓ Analysis successful!")
        print(f"  Depth: {result.skin_depth}")
        print(f"  Undertone: {result.undertone}")
        print(f"  Skin Type: {result.skin_type}")
        print(f"  Confidence: {result.confidence:.2%}")
    else:
        print(f"✗ Error: {result.error}")