# -*- coding: utf-8 -*-
"""
nose_makeup_rules.py — Pure Rule-Based Expert System (No if / No for)
=======================================================================
نظام خبير قائم بالكامل على جداول البحث (Lookup Tables) وقواميس الإرسال
(Dispatch Dictionaries / Lambda Dispatch) دون استخدام أي جملة "if" أو حلقة
"for" في منطق القرار (بنفس أسلوب eye_makeup_rules.py و brow_makeup_rules.py).

القاعدة المتبعة لإزالة if/for فعلياً:
    - بدل "x if cond else y"  →  dict[bool(cond)] بمفاتيح True/False.
    - بدل "for x in items: ..."  →  map(func, items) ثم join/إلخ.
    - العتبات الرقمية (<, >) تُنتج قيمة Boolean تُستخدم كمدخل لجدول بحث،
      ولا تُغيّر مسار التنفيذ.

المصدر: ملف "الخبرة_النهائية" — صفحة 9 (قسم الأنف: طويل / قصير / متوازن)
ومنطق "قاعدة النحت" (البشرة الدافئة/الباردة) من صفحة 10.

نوع الأنف الهندسي يُستخرج من all_face_analysis.py::analyze_nose()
والقيم الممكنة: "Long" / "Short" / "Balanced".
"""


# ══════════════════════════════════════════════════════
# جداول القرار الثابتة (البيانات — وليست منطق تحكم)
# ══════════════════════════════════════════════════════

NOSE_MAKEUP_RULES = {
    "Long": {
        "name_ar": "الأنف الطويل (Nose Long)",
        "goal": "Break the continuous vertical line and shorten the visual length of the nose.",
        "technique": (
            "Apply contour starting from the middle of the nose bridge only (not from the brow), "
            "and draw a soft shading circle around the tip of the nose."
        ),
        "reason": (
            "Because the nose is long, contour is applied from the midpoint only to break the "
            "continuous vertical line; shading around the tip acts as a visual barrier that stops "
            "the eye from tracing the length downward, giving the impression the nose ends higher up."
        ),
        "map": {
            "Contour": "Starts at the middle of the nose bridge, blended down the sides.",
            "Highlight": "A thin line down the center of the bridge, stopping before the tip.",
            "Tip_shading": "A soft circular shadow drawn around (not on top of) the nasal tip.",
        },
        "forbidden": [
            "Avoid running the contour the full length from the brow bone — this elongates the nose further.",
            "Avoid a bright highlight dot directly on the tip — it draws the eye downward and accentuates length.",
        ],
    },
    "Short": {
        "name_ar": "الأنف القصير (Nose Short)",
        "goal": "Create the impression of length by defining the bone structure along the full length of the nose.",
        "technique": (
            "Apply full contour along both sides of the nose starting from the brow to the tip, "
            "plus a highlight on the very tip of the nose."
        ),
        "reason": (
            "To give an impression of length, the system applies full-length contour to define the "
            "bony structure and draw attention along the whole nose; the highlight on the tip acts as "
            "an advancing point that pulls the feature forward and extends its visual reach."
        ),
        "map": {
            "Contour": "Full-length, from the start of the brow down both sides to the tip.",
            "Highlight": "Placed directly on the tip of the nose (advancing technique).",
            "Tip_shading": "None — the tip is highlighted, not shaded.",
        },
        "forbidden": [
            "Avoid stopping the contour at mid-bridge — this cuts the nose visually shorter still.",
            "Avoid shading around the tip — that technique is reserved for long noses and would shorten it further.",
        ],
    },
    "Balanced": {
        "name_ar": "الأنف المتوازن (Nose Balanced)",
        "goal": "Frame the nose ideally while emphasizing the strength of its natural features.",
        "technique": (
            "Apply full contour along the sides with light shading on the tip, plus a highlight on the tip."
        ),
        "reason": (
            "The nose is already balanced, so the system uses the full-definition technique to "
            "emphasize the strength of the features and frame the nose perfectly, without lengthening "
            "or shortening it."
        ),
        "map": {
            "Contour": "Full-length along both sides, moderate intensity.",
            "Highlight": "On the tip of the nose.",
            "Tip_shading": "Light shading on the tip, combined with the highlight for dimension.",
        },
        "forbidden": [
            "Avoid heavy/harsh contour — the balanced nose needs definition, not correction.",
        ],
    },
}

# ══════════════════════════════════════════════════════
# قاعدة اختيار منتج النحت (Contour Product) حسب حرارة البشرة وعمقها
# (نفس منطق قاعدة النحت الوارد صفحة 10 من ملف الخبرة، يُعاد استخدامه هنا
#  لأن الأنف يستخدم نفس منتج الكونتور المستخدم في الوجه)
# ══════════════════════════════════════════════════════

NOSE_CONTOUR_PRODUCT_MAP = {
    ("Warm", "Fair"):   {"product": "Adobe",          "reason_ar": "يميل للذهبي الفاتح، يمنح نحتاً طبيعياً دون أن يظهر كبقعة متسخة أو رمادية."},
    ("Warm", "Medium"): {"product": "Warm Brown",      "reason_ar": "لموازنة تدرجات البيج الدافئ في الوجه."},
    ("Warm", "Dark"):   {"product": "Bronze",          "reason_ar": "يحتاج صبغة قوية (Pigment) لكي تظهر عملية التراجع البصري المطلوبة لتصغير الأنف."},
    ("Cool", "Fair"):   {"product": "Taupe",           "reason_ar": "بني مائل للرمادي الفاتح جداً، يحاكي الظل الطبيعي الساقط على الجلد الوردي دون حدة."},
    ("Cool", "Medium"): {"product": "Mauve",           "reason_ar": "يضيف مسحة وردية/زرقاء تتناغم مع العروق الباردة تحت الجلد."},
    ("Cool", "Dark"):   {"product": "Brown-Grey",      "reason_ar": "يضمن عدم تحول الكونتور إلى لون برتقالي (محذور بشدة للبشرة الباردة)."},
}

NOSE_HIGHLIGHT_RULE = {
    "forbidden": "Never use pure/explicit white.",
    "method": "Produced via tinting (base skin color + white) — ivory for warm skin, pearly pink for cool skin.",
    "tone_lookup": {"Warm": "Ivory", "Cool": "Pearly Pink"},
}

# قيمة افتراضية محايدة عند غياب بيانات البشرة (خيار Warm/Medium الأكثر شيوعاً)
NOSE_DEFAULT_UNDERTONE = "Warm"
NOSE_DEFAULT_DEPTH = "Medium"


# ══════════════════════════════════════════════════════
# محرك القرار — Pure Lookup / Dispatch، بدون if وبدون for
# ══════════════════════════════════════════════════════

def resolve_nose_contour_product(skin_undertone=None, skin_depth=None):
    """
    يحدد منتج الكونتور حسب (الأندرتون، عمق البشرة) عبر جدول بحث ثابت.
    القيم الغائبة تُستبدل بقيم افتراضية محايدة عبر جدول True/False.
    """
    undertone_lookup = {True: skin_undertone, False: NOSE_DEFAULT_UNDERTONE}
    depth_lookup = {True: skin_depth, False: NOSE_DEFAULT_DEPTH}

    undertone = undertone_lookup[skin_undertone is not None]
    depth = depth_lookup[skin_depth is not None]

    return NOSE_CONTOUR_PRODUCT_MAP.get(
        (undertone, depth),
        NOSE_CONTOUR_PRODUCT_MAP[(NOSE_DEFAULT_UNDERTONE, NOSE_DEFAULT_DEPTH)],
    )


def get_nose_makeup_recommendation(nose_analysis_result, skin_undertone=None, skin_depth=None):
    """
    المدخل: قاموس nose_analysis_result كما يخرج من analyze_nose()
            في all_face_analysis.py: 'shape', 'votes', 'metrics', ...
    skin_undertone: "Warm" | "Cool" (اختياري)
    skin_depth: "Fair" | "Medium" | "Dark" (اختياري)
    """
    nose_shape = nose_analysis_result.get("shape", "Balanced")
    rules = NOSE_MAKEUP_RULES.get(nose_shape, NOSE_MAKEUP_RULES["Balanced"])

    contour_product = resolve_nose_contour_product(skin_undertone, skin_depth)

    highlight_tone_lookup = {True: skin_undertone, False: NOSE_DEFAULT_UNDERTONE}
    resolved_undertone = highlight_tone_lookup[skin_undertone is not None]
    highlight_tone = NOSE_HIGHLIGHT_RULE["tone_lookup"][resolved_undertone]

    return {
        "input_shape": nose_shape,
        "rule_category_ar": rules["name_ar"],
        "goal": rules["goal"],
        "technique": rules["technique"],
        "reason": rules["reason"],
        "map": rules["map"],
        "forbidden": rules["forbidden"],
        "contour_product": contour_product["product"],
        "contour_product_reason": contour_product["reason_ar"],
        "highlight_rule": {
            "forbidden": NOSE_HIGHLIGHT_RULE["forbidden"],
            "method": NOSE_HIGHLIGHT_RULE["method"],
            "tone": highlight_tone,
        },
    }


# ══════════════════════════════════════════════════════
# طباعة منسقة — map() بدل for
# ══════════════════════════════════════════════════════

def print_nose_recommendation(recommendation):
    map_text = "\n".join(map(lambda kv: f"    {kv[0]:<14}: {kv[1]}", recommendation["map"].items()))
    forbidden_text = "\n".join(map(lambda f: f"    - {f}", recommendation["forbidden"]))

    header = (
        f"\n{'─'*58}\n"
        f"  Nose shape detected: {recommendation['input_shape']}\n"
        f"  Rule category: {recommendation['rule_category_ar']}\n"
        f"  Goal: {recommendation['goal']}\n"
        f"{'─'*58}\n"
        f"  Technique: {recommendation['technique']}\n\n"
        f"  Placement map:\n{map_text}\n\n"
        f"  Forbidden:\n{forbidden_text}\n\n"
        f"  Contour product: {recommendation['contour_product']}\n"
        f"    Reason: {recommendation['contour_product_reason']}\n\n"
        f"  Highlight rule:\n"
        f"    Tone: {recommendation['highlight_rule']['tone']}\n"
        f"    Method: {recommendation['highlight_rule']['method']}\n"
        f"    Forbidden: {recommendation['highlight_rule']['forbidden']}\n\n"
        f"  Explanation: {recommendation['reason']}\n"
    )
    print(header)


# ══════════════════════════════════════════════════════
# مثال استخدام مباشر
# ══════════════════════════════════════════════════════

if __name__ == "__main__":
    example_nose = {"shape": "Long", "votes": {"Long": 6, "Short": 0, "Balanced": 2}}
    rec = get_nose_makeup_recommendation(example_nose, skin_undertone="Warm", skin_depth="Medium")
    print_nose_recommendation(rec)