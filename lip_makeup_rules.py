# -*- coding: utf-8 -*-
"""
lip_makeup_rules.py — Pure Rule-Based Expert System (No if / No for)
=======================================================================
نظام خبير قائم بالكامل على جداول البحث (Lookup Tables) وقواميس الإرسال
(Dispatch Dictionaries / Lambda Dispatch) دون استخدام أي جملة "if" أو حلقة
"for" في منطق القرار (بنفس أسلوب eye_makeup_rules.py و brow_makeup_rules.py).

يغطي هذا الملف (صفحات 12-13 من ملف الخبرة):
  1) قاعدة "Tall Lips" الذهبية: التركيز على الارتفاع والامتلاء المركزي
  2) قاعدة تصحيح وهندسة الشفاه: 6 حالات
     (Thin / Upper Thin / Lower Thin / Very Large / Full & Balanced)
  3) خبرة منطق اختيار لون الروج: حسب المناسبة (القوام/المنتج) وحسب
     الأندرتون (دافئ/بارد)

الخرج متوافق مع all_face_analysis.py::analyze_lips() حيث النتيجة تحوي
المفاتيح: 'Volume', 'Balance', 'Correction', 'Symmetry', 'Width',
'Cupid Bow', 'Corners'. القيمة "Balance" هي المفتاح الأساسي لتحديد
حالة التصحيح الهندسي هنا (Upper Fuller / Lower Fuller / Balanced)،
وتُدمج مع "Volume" و "Width" لتحديد الحالة الست الكاملة.
"""


# ══════════════════════════════════════════════════════
# القاعدة الذهبية — Tall Lips
# ══════════════════════════════════════════════════════

LIP_GOLDEN_RULE = {
    "name": "Tall Lips",
    "rule": (
        "The system forces focus on height and fullness at the center of the lips rather than their "
        "width, to enhance a \"heart\" appearance in the face and give it lifting energy (Vaulting) "
        "that increases the attractiveness of the features."
    ),
    "tall_lips_explanation": (
        "Focus on the center while avoiding extending the outer corners was chosen to ensure the "
        "\"lifting energy\" is directed upward, which prevents a drooping appearance in the face."
    ),
}


# ══════════════════════════════════════════════════════
# جداول تصحيح وهندسة الشفاه — 6 حالات
# ══════════════════════════════════════════════════════
# مفتاح الحالة مبني من (Volume, Balance) القادمين من analyze_lips():
#   Volume: "Thin" | "Medium" | "Full"
#   Balance: "Upper Fuller" | "Lower Fuller" | "Balanced"
#
# يُشتق منها 6 حالات الخبرة:
#   Thin + Balanced          → "Thin"           (شفاه رقيقة عموماً)
#   Thin/Medium + Upper Fuller (upper thinner)  → "Upper Thin"
#   Thin/Medium + Lower Fuller (lower thinner)  → "Lower Thin"
#   Full + أي توازن + Width=Wide → "Very Large"
#   Full + Balanced           → "Full & Balanced"
#   (احتياطي) أي شيء آخر      → "Full & Balanced"
#
# ملاحظة: "Upper Fuller" في analyze_lips تعني الشفة العليا أضخم، أي
# الشفة السفلى هي الأنحف نسبياً — لكن حالة الخبرة "شفاه علوية رقيقة"
# تعني أن العليا هي الرقيقة. لذلك في هذا الملف نُدخل مفهوم "الشفة
# الأنحف" (thinner_lip) المُشتق مباشرة من Balance عبر جدول بحث ثابت
# لضمان التطابق الدلالي الصحيح مع نص الخبرة.

# Balance من analyze_lips → أي شفة هي "الأنحف نسبياً" (thinner_lip)
THINNER_LIP_FROM_BALANCE = {
    "Upper Fuller": "Lower",   # العليا أضخم ⇒ السفلى أنحف نسبياً
    "Lower Fuller": "Upper",   # السفلى أضخم ⇒ العليا أنحف نسبياً
    "Balanced": "None",
}

LIP_SHAPE_CORRECTION_RULES = {
    "Thin": {
        "name_ar": "شفاه رقيقة (Thin)",
        "correction_style": "Enlarge outward (overline)",
        "technique": "Draw the lip liner outside the natural lip boundary, with lip color matching the liner.",
        "reason": "To create the impression of greater fullness that aligns with ideal-face aesthetics.",
    },
    "Upper Thin": {
        "name_ar": "شفاه علوية رقيقة (Upper Lip Thin)",
        "correction_style": "Balance the ratio",
        "technique": "Draw the line above the natural upper-lip boundary, while keeping the lower lip's natural boundary.",
        "reason": "To achieve symmetry between the upper and lower lips.",
    },
    "Lower Thin": {
        "name_ar": "شفاه سفلى رقيقة (Lower Lip Thin)",
        "correction_style": "Balance the ratio",
        "technique": "The reverse of the previous technique — draw the line below the natural boundary of the lower lip.",
        "reason": "To ensure visual balance and symmetry of the mouth.",
    },
    "Very Large": {
        "name_ar": "شفاه كبيرة جداً (Very Large)",
        "correction_style": "Visual minimization",
        "technique": "Draw the line inside the natural lip boundary, using medium-to-dark colors.",
        "reason": "To reduce the apparent surface area of the lips in an aesthetically natural, non-obvious way.",
    },
    "Full & Balanced": {
        "name_ar": "شفاه ممتلئة ومتوازنة (Full & Balanced)",
        "correction_style": "Preserve natural shape",
        "technique": "Draw the lip liner directly and precisely on the natural lip boundary, then fill with the chosen lipstick color.",
        "reason": (
            "Since the lips are already full and considered the \"ideal aesthetic standard\", the "
            "system only applies \"Definition\" to highlight the natural symmetry, with no need to "
            "change dimensions or use any visual illusion technique."
        ),
    },
}
LIP_SHAPE_DEFAULT = "Full & Balanced"


# ══════════════════════════════════════════════════════
# قاعدة اختيار لون الروج — Skin Integration principle
# ══════════════════════════════════════════════════════

LIP_COLOR_LOGIC_PRINCIPLE = (
    "The goal is for the lips to look naturally 'this color' rather than 'covered' by a layer of "
    "color; the chosen shade is therefore integrated well enough to blend into the skin tissue."
)

LIP_COLOR_BY_UNDERTONE = {
    "Warm": {"palette": "Golden/Peach base rule", "colors": "Coral / Peach tones"},
    "Cool": {"palette": "Cool base rule", "colors": "Berry / Blueish-pink tones (Mauve/Raspberry)"},
}
LIP_COLOR_UNDERTONE_DEFAULT = "Warm"

LIP_OCCASION_STYLE_RULES = {
    "work": {
        "style": "Natural Flush",
        "product": "Lip Stain or a very light matte lipstick.",
        "texture": "Matte — gives a healthy, vibrant look.",
    },
    "evening": {
        "style": "Balanced Look",
        "product": "A strongly pigmented lipstick, balanced with the eye makeup.",
        "texture": "Satin or creamy — gives a three-dimensional depth.",
    },
    "photo": {
        "style": "HD Definition",
        "product": "Matte lipstick with very sharp, razor-sharp edge definition.",
        "texture": "Fully matte — prevents scattered flash reflection.",
    },
    "wedding": {
        "style": "Luscious Lips",
        "product": "Rich lipstick with a gloss layer applied vertically in the center only, to increase light reflection.",
        "texture": "Glossy (center only, over a rich base).",
    },
}
LIP_OCCASION_DEFAULT = "work"


# ══════════════════════════════════════════════════════
# محرك القرار — Pure Lookup / Dispatch، بدون if وبدون for
# ══════════════════════════════════════════════════════

def resolve_lip_shape_category(lip_analysis_result):
    """
    يشتق حالة الخبرة الست (Thin/Upper Thin/Lower Thin/Very Large/Full & Balanced)
    من نتائج analyze_lips() عبر جداول بحث محسوبة مسبقاً فقط.
    """
    volume = lip_analysis_result.get("Volume", "Medium")
    balance = lip_analysis_result.get("Balance", "Balanced")
    width = lip_analysis_result.get("Width", "Average")

    thinner_lip = THINNER_LIP_FROM_BALANCE.get(balance, "None")

    # مفتاح مركّب جاهز محسوب مسبقاً (Eager) لتفادي أي if/elif متسلسل
    category_lookup = {
        ("Thin", "None"):   "Thin",
        ("Thin", "Upper"):  "Upper Thin",
        ("Thin", "Lower"):  "Lower Thin",
        ("Medium", "Upper"): "Upper Thin",
        ("Medium", "Lower"): "Lower Thin",
        ("Medium", "None"):  "Full & Balanced",
        ("Full", "None"):    "Full & Balanced",
        ("Full", "Upper"):   "Full & Balanced",
        ("Full", "Lower"):   "Full & Balanced",
    }
    base_category = category_lookup.get((volume, thinner_lip), LIP_SHAPE_DEFAULT)

    # تجاوز خاص: Full + Wide → Very Large (يُبنى كقيمة جاهزة True/False)
    is_very_large = (volume == "Full") and (width == "Wide")
    override_lookup = {True: "Very Large", False: base_category}
    return override_lookup[is_very_large]


def get_lip_color_recommendation(skin_undertone=None, occasion="work"):
    undertone_lookup = {True: skin_undertone, False: LIP_COLOR_UNDERTONE_DEFAULT}
    resolved_undertone = undertone_lookup[skin_undertone is not None]
    color_rule = LIP_COLOR_BY_UNDERTONE.get(resolved_undertone, LIP_COLOR_BY_UNDERTONE[LIP_COLOR_UNDERTONE_DEFAULT])

    occasion_rule = LIP_OCCASION_STYLE_RULES.get(occasion, LIP_OCCASION_STYLE_RULES[LIP_OCCASION_DEFAULT])

    return {
        "resolved_undertone": resolved_undertone,
        "palette_rule": color_rule["palette"],
        "colors": color_rule["colors"],
        "occasion": occasion,
        "style": occasion_rule["style"],
        "product": occasion_rule["product"],
        "texture": occasion_rule["texture"],
    }


def get_lip_makeup_recommendation(lip_analysis_result, skin_undertone=None, occasion="work"):
    """
    المدخل: (feats, result) tuple أو dict نتيجة analyze_lips() في
            all_face_analysis.py — يُستخدم هنا result (القاموس المصنَّف).
    """
    category = resolve_lip_shape_category(lip_analysis_result)
    shape_rules = LIP_SHAPE_CORRECTION_RULES.get(category, LIP_SHAPE_CORRECTION_RULES[LIP_SHAPE_DEFAULT])
    color_rec = get_lip_color_recommendation(skin_undertone, occasion)

    return {
        "input_volume": lip_analysis_result.get("Volume"),
        "input_balance": lip_analysis_result.get("Balance"),
        "input_width": lip_analysis_result.get("Width"),
        "rule_category": category,
        "rule_category_ar": shape_rules["name_ar"],
        "correction_style": shape_rules["correction_style"],
        "technique": shape_rules["technique"],
        "reason": shape_rules["reason"],
        "golden_rule": LIP_GOLDEN_RULE,
        "color_logic_principle": LIP_COLOR_LOGIC_PRINCIPLE,
        "color_recommendation": color_rec,
    }


# ══════════════════════════════════════════════════════
# طباعة منسقة — map() بدل for
# ══════════════════════════════════════════════════════

def print_lip_recommendation(recommendation):
    cr = recommendation["color_recommendation"]
    header = (
        f"\n{'─'*58}\n"
        f"  Lips detected: Volume={recommendation['input_volume']}  "
        f"Balance={recommendation['input_balance']}  Width={recommendation['input_width']}\n"
        f"  Rule category: {recommendation['rule_category_ar']} ({recommendation['rule_category']})\n"
        f"{'─'*58}\n"
        f"  Golden rule ({recommendation['golden_rule']['name']}): {recommendation['golden_rule']['rule']}\n\n"
        f"  Correction style: {recommendation['correction_style']}\n"
        f"  Technique: {recommendation['technique']}\n"
        f"  Reason: {recommendation['reason']}\n\n"
        f"  Color logic principle: {recommendation['color_logic_principle']}\n"
        f"  Color recommendation ({cr['occasion']}):\n"
        f"    Undertone: {cr['resolved_undertone']}  →  {cr['colors']}\n"
        f"    Style: {cr['style']}\n"
        f"    Product: {cr['product']}\n"
        f"    Texture: {cr['texture']}\n"
    )
    print(header)


# ══════════════════════════════════════════════════════
# مثال استخدام مباشر
# ══════════════════════════════════════════════════════

if __name__ == "__main__":
    example_lips = {
        "Volume": "Medium", "Balance": "Lower Fuller", "Correction": "Needs Upper Lip Enhancement",
        "Symmetry": "Symmetrical", "Width": "Average", "Cupid Bow": "Soft", "Corners": "Neutral",
    }
    rec = get_lip_makeup_recommendation(example_lips, skin_undertone="Cool", occasion="wedding")
    print_lip_recommendation(rec)