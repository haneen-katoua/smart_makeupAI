# -*- coding: utf-8 -*-
"""
all_face_analysis_fixed.py — Fixed & Optimized Face Analysis
============================================================

هذا الملف يصحّح أخطاء حقيقية موجودة في النسخة السابقة (all_face_analysis_fixed
القديمة) كانت تجعل كل الصور تُصنَّف بنفس القيم الثابتة بدل قيم مُشتقة من الصورة
فعلياً. الأخطاء التي تم إصلاحها:

1) العينان (geo_shape / eye_type):
   - كانت الدالة القديمة تُرجع 'Almond' و 'Normal' كنص ثابت (hardcoded) لكل
     الصور، بدل استدعاء أي منطق تصنيف هندسي. تم استرجاع/تطوير التصنيف الحقيقي:
       • geo_shape يُحسب من نسبة العرض/الارتفاع الفعلية لكل عين.
       • eye_type (Hooded / Protruding / Deep-set / Droopy / Round / Almond)
         يُحسب من: (أ) المسافة بين الحاجب وخط الرمش العلوي (الجفن الظاهر) —
         لكشف Hooded، (ب) إحداثي العمق z من MediaPipe لكشف Protruding/Deep-set،
         (ج) زاوية الميل بين الزاوية الداخلية والخارجية (canthal tilt) لكشف
         Droopy، (د) نسبة العرض/الارتفاع لكشف Round.
   - أيضاً كان hair-bug: inter_eye_ratio يُقسَم على عرض عين واحدة فقط بدل
     متوسط عرض العينين → تم تصحيحه.

2) الحواجب: كانت thickness/shape/position/spacing جميعها نصوصاً ثابتة
   ('Medium' / 'Soft Arch' / 'Normal' دائماً). تم حساب:
       • thickness من المسافة العمودية بين الحد العلوي والسفلي لشعر الحاجب.
       • shape من عمق القوس الفعلي (peak مقابل بداية/نهاية الحاجب).
       • position من ارتفاع الحاجب فوق العين نسبة لعرض العين.
       • spacing من المسافة بين طرفي الحاجبين الداخليين نسبة للمسافة بين العينين.

3) الشفاه: كان هناك خطأ فادح في اختيار نقاط MediaPipe — كانت الدالة تستخدم
   النقطتين 13 و14 لحساب "سماكة الشفة العلوية"، وهاتان النقطتان متلاصقتان عند
   خط التقاء الشفتين (السيم) وليس عند حافة الشفة العلوية الخارجية، فتكون
   المسافة بينهما شبه صفرية دائماً → هذا ما كان يجعل كل صورة تُصنَّف
   volume='Thin' و balance='Lower Fuller' بلا استثناء. تم تصحيح النقاط:
       • سماكة الشفة العلوية = المسافة بين النقطة 0 (الحافة الخارجية العلوية)
         والنقطة 13 (خط الالتقاء العلوي).
       • سماكة الشفة السفلى = المسافة بين النقطة 14 (خط الالتقاء السفلي)
         والنقطة 17 (الحافة الخارجية السفلى).
   كما تم حساب cupid_bow (عمق انحناء القوس) و corners (اتجاه زاوية الفم)
   فعلياً بدل تثبيتهما على 'Soft' / 'Neutral'.

4) الأنف: width و bridge كانا ثابتين ('Normal' / 'Straight' دائماً). تم حساب:
       • width من عرض المنخرين الفعلي نسبة لعرض الوجه.
       • bridge (Straight/Convex/Concave) تقريبياً من انحراف نقطة منتصف
         الجسر عن الخط الواصل بين بداية الجسر وطرف الأنف (باستخدام x وz معاً).

5) شكل الوجه: تمت إضافة تصنيف Triangle (وجه كمثري/مثلث: الفك أعرض من عظمة
   الخد) والذي كان مفقوداً تماماً رغم أن brow_makeup_rules.py يحتوي قاعدة له.

ملاحظة مهمة: أي تصنيف هندسي من صورة أمامية (2D + z تقريبي من MediaPipe) هو
تقدير وليس قياساً طبياً دقيقاً 100%. لكن الفرق الجوهري عن النسخة القديمة أن كل
القيم الآن تُشتق فعلياً من إحداثيات الصورة وتتغيّر بتغيّر الصورة، بدل أن تكون
سلاسل نصية مثبّتة مسبقاً.
"""

# ✅ MUST BE FIRST: Python 3.10+ Compatibility Fix
import sys
sys.path.insert(0, '/mnt/project')
import compat_fix

import json
import cv2
import numpy as np
import mediapipe as mp
from typing import Dict, Optional, Tuple, List
import math
from dataclasses import dataclass, asdict


# ══════════════════════════════════════════════════════════════════
# MediaPipe Initialization
# ══════════════════════════════════════════════════════════════════

mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

# MediaPipe Face Mesh landmark indices (تحقّقنا منها مقابل الطوبولوجيا الرسمية)
LANDMARK_INDICES = {
    # الوجه العام
    'forehead': 10,
    'chin': 152,
    'left_cheekbone': 234,
    'right_cheekbone': 454,
    'left_jaw': 210,
    'right_jaw': 430,
    'left_temple': 127,
    'right_temple': 356,

    # الأنف
    'nose_tip': 4,
    'nose_bridge_top': 6,
    'nose_bridge_mid': 197,
    'nose_left': 131,
    'nose_right': 360,
    'nose_ala_left': 129,
    'nose_ala_right': 358,

    # العين اليسرى (تسمية حسب اصطلاح المشروع الأصلي: outer بعيدة عن الأنف)
    'left_eye_outer': 33,
    'left_eye_inner': 133,
    'left_eye_top': 159,
    'left_eye_bottom': 145,
    'left_eye_top_outer': 160,
    'left_eye_top_inner': 158,

    # العين اليمنى
    'right_eye_outer': 263,
    'right_eye_inner': 362,
    'right_eye_top': 386,
    'right_eye_bottom': 374,
    'right_eye_top_outer': 385,
    'right_eye_top_inner': 387,

    # الحاجب الأيسر (بداية/قمة/نهاية) + كنتور علوي/سفلي لحساب السماكة
    'left_brow_start': 46,
    'left_brow_peak': 52,
    'left_brow_end': 53,
    'left_brow_upper': [70, 63, 105, 66, 107],
    'left_brow_lower': [46, 53, 52, 65, 55],

    # الحاجب الأيمن
    'right_brow_start': 276,
    'right_brow_peak': 282,
    'right_brow_end': 283,
    'right_brow_upper': [300, 293, 334, 296, 336],
    'right_brow_lower': [276, 283, 282, 295, 285],

    # الشفاه (مصححة)
    'upper_lip_outer_top': 0,      # الحافة الخارجية العلوية لأعلى نقطة بالشفة العليا
    'upper_lip_inner_bottom': 13,  # خط التقاء الشفتين (الجزء العلوي منه)
    'lower_lip_inner_top': 14,     # خط التقاء الشفتين (الجزء السفلي منه)
    'lower_lip_outer_bottom': 17,  # الحافة الخارجية السفلى لأسفل نقطة بالشفة السفلى
    'lip_left': 61,
    'lip_right': 291,
    'cupid_bow_left_peak': 37,
    'cupid_bow_right_peak': 267,
    'cupid_bow_dip': 0,
}


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

    def to_dict(self):
        return asdict(self)


# ══════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════════

def _safe_get_landmark(landmarks, index: int) -> Optional[Tuple[float, float, float]]:
    """استخراج آمن للنقطة (x, y, z) مع معالجة الأخطاء. z مفيد لتقدير العمق."""
    try:
        if landmarks is None or index >= len(landmarks):
            return None
        lm = landmarks[index]
        return (float(lm.x), float(lm.y), float(getattr(lm, 'z', 0.0)))
    except (AttributeError, IndexError, TypeError):
        return None


def _xy(point: Optional[Tuple]) -> Optional[Tuple[float, float]]:
    """يرجع (x, y) فقط من نقطة (x, y, z)."""
    if point is None:
        return None
    return (point[0], point[1])


def _calculate_distance(point1: Optional[Tuple], point2: Optional[Tuple]) -> float:
    """حساب المسافة الإقليدية بين نقطتين (2D)، يتجاهل z إن وُجدت."""
    if point1 is None or point2 is None:
        return 0.0
    try:
        dx = point1[0] - point2[0]
        dy = point1[1] - point2[1]
        return math.sqrt(dx * dx + dy * dy)
    except (TypeError, IndexError):
        return 0.0


def _calculate_angle_deg(p1: Optional[Tuple], p2: Optional[Tuple]) -> float:
    """زاوية الخط الواصل بين نقطتين بالنسبة للأفقي (بالدرجات).
    موجبة = تتجه للأسفل (لأن محور y يتجه للأسفل في إحداثيات الصورة)."""
    if p1 is None or p2 is None:
        return 0.0
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    if dx == 0 and dy == 0:
        return 0.0
    return math.degrees(math.atan2(dy, dx))


def _canthal_tilt_deg(inner: Optional[Tuple], outer: Optional[Tuple]) -> float:
    """ميل زاوية العين (canthal tilt) من الزاوية الداخلية للخارجية، بشكل
    مستقل عن اتجاه المحور الأفقي. خطأ حقيقي كان موجوداً هنا: العين اليسرى
    والعين اليمنى لهما اتجاه x معاكس (الزاوية الخارجية تقع يميناً لعين
    ويساراً للأخرى)، فاستخدام atan2(dy, dx) مباشرة كان يعطي زاوية قريبة من
    180° للعين اليسرى بدل قريبة من 0° كما هو متوقّع لعين مستقيمة، مما كان
    يُفسِد كشف Droopy/Upturned تحديداً بالعين اليسرى. الحل: نأخذ dx دائماً
    كموجب (اتجاه "للخارج") بغض النظر عن جهة العين."""
    if inner is None or outer is None:
        return 0.0
    dx = abs(outer[0] - inner[0])
    dy = outer[1] - inner[1]
    if dx == 0 and dy == 0:
        return 0.0
    return math.degrees(math.atan2(dy, dx))


def _avg_point(points: List[Optional[Tuple]]) -> Optional[Tuple[float, float, float]]:
    pts = [p for p in points if p is not None]
    if not pts:
        return None
    n = len(pts)
    return (
        sum(p[0] for p in pts) / n,
        sum(p[1] for p in pts) / n,
        sum(p[2] for p in pts) / n if len(pts[0]) > 2 else 0.0,
    )


def _get_many(landmarks, indices: List[int]) -> List[Optional[Tuple]]:
    return [_safe_get_landmark(landmarks, i) for i in indices]


# ══════════════════════════════════════════════════════════════════
# FACE SHAPE ANALYSIS
# ══════════════════════════════════════════════════════════════════

def analyze_face_shape(landmarks, image_width: int, image_height: int) -> Dict:
    """تحليل شكل الوجه بناءً على نسب دقيقة (بما فيها Triangle المفقود سابقاً)."""
    try:
        if landmarks is None or len(landmarks) == 0:
            return {'shape': 'Oval', 'votes': {}, 'ratios': {}, 'confidence': 0.0}

        forehead = _safe_get_landmark(landmarks, LANDMARK_INDICES['forehead'])
        chin = _safe_get_landmark(landmarks, LANDMARK_INDICES['chin'])
        cheekbone_left = _safe_get_landmark(landmarks, LANDMARK_INDICES['left_cheekbone'])
        cheekbone_right = _safe_get_landmark(landmarks, LANDMARK_INDICES['right_cheekbone'])
        jaw_left = _safe_get_landmark(landmarks, LANDMARK_INDICES['left_jaw'])
        jaw_right = _safe_get_landmark(landmarks, LANDMARK_INDICES['right_jaw'])
        temple_left = _safe_get_landmark(landmarks, LANDMARK_INDICES['left_temple'])
        temple_right = _safe_get_landmark(landmarks, LANDMARK_INDICES['right_temple'])

        if None in [forehead, chin, cheekbone_left, cheekbone_right, jaw_left, jaw_right]:
            return {'shape': 'Oval', 'votes': {}, 'ratios': {}, 'confidence': 0.0}

        face_length = _calculate_distance(forehead, chin)
        face_width = _calculate_distance(cheekbone_left, cheekbone_right)
        jaw_width = _calculate_distance(jaw_left, jaw_right)
        forehead_width = _calculate_distance(temple_left, temple_right) if None not in [temple_left, temple_right] else face_width

        if face_width == 0 or face_length == 0:
            return {'shape': 'Oval', 'votes': {}, 'ratios': {}, 'confidence': 0.0}

        length_to_width = face_length / face_width
        jaw_to_cheekbone = jaw_width / face_width
        forehead_to_jaw = forehead_width / jaw_width if jaw_width > 0 else 1.0

        votes = {}

        if 1.25 < length_to_width < 1.75 and 0.85 < jaw_to_cheekbone < 1.05:
            votes['Oval'] = 10
        if 1.0 < length_to_width < 1.25:
            votes['Round'] = 10
        if length_to_width > 1.65:
            votes['Rectangular'] = 9
        if 1.15 < length_to_width < 1.35 and jaw_to_cheekbone > 0.92:
            votes['Square'] = 9
        if jaw_to_cheekbone < 0.82 and length_to_width > 1.3:
            votes['Heart'] = 8
        if 1.35 < length_to_width < 1.65 and 0.75 < jaw_to_cheekbone < 0.88:
            votes['Diamond'] = 8
        # Triangle/كمثري: الفك أعرض بوضوح من عظمة الخد والجبهة (كان مفقوداً)
        if jaw_to_cheekbone > 1.05 and forehead_to_jaw < 0.95:
            votes['Triangle'] = 9

        if votes:
            shape = max(votes.items(), key=lambda x: x[1])[0]
            confidence = min(votes[shape] / sum(votes.values()), 1.0)
        else:
            shape = 'Oval'
            confidence = 0.4

        return {
            'shape': shape,
            'votes': votes,
            'ratios': {
                'face_length_to_width': float(length_to_width),
                'jaw_to_cheekbone_ratio': float(jaw_to_cheekbone),
                'forehead_to_jaw_ratio': float(forehead_to_jaw),
            },
            'confidence': float(confidence)
        }

    except Exception as e:
        return {'shape': 'Oval', 'votes': {}, 'ratios': {}, 'confidence': 0.0, 'error': str(e)}


# ══════════════════════════════════════════════════════════════════
# EYE ANALYSIS
# ══════════════════════════════════════════════════════════════════

def _detect_eye_type(landmarks, side: str, eye_width: float, eye_height: float,
                      inner: Optional[Tuple], outer: Optional[Tuple],
                      z_reference: Optional[float]) -> str:
    """
    كشف النوع الوظيفي للعين اعتماداً على إشارات هندسية حقيقية، بترتيب أولوية
    تمت مراجعته مقابل ملف "الخبرة النهائية" (6 أنواع فقط، بلا زيادة أو نقصان):
    Hooded, Protruding, Almond, Round, Droopy, Deep-set.

    ترتيب الفحص (مهم لأن Hooded كانت لا تظهر أبداً سابقاً لأن فحص Droopy كان
    يُنفَّذ قبلها ويُغلق المسار بأي ميل بسيط بالزاوية):
      1) Hooded  — أولاً: مسافة صغيرة بين أسفل الحاجب وخط الرمش العلوي
      2) Droopy  — عتبة ميل أعلى (6 درجات بدل 4) لتفادي الحساسية الزائدة
      3) Protruding / Deep-set — عمق z مقارنة بجسر الأنف
      4) Round / Almond — تصنيف هندسي نهائي (عتبة مخففة لصالح Round)
    """
    if eye_width <= 0:
        return 'Almond'

    # ── 1) Hooded: المسافة بين الحاجب وخط الرمش العلوي (فُحصت أولاً الآن) ──
    if side == 'left':
        brow_lower_idx = LANDMARK_INDICES['left_brow_lower']
        eye_top_idx = LANDMARK_INDICES['left_eye_top']
    else:
        brow_lower_idx = LANDMARK_INDICES['right_brow_lower']
        eye_top_idx = LANDMARK_INDICES['right_eye_top']

    brow_pts = _get_many(landmarks, brow_lower_idx)
    brow_avg = _avg_point(brow_pts)
    eye_top = _safe_get_landmark(landmarks, eye_top_idx)

    if brow_avg is not None and eye_top is not None:
        brow_to_lid_gap = abs(eye_top[1] - brow_avg[1])  # y فقط (رأسي)
        gap_ratio = brow_to_lid_gap / eye_width
        # عتبة مخففة (كانت 0.20 وتمنع أي عين من الوصول لهذا التصنيف عملياً).
        # القيمة النموذجية لعين غير مبطنة تقارب 0.30-0.45، وأي شيء أقل من ~0.30
        # يعني مساحة ظاهرة قليلة بين الحاجب والرمش، وهذا مؤشر Hooded معقول.
        if gap_ratio < 0.30:
            return 'Hooded'

    # ── 2) Canthal tilt (ميل زاوية العين) — عتبة أعلى لتقليل الحساسية الزائدة ──
    tilt = _canthal_tilt_deg(inner, outer)  # موجب = الزاوية الخارجية أسفل الداخلية
    if tilt > 6.0:
        return 'Droopy'

    # ── 3) العمق (z) لكشف Protruding / Deep-set ──
    if z_reference is not None and eye_top is not None:
        eye_z = eye_top[2]
        z_diff = eye_z - z_reference  # أصغر (أكثر سلبية) = أقرب للكاميرا = بارزة أكثر
        if z_diff < -0.012:
            return 'Protruding'
        if z_diff > 0.012:
            return 'Deep-set'

    # ── 4) الشكل الهندسي (Round) كخيار أخير قبل Almond ──
    # عتبة أكثر تحفظاً (كانت 2.6 وتُصنّف عيوناً لوزية حقيقية كـ Round بالخطأ).
    # اللوزية هي الحالة "المتوازنة" الافتراضية تشريحياً؛ فلا تُصنَّف Round إلا
    # عند نسبة عرض/ارتفاع منخفضة بوضوح (عين مستديرة فعلياً).
    ratio = eye_width / eye_height if eye_height > 0 else 3.0
    if ratio < 2.2:
        return 'Round'

    return 'Almond'


def analyze_eyes(landmarks) -> Dict:
    """تحليل العيون بدقة أعلى — كل القيم تُشتق فعلياً من هندسة الصورة."""
    try:
        if landmarks is None:
            return _default_eye_analysis()

        # نقطة مرجعية للعمق: جسر الأنف (منطقة مستقرة نسبياً في منتصف الوجه)
        nose_bridge = _safe_get_landmark(landmarks, LANDMARK_INDICES['nose_bridge_top'])
        z_reference = nose_bridge[2] if nose_bridge is not None else None

        # العين اليسرى
        left_inner = _safe_get_landmark(landmarks, LANDMARK_INDICES['left_eye_inner'])
        left_outer = _safe_get_landmark(landmarks, LANDMARK_INDICES['left_eye_outer'])
        left_top = _safe_get_landmark(landmarks, LANDMARK_INDICES['left_eye_top'])
        left_bottom = _safe_get_landmark(landmarks, LANDMARK_INDICES['left_eye_bottom'])

        # العين اليمنى
        right_inner = _safe_get_landmark(landmarks, LANDMARK_INDICES['right_eye_inner'])
        right_outer = _safe_get_landmark(landmarks, LANDMARK_INDICES['right_eye_outer'])
        right_top = _safe_get_landmark(landmarks, LANDMARK_INDICES['right_eye_top'])
        right_bottom = _safe_get_landmark(landmarks, LANDMARK_INDICES['right_eye_bottom'])

        if None in [left_inner, left_outer, left_top, left_bottom,
                    right_inner, right_outer, right_top, right_bottom]:
            return _default_eye_analysis()

        left_eye_width = _calculate_distance(left_inner, left_outer)
        left_eye_height = _calculate_distance(left_top, left_bottom)
        left_opening = left_eye_height / left_eye_width if left_eye_width > 0 else 0.35

        right_eye_width = _calculate_distance(right_inner, right_outer)
        right_eye_height = _calculate_distance(right_top, right_bottom)
        right_opening = right_eye_height / right_eye_width if right_eye_width > 0 else 0.35

        # مسافة بين العينين (بين الزاويتين الداخليتين) — مصححة لتقسم على المتوسط
        avg_eye_width = (left_eye_width + right_eye_width) / 2 if (left_eye_width + right_eye_width) > 0 else 1.0
        inter_eye_distance = _calculate_distance(left_inner, right_inner)
        inter_eye_ratio = inter_eye_distance / avg_eye_width if avg_eye_width > 0 else 1.0

        # الحجم
        avg_opening = (left_opening + right_opening) / 2
        if avg_opening > 0.45:
            size = 'Large'
        elif avg_opening < 0.25:
            size = 'Small'
        else:
            size = 'Normal'

        # الشكل الهندسي لكل عين (يُستخدم أيضاً داخل eye_type كخيار أخير)
        # نفس عتبة _detect_eye_type (2.2) لضمان اتساق geo_shape مع eye_type
        left_ratio = left_eye_width / left_eye_height if left_eye_height > 0 else 3.0
        right_ratio = right_eye_width / right_eye_height if right_eye_height > 0 else 3.0
        left_geo_shape = 'Round' if left_ratio < 2.2 else 'Almond'
        right_geo_shape = 'Round' if right_ratio < 2.2 else 'Almond'

        # النوع الوظيفي الحقيقي لكل عين (مستقل لكل جهة)
        left_eye_type = _detect_eye_type(landmarks, 'left', left_eye_width, left_eye_height,
                                          left_inner, left_outer, z_reference)
        right_eye_type = _detect_eye_type(landmarks, 'right', right_eye_width, right_eye_height,
                                           right_inner, right_outer, z_reference)

        # اتجاه الزاوية الخارجية (Upturned / Downturned / Neutral)
        left_tilt = _canthal_tilt_deg(left_inner, left_outer)
        right_tilt = _canthal_tilt_deg(right_inner, right_outer)

        def corner_dir(tilt):
            if tilt > 4.0:
                return 'Downturned'
            if tilt < -4.0:
                return 'Upturned'
            return 'Neutral'

        # التناسق
        symmetry = 'Symmetrical'
        if abs(left_opening - right_opening) > 0.1 or abs(left_eye_width - right_eye_width) > (avg_eye_width * 0.15):
            symmetry = 'Slightly Asymmetrical'

        return {
            'left_eye': {
                'geo_shape': left_geo_shape,
                'eye_type': left_eye_type,
                'size': size,
                'corner_direction': corner_dir(left_tilt),
                'opening': float(min(left_opening, 1.0)),
                'width': float(left_eye_width),
                'height': float(left_eye_height),
            },
            'right_eye': {
                'geo_shape': right_geo_shape,
                'eye_type': right_eye_type,
                'size': size,
                'corner_direction': corner_dir(right_tilt),
                'opening': float(min(right_opening, 1.0)),
                'width': float(right_eye_width),
                'height': float(right_eye_height),
            },
            'inter_eye_ratio': float(inter_eye_ratio),
            'symmetry': symmetry,
            'measurements': {
                'left_eye_aspect_ratio': float(left_opening),
                'right_eye_aspect_ratio': float(right_opening),
                'inter_eye_distance': float(inter_eye_distance),
            }
        }

    except Exception as e:
        result = _default_eye_analysis()
        result['error'] = str(e)
        return result


def _default_eye_analysis() -> Dict:
    """تحليل افتراضي للعيون عند فشل اكتشاف الوجه فقط (وليس قيمة عامة للتصنيف)."""
    return {
        'left_eye': {'geo_shape': 'Almond', 'eye_type': 'Almond', 'size': 'Normal',
                     'corner_direction': 'Neutral', 'opening': 0.35},
        'right_eye': {'geo_shape': 'Almond', 'eye_type': 'Almond', 'size': 'Normal',
                      'corner_direction': 'Neutral', 'opening': 0.35},
        'inter_eye_ratio': 1.0,
        'symmetry': 'Symmetrical'
    }


# ══════════════════════════════════════════════════════════════════
# BROW ANALYSIS
# ══════════════════════════════════════════════════════════════════

def analyze_brows(landmarks) -> Dict:
    """تحليل الحواجب — thickness/shape/position/spacing جميعها مُشتقة فعلياً."""
    try:
        if landmarks is None:
            return _default_brow_analysis()

        left_start = _safe_get_landmark(landmarks, LANDMARK_INDICES['left_brow_start'])
        left_peak = _safe_get_landmark(landmarks, LANDMARK_INDICES['left_brow_peak'])
        left_end = _safe_get_landmark(landmarks, LANDMARK_INDICES['left_brow_end'])
        right_start = _safe_get_landmark(landmarks, LANDMARK_INDICES['right_brow_start'])
        right_peak = _safe_get_landmark(landmarks, LANDMARK_INDICES['right_brow_peak'])
        right_end = _safe_get_landmark(landmarks, LANDMARK_INDICES['right_brow_end'])

        if None in [left_start, left_peak, left_end, right_start, right_peak, right_end]:
            return _default_brow_analysis()

        left_brow_length = _calculate_distance(left_start, left_end)
        right_brow_length = _calculate_distance(right_start, right_end)
        avg_brow_length = (left_brow_length + right_brow_length) / 2

        # ── مقياس مرجعي لحجم الوجه داخل الصورة (عرض عظمتي الخد) ──
        # هذا أساسي: إحداثيات MediaPipe مُطبَّعة على أبعاد الصورة كاملة، فنفس
        # الوجه يعطي مسافات "مطلقة" مختلفة تماماً حسب مدى تقريب/تأطير الصورة
        # (وجه يملأ الكادر يعطي أرقاماً أكبر من نفس الوجه في صورة بعيدة/عريضة).
        # اعتماد عتبات مطلقة على avg_brow_length هو ما كان يجعل كل الصور تقريباً
        # تُصنَّف بنفس القيمة (Short) بغضّ النظر عن طول الحاجب الحقيقي. الحل هو
        # تطبيع الطول على مقياس ثابت النسبة داخل نفس الوجه (عرض عظمتي الخد).
        cheek_l = _safe_get_landmark(landmarks, LANDMARK_INDICES['left_cheekbone'])
        cheek_r = _safe_get_landmark(landmarks, LANDMARK_INDICES['right_cheekbone'])
        face_scale = _calculate_distance(cheek_l, cheek_r)
        if face_scale <= 0:
            face_scale = avg_brow_length * 3.2 or 1.0  # قيمة احتياطية معقولة

        brow_length_ratio = avg_brow_length / face_scale

        # عتبات نسبية (طول الحاجب كنسبة من عرض الوجه) بدل قيم مطلقة:
        if brow_length_ratio > 0.34:
            length = 'Long'
        elif brow_length_ratio < 0.24:
            length = 'Short'
        else:
            length = 'Medium'

        # ── السماكة: أقصى امتداد رأسي (bounding box) لكامل نقاط الحاجب مقسوماً
        # على طول الحاجب. هذا أكثر متانة من مطابقة نقاط الحد العلوي بالسفلي
        # واحدة تلو الأخرى (التي تفترض تطابقاً موضعياً غير مضمون). ──
        left_all_pts = [p for p in (_get_many(landmarks, LANDMARK_INDICES['left_brow_upper']) +
                                     _get_many(landmarks, LANDMARK_INDICES['left_brow_lower'])) if p]
        right_all_pts = [p for p in (_get_many(landmarks, LANDMARK_INDICES['right_brow_upper']) +
                                      _get_many(landmarks, LANDMARK_INDICES['right_brow_lower'])) if p]

        def brow_thickness_bbox(points, length_norm):
            if len(points) < 2 or length_norm <= 0:
                return 0.0
            ys = [p[1] for p in points]
            return (max(ys) - min(ys)) / length_norm

        left_thickness_ratio = brow_thickness_bbox(left_all_pts, left_brow_length)
        right_thickness_ratio = brow_thickness_bbox(right_all_pts, right_brow_length)
        avg_thickness_ratio = (left_thickness_ratio + right_thickness_ratio) / 2

        # عتبات مُعاد معايرتها لطريقة bounding-box (نطاقات القيم مختلفة عن
        # طريقة المطابقة نقطة-بنقطة القديمة، لذلك لا يصح إبقاء نفس الأرقام)
        if avg_thickness_ratio > 0.16:
            thickness = 'Thick'
        elif avg_thickness_ratio < 0.08:
            thickness = 'Thin'
        else:
            thickness = 'Medium'

        # ── شكل القوس ──
        left_avg_height = (left_start[1] + left_end[1]) / 2
        right_avg_height = (right_start[1] + right_end[1]) / 2
        left_arch_depth = left_avg_height - left_peak[1]
        right_arch_depth = right_avg_height - right_peak[1]
        avg_arch_depth = (left_arch_depth + right_arch_depth) / 2

        if avg_arch_depth > 0.03:
            shape = 'Arched'
        elif avg_arch_depth > 0.01:
            shape = 'Soft Arch'
        else:
            shape = 'Straight'

        # ── الموضع: ارتفاع الحاجب فوق العين نسبة لعرض العين ──
        left_eye_top = _safe_get_landmark(landmarks, LANDMARK_INDICES['left_eye_top'])
        left_eye_outer = _safe_get_landmark(landmarks, LANDMARK_INDICES['left_eye_outer'])
        left_eye_inner = _safe_get_landmark(landmarks, LANDMARK_INDICES['left_eye_inner'])
        eye_width_ref = _calculate_distance(left_eye_outer, left_eye_inner) or 1.0

        position = 'Normal'
        if left_eye_top is not None:
            brow_eye_gap = abs(left_peak[1] - left_eye_top[1]) / eye_width_ref
            if brow_eye_gap > 0.55:
                position = 'High'
            elif brow_eye_gap < 0.30:
                position = 'Low'

        # ── التباعد بين الحاجبين نسبة للمسافة بين العينين ──
        inter_eye_distance = _calculate_distance(left_eye_inner,
                                                   _safe_get_landmark(landmarks, LANDMARK_INDICES['right_eye_inner']))
        brow_gap = _calculate_distance(left_start, right_start)
        spacing = 'Normal'
        if inter_eye_distance > 0:
            spacing_ratio = brow_gap / inter_eye_distance
            if spacing_ratio > 1.3:
                spacing = 'Wide'
            elif spacing_ratio < 0.85:
                spacing = 'Narrow'

        # ── التناسق ──
        symmetry = 'Symmetrical'
        length_diff = abs(left_brow_length - right_brow_length)
        arch_diff = abs(left_arch_depth - right_arch_depth)
        if length_diff > (avg_brow_length * 0.2) or arch_diff > 0.02:
            symmetry = 'Slightly Asymmetrical'

        return {
            'thickness': thickness,
            'length': length,
            'shape': shape,
            'position': position,
            'spacing': spacing,
            'symmetry': symmetry,
            'measurements': {
                'left_length': float(left_brow_length),
                'right_length': float(right_brow_length),
                'avg_arch_depth': float(avg_arch_depth),
                'avg_thickness_ratio': float(avg_thickness_ratio),
                'face_scale': float(face_scale),
                'brow_length_ratio': float(brow_length_ratio),
            }
        }

    except Exception as e:
        result = _default_brow_analysis()
        result['error'] = str(e)
        return result


def _default_brow_analysis() -> Dict:
    return {
        'thickness': 'Medium', 'length': 'Medium', 'shape': 'Soft Arch',
        'position': 'Normal', 'spacing': 'Normal', 'symmetry': 'Symmetrical'
    }


# ══════════════════════════════════════════════════════════════════
# LIP ANALYSIS
# ══════════════════════════════════════════════════════════════════

def analyze_lips(landmarks) -> Dict:
    """تحليل الشفاه — تم تصحيح خطأ نقاط MediaPipe (كان يقيس شبه صفر دائماً)."""
    try:
        if landmarks is None:
            return _default_lip_analysis()

        upper_outer = _safe_get_landmark(landmarks, LANDMARK_INDICES['upper_lip_outer_top'])
        upper_inner = _safe_get_landmark(landmarks, LANDMARK_INDICES['upper_lip_inner_bottom'])
        lower_inner = _safe_get_landmark(landmarks, LANDMARK_INDICES['lower_lip_inner_top'])
        lower_outer = _safe_get_landmark(landmarks, LANDMARK_INDICES['lower_lip_outer_bottom'])
        lip_left = _safe_get_landmark(landmarks, LANDMARK_INDICES['lip_left'])
        lip_right = _safe_get_landmark(landmarks, LANDMARK_INDICES['lip_right'])
        bow_left = _safe_get_landmark(landmarks, LANDMARK_INDICES['cupid_bow_left_peak'])
        bow_right = _safe_get_landmark(landmarks, LANDMARK_INDICES['cupid_bow_right_peak'])
        bow_dip = _safe_get_landmark(landmarks, LANDMARK_INDICES['cupid_bow_dip'])

        if None in [upper_outer, upper_inner, lower_inner, lower_outer, lip_left, lip_right]:
            return _default_lip_analysis()

        # سماكة كل شفة (بعد التصحيح: نقاط حقيقية على حافتي الشفة العلوية/السفلى)
        upper_thickness = _calculate_distance(upper_outer, upper_inner)
        lower_thickness = _calculate_distance(lower_inner, lower_outer)
        total_thickness = upper_thickness + lower_thickness
        lip_width = _calculate_distance(lip_left, lip_right)

        # ── نفس مبدأ التطبيع المستخدم بالحواجب: عرض عظمتي الخد كمقياس مرجعي
        # ثابت النسبة، بدل مقارنة مسافات مطلقة (مُطبَّعة بالصورة كلها) بعتبات
        # جامدة — وهو ما كان يجعل كل الصور تقريباً تُصنَّف Thin/Narrow. ──
        cheek_l = _safe_get_landmark(landmarks, LANDMARK_INDICES['left_cheekbone'])
        cheek_r = _safe_get_landmark(landmarks, LANDMARK_INDICES['right_cheekbone'])
        face_scale = _calculate_distance(cheek_l, cheek_r)
        if face_scale <= 0:
            face_scale = lip_width * 2.5 or 1.0

        thickness_ratio_to_face = total_thickness / face_scale
        width_ratio_to_face = lip_width / face_scale

        if thickness_ratio_to_face > 0.11:
            volume = 'Full'
        elif thickness_ratio_to_face < 0.06:
            volume = 'Thin'
        else:
            volume = 'Medium'

        if lower_thickness > 0 and upper_thickness > lower_thickness * 1.2:
            balance = 'Upper Fuller'
        elif upper_thickness > 0 and lower_thickness > upper_thickness * 1.2:
            balance = 'Lower Fuller'
        else:
            balance = 'Balanced'

        if width_ratio_to_face > 0.62:
            width = 'Wide'
        elif width_ratio_to_face < 0.45:
            width = 'Narrow'
        else:
            width = 'Average'

        # ── قوس كيوبيد: عمق الانحناء بين القمتين ونقطة المنتصف ──
        cupid_bow = 'Soft'
        if bow_left is not None and bow_right is not None and bow_dip is not None:
            peaks_avg_y = (bow_left[1] + bow_right[1]) / 2
            dip_depth = abs(bow_dip[1] - peaks_avg_y)
            dip_ratio = dip_depth / lip_width if lip_width > 0 else 0
            if dip_ratio > 0.05:
                cupid_bow = 'Defined'
            elif dip_ratio < 0.015:
                cupid_bow = 'Flat'
            else:
                cupid_bow = 'Soft'

        # ── زوايا الفم: مقارنة ارتفاع الزوايا بمركز الشفتين ──
        mouth_center_y = (upper_inner[1] + lower_inner[1]) / 2
        corners_avg_y = (lip_left[1] + lip_right[1]) / 2
        corner_gap_ratio = (mouth_center_y - corners_avg_y) / lip_width if lip_width > 0 else 0
        if corner_gap_ratio > 0.03:
            corners = 'Upturned'
        elif corner_gap_ratio < -0.03:
            corners = 'Downturned'
        else:
            corners = 'Neutral'

        # ── التناسق (فرق ارتفاع الزاويتين) ──
        symmetry = 'Symmetrical'
        if abs(lip_left[1] - lip_right[1]) > (lip_width * 0.06):
            symmetry = 'Slightly Asymmetrical'

        return {
            'volume': volume,
            'balance': balance,
            'width': width,
            'symmetry': symmetry,
            'cupid_bow': cupid_bow,
            'corners': corners,
            'measurements': {
                'upper_thickness': float(upper_thickness),
                'lower_thickness': float(lower_thickness),
                'thickness_ratio': float(upper_thickness / lower_thickness) if lower_thickness > 0 else 1.0,
                'width': float(lip_width),
                'face_scale': float(face_scale),
                'thickness_ratio_to_face': float(thickness_ratio_to_face),
                'width_ratio_to_face': float(width_ratio_to_face),
            }
        }

    except Exception as e:
        result = _default_lip_analysis()
        result['error'] = str(e)
        return result


def _default_lip_analysis() -> Dict:
    return {
        'volume': 'Medium', 'balance': 'Balanced', 'width': 'Average',
        'symmetry': 'Symmetrical', 'cupid_bow': 'Soft', 'corners': 'Neutral'
    }


# ══════════════════════════════════════════════════════════════════
# NOSE ANALYSIS
# ══════════════════════════════════════════════════════════════════

def analyze_nose(landmarks) -> Dict:
    """تحليل الأنف — width و bridge أصبحا مُشتقين فعلياً بدل ثابتين."""
    try:
        if landmarks is None:
            return _default_nose_analysis()

        nose_tip = _safe_get_landmark(landmarks, LANDMARK_INDICES['nose_tip'])
        nose_bridge_top = _safe_get_landmark(landmarks, LANDMARK_INDICES['nose_bridge_top'])
        nose_bridge_mid = _safe_get_landmark(landmarks, LANDMARK_INDICES['nose_bridge_mid'])
        nose_left = _safe_get_landmark(landmarks, LANDMARK_INDICES['nose_left'])
        nose_right = _safe_get_landmark(landmarks, LANDMARK_INDICES['nose_right'])
        ala_left = _safe_get_landmark(landmarks, LANDMARK_INDICES['nose_ala_left'])
        ala_right = _safe_get_landmark(landmarks, LANDMARK_INDICES['nose_ala_right'])
        # مرجع لعرض الوجه لتطبيع عرض الأنف
        face_left = _safe_get_landmark(landmarks, LANDMARK_INDICES['left_cheekbone'])
        face_right = _safe_get_landmark(landmarks, LANDMARK_INDICES['right_cheekbone'])

        if None in [nose_tip, nose_bridge_top, nose_left, nose_right]:
            return _default_nose_analysis()

        nose_length = _calculate_distance(nose_bridge_top, nose_tip)
        nose_width_sides = _calculate_distance(nose_left, nose_right)
        nostril_width = _calculate_distance(ala_left, ala_right) if None not in [ala_left, ala_right] else nose_width_sides
        nose_width = max(nose_width_sides, nostril_width)

        if nose_width == 0:
            return _default_nose_analysis()

        ratio = nose_length / nose_width
        if ratio > 1.5:
            shape = 'Long'
        elif ratio < 0.8:
            shape = 'Short'
        else:
            shape = 'Balanced'

        # ── عرض الأنف نسبةً لعرض الوجه (وليس رقماً ثابتاً) ──
        width = 'Normal'
        if None not in [face_left, face_right]:
            face_width = _calculate_distance(face_left, face_right)
            if face_width > 0:
                nostril_to_face = nostril_width / face_width
                if nostril_to_face > 0.30:
                    width = 'Wide'
                elif nostril_to_face < 0.20:
                    width = 'Narrow'

        # ── شكل الجسر: انحراف نقطة منتصف الجسر عن الخط الواصل بين البداية والطرف ──
        bridge = 'Straight'
        if nose_bridge_mid is not None:
            # نسقط على نفس الفاصل الزمني بين البداية والطرف حسب y ثم نقارن x/z
            t = ((nose_bridge_mid[1] - nose_bridge_top[1]) /
                 (nose_tip[1] - nose_bridge_top[1])) if (nose_tip[1] - nose_bridge_top[1]) != 0 else 0.5
            t = max(0.0, min(1.0, t))
            interp_z = nose_bridge_top[2] + t * (nose_tip[2] - nose_bridge_top[2])
            z_deviation = nose_bridge_mid[2] - interp_z
            if z_deviation < -0.006:
                bridge = 'Convex'   # الجسر أقرب للكاميرا من المتوقع → أنف أرومي/محدّب
            elif z_deviation > 0.006:
                bridge = 'Concave'  # الجسر أبعد من المتوقع → أنف مقعّر/غاطس

        return {
            'shape': shape,
            'width': width,
            'bridge': bridge,
            'measurements': {
                'length': float(nose_length),
                'width_sides': float(nose_width_sides),
                'nostril_width': float(nostril_width),
                'length_to_width_ratio': float(ratio),
            }
        }

    except Exception as e:
        result = _default_nose_analysis()
        result['error'] = str(e)
        return result


def _default_nose_analysis() -> Dict:
    return {'shape': 'Balanced', 'width': 'Normal', 'bridge': 'Straight'}


# ══════════════════════════════════════════════════════════════════
# MAIN ANALYSIS FUNCTION
# ══════════════════════════════════════════════════════════════════

def analyze_face_from_image(image_source) -> FaceAnalysisResult:
    """تحليل شامل للوجه من صورة"""
    try:
        if isinstance(image_source, str):
            image = cv2.imread(image_source)
            if image is None:
                return FaceAnalysisResult(success=False, face_detected=False,
                                           error=f"Cannot read image: {image_source}")
        else:
            image = image_source

        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w = rgb_image.shape[:2]

        with mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5
        ) as face_mesh:

            results = face_mesh.process(rgb_image)

            if not results.multi_face_landmarks:
                return FaceAnalysisResult(success=True, face_detected=False,
                                           error="No face detected in image")

            landmarks = results.multi_face_landmarks[0].landmark

            return FaceAnalysisResult(
                success=True,
                face_detected=True,
                face_shape=analyze_face_shape(landmarks, w, h),
                eyes=analyze_eyes(landmarks),
                brows=analyze_brows(landmarks),
                lips=analyze_lips(landmarks),
                nose=analyze_nose(landmarks),
                measurements={'image_width': w, 'image_height': h}
            )

    except Exception as e:
        return FaceAnalysisResult(success=False, face_detected=False, error=str(e))


def analyze_face_from_image_dict(image_source) -> Dict:
    """تحليل الوجه وإرجاع نتيجة بصيغة dictionary"""
    result = analyze_face_from_image(image_source)
    result_dict = asdict(result)
    result_dict['error'] = result.error
    return result_dict


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