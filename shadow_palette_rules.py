

# import cv2
# import numpy as np
# import matplotlib.pyplot as plt

# def detect_neutral_color(bgr):
#     b, g, r = bgr

#     # أسود صريح
#     if b < 40 and g < 40 and r < 40:
#         return "black"

#     # أبيض صريح
#     if b > 220 and g > 220 and r > 220:
#         return "white"

#     # غير ذلك → ليس محايداً
#     return None

# # ==========================================================
# # باليت  لون للبشرة الدافئة
# # ==========================================================
# NEUTRAL_12_WARM = {
#     "Highlight": [
#         (18, 20, 255),
#         (22, 25, 240),
#         (15, 15, 255)
#     ],
#     "Base": [
#         (20, 60, 200),
#         (25, 70, 180),
#         (30, 55, 190)
#     ],
#     "Sculpt": [
#         (15, 95, 90),
#         (12, 110, 80),
#         (10, 120, 70)
#     ],
#     "Accent": [
#         (25, 80, 230),
#         (18, 90, 210),
#         (30, 70, 220)
#     ]
# }

# # ==========================================================
# # باليت  لون للبشرة الباردة
# # ==========================================================
# NEUTRAL_12_COOL = {
#     "Highlight": [
#         (160, 15, 255),
#         (170, 20, 240),
#         (155, 10, 255)
#     ],
#     "Base": [
#         (165, 50, 200),
#         (160, 40, 190),
#         (170, 45, 180)
#     ],
#     "Sculpt": [
#         (170, 90, 90),
#         (160, 100, 80),
#         (175, 110, 70)
#     ],
#     "Accent": [
#         (165, 70, 230),
#         (170, 80, 210),
#         (160, 60, 220)
#     ]
# }

# def get_neutral_palette_12(undertone):
#     return NEUTRAL_12_WARM if undertone == "Warm" else NEUTRAL_12_COOL

# # ==========================================================
# # HSV → RGB
# # ==========================================================
# def hsv_to_rgb(hsv):
#     hsv_img = np.uint8([[[hsv[0], hsv[1], hsv[2]]]])
#     return cv2.cvtColor(hsv_img, cv2.COLOR_HSV2RGB)[0][0]

# # ==========================================================
# # عرض باليت 12 لون
# # ==========================================================
# def show_neutral_palette_12(palette, cloth_rgb):
#     plt.figure(figsize=(10, 4))
#     plt.suptitle("Makeup Shadow Palette", fontsize=18, fontweight='bold')

#     plt.gcf().patch.set_facecolor('#f8f8f8')

#     groups = ["Highlight", "Base", "Sculpt", "Accent"]
#     idx = 1

#     for group in groups:
#         print(f"\n{group} Colors:")

#         for hsv in palette[group]:
#             rgb = hsv_to_rgb(hsv)

#             # HEX
#             hex_color = "#{:02X}{:02X}{:02X}".format(rgb[0], rgb[1], rgb[2])

#             # Hue 
#             hsv_back = cv2.cvtColor(np.uint8([[rgb]]), cv2.COLOR_RGB2HSV)[0][0]
#             final_hue = hsv_back[0]

#             print(f"RGB: {rgb}   HEX: {hex_color}   Hue: {final_hue}")

#             ax = plt.subplot(3, 4, idx)
#             ax.imshow(np.ones((150,150,3), dtype=np.uint8) * rgb)

#             for spine in ax.spines.values():
#                 spine.set_edgecolor('#444')
#                 spine.set_linewidth(2)

#             ax.set_xticks([])
#             ax.set_yticks([])
#             idx += 1

#     plt.tight_layout(rect=[0, 0, 1, 0.95])
#     plt.show()


# # ==========================================================
# # تأثير الأندرتون
# # ==========================================================
# def apply_undertone(hsv, undertone):
#     h, s, v = hsv

#     if undertone == "Warm":
#         h = (h + 8) % 180
#         s = min(s + 25, 255)
#         v = min(v + 15, 255)

#     elif undertone == "Cool":
#         h = (h - 12) % 180
#         s = min(s + 35, 255)
#         v = max(v - 20, 0)

#     return (int(h), int(s), int(v))

# # ==========================================================
# # قواعد الباليت 
# # ==========================================================
# def mono(H, u):
#     return {
#         "Base":      apply_undertone((H, 70, 180), u),
#         "Highlight": apply_undertone((H, 30, 255), u),
#         "Sculpt":    apply_undertone((H, 95, 90), u),
#     }

# def analogous(H, u):
#     return {
#         "Base":      apply_undertone(((H + 15) % 180, 65, 185), u),
#         "Highlight": apply_undertone(((H - 10) % 180, 35, 255), u),
#         "Sculpt":    apply_undertone(((H + 35) % 180, 85, 80), u),
#     }

# def split(H, u):
#     return {
#         "Base":      apply_undertone(((H + 75) % 180, 60, 190), u),
#         "Highlight": apply_undertone((H, 25, 255), u),
#         "Sculpt":    apply_undertone(((H + 105) % 180, 90, 70), u),
#     }

# def triadic(H, u):
#     return {
#         "Base":      apply_undertone(((H + 60) % 180, 55, 175), u),
#         "Highlight": apply_undertone((20, 20, 255), u),
#         "Sculpt":    apply_undertone(((H - 60) % 180, 85, 75), u),
#     }

# def earth(H, u):
#     return {
#         "Base":      apply_undertone((15, 65, 160), u),
#         "Highlight": apply_undertone((20, 25, 245), u),
#         "Sculpt":    apply_undertone((12, 95, 60), u),
#     }

# PALETTE_BASE_RULES = {
#     "Monochromatic": mono,
#     "Analogous": analogous,
#     "Split-Complementary": split,
#     "Triadic": triadic,
#     "Earth Colors": earth
# }

# # ==========================================================
# # عرض جميع الاستراتيجيات
# # ==========================================================
# def show_all_palettes(H, skin_undertone, cloth_rgb):
#     strategies = list(PALETTE_BASE_RULES.keys())

#     plt.figure(figsize=(10, 4 * len(strategies)))
#     plt.suptitle("Makeup Shadow Palette", fontsize=18, fontweight='bold')

#     # خلفية ناعمة
#     plt.gcf().patch.set_facecolor('#f8f8f8')

#     for idx, strategy in enumerate(strategies):
#         palette = PALETTE_BASE_RULES[strategy](H, skin_undertone)

#         print(f"\nPalette {idx+1}:")

#         for i, (_, hsv) in enumerate(palette.items()):
#             rgb_p = hsv_to_rgb(hsv)

#             # HEX
#             hex_color = "#{:02X}{:02X}{:02X}".format(rgb_p[0], rgb_p[1], rgb_p[2])

#             # حساب الهيو النهائي من RGB
#             hsv_back = cv2.cvtColor(np.uint8([[rgb_p]]), cv2.COLOR_RGB2HSV)[0][0]
#             final_hue = hsv_back[0]

#             print(f"RGB: {rgb_p}   HEX: {hex_color}   Hue: {final_hue}")

#             ax = plt.subplot(len(strategies), 3, idx * 3 + i + 1)
#             ax.imshow(np.ones((150,150,3), dtype=np.uint8) * rgb_p)

#             for spine in ax.spines.values():
#                 spine.set_edgecolor('#444')
#                 spine.set_linewidth(2)

#             ax.set_xticks([])
#             ax.set_yticks([])

#         # مسافة بين كل باليت
#         plt.subplots_adjust(hspace=0.6)

#     plt.tight_layout(rect=[0, 0, 1, 0.95])
#     plt.show()

# # ==========================================================
# # تشغيل كامل
# # ==========================================================
# if __name__ == "__main__":
#     from skin_analysis import analyze_skin
#     from clothing_hue_extractor import analyze_clothing_color

#     img = cv2.imread("pictures3/warm.jpg")
#     if img is None:
#         raise ValueError("❌ الصورة غير موجودة أو المسار غير صحيح")

#     skin_data = analyze_skin(img)
#     skin_undertone = skin_data["undertone"]


#     cloth = analyze_clothing_color("pictures4/photo_2026-07-17_15-46-29.jpg")

#     # أول شيء: معالجة الألوان المحايدة قبل أي استخدام لـ dominant_bgr
#     cloth_bgr = cloth.get("dominant_bgr", None)

#     if cloth_bgr is None:
#         print("⚠️ No dominant_bgr detected → using neutral palette")
#         cloth_rgb = np.array([200, 200, 200], dtype=np.uint8)
#         palette12 = get_neutral_palette_12(skin_undertone)
#         show_neutral_palette_12(palette12, cloth_rgb)
#         exit()

#     neutral_type = detect_neutral_color(cloth_bgr)

#     if neutral_type is not None:
#         print("⚠️ Neutral color detected → generating 12-color palette")
#         cloth_rgb = np.array([200, 200, 200], dtype=np.uint8)
#         palette12 = get_neutral_palette_12(skin_undertone)
#         show_neutral_palette_12(palette12, cloth_rgb)
#         exit()

#     # إذا اللون غير محايد → نستخدم Hue
#     H = cloth["Input_Hue"]
#     cloth_rgb = np.array(cloth_bgr[::-1], dtype=np.uint8)

#     print("Detected Undertone:", skin_undertone)
#     print("Detected Clothing Hue:", H)

#     show_all_palettes(H, skin_undertone, cloth_rgb)
# ==========================================================
# إصلاح توافق experta مع بايثون 3.10+ (تمت إزالة collections.Mapping)
# # ==========================================================
# import collections
# import collections.abc
# if not hasattr(collections, "Mapping"):
#     collections.Mapping = collections.abc.Mapping

# import cv2
# import numpy as np
# import matplotlib.pyplot as plt
# from functools import reduce

# from experta import KnowledgeEngine, Fact, Rule, MATCH, TEST

# # ==========================================================
# # باليتات محايدة (دافئ / بارد) — بيانات ثابتة، ليست قواعد قرار
# # ==========================================================
# NEUTRAL_12_WARM = {
#     "Highlight": [(18, 20, 255), (22, 25, 240), (15, 15, 255)],
#     "Base":      [(20, 60, 200), (25, 70, 180), (30, 55, 190)],
#     "Sculpt":    [(15, 95, 90), (12, 110, 80), (10, 120, 70)],
#     "Accent":    [(25, 80, 230), (18, 90, 210), (30, 70, 220)],
# }

# NEUTRAL_12_COOL = {
#     "Highlight": [(160, 15, 255), (170, 20, 240), (155, 10, 255)],
#     "Base":      [(165, 50, 200), (160, 40, 190), (170, 45, 180)],
#     "Sculpt":    [(170, 90, 90), (160, 100, 80), (175, 110, 70)],
#     "Accent":    [(165, 70, 230), (170, 80, 210), (160, 60, 220)],
# }

# PALETTE_BY_UNDERTONE = {"Warm": NEUTRAL_12_WARM, "Cool": NEUTRAL_12_COOL}


# def get_neutral_palette_12(undertone):
#     return PALETTE_BY_UNDERTONE.get(undertone, NEUTRAL_12_COOL)


# # ==========================================================
# # HSV → RGB وأدوات رسم عامة (بدون منطق قرار)
# # ==========================================================
# def hsv_to_rgb(hsv):
#     hsv_img = np.uint8([[[hsv[0], hsv[1], hsv[2]]]])
#     return cv2.cvtColor(hsv_img, cv2.COLOR_HSV2RGB)[0][0]


# def rgb_hex_hue(rgb):
#     hex_color = "#{:02X}{:02X}{:02X}".format(rgb[0], rgb[1], rgb[2])
#     hsv_back = cv2.cvtColor(np.uint8([[rgb]]), cv2.COLOR_RGB2HSV)[0][0]
#     return hex_color, hsv_back[0]


# def style_spines(ax):
#     list(map(lambda spine: (spine.set_edgecolor('#444'), spine.set_linewidth(2)), ax.spines.values()))
#     return ax


# def dedupe_hsv(hsv, seen, step=6, guard=30):
#     """
#     يرجّع (hsv, rgb) بحيث لا يتكرّر rgb (كـ tuple قابل للمقارنة) ضمن مجموعة seen.
#     إن كان اللون مكررًا، يُزاح الـHue تدريجيًا عبر استدعاء الدالة لنفسها
#     (بدل for/while)، مع سقف (guard) لمنع أي استدعاء ذاتي بلا نهاية.
#     """
#     rgb = hsv_to_rgb(hsv)
#     rgb_key = tuple(int(x) for x in rgb)
#     is_acceptable = (rgb_key not in seen) or guard <= 0
#     return (hsv, rgb) if is_acceptable else dedupe_hsv(
#         ((hsv[0] + step) % 180, hsv[1], hsv[2]), seen, step, guard - 1
#     )


# def render_color_cell(cell_index, hsv, rows, cols, seen):
#     hsv_final, rgb = dedupe_hsv(hsv, seen)
#     seen.add(tuple(int(x) for x in rgb))
#     hex_color, final_hue = rgb_hex_hue(rgb)
#     print(f"RGB: {rgb}   HEX: {hex_color}   Hue: {final_hue}")
#     ax = plt.subplot(rows, cols, cell_index)
#     ax.imshow(np.ones((150, 150, 3), dtype=np.uint8) * rgb)
#     style_spines(ax)
#     ax.set_xticks([])
#     ax.set_yticks([])
#     return rgb


# def render_neutral_group(start_index, group_name, colors, rows, cols, seen):
#     print(f"\n{group_name} Colors:")
#     indices = range(start_index, start_index + len(colors))
#     list(map(lambda pair: render_color_cell(pair[0], pair[1], rows, cols, seen), zip(indices, colors)))
#     return start_index + len(colors)


# def show_neutral_palette_12(palette, cloth_rgb):
#     plt.figure(figsize=(10, 4))
#     plt.suptitle("Makeup Shadow Palette", fontsize=18, fontweight='bold')
#     plt.gcf().patch.set_facecolor('#f8f8f8')

#     groups = ["Highlight", "Base", "Sculpt", "Accent"]
#     rows, cols = 3, 4
#     seen = set()  # يجمع كل الألوان المعروضة في هذه اللوحة لمنع التكرار
#     reduce(lambda idx, group: render_neutral_group(idx, group, palette[group], rows, cols, seen), groups, 1)

#     plt.tight_layout(rect=[0, 0, 1, 0.95])
#     plt.show()


# # ==========================================================
# # قواعد الباليتات الخمس — صيغ رياضية ثابتة، تُستدعى بحسب
# # اسم "transform" الذي يقرره محرك experta (وليس بـ if/elif)
# # ==========================================================
# UNDERTONE_TRANSFORMS = {
#     "warm": lambda h, s, v: ((h + 8) % 180, min(s + 25, 255), min(v + 15, 255)),
#     "cool": lambda h, s, v: ((h - 12) % 180, min(s + 35, 255), max(v - 20, 0)),
# }


# def apply_undertone(hsv, transform_name):
#     h, s, v = hsv
#     transform = UNDERTONE_TRANSFORMS.get(transform_name, lambda h, s, v: (h, s, v))  # بدون تحويل إن لم يقرر المحرك شيئًا
#     h2, s2, v2 = transform(h, s, v)
#     return (int(h2), int(s2), int(v2))


# def mono(H, t):
#     return {
#         "Base":      apply_undertone((H, 70, 180), t),
#         "Highlight": apply_undertone((H, 30, 255), t),
#         "Sculpt":    apply_undertone((H, 95, 90), t),
#     }


# def analogous(H, t):
#     return {
#         "Base":      apply_undertone(((H + 15) % 180, 65, 185), t),
#         "Highlight": apply_undertone(((H - 10) % 180, 35, 255), t),
#         "Sculpt":    apply_undertone(((H + 35) % 180, 85, 80), t),
#     }


# def split(H, t):
#     return {
#         "Base":      apply_undertone(((H + 75) % 180, 60, 190), t),
#         "Highlight": apply_undertone((H, 25, 255), t),
#         "Sculpt":    apply_undertone(((H + 105) % 180, 90, 70), t),
#     }


# def triadic(H, t):
#     return {
#         "Base":      apply_undertone(((H + 60) % 180, 55, 175), t),
#         "Highlight": apply_undertone((20, 20, 255), t),
#         "Sculpt":    apply_undertone(((H - 60) % 180, 85, 75), t),
#     }


# def earth(H, t):
#     return {
#         "Base":      apply_undertone((15, 65, 160), t),
#         "Highlight": apply_undertone((20, 25, 245), t),
#         "Sculpt":    apply_undertone((12, 95, 60), t),
#     }


# PALETTE_BASE_RULES = {
#     "Monochromatic": mono,
#     "Analogous": analogous,
#     "Split-Complementary": split,
#     "Triadic": triadic,
#     "Earth Colors": earth,
# }


# def render_strategy(strategy_index, strategy, H, transform_name, rows, cols, seen):
#     palette = PALETTE_BASE_RULES[strategy](H, transform_name)
#     print(f"\nPalette {strategy_index + 1}:")
#     values = list(palette.values())
#     base_cell = strategy_index * cols
#     list(map(lambda pair: render_color_cell(base_cell + pair[0] + 1, pair[1], rows, cols, seen), enumerate(values)))
#     plt.subplots_adjust(hspace=0.6)
#     return strategy_index + 1


# def show_all_palettes(H, transform_name, cloth_rgb):
#     """
#     يعرض كل الاستراتيجيات الخمس معًا دفعة واحدة (المستخدم لا يختار استراتيجية):
#     كل الألوان التي تناسب الملابس تُعرض دفعة واحدة، مع ضمان عدم تكرار
#     أي لون بين كل هذه اللوحات عبر مجموعة seen المشتركة.
#     """
#     strategies = list(PALETTE_BASE_RULES.keys())
#     rows, cols = len(strategies), 3

#     plt.figure(figsize=(10, 4 * rows))
#     plt.suptitle("Makeup Shadow Palette", fontsize=18, fontweight='bold')
#     plt.gcf().patch.set_facecolor('#f8f8f8')

#     seen = set()  # يجمع كل الألوان عبر الاستراتيجيات الخمس مجتمعة لمنع أي تكرار
#     reduce(lambda idx, item: render_strategy(item[0], item[1], H, transform_name, rows, cols, seen),
#            enumerate(strategies), 0)

#     plt.tight_layout(rect=[0, 0, 1, 0.95])
#     plt.show()


# # ==========================================================
# #                  محرك القواعد الخبير (experta)
# #   هنا فقط تمّ نقل منطق "إن ... وإلا" إلى قواعد خبير حقيقية
# # ==========================================================
# class ClothColor(Fact):
#     """bgr: صندوق BGR المهيمن للملابس (أو None) — hue: قيمة Input_Hue إن وُجدت"""
#     pass


# class SkinInfo(Fact):
#     """undertone: 'Warm' أو 'Cool' كما اكتُشف من skin_analysis"""
#     pass


# class MakeupExpert(KnowledgeEngine):
#     """
#     محرك قرار خبير: يستقبل حقائق (لون الملابس + أندرتون البشرة)
#     ويُصدر قرارين عبر إطلاق القواعد بدل if/elif:
#       - self.path        : 'neutral' أو 'colored'
#       - self.reason       : سبب القرار (لتوليد نفس رسائل الطباعة الأصلية)
#       - self.hue          : Hue المستخدم إن كان المسار 'colored'
#       - self.transform    : 'warm' أو 'cool' أو None (تُستخدم في apply_undertone)
#     """

#     def __init__(self):
#         super().__init__()
#         self.path = None
#         self.reason = None
#         self.hue = None
#         self.transform = None

#     # ---------- قواعد كشف حالة لون الملابس ----------
#     @Rule(ClothColor(bgr=None))
#     def rule_missing_color(self):
#         self.path, self.reason = "neutral", "missing"

#     @Rule(ClothColor(bgr=MATCH.bgr),
#           TEST(lambda bgr: bgr is not None and bgr[0] < 40 and bgr[1] < 40 and bgr[2] < 40))
#     def rule_black_detected(self, bgr):
#         self.path, self.reason = "neutral", "black"

#     @Rule(ClothColor(bgr=MATCH.bgr),
#           TEST(lambda bgr: bgr is not None and bgr[0] > 220 and bgr[1] > 220 and bgr[2] > 220))
#     def rule_white_detected(self, bgr):
#         self.path, self.reason = "neutral", "white"

#     @Rule(ClothColor(bgr=MATCH.bgr, hue=MATCH.hue),
#           TEST(lambda bgr: bgr is not None
#                and not (bgr[0] < 40 and bgr[1] < 40 and bgr[2] < 40)
#                and not (bgr[0] > 220 and bgr[1] > 220 and bgr[2] > 220)))
#     def rule_colored_detected(self, bgr, hue):
#         self.path, self.reason, self.hue = "colored", "colored", hue

#     # ---------- قواعد اختيار تحويل الأندرتون ----------
#     @Rule(SkinInfo(undertone="Warm"))
#     def rule_warm_undertone(self):
#         self.transform = "warm"

#     @Rule(SkinInfo(undertone="Cool"))
#     def rule_cool_undertone(self):
#         self.transform = "cool"


# def run_neutral_path(reason, skin_undertone):
#     messages = {
#         "missing": "⚠️ No dominant_bgr detected → using neutral palette",
#         "black":   "⚠️ Neutral color detected → generating 12-color palette",
#         "white":   "⚠️ Neutral color detected → generating 12-color palette",
#     }
#     print(messages[reason])
#     cloth_rgb = np.array([200, 200, 200], dtype=np.uint8)
#     palette12 = get_neutral_palette_12(skin_undertone)
#     show_neutral_palette_12(palette12, cloth_rgb)


# def run_colored_path(hue, cloth_bgr, transform_name, skin_undertone):
#     cloth_rgb = np.array(cloth_bgr[::-1], dtype=np.uint8)
#     print("Detected Undertone:", skin_undertone)
#     print("Detected Clothing Hue:", hue)
#     show_all_palettes(hue, transform_name, cloth_rgb)


# PATH_HANDLERS = {
#     "neutral": lambda expert, cloth, skin_undertone: run_neutral_path(expert.reason, skin_undertone),
#     "colored": lambda expert, cloth, skin_undertone: run_colored_path(
#         expert.hue, cloth.get("dominant_bgr"), expert.transform, skin_undertone),
# }


# def main():
#     from skin_analysis import analyze_skin
#     from clothing_hue_extractor import analyze_clothing_color

#     img = cv2.imread("pictures3/warm.jpg")
#     assert img is not None, "❌ الصورة غير موجودة أو المسار غير صحيح"

#     skin_data = analyze_skin(img)
#     skin_undertone = skin_data["undertone"]

#     cloth = analyze_clothing_color("pictures4/photo_2026-07-14_09-06-46.jpg")
#     cloth_bgr = cloth.get("dominant_bgr", None)

#     # --- تشغيل محرك القواعد الخبير ---
#     expert = MakeupExpert()
#     expert.reset()
#     expert.declare(ClothColor(bgr=cloth_bgr, hue=cloth.get("Input_Hue")))
#     expert.declare(SkinInfo(undertone=skin_undertone))
#     expert.run()

#     PATH_HANDLERS[expert.path](expert, cloth, skin_undertone)


# if __name__ == "__main__":
#     main()
# ==========================================================
# إصلاح توافق experta مع بايثون 3.10+ (تمت إزالة collections.Mapping)
# ==========================================================

import collections
import collections.abc
if not hasattr(collections, "Mapping"):
    collections.Mapping = collections.abc.Mapping

import cv2
import numpy as np
import matplotlib.pyplot as plt
from functools import reduce

from experta import KnowledgeEngine, Fact, Rule, MATCH, TEST

# ==========================================================
# باليتات محايدة (دافئ / بارد) — بيانات ثابتة، ليست قواعد قرار
# ==========================================================
NEUTRAL_12_WARM = {
    "Highlight": [(18, 20, 255), (22, 25, 240), (15, 15, 255)],
    "Base":      [(20, 60, 200), (25, 70, 180), (30, 55, 190)],
    "Sculpt":    [(15, 95, 90), (12, 110, 80), (10, 120, 70)],
    "Accent":    [(25, 80, 230), (18, 90, 210), (30, 70, 220)],
}

NEUTRAL_12_COOL = {
    "Highlight": [(160, 15, 255), (170, 20, 240), (155, 10, 255)],
    "Base":      [(165, 50, 200), (160, 40, 190), (170, 45, 180)],
    "Sculpt":    [(170, 90, 90), (160, 100, 80), (175, 110, 70)],
    "Accent":    [(165, 70, 230), (170, 80, 210), (160, 60, 220)],
}

PALETTE_BY_UNDERTONE = {"Warm": NEUTRAL_12_WARM, "Cool": NEUTRAL_12_COOL}


def get_neutral_palette_12(undertone):
    return PALETTE_BY_UNDERTONE.get(undertone, NEUTRAL_12_COOL)


# ==========================================================
# HSV → RGB وأدوات رسم عامة (بدون منطق قرار)
# ==========================================================
def hsv_to_rgb(hsv):
    hsv_img = np.uint8([[[hsv[0], hsv[1], hsv[2]]]])
    return cv2.cvtColor(hsv_img, cv2.COLOR_HSV2RGB)[0][0]


def rgb_hex_hue(rgb):
    hex_color = "#{:02X}{:02X}{:02X}".format(rgb[0], rgb[1], rgb[2])
    hsv_back = cv2.cvtColor(np.uint8([[rgb]]), cv2.COLOR_RGB2HSV)[0][0]
    return hex_color, hsv_back[0]


def style_spines(ax):
    list(map(lambda spine: (spine.set_edgecolor('#444'), spine.set_linewidth(2)), ax.spines.values()))
    return ax


def dedupe_hsv(hsv, seen, step=6, guard=30):
    """
    يرجّع (hsv, rgb) بحيث لا يتكرّر rgb (كـ tuple قابل للمقارنة) ضمن مجموعة seen.
    إن كان اللون مكررًا، يُزاح الـHue تدريجيًا عبر استدعاء الدالة لنفسها
    (بدل for/while)، مع سقف (guard) لمنع أي استدعاء ذاتي بلا نهاية.
    """
    rgb = hsv_to_rgb(hsv)
    rgb_key = tuple(int(x) for x in rgb)
    is_acceptable = (rgb_key not in seen) or guard <= 0
    return (hsv, rgb) if is_acceptable else dedupe_hsv(
        ((hsv[0] + step) % 180, hsv[1], hsv[2]), seen, step, guard - 1
    )


def render_color_cell(cell_index, hsv, rows, cols, seen):
    hsv_final, rgb = dedupe_hsv(hsv, seen)
    seen.add(tuple(int(x) for x in rgb))
    hex_color, final_hue = rgb_hex_hue(rgb)
    print(f"RGB: {rgb}   HEX: {hex_color}   Hue: {final_hue}")
    ax = plt.subplot(rows, cols, cell_index)
    ax.imshow(np.ones((150, 150, 3), dtype=np.uint8) * rgb)
    style_spines(ax)
    ax.set_xticks([])
    ax.set_yticks([])
    return rgb


def render_neutral_group(start_index, group_name, colors, rows, cols, seen):
    print(f"\n{group_name} Colors:")
    indices = range(start_index, start_index + len(colors))
    list(map(lambda pair: render_color_cell(pair[0], pair[1], rows, cols, seen), zip(indices, colors)))
    return start_index + len(colors)


def show_neutral_palette_12(palette, cloth_rgb):
    plt.figure(figsize=(10, 4))
    plt.suptitle("Makeup Shadow Palette", fontsize=18, fontweight='bold')
    plt.gcf().patch.set_facecolor('#f8f8f8')

    groups = ["Highlight", "Base", "Sculpt", "Accent"]
    rows, cols = 3, 4
    seen = set()  # يجمع كل الألوان المعروضة في هذه اللوحة لمنع التكرار
    reduce(lambda idx, group: render_neutral_group(idx, group, palette[group], rows, cols, seen), groups, 1)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show()


# ==========================================================
# قواعد الباليتات الخمس — صيغ رياضية ثابتة، تُستدعى بحسب
# اسم "transform" الذي يقرره محرك experta (وليس بـ if/elif)
# ==========================================================
UNDERTONE_TRANSFORMS = {
    "warm": lambda h, s, v: ((h + 8) % 180, min(s + 25, 255), min(v + 15, 255)),
    "cool": lambda h, s, v: ((h - 12) % 180, min(s + 35, 255), max(v - 20, 0)),
}


def apply_undertone(hsv, transform_name):
    h, s, v = hsv
    transform = UNDERTONE_TRANSFORMS.get(transform_name, lambda h, s, v: (h, s, v))  # بدون تحويل إن لم يقرر المحرك شيئًا
    h2, s2, v2 = transform(h, s, v)
    return (int(h2), int(s2), int(v2))


def mono(H, t):
    return {
        "Base":      apply_undertone((H, 70, 180), t),
        "Highlight": apply_undertone((H, 30, 255), t),
        "Sculpt":    apply_undertone((H, 95, 90), t),
    }


def analogous(H, t):
    return {
        "Base":      apply_undertone(((H + 15) % 180, 65, 185), t),
        "Highlight": apply_undertone(((H - 10) % 180, 35, 255), t),
        "Sculpt":    apply_undertone(((H + 35) % 180, 85, 80), t),
    }


def split(H, t):
    return {
        "Base":      apply_undertone(((H + 75) % 180, 60, 190), t),
        "Highlight": apply_undertone((H, 25, 255), t),
        "Sculpt":    apply_undertone(((H + 105) % 180, 90, 70), t),
    }


def triadic(H, t):
    return {
        "Base":      apply_undertone(((H + 60) % 180, 55, 175), t),
        "Highlight": apply_undertone((20, 20, 255), t),
        "Sculpt":    apply_undertone(((H - 60) % 180, 85, 75), t),
    }


def earth(H, t):
    return {
        "Base":      apply_undertone((15, 65, 160), t),
        "Highlight": apply_undertone((20, 25, 245), t),
        "Sculpt":    apply_undertone((12, 95, 60), t),
    }


PALETTE_BASE_RULES = {
    "Monochromatic": mono,
    "Analogous": analogous,
    "Split-Complementary": split,
    "Triadic": triadic,
    "Earth Colors": earth,
}


def render_strategy(strategy_index, strategy, H, transform_name, rows, cols, seen):
    palette = PALETTE_BASE_RULES[strategy](H, transform_name)
    print(f"\nPalette {strategy_index + 1}:")
    values = list(palette.values())
    base_cell = strategy_index * cols
    list(map(lambda pair: render_color_cell(base_cell + pair[0] + 1, pair[1], rows, cols, seen), enumerate(values)))
    plt.subplots_adjust(hspace=0.6)
    return strategy_index + 1


def show_all_palettes(H, transform_name, cloth_rgb):
    """
    يعرض كل الاستراتيجيات الخمس معًا دفعة واحدة (المستخدم لا يختار استراتيجية):
    كل الألوان التي تناسب الملابس تُعرض دفعة واحدة، مع ضمان عدم تكرار
    أي لون بين كل هذه اللوحات عبر مجموعة seen المشتركة.
    """
    strategies = list(PALETTE_BASE_RULES.keys())
    rows, cols = len(strategies), 3

    plt.figure(figsize=(10, 4 * rows))
    plt.suptitle("Makeup Shadow Palette", fontsize=18, fontweight='bold')
    plt.gcf().patch.set_facecolor('#f8f8f8')

    seen = set()  # يجمع كل الألوان عبر الاستراتيجيات الخمس مجتمعة لمنع أي تكرار
    reduce(lambda idx, item: render_strategy(item[0], item[1], H, transform_name, rows, cols, seen),
           enumerate(strategies), 0)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show()


# ==========================================================
#                  محرك القواعد الخبير (experta)
#   هنا فقط تمّ نقل منطق "إن ... وإلا" إلى قواعد خبير حقيقية
# ==========================================================
class ClothColor(Fact):
    """bgr: صندوق BGR المهيمن للملابس (أو None) — hue: قيمة Input_Hue إن وُجدت"""
    pass


class SkinInfo(Fact):
    """undertone: 'Warm' أو 'Cool' كما اكتُشف من skin_analysis"""
    pass


class MakeupExpert(KnowledgeEngine):
    """
    محرك قرار خبير: يستقبل حقائق (لون الملابس + أندرتون البشرة)
    ويُصدر قرارين عبر إطلاق القواعد بدل if/elif:
      - self.path        : 'neutral' أو 'colored'
      - self.reason       : سبب القرار (لتوليد نفس رسائل الطباعة الأصلية)
      - self.hue          : Hue المستخدم إن كان المسار 'colored'
      - self.transform    : 'warm' أو 'cool' أو None (تُستخدم في apply_undertone)
    """

    def __init__(self):
        super().__init__()
        self.path = None
        self.reason = None
        self.hue = None
        self.transform = None

    # ---------- قواعد كشف حالة لون الملابس ----------
    @Rule(ClothColor(bgr=None))
    def rule_missing_color(self):
        self.path, self.reason = "neutral", "missing"

    @Rule(ClothColor(bgr=MATCH.bgr),
          TEST(lambda bgr: bgr is not None and bgr[0] < 40 and bgr[1] < 40 and bgr[2] < 40))
    def rule_black_detected(self, bgr):
        self.path, self.reason = "neutral", "black"

    @Rule(ClothColor(bgr=MATCH.bgr),
          TEST(lambda bgr: bgr is not None and bgr[0] > 220 and bgr[1] > 220 and bgr[2] > 220))
    def rule_white_detected(self, bgr):
        self.path, self.reason = "neutral", "white"

    @Rule(ClothColor(bgr=MATCH.bgr, hue=MATCH.hue),
          TEST(lambda bgr: bgr is not None
               and not (bgr[0] < 40 and bgr[1] < 40 and bgr[2] < 40)
               and not (bgr[0] > 220 and bgr[1] > 220 and bgr[2] > 220)))
    def rule_colored_detected(self, bgr, hue):
        self.path, self.reason, self.hue = "colored", "colored", hue

    # ---------- قواعد اختيار تحويل الأندرتون ----------
    @Rule(SkinInfo(undertone="Warm"))
    def rule_warm_undertone(self):
        self.transform = "warm"

    @Rule(SkinInfo(undertone="Cool"))
    def rule_cool_undertone(self):
        self.transform = "cool"


def run_neutral_path(reason, skin_undertone):
    messages = {
        "missing": "⚠️ No dominant_bgr detected → using neutral palette",
        "black":   "⚠️ Neutral color detected → generating 12-color palette",
        "white":   "⚠️ Neutral color detected → generating 12-color palette",
    }
    print(messages[reason])
    cloth_rgb = np.array([200, 200, 200], dtype=np.uint8)
    palette12 = get_neutral_palette_12(skin_undertone)
    show_neutral_palette_12(palette12, cloth_rgb)


def run_colored_path(hue, cloth_bgr, transform_name, skin_undertone):
    cloth_rgb = np.array(cloth_bgr[::-1], dtype=np.uint8)
    print("Detected Undertone:", skin_undertone)
    print("Detected Clothing Hue:", hue)
    show_all_palettes(hue, transform_name, cloth_rgb)


PATH_HANDLERS = {
    "neutral": lambda expert, cloth, skin_undertone: run_neutral_path(expert.reason, skin_undertone),
    "colored": lambda expert, cloth, skin_undertone: run_colored_path(
        expert.hue, cloth.get("dominant_bgr"), expert.transform, skin_undertone),
}


def main():
    from skin_analysis import analyze_skin
    from clothing_hue_extractor import analyze_clothing_color

    img = cv2.imread("pictures3/warm.jpg")
    assert img is not None, "❌ الصورة غير موجودة أو المسار غير صحيح"

    skin_data = analyze_skin(img)
    skin_undertone = skin_data["undertone"]

    cloth = analyze_clothing_color("pictures4/photo_2026-07-14_09-06-46.jpg")
    cloth_bgr = cloth.get("dominant_bgr", None)

    # --- تشغيل محرك القواعد الخبير ---
    expert = MakeupExpert()
    expert.reset()
    expert.declare(ClothColor(bgr=cloth_bgr, hue=cloth.get("Input_Hue")))
    expert.declare(SkinInfo(undertone=skin_undertone))
    expert.run()

    PATH_HANDLERS[expert.path](expert, cloth, skin_undertone)


if __name__ == "__main__":
    main()
