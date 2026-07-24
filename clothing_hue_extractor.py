import cv2
import numpy as np
from sklearn.cluster import KMeans
import rembg
import os
import matplotlib.pyplot as plt

# ==========================================================
# 1) إزالة الخلفية (Masking)
# ==========================================================
def remove_background(img):
    result = rembg.remove(img)
    if result.shape[2] == 4:
        result = cv2.cvtColor(result, cv2.COLOR_BGRA2BGR)
    return result

# ==========================================================
# 2) White Balance خفيف للملابس فقط
# ==========================================================
def soft_white_balance(img):
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    L, A, B = cv2.split(lab)
    # خففنا التصحيح حتى لا يبرد اللون
    balanced = cv2.merge((L, A, B))
    return cv2.cvtColor(balanced, cv2.COLOR_LAB2BGR)

# ==========================================================
# 3) فلترة الظلال واللمعات
# ==========================================================
def filter_pixels(pixels):
    if len(pixels) == 0:
        return pixels
    lab = cv2.cvtColor(pixels.reshape(-1,1,3), cv2.COLOR_BGR2LAB).reshape(-1,3)
    L = lab[:,0]
    # سمحنا بنطاق أوسع حتى لا نحذف البكسلات الفاتحة
    mask = (L > 10) & (L < 250)
    return pixels[mask]

# ==========================================================
# 4) اكتشاف الألوان المحايدة
def is_neutral_color(bgr):
    b, g, r = bgr

    # أسود حقيقي فقط
    if b < 25 and g < 25 and r < 25:
        return True

    # أبيض حقيقي فقط
    if b > 245 and g > 245 and r > 245:
        return True

    # غير ذلك → لون قابل للاكتشاف
    return False



# ==========================================================
# 5) استخراج اللون المهيمن
# ==========================================================
def extract_dominant_color(img, k=5):
    pixels = img.reshape(-1, 3)
    pixels = filter_pixels(pixels)
    if len(pixels) < k:
        return None
    # kmeans = KMeans(n_clusters=k, random_state=0).fit(pixels)
    # labels, counts = np.unique(kmeans.labels_, return_counts=True)
    # داخل extract_dominant_color
    # kmeans = KMeans(n_clusters=k, random_state=0).fit(pixels)
    # labels, counts = np.unique(kmeans.labels_, return_counts=True)

    # # خذي المتوسط بين أكبر عنقودين بدل واحد فقط
    # top_two = np.argsort(counts)[-2:]
    # dominant = np.mean(kmeans.cluster_centers_[top_two], axis=0)

    # dominant = kmeans.cluster_centers_[np.argmax(counts)]
    # print("Cluster centers:", kmeans.cluster_centers_)  # لمراقبة الألوان المكتشفة
    # return dominant
    # داخل extract_dominant_color
    # kmeans = KMeans(n_clusters=k, random_state=0).fit(pixels)
    # labels, counts = np.unique(kmeans.labels_, return_counts=True)

    # # خذي المتوسط بين أكبر عنقودين بدل واحد فقط
    # top_two = np.argsort(counts)[-2:]
    # dominant = np.mean(kmeans.cluster_centers_[top_two], axis=0)
    # داخل extract_dominant_color
    kmeans = KMeans(n_clusters=k, random_state=0).fit(pixels)
    labels, counts = np.unique(kmeans.labels_, return_counts=True)

    # خذي المتوسط بين أكبر عنقودين، لكن مع ترجيح للأفتح
    top_two = np.argsort(counts)[-2:]
    dominant = np.mean(kmeans.cluster_centers_[top_two], axis=0)

    # إذا اللون غامق جداً، افتحيه قليلاً
    # dominant = np.clip(dominant * 1.15, 0, 255)
    dominant = np.clip(dominant * 1.05, 0, 255)


    print("Cluster centers:", kmeans.cluster_centers_)  # لمراقبة الألوان المكتشفة
    return dominant


# ==========================================================
# 6) تحويل اللون إلى Hue
# ==========================================================
def bgr_to_hue(bgr):
    hsv = cv2.cvtColor(np.uint8([[bgr]]), cv2.COLOR_BGR2HSV)[0][0]
    return int(hsv[0])

# ==========================================================
# 7) Rule C4 – Earth Tone Compensation
# ==========================================================
def apply_rule_c4():
    return {
        
        "Input_Hue": None
    }

# ==========================================================
# 8) الدالة الأساسية
# ==========================================================
def analyze_clothing_color(image_path):
    if not os.path.exists(image_path):
        return {"error": "Image not found"}
    img = cv2.imread(image_path)
    if img is None:
        return {"error": "Image not found"}
    no_bg = remove_background(img)
    corrected = soft_white_balance(no_bg)
    dominant = extract_dominant_color(corrected)
    if dominant is None:
        return {"error": "Could not extract dominant color"}
    if is_neutral_color(dominant):
        return apply_rule_c4()
    hue = bgr_to_hue(dominant)
    return {
        "status": "Color extracted",
        "dominant_bgr": [int(c) for c in dominant],
        "Input_Hue": hue,
        "hex": f"#{int(dominant[2]):02x}{int(dominant[1]):02x}{int(dominant[0]):02x}"
    }

# ==========================================================
# 9) تجربة الكود + عرض اللون عبر matplotlib
# ==========================================================
if __name__ == "__main__":
    result = analyze_clothing_color("pictures4/photo_2026-07-14_09-05-54.jpg")
    print(result)

    if result.get("status") == "Color extracted":
        bgr = np.array(result["dominant_bgr"], dtype=np.uint8)
        rgb = bgr[::-1]  # تحويل BGR → RGB
        plt.figure(figsize=(3,3))
        plt.imshow(np.ones((100,100,3), dtype=np.uint8) * rgb)
        plt.title(f"Dominant Color (Hue={result['Input_Hue']})")
        plt.axis('off')
        plt.show()
