# -*- coding: utf-8 -*-
"""
face_makeup_rules.py — Pure Rule-Based Expert System (No if / No for)
=======================================================================
نظام خبير قائم بالكامل على جداول البحث (Lookup Tables) وقواميس الإرسال
(Dispatch Dictionaries / Lambda Dispatch) دون استخدام أي جملة "if" أو حلقة
"for" في منطق القرار (بنفس أسلوب eye_makeup_rules.py و brow_makeup_rules.py).

يغطي هذا الملف:
  1) خرائط الكونتور/البلاشر/الهاياليت حسب شكل الوجه (صفحات 9-10):
     Rectangular / Round / Oval
  2) قاعدة اختيار لون البلاشر (5 خطوات — صفحة 11-12):
     Hue range + مصفوفة أرضية (Undertone×Depth) + تعديل حسب استراتيجية
     العين + فلتر المناسبة (Texture) + إزاحة الأندرتون النهائية

القيم المدخلة متوافقة مع all_face_analysis.py::analyze_face_shape()
(القيم الممكنة: "Oval" / "Round" / "Rectangular").
"""


# ══════════════════════════════════════════════════════
# RULE SET 1 — خرائط الكونتور/البلاشر/الهاياليت حسب شكل الوجه
# ══════════════════════════════════════════════════════

FACE_CONTOUR_BLUSH_RULES = {
    "Rectangular": {
        "name_ar": "الوجه المستطيل (Face Rectangular)",
        "goal": "Shorten the vertical span and add illusory width to approximate an oval shape.",
        "sculpt": {
            "placement": "A clean horizontal line from the middle of the ear to the middle of the cheek.",
            "purpose": "Breaks the vertical length of the face.",
        },
        "blush": {
            "placement": "Applied horizontally beside the contour line.",
            "purpose": "Visually increases the width of the face.",
        },
        "highlight": {
            "placement": "Center of the forehead and the chin only.",
            "purpose": "Draws attention to the center and avoids the edges.",
        },
        "extra": {
            "placement": "Soft shading at the hairline (top of the forehead) and under the chin only.",
            "purpose": "Shortens the face.",
        },
    },
    "Round": {
        "name_ar": "الوجه الدائري (Face Round)",
        "goal": "Break the roundness, reduce width, and give an impression of length and sharpness.",
        "sculpt": {
            "placement": "A sharp downward-angled contour from the ear to the corner under the mouth, defining the jaw (jawline snatch/Texas contour).",
            "purpose": "Defines the jawbone.",
        },
        "blush": {
            "placement": "Directly under the eye, pulled upward and blended with the eye shadow.",
            "purpose": "Lifts the features of the face.",
        },
        "highlight": {
            "placement": "The tops of the cheeks (highest point) and the chin.",
            "purpose": "Increases the vertical span of the face.",
        },
        "extra": {
            "placement": "Standard contour from the middle of the ear to the middle of the cheek, pulled from the side of the nose toward the outer eye corner.",
            "purpose": "Defines the natural bone structure without harshness; enhances the natural cheekbone projection just above it.",
        },
    },
    "Oval": {
        "name_ar": "الوجه البيضاوي (Face Oval)",
        "goal": "Maintain the ideal balance and define the features.",
        "sculpt": {
            "placement": "Very light contour just above the blush (on the cheekbone).",
            "purpose": "Defines the features and adds three-dimensionality.",
        },
        "blush": {
            "placement": "On the apples of the cheeks only.",
            "purpose": "Adds a healthy, three-dimensional glow.",
        },
        "highlight": {
            "placement": "Under the cheekbone.",
            "purpose": "Defines the features.",
        },
        "extra": {
            "placement": (
                "Full: dark contour is replaced with a very light warm bronzer to prevent a "
                "\"sunken face\" look. Blend style — for a fuller face: an upward blending arrow "
                "toward the ear (lift); for a slimmer face: circular blending at the center (adds "
                "vitality/volume). A very subtle touch of the same blush color is added to the "
                "nose bridge; contour is used in the hollows of the cheeks and under the eyes to "
                "pull sunken areas forward."
            ),
            "purpose": "Prevents a hollow/sunken appearance while keeping the balance ideal.",
        },
    },
}

# نظام "امتلاء الوجه" (Full/Slim) يُستخدم فقط لاختيار أسلوب الدمج للوجه
# البيضاوي (Oval) بحسب النص الأصلي — يُمرَّر اختيارياً من المستخدم/التحليل
FACE_FULLNESS_BLEND_STYLE = {
    "Full": "Upward blending arrow toward the ear (lift).",
    "Slim": "Circular blending at the center (adds volume/vitality).",
}
FACE_FULLNESS_DEFAULT = "Full"


# ══════════════════════════════════════════════════════
# RULE SET 2 — قاعدة اختيار لون البلاشر (5 خطوات)
# ══════════════════════════════════════════════════════

# الخطوة 1: عجلة الألوان مقيدة بمدى Hue محدد (330°→30°) والبني ممنوع كلياً
BLUSH_HUE_RULE = {
    "allowed_hue_range_deg": (330, 30),  # يلتف عبر الصفر (Red/Pink/Peach)
    "forbidden_color": "Brown",
    "forbidden_reason": "Brown is a matte/dead color reserved for contour, not blush.",
    "family": "RCW (Red, Coral, White-pink tones) — reflects the natural blood vessels under the skin.",
}

# الخطوة 2: مصفوفة الألوان الأرضية (Undertone × Depth) → اللون الخام
BLUSH_BASE_COLOR_MATRIX = {
    ("Warm", "Fair"):   "Gold Peach",
    ("Warm", "Medium"): "Coral",
    ("Warm", "Dark"):   "Burnt Orange",
    ("Cool", "Fair"):   "Mauve",
    ("Cool", "Medium"): "Dusty Rose",
    ("Cool", "Dark"):   "Raspberry",
}

# الخطوة 3: التعديل حسب استراتيجية مكياج العين المختارة
BLUSH_EYE_STRATEGY_ADJUSTMENT = {
    "Monochromatic": {
        "rule": "Choose the color from the matrix that leans toward the same warmth as both the eye shadow and the skin tone.",
        "opacity": "Standard",
    },
    "Complementary-Split": {
        "rule": "Neutralize the color — take it from the matrix and make it very sheer/transparent (80% Sheer) so the eye remains the focal point.",
        "opacity": "Sheer 80%",
    },
    "Triadic": {
        "rule": "Neutralize the color — take it from the matrix and make it very sheer/transparent (80% Sheer) so the eye remains the focal point.",
        "opacity": "Sheer 80%",
    },
    "Earth-Toned": {
        "rule": "Choose the most vivid/vibrant version of the color from the matrix to break the monotony of earth tones and give life to the face.",
        "opacity": "Full Vivid",
    },
}
BLUSH_EYE_STRATEGY_DEFAULT = "Monochromatic"

# الخطوة 4: فلتر المناسبة (القوام والكثافة)
BLUSH_OCCASION_TEXTURE = {
    "work":    {"finish": "Matte", "transparency": "80% Sheer", "description": "Looks like a natural flush coming from the skin."},
    "evening": {"finish": "Full Pigment + Satin/Shimmer", "transparency": "Full Opacity", "description": "Stands out under evening lighting."},
    "photo":   {"finish": "Matte", "transparency": "80% Sheer", "description": "Looks like a natural flush coming from the skin (avoids flash reflection)."},
    "wedding": {"finish": "Full Pigment + Satin/Shimmer", "transparency": "Full Opacity", "description": "Stands out under evening/celebration lighting."},
}
BLUSH_OCCASION_DEFAULT = "work"

# الخطوة 5: إزاحة لونية أخيرة حسب الأندرتون
BLUSH_UNDERTONE_SHIFT = {
    "Warm": "A golden shift is added to the final color.",
    "Cool": "A blue/magenta shift is added to the final color.",
}
BLUSH_UNDERTONE_DEFAULT = "Warm"

BLUSH_DEPTH_DEFAULT = "Medium"


# ══════════════════════════════════════════════════════
# محرك القرار — Pure Lookup / Dispatch، بدون if وبدون for
# ══════════════════════════════════════════════════════

def resolve_blush_base_color(skin_undertone=None, skin_depth=None):
    undertone_lookup = {True: skin_undertone, False: BLUSH_UNDERTONE_DEFAULT}
    depth_lookup = {True: skin_depth, False: BLUSH_DEPTH_DEFAULT}

    undertone = undertone_lookup[skin_undertone is not None]
    depth = depth_lookup[skin_depth is not None]

    return undertone, depth, BLUSH_BASE_COLOR_MATRIX.get(
        (undertone, depth),
        BLUSH_BASE_COLOR_MATRIX[(BLUSH_UNDERTONE_DEFAULT, BLUSH_DEPTH_DEFAULT)],
    )


def get_blush_color_recommendation(skin_undertone=None, skin_depth=None,
                                    eye_strategy=None, occasion="work"):
    """
    يبني توصية لون البلاشر عبر الخطوات الخمس بالكامل، اعتماداً على جداول بحث فقط.
    """
    undertone, depth, base_color = resolve_blush_base_color(skin_undertone, skin_depth)

    strategy_lookup = {True: eye_strategy, False: BLUSH_EYE_STRATEGY_DEFAULT}
    resolved_strategy = strategy_lookup[eye_strategy is not None]
    strategy_rule = BLUSH_EYE_STRATEGY_ADJUSTMENT.get(
        resolved_strategy, BLUSH_EYE_STRATEGY_ADJUSTMENT[BLUSH_EYE_STRATEGY_DEFAULT]
    )

    texture_rule = BLUSH_OCCASION_TEXTURE.get(occasion, BLUSH_OCCASION_TEXTURE[BLUSH_OCCASION_DEFAULT])

    undertone_shift = BLUSH_UNDERTONE_SHIFT.get(undertone, BLUSH_UNDERTONE_SHIFT[BLUSH_UNDERTONE_DEFAULT])

    return {
        "hue_rule": BLUSH_HUE_RULE,
        "base_color": base_color,
        "resolved_undertone": undertone,
        "resolved_depth": depth,
        "eye_strategy": resolved_strategy,
        "eye_strategy_rule": strategy_rule,
        "occasion": occasion,
        "texture_rule": texture_rule,
        "undertone_shift": undertone_shift,
    }


def get_face_contour_blush_recommendation(face_analysis_result, fullness="Full",
                                           skin_undertone=None, skin_depth=None,
                                           eye_strategy=None, occasion="work"):
    """
    المدخل: قاموس face_analysis_result كما يخرج من analyze_face_shape()
            في all_face_analysis.py: 'shape', 'votes', 'ratios', ...
    fullness: "Full" | "Slim" (يُستخدم فقط لأسلوب الدمج في الوجه البيضاوي)
    """
    face_shape = face_analysis_result.get("shape", "Oval")
    rules = FACE_CONTOUR_BLUSH_RULES.get(face_shape, FACE_CONTOUR_BLUSH_RULES["Oval"])

    fullness_lookup = {True: fullness, False: FACE_FULLNESS_DEFAULT}
    resolved_fullness = fullness_lookup[fullness is not None]
    blend_style = FACE_FULLNESS_BLEND_STYLE.get(resolved_fullness, FACE_FULLNESS_BLEND_STYLE[FACE_FULLNESS_DEFAULT])

    # أسلوب الدمج يُضاف فقط عند تفعيله (له معنى صريح في الوجه البيضاوي فقط،
    # لكنه يُرفق دائماً كمعلومة إضافية دون أي "if")
    blend_style_lookup = {
        "Oval": blend_style,
    }
    blend_note = blend_style_lookup.get(face_shape, "Not applicable — style is fixed for this face shape.")

    blush_color = get_blush_color_recommendation(skin_undertone, skin_depth, eye_strategy, occasion)

    return {
        "input_shape": face_shape,
        "rule_category_ar": rules["name_ar"],
        "goal": rules["goal"],
        "sculpt": rules["sculpt"],
        "blush": rules["blush"],
        "highlight": rules["highlight"],
        "extra": rules["extra"],
        "fullness": resolved_fullness,
        "blend_style_note": blend_note,
        "blush_color": blush_color,
    }


# ══════════════════════════════════════════════════════
# طباعة منسقة — map() بدل for
# ══════════════════════════════════════════════════════

def print_face_contour_blush_recommendation(recommendation):
    bc = recommendation["blush_color"]
    header = (
        f"\n{'─'*58}\n"
        f"  Face shape detected: {recommendation['input_shape']}\n"
        f"  Rule category: {recommendation['rule_category_ar']}\n"
        f"  Goal: {recommendation['goal']}\n"
        f"{'─'*58}\n"
        f"  Sculpt/Contour:\n    Placement: {recommendation['sculpt']['placement']}\n    Purpose: {recommendation['sculpt']['purpose']}\n\n"
        f"  Blush:\n    Placement: {recommendation['blush']['placement']}\n    Purpose: {recommendation['blush']['purpose']}\n\n"
        f"  Highlight:\n    Placement: {recommendation['highlight']['placement']}\n    Purpose: {recommendation['highlight']['purpose']}\n\n"
        f"  Extra technique:\n    {recommendation['extra']['placement']}\n    Purpose: {recommendation['extra']['purpose']}\n\n"
        f"  Fullness: {recommendation['fullness']}  |  Blend style: {recommendation['blend_style_note']}\n\n"
        f"  Blush Color Recommendation:\n"
        f"    Base color: {bc['base_color']}  (undertone={bc['resolved_undertone']}, depth={bc['resolved_depth']})\n"
        f"    Hue range allowed: {bc['hue_rule']['allowed_hue_range_deg']}°  Forbidden: {bc['hue_rule']['forbidden_color']}\n"
        f"    Eye strategy: {bc['eye_strategy']} → {bc['eye_strategy_rule']['rule']} (opacity: {bc['eye_strategy_rule']['opacity']})\n"
        f"    Occasion texture ({bc['occasion']}): {bc['texture_rule']['finish']}, {bc['texture_rule']['transparency']}\n"
        f"    Undertone shift: {bc['undertone_shift']}\n"
    )
    print(header)


# ══════════════════════════════════════════════════════
# مثال استخدام مباشر
# ══════════════════════════════════════════════════════

if __name__ == "__main__":
    example_face = {"shape": "Oval", "votes": {"Oval": 10, "Round": 2, "Rectangular": 0}}
    rec = get_face_contour_blush_recommendation(
        example_face, fullness="Full",
        skin_undertone="Warm", skin_depth="Medium",
        eye_strategy="Monochromatic", occasion="evening",
    )
    print_face_contour_blush_recommendation(rec)