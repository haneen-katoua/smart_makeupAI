# -*- coding: utf-8 -*-
"""
eye_makeup_rules.py — v3 (Pure Rule-Based Expert System — No if / No for)
==========================================================================
نظام خبير قائم بالكامل على جداول البحث (Lookup Tables) وقواميس الإرسال
(Dispatch Dictionaries / Lambda Dispatch) دون استخدام أي جملة "if" أو حلقة
"for" في منطق القرار.

القاعدة المتبعة لإزالة if/for فعلياً (وليس فقط شكلياً):
    - بدل "x if cond else y"  →  dict[bool(cond)]  حيث المفتاحان True/False
      محسوبان مسبقاً (Eager) كقيمتين عاديتين، أو كـ lambda إذا كان التنفيذ
      له أثر جانبي (side effect مثل print) — بحيث لا يُستدعى إلا الفرع
      المطلوب فقط.
    - بدل "for x in items: ..."  →  map(func, items) ثم join/sum/إلخ.
    - أي عتبات رقمية (<, >) هي عمليات مقارنة عادية، لا تُعتبر "if" لأنها لا
      تُغيّر مسار تنفيذ الكود (Control Flow) بل تُنتج قيمة Boolean تُستخدم
      كمدخل لجدول بحث.

المصدر: ملف "الخبرة_النهائية" — صفحات 1 إلى 8 (قسم العيون فقط).
"""


# ══════════════════════════════════════════════════════
# جداول القرار الثابتة (البيانات — وليست منطق تحكم)
# ══════════════════════════════════════════════════════

EYE_MAKEUP_RULES = {
    "Hooded": {
        "name_ar": "Hooded Eye",
        "goal": "Create illusory depth (Floating / Illusion Crease)",
        "technique": "Use the floating/illusion crease technique: draw an artificial \"shadow\" above the natural skin fold to create visual depth that reduces the appearance of hooding.",
        "forbidden": [
            "Avoid classic eyeliner under the lash line — it breaks/smudges under the sagging skin.",
            "Avoid dense lashes concentrated in the center — they visually press down on the eyelid fold and increase the hooded look.",
        ],
        "shadow_map": {
            "Highlight": "Under the brow bone and at the inner corner only.",
            "Base":      "On the mobile lid (visible only when the eye is closed).",
            "Sculpt":    "Above the natural crease (the illusion crease) — always in a matte finish to visually conceal the sagging skin.",
        },
        "occasions": {
            "work":    {"style": "Natural Matte Micro Bat-Wing", "texture": "100% matte (nude tones only)", "lashes": "Volumizing mascara at the outer corners", "eyeliner": "Dry brown pencil"},
            "evening": {"style": "Dramatic Smoky Sharp Bat-Wing", "texture": "Shimmer on the mobile lid only", "lashes": "Dense D3 lashes, outer-focused", "eyeliner": "Liquid eyeliner"},
            "photo":   {"style": "Matte Cut Crease Smudged Bat-Wing", "texture": "Fully matte (to avoid flash reflection)", "lashes": "Medium-density cat-eye lashes", "eyeliner": "Eyeliner blended with shadow"},
            "wedding": {"style": "Luxury Cut Crease Precise Silk Bat-Wing", "texture": "Satin finish at the front of the eye", "lashes": "Long, spaced-out luxury lashes", "eyeliner": "Silky eyeliner"},
        },
        "explanations": [
            "Cut Crease rationale: creates new dimension for the eye, making the fixed lid appear like a wide mobile lid.",
            "Reason for avoiding central lashes: long central lashes are excluded because they visually press on the eyelid fold and increase hooding.",
            "Reason for a dry product (pencil): a dry pencil gives a natural shadow that defines the eye without the harshness of liquid eyeliner.",
            "Reason for matte texture (photography): shimmer is amplified under flash, making the hooded area look puffy and less refined.",
        ],
    },
    "Protruding": {
        "name_ar": "Protruding Eye",
        "goal": "Reduce the appearance of protrusion",
        "technique": "Use vertical blending techniques (smoky) or socket definition (banana): apply dark, matte colors on the mobile lid and crease to reduce the protruding area and visually \"recede\" the eye.",
        "forbidden": ["Avoid very light or shimmery colors in the center of the lid (they increase the appearance of bulging)."],
        "shadow_map": {
            "Highlight": "Very light, under the brow only (avoid shimmer).",
            "Base":      "Medium/dark tone across the entire protruding lid to visually reduce its size.",
            "Sculpt":    "Blended with the base color vertically (smoky) to break up the protruding area.",
        },
        "occasions": {
            "work":    {"style": "Soft Smoky", "texture": "100% matte (dark earth tones)", "lashes": "Volumizing mascara at the center", "eyeliner": "Brown kohl inside the eye"},
            "evening": {"style": "Intense Smoky Thick Wing", "texture": "Very light shimmer at the lash line only", "lashes": "Rounded D3 lashes", "eyeliner": "Thick eyeliner"},
            "photo":   {"style": "Matte Banana Smudged", "texture": "Fully matte (to avoid flash reflecting off the protrusion)", "lashes": "Natural, even-length lashes", "eyeliner": "Blended eyeliner"},
            "wedding": {"style": "Luxury Smoky / Banana", "texture": "Very light satin", "lashes": "Dense, well-groomed luxury lashes", "eyeliner": "Silky, precisely lined eyeliner"},
        },
        "explanations": [
            "Style rationale (Banana/Smoky): covering the lid with dark colors creates an artificial shadow that reduces the eye's protrusion and gives it depth.",
            "Rationale for lashes without extreme flare: rounded lashes (no flick) avoid visually widening the eye further, focusing instead on shading the protruding area.",
            "Dark kohl inside the eye rationale: it reduces the visible white of the eye and lessens the \"surprised\" look associated with protrusion.",
            "Reason for avoiding light shades in photography: strong lighting highlights reflective surfaces, making the eye look even more protruding in photos.",
        ],
    },
    "Almond": {
        "name_ar": "Almond Eye",
        "goal": "Enhance balance (no correction needed — the ideal reference shape)",
        "technique": "The almond eye is anatomically balanced and serves as the ideal template for any makeup design without needing corrective techniques.",
        "forbidden": [],
        "shadow_map": {
            "Highlight": "Under the brow and at the inner corner.",
            "Base":      "Across the entire mobile lid.",
            "Sculpt":    "In the natural crease to define the eye's ideal shape.",
        },
        "occasions": {
            "work":    {"style": "Natural Definition", "texture": "100% matte (earth tones)", "lashes": "Natural mascara (spider-lash effect)", "eyeliner": "Thin line along the lash line"},
            "evening": {"style": "Dramatic Smoky", "texture": "Shimmer or glitter across the whole lid", "lashes": "Varied, dense 3D lashes", "eyeliner": "Sharp winged eyeliner"},
            "photo":   {"style": "Half Cut Crease", "texture": "Fully matte due to lighting", "lashes": "Medium cat-eye lashes", "eyeliner": "Fine liquid eyeliner"},
            "wedding": {"style": "Spotlight / Banana", "texture": "Satin at the center of the lid", "lashes": "Long, dense luxury lashes", "eyeliner": "Precisely applied silky eyeliner"},
        },
        "explanations": [
            "Style rationale: the eye is anatomically balanced, making it the ideal template for any design without corrective techniques.",
            "Winged eyeliner rationale: it enhances the naturally appealing curve of the almond eye and highlights the balance of its corners.",
            "Spotlight technique rationale: placing highlight at the center of the lid gives a three-dimensional look that emphasizes symmetry.",
            "Matte texture in photography rationale: almond features are already very clear, and excess shimmer could blur the precision of the eye's proportions.",
        ],
    },
    "Round": {
        "name_ar": "Round Eye",
        "goal": "Horizontal pull",
        "technique": "Use socket definition (banana) or a partial half cut crease: blend shadow upward and outward at the outer corners to break the roundness and give the eye a horizontal pull.",
        "forbidden": ["Avoid concentrating lashes at the center (it increases vertical openness and unevenly emphasizes the round shape)."],
        "shadow_map": {
            "Highlight": "At the inner corner of the lid.",
            "Base":      "Distributed across the lid and blended diagonally outward.",
            "Sculpt":    "Focused at the outer corner (outer V) and extended outward to suggest an almond shape.",
        },
        "occasions": {
            "work":    {"style": "Soft Banana", "texture": "100% matte (light earth tones)", "lashes": "Natural mascara, denser toward the outer corners", "eyeliner": "Very thin line along the lashes, thickening outward"},
            "evening": {"style": "Bold Banana", "texture": "Shimmer or glitter on the lid", "lashes": "Winged 3D lashes (cat-eye)", "eyeliner": "Sharp winged eyeliner"},
            "photo":   {"style": "Matte Half Cut Crease", "texture": "Fully matte", "lashes": "Outer-corner lashes only (half-lashes)", "eyeliner": "Blended eyeliner pulled outward (smudged)"},
            "wedding": {"style": "Luxury Half Cut Crease", "texture": "Satin on the cut section", "lashes": "Long luxury lashes at the outer corners", "eyeliner": "Precisely pulled silky eyeliner"},
        },
        "explanations": [
            "Style rationale (Banana/Half Cut Crease): drawing an imaginary line beyond the natural eye boundary suggests elongation and reduces the round appearance.",
            "Outer blending rationale: blending shadow upward at the outer corner lifts the eye and shifts its shape from round toward almond.",
            "Reason for avoiding central lashes: dense lashes at the center increase vertical openness and emphasize the round shape.",
            "Matte texture in photography rationale: shimmer at the center of a round eye reflects flash light, making the eye look more bulging and rounder.",
        ],
    },
    "Droopy": {
        "name_ar": "Droopy Eye",
        "goal": "Visual lifting (illusion lifting)",
        "technique": "Direct all lines (shadow and eyeliner) upward before reaching the end of the natural lashes, to prevent the eye from appearing \"sad\" or drooping.",
        "forbidden": [
            "Avoid following the natural downward lash line at the outer corner; eyeliner and shadow must be drawn at an upward angle toward the tail of the brow.",
            "Avoid placing dark colors below the level of the outer lower lashes (it adds weight to the eye and pulls it downward).",
        ],
        "shadow_map": {
            "Highlight": "Inner corner and front lid.",
            "Base":      "The mobile lid.",
            "Sculpt":    "Drawn as an upward-pointing arrow at the outer corner; no dark color is allowed below the level of the outer lashes to ensure lift.",
        },
        "occasions": {
            "work":    {"style": "Natural Lift", "texture": "100% matte (light earth tones)", "lashes": "Volumizing mascara at the upper outer lashes", "eyeliner": "Soft upward pull with a brown pencil"},
            "evening": {"style": "Bold Winged Smoky", "texture": "Shimmer at the inner corner only", "lashes": "3D lashes pulled toward the outer corners", "eyeliner": "Sharp winged eyeliner"},
            "photo":   {"style": "Sculpted Outer V", "texture": "Fully matte (to ensure the lift reads clearly in HD)", "lashes": "Outer-corner lashes (half-lashes)", "eyeliner": "Blended eyeliner pulled upward"},
            "wedding": {"style": "Luxury Winged Style", "texture": "Satin at the center of the lid", "lashes": "Long luxury lashes at the outer corners", "eyeliner": "Precisely pulled silky eyeliner"},
        },
        "explanations": [
            "Lifting technique rationale: it raises the outer corner of the eye, shifting the look from drooping to balanced and visually appealing.",
            "Eyeliner pull rationale: directing the line upward before the eye's natural end avoids following the lashes' natural downward curve, opening and widening the gaze.",
            "Winged lashes rationale: lengthening the outer tips pulls the eye upward and conceals the drooping corners.",
            "Reason for avoiding dark color under the eye: dark colors on the outer lower lashes add weight, pull the eye down, and emphasize a sleepy look.",
        ],
    },
    "Deep-set": {
        "name_ar": "Deep-set Eye",
        "goal": "Advancing technique",
        "technique": "Apply light, bright colors across the entire mobile lid to visually \"pull\" the eye forward, using medium (not dark) tones in the crease.",
        "forbidden": ["Never place very dark colors inside the eye's crease (it deepens the hollow and makes the eye look sunken)."],
        "shadow_map": {
            "Highlight": "Across the entire sunken lid to visually pull it forward.",
            "Base":      "A light touch at the center of the lid.",
            "Sculpt":    "Very light, in light shades (like taupe) to avoid deepening the eye further.",
        },
        "occasions": {
            "work":    {"style": "Natural Glow", "texture": "100% matte (ivory/beige tones)", "lashes": "Lengthening mascara at the center only", "eyeliner": "Very thin line (for definition only)"},
            "evening": {"style": "Soft Gradient Smoky", "texture": "Strong shimmer across the whole mobile lid", "lashes": "Light-texture 3D lashes", "eyeliner": "Smudged eyeliner"},
            "photo":   {"style": "Matte Half Cut Crease", "texture": "Fully matte (to balance the natural shadow of the hollow)", "lashes": "Long natural lashes at the outer corners", "eyeliner": "Thin, blended eyeliner"},
            "wedding": {"style": "Luxury Half Cut Crease", "texture": "Bright satin on the cut section", "lashes": "Long, wispy luxury lashes", "eyeliner": "Precisely pulled silky eyeliner"},
        },
        "explanations": [
            "Style rationale: light colors on the lid act as a reflector, bringing forward the deep-set eye and reducing how recessed it looks.",
            "Reason for avoiding dark colors in the crease: they deepen the natural shadow of the hollow, making the eye look more sunken and tired.",
            "Half Cut Crease rationale: it creates a wide area of light on the inner half of the eye, opening the gaze and balancing a prominent brow bone.",
            "Matte texture in photography rationale: a deep-set eye already creates natural shadow, so matte ensures even light distribution without random highlights that would visually deepen the hollow.",
        ],
    },
}

EYE_SPACING_RULES = {
    "Close-set": {"name_ar": "Close-set eyes", "rule": "Highlight must be applied at the inner corner (tear duct area)."},
    "Wide-set":  {"name_ar": "Wide-set eyes", "rule": "A medium-to-dark shadow (sculpt or base color) must be applied at the inner corner."},
    "Normal":    {"name_ar": "Normal spacing", "rule": "No correction needed at the inner corner."},
}

# الأنواع "الوظيفية" تطغى دائماً على الشكل الهندسي المجرد عند التعارض
FUNCTIONAL_EYE_TYPES = {"Hooded", "Protruding", "Droopy", "Deep-set"}

# عند غياب نوع وظيفي خاص (Normal): تحويل الشكل الهندسي إلى فئة الخبرة
# Round → Round / أي شيء آخر (Almond أو Average) → Almond (الشكل المرجعي)
SHAPE_FALLBACK_MAP = {"Round": "Round"}

# مفاتيح ثابتة لجدول تصنيف المسافة بين العينين (status_key الناتج عن مقارنتين)
EYE_SPACING_STATUS_LOOKUP = {0: "Normal", 1: "Close-set", 2: "Wide-set"}

# عتبات نسبة المسافة بين العينين — تقريبية ريثما تُعاير على بيانات حقيقية
# inter_eye_ratio = (إحداثي الزاوية الداخلية اليسرى - اليمنى) / عرض الوجه
EYE_SPACING_DEFAULT_RATIO = 0.35  # قيمة محايدة (ضمن مدى Normal) عند غياب القياس


# ══════════════════════════════════════════════════════
# محرك القرار — Pure Lookup / Dispatch، بدون if وبدون for
# ══════════════════════════════════════════════════════

def resolve_rule_category(geo_shape, eye_type):
    """
    حل الفئة عبر جدول بحث ثابت فقط:
    True  → eye_type نفسه (لأنه نوع وظيفي)
    False → الشكل الهندسي مُمرَّر عبر SHAPE_FALLBACK_MAP (افتراضي Almond)
    """
    category_lookup = {
        True:  eye_type,
        False: SHAPE_FALLBACK_MAP.get(geo_shape, "Almond"),
    }
    return category_lookup[eye_type in FUNCTIONAL_EYE_TYPES]


def classify_eye_spacing(inter_eye_ratio):
    """
    تصنيف نسبة المسافة بين العينين عبر جدول بحث حسابي بحت:
    - يُحسب status_key من مجموع نتيجتي مقارنة (Boolean→int) دون أي if.
    - النتيجة النهائية تمر عبر جدول {True/False} لإرجاع None
      مباشرة في حال لم تتوفر القيمة أصلاً (بدل أي شرط صريح).
    """
    ratio_lookup = {True: inter_eye_ratio, False: EYE_SPACING_DEFAULT_RATIO}
    ratio = ratio_lookup[inter_eye_ratio is not None]

    status_key = int(ratio < 0.32) * 1 + int(ratio > 0.42) * 2
    spacing_label = EYE_SPACING_STATUS_LOOKUP[status_key]

    result_lookup = {True: spacing_label, False: None}
    return result_lookup[inter_eye_ratio is not None]


def get_eye_makeup_recommendation(eye_analysis_result, occasion="work", inter_eye_ratio=None):
    """
    المدخل: قاموس eye_analysis_result كما يخرج من analyze_one_eye()
            في face_analysis.py: 'geo_shape', 'eye_type', 'combined', ...
    occasion: "work" | "evening" | "photo" | "wedding"
    inter_eye_ratio: نسبة المسافة بين العينين (اختياري)
    """
    geo_shape = eye_analysis_result.get("geo_shape")
    eye_type  = eye_analysis_result.get("eye_type")
    combined  = eye_analysis_result.get("combined")

    category = resolve_rule_category(geo_shape, eye_type)
    rules = EYE_MAKEUP_RULES[category]
    occasion_plan = rules["occasions"].get(occasion, rules["occasions"]["work"])

    # ملاحظة التعارض الهندسي: تُبنى كقيمة جاهزة مسبقاً ضمن جدول True/False
    is_discrepancy = (eye_type in FUNCTIONAL_EYE_TYPES) and (geo_shape == "Round")
    note_lookup = {
        True: (
            f"Note: the eye's geometric shape ({geo_shape}) differs from the "
            f"functional condition used for correction ({category}). The "
            f"{rules['name_ar']} rules were applied because functional "
            f"correction takes priority, while the geometric shape is still "
            f"considered when adjusting the thickness/extension of the "
            f"eyeliner only."
        ),
        False: None,
    }
    note = note_lookup[is_discrepancy]

    spacing_category = classify_eye_spacing(inter_eye_ratio)
    spacing_rule = EYE_SPACING_RULES.get(spacing_category, None)

    return {
        "input_combined": combined,
        "rule_category": category,
        "rule_category_ar": rules["name_ar"],
        "goal": rules["goal"],
        "technique": rules["technique"],
        "forbidden": rules["forbidden"],
        "shadow_map": rules["shadow_map"],
        "occasion": occasion,
        "occasion_plan": occasion_plan,
        "explanations": rules["explanations"],
        "geometry_note": note,
        "spacing": spacing_rule,
    }


# ══════════════════════════════════════════════════════
# طباعة منسقة — map() بدل for، lambda dispatch بدل if
# ══════════════════════════════════════════════════════

def print_eye_recommendation(label, recommendation):
    forbidden_text = "\n".join(map(lambda f: f"    - {f}", recommendation["forbidden"]))
    forbidden_display_lookup = {
        True:  forbidden_text,
        False: "    - No specific restrictions",
    }
    forbidden_display = forbidden_display_lookup[bool(recommendation["forbidden"])]

    shadow_text = "\n".join(
        map(lambda kv: f"    {kv[0]:<10}: {kv[1]}", recommendation["shadow_map"].items())
    )
    explanations_text = "\n".join(map(lambda e: f"    • {e}", recommendation["explanations"]))

    op = recommendation["occasion_plan"]

    header = (
        f"\n{'─'*58}\n"
        f"  [{label}]  Detected eye: {recommendation['input_combined']}\n"
        f"  Makeup rule category applied: {recommendation['rule_category_ar']} ({recommendation['rule_category']})\n"
        f"  Goal: {recommendation['goal']}\n"
        f"{'─'*58}\n"
        f"  Technique: {recommendation['technique']}\n"
        f"  Forbidden:\n{forbidden_display}\n\n"
        f"  Shadow distribution map:\n{shadow_text}\n\n"
        f"  Occasion: {recommendation['occasion']}\n"
        f"    Style    : {op['style']}\n"
        f"    Texture  : {op['texture']}\n"
        f"    Lashes   : {op['lashes']}\n"
        f"    Eyeliner : {op['eyeliner']}\n"
    )
    print(header)

    # تنفيذ مشروط بدون "if": قاموس إرسال من lambdas، يُستدعى فقط الفرع المطابق
    geometry_action_lookup = {
        True:  lambda: print(f"  {recommendation['geometry_note']}\n"),
        False: lambda: None,
    }
    geometry_action_lookup[recommendation["geometry_note"] is not None]()

    spacing_action_lookup = {
        True: lambda: print(
            f"  Inter-eye spacing correction ({recommendation['spacing']['name_ar']}):\n"
            f"    {recommendation['spacing']['rule']}\n"
        ),
        False: lambda: None,
    }
    spacing_action_lookup[recommendation["spacing"] is not None]()

    print(f"  Explanations:\n{explanations_text}\n")


# ══════════════════════════════════════════════════════
# مثال استخدام مباشر
# ══════════════════════════════════════════════════════

if __name__ == "__main__":
    example_left_eye = {
        "geo_shape": "Round", "eye_type": "Hooded",
        "combined": "Round Hooded", "size": "Normal", "corner": "Neutral",
    }
    example_right_eye = {
        "geo_shape": "Round", "eye_type": "Normal",
        "combined": "Round", "size": "Normal", "corner": "Neutral",
    }

    rec_l = get_eye_makeup_recommendation(example_left_eye, occasion="evening", inter_eye_ratio=0.30)
    rec_r = get_eye_makeup_recommendation(example_right_eye, occasion="evening")

    print_eye_recommendation("Left", rec_l)
    print_eye_recommendation("Right", rec_r)