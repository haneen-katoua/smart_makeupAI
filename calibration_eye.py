import os
import cv2
import mediapipe as mp
import math

# =====================================
# حساب المسافة
# =====================================

def distance(p1, p2):

    return math.sqrt(
        (p1[0] - p2[0])**2 +
        (p1[1] - p2[1])**2
    )

# =====================================
# حساب زاوية العين
# =====================================

def calculate_angle(p1, p2):

    x1, y1 = p1
    x2, y2 = p2

    angle = math.degrees(
        math.atan2(
            (y2 - y1),
            (x2 - x1)
        )
    )

    return angle

# =====================================
# تشغيل FaceMesh
# =====================================

mp_face_mesh = mp.solutions.face_mesh

# =====================================
# نقاط العين
# =====================================

LEFT_EYE = {

    "left_corner": 33,
    "right_corner": 133,

    "top": 159,
    "bottom": 145,

    "upper_lid": 158,

    "brow": 70
}

# =====================================
# مسار الداتا سيت
# =====================================

DATASET_PATH = "dataset"

# =====================================
# تشغيل FaceMesh
# =====================================

with mp_face_mesh.FaceMesh(
    static_image_mode=True,
    max_num_faces=1,
    refine_landmarks=True
) as face_mesh:

    # =====================================
    # المرور على أنواع العيون
    # =====================================

    for eye_type in os.listdir(DATASET_PATH):

        folder_path = os.path.join(DATASET_PATH, eye_type)

        # =====================================
        # تخزين النتائج
        # =====================================

        eye_ratios = []
        eyelid_ratios = []
        brow_ratios = []

        # NEW FEATURES
        eye_angles = []
        corner_differences = []

        print("\n====================")
        print("TYPE:", eye_type)
        print("====================")

        # =====================================
        # المرور على الصور
        # =====================================

        for filename in os.listdir(folder_path):

            image_path = os.path.join(folder_path, filename)

            image = cv2.imread(image_path)

            if image is None:
                continue

            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            results = face_mesh.process(rgb)

            # =====================================
            # إذا لم يكتشف وجه
            # =====================================

            if not results.multi_face_landmarks:
                continue

            face_landmarks = results.multi_face_landmarks[0]

            h, w, _ = image.shape

            points = {}

            # =====================================
            # استخراج النقاط
            # =====================================

            for name, idx in LEFT_EYE.items():

                landmark = face_landmarks.landmark[idx]

                x = int(landmark.x * w)
                y = int(landmark.y * h)

                points[name] = (x, y)

            # =====================================
            # الحسابات الأساسية
            # =====================================

            eye_width = distance(
                points["left_corner"],
                points["right_corner"]
            )

            eye_height = distance(
                points["top"],
                points["bottom"]
            )

            eyelid_height = distance(
                points["top"],
                points["upper_lid"]
            )

            brow_distance = distance(
                points["top"],
                points["brow"]
            )

            # =====================================
            # Ratios
            # =====================================

            eye_ratio = eye_height / eye_width

            eyelid_ratio = eyelid_height / eye_width

            brow_ratio = brow_distance / eye_width

            # =====================================
            # Eye Angle
            # =====================================

            eye_angle = calculate_angle(
                points["left_corner"],
                points["right_corner"]
            )

            # =====================================
            # Corner Difference
            # =====================================

            corner_difference = (
                points["right_corner"][1]
                - points["left_corner"][1]
            )

            # =====================================
            # تخزين النتائج
            # =====================================

            eye_ratios.append(eye_ratio)

            eyelid_ratios.append(eyelid_ratio)

            brow_ratios.append(brow_ratio)

            eye_angles.append(eye_angle)

            corner_differences.append(corner_difference)

        # =====================================
        # الإحصائيات النهائية
        # =====================================

        if eye_ratios:

            print("\n========== AVERAGES ==========")

            print(
                "Average Eye Ratio:",
                sum(eye_ratios) / len(eye_ratios)
            )

            print(
                "Average Eyelid Ratio:",
                sum(eyelid_ratios) / len(eyelid_ratios)
            )

            print(
                "Average Brow Ratio:",
                sum(brow_ratios) / len(brow_ratios)
            )

            print(
                "Average Eye Angle:",
                sum(eye_angles) / len(eye_angles)
            )

            print(
                "Average Corner Difference:",
                sum(corner_differences) / len(corner_differences)
            )

            # =====================================

            print("\n========== MIN VALUES ==========")

            print("Min Eye Ratio:", min(eye_ratios))

            print("Min Eyelid Ratio:", min(eyelid_ratios))

            print("Min Brow Ratio:", min(brow_ratios))

            print("Min Eye Angle:", min(eye_angles))

            print(
                "Min Corner Difference:",
                min(corner_differences)
            )

            # =====================================

            print("\n========== MAX VALUES ==========")

            print("Max Eye Ratio:", max(eye_ratios))

            print("Max Eyelid Ratio:", max(eyelid_ratios))

            print("Max Brow Ratio:", max(brow_ratios))

            print("Max Eye Angle:", max(eye_angles))

            print(
                "Max Corner Difference:",
                max(corner_differences)
            )