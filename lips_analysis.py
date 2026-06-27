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
# Landmarks — نقاط MediaPipe للشفاه
# =====================================================

# زوايا الفم
MOUTH_LEFT  = 61
MOUTH_RIGHT = 291

# الشفة العليا
UPPER_LIP_TOP_MID   = 0    # أعلى نقطة في الشفة العليا (خارجياً)
UPPER_LIP_INNER_MID = 13   # الحافة الداخلية للشفة العليا

# الشفة السفلى
LOWER_LIP_INNER_MID = 14   # الحافة الداخلية للشفة السفلى
LOWER_LIP_BOT_MID   = 17   # أسفل نقطة في الشفة السفلى (خارجياً)

# قوس كيوبيد — النقاط الثلاث العلوية
CUPID_LEFT   = 37    # قمة يسار القوس
CUPID_CENTER = 0     # مركز القوس (المنخفض)
CUPID_RIGHT  = 267   # قمة يمين القوس

# نقاط الشفة العليا الجانبية (لحساب التناسق)
UPPER_LIP_LEFT_INNER  = 78
UPPER_LIP_RIGHT_INNER = 308
LOWER_LIP_LEFT_INNER  = 88
LOWER_LIP_RIGHT_INNER = 318

# زوايا الفم (لكشف الاتجاه upturned/downturned)
CORNER_LEFT  = 61
CORNER_RIGHT = 291

# مرجع الوجه
FACE_LEFT   = 234
FACE_RIGHT  = 454
FACE_TOP    = 10
FACE_CHIN   = 152

# العيون (مرجع عرض الفم)
EYE_LEFT_INNER  = 33
EYE_RIGHT_INNER = 263


# =====================================================
# Helper
# =====================================================

def get_pt(lm, idx, w, h):
    l = lm[idx]
    return (int(l.x * w), int(l.y * h))


# =====================================================
# Feature Extraction — مقاييس مُصحَّحة
# =====================================================

def extract_lip_features(lm, w, h, face_width, face_height):
    """
    مقاييس مستقلة وواضحة لكل خاصية.

    المشاكل المُصلَحة:
      ① lip_score: كان يخلط ارتفاع الشفة بفرق الزوايا → فصلنا المقاييس
      ② balance  : نقاط 0 و 17 ليستا الحدود الصحيحة → استخدمنا النقاط الصحيحة
      ③ symmetry : قيم normalized بدون مرجع → نُعيِّر بعرض الفم
      ④ cupid_bow: لم يكن موجوداً أصلاً → أضفناه
      ⑤ corner_tilt: لم يكن موجوداً → أضفناه لكشف الاتجاه
    """

    # ── نقاط أساسية ──
    left_pt          = get_pt(lm, MOUTH_LEFT,         w, h)
    right_pt         = get_pt(lm, MOUTH_RIGHT,        w, h)
    upper_top_pt     = get_pt(lm, UPPER_LIP_TOP_MID,  w, h)   # أعلى الشفة العليا
    upper_inner_pt   = get_pt(lm, UPPER_LIP_INNER_MID,w, h)   # باطن الشفة العليا
    lower_inner_pt   = get_pt(lm, LOWER_LIP_INNER_MID,w, h)   # باطن الشفة السفلى
    lower_bot_pt     = get_pt(lm, LOWER_LIP_BOT_MID,  w, h)   # أسفل الشفة السفلى

    cupid_left_pt    = get_pt(lm, CUPID_LEFT,  w, h)
    cupid_center_pt  = get_pt(lm, CUPID_CENTER,w, h)
    cupid_right_pt   = get_pt(lm, CUPID_RIGHT, w, h)

    ul_left_pt       = get_pt(lm, UPPER_LIP_LEFT_INNER,  w, h)
    ul_right_pt      = get_pt(lm, UPPER_LIP_RIGHT_INNER, w, h)
    ll_left_pt       = get_pt(lm, LOWER_LIP_LEFT_INNER,  w, h)
    ll_right_pt      = get_pt(lm, LOWER_LIP_RIGHT_INNER, w, h)

    corner_l_pt      = get_pt(lm, CORNER_LEFT,  w, h)
    corner_r_pt      = get_pt(lm, CORNER_RIGHT, w, h)

    eye_left_pt      = get_pt(lm, EYE_LEFT_INNER,  w, h)
    eye_right_pt     = get_pt(lm, EYE_RIGHT_INNER, w, h)

    # ── عرض الفم ──
    mouth_width = distance(left_pt, right_pt)

    # ── ① ارتفاع الشفة العليا (من أعلى نقطة خارجية لباطنها) ──
    upper_lip_height = distance(upper_top_pt, upper_inner_pt)

    # ── ② ارتفاع الشفة السفلى (من باطنها لأسفل نقطة خارجية) ──
    lower_lip_height = distance(lower_inner_pt, lower_bot_pt)

    # ── ③ إجمالي ارتفاع الفتحة (بين الشفتين) ──
    lip_opening_height = distance(upper_inner_pt, lower_inner_pt)

    # ── ④ نسبة الحجم الكلي للشفاه بالنسبة للوجه ──
    total_lip_height = upper_lip_height + lower_lip_height
    volume_ratio = total_lip_height / face_height

    # ── ⑤ التوازن بين الشفتين ──
    if (upper_lip_height + lower_lip_height) > 0:
        balance_ratio = upper_lip_height / (upper_lip_height + lower_lip_height)
    else:
        balance_ratio = 0.5

    # ── ⑥ التناسق — مقارنة الجانبين ──
    left_gap  = abs(ul_left_pt[1]  - ll_left_pt[1])
    right_gap = abs(ul_right_pt[1] - ll_right_pt[1])
    symmetry  = abs(left_gap - right_gap) / (mouth_width + 1e-6)

    # ── ⑦ عرض الفم نسبةً للمسافة بين العيون ──
    eye_distance        = distance(eye_left_pt, eye_right_pt)
    mouth_width_ratio   = mouth_width / (eye_distance + 1e-6)

    # ── ⑧ قوس كيوبيد ──
    # عمق القوس = كم انخفض المركز عن متوسط القمتين
    cupid_peaks_avg_y = (cupid_left_pt[1] + cupid_right_pt[1]) / 2
    cupid_bow_depth   = (cupid_center_pt[1] - cupid_peaks_avg_y) / (face_height + 1e-6)
    # موجب = القمتان أعلى من المركز = قوس حقيقي
    # سالب أو صفر = شفة مسطّحة

    # ── ⑨ اتجاه زوايا الفم ──
    # corner_tilt موجب = الزاوية اليمنى أنزل (downturned)، سالب = upturned
    corner_tilt = (corner_r_pt[1] - corner_l_pt[1]) / (mouth_width + 1e-6)

    return {
        "pts": {
            "left": left_pt, "right": right_pt,
            "upper_top": upper_top_pt, "upper_inner": upper_inner_pt,
            "lower_inner": lower_inner_pt, "lower_bot": lower_bot_pt,
            "cupid_left": cupid_left_pt, "cupid_center": cupid_center_pt,
            "cupid_right": cupid_right_pt,
            "corner_l": corner_l_pt, "corner_r": corner_r_pt,
        },
        "mouth_width":       mouth_width,
        "upper_lip_height":  upper_lip_height,
        "lower_lip_height":  lower_lip_height,
        "total_lip_height":  total_lip_height,
        "volume_ratio":      volume_ratio,
        "balance_ratio":     balance_ratio,
        "symmetry":          symmetry,
        "mouth_width_ratio": mouth_width_ratio,
        "cupid_bow_depth":   cupid_bow_depth,
        "corner_tilt":       corner_tilt,
    }


# =====================================================
# Classification
# =====================================================

def classify_lips(feats):
    """
    يُصنِّف كل خاصية باستقلالية تامة.
    كل مقياس له معنى واحد واضح.
    """
    result = {}

    vr   = feats["volume_ratio"]
    br   = feats["balance_ratio"]
    sym  = feats["symmetry"]
    mwr  = feats["mouth_width_ratio"]
    cbd  = feats["cupid_bow_depth"]
    ct   = feats["corner_tilt"]

    # ── ① الحجم ──
    # volume_ratio = total_lip_height / face_height
    # مرجعية: رفيعة < 0.035 < متوسطة < 0.060 < ممتلئة
    if vr >= 0.060:
        result["Volume"] = "Full"
    elif vr >= 0.035:
        result["Volume"] = "Medium"
    else:
        result["Volume"] = "Thin"

    # ── ② التوازن ──
    # balance_ratio = upper_h / (upper_h + lower_h)
    # > 0.52 = الشفة العليا أسمك نسبياً
    # < 0.48 = الشفة السفلى أسمك
    if br > 0.55:
        result["Balance"] = "Upper Fuller"
    elif br < 0.45:
        result["Balance"] = "Lower Fuller"
    else:
        result["Balance"] = "Balanced"

    # ── ③ التناسق ──
    if sym < 0.04:
        result["Symmetry"] = "Symmetrical"
    elif sym < 0.10:
        result["Symmetry"] = "Slightly Asymmetrical"
    else:
        result["Symmetry"] = "Asymmetrical"

    # ── ④ عرض الفم ──
    # mouth_width_ratio = mouth_width / eye_distance
    # < 0.90 = ضيق، 0.90–1.20 = متوسط، > 1.20 = عريض
    if mwr < 0.90:
        result["Width"] = "Narrow"
    elif mwr > 1.20:
        result["Width"] = "Wide"
    else:
        result["Width"] = "Average"

    # ── ⑤ قوس كيوبيد ──
    # cupid_bow_depth موجب وكبير = قوس واضح
    if cbd > 0.018:
        result["Cupid Bow"] = "Defined"
    elif cbd > 0.008:
        result["Cupid Bow"] = "Soft"
    else:
        result["Cupid Bow"] = "Flat"

    # ── ⑥ اتجاه الزوايا ──
    # corner_tilt: موجب = downturned، سالب = upturned
    if ct > 0.06:
        result["Corners"] = "Downturned"
    elif ct < -0.06:
        result["Corners"] = "Upturned"
    else:
        result["Corners"] = "Neutral"

    return result


# =====================================================
# Drawing
# =====================================================

def draw_lip_results(image, feats, result):
    pts = feats["pts"]

    colors = {
        "corner":   (0, 255, 0),
        "upper":    (255, 140, 0),
        "lower":    (0, 140, 255),
        "cupid":    (200, 0, 200),
    }

    cv2.circle(image, pts["left"],         4, colors["corner"],  -1)
    cv2.circle(image, pts["right"],        4, colors["corner"],  -1)
    cv2.circle(image, pts["upper_top"],    4, colors["upper"],   -1)
    cv2.circle(image, pts["upper_inner"],  4, colors["upper"],   -1)
    cv2.circle(image, pts["lower_inner"],  4, colors["lower"],   -1)
    cv2.circle(image, pts["lower_bot"],    4, colors["lower"],   -1)
    cv2.circle(image, pts["cupid_left"],   5, colors["cupid"],   -1)
    cv2.circle(image, pts["cupid_center"], 5, colors["cupid"],   -1)
    cv2.circle(image, pts["cupid_right"],  5, colors["cupid"],   -1)

    # خطوط القياس
    cv2.line(image, pts["upper_top"],   pts["upper_inner"],  colors["upper"], 1)
    cv2.line(image, pts["lower_inner"], pts["lower_bot"],    colors["lower"], 1)
    cv2.line(image, pts["left"],        pts["right"],        (200, 200, 0),   1)

    # خط قوس كيوبيد
    cv2.line(image, pts["cupid_left"],  pts["cupid_center"], colors["cupid"], 1)
    cv2.line(image, pts["cupid_center"],pts["cupid_right"],  colors["cupid"], 1)

    # نص النتائج
    base_x = pts["left"][0] - 10
    base_y = pts["upper_top"][1] - 60
    for i, (k, v) in enumerate(result.items()):
        line = f"{k}: {v}"
        y = base_y + i * 16
        cv2.putText(image, line, (base_x, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.40, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(image, line, (base_x, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.40, (10,  10,  10),  1, cv2.LINE_AA)


# =====================================================
# Main
# =====================================================

def main(image_path: str, output_path: str = "lip_result.jpg"):

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
    ) as face_mesh:

        results = face_mesh.process(rgb)
        if not results.multi_face_landmarks:
            print("[ERROR] No face detected")
            return

        lm = results.multi_face_landmarks[0].landmark

        # أبعاد الوجه للمرجع
        face_left_pt  = get_pt(lm, FACE_LEFT,  w, h)
        face_right_pt = get_pt(lm, FACE_RIGHT, w, h)
        face_top_pt   = get_pt(lm, FACE_TOP,   w, h)
        face_chin_pt  = get_pt(lm, FACE_CHIN,  w, h)
        face_width    = distance(face_left_pt, face_right_pt)
        face_height   = distance(face_top_pt,  face_chin_pt)

        feats  = extract_lip_features(lm, w, h, face_width, face_height)
        result = classify_lips(feats)
        draw_lip_results(image, feats, result)

        print("\n========== LIP METRICS ==========")
        print(f"  mouth_width       : {feats['mouth_width']:.1f} px")
        print(f"  upper_lip_height  : {feats['upper_lip_height']:.1f} px")
        print(f"  lower_lip_height  : {feats['lower_lip_height']:.1f} px")
        print(f"  volume_ratio      : {feats['volume_ratio']:.4f}")
        print(f"  balance_ratio     : {feats['balance_ratio']:.4f}")
        print(f"  symmetry          : {feats['symmetry']:.4f}")
        print(f"  mouth_width_ratio : {feats['mouth_width_ratio']:.4f}")
        print(f"  cupid_bow_depth   : {feats['cupid_bow_depth']:.4f}")
        print(f"  corner_tilt       : {feats['corner_tilt']:.4f}")

        print("\n========== LIP CLASSIFICATION ==========")
        for k, v in result.items():
            print(f"  {k:<14}: {v}")

    cv2.imwrite(output_path, image)
    print(f"\n[OK] Saved → {output_path}")


if __name__ == "__main__":
    main(
        image_path="pictures2/photo_2026-06-04_11-19-47.jpg",
        output_path="lip_result.jpg",
    )