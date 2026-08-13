

# # # import collections
# # # import collections.abc
# # # if not hasattr(collections, "Mapping"):
# # #     collections.Mapping = collections.abc.Mapping

# # # import cv2
# # # import numpy as np
# # # import matplotlib.pyplot as plt
# # # from functools import reduce

# # # from experta import KnowledgeEngine, Fact, Rule, MATCH, TEST

# # # # ==========================================================
# # # # باليتات محايدة (دافئ / بارد) — بيانات ثابتة، ليست قواعد قرار
# # # # ==========================================================
# # # NEUTRAL_12_WARM = {
# # #     "Highlight": [(18, 20, 255), (22, 25, 240), (15, 15, 255)],
# # #     "Base":      [(20, 60, 200), (25, 70, 180), (30, 55, 190)],
# # #     "Sculpt":    [(15, 95, 90), (12, 110, 80), (10, 120, 70)],
# # #     "Accent":    [(25, 80, 230), (18, 90, 210), (30, 70, 220)],
# # # }

# # # NEUTRAL_12_COOL = {
# # #     "Highlight": [(160, 15, 255), (170, 20, 240), (155, 10, 255)],
# # #     "Base":      [(165, 50, 200), (160, 40, 190), (170, 45, 180)],
# # #     "Sculpt":    [(170, 90, 90), (160, 100, 80), (175, 110, 70)],
# # #     "Accent":    [(165, 70, 230), (170, 80, 210), (160, 60, 220)],
# # # }

# # # PALETTE_BY_UNDERTONE = {"Warm": NEUTRAL_12_WARM, "Cool": NEUTRAL_12_COOL}


# # # def get_neutral_palette_12(undertone):
# # #     return PALETTE_BY_UNDERTONE.get(undertone, NEUTRAL_12_COOL)


# # # # ==========================================================
# # # # HSV → RGB وأدوات رسم عامة (بدون منطق قرار)
# # # # ==========================================================
# # # def hsv_to_rgb(hsv):
# # #     hsv_img = np.uint8([[[hsv[0], hsv[1], hsv[2]]]])
# # #     return cv2.cvtColor(hsv_img, cv2.COLOR_HSV2RGB)[0][0]


# # # def rgb_hex_hue(rgb):
# # #     hex_color = "#{:02X}{:02X}{:02X}".format(rgb[0], rgb[1], rgb[2])
# # #     hsv_back = cv2.cvtColor(np.uint8([[rgb]]), cv2.COLOR_RGB2HSV)[0][0]
# # #     return hex_color, hsv_back[0]


# # # def style_spines(ax):
# # #     list(map(lambda spine: (spine.set_edgecolor('#444'), spine.set_linewidth(2)), ax.spines.values()))
# # #     return ax


# # # # ==========================================================
# # # # منع تكرار الألوان — بأولوية تعديل V ثم S (يحافظ على العائلة اللونية)
# # # # وسقف صغير جدًا لتحريك الـ Hue (حتى ما ينقلب اللون لعائلة تانية)
# # # # ==========================================================
# # # def color_distance(rgb1, rgb2):
# # #     return sum((int(a) - int(b)) ** 2 for a, b in zip(rgb1, rgb2)) ** 0.5


# # # def _is_far_enough(rgb, seen, min_distance):
# # #     return all(color_distance(rgb, prev) >= min_distance for prev in seen)

# # # def dedupe_hsv(hsv, seen, min_distance=35):
# # #     h, s, v = hsv
# # #     rgb = hsv_to_rgb(hsv)
# # #     for prev in seen:
# # #         if np.linalg.norm(np.array(rgb) - np.array(prev)) < min_distance:
# # #             v = max(30, min(255, v + 25))
# # #             s = max(20, min(255, s + 15))
# # #             rgb = hsv_to_rgb((h, s, v))
# # #     return (h, s, v), rgb

# # # def render_color_cell(cell_index, hsv, rows, cols, seen):
# # #     hsv_final, rgb = dedupe_hsv(hsv, seen)
# # #     seen.add(tuple(int(x) for x in rgb))
# # #     hex_color, final_hue = rgb_hex_hue(rgb)
# # #     print(f"RGB: {rgb}   HEX: {hex_color}   Hue: {final_hue}")
# # #     ax = plt.subplot(rows, cols, cell_index)
# # #     ax.imshow(np.ones((150, 150, 3), dtype=np.uint8) * rgb)
# # #     style_spines(ax)
# # #     ax.set_xticks([])
# # #     ax.set_yticks([])
# # #     return rgb


# # # def render_neutral_group(start_index, group_name, colors, rows, cols, seen):
# # #     print(f"\n{group_name} Colors:")
# # #     indices = range(start_index, start_index + len(colors))
# # #     list(map(lambda pair: render_color_cell(pair[0], pair[1], rows, cols, seen), zip(indices, colors)))
# # #     return start_index + len(colors)


# # # def show_neutral_palette_12(palette, cloth_rgb):
# # #     plt.figure(figsize=(10, 4))
# # #     plt.suptitle("Makeup Shadow Palette", fontsize=18, fontweight='bold')
# # #     plt.gcf().patch.set_facecolor('#f8f8f8')

# # #     groups = ["Highlight", "Base", "Sculpt", "Accent"]
# # #     rows, cols = 3, 4
# # #     seen = set()  # يجمع كل الألوان المعروضة في هذه اللوحة لمنع التكرار
# # #     reduce(lambda idx, group: render_neutral_group(idx, group, palette[group], rows, cols, seen), groups, 1)

# # #     plt.tight_layout(rect=[0, 0, 1, 0.95])
# # #     plt.show()


# # # # ==========================================================
# # # # قواعد الباليتات الخمس — صيغ رياضية ثابتة + "غلاف دور" موحّد
# # # # تُستدعى بحسب اسم "transform" الذي يقرره محرك experta (وليس بـ if/elif)
# # # # ==========================================================

# # # # UNDERTONE_TRANSFORMS = {
# # # #     "warm": lambda h, s, v: ((h + 8) % 180, min(s + 15, 200), min(v + 15, 245)),
# # # #     "cool": lambda h, s, v: ((h - 12) % 180, min(s + 20, 190), max(v - 15, 45)),
# # # # }

# # # UNDERTONE_TRANSFORMS = {
# # #     "warm": lambda h, s, v: ((h + 5) % 180, min(s + 20, 255), min(v + 15, 255)),
# # #     "cool": lambda h, s, v: ((h - 5) % 180, max(s - 15, 0), max(v - 10, 0)),
# # # }
# # # # def apply_undertone(hsv, transform_name):
# # # #     h, s, v = hsv
# # # #     if transform_name == "warm":
# # # #         # دافئ: خوخي، ذهبي، برونزي
# # # #         h2 = (h + 6) % 180
# # # #         s2 = min(s + 30, 255)
# # # #         v2 = min(v + 25, 255)
# # # #     elif transform_name == "cool":
# # # #         # بارد: Mauve، Rose، Silver
# # # #         h2 = (h - 8) % 180
# # # #         s2 = max(s - 25, 0)
# # # #         v2 = max(v - 20, 0)
# # # #     else:
# # # #         h2, s2, v2 = h, s, v
# # # #     return (int(h2), int(s2), int(v2))
# # # def apply_undertone(hsv, transform_name):
# # #     h, s, v = hsv
# # #     if transform_name == "warm":
# # #         # دافئ: خوخي، ذهبي، برونزي
# # #         if 0 <= h <= 30 or 150 <= h <= 180:
# # #             h2 = (h + 5) % 180
# # #         else:
# # #             h2 = (h + 10) % 180
# # #         s2 = min(s + 35, 255)
# # #         v2 = min(v + 25, 255)
# # #     elif transform_name == "cool":
# # #         # بارد: Mauve، Rose، Silver
# # #         if 0 <= h <= 30 or 150 <= h <= 180:
# # #             h2 = (h - 10) % 180
# # #         else:
# # #             h2 = (h - 5) % 180
# # #         s2 = max(s - 25, 0)
# # #         v2 = max(v - 20, 0)
# # #     else:
# # #         h2, s2, v2 = h, s, v
# # #     return (int(h2), int(s2), int(v2))


# # # def hue_circular_distance(h1, h2, wheel=180):
# # #     """أقصر مسافة بين زاويتين على عجلة الألوان (بدل الطرح المباشر)."""
# # #     d = abs(h1 - h2) % wheel
# # #     return min(d, wheel - d)


# # # def clamp(value, lo, hi):
# # #     return max(lo, min(hi, value))


# # # # حدود S/V لكل دور — هيدا يلي بيضمن الإحساس الموحّد (Highlight فاتح دايمًا،
# # # # Base متوسط، Sculpt غامق) بغض النظر عن الاستراتيجية أو زاوية اللون
# # # ROLE_ENVELOPE = {
# # #     "Highlight": {"s": (15, 45), "v": (225, 255)},
# # #     "Base":      {"s": (40, 90), "v": (150, 205)},
# # #     "Sculpt":    {"s": (50, 100), "v": (45, 95)},
# # # }


# # # def apply_role_envelope(hsv, role, hue_distance_from_input):
# # #     """
# # #     يحصر S وV ضمن مجال الدور، ويخفّف التشبع تلقائيًا كل ما كانت
# # #     الزاوية بعيدة عن لون الملابس الأصلي (متل ألوان split/triadic
# # #     المتكاملة) — هيك بتصير درجة أنيقة مطفية بدل لون نيون فاقع.
# # #     """
# # #     h, s, v = hsv
# # #     lo_s, hi_s = ROLE_ENVELOPE[role]["s"]
# # #     lo_v, hi_v = ROLE_ENVELOPE[role]["v"]

# # #     mute_factor = 1.0
# # #     if hue_distance_from_input > 60:
# # #         mute_factor = 0.72
# # #     elif hue_distance_from_input > 30:
# # #         mute_factor = 0.88

# # #     s2 = clamp(s * mute_factor, lo_s, hi_s)
# # #     v2 = clamp(v, lo_v, hi_v)
# # #     return (int(h), int(s2), int(v2))


# # # def build_role(hue, s, v, role, input_hue, transform_name):
# # #     """يبني لون الدور: يطبّق الأندرتون، ثم يحصره بغلاف الدور مع التخفيف التلقائي."""
# # #     h2, s2, v2 = apply_undertone((hue, s, v), transform_name)
# # #     dist = hue_circular_distance(h2, input_hue)
# # #     return apply_role_envelope((h2, s2, v2), role, dist)
# # # def mono(H, t):
# # #     return {
# # #         "Base":      apply_undertone((H, 60, 190), t),
# # #         "Highlight": apply_undertone((H, 30, 255), t),
# # #         "Sculpt":    apply_undertone((H, 85, 85), t),
# # #     }

# # # def analogous(H, t):
# # #     return {
# # #         "Base":      apply_undertone(((H + 10) % 180, 65, 185), t),
# # #         "Highlight": apply_undertone(((H - 5) % 180, 40, 250), t),
# # #         "Sculpt":    apply_undertone(((H + 20) % 180, 90, 80), t),
# # #     }

# # # def split(H, t):
# # #     return {
# # #         "Base":      apply_undertone(((H + 15) % 180, 55, 180), t),
# # #         "Highlight": apply_undertone((H, 25, 255), t),
# # #         "Sculpt":    apply_undertone(((H + 25) % 180, 95, 75), t),
# # #     }

# # # def triadic(H, t):
# # #     return {
# # #         "Base":      apply_undertone(((H + 8) % 180, 55, 185), t),
# # #         "Highlight": apply_undertone(((H + 2) % 180, 35, 255), t),
# # #         "Sculpt":    apply_undertone(((H + 15) % 180, 75, 80), t),
# # #     }

# # # def earth(H, t):
# # #     return {
# # #         "Base":      apply_undertone((H, 50, 175), t),
# # #         "Highlight": apply_undertone((H, 25, 255), t),
# # #         "Sculpt":    apply_undertone((H, 70, 75), t),
# # #     }


# # # PALETTE_BASE_RULES = {
# # #     "Monochromatic": mono,
# # #     "Analogous": analogous,
# # #     "Split-Complementary": split,
# # #     "Triadic": triadic,
# # #     "Earth Colors": earth,
# # # }


# # # def render_strategy(strategy_index, strategy, H, transform_name, rows, cols, seen):
# # #     palette = PALETTE_BASE_RULES[strategy](H, transform_name)
# # #     print(f"\nPalette {strategy_index + 1}:")
# # #     values = list(palette.values())
# # #     base_cell = strategy_index * cols
# # #     list(map(lambda pair: render_color_cell(base_cell + pair[0] + 1, pair[1], rows, cols, seen), enumerate(values)))
# # #     plt.subplots_adjust(hspace=0.6)
# # #     return strategy_index + 1


# # # def show_all_palettes(H, transform_name, cloth_rgb):
# # #     """
# # #     يعرض كل الاستراتيجيات الخمس معًا دفعة واحدة (المستخدم لا يختار استراتيجية):
# # #     كل الألوان التي تناسب الملابس تُعرض دفعة واحدة، مع ضمان عدم تكرار
# # #     أي لون بين كل هذه اللوحات عبر مجموعة seen المشتركة.
# # #     """
# # #     strategies = list(PALETTE_BASE_RULES.keys())
# # #     rows, cols = len(strategies), 3

# # #     plt.figure(figsize=(10, 4 * rows))
# # #     plt.suptitle("Makeup Shadow Palette", fontsize=18, fontweight='bold')
# # #     plt.gcf().patch.set_facecolor('#f8f8f8')

# # #     seen = set()  # يجمع كل الألوان عبر الاستراتيجيات الخمس مجتمعة لمنع أي تكرار
# # #     reduce(lambda idx, item: render_strategy(item[0], item[1], H, transform_name, rows, cols, seen),
# # #            enumerate(strategies), 0)

# # #     plt.tight_layout(rect=[0, 0, 1, 0.95])
# # #     plt.show()


# # # # ==========================================================
# # # #                  محرك القواعد الخبير (experta)
# # # #   هنا فقط تمّ نقل منطق "إن ... وإلا" إلى قواعد خبير حقيقية
# # # # ==========================================================
# # # class ClothColor(Fact):
# # #     """bgr: صندوق BGR المهيمن للملابس (أو None) — hue: قيمة Input_Hue إن وُجدت"""
# # #     pass


# # # class SkinInfo(Fact):
# # #     """undertone: 'Warm' أو 'Cool' كما اكتُشف من skin_analysis"""
# # #     pass


# # # class MakeupExpert(KnowledgeEngine):
# # #     """
# # #     محرك قرار خبير: يستقبل حقائق (لون الملابس + أندرتون البشرة)
# # #     ويُصدر قرارين عبر إطلاق القواعد بدل if/elif:
# # #       - self.path        : 'neutral' أو 'colored'
# # #       - self.reason       : سبب القرار (لتوليد نفس رسائل الطباعة الأصلية)
# # #       - self.hue          : Hue المستخدم إن كان المسار 'colored'
# # #       - self.transform    : 'warm' أو 'cool' أو None (تُستخدم في apply_undertone)
# # #     """

# # #     def __init__(self):
# # #         super().__init__()
# # #         self.path = None
# # #         self.reason = None
# # #         self.hue = None
# # #         self.transform = None

# # #     # ---------- قواعد كشف حالة لون الملابس ----------
# # #     @Rule(ClothColor(bgr=None))
# # #     def rule_missing_color(self):
# # #         self.path, self.reason = "neutral", "missing"

# # #     @Rule(ClothColor(bgr=MATCH.bgr),
# # #           TEST(lambda bgr: bgr is not None and bgr[0] < 40 and bgr[1] < 40 and bgr[2] < 40))
# # #     def rule_black_detected(self, bgr):
# # #         self.path, self.reason = "neutral", "black"

# # #     @Rule(ClothColor(bgr=MATCH.bgr),
# # #           TEST(lambda bgr: bgr is not None and bgr[0] > 220 and bgr[1] > 220 and bgr[2] > 220))
# # #     def rule_white_detected(self, bgr):
# # #         self.path, self.reason = "neutral", "white"

# # #     @Rule(ClothColor(bgr=MATCH.bgr, hue=MATCH.hue),
# # #           TEST(lambda bgr: bgr is not None
# # #                and not (bgr[0] < 40 and bgr[1] < 40 and bgr[2] < 40)
# # #                and not (bgr[0] > 220 and bgr[1] > 220 and bgr[2] > 220)))
# # #     def rule_colored_detected(self, bgr, hue):
# # #         self.path, self.reason, self.hue = "colored", "colored", hue

# # #     # ---------- قواعد اختيار تحويل الأندرتون ----------
# # #     @Rule(SkinInfo(undertone="Warm"))
# # #     def rule_warm_undertone(self):
# # #         self.transform = "warm"

# # #     @Rule(SkinInfo(undertone="Cool"))
# # #     def rule_cool_undertone(self):
# # #         self.transform = "cool"


# # # def run_neutral_path(reason, skin_undertone):
# # #     messages = {
# # #         "missing": "⚠️ No dominant_bgr detected → using neutral palette",
# # #         "black":   "⚠️ Neutral color detected → generating 12-color palette",
# # #         "white":   "⚠️ Neutral color detected → generating 12-color palette",
# # #     }
# # #     print(messages[reason])
# # #     cloth_rgb = np.array([200, 200, 200], dtype=np.uint8)
# # #     palette12 = get_neutral_palette_12(skin_undertone)
# # #     show_neutral_palette_12(palette12, cloth_rgb)


# # # def run_colored_path(hue, cloth_bgr, transform_name, skin_undertone):
# # #     cloth_rgb = np.array(cloth_bgr[::-1], dtype=np.uint8)
# # #     print("Detected Undertone:", skin_undertone)
# # #     print("Detected Clothing Hue:", hue)
# # #     show_all_palettes(hue, transform_name, cloth_rgb)


# # # PATH_HANDLERS = {
# # #     "neutral": lambda expert, cloth, skin_undertone: run_neutral_path(expert.reason, skin_undertone),
# # #     "colored": lambda expert, cloth, skin_undertone: run_colored_path(
# # #         expert.hue, cloth.get("dominant_bgr"), expert.transform, skin_undertone),
# # # }


# # # def main():
# # #     from skin_analysis import analyze_skin_from_image_dict as analyze_skin
# # #     from clothing_hue_extractor import analyze_clothing_color

# # #     face_img_path = "pictures3/warm.jpg"
# # #     skin_data = analyze_skin(face_img_path)
# # #     skin_undertone = skin_data.get("undertone", "Warm")

# # #     cloth = analyze_clothing_color("pictures4/photo_2026-07-15_16-06-32.jpg")
# # #     print("Clothing analysis result:", cloth)

# # #     cloth_bgr = cloth.get("dominant_bgr", None)

# # #     expert = MakeupExpert()
# # #     expert.reset()
# # #     expert.declare(ClothColor(bgr=cloth_bgr, hue=cloth.get("Input_Hue")))
# # #     expert.declare(SkinInfo(undertone=skin_undertone))
# # #     expert.run()

# # #     PATH_HANDLERS[expert.path](expert, cloth, skin_undertone)


# # # if __name__ == "__main__":
# # #     main()
# # import cv2
# # import numpy as np
# # import matplotlib.pyplot as plt

# # def detect_neutral_color(bgr):
# #     b, g, r = bgr

# #     # أسود صريح
# #     if b < 40 and g < 40 and r < 40:
# #         return "black"

# #     # أبيض صريح
# #     if b > 220 and g > 220 and r > 220:
# #         return "white"

# #     # غير ذلك → ليس محايداً
# #     return None

# # # ==========================================================
# # # باليت لون للبشرة الدافئة
# # # ==========================================================
# # NEUTRAL_12_WARM = {
# #     "Highlight": [
# #         (18, 20, 255),
# #         (22, 25, 240),
# #         (15, 15, 255)
# #     ],
# #     "Base": [
# #         (20, 60, 200),
# #         (25, 70, 180),
# #         (30, 55, 190)
# #     ],
# #     "Sculpt": [
# #         (15, 95, 90),
# #         (12, 110, 80),
# #         (10, 120, 70)
# #     ],
# #     "Accent": [
# #         (25, 80, 230),
# #         (18, 90, 210),
# #         (30, 70, 220)
# #     ]
# # }

# # # ==========================================================
# # # باليت لون للبشرة الباردة
# # # ==========================================================
# # NEUTRAL_12_COOL = {
# #     "Highlight": [
# #         (160, 15, 255),
# #         (170, 20, 240),
# #         (155, 10, 255)
# #     ],
# #     "Base": [
# #         (165, 50, 200),
# #         (160, 40, 190),
# #         (170, 45, 180)
# #     ],
# #     "Sculpt": [
# #         (170, 90, 90),
# #         (160, 100, 80),
# #         (175, 110, 70)
# #     ],
# #     "Accent": [
# #         (165, 70, 230),
# #         (170, 80, 210),
# #         (160, 60, 220)
# #     ]
# # }

# # def get_neutral_palette_12(undertone):
# #     return NEUTRAL_12_WARM if undertone == "Warm" else NEUTRAL_12_COOL

# # # ==========================================================
# # # HSV → RGB
# # # ==========================================================
# # def hsv_to_rgb(hsv):
# #     hsv_img = np.uint8([[[hsv[0], hsv[1], hsv[2]]]])
# #     return cv2.cvtColor(hsv_img, cv2.COLOR_HSV2RGB)[0][0]

# # # ==========================================================
# # # عرض باليت 12 لون
# # # ==========================================================
# # def show_neutral_palette_12(palette, cloth_rgb):
# #     plt.figure(figsize=(10, 4))
# #     plt.suptitle("Makeup Shadow Palette", fontsize=18, fontweight='bold')

# #     plt.gcf().patch.set_facecolor('#f8f8f8')

# #     groups = ["Highlight", "Base", "Sculpt", "Accent"]
# #     idx = 1

# #     for group in groups:
# #         print(f"\n{group} Colors:")

# #         for hsv in palette[group]:
# #             rgb = hsv_to_rgb(hsv)

# #             # HEX
# #             hex_color = "#{:02X}{:02X}{:02X}".format(rgb[0], rgb[1], rgb[2])

# #             # Hue 
# #             hsv_back = cv2.cvtColor(np.uint8([[rgb]]), cv2.COLOR_RGB2HSV)[0][0]
# #             final_hue = hsv_back[0]

# #             print(f"RGB: {rgb}   HEX: {hex_color}   Hue: {final_hue}")

# #             ax = plt.subplot(3, 4, idx)
# #             ax.imshow(np.ones((150,150,3), dtype=np.uint8) * rgb)

# #             for spine in ax.spines.values():
# #                 spine.set_edgecolor('#444')
# #                 spine.set_linewidth(2)

# #             ax.set_xticks([])
# #             ax.set_yticks([])
# #             idx += 1

# #     plt.tight_layout(rect=[0, 0, 1, 0.95])
# #     plt.show()

# # # ==========================================================
# # # تأثير الأندرتون
# # # ==========================================================
# # def apply_undertone(hsv, undertone):
# #     h, s, v = hsv

# #     if undertone == "Warm":
# #         h = (h + 8) % 180
# #         s = min(s + 25, 255)
# #         v = min(v + 15, 255)

# #     elif undertone == "Cool":
# #         h = (h - 12) % 180
# #         s = min(s + 35, 255)
# #         v = max(v - 20, 0)

# #     return (int(h), int(s), int(v))

# # # ==========================================================
# # # قواعد الباليت 
# # # ==========================================================
# # def mono(H, u):
# #     return {
# #         "Base":      apply_undertone((H, 70, 180), u),
# #         "Highlight": apply_undertone((H, 30, 255), u),
# #         "Sculpt":    apply_undertone((H, 95, 90), u),
# #     }

# # def analogous(H, u):
# #     return {
# #         "Base":      apply_undertone(((H + 15) % 180, 65, 185), u),
# #         "Highlight": apply_undertone(((H - 10) % 180, 35, 255), u),
# #         "Sculpt":    apply_undertone(((H + 35) % 180, 85, 80), u),
# #     }

# # def split(H, u):
# #     return {
# #         "Base":      apply_undertone(((H + 75) % 180, 60, 190), u),
# #         "Highlight": apply_undertone((H, 25, 255), u),
# #         "Sculpt":    apply_undertone(((H + 105) % 180, 90, 70), u),
# #     }

# # def triadic(H, u):
# #     return {
# #         "Base":      apply_undertone(((H + 60) % 180, 55, 175), u),
# #         "Highlight": apply_undertone((20, 20, 255), u),
# #         "Sculpt":    apply_undertone(((H - 60) % 180, 85, 75), u),
# #     }

# # def earth(H, u):
# #     return {
# #         "Base":      apply_undertone((15, 65, 160), u),
# #         "Highlight": apply_undertone((20, 25, 245), u),
# #         "Sculpt":    apply_undertone((12, 95, 60), u),
# #     }

# # PALETTE_BASE_RULES = {
# #     "Monochromatic": mono,
# #     "Analogous": analogous,
# #     "Split-Complementary": split,
# #     "Triadic": triadic,
# #     "Earth Colors": earth
# # }

# # # ==========================================================
# # # عرض جميع الاستراتيجيات
# # # ==========================================================
# # def show_all_palettes(H, skin_undertone, cloth_rgb):
# #     strategies = list(PALETTE_BASE_RULES.keys())

# #     plt.figure(figsize=(10, 4 * len(strategies)))
# #     plt.suptitle("Makeup Shadow Palette", fontsize=18, fontweight='bold')

# #     plt.gcf().patch.set_facecolor('#f8f8f8')

# #     for idx, strategy in enumerate(strategies):
# #         palette = PALETTE_BASE_RULES[strategy](H, skin_undertone)

# #         print(f"\nPalette {idx+1}:")

# #         for i, (_, hsv) in enumerate(palette.items()):
# #             rgb_p = hsv_to_rgb(hsv)

# #             hex_color = "#{:02X}{:02X}{:02X}".format(rgb_p[0], rgb_p[1], rgb_p[2])

# #             hsv_back = cv2.cvtColor(np.uint8([[rgb_p]]), cv2.COLOR_RGB2HSV)[0][0]
# #             final_hue = hsv_back[0]

# #             print(f"RGB: {rgb_p}   HEX: {hex_color}   Hue: {final_hue}")

# #             ax = plt.subplot(len(strategies), 3, idx * 3 + i + 1)
# #             ax.imshow(np.ones((150,150,3), dtype=np.uint8) * rgb_p)

# #             for spine in ax.spines.values():
# #                 spine.set_edgecolor('#444')
# #                 spine.set_linewidth(2)

# #             ax.set_xticks([])
# #             ax.set_yticks([])

# #         plt.subplots_adjust(hspace=0.6)

# #     plt.tight_layout(rect=[0, 0, 1, 0.95])
# #     plt.show()

# # # ==========================================================
# # # تشغيل كامل
# # # ==========================================================
# # if __name__ == "__main__":
# #     from skin_analysis import analyze_skin_from_image_dict as analyze_skin
# #     from clothing_hue_extractor import analyze_clothing_color

# #     img = cv2.imread("pictures3/warm.jpg")
# #     if img is None:
# #         raise ValueError("❌ الصورة غير موجودة أو المسار غير صحيح")

# #     skin_data = analyze_skin("pictures3/warm.jpg")
# #     skin_undertone = skin_data["undertone"]

# #     cloth = analyze_clothing_color("pictures4/photo_2026-07-17_15-46-20.jpg")

# #     cloth_bgr = cloth.get("dominant_bgr", None)

# #     if cloth_bgr is None:
# #         print("⚠️ No dominant_bgr detected → using neutral palette")
# #         cloth_rgb = np.array([200, 200, 200], dtype=np.uint8)
# #         palette12 = get_neutral_palette_12(skin_undertone)
# #         show_neutral_palette_12(palette12, cloth_rgb)
# #         exit()

# #     neutral_type = detect_neutral_color(cloth_bgr)

# #     if neutral_type is not None:
# #         print("⚠️ Neutral color detected → generating 12-color palette")
# #         cloth_rgb = np.array([200, 200, 200], dtype=np.uint8)
# #         palette12 = get_neutral_palette_12(skin_undertone)
# #         show_neutral_palette_12(palette12, cloth_rgb)
# #         exit()

# #     H = cloth["Input_Hue"]
# #     cloth_rgb = np.array(cloth_bgr[::-1], dtype=np.uint8)

# #     print("Detected Undertone:", skin_undertone)
# #     print("Detected Clothing Hue:", H)

# #     show_all_palettes(H, skin_undertone, cloth_rgb)

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
# # باليتات محايدة (دافئ / بارد)
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
# # أدوات تحويل الألوان وإلغاء التكرار
# # ==========================================================
# def hsv_to_rgb(hsv):
#     hsv_img = np.uint8([[[hsv[0], hsv[1], hsv[2]]]])
#     return cv2.cvtColor(hsv_img, cv2.COLOR_HSV2RGB)[0][0]

# def color_distance(rgb1, rgb2):
#     """حساب المسافة بين لونين في الفضاء اللوني RGB"""
#     return np.linalg.norm(np.array(rgb1, dtype=float) - np.array(rgb2, dtype=float))

# def dedupe_hsv(hsv, seen, min_distance=30):
#     """
#     تعديل درجة السطوع V والتشبع S لمنع التكرار والابتعاد عن الألوان السابقة
#     مع الحفاظ على العائلة اللونية Hue
#     """
#     h, s, v = hsv
#     rgb = hsv_to_rgb((h, s, v))
    
#     # محاولة تعديل اللون إذا كان قريباً جداً من أي لون سابق
#     attempts = 0
#     while any(color_distance(rgb, prev) < min_distance for prev in seen) and attempts < 10:
#         v = (v + 30) if v <= 200 else (v - 30)
#         s = (s + 20) if s <= 220 else (s - 20)
#         v = int(np.clip(v, 30, 255))
#         s = int(np.clip(s, 20, 255))
#         rgb = hsv_to_rgb((h, s, v))
#         attempts += 1
        
#     return (h, s, v), rgb

# # ==========================================================
# # عرض باليت 12 لون (بدون تكرار)
# # ==========================================================
# def show_neutral_palette_12(palette, cloth_rgb):
#     plt.figure(figsize=(10, 4))
#     plt.suptitle("Makeup Shadow Palette", fontsize=18, fontweight='bold')
#     plt.gcf().patch.set_facecolor('#f8f8f8')

#     groups = ["Highlight", "Base", "Sculpt", "Accent"]
#     idx = 1
#     seen = set()  # تتبع الألوان الظاهرة لمنع التكرار

#     for group in groups:
#         print(f"\n{group} Colors:")

#         for hsv in palette[group]:
#             _, rgb = dedupe_hsv(hsv, seen)
#             seen.add(tuple(map(int, rgb)))

#             hex_color = "#{:02X}{:02X}{:02X}".format(rgb[0], rgb[1], rgb[2])
#             hsv_back = cv2.cvtColor(np.uint8([[rgb]]), cv2.COLOR_RGB2HSV)[0][0]
#             final_hue = hsv_back[0]

#             print(f"RGB: {rgb}   HEX: {hex_color}   Hue: {final_hue}")

#             ax = plt.subplot(3, 4, idx)
#             ax.imshow(np.ones((150, 150, 3), dtype=np.uint8) * rgb)

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
# # قواعد الباليتات
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

# def show_all_palettes(H, skin_undertone, cloth_rgb):
#     strategies = list(PALETTE_BASE_RULES.keys())

#     plt.figure(figsize=(10, 4 * len(strategies)))
#     plt.suptitle("Makeup Shadow Palette", fontsize=18, fontweight='bold')
#     plt.gcf().patch.set_facecolor('#f8f8f8')

#     seen = set() 
#     for idx, strategy in enumerate(strategies):
#         palette = PALETTE_BASE_RULES[strategy](H, skin_undertone)
#         print(f"\nPalette {idx+1}:")

#         for i, (_, hsv) in enumerate(palette.items()):
#             # فحص ومنع التكرار
#             _, rgb_p = dedupe_hsv(hsv, seen, min_distance=30)
#             seen.add(tuple(map(int, rgb_p)))

#             hex_color = "#{:02X}{:02X}{:02X}".format(rgb_p[0], rgb_p[1], rgb_p[2])
#             hsv_back = cv2.cvtColor(np.uint8([[rgb_p]]), cv2.COLOR_RGB2HSV)[0][0]
#             final_hue = hsv_back[0]

#             print(f"RGB: {rgb_p}   HEX: {hex_color}   Hue: {final_hue}")

#             ax = plt.subplot(len(strategies), 3, idx * 3 + i + 1)
#             ax.imshow(np.ones((150, 150, 3), dtype=np.uint8) * rgb_p)

#             for spine in ax.spines.values():
#                 spine.set_edgecolor('#444')
#                 spine.set_linewidth(2)

#             ax.set_xticks([])
#             ax.set_yticks([])

#         plt.subplots_adjust(hspace=0.6)

#     plt.tight_layout(rect=[0, 0, 1, 0.95])
#     plt.show()

# # ==========================================================
# # التشغيل الرئيسي
# # ==========================================================
# if __name__ == "__main__":
#     from skin_analysis import analyze_skin_from_image_dict as analyze_skin
#     from clothing_hue_extractor import analyze_clothing_color

#     img = cv2.imread("pictures3/cool6.jpg")
#     if img is None:
#         raise ValueError("❌ الصورة غير موجودة أو المسار غير صحيح")

#     skin_data = analyze_skin("pictures3/cool6.jpg")
#     skin_undertone = skin_data["undertone"]

#     cloth = analyze_clothing_color("pictures4/photo_2026-07-17_15-46-29.jpg.jpg")
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

#     H = cloth["Input_Hue"]
#     cloth_rgb = np.array(cloth_bgr[::-1], dtype=np.uint8)

#     print("Detected Undertone:", skin_undertone)
#     print("Detected Clothing Hue:", H)

#     show_all_palettes(H, skin_undertone, cloth_rgb)
import collections
import collections.abc
if not hasattr(collections, "Mapping"):
    collections.Mapping = collections.abc.Mapping

import cv2
import numpy as np
import matplotlib.pyplot as plt
from experta import KnowledgeEngine, Fact, Rule, MATCH, TEST

# ==========================================================
# حقائق النظام الخبير (Facts)
# ==========================================================
class ClothingFact(Fact):
    """يمثل لون وملابس المستخدم"""
    pass

class SkinFact(Fact):
    """يمثل أندرتون البشرة"""
    pass


# ==========================================================
# محرك القواعد الخبير (Experta Knowledge Engine)
# ==========================================================
class MakeupExpertEngine(KnowledgeEngine):
    
    def __init__(self):
        super().__init__()
        self.path_type = None
        self.palette_data = None
        self.skin_undertone = None
        self.cloth_rgb = None
        self.cloth_hue = 0

    # 1. قاعدة كشف غياب لون الملابس
    @Rule(ClothingFact(bgr=None))
    def rule_missing_clothing(self):
        self.path_type = "neutral_12"

    # 2. قاعدة كشف الألوان المحايدة (أسود أو أبيض)
    @Rule(ClothingFact(bgr=MATCH.bgr),
          TEST(lambda bgr: bgr is not None and ((bgr[0] < 40 and bgr[1] < 40 and bgr[2] < 40) or (bgr[0] > 220 and bgr[1] > 220 and bgr[2] > 220))))
    def rule_neutral_clothing(self, bgr):
        self.path_type = "neutral_12"

    # 3. قاعدة معالجة الألوان الملونة (غير المحايدة)
    @Rule(ClothingFact(bgr=MATCH.bgr, hue=MATCH.hue),
          SkinFact(undertone=MATCH.undertone),
          TEST(lambda bgr: bgr is not None and not ((bgr[0] < 40 and bgr[1] < 40 and bgr[2] < 40) or (bgr[0] > 220 and bgr[1] > 220 and bgr[2] > 220))))
    def rule_colored_clothing(self, bgr, hue, undertone):
        self.path_type = "colored_palettes"
        self.cloth_hue = hue
        self.skin_undertone = undertone
        self.cloth_rgb = np.array(bgr[::-1], dtype=np.uint8)


# ==========================================================
# بيانات ثابتة ودوال مساعدة (بدون منطق قرارات)
# ==========================================================
NEUTRAL_12_WARM = {
    "Highlight": [(18, 20, 255), (22, 25, 240), (15, 15, 255)],
    "Base":      [(20, 60, 200), (25, 70, 180), (30, 55, 190)],
    "Sculpt":    [(15, 95, 90), (12, 110, 80), (10, 120, 70)],
    "Accent":    [(25, 80, 230), (18, 90, 210), (30, 70, 220)]
}

NEUTRAL_12_COOL = {
    "Highlight": [(160, 15, 255), (170, 20, 240), (155, 10, 255)],
    "Base":      [(165, 50, 200), (160, 40, 190), (170, 45, 180)],
    "Sculpt":    [(170, 90, 90), (160, 100, 80), (175, 110, 70)],
    "Accent":    [(165, 70, 230), (170, 80, 210), (160, 60, 220)]
}

PALETTES_DICT = {"Warm": NEUTRAL_12_WARM, "Cool": NEUTRAL_12_COOL}

def hsv_to_rgb(hsv):
    hsv_img = np.uint8([[[hsv[0], hsv[1], hsv[2]]]])
    return cv2.cvtColor(hsv_img, cv2.COLOR_HSV2RGB)[0][0]

def color_distance(rgb1, rgb2):
    return np.linalg.norm(np.array(rgb1, dtype=float) - np.array(rgb2, dtype=float))

def dedupe_hsv(hsv, seen, min_distance=30):
    h, s, v = hsv
    rgb = hsv_to_rgb((h, s, v))
    attempts = 0
    while any(color_distance(rgb, prev) < min_distance for prev in seen) and attempts < 10:
        v = (v + 30) if v <= 200 else (v - 30)
        s = (s + 20) if s <= 220 else (s - 20)
        v = int(np.clip(v, 30, 255))
        s = int(np.clip(s, 20, 255))
        rgb = hsv_to_rgb((h, s, v))
        attempts += 1
    return (h, s, v), rgb

def apply_undertone(hsv, undertone):
    h, s, v = hsv
    transforms = {
        "Warm": ((h + 8) % 180, min(s + 25, 255), min(v + 15, 255)),
        "Cool": ((h - 12) % 180, min(s + 35, 255), max(v - 20, 0))
    }
    return tuple(map(int, transforms.get(undertone, (h, s, v))))

def generate_strategy_palettes(H, u):
    return {
        "Monochromatic": {
            "Base":      apply_undertone((H, 70, 180), u),
            "Highlight": apply_undertone((H, 30, 255), u),
            "Sculpt":    apply_undertone((H, 95, 90), u),
        },
        "Analogous": {
            "Base":      apply_undertone(((H + 15) % 180, 65, 185), u),
            "Highlight": apply_undertone(((H - 10) % 180, 35, 255), u),
            "Sculpt":    apply_undertone(((H + 35) % 180, 85, 80), u),
        },
        "Split-Complementary": {
            "Base":      apply_undertone(((H + 75) % 180, 60, 190), u),
            "Highlight": apply_undertone((H, 25, 255), u),
            "Sculpt":    apply_undertone(((H + 105) % 180, 90, 70), u),
        },
        "Triadic": {
            "Base":      apply_undertone(((H + 60) % 180, 55, 175), u),
            "Highlight": apply_undertone((20, 20, 255), u),
            "Sculpt":    apply_undertone(((H - 60) % 180, 85, 75), u),
        },
        "Earth Colors": {
            "Base":      apply_undertone((15, 65, 160), u),
            "Highlight": apply_undertone((20, 25, 245), u),
            "Sculpt":    apply_undertone((12, 95, 60), u),
        }
    }


def render_neutral_palette_12(skin_undertone):
    print("⚠️ Neutral/Missing color detected → generating 12-color palette")
    palette = PALETTES_DICT.get(skin_undertone, NEUTRAL_12_COOL)
    
    plt.figure(figsize=(10, 4))
    plt.suptitle("Makeup Shadow Palette", fontsize=18, fontweight='bold')
    plt.gcf().patch.set_facecolor('#f8f8f8')

    groups = ["Highlight", "Base", "Sculpt", "Accent"]
    seen = set()
    idx = 1

    for group in groups:
        print(f"\n{group} Colors:")
        for hsv in palette[group]:
            _, rgb = dedupe_hsv(hsv, seen)
            seen.add(tuple(map(int, rgb)))
            
            hex_color = "#{:02X}{:02X}{:02X}".format(rgb[0], rgb[1], rgb[2])
            print(f"RGB: {rgb}  HEX: {hex_color}")

            ax = plt.subplot(3, 4, idx)
            ax.imshow(np.ones((150, 150, 3), dtype=np.uint8) * rgb)
            for spine in ax.spines.values():
                spine.set_edgecolor('#444')
                spine.set_linewidth(2)
            ax.set_xticks([])
            ax.set_yticks([])
            idx += 1

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show()

def render_all_palettes(H, skin_undertone):
    print("Detected Undertone:", skin_undertone)
    print("Detected Clothing Hue:", H)

    strategies = generate_strategy_palettes(H, skin_undertone)
    
    plt.figure(figsize=(10, 4 * len(strategies)))
    plt.suptitle("Makeup Shadow Palette", fontsize=18, fontweight='bold')
    plt.gcf().patch.set_facecolor('#f8f8f8')

    seen = set()
    for idx, (strategy_name, palette) in enumerate(strategies.items()):
        print(f"\nPalette {idx+1} ({strategy_name}):")
        for i, (_, hsv) in enumerate(palette.items()):
            _, rgb_p = dedupe_hsv(hsv, seen, min_distance=30)
            seen.add(tuple(map(int, rgb_p)))

            hex_color = "#{:02X}{:02X}{:02X}".format(rgb_p[0], rgb_p[1], rgb_p[2])
            print(f"RGB: {rgb_p}  HEX: {hex_color}")

            ax = plt.subplot(len(strategies), 3, idx * 3 + i + 1)
            ax.imshow(np.ones((150, 150, 3), dtype=np.uint8) * rgb_p)
            for spine in ax.spines.values():
                spine.set_edgecolor('#444')
                spine.set_linewidth(2)
            ax.set_xticks([])
            ax.set_yticks([])

    plt.subplots_adjust(hspace=0.6)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    # plt.show()
    
    
    import os
    import uuid

    output_dir = "media1/palettes"
    os.makedirs(output_dir, exist_ok=True)

    filename = f"{uuid.uuid4()}.png"
    filepath = os.path.join(output_dir, filename)

    plt.savefig(filepath, dpi=200, bbox_inches="tight")
    plt.close()

    return filepath

if __name__ == "__main__":
    from skin_analysis import analyze_skin_from_image_dict as analyze_skin
    from clothing_hue_extractor import analyze_clothing_color

    img_path = "pictures3/cool6.jpg"
    img = cv2.imread(img_path)
    if img is None:
        raise ValueError("❌ الصورة غير موجودة أو المسار غير صحيح")

    skin_data = analyze_skin(img_path)
    skin_undertone = skin_data["undertone"]

    cloth = analyze_clothing_color("pictures4/photo_2026-07-15_16-06-32.jpg")
    cloth_bgr = cloth.get("dominant_bgr", None)
    cloth_hue = cloth.get("Input_Hue", 0)

    # تشغيل محرك القواعد الخبير لاتخاذ القرار برمجياً
    expert = MakeupExpertEngine()
    expert.reset()
    expert.declare(SkinFact(undertone=skin_undertone))
    expert.declare(ClothingFact(bgr=cloth_bgr, hue=cloth_hue))
    expert.run()

    if expert.path_type == "neutral_12":
        render_neutral_palette_12(skin_undertone)
    elif expert.path_type == "colored_palettes":
        render_all_palettes(expert.cloth_hue, expert.skin_undertone)