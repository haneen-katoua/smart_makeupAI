"""
face_analysis.py — v10
======================
التعديلات الجوهرية:

① شكل الوجه → 3 أشكال فقط (Oval / Round / Rectangular)
   منطق مُعاد كتابته بالكامل بعتبات أوضح

② العيون → خرج مدمج "شكل + نوع" كما في ملف الخبرة:
   الأنواع: Hooded / Protruding / Almond / Round / Droopy / Deep-set
   الخرج النهائي أمثلة: "Almond Hooded" / "Round Protruding" / "Almond Deep-set" ...
   منطق: أولاً نحدد النوع (الحالة الغالبة)، ثم نحدد الشكل الهندسي

③ الحواجب → إصلاح "مقوسة دائماً":
   - عتبة Arched رُفعت إلى arch >= 0.050
   - Soft Arch: 0.018 <= arch < 0.050  (الغالبية)
   - Straight: arch < 0.018

④ الشفاه → إصلاح منطق التوازن:
   balance_ratio = upper_h / total_h
   إذا > 0.55 → الشفة العليا أسمك (تصحيح: السفلى)
   إذا < 0.45 → الشفة السفلى أسمك (تصحيح: العليا) ← الحالة الأكثر شيوعاً
   هذا هو المنطق الصحيح تشريحياً
"""

import cv2
import mediapipe as mp
import math
import numpy as np


# ══════════════════════════════════════════════════════
# DISTANCE
# ══════════════════════════════════════════════════════

def distance(p1, p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)


# ══════════════════════════════════════════════════════
# LANDMARK INDICES
# ══════════════════════════════════════════════════════

FACE_LEFT  = 234;  FACE_RIGHT = 454
FACE_TOP   = 10;   FACE_CHIN  = 152

JAW_CAND_L  = [132, 58, 172, 136, 150]
JAW_CAND_R  = [361, 288, 397, 365, 379]
FOREHEAD_L  = [54, 103, 67, 109, 127]
FOREHEAD_R  = [284, 332, 297, 338, 356]
CHEEK_L     = [116, 117, 118, 119, 93]
CHEEK_R     = [345, 346, 347, 348, 323]
TEMPLE_L    = 127;  TEMPLE_R = 356

L_EYE = {"inner": 33,  "outer": 133, "upper": 159, "lower": 145,
          "iris_top": 474, "iris_bot": 477,
          "corner_out": 130, "corner_in": 133}
R_EYE = {"inner": 362, "outer": 263, "upper": 386, "lower": 374,
          "iris_top": 469, "iris_bot": 472,
          "corner_out": 359, "corner_in": 362}

# نقاط إضافية للعين (بروز/غؤور)
L_EYE_DEPTH = {"brow_bone": 55, "lower_lid": 145}
R_EYE_DEPTH = {"brow_bone": 285, "lower_lid": 374}

L_BROW_IDX = [70, 63, 105, 66, 107, 52, 53, 46]
R_BROW_IDX = [300, 293, 334, 296, 336, 282, 283, 276]

FOREHEAD_TOP_IDX = [10, 151, 9, 8]
CHIN_BOT_IDX     = [152, 175, 199, 200]

MOUTH_LEFT       = 61;   MOUTH_RIGHT      = 291
UPPER_LIP_TOP    = 0;    UPPER_LIP_INNER  = 13
LOWER_LIP_INNER  = 14;   LOWER_LIP_BOT    = 17
CUPID_LEFT       = 37;   CUPID_CENTER     = 0;   CUPID_RIGHT = 267
UL_LEFT_INNER    = 78;   UL_RIGHT_INNER   = 308
LL_LEFT_INNER    = 88;   LL_RIGHT_INNER   = 318

NOSE_TIP        = 4
NOSE_BRIDGE_T   = 6
NOSE_LENGTH_TOP = 168
ALAR_L_OUTER    = 294
ALAR_R_OUTER    = 64
ALAR_L_BASE     = 358
ALAR_R_BASE     = 129


# ══════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════

def get_pt(lm, idx, w, h):
    l = lm[idx]
    return (int(l.x * w), int(l.y * h))

def get_pts(lm, indices, w, h):
    return [get_pt(lm, i, w, h) for i in indices]

def avg_pt(pts):
    return (int(np.mean([p[0] for p in pts])),
            int(np.mean([p[1] for p in pts])))

def widest_pair(lm, lc, rc, w, h):
    best, bl, br = -1, None, None
    for li in lc:
        for ri in rc:
            pl = get_pt(lm, li, w, h); pr = get_pt(lm, ri, w, h)
            d = distance(pl, pr)
            if d > best: best, bl, br = d, pl, pr
    return bl, br, best

def widest_pair_bounded(lm, lc, rc, w, h, face_left_x, face_right_x):
    best, bl, br = -1, None, None
    for li in lc:
        for ri in rc:
            pl = get_pt(lm, li, w, h); pr = get_pt(lm, ri, w, h)
            if pl[0] < face_left_x or pr[0] > face_right_x:
                continue
            d = distance(pl, pr)
            if d > best: best, bl, br = d, pl, pr
    if bl is None:
        return widest_pair(lm, lc, rc, w, h)
    return bl, br, best

def put_text(img, text, pos, scale=0.42, fg=(255,255,255), bg=(20,20,20)):
    cv2.putText(img, text, pos, cv2.FONT_HERSHEY_SIMPLEX, scale, fg, 2, cv2.LINE_AA)
    cv2.putText(img, text, pos, cv2.FONT_HERSHEY_SIMPLEX, scale, bg, 1, cv2.LINE_AA)

def draw_line(img, p1, p2, color, t=1):
    if p1 and p2: cv2.line(img, p1, p2, color, t)

def draw_dot(img, p, r=4, color=(0,255,0)):
    if p: cv2.circle(img, p, r, color, -1)

def filter_brow_pts(pts):
    ys = np.array([p[1] for p in pts], dtype=float)
    q1, q3 = np.percentile(ys, 25), np.percentile(ys, 75)
    iqr = q3 - q1
    if iqr < 1e-6: return pts
    lower_fence = q1 - 1.5*iqr
    upper_fence  = q3 + 1.5*iqr
    filtered = [p for p in pts if lower_fence <= p[1] <= upper_fence]
    return filtered if len(filtered) >= 3 else pts


# ══════════════════════════════════════════════════════
# MODULE 1 — FACE SHAPE  (3 أشكال فقط)
# ══════════════════════════════════════════════════════
#
#  Round      : lwr < 1.18  (وجه دائري — طول قريب من العرض)
#  Oval        : 1.18 ≤ lwr ≤ 1.50  +  الخدود هي الأوسع
#  Rectangular : lwr > 1.40  +  جبهة وفك متقاربان
#
#  منطق: نقيس أولاً lwr (نسبة الطول/العرض) كمرجع رئيسي
#  ثم نستعين بعلاقة الجبهة/الفك/الخدود كمرجع ثانوي
# ══════════════════════════════════════════════════════

def analyze_face_shape(lm, w, h, face_width, face_height):

    top_pts  = [get_pt(lm, i, w, h) for i in FOREHEAD_TOP_IDX]
    chin_pts = [get_pt(lm, i, w, h) for i in CHIN_BOT_IDX]
    forehead_top = avg_pt(top_pts)
    chin_pt      = avg_pt(chin_pts)
    face_length  = distance(forehead_top, chin_pt)

    face_left_pt  = get_pt(lm, FACE_LEFT,  w, h)
    face_right_pt = get_pt(lm, FACE_RIGHT, w, h)
    fl_x = face_left_pt[0]
    fr_x = face_right_pt[0]

    fh_l, fh_r, fh_w   = widest_pair_bounded(lm, FOREHEAD_L, FOREHEAD_R, w, h, fl_x, fr_x)
    jaw_l, jaw_r, jaw_w = widest_pair_bounded(lm, JAW_CAND_L, JAW_CAND_R, w, h, fl_x, fr_x)
    ck_l,  ck_r,  ck_w  = widest_pair_bounded(lm, CHEEK_L,    CHEEK_R,    w, h, fl_x, fr_x)
    tmp_l = get_pt(lm, TEMPLE_L, w, h)
    tmp_r = get_pt(lm, TEMPLE_R, w, h)

    lwr = face_length  / (face_width  + 1e-6)  # نسبة الطول/العرض
    jfr = jaw_w        / (face_width  + 1e-6)  # الفك / العرض الكلي
    ffr = fh_w         / (face_width  + 1e-6)  # الجبهة / العرض الكلي
    cfr = ck_w         / (face_width  + 1e-6)  # الخدود / العرض الكلي
    fj_diff = ffr - jfr                         # موجب=جبهة أعرض، سالب=فك أعرض

    votes = {"Oval": 0, "Round": 0, "Rectangular": 0}

    # ══ ROUND: الطول قريب من العرض ══
    # المؤشر الأقوى: lwr منخفض
    if lwr < 1.10:           votes["Round"] += 6
    elif lwr < 1.18:         votes["Round"] += 4
    elif lwr < 1.25:         votes["Round"] += 2
    # فك ناعم (ليس عريضاً جداً)
    if jfr < 0.82:           votes["Round"] += 2
    # الخدود أوسع من الجبهة والفك
    if cfr >= jfr and cfr >= ffr: votes["Round"] += 1
    # جبهة وفك متقاربان (شكل مستدير)
    if abs(fj_diff) < 0.08:  votes["Round"] += 1

    # ══ RECTANGULAR: طول واضح + توازي الجبهة والفك ══
    # المؤشر الأقوى: lwr مرتفع
    if lwr > 1.55:           votes["Rectangular"] += 6
    elif lwr > 1.45:         votes["Rectangular"] += 5
    elif lwr > 1.35:         votes["Rectangular"] += 3
    elif lwr > 1.25:         votes["Rectangular"] += 1
    # جبهة وفك متقاربان (جانبا المستطيل متوازيان)
    if abs(fj_diff) < 0.10 and lwr > 1.25:  votes["Rectangular"] += 3
    if abs(fj_diff) < 0.07 and lwr > 1.35:  votes["Rectangular"] += 2
    # الخدود ليست أوسع نقطة
    if cfr <= ffr or cfr <= jfr: votes["Rectangular"] += 1

    # ══ OVAL: التوازن المثالي ══
    # النطاق الأمثل: lwr بين 1.18 و 1.50
    if 1.18 <= lwr <= 1.50:  votes["Oval"] += 4
    elif 1.10 <= lwr < 1.18: votes["Oval"] += 2
    elif 1.50 < lwr <= 1.60: votes["Oval"] += 2
    # الخدود هي الأوسع (الميزة الجوهرية للبيضاوي)
    if cfr > jfr and cfr > ffr:  votes["Oval"] += 4
    elif cfr > jfr:               votes["Oval"] += 2
    # نسب متوازنة للجبهة والفك
    if 0.65 <= jfr <= 0.85:  votes["Oval"] += 2
    if 0.75 <= ffr <= 0.95:  votes["Oval"] += 1
    if abs(fj_diff) < 0.12:  votes["Oval"] += 1
    # النطاق الأمثل الضيق للبيضاوي الكلاسيكي
    if 1.22 <= lwr <= 1.42 and cfr > jfr and cfr > ffr:
        votes["Oval"] += 3

    sv = sorted(votes.items(), key=lambda x: -x[1])
    winner = sv[0][0]

    return {
        "shape": winner, "votes": votes,
        "ratios": {
            "length_width": lwr, "jaw_face": jfr,
            "forehead_face": ffr, "cheek_face": cfr,
            "fj_diff": fj_diff,
        },
        "pts": {
            "jaw_l": jaw_l, "jaw_r": jaw_r,
            "fh_l": fh_l,   "fh_r": fh_r,
            "ck_l": ck_l,   "ck_r": ck_r,
            "tmp_l": tmp_l, "tmp_r": tmp_r,
            "top": forehead_top, "chin": chin_pt,
        },
    }

def draw_face_shape(img, res):
    p = res["pts"]
    draw_line(img, p["top"],   p["chin"],  (200,200,0), 1)
    draw_line(img, p["jaw_l"], p["jaw_r"], (0,100,255), 1)
    draw_line(img, p["fh_l"],  p["fh_r"],  (255,100,0), 1)
    draw_line(img, p["ck_l"],  p["ck_r"],  (100,255,0), 1)
    for pt in p.values(): draw_dot(img, pt, 3, (0,220,220))


# ══════════════════════════════════════════════════════
# MODULE 2 — EYES
# ══════════════════════════════════════════════════════
#
# الخرج المطلوب: "شكل + نوع" مدمجان
# مثال: "Almond Hooded" / "Round Protruding" / "Almond Deep-set"
#
# أنواع العيون (6 أنواع) حسب ملف الخبرة:
#   Hooded      → مبطنة:   الجفن يغطي الجفن المتحرك (lid_cover عالٍ)
#   Protruding  → جاحظة:   العين بارزة للأمام (eye_h/iris_h عالٍ + lid_cover منخفض)
#   Droopy      → ناعسة:   الزاوية الخارجية تنزل عن الداخلية (corner_tilt موجب عالٍ)
#   Deep-set    → غائرة:   حاجب بارز + بون الحاجب يغطي العين (brow_eye_gap عالٍ جداً)
#   Normal      → طبيعية:  لا حالة خاصة واضحة
#
# شكل العين (هندسي):
#   Almond → length_ratio >= 2.1
#   Round  → length_ratio < 1.90
#   Average → بينهما
#
# منطق التصنيف:
#   1. نحدد النوع (الحالة الغالبة) بأولوية محددة
#   2. نحدد الشكل الهندسي
#   3. ندمجهما: "Almond Hooded" / "Round Protruding" ...
#   إذا Normal + Almond → "Almond" فقط
#   إذا Normal + Round  → "Round" فقط
# ══════════════════════════════════════════════════════

def analyze_one_eye(lm, eye_d, w, h, face_width, face_height, brow_eye_gap):
    pts = {name: get_pt(lm, idx, w, h) for name, idx in eye_d.items()
           if name in ("inner","outer","upper","lower","iris_top","iris_bot")}

    eye_w  = distance(pts["inner"], pts["outer"])
    eye_h  = distance(pts["upper"], pts["lower"])
    iris_h = distance(pts["iris_top"], pts["iris_bot"])

    if eye_h < 1 or face_width < 1 or iris_h < 1:
        return None, None

    length_ratio      = eye_w / eye_h
    height_face_ratio = eye_h / face_width
    corner_tilt       = (pts["outer"][1] - pts["inner"][1]) / face_width

    eye_open_ratio  = eye_h / iris_h
    lid_cover_ratio = max(0.0, 2.0 - eye_open_ratio) / 2.0

    m = {
        "pts": pts,
        "eye_w": eye_w, "eye_h": eye_h, "iris_h": iris_h,
        "length_ratio": length_ratio,
        "height_face_ratio": height_face_ratio,
        "corner_tilt": corner_tilt,
        "lid_cover_ratio": lid_cover_ratio,
        "brow_eye_gap": brow_eye_gap,
    }

    # ── الشكل الهندسي ──
    if length_ratio >= 2.1:
        geo_shape = "Almond"
    elif length_ratio < 1.90:
        geo_shape = "Round"
    else:
        geo_shape = "Average"

    # ── النوع (الحالة الغالبة) ──
    # أولوية التصنيف: Hooded > Droopy > Protruding > Deep-set > Normal
    #
    # Hooded: الجفن يغطي بشكل واضح
    #   - lid_cover_ratio > 0.18  +  brow_eye_gap < 0.025
    #   - أو lid_cover_ratio > 0.25 (مبطنة واضحة بغض النظر عن الحاجب)
    #
    # Protruding: عين جاحظة بارزة
    #   - eye_open_ratio عالٍ جداً (العين أوسع من قزحيتها بكثير)
    #   - lid_cover_ratio منخفض جداً
    #   - height_face_ratio عالٍ
    #
    # Droopy: زاوية خارجية نازلة
    #   - corner_tilt > 0.030  (الزاوية الخارجية أدنى من الداخلية بشكل واضح)
    #
    # Deep-set: غائرة داخل المحجر
    #   - brow_eye_gap > 0.075  (الحاجب بعيد عن العين = عظمة الحاجب بارزة)
    #   - height_face_ratio < 0.068

    if lid_cover_ratio > 0.25 or (lid_cover_ratio > 0.18 and brow_eye_gap < 0.025):
        eye_type = "Hooded"
    elif corner_tilt > 0.030:
        eye_type = "Droopy"
    elif eye_open_ratio > 1.75 and lid_cover_ratio < 0.10 and height_face_ratio > 0.085:
        eye_type = "Protruding"
    elif brow_eye_gap > 0.075 and height_face_ratio < 0.068:
        eye_type = "Deep-set"
    else:
        eye_type = "Normal"

    # ── الخرج المدمج ──
    if eye_type == "Normal":
        # لا نوع خاص → نعطي الشكل الهندسي فقط
        combined = geo_shape
    else:
        combined = f"{geo_shape} {eye_type}"

    # ── الحجم ──
    if height_face_ratio > 0.095:
        size = "Large"
    elif height_face_ratio < 0.060:
        size = "Small"
    else:
        size = "Normal"

    result = {
        "combined": combined,       # الخرج الرئيسي للنظام الخبير
        "geo_shape": geo_shape,     # الشكل الهندسي فقط
        "eye_type":  eye_type,      # النوع فقط
        "size": size,
        "corner": "Downturned" if corner_tilt > 0.025 else
                  "Upturned"   if corner_tilt < -0.025 else "Neutral",
        "_dbg": (f"lcr={lid_cover_ratio:.3f} open={eye_open_ratio:.2f} "
                 f"beg={brow_eye_gap:.4f} tilt={corner_tilt:.4f} "
                 f"lr={length_ratio:.2f} hfr={height_face_ratio:.3f}"),
    }
    return m, result


def analyze_eyes(lm, w, h, face_width, face_height, brow_gap_L, brow_gap_R):
    mL, rL = analyze_one_eye(lm, L_EYE, w, h, face_width, face_height, brow_gap_L)
    mR, rR = analyze_one_eye(lm, R_EYE, w, h, face_width, face_height, brow_gap_R)

    # تناسق قسري للنوع بين العينين
    if rL is not None and rR is not None:
        type_rank = {"Normal":0,"Deep-set":1,"Droopy":2,"Protruding":2,"Hooded":3}
        rankL = type_rank.get(rL["eye_type"], 0)
        rankR = type_rank.get(rR["eye_type"], 0)
        if abs(rankL - rankR) == 1:
            dominant = rL["eye_type"] if rankL > rankR else rR["eye_type"]
            for r in (rL, rR):
                r["eye_type"] = dominant
                # أعد بناء combined
                if dominant == "Normal":
                    r["combined"] = r["geo_shape"]
                else:
                    r["combined"] = f"{r['geo_shape']} {dominant}"
            rL["_dbg"] += " →forced"
            rR["_dbg"] += " →forced"

    return {"Left": (mL, rL), "Right": (mR, rR)}


def draw_one_eye(img, m, res, label):
    if m is None: return
    pts = m["pts"]
    for p in pts.values(): draw_dot(img, p, 3, (0,255,0))
    draw_line(img, pts["inner"], pts["outer"], (200,200,0), 1)
    draw_line(img, pts["upper"], pts["lower"], (0,200,255), 1)
    bx = min(pts["inner"][0], pts["outer"][0]) - 5
    by = min(pts["upper"][1], pts["iris_top"][1]) - 50
    lines = [
        label,
        f"Eye: {res['combined']}",
        f"Size:{res['size']}  Corner:{res['corner']}",
    ]
    for i, ln in enumerate(lines): put_text(img, ln, (bx, by + i*16))


# ══════════════════════════════════════════════════════
# MODULE 3 — BROWS
# ══════════════════════════════════════════════════════
#
# إصلاح "مقوسة دائماً":
#   Arched:    arch >= 0.050  (عتبة أعلى — مقوسة فعلاً)
#   Soft Arch: 0.018 <= arch < 0.050  (الحالة الغالبة = حواجب طبيعية بقوس خفيف)
#   Straight:  arch < 0.018
#
# السبب: arch يُحسب كنسبة من face_height
#   قيمة 0.030-0.044 = قوس خفيف طبيعي → Soft Arch
#   قيمة >= 0.050 = مقوسة واضحة بصرياً → Arched
# ══════════════════════════════════════════════════════

def analyze_one_brow(brow_pts, eye_top_y, face_width, face_height):
    clean_pts = filter_brow_pts(brow_pts)
    ys_clean  = [p[1] for p in clean_pts]
    xs_all    = [p[0] for p in brow_pts]

    top_y = min(ys_clean)
    bot_y = max(ys_clean)

    thickness = (bot_y - top_y) / face_height
    length    = (max(xs_all) - min(xs_all)) / face_width

    peak_pt  = min(clean_pts, key=lambda p: p[1])
    left_pt  = min(clean_pts, key=lambda p: p[0])
    right_pt = max(clean_pts, key=lambda p: p[0])

    denom   = max(right_pt[0] - left_pt[0], 1)
    chord_y = left_pt[1] + (right_pt[1]-left_pt[1]) * (peak_pt[0]-left_pt[0]) / denom
    arch    = (chord_y - peak_pt[1]) / face_height

    brow_eye_gap = (eye_top_y - bot_y) / face_height

    return {
        "thickness": thickness, "length": length,
        "arch": arch, "brow_eye_gap": brow_eye_gap,
        "peak_pt": peak_pt, "left_pt": left_pt, "right_pt": right_pt,
        "brow_bot_y": bot_y, "clean_pts": clean_pts,
    }


def classify_brows(fL, fR, inter_ratio):
    facts = {}
    thickness    = (fL["thickness"]    + fR["thickness"])    / 2
    length       = (fL["length"]       + fR["length"])       / 2
    arch         = (fL["arch"]         + fR["arch"])         / 2
    brow_eye_gap = (fL["brow_eye_gap"] + fR["brow_eye_gap"]) / 2

    # السماكة
    if thickness >= 0.078:   facts["Thickness"] = "Thick"
    elif thickness >= 0.048: facts["Thickness"] = "Medium"
    else:                    facts["Thickness"] = "Thin"

    # الطول
    if length >= 0.32:       facts["Length"] = "Long"
    elif length <= 0.22:     facts["Length"] = "Short"
    else:                    facts["Length"] = "Medium"

    # الشكل — عتبة مرفوعة لتجنب "Arched دائماً"
    if arch >= 0.050:        facts["Shape"] = "Arched"
    elif arch >= 0.018:      facts["Shape"] = "Soft Arch"
    else:                    facts["Shape"] = "Straight"

    # الموضع
    if brow_eye_gap >= 0.080:    facts["Position"] = "High"
    elif brow_eye_gap <= 0.020:  facts["Position"] = "Low"
    else:                        facts["Position"] = "Normal"

    # المسافة بين الحاجبين
    if inter_ratio < 0.08:   facts["Spacing"] = "Close"
    elif inter_ratio > 0.18: facts["Spacing"] = "Wide"
    else:                    facts["Spacing"] = "Normal"

    # التماثل
    sym = (abs(fL["thickness"]    - fR["thickness"])    +
           abs(fL["length"]       - fR["length"])       +
           abs(fL["arch"]         - fR["arch"])         +
           abs(fL["brow_eye_gap"] - fR["brow_eye_gap"])) / 4
    if sym < 0.008:          facts["Symmetry"] = "Symmetrical"
    elif sym < 0.020:        facts["Symmetry"] = "Slightly Asymmetrical"
    else:                    facts["Symmetry"] = "Asymmetrical"

    return facts


def analyze_brows(lm, w, h, face_width, face_height):
    l_pts     = get_pts(lm, L_BROW_IDX, w, h)
    r_pts     = get_pts(lm, R_BROW_IDX, w, h)
    l_eye_top = get_pt(lm, L_EYE["upper"], w, h)[1]
    r_eye_top = get_pt(lm, R_EYE["upper"], w, h)[1]

    fL = analyze_one_brow(l_pts, l_eye_top, face_width, face_height)
    fR = analyze_one_brow(r_pts, r_eye_top, face_width, face_height)

    left_inner_x  = max(p[0] for p in l_pts)
    right_inner_x = min(p[0] for p in r_pts)
    inter_ratio   = abs(right_inner_x - left_inner_x) / face_width

    return {
        "feats_L": fL, "feats_R": fR,
        "inter_ratio": inter_ratio,
        "classification": classify_brows(fL, fR, inter_ratio),
        "pts_L": l_pts, "pts_R": r_pts,
        "brow_eye_gap_L": fL["brow_eye_gap"],
        "brow_eye_gap_R": fR["brow_eye_gap"],
    }


def draw_brows(img, br):
    for pts, feats, color, label in [
        (br["pts_L"], br["feats_L"], (0,220,80),  "L.Brow"),
        (br["pts_R"], br["feats_R"], (80,180,255), "R.Brow"),
    ]:
        peak = feats["peak_pt"]; lp = feats["left_pt"]; rp = feats["right_pt"]
        for p in feats["clean_pts"]: draw_dot(img, p, 3, color)
        for p in pts:
            if p not in feats["clean_pts"]: draw_dot(img, p, 4, (0,0,220))
        draw_line(img, lp, rp, (180,180,180), 1)
        chord_y = int(lp[1] + (rp[1]-lp[1]) * (peak[0]-lp[0]) / max(rp[0]-lp[0],1))
        draw_line(img, (peak[0], chord_y), peak, (255,200,0), 1)
        draw_dot(img, peak, 5, (255,200,0))
        put_text(img, label, (lp[0], lp[1]-20))


# ══════════════════════════════════════════════════════
# MODULE 4 — LIPS
# ══════════════════════════════════════════════════════
#
# إصلاح منطق التوازن:
#
#   balance_ratio = upper_h / total_h
#
#   > 0.55 → الشفة العليا تأخذ أكثر من 55% من الحجم الكلي
#            ∴ الشفة العليا أسمك / أكبر
#            ∴ التصحيح المطلوب: على السفلى (لتكبيرها)
#            → نسمي: "Upper Fuller" (العليا ممتلئة أكثر)
#
#   < 0.45 → الشفة السفلى تأخذ أكثر من 55% من الحجم الكلي
#            ∴ الشفة السفلى أسمك / أكبر  ← الأكثر شيوعاً
#            ∴ التصحيح المطلوب: على العليا (لتكبيرها)
#            → نسمي: "Lower Fuller" (السفلى ممتلئة أكثر)
#
#   الخرج للنظام الخبير يكون:
#   "Lower Fuller" → التصحيح على الشفة العليا
#   "Upper Fuller" → التصحيح على الشفة السفلى
#   "Balanced"     → لا تصحيح
# ══════════════════════════════════════════════════════

def analyze_lips(lm, w, h, face_width, face_height):
    left_pt        = get_pt(lm, MOUTH_LEFT,       w, h)
    right_pt       = get_pt(lm, MOUTH_RIGHT,      w, h)
    upper_top_pt   = get_pt(lm, UPPER_LIP_TOP,    w, h)
    upper_inner_pt = get_pt(lm, UPPER_LIP_INNER,  w, h)
    lower_inner_pt = get_pt(lm, LOWER_LIP_INNER,  w, h)
    lower_bot_pt   = get_pt(lm, LOWER_LIP_BOT,    w, h)
    cupid_l_pt     = get_pt(lm, CUPID_LEFT,       w, h)
    cupid_c_pt     = get_pt(lm, CUPID_CENTER,     w, h)
    cupid_r_pt     = get_pt(lm, CUPID_RIGHT,      w, h)
    ul_left_pt     = get_pt(lm, UL_LEFT_INNER,    w, h)
    ul_right_pt    = get_pt(lm, UL_RIGHT_INNER,   w, h)
    ll_left_pt     = get_pt(lm, LL_LEFT_INNER,    w, h)
    ll_right_pt    = get_pt(lm, LL_RIGHT_INNER,   w, h)
    eye_l_pt       = get_pt(lm, L_EYE["inner"],   w, h)
    eye_r_pt       = get_pt(lm, R_EYE["inner"],   w, h)

    mouth_w       = distance(left_pt, right_pt)
    upper_h       = distance(upper_top_pt,   upper_inner_pt)
    lower_h       = distance(lower_inner_pt, lower_bot_pt)
    total_h       = upper_h + lower_h
    volume_ratio  = total_h / face_height

    # balance_ratio: نسبة الشفة العليا من الحجم الكلي
    # > 0.5 → العليا أكبر / < 0.5 → السفلى أكبر
    balance_ratio = upper_h / (total_h + 1e-6)

    left_gap  = abs(ul_left_pt[1]  - ll_left_pt[1])
    right_gap = abs(ul_right_pt[1] - ll_right_pt[1])
    symmetry  = abs(left_gap - right_gap) / (mouth_w + 1e-6)

    eye_dist          = distance(eye_l_pt, eye_r_pt)
    mouth_width_ratio = mouth_w / (eye_dist + 1e-6)

    cupid_avg_y = (cupid_l_pt[1] + cupid_r_pt[1]) / 2
    cupid_depth = (cupid_c_pt[1] - cupid_avg_y) / (face_height + 1e-6)
    corner_tilt = (right_pt[1] - left_pt[1]) / (mouth_w + 1e-6)

    feats = {
        "pts": {"left": left_pt, "right": right_pt,
                "upper_top": upper_top_pt, "upper_inner": upper_inner_pt,
                "lower_inner": lower_inner_pt, "lower_bot": lower_bot_pt,
                "cupid_l": cupid_l_pt, "cupid_c": cupid_c_pt, "cupid_r": cupid_r_pt},
        "volume_ratio": volume_ratio, "balance_ratio": balance_ratio,
        "symmetry": symmetry, "mouth_width_ratio": mouth_width_ratio,
        "cupid_depth": cupid_depth, "corner_tilt": corner_tilt,
        "upper_h": upper_h, "lower_h": lower_h,
    }

    result = {}

    # الحجم الكلي
    if volume_ratio >= 0.100:   result["Volume"]    = "Full"
    elif volume_ratio >= 0.055: result["Volume"]    = "Medium"
    else:                       result["Volume"]    = "Thin"

    # التوازن — المنطق المصحح:
    # balance_ratio > 0.55 → العليا تأخذ > 55% → العليا أضخم → "Upper Fuller"
    # balance_ratio < 0.45 → السفلى تأخذ > 55% → السفلى أضخم → "Lower Fuller"
    if balance_ratio > 0.55:
        result["Balance"]   = "Upper Fuller"       # العليا أكبر → التصحيح على السفلى
        result["Correction"] = "Needs Lower Lip Enhancement"
    elif balance_ratio < 0.45:
        result["Balance"]   = "Lower Fuller"       # السفلى أكبر → التصحيح على العليا
        result["Correction"] = "Needs Upper Lip Enhancement"
    else:
        result["Balance"]   = "Balanced"
        result["Correction"] = "No correction needed"

    # التماثل
    if symmetry < 0.04:         result["Symmetry"]  = "Symmetrical"
    elif symmetry < 0.10:       result["Symmetry"]  = "Slightly Asymmetrical"
    else:                       result["Symmetry"]  = "Asymmetrical"

    # العرض
    if mouth_width_ratio < 0.90:  result["Width"]   = "Narrow"
    elif mouth_width_ratio > 1.20: result["Width"]  = "Wide"
    else:                          result["Width"]  = "Average"

    # قوس كيوبيد
    if cupid_depth > 0.018:     result["Cupid Bow"] = "Defined"
    elif cupid_depth > 0.008:   result["Cupid Bow"] = "Soft"
    else:                       result["Cupid Bow"] = "Flat"

    # الزوايا
    if corner_tilt > 0.06:      result["Corners"]   = "Downturned"
    elif corner_tilt < -0.06:   result["Corners"]   = "Upturned"
    else:                       result["Corners"]   = "Neutral"

    return feats, result


def draw_lips(img, feats, result):
    pts = feats["pts"]
    draw_dot(img, pts["left"],        4, (0,255,0))
    draw_dot(img, pts["right"],       4, (0,255,0))
    draw_dot(img, pts["upper_top"],   4, (255,140,0))
    draw_dot(img, pts["upper_inner"], 4, (255,140,0))
    draw_dot(img, pts["lower_inner"], 4, (0,140,255))
    draw_dot(img, pts["lower_bot"],   4, (0,140,255))
    draw_dot(img, pts["cupid_l"],     5, (200,0,200))
    draw_dot(img, pts["cupid_c"],     5, (200,0,200))
    draw_dot(img, pts["cupid_r"],     5, (200,0,200))
    draw_line(img, pts["upper_top"],   pts["upper_inner"], (255,140,0), 1)
    draw_line(img, pts["lower_inner"], pts["lower_bot"],   (0,140,255), 1)
    draw_line(img, pts["left"],        pts["right"],       (200,200,0), 1)
    bx = pts["left"][0] - 5; by = pts["upper_top"][1] - 70
    for i, (k,v) in enumerate(result.items()):
        put_text(img, f"{k}: {v}", (bx, by+i*15), scale=0.38)


# ══════════════════════════════════════════════════════
# MODULE 5 — NOSE  (Long / Short / Balanced)
# ══════════════════════════════════════════════════════

def analyze_nose(lm, w, h, face_width, face_height, face_top_y, face_chin_y):
    tip_pt    = get_pt(lm, NOSE_TIP,        w, h)
    bridge_pt = get_pt(lm, NOSE_BRIDGE_T,   w, h)
    start_pt  = get_pt(lm, NOSE_LENGTH_TOP, w, h)
    alar_l_pt = get_pt(lm, ALAR_L_OUTER,    w, h)
    alar_r_pt = get_pt(lm, ALAR_R_OUTER,    w, h)
    alar_lb_pt = get_pt(lm, ALAR_L_BASE,    w, h)
    alar_rb_pt = get_pt(lm, ALAR_R_BASE,    w, h)

    nose_length       = distance(start_pt, tip_pt)
    nose_length_ratio = nose_length / (face_height + 1e-6)
    alar_width        = distance(alar_l_pt, alar_r_pt)
    alar_width_ratio  = alar_width / (face_width + 1e-6)
    base_width        = distance(alar_lb_pt, alar_rb_pt)
    base_width_ratio  = base_width / (face_width + 1e-6)
    tip_position      = (tip_pt[1] - face_top_y) / (face_height + 1e-6)

    votes = {"Long": 0, "Short": 0, "Balanced": 0}

    if nose_length_ratio > 0.48:
        votes["Long"] += 4
    elif nose_length_ratio < 0.38:
        votes["Short"] += 4
    else:
        votes["Balanced"] += 3

    if tip_position > 0.60:   votes["Long"]     += 2
    elif tip_position < 0.47: votes["Short"]    += 2
    else:                      votes["Balanced"] += 2

    if alar_width_ratio < 0.22 and votes["Long"] > 0:   votes["Long"]  += 1
    elif alar_width_ratio > 0.32 and votes["Short"] > 0: votes["Short"] += 1

    sv = sorted(votes.items(), key=lambda x: -x[1])
    nose_shape = sv[0][0]

    return {
        "shape": nose_shape, "votes": votes,
        "metrics": {
            "nose_length_ratio": nose_length_ratio,
            "alar_width_ratio":  alar_width_ratio,
            "base_width_ratio":  base_width_ratio,
            "tip_position":      tip_position,
        },
        "pts": {
            "tip": tip_pt, "bridge": bridge_pt, "start": start_pt,
            "alar_l": alar_l_pt, "alar_r": alar_r_pt,
            "base_l": alar_lb_pt, "base_r": alar_rb_pt,
        },
    }


def draw_nose(img, res):
    p = res["pts"]
    draw_dot(img, p["tip"],    5, (255,80,0))
    draw_dot(img, p["bridge"], 4, (255,160,0))
    draw_dot(img, p["start"],  4, (200,200,0))
    draw_dot(img, p["alar_l"], 4, (0,200,200))
    draw_dot(img, p["alar_r"], 4, (0,200,200))
    draw_dot(img, p["base_l"], 4, (0,160,255))
    draw_dot(img, p["base_r"], 4, (0,160,255))
    draw_line(img, p["start"],  p["tip"],    (255,140,0), 1)
    draw_line(img, p["alar_l"], p["alar_r"], (0,200,200), 1)
    draw_line(img, p["base_l"], p["base_r"], (0,160,255), 1)
    bx = p["tip"][0]+8; by = p["tip"][1]
    put_text(img, f"Nose: {res['shape']}", (bx, by), scale=0.40)


# ══════════════════════════════════════════════════════
# PRINT HELPERS
# ══════════════════════════════════════════════════════

def section(title):
    print(f"\n{'='*58}\n  {title}\n{'='*58}")

def row(label, value, w=28):
    print(f"  {label:<{w}}: {value}")


# ══════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════

def main(image_path: str, output_path: str = "face_analysis_result.jpg"):
    image = cv2.imread(image_path)
    if image is None:
        print(f"[ERROR] Image not found: {image_path}"); return

    h, w, _ = image.shape
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    with mp.solutions.face_mesh.FaceMesh(
        static_image_mode=True, max_num_faces=1, refine_landmarks=True
    ) as mesh:
        res = mesh.process(rgb)
        if not res.multi_face_landmarks:
            print("[ERROR] No face detected"); return
        lm = res.multi_face_landmarks[0].landmark

        face_width  = distance(get_pt(lm, FACE_LEFT,  w, h), get_pt(lm, FACE_RIGHT, w, h))
        face_height = distance(get_pt(lm, FACE_TOP,   w, h), get_pt(lm, FACE_CHIN,  w, h))
        face_top_y  = get_pt(lm, FACE_TOP,  w, h)[1]
        face_chin_y = get_pt(lm, FACE_CHIN, w, h)[1]

        brow_res           = analyze_brows(lm, w, h, face_width, face_height)
        eye_res            = analyze_eyes(lm, w, h, face_width, face_height,
                                          brow_res["brow_eye_gap_L"],
                                          brow_res["brow_eye_gap_R"])
        face_res           = analyze_face_shape(lm, w, h, face_width, face_height)
        lip_feats, lip_res = analyze_lips(lm, w, h, face_width, face_height)
        nose_res           = analyze_nose(lm, w, h, face_width, face_height,
                                          face_top_y, face_chin_y)

        draw_face_shape(image, face_res)
        draw_brows(image, brow_res)
        for side, (m_eye, r_eye) in eye_res.items():
            draw_one_eye(image, m_eye, r_eye, side)
        draw_lips(image, lip_feats, lip_res)
        draw_nose(image, nose_res)

        # ══ طباعة ══

        section("REFERENCE")
        row("face_width",  f"{face_width:.1f} px")
        row("face_height", f"{face_height:.1f} px")

        section("FACE SHAPE  (Oval / Round / Rectangular)")
        r = face_res["ratios"]
        row("length_width",  f"{r['length_width']:.3f}   (<1.18=Round → >1.40=Rectangular)")
        row("jaw_face",      f"{r['jaw_face']:.3f}")
        row("forehead_face", f"{r['forehead_face']:.3f}")
        row("cheek_face",    f"{r['cheek_face']:.3f}   (أوسع=Oval)")
        row("fj_diff",       f"{r['fj_diff']:+.3f}   (الجبهة - الفك)")
        print()
        for sn, v in sorted(face_res["votes"].items(), key=lambda x: -x[1]):
            print(f"  {sn:<14}: {'█'*v} ({v})")
        print()
        row("★ Face Shape", face_res["shape"])

        section("BROWS")
        fL = brow_res["feats_L"]; fR = brow_res["feats_R"]
        avg_arch = (fL['arch'] + fR['arch']) / 2
        row("arch",         f"L={fL['arch']:.4f}  R={fR['arch']:.4f}  avg={avg_arch:.4f}  (>=0.050=Arched, >=0.018=SoftArch)")
        row("thickness",    f"L={fL['thickness']:.4f}  R={fR['thickness']:.4f}")
        row("length",       f"L={fL['length']:.4f}  R={fR['length']:.4f}")
        row("brow_eye_gap", f"L={fL['brow_eye_gap']:.4f}  R={fR['brow_eye_gap']:.4f}")
        row("inter_brow",   f"{brow_res['inter_ratio']:.4f}")
        print()
        for k, v in brow_res["classification"].items(): row(k, v)

        section("EYES")
        for side, (m_eye, r_eye) in eye_res.items():
            if m_eye is None: continue
            print(f"\n  [{side}]")
            row("  length_ratio",      f"{m_eye['length_ratio']:.3f}  (>=2.1=Almond, <1.90=Round)")
            row("  height_face_ratio", f"{m_eye['height_face_ratio']:.3f}  (>0.095=Large, <0.060=Small)")
            row("  lid_cover_ratio",   f"{m_eye['lid_cover_ratio']:.3f}  (>0.25→Hooded, >0.18+beg<0.025→Hooded)")
            row("  eye_open_ratio",    f"{m_eye['eye_h']/m_eye['iris_h']:.3f}  (>1.75→Protruding)")
            row("  brow_eye_gap",      f"{m_eye['brow_eye_gap']:.4f}  (>0.075→Deep-set)")
            row("  corner_tilt",       f"{m_eye['corner_tilt']:.4f}  (>0.030→Droopy)")
            row("  debug",             r_eye["_dbg"])
            print()
            row("  ★ Eye (Shape+Type)", r_eye["combined"])
            row("  Size",              r_eye["size"])
            row("  Corner",            r_eye["corner"])

        section("NOSE  (Long / Short / Balanced)")
        m = nose_res["metrics"]
        row("nose_length_ratio", f"{m['nose_length_ratio']:.4f}  (>0.48=Long, <0.38=Short)")
        row("alar_width_ratio",  f"{m['alar_width_ratio']:.4f}")
        row("tip_position",      f"{m['tip_position']:.4f}  (>0.60→Long)")
        print()
        for sn, v in sorted(nose_res["votes"].items(), key=lambda x: -x[1]):
            print(f"  {sn:<14}: {'█'*v} ({v})")
        print()
        row("★ Nose Shape", nose_res["shape"])

        section("LIPS")
        row("upper_h",       f"{lip_feats['upper_h']:.1f} px")
        row("lower_h",       f"{lip_feats['lower_h']:.1f} px")
        row("balance_ratio", f"{lip_feats['balance_ratio']:.4f}  (>0.55=UpperFuller / <0.45=LowerFuller)")
        row("volume_ratio",  f"{lip_feats['volume_ratio']:.4f}  (>=0.100=Full)")
        row("mouth_width_ratio", f"{lip_feats['mouth_width_ratio']:.4f}")
        row("cupid_depth",   f"{lip_feats['cupid_depth']:.4f}")
        row("corner_tilt",   f"{lip_feats['corner_tilt']:.4f}")
        print()
        for k, v in lip_res.items(): row(k, v)

        # ══ ملخص نهائي ══
        section("★ FINAL SUMMARY  (للنظام الخبير)")
        row("Face Shape",     face_res["shape"])
        eye_L_res = eye_res["Left"][1]
        eye_R_res = eye_res["Right"][1]
        row("Eye (L)",        eye_L_res["combined"] if eye_L_res else "N/A")
        row("Eye (R)",        eye_R_res["combined"] if eye_R_res else "N/A")
        row("Eye Size",       eye_L_res["size"]     if eye_L_res else "N/A")
        row("Brow Thickness", brow_res["classification"].get("Thickness","N/A"))
        row("Brow Length",    brow_res["classification"].get("Length","N/A"))
        row("Brow Shape",     brow_res["classification"].get("Shape","N/A"))
        row("Nose Shape",     nose_res["shape"])
        row("Lip Volume",     lip_res.get("Volume","N/A"))
        row("Lip Balance",    lip_res.get("Balance","N/A"))
        row("Lip Correction", lip_res.get("Correction","N/A"))

    cv2.imwrite(output_path, image)
    print(f"\n[OK] Saved → {output_path}")


if __name__ == "__main__":
    main(
        image_path  = "pictures2/photo_2026-06-04_11-18-37.jpg",
        output_path = "face_analysis_result.jpg",
    )