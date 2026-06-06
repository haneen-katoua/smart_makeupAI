import cv2
import mediapipe as mp
import math

# =====================================================
# حساب المسافة بين نقطتين
# =====================================================

def distance(p1, p2):

    return math.sqrt(
        (p1[0] - p2[0])**2 +
        (p1[1] - p2[1])**2
    )

# =====================================================
# حساب ميل العين
# =====================================================

def calculate_slope(p1, p2):

    x1, y1 = p1
    x2, y2 = p2

    dx = x2 - x1
    dy = y2 - y1

    if dx == 0:
        return 0

    return dy / dx

# =====================================================
# قراءة الصورة
# =====================================================

image = cv2.imread("pictures2/photo_2026-06-04_11-19-47.jpg")

if image is None:

    print("Image not found")
    exit()

# =====================================================
# تحويل RGB
# =====================================================

rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# =====================================================
# MediaPipe FaceMesh
# =====================================================

mp_face_mesh = mp.solutions.face_mesh

# =====================================================
# نقاط العين
# =====================================================

LEFT_EYE = {

    # زوايا العين
    "left_corner": 33,
    "right_corner": 133,

    # أعلى وأسفل العين
    "top": 159,
    "bottom": 145,

    # الجفن
    "upper_lid": 158,

    # الحاجب
    "brow": 70
}

# =====================================================
# تشغيل التحليل
# =====================================================

with mp_face_mesh.FaceMesh(
    static_image_mode=True,
    max_num_faces=1,
    refine_landmarks=True
) as face_mesh:

    results = face_mesh.process(rgb)

    # =====================================================
    # إذا لم يتم اكتشاف وجه
    # =====================================================

    if not results.multi_face_landmarks:

        print("No face detected")
        exit()

    face_landmarks = results.multi_face_landmarks[0]

    h, w, _ = image.shape

    points = {}

    # =====================================================
    # استخراج النقاط
    # =====================================================

    for name, idx in LEFT_EYE.items():

        landmark = face_landmarks.landmark[idx]

        x = int(landmark.x * w)
        y = int(landmark.y * h)

        points[name] = (x, y)

        # رسم النقاط
        cv2.circle(
            image,
            (x, y),
            4,
            (0,255,0),
            -1
        )


# =====================================================
# الحسابات الأساسية
# =====================================================

    # عرض العين
    eye_width = distance(
        points["left_corner"],
        points["right_corner"]
    )

    # ارتفاع العين
    eye_height = distance(
        points["top"],
        points["bottom"]
    )

    # ارتفاع الجفن
    eyelid_height = distance(
        points["top"],
        points["upper_lid"]
    )

    # المسافة للحاجب
    brow_distance = distance(
        points["top"],
        points["brow"]
    )

# =====================================================
# الحسابات النهائية
# =====================================================

    # نسبة ارتفاع العين
    eye_ratio = eye_height / eye_width

    # نسبة الجفن
    eyelid_ratio = eyelid_height / eye_width

    # نسبة الحاجب
    brow_ratio = brow_distance / eye_width

    # ميل العين
    eye_slope = calculate_slope(
        points["left_corner"],
        points["right_corner"]
    )

    # فرق الزوايا الحقيقي
    corner_difference_ratio = (

        points["right_corner"][1]
        - points["left_corner"][1]

    ) / eye_width

# =====================================================
# طباعة النتائج
# =====================================================

    print("\n========== FEATURES ==========")

    print("Eye Ratio:", eye_ratio)

    print("Eyelid Ratio:", eyelid_ratio)

    print("Brow Ratio:", brow_ratio)

    print("Eye Slope:", eye_slope)

    print(
        "Corner Difference Ratio:",
        corner_difference_ratio
    )

# =====================================================
# التصنيفات
# =====================================================

    eye_features = []

# =====================================================
# HOODED EYES
# =====================================================

    """
    العين المبطنة:
    - ارتفاع العين أصغر
    - الجفن أصغر
    """

    if (

        eye_ratio < 0.34

        and eyelid_ratio < 0.20

    ):

        eye_features.append("Hooded")

# =====================================================
# ROUND EYES
# =====================================================

    """
    العين المدورة:
    - ارتفاع العين كبير
    """

    if eye_ratio > 0.375:

        eye_features.append("Round")

# =====================================================
# ALMOND EYES
# =====================================================

    """
    العين اللوزية:
    - ميل للأعلى
    - زاوية خارجية مرتفعة
    """

    if (

        eye_slope > 0.05

        and corner_difference_ratio > 0.08

    ):

        eye_features.append("Almond")

# =====================================================
# DROOPY EYES
# =====================================================

    """
    العين الناعسة:
    - نزول الزاوية الخارجية
    """

    if (

        eye_slope < -0.02

        or corner_difference_ratio < 0

    ):

        eye_features.append("Droopy")

# =====================================================
# BIG EYES
# =====================================================

    if eye_ratio > 0.41:

        eye_features.append("Big Eyes")

# =====================================================
# SMALL EYES
# =====================================================

    if eye_ratio < 0.28:

        eye_features.append("Small Eyes")

# =====================================================
# إذا لم يوجد تصنيف
# =====================================================

    if len(eye_features) == 0:

        eye_features.append("Normal")

# =====================================================
# النتيجة النهائية
# =====================================================

    final_result = ", ".join(eye_features)

    print("\n========== RESULT ==========")

    print(final_result)


# =====================================================
# حفظ الصورة
# =====================================================

cv2.imwrite(
    "eye_analysis_result.jpg",
    image
)

print("\nResult saved")