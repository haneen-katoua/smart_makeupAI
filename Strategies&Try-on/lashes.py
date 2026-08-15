# -*- coding: utf-8 -*-

import json
import os
import sys
import cv2
import matplotlib.pyplot as plt
import mediapipe as mp
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from eye_makeup_rules import EyeMakeupEngine

try:
    import collections
    import collections.abc

    for item in [
        "MutableMapping",
        "MutableSequence",
        "MutableSet",
        "Mapping",
        "Sequence",
        "Set",
    ]:
        if not hasattr(collections, item) and hasattr(collections.abc, item):
            setattr(collections, item, getattr(collections.abc, item))
except Exception:
    pass


LEFT_EYE_PTS = {
    "inner": 362,
    "outer": 263,
    "top": 386,
    "bottom": 374,
    "curve": [362, 398, 384, 385, 386, 387, 388, 466, 263],
}
RIGHT_EYE_PTS = {
    "inner": 133,
    "outer": 33,
    "top": 159,
    "bottom": 145,
    "curve": [33, 246, 161, 160, 159, 158, 157, 173, 133],
}

LASH_HEIGHT_FACTORS = {
    "Natural_Everyday": 0.18,
    "Cat_Eye_Outer_Volume": 0.30,
    "Doll_Center_Volume": 0.24,
    "Dramatic_3D_Volume": 0.38,
    "Wispy_Manga": 0.36,
}


def apply_root_to_tip_alpha_gradient(texture, style="Natural_Everyday"):
    if texture is None or texture.shape[2] < 4:
        return texture

    result = texture.copy()
    h, w = result.shape[:2]

    y_coords = np.linspace(0.0, 1.0, h)[:, np.newaxis]
    alpha_decay = np.power(1.0 - y_coords, 0.65)
    alpha_decay = np.clip(alpha_decay + 0.35, 0.0, 1.0)

    original_alpha = result[:, :, 3].astype(np.float32) / 255.0
    new_alpha = original_alpha * alpha_decay


    jitter_intensity = 0.14 if style == "Dramatic_3D_Volume" else 0.05
    np.random.seed(42)
    noise = np.random.uniform(1.0 - jitter_intensity, 1.0 + jitter_intensity, (h, w))
    new_alpha = np.clip(new_alpha * noise, 0.0, 1.0)

    alpha_uint8 = np.clip(new_alpha * 255.0, 0, 255).astype(np.uint8)
    alpha_blurred = cv2.GaussianBlur(alpha_uint8, (3, 3), 0.7)
    result[:, :, 3] = alpha_blurred

    if style in ["Dramatic_3D_Volume", "Wispy_Manga", "Cat_Eye_Outer_Volume"]:
        rgb = result[:, :, :3].astype(np.float32)
        tip_mask = np.clip((0.45 - y_coords) / 0.45, 0.0, 1.0) 
        
        specular_noise = np.random.uniform(0.0, 1.0, (h, w))
        specular_map = (specular_noise > 0.95).astype(np.float32) * tip_mask 
        specular_map *= 35.0
        
        for c in range(3):
            rgb[:, :, c] = np.clip(rgb[:, :, c] + specular_map, 0, 255)
            
        result[:, :, :3] = rgb.astype(np.uint8)

    return result


def create_follicle_root_shadow(curve_pts, canvas_shape, style="Natural_Everyday"):
    h, w = canvas_shape[:2]
    shadow = np.zeros((h, w, 4), dtype=np.uint8)

    pts = np.asarray(curve_pts, dtype=np.float32)
    if len(pts) < 3:
        return shadow

    strength = 0.08 if style == "Dramatic_3D_Volume" else 0.15

    num_roots = int(np.linalg.norm(pts[-1] - pts[0]) * 0.8)
    if num_roots <= 0:
        return shadow

    t_vals = np.linspace(0, 1, num_roots)
    root_x = np.interp(t_vals, np.linspace(0, 1, len(pts)), pts[:, 0])
    root_y = np.interp(t_vals, np.linspace(0, 1, len(pts)), pts[:, 1])

    dots_mask = np.zeros((h, w), dtype=np.uint8)
    for x, y in zip(root_x, root_y):
        ix, iy = int(round(x)), int(round(y))
        if 0 <= ix < w and 0 <= iy < h:
            cv2.circle(dots_mask, (ix, iy), 1, 180, -1)

    dots_mask = cv2.GaussianBlur(dots_mask, (3, 3), 0.8)

    shadow[:, :, 0] = 15
    shadow[:, :, 1] = 10
    shadow[:, :, 2] = 8
    shadow[:, :, 3] = np.clip(dots_mask.astype(np.float32) * strength, 0, 255).astype(np.uint8)

    return shadow


def prepare_lash_texture_high_res(texture, target_w, target_h):
    if texture is None:
        return None

    alpha = texture[:, :, 3] if texture.shape[2] == 4 else texture[:, :, 0]
    ys, xs = np.where(alpha > 5)

    if len(xs) > 0 and len(ys) > 0:
        x1, x2 = int(xs.min()), int(xs.max())
        y1, y2 = int(ys.min()), int(ys.max())
        texture = texture[y1:y2+1, x1:x2+1]

    resized = cv2.resize(
        texture,
        (max(4, int(target_w)), max(4, int(target_h))),
        interpolation=cv2.INTER_LANCZOS4
    )
    return resized

def warp_lash_preserving_structure(texture, curve_pts, canvas_shape, style="Natural_Everyday"):
    h, w = canvas_shape[:2]
    th, tw = texture.shape[:2]
 
    if th < 2 or tw < 2:
        return np.zeros((h, w, 4), dtype=np.uint8)
 
    pts = np.asarray(curve_pts, dtype=np.float32)
    p_inner = pts[0]
    p_outer = pts[-1]
 
    eye_vec = p_outer - p_inner
    eye_dist = np.linalg.norm(eye_vec)
    if eye_dist < 1e-5:
        return np.zeros((h, w, 4), dtype=np.uint8)
 
    u_axis = eye_vec / eye_dist
    normal_vec = np.array([-eye_vec[1], eye_vec[0]], dtype=np.float32) / eye_dist
    if normal_vec[1] > 0:
        normal_vec *= -1.0
 
    height_factor = LASH_HEIGHT_FACTORS.get(style, 0.35)
    target_height = eye_dist * height_factor
 
    mid_idx = len(pts) // 2
    p_center = pts[mid_idx]
 
    arc_lift_factor = 1.0
    if style in ["Dramatic_3D_Volume", "Wispy_Manga"]:
        arc_lift_factor = 0.88
    elif style == "Cat_Eye_Outer_Volume":
        arc_lift_factor = 0.93
 
    dst_top = p_center + normal_vec * (target_height * arc_lift_factor)
 
    src_tri = np.float32([[0, th - 1], [tw - 1, th - 1], [tw * 0.5, 0]])
    dst_tri = np.float32([p_inner, p_outer, dst_top])
 
    affine_mat = cv2.getAffineTransform(src_tri, dst_tri)
 
    warped = cv2.warpAffine(
        texture, affine_mat, (w, h),
        flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0)
    )

    inv_affine = cv2.invertAffineTransform(affine_mat)
 
    xs = np.arange(w, dtype=np.float32)
    ys = np.arange(h, dtype=np.float32)
    grid_x, grid_y = np.meshgrid(xs, ys)
 
    src_y = inv_affine[1, 0] * grid_x + inv_affine[1, 1] * grid_y + inv_affine[1, 2]
    root_weight = np.clip(src_y / max(th - 1, 1), 0.0, 1.0)  
 
    rel = pts - p_inner
    u_vals = rel @ u_axis
    n_vals = rel @ normal_vec
    order = np.argsort(u_vals)
    u_sorted, n_sorted = u_vals[order], n_vals[order]
 
    u_pix = (grid_x - p_inner[0]) * u_axis[0] + (grid_y - p_inner[1]) * u_axis[1]
    curve_offset = np.interp(u_pix, u_sorted, n_sorted, left=n_sorted[0], right=n_sorted[-1])
 
    shift = curve_offset * root_weight
    map_x = (grid_x - shift * normal_vec[0]).astype(np.float32)
    map_y = (grid_y - shift * normal_vec[1]).astype(np.float32)
 
    warped = cv2.remap(
        warped, map_x, map_y,
        interpolation=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0)
    )

    if style in ["Dramatic_3D_Volume", "Wispy_Manga", "Cat_Eye_Outer_Volume"]:
        rows, cols = warped.shape[:2]
 
        map_x2 = np.tile(np.arange(cols, dtype=np.float32), (rows, 1))
        map_y2 = np.tile(np.arange(rows, dtype=np.float32)[:, np.newaxis], (1, cols))
 
        x_min, x_max = min(p_inner[0], p_outer[0]), max(p_inner[0], p_outer[0])
        x_center = (x_min + x_max) / 2.0
        eye_width = max(1.0, x_max - x_min)
 
        dist_from_center = (map_x2 - x_center) / (eye_width / 2.0)
        bend_mask = np.clip(1.0 - dist_from_center**2, 0.0, 1.0)
 
        y_mask = (rows - map_y2) / float(rows)
        y_mask = np.clip(y_mask, 0.0, 1.0)
 
        bend_amount = target_height * 0.12 if style == "Dramatic_3D_Volume" else target_height * 0.06
        map_y2 -= (bend_mask * y_mask * bend_amount).astype(np.float32)
 
        warped = cv2.remap(
            warped, map_x2, map_y2,
            interpolation=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0)
        )
 
    return warped
 

def _warp_triangle(src_img, dst_img, tri_src, tri_dst):
    """يلف مثلث وحد من الصورة المصدر ويدمجه بالـ overlay الوجهة (alpha blend)."""
    r1 = cv2.boundingRect(np.float32([tri_src]))
    r2 = cv2.boundingRect(np.float32([tri_dst]))
    if r1[2] <= 0 or r1[3] <= 0 or r2[2] <= 0 or r2[3] <= 0:
        return
 
    tri_src_off = tri_src - np.float32([r1[0], r1[1]])
    tri_dst_off = tri_dst - np.float32([r2[0], r2[1]])
 
    x1, y1 = max(r1[0], 0), max(r1[1], 0)
    x2, y2 = min(r1[0] + r1[2], src_img.shape[1]), min(r1[1] + r1[3], src_img.shape[0])
    if x2 <= x1 or y2 <= y1:
        return
    src_crop = src_img[r1[1]:r1[1] + r1[3], r1[0]:r1[0] + r1[2]]
    if src_crop.size == 0 or src_crop.shape[0] != r1[3] or src_crop.shape[1] != r1[2]:
       
        return
 
    mat = cv2.getAffineTransform(tri_src_off.astype(np.float32), tri_dst_off.astype(np.float32))
    warped = cv2.warpAffine(
        src_crop, mat, (r2[2], r2[3]),
        flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0)
    )
 
    mask = np.zeros((r2[3], r2[2]), dtype=np.uint8)
    cv2.fillConvexPoly(mask, np.int32(tri_dst_off), 255)
 
    dst_x0, dst_y0 = r2[0], r2[1]
    dst_x1, dst_y1 = r2[0] + r2[2], r2[1] + r2[3]
 
    cx0, cy0 = max(dst_x0, 0), max(dst_y0, 0)
    cx1, cy1 = min(dst_x1, dst_img.shape[1]), min(dst_y1, dst_img.shape[0])
    if cx1 <= cx0 or cy1 <= cy0:
        return
 
    wx0, wy0 = cx0 - dst_x0, cy0 - dst_y0
    wx1, wy1 = cx1 - dst_x0, cy1 - dst_y0
 
    region = dst_img[cy0:cy1, cx0:cx1]
    warped_region = warped[wy0:wy1, wx0:wx1]
    mask_region = mask[wy0:wy1, wx0:wx1]
 
    alpha_new = (warped_region[:, :, 3].astype(np.float32) / 255.0) * (mask_region.astype(np.float32) / 255.0)
    alpha_old = region[:, :, 3].astype(np.float32) / 255.0
 
    for c in range(3):
        region[:, :, c] = (
            warped_region[:, :, c] * alpha_new + region[:, :, c] * alpha_old * (1.0 - alpha_new)
        ).astype(np.uint8)
    region[:, :, 3] = np.clip((alpha_new + alpha_old * (1.0 - alpha_new)) * 255.0, 0, 255).astype(np.uint8)
 
 
def warp_lash_along_curve(texture, curve_pts, canvas_shape, style="Natural_Everyday"):

    h, w = canvas_shape[:2]
    th, tw = texture.shape[:2]
    result = np.zeros((h, w, 4), dtype=np.uint8)
 
    pts = np.asarray(curve_pts, dtype=np.float32)
    n = len(pts)
    if n < 3 or th < 2 or tw < 2:
        return result
 
    seg_lengths = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    cum_len = np.concatenate([[0.0], np.cumsum(seg_lengths)])
    total_len = cum_len[-1]
    if total_len < 1e-5:
        return result
    t_curve = cum_len / total_len 
 
    normals = np.zeros_like(pts)
    for i in range(n):
        i0, i1 = max(i - 1, 0), min(i + 1, n - 1)
        tangent = pts[i1] - pts[i0]
        norm = np.linalg.norm(tangent)
        tangent = tangent / norm if norm > 1e-5 else np.array([1.0, 0.0], dtype=np.float32)
        nrm = np.array([-tangent[1], tangent[0]], dtype=np.float32)
        if nrm[1] > 0:
            nrm = -nrm
        normals[i] = nrm
 
    height_factor = LASH_HEIGHT_FACTORS.get(style, 0.35)
    base_height = total_len * height_factor
 
    def height_profile(t):
        taper = np.clip(np.sin(np.pi * np.clip(t, 0.0, 1.0)) ** 0.6, 0.18, 1.0)
        return base_height * taper
 
    src_xs = (t_curve * (tw - 1)).astype(np.float32)
 
    for i in range(n - 1):
        sx0, sx1 = src_xs[i], src_xs[i + 1]
        src_quad = np.float32([[sx0, th - 1], [sx1, th - 1], [sx1, 0.0], [sx0, 0.0]])
 
        h0, h1 = height_profile(t_curve[i]), height_profile(t_curve[i + 1])
        p0_root, p1_root = pts[i], pts[i + 1]
        p0_tip = p0_root + normals[i] * h0
        p1_tip = p1_root + normals[i + 1] * h1
 
        dst_quad = np.float32([p0_root, p1_root, p1_tip, p0_tip])
 
        _warp_triangle(texture, result, np.float32([src_quad[0], src_quad[1], src_quad[2]]),
                        np.float32([dst_quad[0], dst_quad[1], dst_quad[2]]))
        _warp_triangle(texture, result, np.float32([src_quad[0], src_quad[2], src_quad[3]]),
                        np.float32([dst_quad[0], dst_quad[2], dst_quad[3]]))
 
    return result
 

def generate_lashes_overlay_rgba(image_shape, landmarks, style="Dramatic_3D_Volume", scale=100.0):
    h, w = image_shape[:2]
    result_overlay = np.zeros((h, w, 4), dtype=np.uint8)

    try:
        SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        SCRIPT_DIR = os.getcwd()
    dataset_dir = os.path.join(SCRIPT_DIR, "lashes_dataset")

    eyes_config = [(LEFT_EYE_PTS, False), (RIGHT_EYE_PTS, True)]

    for eye_pts, is_left_eye in eyes_config:
        curve_pts = np.array(
            [[landmarks[i].x * w, landmarks[i].y * h] for i in eye_pts["curve"]],
            dtype=np.float32
        )

        tex_side_str = "right" if is_left_eye else "left"
        tex_path = os.path.join(dataset_dir, f"{style}_{tex_side_str}.png")

        if not os.path.exists(tex_path):
            continue

        texture = cv2.imread(tex_path, cv2.IMREAD_UNCHANGED)
        if texture is None:
            continue

        if texture.shape[2] == 3:
            b, g, r = cv2.split(texture)
            a = np.full(b.shape, 255, dtype=np.uint8)
            texture = cv2.merge([b, g, r, a])

        texture = cv2.flip(texture, 1)
        texture = apply_root_to_tip_alpha_gradient(texture, style=style)

        arc_len = np.sum(np.linalg.norm(np.diff(curve_pts, axis=0), axis=1))
        target_w = int(arc_len)
        target_h = int(target_w * LASH_HEIGHT_FACTORS.get(style, 0.35))

        if target_w < 5 or target_h < 5:
            continue

        texture_prepared = prepare_lash_texture_high_res(texture, target_w, target_h)
        follicle_shadow = create_follicle_root_shadow(curve_pts, (h, w), style=style)

        sh_a = follicle_shadow[:, :, 3].astype(np.float32) / 255.0
        bg_a = result_overlay[:, :, 3].astype(np.float32) / 255.0
        for c in range(3):
            result_overlay[:, :, c] = (
                follicle_shadow[:, :, c] * sh_a + result_overlay[:, :, c] * bg_a * (1.0 - sh_a)
            ).astype(np.uint8)
        result_overlay[:, :, 3] = np.clip((sh_a + bg_a * (1.0 - sh_a)) * 255.0, 0, 255).astype(np.uint8)

      
        eye_layer = warp_lash_preserving_structure(texture_prepared, curve_pts, (h, w), style=style)

        fg_a = eye_layer[:, :, 3].astype(np.float32) / 255.0
        bg_a = result_overlay[:, :, 3].astype(np.float32) / 255.0
        for c in range(3):
            result_overlay[:, :, c] = (
                eye_layer[:, :, c] * fg_a + result_overlay[:, :, c] * bg_a * (1.0 - fg_a)
            ).astype(np.uint8)

        result_overlay[:, :, 3] = np.clip((fg_a + bg_a * (1.0 - fg_a)) * 255.0, 0, 255).astype(np.uint8)

    return result_overlay


def apply_photorealistic_lashes_correct(image, lashes_rgba):
    img_bgra = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA).astype(np.float32)
    overlay = lashes_rgba.astype(np.float32)

    alpha = overlay[:, :, 3:4] / 255.0
    blended_rgb = overlay[:, :, :3] * alpha + img_bgra[:, :, :3] * (1.0 - alpha)

    return np.clip(blended_rgb, 0, 255).astype(np.uint8)

def apply_experta_lashes_recommendation(image, landmarks, face_scale, experta_result, input_data=None):
    lashes_rec = ""
    eye_category = "Almond"
    
    if "expert_output" in experta_result:
        eyes = experta_result.get("expert_output", {}).get("eyes", {})
        eye_info = eyes.get("left") or eyes.get("right") or {}
        lashes_rec = eye_info.get("plan", {}).get("lashes", "")
        eye_category = eye_info.get("category", {}).get("category", "Almond")
    elif "plan" in experta_result:
        lashes_rec = experta_result.get("plan", {}).get("lashes", "")
        eye_category = experta_result.get("category", {}).get("category", "Almond")
    
    lashes_rec = str(lashes_rec).strip()
    eye_category = str(eye_category).strip()
    
    occasion = 'work'
    if input_data and 'occasion' in input_data:
        occasion = str(input_data['occasion']).strip().lower()

    lash_mapping = {
        'ماسكرا تكثيف عند الزاوية الخارجية': 'Cat_Eye_Outer_Volume',
        'رموش كثيفة 3D': 'Dramatic_3D_Volume',
        'رموش طويلة وكثيفة فاخرة': 'Dramatic_3D_Volume',
        'رموش قطة متوسطة / رموش طبيعية': 'Cat_Eye_Outer_Volume',
    }

    chosen_style = lash_mapping.get(lashes_rec)

    if not chosen_style:
        if 'فاخرة' in lashes_rec or '3D' in lashes_rec or 'ثلاثية' in lashes_rec:
            chosen_style = 'Dramatic_3D_Volume'
        elif 'قطة' in lashes_rec or 'خارجية' in lashes_rec:
            chosen_style = 'Cat_Eye_Outer_Volume'
        elif 'طبيعية' in lashes_rec or 'ماسكرا' in lashes_rec:
            chosen_style = 'Natural_Everyday'
        else:
            chosen_style = 'Natural_Everyday'

    print(f" [Experta Lashes Bridge] النص من القواعد: '{lashes_rec}' | النمط المطبق: '{chosen_style}'")

    overlay_rgba = generate_lashes_overlay_rgba(image.shape, landmarks, style=chosen_style, scale=face_scale)
    result = apply_photorealistic_lashes_correct(image, overlay_rgba)
    return result, chosen_style


if __name__ == "__main__":
    try:
        with open("makeup_analysis.json", "r", encoding="utf-8") as f:
            input_data = json.load(f)
    except Exception:
        input_data = {
            'geo_shape': 'Almond',
            'eye_type': 'Hooded',
            'inter_eye_ratio': 0.35,
            'occasion': 'evening'
        }

    try:
        if EyeMakeupEngine is not None:
            engine = EyeMakeupEngine()
            experta_result = input_data
        else:
            raise ImportError("EyeMakeupEngine غير متاح.")
    except Exception as e:
        print(f" تجري معالجة القواعد افتراضياً: {e}")
        experta_result = {
            'category': {'category': input_data.get('eye_type', 'Hooded')},
            'plan': {'lashes': 'رموش كثيفة 3D' if input_data.get('occasion') == 'evening' else 'ماسكرا تكثيف عند الزاوية الخارجية'}
        }

    image_path = "test2.jpg"
    img = cv2.imread(image_path)

    if img is not None:
        h, w, _ = img.shape
        mp_face_mesh = mp.solutions.face_mesh

        with mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, refine_landmarks=True) as face_mesh:
            results = face_mesh.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

            if results.multi_face_landmarks:
                landmarks = results.multi_face_landmarks[0].landmark

                pt1 = np.array([landmarks[234].x * w, landmarks[234].y * h])
                pt2 = np.array([landmarks[454].x * w, landmarks[454].y * h])
                scale = np.linalg.norm(pt1 - pt2)

                output_img, applied_style = apply_experta_lashes_recommendation(img, landmarks, scale, experta_result, input_data)
                cv2.imwrite("experta_lashes_output.jpg", output_img)
                print(f" تم تطبيق الرموش وتصدير الصورة إلى: experta_lashes_output.jpg")

                styles = [
                    "Natural_Everyday",
                    "Cat_Eye_Outer_Volume",
                    "Doll_Center_Volume",
                    "Dramatic_3D_Volume",
                    "Wispy_Manga"
                ]

                fig, axes = plt.subplots(2, 3, figsize=(15, 9))
                axes = axes.ravel()

                for idx, st in enumerate(styles):
                    overlay_rgba = generate_lashes_overlay_rgba(img.shape, landmarks, style=st, scale=scale)
                    res = apply_photorealistic_lashes_correct(img, overlay_rgba)

                    axes[idx].imshow(cv2.cvtColor(res, cv2.COLOR_BGR2RGB))
                    axes[idx].set_title(f"Lash Style: {st}", fontsize=11, fontweight='bold')
                    axes[idx].axis("off")

                axes[5].axis("off")

                plt.tight_layout()
                plt.show()
            else:
                print(" لم يتم التعرف على المعالم في الصورة.")
    else:
        print(f" تعذر تحميل الصورة: {image_path}")