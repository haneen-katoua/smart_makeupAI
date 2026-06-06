import pandas as pd

# Labels
labels = pd.read_csv(
    "dataset/celeba/list_attr_celeba.csv"
)

# Features
features = pd.read_csv(
    "features.csv"
)

# توحيد الاسم
labels = labels.rename(
    columns={
        "image_id": "image"
    }
)

# دمج
merged = pd.merge(
    features,
    labels[
        [
            "image",
            "Bushy_Eyebrows",
            "Arched_Eyebrows"
        ]
    ],
    on="image"
)

print(merged.head())

print("\nRows:")
print(len(merged))
print(merged.describe())

# حفظ
merged.to_csv(
    "training_data.csv",
    index=False
)

print("\nSaved training_data.csv")