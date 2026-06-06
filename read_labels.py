import pandas as pd

attr_file = "dataset/celeba/list_attr_celeba.csv"

df = pd.read_csv(attr_file)

brow_labels = df[
    [
        "image_id",
        "Bushy_Eyebrows",
        "Arched_Eyebrows"
    ]
]

print(brow_labels.head())

print("\nNumber of photos:")
print(len(brow_labels))