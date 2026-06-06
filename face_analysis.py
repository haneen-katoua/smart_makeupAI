import cv2
import mediapipe as mp
import math

# ====================================
# Distance
# ====================================
def distance(p1, p2):
    return math.sqrt(
        (p1[0] - p2[0])**2 +
        (p1[1] - p2[1])**2
    )

# ====================================
# Face Shape Classification
# ====================================
def classify_face_shape(
    length_width_ratio,
    jaw_face_ratio,
    cheek_face_ratio
):

    # Long face
    if length_width_ratio > 1.25:
        return "Oblong Face"

    # Round face
    elif (
        length_width_ratio < 1.17
        and jaw_face_ratio < 0.81
    ):
        return "Round Face"

    # Square face
    elif (
        jaw_face_ratio > 0.83
        and length_width_ratio < 1.25
    ):
        return "Square Face"

    # Oval face
    else:
        return "Oval Face"

# ====================================
# Load Image
# ====================================
image_path = "pictures2/photo_2026-06-04_11-20-15.jpg"

image = cv2.imread(image_path)

if image is None:
    print("Image not found")
    exit()

h, w, _ = image.shape

rgb = cv2.cvtColor(
    image,
    cv2.COLOR_BGR2RGB
)

# ====================================
# FaceMesh
# ====================================
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

    # ====================================
    # Face Length
    # ====================================

    forehead = face.landmark[10]
    chin = face.landmark[152]

    forehead_pt = (
        int(forehead.x * w),
        int(forehead.y * h)
    )

    chin_pt = (
        int(chin.x * w),
        int(chin.y * h)
    )

    face_length = distance(
        forehead_pt,
        chin_pt
    )

    # ====================================
    # Face Width
    # ====================================

    left_face = face.landmark[234]
    right_face = face.landmark[454]

    left_face_pt = (
        int(left_face.x * w),
        int(left_face.y * h)
    )

    right_face_pt = (
        int(right_face.x * w),
        int(right_face.y * h)
    )

    face_width = distance(
        left_face_pt,
        right_face_pt
    )

    # ====================================
    # Jaw Width
    # ====================================

    jaw_left = face.landmark[172]
    jaw_right = face.landmark[397]

    jaw_left_pt = (
        int(jaw_left.x * w),
        int(jaw_left.y * h)
    )

    jaw_right_pt = (
        int(jaw_right.x * w),
        int(jaw_right.y * h)
    )

    jaw_width = distance(
        jaw_left_pt,
        jaw_right_pt
    )
    
    # ====================================
    # Cheekbone Width
    # ====================================

    left_cheek = face.landmark[93]
    right_cheek = face.landmark[323]

    left_cheek_pt = (
        int(left_cheek.x * w),
        int(left_cheek.y * h)
    )

    right_cheek_pt = (
        int(right_cheek.x * w),
        int(right_cheek.y * h)
    )

    cheek_width = distance(
        left_cheek_pt,
        right_cheek_pt
    )

    # ====================================
    # Ratios
    # ====================================

    length_width_ratio = (
        face_length /
        (face_width + 1e-6)
    )

    jaw_face_ratio = (
        jaw_width /
        (face_width + 1e-6)
    )
    
    cheek_face_ratio = (
    cheek_width /
    (face_width + 1e-6)
    )

    # ====================================
    # Result
    # ====================================

    face_shape = classify_face_shape(
    length_width_ratio,
    jaw_face_ratio,
    cheek_face_ratio
    )

    # ====================================
    # Print
    # ====================================

    print("\n===== FEATURES =====")

    print(
        "Face Length:",
        round(face_length, 2)
    )

    print(
        "Face Width:",
        round(face_width, 2)
    )

    print(
        "Jaw Width:",
        round(jaw_width, 2)
    )

    print(
        "Length/Width Ratio:",
        round(length_width_ratio, 3)
    )

    print(
        "Jaw/Face Ratio:",
        round(jaw_face_ratio, 3)
    )
    
    print(
    "Cheek/Face Ratio:",
    round(cheek_face_ratio, 3)
    )

    print("\n===== RESULT =====")

    print(face_shape)