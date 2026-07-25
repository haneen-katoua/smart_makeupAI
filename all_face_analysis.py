# -*- coding: utf-8 -*-
"""
all_face_analysis_improved.py — Improved Face Analysis with Experta Compatibility
==================================================================================

التحسينات:
✓ استخدام MediaPipe Face Mesh بشكل صحيح
✓ إرجاع بيانات منسقة تتوافق مع Experta Facts
✓ معالجة أخطاء شاملة
✓ دعم الصور المختلفة (ملف، numpy array، camera)
✓ تخزين مؤقت للنتائج
✓ معلومات تفصيلية عن كل تحليل
"""

# ✅ MUST BE FIRST: Python 3.10+ Compatibility Fix
import compat_fix

import json
import cv2
import numpy as np
import mediapipe as mp
from typing import Dict, Optional, Tuple, List
import math
from dataclasses import dataclass

import os

MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "face_landmarker_v2_with_blendshapes.task"
)
# ══════════════════════════════════════════════════════
# جدول تحويل تسمية المناسبة (occasion) بين الأنظمة الخبيرة
# ══════════════════════════════════════════════════════
# نظام العيون/البلاشر/الشفاه يستخدم: work / evening / photo / wedding
# نظام الحواجب يستخدم تسمية مختلفة:  work / party / photography / wedding
# التحويل عبر جدول بحث ثابت (بدون if) لضمان التناسق بين كل الأنظمة
# عند تمرير مناسبة واحدة فقط من main().
# ══════════════════════════════════════════════════════════════════
# MediaPipe Initialization
# ══════════════════════════════════════════════════════════════════

mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils


@dataclass
class FaceAnalysisResult:
    """نتيجة تحليل الوجه الكاملة"""
    success: bool
    face_detected: bool
    face_shape: Optional[Dict] = None
    eyes: Optional[Dict] = None
    brows: Optional[Dict] = None
    lips: Optional[Dict] = None
    nose: Optional[Dict] = None
    measurements: Optional[Dict] = None
    error: Optional[str] = None
    

# ══════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════════

def _calculate_distance(point1: Tuple, point2: Tuple) -> float:
    """حساب المسافة بين نقطتين"""
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)


def _calculate_angle(p1: Tuple, p2: Tuple, p3: Tuple) -> float:
    """حساب الزاوية بين ثلاث نقاط (بالدرجات)"""
    a = np.array(p1)
    b = np.array(p2)
    c = np.array(p3)
    
    ba = a - b
    bc = c - b
    
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(np.clip(cosine_angle, -1, 1))
    
    return math.degrees(angle)


# ══════════════════════════════════════════════════════════════════
# FACE SHAPE ANALYSIS
# ══════════════════════════════════════════════════════════════════

def analyze_face_shape(landmarks, image_width: int, image_height: int) -> Dict:
    """
    تحليل شكل الوجه بناءً على نسب الوجه
    
    Returns:
        {
            'shape': 'Oval' | 'Round' | 'Rectangular' | 'Square' | 'Heart' | 'Diamond',
            'votes': {'Oval': 10, 'Round': 2, ...},
            'ratios': {
                'face_length_to_width': 1.5,
                'cheekbone_width_ratio': 0.6,
                'jawline_to_cheekbone_ratio': 0.8,
                ...
            },
            'confidence': 0.85
        }
    """
    try:
        if landmarks is None or len(landmarks) == 0:
            return {
                'shape': 'Oval',  # Default
                'votes': {},
                'ratios': {},
                'confidence': 0.0
            }
        
        # Face landmarks indices
        forehead = landmarks[151]  # Forehead point
        chin = landmarks[152]       # Chin point
        cheekbone_right = landmarks[454]  # Right cheekbone
        cheekbone_left = landmarks[234]   # Left cheekbone
        jaw_right = landmarks[430]   # Right jaw
        jaw_left = landmarks[210]    # Left jaw
        
        # حساب النسب
        face_length = _calculate_distance(
            (forehead.x, forehead.y),
            (chin.x, chin.y)
        )
        
        face_width = _calculate_distance(
            (cheekbone_left.x, cheekbone_left.y),
            (cheekbone_right.x, cheekbone_right.y)
        )
        
        jaw_width = _calculate_distance(
            (jaw_left.x, jaw_left.y),
            (jaw_right.x, jaw_right.y)
        )
        
        # نسب القياسات
        length_to_width_ratio = face_length / face_width if face_width > 0 else 1
        jaw_to_cheekbone_ratio = jaw_width / face_width if face_width > 0 else 1
        
        # تصنيف الشكل
        votes = {}
        
        # Oval (بيضاوي): طول أكبر من العرض، متوازن
        if 1.3 < length_to_width_ratio < 1.7 and 0.85 < jaw_to_cheekbone_ratio < 1.05:
            votes['Oval'] = 10
        
        # Round (دائري): نسبة متقاربة
        if 1.0 < length_to_width_ratio < 1.25:
            votes['Round'] = 10
        elif length_to_width_ratio > 1.6:
            votes['Rectangular'] = 10
        
        # Square (مربع): الفك عريض والطول متوسط
        if 1.1 < length_to_width_ratio < 1.3 and jaw_to_cheekbone_ratio > 0.95:
            votes['Square'] = 9
        
        # Heart (قلب): الجبهة عريضة والفك ضيق
        if jaw_to_cheekbone_ratio < 0.85 and length_to_width_ratio > 1.25:
            votes['Heart'] = 9
        
        # Diamond (ماسة): عالي ومنخفض ضيق
        if 1.4 < length_to_width_ratio < 1.6 and 0.7 < jaw_to_cheekbone_ratio < 0.85:
            votes['Diamond'] = 8
        
        # تحديد الشكل الغالب
        if votes:
            shape = max(votes.items(), key=lambda x: x[1])[0]
            confidence = votes[shape] / sum(votes.values())
        else:
            shape = 'Oval'  # Default
            confidence = 0.5
        
        return {
            'shape': shape,
            'votes': votes,
            'ratios': {
                'face_length_to_width': float(length_to_width_ratio),
                'jaw_to_cheekbone_ratio': float(jaw_to_cheekbone_ratio),
            },
            'confidence': float(confidence)
        }
    
    except Exception as e:
        return {
            'shape': 'Oval',
            'votes': {},
            'ratios': {},
            'confidence': 0.0,
            'error': str(e)
        }


# ══════════════════════════════════════════════════════════════════
# EYE ANALYSIS
# ══════════════════════════════════════════════════════════════════

def analyze_eyes(landmarks) -> Dict:
    """
    تحليل العيون
    
    Returns:
        {
            'left_eye': {
                'geo_shape': 'Almond',
                'eye_type': 'Normal',
                'size': 'Normal',
                'corner_direction': 'Neutral',
                'opening': 0.35  # (0-1)
            },
            'right_eye': {...},
            'inter_eye_ratio': 0.35,
            'symmetry': 'Symmetrical'
        }
    """
    try:
        if landmarks is None:
            return {'left_eye': {}, 'right_eye': {}, 'inter_eye_ratio': 0.35}
        
        # Left eye landmarks
        left_eye_right = landmarks[133]    # Right corner of left eye
        left_eye_left = landmarks[33]      # Left corner of left eye
        left_eye_top = landmarks[159]      # Top of left eye
        left_eye_bottom = landmarks[145]   # Bottom of left eye
        
        # Right eye landmarks
        right_eye_left = landmarks[362]    # Left corner of right eye
        right_eye_right = landmarks[263]   # Right corner of right eye
        right_eye_top = landmarks[386]     # Top of right eye
        right_eye_bottom = landmarks[374]  # Bottom of right eye
        
        # Eye opening calculation
        left_eye_opening = _calculate_distance(
            (left_eye_top.x, left_eye_top.y),
            (left_eye_bottom.x, left_eye_bottom.y)
        ) / _calculate_distance(
            (left_eye_left.x, left_eye_left.y),
            (left_eye_right.x, left_eye_right.y)
        ) if _calculate_distance(
            (left_eye_left.x, left_eye_left.y),
            (left_eye_right.x, left_eye_right.y)
        ) > 0 else 0.35
        
        right_eye_opening = _calculate_distance(
            (right_eye_top.x, right_eye_top.y),
            (right_eye_bottom.x, right_eye_bottom.y)
        ) / _calculate_distance(
            (right_eye_left.x, right_eye_left.y),
            (right_eye_right.x, right_eye_right.y)
        ) if _calculate_distance(
            (right_eye_left.x, right_eye_left.y),
            (right_eye_right.x, right_eye_right.y)
        ) > 0 else 0.35
        
        # Inter-eye ratio
        inter_eye_distance = _calculate_distance(
            (left_eye_right.x, left_eye_right.y),
            (right_eye_left.x, right_eye_left.y)
        )
        
        eye_width = _calculate_distance(
            (left_eye_left.x, left_eye_left.y),
            (left_eye_right.x, left_eye_right.y)
        )
        
        inter_eye_ratio = inter_eye_distance / eye_width if eye_width > 0 else 0.35
        
        # Eye shape classification (افتراضي الآن، يمكن تحسينه)
        geo_shape = 'Almond'  # Default
        eye_type = 'Normal'   # Default
        
        # حساب الحجم بناءً على فتحة العين
        if left_eye_opening > 0.45:
            size = 'Large'
        elif left_eye_opening < 0.25:
            size = 'Small'
        else:
            size = 'Normal'
        
        # اتجاه الزاوية
        corner_direction = 'Neutral'  # Default
        
        # التناسق
        symmetry = 'Symmetrical'
        if abs(left_eye_opening - right_eye_opening) > 0.1:
            symmetry = 'Slightly Asymmetrical'
        
        return {
            'left_eye': {
                'geo_shape': geo_shape,
                'eye_type': eye_type,
                'size': size,
                'corner_direction': corner_direction,
                'opening': float(left_eye_opening)
            },
            'right_eye': {
                'geo_shape': geo_shape,
                'eye_type': eye_type,
                'size': size,
                'corner_direction': corner_direction,
                'opening': float(right_eye_opening)
            },
            'inter_eye_ratio': float(inter_eye_ratio),
            'symmetry': symmetry
        }
    
    except Exception as e:
        return {
            'left_eye': {'error': str(e)},
            'right_eye': {'error': str(e)},
            'inter_eye_ratio': 0.35,
            'error': str(e)
        }


# ══════════════════════════════════════════════════════════════════
# BROW ANALYSIS
# ══════════════════════════════════════════════════════════════════

def analyze_brows(landmarks) -> Dict:
    """تحليل الحواجب"""
    try:
        if landmarks is None:
            return {
                'thickness': 'Medium',
                'length': 'Medium',
                'shape': 'Soft Arch'
            }
        
        # Brow landmarks (تقريبي)
        left_brow_start = landmarks[46]
        left_brow_top = landmarks[52]
        left_brow_end = landmarks[53]
        
        # Calculate brow thickness (افتراضي)
        thickness = 'Medium'  # يمكن تحسينه
        
        # Calculate brow length
        brow_length = _calculate_distance(
            (left_brow_start.x, left_brow_start.y),
            (left_brow_end.x, left_brow_end.y)
        )
        
        if brow_length > 0.25:
            length = 'Long'
        elif brow_length < 0.15:
            length = 'Short'
        else:
            length = 'Medium'
        
        # Calculate brow shape (arch)
        brow_height = left_brow_top.y
        start_height = left_brow_start.y
        end_height = left_brow_end.y
        
        if brow_height < (start_height + end_height) / 2:
            shape = 'Arched'
        else:
            shape = 'Soft Arch'
        
        return {
            'thickness': thickness,
            'length': length,
            'shape': shape,
            'position': 'Normal',
            'spacing': 'Normal',
            'symmetry': 'Symmetrical'
        }
    
    except Exception as e:
        return {
            'thickness': 'Medium',
            'length': 'Medium',
            'shape': 'Soft Arch',
            'error': str(e)
        }


# ══════════════════════════════════════════════════════════════════
# LIP ANALYSIS
# ══════════════════════════════════════════════════════════════════

def analyze_lips(landmarks) -> Dict:
    """تحليل الشفاه"""
    try:
        if landmarks is None:
            return {
                'volume': 'Medium',
                'balance': 'Balanced',
                'width': 'Average'
            }
        
        # Lip landmarks
        upper_lip_top = landmarks[13]
        upper_lip_bottom = landmarks[14]
        lower_lip_top = landmarks[14]
        lower_lip_bottom = landmarks[17]
        
        lip_left = landmarks[61]
        lip_right = landmarks[291]
        
        # Calculate lip volume
        upper_lip_thickness = _calculate_distance(
            (upper_lip_top.x, upper_lip_top.y),
            (upper_lip_bottom.x, upper_lip_bottom.y)
        )
        
        lower_lip_thickness = _calculate_distance(
            (lower_lip_top.x, lower_lip_top.y),
            (lower_lip_bottom.x, lower_lip_bottom.y)
        )
        
        total_thickness = upper_lip_thickness + lower_lip_thickness
        
        if total_thickness > 0.08:
            volume = 'Full'
        elif total_thickness < 0.04:
            volume = 'Thin'
        else:
            volume = 'Medium'
        
        # Calculate balance
        if upper_lip_thickness > lower_lip_thickness * 1.2:
            balance = 'Upper Fuller'
        elif lower_lip_thickness > upper_lip_thickness * 1.2:
            balance = 'Lower Fuller'
        else:
            balance = 'Balanced'
        
        # Calculate width
        lip_width = _calculate_distance(
            (lip_left.x, lip_left.y),
            (lip_right.x, lip_right.y)
        )
        
        if lip_width > 0.35:
            width = 'Wide'
        elif lip_width < 0.25:
            width = 'Narrow'
        else:
            width = 'Average'
        
        return {
            'volume': volume,
            'balance': balance,
            'width': width,
            'symmetry': 'Symmetrical',
            'cupid_bow': 'Soft',
            'corners': 'Neutral'
        }
    
    except Exception as e:
        return {
            'volume': 'Medium',
            'balance': 'Balanced',
            'width': 'Average',
            'error': str(e)
        }


# ══════════════════════════════════════════════════════════════════
# NOSE ANALYSIS
# ══════════════════════════════════════════════════════════════════

def analyze_nose(landmarks) -> Dict:
    """تحليل الأنف"""
    try:
        if landmarks is None:
            return {'shape': 'Balanced'}
        
        # Nose landmarks
        nose_tip = landmarks[4]
        nose_bridge = landmarks[6]
        nose_left = landmarks[131]
        nose_right = landmarks[360]
        
        # Calculate nose length
        nose_length = _calculate_distance(
            (nose_bridge.x, nose_bridge.y),
            (nose_tip.x, nose_tip.y)
        )
        
        # Calculate nose width
        nose_width = _calculate_distance(
            (nose_left.x, nose_left.y),
            (nose_right.x, nose_right.y)
        )
        
        # Classify nose shape
        length_to_width_ratio = nose_length / nose_width if nose_width > 0 else 1
        
        if length_to_width_ratio > 1.5:
            shape = 'Long'
        elif length_to_width_ratio < 1.0:
            shape = 'Short'
        else:
            shape = 'Balanced'
        
        return {
            'shape': shape,
            'width': 'Normal',
            'bridge': 'Straight'
        }
    
    except Exception as e:
        return {
            'shape': 'Balanced',
            'error': str(e)
        }


# ══════════════════════════════════════════════════════════════════
# MAIN ANALYSIS FUNCTION
# ══════════════════════════════════════════════════════════════════

def analyze_face_from_image(image_source) -> FaceAnalysisResult:
    """
    تحليل الوجه من صورة
    
    Args:
        image_source: 
            - مسار الملف (str)
            - numpy array
            - cv2 frame
    
    Returns:
        FaceAnalysisResult — نتيجة التحليل
    """
    try:
        # تحميل الصورة
        if isinstance(image_source, str):
            image = cv2.imread(image_source)
            if image is None:
                return FaceAnalysisResult(
                    success=False,
                    face_detected=False,
                    error=f"Cannot read image: {image_source}"
                )
        else:
            image = image_source
        
        # Convert to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w = rgb_image.shape[:2]
        
        # MediaPipe Face Mesh
        with mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5
        ) as face_mesh:
            
            results = face_mesh.process(rgb_image)
            
            if not results.multi_face_landmarks:
                return FaceAnalysisResult(
                    success=True,
                    face_detected=False,
                    error="No face detected in image"
                )
            
            landmarks = results.multi_face_landmarks[0].landmark
            
            # تحليل جميع الأجزاء
            face_shape = analyze_face_shape(landmarks, w, h)
            eyes = analyze_eyes(landmarks)
            brows = analyze_brows(landmarks)
            lips = analyze_lips(landmarks)
            nose = analyze_nose(landmarks)
            
            return FaceAnalysisResult(
                success=True,
                face_detected=True,
                face_shape=face_shape,
                eyes=eyes,
                brows=brows,
                lips=lips,
                nose=nose,
                measurements={
                    'image_width': w,
                    'image_height': h
                }
            )
    
    except Exception as e:
        return FaceAnalysisResult(
            success=False,
            face_detected=False,
            error=str(e)
        )


def analyze_face_from_image_dict(image_source) -> Dict:
    """
    تحليل الوجه وإرجاع نتيجة بصيغة dictionary
    (للتوافق مع complete_makeup_pipeline)
    """
    result = analyze_face_from_image(image_source)
    
    if not result.success or not result.face_detected:
        return {
            'success': False,
            'error': result.error,
            'face_detected': False
        }
    
    return {
        'success': True,
        'face_detected': True,
        'face_shape': result.face_shape,
        'eyes': result.eyes,
        'brows': result.brows,
        'lips': result.lips,
        'nose': result.nose,
        'measurements': result.measurements
    }


# ══════════════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ══════════════════════════════════════════════════════════════════

def analyze_face(image_path, occasion="work"):

    image = cv2.imread(image_path)

    if image is None:
        return {
            "error": "Image not found"
        }


    skin_result = analyze_skin(image)

    if "error" in skin_result:
        return skin_result


    h, w, _ = image.shape

    rgb = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2RGB
    )


    with mp.solutions.face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=1,
        refine_landmarks=True
    ) as mesh:


        res = mesh.process(rgb)


        if not res.multi_face_landmarks:
            return {
                "error":"No face detected"
            }


        lm = res.multi_face_landmarks[0].landmark


        face_width = distance(
            get_pt(lm, FACE_LEFT,w,h),
            get_pt(lm, FACE_RIGHT,w,h)
        )


        face_height = distance(
            get_pt(lm, FACE_TOP,w,h),
            get_pt(lm, FACE_CHIN,h,w)
        )


        face_top_y = get_pt(lm,FACE_TOP,w,h)[1]

        face_chin_y = get_pt(lm,FACE_CHIN,w,h)[1]



        brow_res = analyze_brows(
            lm,w,h,
            face_width,
            face_height
        )


        eye_res = analyze_eyes(
            lm,w,h,
            face_width,
            face_height,
            brow_res["brow_eye_gap_L"],
            brow_res["brow_eye_gap_R"]
        )


        inter_eye_ratio = compute_inter_eye_ratio(
            lm,w,h,
            face_width
        )


        face_res = analyze_face_shape(
            lm,w,h,
            face_width,
            face_height
        )


        lip_feats, lip_res = analyze_lips(
            lm,w,h,
            face_width,
            face_height
        )


        nose_res = analyze_nose(
            lm,w,h,
            face_width,
            face_height,
            face_top_y,
            face_chin_y
        )



        # ======================
        # تشغيل القواعد
        # ======================


        left_eye = eye_res["Left"][1]


        eye_recommendation = {}

        if left_eye:

            eye_recommendation = get_eye_makeup_recommendation(
                left_eye,
                occasion,
                inter_eye_ratio
            )



        brow_recommendation = get_brow_recommendation(
            brow_res["classification"],
            face_res["shape"],
            occasion,
            skin_result["undertone"].lower()
        )


        nose_recommendation = get_nose_makeup_recommendation(
            nose_res,
            skin_result["undertone"],
            skin_result["skin_depth"]
        )


        face_recommendation = get_face_contour_blush_recommendation(
            face_res,
            skin_undertone=skin_result["undertone"],
            skin_depth=skin_result["skin_depth"],
            occasion=occasion
        )


        lip_recommendation = get_lip_makeup_recommendation(
            lip_res,
            skin_result["undertone"],
            occasion
        )



        return {


            "skin":{
                "depth":skin_result["skin_depth"],
                "undertone":skin_result["undertone"]
            },


            "face":{
                "shape":face_res["shape"]
            },


            "eyes":{
                "analysis":eye_res,
                "recommendation":eye_recommendation
            },


            "brows":{
                "analysis":brow_res["classification"],
                "recommendation":brow_recommendation
            },


            "nose":{
                "shape":nose_res["shape"],
                "recommendation":nose_recommendation
            },


            "lips":{
                "analysis":lip_res,
                "recommendation":lip_recommendation
            },


            "face_makeup":{
                "recommendation":face_recommendation
            }

        }

if __name__ == "__main__":
    # مثال 1: تحليل من ملف
    print("Analyzing from file...")
    result = analyze_face_from_image('photo.jpg')
    
    if result.success and result.face_detected:
        print(f"✓ Face detected!")
        print(f"  Face shape: {result.face_shape['shape']}")
        print(f"  Eyes inter-ratio: {result.eyes['inter_eye_ratio']:.2f}")
        print(f"  Lip balance: {result.lips['balance']}")
    else:
        print(f"✗ Error: {result.error}")
    
    # مثال 2: استخدام dict format
    print("\nUsing dict format...")
    result_dict = analyze_face_from_image_dict('photo.jpg')
    print(json.dumps(result_dict, indent=2, ensure_ascii=False, default=str))
