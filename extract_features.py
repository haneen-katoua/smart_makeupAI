import cv2
import mediapipe as mp
import pandas as pd
import os
import math
import random

# =========================
# Distance
# =========================
def distance(p1, p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

# =========================
# FaceMesh
# =========================
mp_face_mesh = mp.solutions.face_mesh

# نقاط أقوى شوي للحاجب (أكثر من نقطة)
BROW_POINTS = [70, 63, 105, 66, 107, 55, 52]

EYE = {
    "left": 33,
    "right": 133
}

images_folder = "dataset/celeba/img_align_celeba/img_align_celeba"

all_images = os.listdir(images_folder)

images = random.sample(all_images, 1000)

features = []

with mp_face_mesh.FaceMesh(
    static_image_mode=True,
    max_num_faces=1,
    refine_landmarks=True
) as face_mesh:

    for img_name in images:

        img_path = os.path.join(images_folder, img_name)
        img = cv2.imread(img_path)

        if img is None:
            continue

        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb)

        if not results.multi_face_landmarks:
            continue

        face = results.multi_face_landmarks[0]
        h, w, _ = img.shape

        # =========================
        # Eye width (Normalization)
        # =========================
        l = face.landmark[EYE["left"]]
        r = face.landmark[EYE["right"]]

        eye_width = distance(
            (int(l.x*w), int(l.y*h)),
            (int(r.x*w), int(r.y*h))
        )

        if eye_width == 0:
            continue

        brow_y = []

        brow_points = []

        for idx in BROW_POINTS:
            lm = face.landmark[idx]
            x = int(lm.x * w)
            y = int(lm.y * h)
            brow_points.append((x, y))
            brow_y.append(y)

        # =========================
        # Thickness (average vertical spread)
        # =========================
        thickness = (max(brow_y) - min(brow_y)) / eye_width

        # =========================
        # Width (horizontal spread)
        # =========================
        width = distance(
            brow_points[0],
            brow_points[-1]
        ) / eye_width

        # =========================
        # Arch (middle vs sides)
        # =========================
        middle_y = brow_points[len(brow_points)//2][1]
        avg_side_y = (brow_points[0][1] + brow_points[-1][1]) / 2

        arch = (avg_side_y - middle_y) / eye_width

        # =========================
        # Symmetry
        # =========================
        symmetry = abs(brow_points[0][1] - brow_points[-1][1]) / eye_width

        features.append([
            img_name,
            thickness,
            width,
            arch,
            symmetry
        ])

df = pd.DataFrame(features, columns=[
    "image",
    "thickness",
    "width",
    "arch",
    "symmetry"
])

df.to_csv("features.csv", index=False)

print(df.head())
print("\nSaved features.csv")