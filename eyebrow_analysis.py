import cv2
import mediapipe as mp
import math

# =========================
# Distance
# =========================
def distance(p1, p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

# =========================
# Rule-based classifier
# =========================
def classify_brows(thickness, arch, symmetry):

    result = []

    # Thickness
    if thickness > 0.42:
        result.append("Thick Brows")
    else:
        result.append("Thin Brows")

    # Arch
    if arch > 0.18:
        result.append("Arched Brows")
    else:
        result.append("Straight Brows")

    # Symmetry
    if symmetry > 0.10:
        result.append("Asymmetrical Brows")
    else:
        result.append("Symmetrical Brows")

    return ", ".join(result)

# =========================
# Load image
# =========================
image_path = "pictures2/photo_2026-06-04_11-20-07.jpg"   # <-- غيّري اسم الصورة هون

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
    # Eye reference (for normalization)
    # =========================
    left_eye = face.landmark[33]
    right_eye = face.landmark[133]

    eye_width = distance(
        (int(left_eye.x*w), int(left_eye.y*h)),
        (int(right_eye.x*w), int(right_eye.y*h))
    )

    # =========================
    # Brow points (simple set)
    # =========================
    brow_idx = [70, 63, 105, 66, 107, 55, 52]

    brow_points = []
    brow_y = []

    for idx in brow_idx:
        lm = face.landmark[idx]
        x = int(lm.x * w)
        y = int(lm.y * h)
        brow_points.append((x, y))
        brow_y.append(y)

    # =========================
    # Features
    # =========================

    thickness = (max(brow_y) - min(brow_y)) / eye_width

    width = distance(brow_points[0], brow_points[-1]) / eye_width

    middle_y = brow_points[len(brow_points)//2][1]
    avg_side_y = (brow_points[0][1] + brow_points[-1][1]) / 2

    arch = (avg_side_y - middle_y) / eye_width

    symmetry = abs(brow_points[0][1] - brow_points[-1][1]) / eye_width

    # =========================
    # Classification
    # =========================
    result = classify_brows(thickness, arch, symmetry)

    # =========================
    # Output
    # =========================
    print("\n===== FEATURES =====")
    print("Thickness:", thickness)
    print("Arch:", arch)
    print("Symmetry:", symmetry)

    print("\n===== RESULT =====")
    print(result)