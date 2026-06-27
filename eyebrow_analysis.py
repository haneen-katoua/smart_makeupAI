import cv2
import mediapipe as mp
import math
import numpy as np


# =====================================================
# Distance
# =====================================================

def distance(p1, p2):
    return math.sqrt(
        (p1[0] - p2[0]) ** 2 +
        (p1[1] - p2[1]) ** 2
    )


# =====================================================
# Landmarks
# =====================================================

# نقاط الحاجب الأيسر — من الطرف الداخلي للخارجي
LEFT_BROW_IDX = [70, 63, 105, 66, 107, 55, 52, 53, 46]

# نقاط الحاجب الأيمن — مرآة الأيسر
RIGHT_BROW_IDX = [300, 293, 334, 296, 336, 285, 282, 283, 276]

# نقاط العيون (لحساب المرجع وتقييم موضع الحاجب)
LEFT_EYE  = {"inner": 33,  "outer": 133, "top": 159, "bottom": 145}
RIGHT_EYE = {"inner": 362, "outer": 263, "top": 386, "bottom": 374}

# نقاط الوجه لحساب المرجع الكلي
FACE = {"left": 234, "right": 454, "top": 10, "chin": 152}


# =====================================================
# Helper
# =====================================================

def get_pt(lm, idx, w, h):
    l = lm[idx]
    return (int(l.x * w), int(l.y * h))


def get_pts(lm, indices, w, h):
    return [get_pt(lm, i, w, h) for i in indices]


# =====================================================
# Feature Extraction — مقاييس مُصحَّحة
# =====================================================

def extract_brow_features(brow_pts, eye_pts, face_width, face_height):
    """
    يستخرج مقاييس الحاجب المُعيَّرة بالنسبة للوجه.

    المشاكل المُصلَحة:
      ① السماكة: نقيس المسافة الفعلية بين أعلى وأدنى نقطة في الحاجب
                 (الكود القديم كان يحسب انحرافاً إحصائياً لا سماكةً بصرية)
      ② الطول:   نُعيِّر بعرض الوجه لا عرض العين الواحدة
                 (عرض العين يتغير بالزاوية وبالتعبير الوجهي)
      ③ التقوس:  نأخذ أعلى نقطة حقيقية min(y) لا النقطة الوسطى في القائمة
                 (النقطة الوسطى في القائمة قد تكون طرف الحاجب)
      ④ ارتفاع الحاجب عن العين: مقياس جديد مهم للتصنيف الكامل
    """

    ys = [p[1] for p in brow_pts]
    xs = [p[0] for p in brow_pts]

    # ① السماكة الفعلية = أدنى نقطة - أعلى نقطة (الفرق العمودي)
    #    نُعيِّر بارتفاع الوجه للحصول على نسبة مستقلة عن الدقة
    brow_top_y    = min(ys)
    brow_bottom_y = max(ys)
    thickness_px  = brow_bottom_y - brow_top_y
    thickness     = thickness_px / face_height   # نسبة لارتفاع الوجه

    # ② الطول = المسافة الأفقية من أقصى اليسار لأقصى اليمين
    #    نُعيِّر بعرض الوجه لا عرض العين
    brow_left_x  = min(xs)
    brow_right_x = max(xs)
    brow_length_px = brow_right_x - brow_left_x
    length       = brow_length_px / face_width

    # ③ التقوس = نسبة ارتفاع القمة عن خط الطرفين
    #    نأخذ نقطة القمة الحقيقية (أعلى y في الصورة = أصغر قيمة y)
    peak_pt = min(brow_pts, key=lambda p: p[1])        # أعلى نقطة في الحاجب
    left_pt  = min(brow_pts, key=lambda p: p[0])       # أقصى يسار
    right_pt = max(brow_pts, key=lambda p: p[0])       # أقصى يمين

    # ارتفاع القمة عن خط الوتر (الطرفين)
    chord_y_at_peak_x = (
        left_pt[1]
        + (right_pt[1] - left_pt[1])
        * (peak_pt[0] - left_pt[0])
        / max(right_pt[0] - left_pt[0], 1)
    )
    arch_px = chord_y_at_peak_x - peak_pt[1]   # موجب = قمة حقيقية، سالب = حاجب محدّب لأسفل
    arch     = arch_px / face_height

    # ④ ارتفاع الحاجب عن العين = المسافة العمودية بين أسفل الحاجب وأعلى الجفن
    eye_top_y      = eye_pts["top"][1]
    brow_base_y    = brow_bottom_y
    brow_eye_gap_px = eye_top_y - brow_base_y   # موجب = فراغ، سالب = متداخلان
    brow_eye_gap    = brow_eye_gap_px / face_height

    return {
        "thickness":     thickness,
        "length":        length,
        "arch":          arch,
        "brow_eye_gap":  brow_eye_gap,
        "peak_pt":       peak_pt,
        "left_pt":       left_pt,
        "right_pt":      right_pt,
        "brow_bottom_y": brow_bottom_y,
    }


# =====================================================
# Symmetry — مُصلَح ليقارن الحاجبَين معاً
# =====================================================

def compute_symmetry(left_feats, right_feats, face_width, face_height):
    """
    المشكلة القديمة: كانت تقارن طرفَي حاجب واحد → تقيس الميلان لا التناسق.
    الحل: نقارن نفس المقاييس بين الحاجب الأيسر والأيمن.
    """
    diff_thickness = abs(left_feats["thickness"] - right_feats["thickness"])
    diff_length    = abs(left_feats["length"]    - right_feats["length"])
    diff_arch      = abs(left_feats["arch"]      - right_feats["arch"])
    diff_gap       = abs(left_feats["brow_eye_gap"] - right_feats["brow_eye_gap"])

    # نسبة التناسق الكلي = متوسط الفروقات المُعيَّرة
    symmetry_score = (diff_thickness + diff_length + diff_arch + diff_gap) / 4
    return symmetry_score


# =====================================================
# Classification
# =====================================================

def classify_brow(feats_L, feats_R, symmetry_score, inter_brow_ratio):
    """
    يُصنِّف الحاجبين مع عتبات مُعايَرة للمقاييس الجديدة.
    العتبات مبنية على نسب من ارتفاع/عرض الوجه (face_height / face_width).
    """
    facts = {}

    # نأخذ متوسط الحاجبين للمقاييس المشتركة
    thickness    = (feats_L["thickness"]    + feats_R["thickness"])    / 2
    length       = (feats_L["length"]       + feats_R["length"])       / 2
    arch         = (feats_L["arch"]         + feats_R["arch"])         / 2
    brow_eye_gap = (feats_L["brow_eye_gap"] + feats_R["brow_eye_gap"]) / 2

    # ① السماكة
    # نسبة thickness = brow_height / face_height
    # قيم مرجعية تجريبية: رفيع < 0.030 < متوسط < 0.055 < سميك
    if thickness >= 0.055:
        facts["Thickness"] = "Thick"
    elif thickness >= 0.030:
        facts["Thickness"] = "Medium"
    else:
        facts["Thickness"] = "Thin"

    # ② الطول
    # نسبة length = brow_span / face_width
    # قيم مرجعية: قصير < 0.22 < متوسط < 0.32 < طويل
    if length >= 0.32:
        facts["Length"] = "Long"
    elif length <= 0.22:
        facts["Length"] = "Short"
    else:
        facts["Length"] = "Medium"

    # ③ الشكل / التقوس
    # arch = peak_rise / face_height
    # موجب = مقوّس للأعلى، سالب = مستوٍ أو محدّب للأسفل
    if arch >= 0.025:
        facts["Shape"] = "Arched"
    elif arch <= 0.008:
        facts["Shape"] = "Straight"
    else:
        facts["Shape"] = "Soft Arch"

    # ④ ارتفاع الحاجب عن العين
    # brow_eye_gap = gap / face_height
    # صغير = حاجب منخفض/مبطّن، كبير = حاجب مرتفع
    if brow_eye_gap >= 0.040:
        facts["Position"] = "High"
    elif brow_eye_gap <= 0.015:
        facts["Position"] = "Low"
    else:
        facts["Position"] = "Normal"

    # ⑤ المسافة بين الحاجبين
    # inter_brow_ratio = gap_between_brows / face_width
    if inter_brow_ratio < 0.08:
        facts["Spacing"] = "Close"
    elif inter_brow_ratio > 0.18:
        facts["Spacing"] = "Wide"
    else:
        facts["Spacing"] = "Normal"

    # ⑥ التناسق بين الحاجبين
    if symmetry_score < 0.008:
        facts["Symmetry"] = "Symmetrical"
    elif symmetry_score < 0.020:
        facts["Symmetry"] = "Slightly Asymmetrical"
    else:
        facts["Symmetry"] = "Asymmetrical"

    return facts


# =====================================================
# Drawing
# =====================================================

def draw_brow(image, brow_pts, feats, color, label):
    peak = feats["peak_pt"]
    left = feats["left_pt"]
    right = feats["right_pt"]

    for p in brow_pts:
        cv2.circle(image, p, 3, color, -1)

    # خط الوتر (بين الطرفين)
    cv2.line(image, left, right, (180, 180, 180), 1)

    # خط عمودي للقمة
    chord_y = int(
        left[1] + (right[1] - left[1])
        * (peak[0] - left[0]) / max(right[0] - left[0], 1)
    )
    cv2.line(image, (peak[0], chord_y), peak, (255, 200, 0), 1)
    cv2.circle(image, peak, 5, (255, 200, 0), -1)

    # تسمية
    base_x = left[0]
    base_y = left[1] - 22
    cv2.putText(image, label, (base_x, base_y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(image, label, (base_x, base_y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (30, 30, 30), 1, cv2.LINE_AA)


# =====================================================
# Main
# =====================================================

def main(image_path: str, output_path: str = "brow_result.jpg"):

    image = cv2.imread(image_path)
    if image is None:
        print(f"[ERROR] Image not found: {image_path}")
        return

    h, w, _ = image.shape
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    with mp.solutions.face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=1,
        refine_landmarks=True,
    ) as mesh:

        res = mesh.process(rgb)
        if not res.multi_face_landmarks:
            print("[ERROR] No face detected")
            return

        lm = res.multi_face_landmarks[0].landmark

        # ---- نقاط المرجع ----
        face_left  = get_pt(lm, FACE["left"],  w, h)
        face_right = get_pt(lm, FACE["right"], w, h)
        face_top   = get_pt(lm, FACE["top"],   w, h)
        face_chin  = get_pt(lm, FACE["chin"],  w, h)

        face_width  = distance(face_left, face_right)
        face_height = distance(face_top,  face_chin)

        # ---- نقاط العيون ----
        left_eye_pts  = {k: get_pt(lm, v, w, h) for k, v in LEFT_EYE.items()}
        right_eye_pts = {k: get_pt(lm, v, w, h) for k, v in RIGHT_EYE.items()}

        # ---- نقاط الحاجبين ----
        left_brow_pts  = get_pts(lm, LEFT_BROW_IDX,  w, h)
        right_brow_pts = get_pts(lm, RIGHT_BROW_IDX, w, h)

        # ---- استخراج المقاييس ----
        feats_L = extract_brow_features(left_brow_pts,  left_eye_pts,  face_width, face_height)
        feats_R = extract_brow_features(right_brow_pts, right_eye_pts, face_width, face_height)

        # ---- التناسق (مقارنة الحاجبين معاً) ----
        symmetry_score = compute_symmetry(feats_L, feats_R, face_width, face_height)

        # ---- المسافة بين الحاجبين ----
        inner_left_brow  = min(left_brow_pts,  key=lambda p: p[0])  # أقرب نقطة للأنف في الحاجب الأيسر
        inner_right_brow = max(right_brow_pts, key=lambda p: p[0])  # أقرب نقطة للأنف في الحاجب الأيمن

        # نأخذ أقصى يمين الأيسر وأقصى يسار الأيمن
        left_inner_x  = max(p[0] for p in left_brow_pts)
        right_inner_x = min(p[0] for p in right_brow_pts)
        inter_brow_px    = abs(right_inner_x - left_inner_x)
        inter_brow_ratio = inter_brow_px / face_width

        # ---- التصنيف ----
        result = classify_brow(feats_L, feats_R, symmetry_score, inter_brow_ratio)

        # ---- الرسم ----
        draw_brow(image, left_brow_pts,  feats_L, (0, 220, 80),  "Left Brow")
        draw_brow(image, right_brow_pts, feats_R, (80, 180, 255), "Right Brow")

        # خط عرض الوجه
        cv2.line(image, face_left, face_right, (200, 200, 0), 1)

        # ---- طباعة النتائج ----
        avg_thickness = (feats_L["thickness"]    + feats_R["thickness"])    / 2
        avg_length    = (feats_L["length"]       + feats_R["length"])       / 2
        avg_arch      = (feats_L["arch"]         + feats_R["arch"])         / 2
        avg_gap       = (feats_L["brow_eye_gap"] + feats_R["brow_eye_gap"]) / 2

        print("\n========== BROW METRICS ==========")
        print(f"face_width        : {face_width:.1f} px")
        print(f"face_height       : {face_height:.1f} px")
        print()
        print(f"thickness (avg)   : {avg_thickness:.4f}  (L={feats_L['thickness']:.4f}  R={feats_R['thickness']:.4f})")
        print(f"length    (avg)   : {avg_length:.4f}  (L={feats_L['length']:.4f}  R={feats_R['length']:.4f})")
        print(f"arch      (avg)   : {avg_arch:.4f}  (L={feats_L['arch']:.4f}  R={feats_R['arch']:.4f})")
        print(f"brow_eye_gap(avg) : {avg_gap:.4f}  (L={feats_L['brow_eye_gap']:.4f}  R={feats_R['brow_eye_gap']:.4f})")
        print(f"inter_brow_ratio  : {inter_brow_ratio:.4f}")
        print(f"symmetry_score    : {symmetry_score:.4f}")

        print("\n========== BROW CLASSIFICATION ==========")
        for k, v in result.items():
            print(f"  {k:<12}: {v}")

    # cv2.imwrite(output_path, image)
    # print(f"\n[OK] Saved → {output_path}")


if __name__ == "__main__":
    main(
        image_path="pictures2/photo_2026-06-04_11-18-54.jpg",
        # output_path="brow_result.jpg",
    )