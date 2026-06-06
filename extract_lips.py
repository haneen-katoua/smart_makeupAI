import cv2
import mediapipe as mp
import pandas as pd
import os
import random
import math

# =========================
# Distance
# =========================
def distance(p1, p2):
    return math.sqrt(
        (p1[0]-p2[0])**2 +
        (p1[1]-p2[1])**2
    )

# =========================
# Dataset path
# =========================
dataset_path = r"dataset/celeba/img_align_celeba/img_align_celeba"

all_images = [
    f for f in os.listdir(dataset_path)
    if f.lower().endswith(".jpg")
]

print("Total images:", len(all_images))

# =========================
# Sample size
# =========================
sample_size = 1000

images = random.sample(
    all_images,
    min(sample_size, len(all_images))
)

# =========================
# FaceMesh
# =========================
mp_face_mesh = mp.solutions.face_mesh

results_list = []

with mp_face_mesh.FaceMesh(
    static_image_mode=True,
    max_num_faces=1,
    refine_landmarks=True
) as face_mesh:

    for i, image_name in enumerate(images):

        image_path = os.path.join(
            dataset_path,
            image_name
        )

        image = cv2.imread(image_path)

        if image is None:
            continue

        h, w, _ = image.shape

        rgb = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2RGB
        )

        result = face_mesh.process(rgb)

        if not result.multi_face_landmarks:
            continue

        face = result.multi_face_landmarks[0]

        try:

            mouth_left = face.landmark[61]
            mouth_right = face.landmark[291]

            left_eye = face.landmark[33]
            right_eye = face.landmark[263]

            mouth_left_pt = (
                int(mouth_left.x * w),
                int(mouth_left.y * h)
            )

            mouth_right_pt = (
                int(mouth_right.x * w),
                int(mouth_right.y * h)
            )

            left_eye_pt = (
                int(left_eye.x * w),
                int(left_eye.y * h)
            )

            right_eye_pt = (
                int(right_eye.x * w),
                int(right_eye.y * h)
            )

            mouth_width = distance(
                mouth_left_pt,
                mouth_right_pt
            )

            eye_distance = distance(
                left_eye_pt,
                right_eye_pt
            )

            mouth_width_ratio = (
                mouth_width /
                (eye_distance + 1e-6)
            )

            results_list.append({
                "image": image_name,
                "mouth_width_ratio": mouth_width_ratio
            })

        except:
            continue

        if i % 100 == 0:
            print(f"Processed {i}")

# =========================
# Save CSV
# =========================
df = pd.DataFrame(results_list)

df.to_csv(
    "mouth_width_stats.csv",
    index=False
)

print("\nSaved mouth_width_stats.csv")

# =========================
# Statistics
# =========================
print("\n===== STATISTICS =====")

print(df["mouth_width_ratio"].describe())

print("\nQ1:")
print(df["mouth_width_ratio"].quantile(0.25))

print("\nMedian:")
print(df["mouth_width_ratio"].quantile(0.50))

print("\nQ3:")
print(df["mouth_width_ratio"].quantile(0.75))