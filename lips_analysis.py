import cv2
import mediapipe as mp
import math

# =========================
# Distance
# =========================
def distance(p1, p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

# =========================
# Classification
# =========================
def classify_lips(
    lip_ratio,
    symmetry,
    balance_ratio,
    mouth_width_ratio
):

    result = []

    # =========================
    # 1. Volume
    # =========================
    if lip_ratio < 0.08:
        result.append("Thin Lips")
    elif lip_ratio < 0.14:
        result.append("Medium Lips")
    else:
        result.append("Full Lips")

    # =========================
    # 2. Symmetry
    # =========================
    if symmetry < 0.01:
        result.append("Symmetrical Lips")
    elif symmetry < 0.03:
        result.append("Slightly Asymmetrical Lips")
    else:
        result.append("Asymmetrical Lips")

    # =========================
    # 3. Balance
    # =========================
    if balance_ratio > 0.53:
        result.append("Upper Lip Fuller")

    elif balance_ratio < 0.47:
        result.append("Lower Lip Fuller")

    else:
        result.append("Balanced Lips")
    
    
        # =========================
    # 4. Mouth Width
    # =========================
    if mouth_width_ratio < 0.55:
        result.append("Narrow Mouth")

    elif mouth_width_ratio > 0.70:
        result.append("Wide Mouth")

    else:
        result.append("Average Mouth")
            
    return ", ".join(result)    
        
        

# =========================
# Load image
# =========================
image_path = "pictures2/photo_2026-06-04_11-19-47.jpg"

image = cv2.imread(image_path)

if image is None:
    print("Image not found")
    exit()

h, w, _ = image.shape
rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# =========================
# FaceMesh
# =========================
mp_face_mesh = mp.solutions.face_mesh

with mp_face_mesh.FaceMesh(
    static_image_mode=True,
    max_num_faces=1,
    refine_landmarks=True
) as face_mesh:

    results = face_mesh.process(rgb)

    if not results.multi_face_landmarks:
        print("No face detected")
        exit()

    face = results.multi_face_landmarks[0]

    # =========================
    # Lip landmarks
    # =========================

    left = face.landmark[61]
    right = face.landmark[291]
    
    left_eye = face.landmark[33]
    right_eye = face.landmark[263]

    upper = face.landmark[13]
    lower = face.landmark[14]

    upper_left = face.landmark[78]
    upper_right = face.landmark[308]
    lower_left = face.landmark[88]
    lower_right = face.landmark[318]

    # =========================
    # Convert to pixels (IMPORTANT)
    # =========================
    left_pt = (int(left.x*w), int(left.y*h))
    right_pt = (int(right.x*w), int(right.y*h))
    
    left_eye_pt = (
    int(left_eye.x * w),
    int(left_eye.y * h)
    )

    right_eye_pt = (
        int(right_eye.x * w),
        int(right_eye.y * h)
    )

    upper_mid = (int(upper.x*w), int(upper.y*h))
    lower_mid = (int(lower.x*w), int(lower.y*h))

    # =========================
    # FEATURES
    # =========================

    # lip score (stable core feature)
    lip_width = distance(left_pt, right_pt) / w
    lip_height = distance(upper_mid, lower_mid) / h

    corner_height_diff = (
        abs(upper_left.y - lower_left.y) +
        abs(upper_right.y - lower_right.y)
    ) / 2

    lip_score = (lip_height + corner_height_diff) / (lip_width + 1e-6)

    # =========================
    # Symmetry (FIXED properly)
    # =========================
    symmetry = abs(
        (upper_left.y - lower_left.y) -
        (upper_right.y - lower_right.y)
    )

    # =========================
    # Balance (Upper vs Lower Lip)
    # =========================

    upper_outer = face.landmark[0]
    lower_outer = face.landmark[17]

    upper_outer_pt = (
        int(upper_outer.x * w),
        int(upper_outer.y * h)
    )

    lower_outer_pt = (
        int(lower_outer.x * w),
        int(lower_outer.y * h)
    )

    upper_thickness = distance(
        upper_outer_pt,
        upper_mid
    )

    lower_thickness = distance(
        lower_outer_pt,
        lower_mid
    )

    balance_ratio = upper_thickness / (
        upper_thickness + lower_thickness + 1e-6
    )
    
    mouth_width = distance(
    left_pt,
    right_pt
    )

    eye_distance = distance(
        left_eye_pt,
        right_eye_pt
    )

    mouth_width_ratio = mouth_width / (
        eye_distance + 1e-6
    )

    print("Upper Thickness:", upper_thickness)
    print("Lower Thickness:", lower_thickness)

    # =========================
    # FINAL LIP RATIO (keep stable model)
    # =========================
    lip_ratio = lip_score

    # =========================
    # RESULT
    # =========================
    result = classify_lips(
        lip_ratio,
        symmetry,
        balance_ratio,
        mouth_width_ratio
    )
    print("\n===== FEATURES =====")
    print("Lip Score:", lip_score)
    print("Lip Ratio:", lip_ratio)
    print("Symmetry:", symmetry)
    print("Balance Ratio:", balance_ratio)
    print("Mouth Width Ratio:", mouth_width_ratio)

    print("\n===== RESULT =====")
    print(result)