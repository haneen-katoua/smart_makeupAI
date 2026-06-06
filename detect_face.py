import cv2
import mediapipe as mp
import pandas as pd
import os
import random
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
# Dataset path
# ====================================
dataset_path = r"dataset/celeba/img_align_celeba/img_align_celeba"

all_images = [
    f for f in os.listdir(dataset_path)
    if f.lower().endswith(".jpg")
]

print("Total images:", len(all_images))

# ====================================
# Sample size
# ====================================
sample_size = 1000

images = random.sample(
    all_images,
    min(sample_size, len(all_images))
)

# ====================================
# FaceMesh
# ====================================
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

            results_list.append({
                "image": image_name,
                "face_length": face_length,
                "face_width": face_width,
                "jaw_width": jaw_width,
                "cheek_width": cheek_width,
                "length_width_ratio": length_width_ratio,
                "jaw_face_ratio": jaw_face_ratio,
                "cheek_face_ratio": cheek_face_ratio,

            })

        except:
            continue

        if i % 100 == 0:
            print(f"Processed {i}")

# ====================================
# Save CSV
# ====================================

df = pd.DataFrame(results_list)

df.to_csv(
    "face_shape_stats.csv",
    index=False
)

print("\nSaved face_shape_stats.csv")

# ====================================
# Statistics
# ====================================

print("\n===== LENGTH/WIDTH =====")
print(df["length_width_ratio"].describe())

print("\nQ1")
print(df["length_width_ratio"].quantile(0.25))

print("\nMedian")
print(df["length_width_ratio"].quantile(0.50))

print("\nQ3")
print(df["length_width_ratio"].quantile(0.75))

print("\n===== JAW/FACE =====")
print(df["jaw_face_ratio"].describe())

print("\nQ1")
print(df["jaw_face_ratio"].quantile(0.25))

print("\nMedian")
print(df["jaw_face_ratio"].quantile(0.50))

print("\nQ3")
print(df["jaw_face_ratio"].quantile(0.75))

print("\n===== CHEEK/FACE =====")

print(
    df["cheek_face_ratio"].describe()
)

print("\nQ1")
print(
    df["cheek_face_ratio"].quantile(0.25)
)

print("\nMedian")
print(
    df["cheek_face_ratio"].quantile(0.50)
)

print("\nQ3")
print(
    df["cheek_face_ratio"].quantile(0.75)
)