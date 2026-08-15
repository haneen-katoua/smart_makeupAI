# -*- coding: utf-8 -*-

import os
import json
import cv2
import numpy as np
import mediapipe as mp
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

REAL_BROW_SWATCHES = {
    "Blonde-Warm": "#A67B5B",
    "Blonde-Cool": "#8C7A6B",
    "Auburn-Warm": "#7A4332",
    "SoftBrown-Warm": "#5C4033",
    "SoftBrown-Cool": "#4A3B32",
    "MediumBrown-Warm": "#423127",
    "MediumBrown-Cool": "#362D27",
    "DarkBrown-Warm": "#2C1D18",
    "DarkBrown-Cool": "#211C19",
    "Ebony-Cool": "#191716",
    "Taupe-Cool": "#6B625B",
    "Ash-Cool": "#4F4B47",
}


def parse_color(text_or_hex, default_bgr=(25, 28, 35)):
    if not text_or_hex:
        return default_bgr
    if isinstance(text_or_hex, str) and text_or_hex.startswith("#"):
        hex_str = text_or_hex.lstrip("#")
        rgb = tuple(int(hex_str[i : i + 2], 16) for i in (0, 2, 4))
        return (rgb[2], rgb[1], rgb[0])
    return default_bgr


_KB_SWATCH_MAP = {
    ("warm", "fair"): "Auburn-Warm",
    ("warm", "medium"): "MediumBrown-Warm",
    ("warm", "dark"): "DarkBrown-Warm",
    ("cool", "fair"): "Taupe-Cool",
    ("cool", "medium"): "Ash-Cool",
    ("cool", "dark"): "DarkBrown-Cool",
}


def map_kb_color_to_swatch(color_info, fallback_undertone="warm", fallback_depth="medium"):
    if not color_info or not isinstance(color_info, dict):
        swatch_name = _KB_SWATCH_MAP.get((fallback_undertone, fallback_depth), "MediumBrown-Warm")
        return swatch_name, parse_color(REAL_BROW_SWATCHES[swatch_name])
    
    palette = color_info.get("palette", "") or ""
    tone = color_info.get("tone", "") or ""
    
    undertone = "warm" if "دافئ" in palette else ("cool" if "بارد" in palette else fallback_undertone)
    
    if "داكن" in tone or "غني" in tone:
        depth = "dark"
    elif "فاتح" in tone:
        depth = "fair"
    else:
        depth = fallback_depth

    swatch_name = _KB_SWATCH_MAP.get((undertone, depth), "MediumBrown-Warm")
    return swatch_name, parse_color(REAL_BROW_SWATCHES[swatch_name])


def map_color_intensity_to_strength(color_intensity):
    if not color_intensity:
        return 0.28

    ci = str(color_intensity)

    if "طبيعي إلى قوي" in ci:
        return 0.30
    if "قوي" in ci:
        return 0.35
    if "شفاف" in ci:
        return 0.12
    if "طبيعي" in ci:
        return 0.22

    return 0.28

VALID_BROW_SHAPES = {
    "Round",
    "Square",
    "Oval",
    "Heart",
    "Rectangular",
    "Triangle",
    "Diamond",
}

VALID_OCCASIONS = {
    "work",
    "university",
    "evening",
    "party",
    "photo",
    "wedding",
}


def normalize_brow_shape(shape):
    if not shape:
        return "Oval"

    shape = str(shape).strip()

    if shape in VALID_BROW_SHAPES:
        return shape

    print(f" Face shape غير معروف: {shape} → Oval")
    return "Oval"


def normalize_brow_occasion(occasion):
    if not occasion:
        return "work"

    occasion = str(occasion).strip().lower()

    if occasion in VALID_OCCASIONS:
        return occasion

    print(f" Occasion غير معروف: {occasion} → work")
    return "work"

BROW_RIGHT_FULL = [70, 63, 105, 66, 107, 55, 65, 52, 53, 46]
BROW_LEFT_FULL = [300, 293, 334, 296, 336, 285, 295, 282, 283, 276]

EYE_RIGHT_LOCK = [33, 160, 158, 157, 173, 133, 155, 154, 153, 145, 144, 163]
EYE_LEFT_LOCK = [263, 387, 385, 384, 398, 362, 382, 381, 380, 374, 373, 390]


def warp_triangle(img1, img2, tri1, tri2):
    r1 = cv2.boundingRect(np.float32([tri1]))
    r2 = cv2.boundingRect(np.float32([tri2]))

    if r1[2] <= 0 or r1[3] <= 0 or r2[2] <= 0 or r2[3] <= 0:
        return

    tri1_cropped = []
    tri2_cropped = []

    for i in range(0, 3):
        tri1_cropped.append(((tri1[i][0] - r1[0]), (tri1[i][1] - r1[1])))
        tri2_cropped.append(((tri2[i][0] - r2[0]), (tri2[i][1] - r2[1])))

    img1_cropped = img1[r1[1] : r1[1] + r1[3], r1[0] : r1[0] + r1[2]]

    M = cv2.getAffineTransform(np.float32(tri1_cropped), np.float32(tri2_cropped))

    img2_cropped = cv2.warpAffine(
        img1_cropped, M, (r2[2], r2[3]), None,
        flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101,
    )

    mask = np.zeros((r2[3], r2[2], 3), dtype=np.float32)
    cv2.fillConvexPoly(mask, np.int32(tri2_cropped), (1.0, 1.0, 1.0), 16, 0)

    img2_cropped = img2_cropped * mask
    img2[r2[1] : r2[1] + r2[3], r2[0] : r2[0] + r2[2]] = (
        img2[r2[1] : r2[1] + r2[3], r2[0] : r2[0] + r2[2]] * ((1.0, 1.0, 1.0) - mask)
    )
    region = img2[r2[1] : r2[1] + r2[3], r2[0] : r2[0] + r2[2]].astype(np.float32)
    region += img2_cropped
    img2[r2[1] : r2[1] + r2[3], r2[0] : r2[0] + r2[2]] = np.clip(region, 0, 255).astype(np.uint8)


def morph_eyebrow_texture_safe(image, orig_pts, new_pts, eye_lock_pts, face_scale):
    h, w, _ = image.shape
    warped_img = image.copy()

    all_pts = np.vstack([orig_pts, new_pts, eye_lock_pts])
    x, y, bw, bh = cv2.boundingRect(np.int32(all_pts))
    pad = int(face_scale * 0.12)

    x1, y1 = max(0, x - pad), max(0, y - pad)
    x2, y2 = min(w, x + bw + pad), min(h, y + bh + pad)

    rect = (x1, y1, x2 - x1, y2 - y1)

    anchors = np.array(
        [[x1, y1], [x2 - 1, y1], [x1, y2 - 1], [x2 - 1, y2 - 1]], dtype=np.float32
    )

    src_all = np.vstack([orig_pts, eye_lock_pts, anchors])
    dst_all = np.vstack([new_pts, eye_lock_pts, anchors])

    subdiv = cv2.Subdiv2D(rect)
    for p in dst_all:
        subdiv.insert((float(p[0]), float(p[1])))

    triangle_list = subdiv.getTriangleList()

    for t in triangle_list:
        pt_dst = [(t[0], t[1]), (t[2], t[3]), (t[4], t[5])]

        in_bounds = True
        for p in pt_dst:
            if not (x1 <= p[0] < x2 and y1 <= p[1] < y2):
                in_bounds = False
                break
        if not in_bounds:
            continue

        idx = []
        for p in pt_dst:
            dists = np.linalg.norm(dst_all - p, axis=1)
            idx.append(np.argmin(dists))

        if len(idx) == 3:
            pt_src = [src_all[idx[0]], src_all[idx[1]], src_all[idx[2]]]
            warp_triangle(image, warped_img, pt_src, pt_dst)

    return warped_img


OCCASION_INTENSITY = {
    "work":       {"lift":  0.000, "tail": 0.000},
    "university": {"lift":  0.000, "tail": 0.000},
    "evening":    {"lift": -0.006, "tail": 0.006},
    "party":      {"lift": -0.008, "tail": 0.008},
    "photo":      {"lift": -0.010, "tail": 0.010},
    "wedding":    {"lift": -0.012, "tail": 0.012},
}


def transform_brow_shape(landmarks, landmark_indices, w, h, face_scale, shape_type, occasion):
    orig_pts = np.array(
        [[landmarks[i].x * w, landmarks[i].y * h] for i in landmark_indices],
        dtype=np.float32,
    )

    n = len(orig_pts)
    half = n // 2 

    x_half = np.linspace(-1.8, 1.8, half)

    arch_sharp = np.exp(-(x_half ** 2) * 1.2)
    arch_soft  = np.exp(-(x_half ** 2) * 0.7)
    arch_flat  = np.ones(half) * 0.4

    tail_ramp_upper = np.linspace(0, 1, half)
    tail_ramp_lower = np.linspace(1, 0, half)
    tail_ramp = np.concatenate([tail_ramp_upper, tail_ramp_lower])

    shift_y = np.zeros(n, dtype=np.float32)
    shift_x = np.zeros(n, dtype=np.float32)

    is_right = landmark_indices[0] < 200
    tail_dir = 1.0 if is_right else -1.0

    if shape_type == "Round":
        w_arch = np.concatenate([arch_sharp, arch_sharp])
        shift_y -= w_arch * (face_scale * 0.022)

    elif shape_type == "Square":
        w_arch = np.concatenate([arch_soft, arch_soft])
        shift_y -= w_arch * (face_scale * 0.016)
        shift_y[-2:] += face_scale * 0.004

    elif shape_type == "Oval":
        w_arch = np.concatenate([arch_soft, arch_soft])
        shift_y -= w_arch * (face_scale * 0.012)

    elif shape_type == "Heart":
        w_arch = np.concatenate([arch_soft, arch_soft])
        shift_y += w_arch * (face_scale * 0.005)

    elif shape_type == "Rectangular":
        w_arch = np.concatenate([arch_flat, arch_flat])
        shift_y += w_arch * (face_scale * 0.010)
        shift_x += tail_dir * face_scale * 0.015 * tail_ramp

    elif shape_type == "Triangle":
        w_arch = np.concatenate([arch_soft, arch_soft])
        shift_y -= w_arch * (face_scale * 0.011)
        shift_x += tail_dir * face_scale * 0.012 * tail_ramp

    elif shape_type == "Diamond":
        w_arch = np.concatenate([arch_soft, arch_soft])
        shift_y -= w_arch * (face_scale * 0.014)

    intensity = OCCASION_INTENSITY.get(occasion, OCCASION_INTENSITY["work"])
    shift_y += intensity["lift"] * face_scale
    shift_x += tail_dir * intensity["tail"] * face_scale * tail_ramp

    MAX_SHIFT_Y_RATIO = 0.030
    MAX_SHIFT_X_RATIO = 0.020
    shift_y = np.clip(shift_y, -face_scale * MAX_SHIFT_Y_RATIO, face_scale * MAX_SHIFT_Y_RATIO)
    shift_x = np.clip(shift_x, -face_scale * MAX_SHIFT_X_RATIO, face_scale * MAX_SHIFT_X_RATIO)

    new_pts = orig_pts.copy()
    new_pts[:, 0] += shift_x
    new_pts[:, 1] += shift_y

    return orig_pts, new_pts


def apply_brow_color_tint(image, pts, color_bgr, face_scale, strength=0.28):
    if color_bgr is None:
        return image

    h, w, _ = image.shape
    pts_int = np.array(pts, dtype=np.int32)

    mask = np.zeros((h, w), dtype=np.float32)
    cv2.fillPoly(mask, [pts_int], 1.0)

    blur_k = max(7, min(int(face_scale * 0.030), 21)) | 1
    soft_mask = cv2.GaussianBlur(mask, (blur_k, blur_k), 0)[:, :, np.newaxis]

    color_layer = np.full_like(image, color_bgr, dtype=np.float32)
    img_float = image.astype(np.float32)

    strength = min(strength, 0.32)

    tinted = img_float * (1 - soft_mask * strength) + color_layer * (soft_mask * strength)
    return np.clip(tinted, 0, 255).astype(np.uint8)


def render_brow_engine_v13_2(image, landmarks, face_scale, shape_type="Oval", occasion="work",
                             override_bgr=None, tint_strength=0.28):
    h, w, _ = image.shape
    out_img = image.copy()

    brow_pairs = [
        (BROW_RIGHT_FULL, EYE_RIGHT_LOCK),
        (BROW_LEFT_FULL, EYE_LEFT_LOCK),
    ]

    for brow_indices, eye_lock_indices in brow_pairs:
        orig_pts, new_pts = transform_brow_shape(
            landmarks, brow_indices, w, h, face_scale, shape_type, occasion
        )

        eye_lock_pts = np.array(
            [[landmarks[i].x * w, landmarks[i].y * h] for i in eye_lock_indices],
            dtype=np.float32,
        )

        out_img = morph_eyebrow_texture_safe(out_img, orig_pts, new_pts, eye_lock_pts, face_scale)

        if override_bgr is not None:
            out_img = apply_brow_color_tint(
                out_img, new_pts, override_bgr, face_scale, strength=tint_strength
            )

    return out_img


def render_brow_swatches_palette(swatches_dict, cols=6, tile_size=45):
    keys = list(swatches_dict.keys())
    rows = (len(keys) + cols - 1) // cols
    pad = 6
    img_h = rows * (tile_size + pad) + pad
    img_w = cols * (tile_size + pad) + pad

    palette_img = np.zeros((img_h, img_w, 3), dtype=np.uint8) + 240
    clickable_regions = []

    for idx, (shade_name, hex_code) in enumerate(swatches_dict.items()):
        r, c = idx // cols, idx % cols
        x1, y1 = pad + c * (tile_size + pad), pad + r * (tile_size + pad)
        x2, y2 = x1 + tile_size, y1 + tile_size

        bgr = parse_color(hex_code)
        cv2.rectangle(palette_img, (x1, y1), (x2, y2), bgr, -1)
        cv2.rectangle(palette_img, (x1, y1), (x2, y2), (180, 180, 180), 1)
        cv2.putText(
            palette_img, shade_name[:8], (x1 + 2, y1 + tile_size - 6),
            cv2.FONT_HERSHEY_SIMPLEX, 0.28, (255, 255, 255), 1, cv2.LINE_AA
        )
        clickable_regions.append({"name": shade_name, "bgr": bgr, "rect": (x1, y1, x2, y2)})

    return palette_img, clickable_regions


def launch_brow_wheel_engine(image, landmarks, experta_results, face_scale):

    recommendation = experta_results.get("recommendation") or {}
    color_info = experta_results.get("color") or {}
    style_info = experta_results.get("style") or {}

    shape_type = normalize_brow_shape(
        recommendation.get("face_shape")
    )

    occasion_real = normalize_brow_occasion(
        recommendation.get("occasion")
    )

    kb_swatch_name, kb_default_bgr = map_kb_color_to_swatch(
        color_info
    )

    kb_color_intensity = style_info.get(
        "color_intensity",
        "طبيعي"
    )

    kb_strength = map_color_intensity_to_strength(
        kb_color_intensity
    )

    palette_img, clickable_regions = render_brow_swatches_palette(REAL_BROW_SWATCHES)

    current_shade_bgr = kb_default_bgr
    current_strength = kb_strength

    _ALL_SHAPES_ORDER = ["Round", "Square", "Oval", "Heart", "Rectangular", "Triangle", "Diamond"]
    compare_shapes = [s for s in _ALL_SHAPES_ORDER if s != shape_type][:2]

    strategies = [
        ("0. Original Image", None, None),
        (f"1. Recommended ({shape_type}/{occasion_real})", shape_type, occasion_real),
        (f"2. Shape: {compare_shapes[0]}", compare_shapes[0], occasion_real),
        (f"3. Shape: {compare_shapes[1]}", compare_shapes[1], occasion_real),
        (f"4. Occasion: work", shape_type, "work"),
        (f"5. Occasion: wedding", shape_type, "wedding"),
    ]

    def generate_grid_images(bgr_color, strength):
        grid_imgs = []
        for title, s_type, occ in strategies:
            if s_type is None:
                res_img = image.copy()
            else:
                res_img = render_brow_engine_v13_2(
                    image.copy(), landmarks, face_scale,
                    shape_type=s_type, occasion=occ,
                    override_bgr=bgr_color, tint_strength=strength
                )
            cv2.rectangle(res_img, (0, 0), (res_img.shape[1], 35), (0, 0, 0), -1)
            cv2.putText(
                res_img, title, (15, 23),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 180), 2, cv2.LINE_AA
            )
            grid_imgs.append(cv2.cvtColor(res_img, cv2.COLOR_BGR2RGB))

        return np.vstack([np.hstack(grid_imgs[:3]), np.hstack(grid_imgs[3:])])

    fig = plt.figure(figsize=(15, 10))
    fig.canvas.manager.set_window_title("Real Hair AR Eyebrow Engine v13.3 (Natural & Realistic)")

    ax_grid = plt.subplot2grid((4, 2), (0, 0), colspan=2, rowspan=3)
    current_grid_img = generate_grid_images(current_shade_bgr, current_strength)
    grid_display = ax_grid.imshow(current_grid_img)

    ax_grid.set_title(
        f"Face: {shape_type} | Occasion: {occasion_real} | KB Color: {kb_swatch_name}",
        fontsize=11, fontweight="bold"
    )
    ax_grid.axis("off")

    ax_palette = plt.subplot2grid((4, 2), (3, 0))
    ax_palette.imshow(cv2.cvtColor(palette_img, cv2.COLOR_BGR2RGB))
    ax_palette.axis("off")

    ax_button = plt.subplot2grid((4, 2), (3, 1))
    ax_button.axis("off")
    btn_save = Button(ax_button, "Save High-Res Grid", color="thistle", hovercolor="violet")

    def save_high_res(event):
        cv2.imwrite("brow_v13_3_output.png", cv2.cvtColor(current_grid_img, cv2.COLOR_RGB2BGR))
        print("تم حفظ النتيجة بنجاح!")

    btn_save.on_clicked(save_high_res)

    def on_palette_click(event):
        nonlocal current_shade_bgr, current_grid_img
        if event.inaxes != ax_palette or event.xdata is None or event.ydata is None:
            return
        px, py = int(round(event.xdata)), int(round(event.ydata))
        for item in clickable_regions:
            x1, y1, x2, y2 = item["rect"]
            if x1 <= px <= x2 and y1 <= py <= y2:
                current_shade_bgr = item["bgr"]
                current_grid_img = generate_grid_images(current_shade_bgr, current_strength)
                grid_display.set_data(current_grid_img)
                fig.canvas.draw_idle()
                break

    fig.canvas.mpl_connect("button_press_event", on_palette_click)
    plt.tight_layout()
    plt.show()



def load_json_results(json_path="makeup_analysis.json"):
    if not os.path.exists(json_path):
        print(f" ملف JSON غير موجود في المسار: {json_path}. سيتم استخدام القيم الافتراضية.")
        return {
            "recommendation": {"face_shape": "Round", "occasion": "wedding"},
            "style": {"color_intensity": "قوي وجريء"},
            "color": {"tone": "بني رمادي (آش براون)", "palette": "أساس بارد"}
        }

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(" تم تحميل بيانات القواعد بنجاح من ملف JSON.")
    return data


if __name__ == "__main__":
    experta_result = load_json_results("makeup_analysis.json")
    image_path = "test2.jpg"
    img = cv2.imread(image_path)

    if img is not None:
        h, w, _ = img.shape
        mp_face_mesh = mp.solutions.face_mesh

        with mp_face_mesh.FaceMesh(
            static_image_mode=True, max_num_faces=1,
            refine_landmarks=True, min_detection_confidence=0.5,
        ) as face_mesh:
            results = face_mesh.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

            if results.multi_face_landmarks:
                face_landmarks = results.multi_face_landmarks[0].landmark
                pt1 = np.array([face_landmarks[234].x * w, face_landmarks[234].y * h])
                pt2 = np.array([face_landmarks[454].x * w, face_landmarks[454].y * h])
                face_scale = np.linalg.norm(pt1 - pt2)
                
                launch_brow_wheel_engine(
                    image=img,
                    landmarks=face_landmarks,
                    experta_results=experta_result,
                    face_scale=face_scale,
                )
            else:
                print(" لم يتم العثور على وجه في الصورة")
    else:
        print(f" تعذر العثور على الصورة: {image_path}")
        