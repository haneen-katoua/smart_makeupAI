"""
brow_makeup_rules.py
════════════════════════════════════════════════════════════════

نظام قواعس الحواجب — Rule-based (بدون if/for)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

المنطق الأساسي:
  • الحاجب = إطار "عالم العين" → لا يتجاوز حدود الـ V من فتحة الأنف
  • قاعدة "النقاط الثلاث": البداية (من الأنف عموديا) + القمة (مع حدقة العين) + النهاية (مع الزاوية الخارجية)
  • التصحيح يعتمد على: شكل الوجه + المناسبة (occasion)

الخرج النهائي:
  {
    "style": "Natural Grooming" / "Arch Defined" / "Brow Sculpted" / "Glamour Bold",
    "arch_type": "High Arch" / "Soft Arch" / "Flat" / "Soft Rounded",
    "tail_direction": "Extended & Heavy" / "Extended" / "Tapered" / "Natural",
    "technique": "Grooming" / "Definition" / "Sculpting" / "Bold Precision",
    "product": "Gel" / "Powder" / "Pencil" / "Bold Liner",
    "color_intensity": "Sheer" / "Natural" / "Strong" / "Bold",
    "three_dots": {...},  # نقاط هندسية دقيقة
    "explanation": "..."
  }
════════════════════════════════════════════════════════════════
"""


# ══════════════════════════════════════════════════════════════
# RULE 1: OCCASION-BASED STYLE MAPPING
# ══════════════════════════════════════════════════════════════
# الخرج يُحدد حسب المناسبة + خصائص الحاجب الأصلية

BROW_STYLE_BY_OCCASION = {
    # جامعة / عمل — طبيعي ونظيف
    "work": {
        "style": "Natural Grooming",
        "description": "تمشيط شفاف أو لون خفيف جداً على الشعر",
        "technique": "Grooming",
        "product": "Gel Clear or Tinted",
        "color_intensity": "Sheer",
        "appearance": "Unpainted & Clean",
    },
    # سهرة / حفلة — محدد مع قمة واضحة
    "party": {
        "style": "Arch Defined",
        "description": "تحديد نقاط الارتكاز (البداية، القمة، النهاية) بودرة أو قلم",
        "technique": "Definition",
        "product": "Powder or Pencil",
        "color_intensity": "Natural",
        "appearance": "Defined Symmetry",
    },
    # تصوير / إعلام — كثيف مع ضربات طبيعية
    "photography": {
        "style": "Brow Sculpted",
        "description": "تعبئة الفراغات بضربات ريشة 45° تحاكي نمو الشعر",
        "technique": "Sculpting",
        "product": "Pencil or Powder Strokes",
        "color_intensity": "Strong (HD-ready)",
        "appearance": "Natural Density",
    },
    # زفاف / دراما — رسم حاد مع رفع قصوى
    "wedding": {
        "style": "Glamour Bold",
        "description": "رسم حاد ومحدد مع رفع القمة لخلق طاقة رفع قصوى",
        "technique": "Bold Precision",
        "product": "Brow Liner & Definer",
        "color_intensity": "Bold",
        "appearance": "Dramatic Lift",
    },
}


# ══════════════════════════════════════════════════════════════
# RULE 2: FACE SHAPE CORRECTION MAPPING
# ══════════════════════════════════════════════════════════════
# تصحيح هندسة الحاجب حسب شكل الوجه

BROW_CORRECTION_BY_FACE_SHAPE = {
    # وجه دائري — كسر الاستدارة + إيحاء بالطول
    "Round": {
        "arch_type": "High Arch",
        "arch_position": "Elevated",
        "tail_direction": "Extended Outward",
        "tail_weight": "Heavy",
        "shape_rule": "رفع القمة عاليا مع ذيل نحو الخارج والحدة",
        "visual_purpose": "كسر الاستدارة وإعطاء إيحاء بالطول والحدة",
    },
    # وجه مستطيل — خط أفقي للتوازن
    "Rectangular": {
        "arch_type": "Soft Arch or Flat",
        "arch_position": "Moderate to Low",
        "tail_direction": "Extended Long",
        "tail_weight": "Tapered Light",
        "shape_rule": "قمة مسطحة نسبيا مع ذيل طويل",
        "visual_purpose": "كسر الخط العمودي وإضافة عرض وهمي",
    },
    # وجه بيضاوي — متوازن تشريحيا
    "Oval": {
        "arch_type": "Natural",
        "arch_position": "Natural Position",
        "tail_direction": "Natural",
        "tail_weight": "Natural",
        "shape_rule": "الشكل الطبيعي مثالي دون تعديل",
        "visual_purpose": "متوازن تشريحيا وال يحتاج تصحيح",
    },
    # وجه مثلثي — موازنة الفك الثقيل
    "Triangle": {
        "arch_type": "Neutral Arch",
        "arch_position": "Moderate",
        "tail_direction": "Extended Heavy",
        "tail_weight": "Heavy Relative",
        "shape_rule": "قمة محايدة مع ذيل ممتد وثقيل",
        "visual_purpose": "موازنة عرض الفك بإضافة ثقل بصري أعلى",
    },
    # وجه مربعي — تليين الزوايا
    "Square": {
        "arch_type": "Soft Arch",
        "arch_position": "Slightly Elevated Soft",
        "tail_direction": "Tapered",
        "tail_weight": "Light",
        "shape_rule": "قمة مرفوعة بزاوية ناعمة",
        "visual_purpose": "كسر حدة الزوايا وإضافة منحنى لتليين المالمح",
    },
    # وجه على شكل قلب — موازنة الجبهة
    "Heart": {
        "arch_type": "Low Soft Arch",
        "arch_position": "Low and Soft",
        "tail_direction": "Tapered Thin",
        "tail_weight": "Thin",
        "shape_rule": "قمة خفيفة منخفضة مع ذيل نحيف",
        "visual_purpose": "موازنة عرض الجبهة وتخفيف الثقل البصري",
    },
    # وجه على شكل ماسة — تليين البروزات
    "Diamond": {
        "arch_type": "Soft Arch",
        "arch_position": "Soft Rounded",
        "tail_direction": "Tapered Light",
        "tail_weight": "Light",
        "shape_rule": "قمة ناعمة مع بداية وذيل خفيف",
        "visual_purpose": "توسيع الجبهة وتليين حدة عظام الخد البارزة",
    },
}


# ══════════════════════════════════════════════════════════════
# RULE 3: BROW CHARACTERISTICS CLASSIFICATION
# ══════════════════════════════════════════════════════════════
# تصنيف الحاجب حسب الخصائص المُقاسة

BROW_ARCH_LEVELS = {
    # Thickness × Length × Arch
    ("Thick", "Long", "Arched"): {
        "natural_appearance": "Bold & Statement",
        "styling_priority": "Define peaks sharply",
        "risk": "Can overwhelm face if not balanced",
    },
    ("Thick", "Long", "Soft Arch"): {
        "natural_appearance": "Full & Expressive",
        "styling_priority": "Enhance natural arch subtly",
        "risk": "May appear heavy; use light colors",
    },
    ("Thick", "Medium", "Arched"): {
        "natural_appearance": "Balanced & Defined",
        "styling_priority": "Amplify arch definition",
        "risk": "None; ideal base",
    },
    ("Thick", "Short", "Arched"): {
        "natural_appearance": "Compact & Strong",
        "styling_priority": "Extend tail slightly",
        "risk": "Can look severe; soften with color",
    },
    ("Medium", "Long", "Soft Arch"): {
        "natural_appearance": "Natural & Approachable",
        "styling_priority": "Groom and define subtly",
        "risk": "Requires regular maintenance",
    },
    ("Medium", "Medium", "Soft Arch"): {
        "natural_appearance": "Harmonious",
        "styling_priority": "Standard definition",
        "risk": "None",
    },
    ("Thin", "Long", "Soft Arch"): {
        "natural_appearance": "Delicate & Sparse",
        "styling_priority": "Fill and define",
        "risk": "Requires precise product",
    },
    ("Thin", "Short", "Straight"): {
        "natural_appearance": "Understated",
        "styling_priority": "Full reconstruction",
        "risk": "Needs skilled technique",
    },
}


# ══════════════════════════════════════════════════════════════
# RULE 4: TECHNIQUE & PRODUCT SELECTION — اختيار الأداة والمنتج
# ══════════════════════════════════════════════════════════════

TECHNIQUE_EXECUTION = {
    "Grooming": {
        "tools": ["Clear Gel", "Tinted Gel Light"],
        "method": "تمشيط الشعر لألعلى ثم للخارج (Cascade Outward)",
        "coverage": "الشعر الموجود فقط",
        "finish": "Natural & Unpainted",
        "time_efficiency": "Quick (30 sec)",
    },
    "Definition": {
        "tools": ["Powder", "Pencil (medium)"],
        "method": "تحديد 3 نقاط الارتكاز بدقة + خطوط رفيعة",
        "coverage": "تحديد النقاط فقط",
        "finish": "Defined but Natural",
        "time_efficiency": "Medium (2-3 min)",
    },
    "Sculpting": {
        "tools": ["Pencil Fine", "Powder + Brush 45°"],
        "method": "ضربات ريشة بزاوية 45° تحاكي نمو الشعر",
        "coverage": "ملء الفراغات + تعريف الشكل",
        "finish": "Dense & Natural",
        "time_efficiency": "Longer (5-7 min)",
    },
    "Bold Precision": {
        "tools": ["Brow Liner", "Bold Definer Pencil"],
        "method": "رسم حاد ومحدد + رفع قمة عالية جدا",
        "coverage": "كامل الحاجب بخط حاد",
        "finish": "Dramatic & Precise",
        "time_efficiency": "Slow (8-10 min)",
    },
}


# ══════════════════════════════════════════════════════════════
# RULE 5: COLOR INTENSITY & UNDERTONE MATCHING
# ══════════════════════════════════════════════════════════════

BROW_COLOR_INTENSITY = {
    "Sheer": {
        "pigment": 20,
        "coverage": "Transparent",
        "occasion": "work",
        "description": "تلميح طفيف = لا يُرى إلا عن قرب",
    },
    "Natural": {
        "pigment": 60,
        "coverage": "Semi-opaque",
        "occasion": "party",
        "description": "لون طبيعي = يُرى بوضوح لكن ليس درامي",
    },
    "Strong": {
        "pigment": 85,
        "coverage": "Opaque",
        "occasion": "photography",
        "description": "قوي = مرئي تحت الأضواء والكاميرا",
    },
    "Bold": {
        "pigment": 100,
        "coverage": "Full Opaque",
        "occasion": "wedding",
        "description": "جريء = درامي تحت جميع الإضاءات",
    },
}


# ══════════════════════════════════════════════════════════════
# RULE 6: AUTOMATIC EYEBROW GRADIENT
# ══════════════════════════════════════════════════════════════
# التدرج التلقائي: سميك من الداخل → نحيف للخارج

GRADIENT_RULE = {
    "logic": "التدرج التلقائي: يبدأ الحاجب كثيفا من الداخل ويصبح نحيفا نحو الخارج",
    "zones": {
        "start_zone": {
            "width": "100% (full density)",
            "taper": "No taper",
            "description": "البداية كثيفة وقوية",
        },
        "peak_zone": {
            "width": "85-90% (slight taper)",
            "taper": "Subtle",
            "description": "القمة كثيفة لكن أقل قليلا من البداية",
        },
        "tail_zone": {
            "width": "40-60% (heavy taper)",
            "taper": "Significant",
            "description": "النهاية نحيفة وخفيفة = تنتهي في خط رفيع",
        },
    },
    "purpose": "خلق وهم الحواجب المثالية بتدرج طبيعي",
}


# ══════════════════════════════════════════════════════════════
# RULE 7: LIFTING MECHANICS — آلية الرفع البصري
# ══════════════════════════════════════════════════════════════

LIFTING_MECHANICS = {
    "upward_cascade": {
        "direction": "للأعلى ثم للخارج (Cascade Outward)",
        "purpose": "ضمان بقاء طاقة الوجه صاعدة وشابة",
        "execution": "تمشيط الشعر بحركة طبيعية نحو الأعلى",
    },
    "arch_position": {
        "rule": "كلما ارتفعت القمة → زادت طاقة الرفع",
        "chart": {
            "Low": "مهدئ وناعم",
            "Moderate": "متوازن",
            "High": "درامي ورفع قصوى",
        },
    },
    "tail_extension": {
        "rule": "ذيل ممتد وطويل = سحب بصري خارجي نحو الأعلى",
        "effect": "يعطي إيحاء بوجه أطول وأنحف",
    },
}


# ══════════════════════════════════════════════════════════════
# FUNCTION: GET BROW RECOMMENDATION
# ══════════════════════════════════════════════════════════════

def get_brow_recommendation(
    brow_classification: dict,  # من analyze_brows في face_analysis.py
    face_shape: str,            # Oval / Round / Rectangular
    occasion: str = "work",     # work / party / photography / wedding
    skin_tone: str = "warm",    # warm / cool
):
    """
    استخرج التوصيات الكاملة للحاجب بناءً على:
      1. خصائص الحاجب الطبيعية (thickness, length, arch, shape)
      2. شكل الوجه (face_shape)
      3. المناسبة (occasion)
      4. لون البشرة (للون الحاجب)
    
    العودة: dict شامل بجميع التفاصيل
    """
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STEP 1: استخرج الأساليب حسب المناسبة
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    occasion_base = BROW_STYLE_BY_OCCASION.get(occasion, BROW_STYLE_BY_OCCASION["work"])
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STEP 2: استخرج التصحيحات حسب شكل الوجه
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    face_correction = BROW_CORRECTION_BY_FACE_SHAPE.get(
        face_shape,
        BROW_CORRECTION_BY_FACE_SHAPE["Oval"]
    )
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STEP 3: احصل على خصائص الحاجب الطبيعية
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    thickness = brow_classification.get("Thickness", "Medium")
    length = brow_classification.get("Length", "Medium")
    shape = brow_classification.get("Shape", "Soft Arch")
    position = brow_classification.get("Position", "Normal")
    spacing = brow_classification.get("Spacing", "Normal")
    symmetry = brow_classification.get("Symmetry", "Symmetrical")
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STEP 4: اختر الأداة والتقنية
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    technique_key = occasion_base.get("technique", "Grooming")
    technique_details = TECHNIQUE_EXECUTION.get(technique_key, {})
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STEP 5: اختر شدة اللون
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    color_intensity_key = occasion_base.get("color_intensity", "Natural")
    color_intensity_details = BROW_COLOR_INTENSITY.get(color_intensity_key, {})
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STEP 6: تحديد لون الحاجب حسب البشرة
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    brow_color_mapping = {
        "warm": {
            "fair": "Warm Brown / Auburn",
            "medium": "Medium Brown",
            "dark": "Rich Brown / Dark Blonde",
        },
        "cool": {
            "fair": "Soft Taupe / Grey Brown",
            "medium": "Ash Brown / Cool Brown",
            "dark": "Cool Dark Brown / Ash",
        },
    }
    
    # (في تطبيق حقيقي، سيتم استخراج عمق البشرة من تحليل الصورة)
    brow_color = "Dark Brown"  # default
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STEP 7: بناء الشرح التفصيلي
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    explanation_parts = [
        f"🎨 شكل الوجه '{face_shape}': {face_correction['visual_purpose']}",
        f"📐 الحاجب الطبيعي: {thickness} + {length} + {shape}",
        f"✨ المناسبة '{occasion}': {occasion_base['description']}",
        f"🔧 التقنية: {technique_details.get('method', 'N/A')}",
        f"🎯 القمة: {face_correction['arch_type']} → {face_correction['arch_position']}",
        f"➡️ الذيل: {face_correction['tail_direction']} ({face_correction['tail_weight']})",
    ]
    
    return {
        # ── الأسلوب الأساسي ──
        "style": occasion_base.get("style", "Natural Grooming"),
        "occasion": occasion,
        "face_shape": face_shape,
        
        # ── خصائص الحاجب الطبيعية ──
        "natural_brow": {
            "thickness": thickness,
            "length": length,
            "shape": shape,
            "position": position,
            "spacing": spacing,
            "symmetry": symmetry,
        },
        
        # ── الهندسة والتصحيح ──
        "arch_correction": {
            "arch_type": face_correction["arch_type"],
            "arch_position": face_correction["arch_position"],
            "visual_purpose": face_correction["visual_purpose"],
        },
        
        "tail_correction": {
            "direction": face_correction["tail_direction"],
            "weight": face_correction["tail_weight"],
            "rule": face_correction["shape_rule"],
        },
        
        # ── التقنية والمنتج ──
        "technique": {
            "name": technique_key,
            "tools": technique_details.get("tools", []),
            "method": technique_details.get("method", ""),
            "coverage": technique_details.get("coverage", ""),
            "finish": technique_details.get("finish", ""),
            "time_efficiency": technique_details.get("time_efficiency", ""),
        },
        
        # ── اللون ──
        "color": {
            "tone": brow_color,
            "intensity": color_intensity_key,
            "pigment_level": color_intensity_details.get("pigment", 0),
            "coverage": color_intensity_details.get("coverage", ""),
        },
        
        # ── الآليات البصرية ──
        "lifting_mechanics": {
            "direction": LIFTING_MECHANICS["upward_cascade"]["direction"],
            "purpose": LIFTING_MECHANICS["upward_cascade"]["purpose"],
            "tail_extends": "Yes - extends beyond natural eye corner",
        },
        
        "gradient": GRADIENT_RULE,
        
        # ── الشرح ──
        "explanation": "\n".join(explanation_parts),
    }


# ══════════════════════════════════════════════════════════════
# PRINT HELPER
# ══════════════════════════════════════════════════════════════

def print_brow_recommendation(side: str, recommendation: dict):
    """
    طباعة توصيات الحاجب بتنسيق منظم
    """
    print(f"\n{'='*70}")
    print(f"  EYEBROW RECOMMENDATION — {side}")
    print(f"{'='*70}\n")
    
    # الأسلوب الأساسي
    print(f"  Style:        {recommendation['style']}")
    print(f"  Occasion:     {recommendation['occasion']}")
    print(f"  Face Shape:   {recommendation['face_shape']}\n")
    
    # الخصائص الطبيعية
    print(f"  Natural Brow Characteristics:")
    for k, v in recommendation["natural_brow"].items():
        print(f"    • {k.capitalize()}: {v}")
    print()
    
    # التصحيحات
    print(f"  Arch Correction:")
    for k, v in recommendation["arch_correction"].items():
        print(f"    • {k.replace('_', ' ').title()}: {v}")
    print()
    
    print(f"  Tail Correction:")
    for k, v in recommendation["tail_correction"].items():
        print(f"    • {k.replace('_', ' ').title()}: {v}")
    print()
    
    # التقنية والمنتج
    print(f"  Technique & Product:")
    for k, v in recommendation["technique"].items():
        if isinstance(v, list):
            print(f"    • {k.replace('_', ' ').title()}: {', '.join(v)}")
        else:
            print(f"    • {k.replace('_', ' ').title()}: {v}")
    print()
    
    # اللون
    print(f"  Color:")
    for k, v in recommendation["color"].items():
        print(f"    • {k.replace('_', ' ').title()}: {v}")
    print()
    
    # الشرح
    print(f"  💡 Explanation:")
    for line in recommendation["explanation"].split("\n"):
        print(f"     {line}")
    print()


# ══════════════════════════════════════════════════════════════
# DEMO / TEST
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # مثال: حاجب سميك متوسط الطول مع قوس ناعم
    sample_brow_classification = {
        "Thickness": "Medium",
        "Length": "Medium",
        "Shape": "Soft Arch",
        "Position": "Normal",
        "Spacing": "Normal",
        "Symmetry": "Symmetrical",
    }
    
    print("\n" + "="*70)
    print("  BROW MAKEUP RULES — SYSTEM TEST")
    print("="*70)
    
    for occasion in ["work", "party", "photography", "wedding"]:
        for face_shape in ["Oval", "Round", "Rectangular"]:
            rec = get_brow_recommendation(
                brow_classification=sample_brow_classification,
                face_shape=face_shape,
                occasion=occasion,
                skin_tone="warm",
            )
            print_brow_recommendation(
                f"{face_shape} | {occasion.upper()}",
                rec
            )