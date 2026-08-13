# -*- coding: utf-8 -*-
"""
lip_makeup_rules.py — Experta-based Expert System (كامل بالعربي)
===========================================================
تصنيف وتصحيح الشفاه + اختيار لون الروج حسب البشرة والمناسبة
"""

# ✅ MUST BE FIRST: Python 3.10+ Compatibility Fix
import compat_fix

from experta import *
import json


# ══════════════════════════════════════════════════════
# FACTS
# ══════════════════════════════════════════════════════

class LipAnalysis(Fact):
    volume = Field(str)
    balance = Field(str)
    width = Field(str)
    symmetry = Field(str)
    cupid_bow = Field(str)
    corners = Field(str)


class SkinProfile(Fact):
    undertone = Field(str)
    depth = Field(str)


class OccasionContext(Fact):
    occasion = Field(str)


class LipShapeCategory(Fact):
    category = Field(str)
    name_ar = Field(str)
    correction_style = Field(str)
    technique = Field(str)
    reason = Field(str)


class LipColorMatch(Fact):
    undertone = Field(str)
    palette = Field(str)
    colors = Field(str)


class LipOccasionStyle(Fact):
    occasion = Field(str)
    style = Field(str)
    product = Field(str)
    texture = Field(str)


class LipRecommendation(Fact):
    shape_category = Field(str)
    lip_colors = Field(str)
    occasion = Field(str)
    complete = Field(bool, default=False)


# ══════════════════════════════════════════════════════
# RULES
# ══════════════════════════════════════════════════════

class LipRulesKB(KnowledgeEngine):

    # ──── Rule 1: تصنيف حالة الشفاه ────

    @Rule(LipAnalysis(volume='Thin', balance='Balanced'))
    def thin_lips_detected(self):
        self.declare(LipShapeCategory(
            category='Thin', name_ar='شفاه رقيقة',
            correction_style='تكبير للخارج (Overline)',
            technique='رسم لاينر الشفاه خارج الحد الطبيعي للشفة',
            reason='لخلق إيحاء بامتلاء أكبر'))

    @Rule(LipAnalysis(volume='Thin', balance='Upper Fuller'))
    def thin_upper_lip_detected(self):
        self.declare(LipShapeCategory(
            category='Upper Thin', name_ar='شفة علوية رقيقة',
            correction_style='موازنة النسبة',
            technique='رسم الخط أعلى الحد الطبيعي للشفة العلوية',
            reason='لتحقيق التماثل بين الشفتين العلوية والسفلى'))

    @Rule(LipAnalysis(volume='Thin', balance='Lower Fuller'))
    def thin_lower_lip_detected(self):
        self.declare(LipShapeCategory(
            category='Lower Thin', name_ar='شفة سفلى رقيقة',
            correction_style='موازنة النسبة',
            technique='رسم الخط أسفل الحد الطبيعي للشفة السفلى',
            reason='لضمان التوازن البصري وتماثل الفم'))

    @Rule(LipAnalysis(volume='Medium', balance='Upper Fuller'))
    def medium_upper_fuller(self):
        self.declare(LipShapeCategory(
            category='Upper Thin', name_ar='شفة علوية أرق نسبياً',
            correction_style='موازنة النسبة',
            technique='رسم الخط أعلى الحد الطبيعي للشفة العلوية',
            reason='لتحقيق التماثل بين الشفتين'))

    @Rule(LipAnalysis(volume='Medium', balance='Lower Fuller'))
    def medium_lower_fuller(self):
        self.declare(LipShapeCategory(
            category='Lower Thin', name_ar='شفة سفلى أرق نسبياً',
            correction_style='موازنة النسبة',
            technique='رسم الخط أسفل الحد الطبيعي للشفة السفلى',
            reason='لضمان التماثل بين الشفتين'))

    @Rule(LipAnalysis(volume='Full', width='Wide'))
    def very_large_lips(self):
        self.declare(LipShapeCategory(
            category='Very Large', name_ar='شفاه كبيرة جداً',
            correction_style='تصغير بصري',
            technique='رسم الخط داخل الحد الطبيعي للشفة، مع استخدام ألوان متوسطة إلى داكنة',
            reason='لتقليل المساحة الظاهرة للشفاه'))

    @Rule(LipAnalysis(volume='Full', balance='Balanced'))
    def full_balanced_lips(self):
        self.declare(LipShapeCategory(
            category='Full & Balanced', name_ar='شفاه ممتلئة ومتوازنة',
            correction_style='الحفاظ على الشكل الطبيعي',
            technique='رسم لاينر الشفاه على الحد الطبيعي للشفة',
            reason='الشفاه ممتلئة أصلاً وتُعد المعيار الجمالي المثالي'))

    @Rule(LipAnalysis(volume='Medium', balance='Balanced'))
    def medium_balanced_lips(self):
        self.declare(LipShapeCategory(
            category='Full & Balanced', name_ar='شفاه متوسطة ومتوازنة',
            correction_style='الحفاظ على الشكل الطبيعي',
            technique='رسم لاينر الشفاه على الحد الطبيعي للشفة',
            reason='متوازنة وتحتاج فقط للتحديد'))

    # ──── Rule 2: لون الروج حسب الأندرتون ────

    @Rule(SkinProfile(undertone='Warm'))
    def warm_lip_color(self):
        self.declare(LipColorMatch(undertone='Warm', palette='أساس ذهبي/خوخي',
                                    colors='درجات مرجانية وخوخية'))

    @Rule(SkinProfile(undertone='Cool'))
    def cool_lip_color(self):
        self.declare(LipColorMatch(undertone='Cool', palette='أساس بارد',
                                    colors='درجات التوت والوردي المائل للأزرق (ماوف/راسبيري)'))

    # ──── Rule 3: المنتج والملمس حسب المناسبة ────

    @Rule(OccasionContext(occasion='work'))
    def work_lip_style(self):
        self.declare(LipOccasionStyle(occasion='work', style='تورّد طبيعي',
                                       product='صبغة شفاه أو أحمر شفاه مطفأ فاتح جداً',
                                       texture='مطفأ — يمنح مظهراً صحياً ونابضاً بالحياة'))

    @Rule(OccasionContext(occasion='university'))
    def university_lip_style(self):
        self.declare(LipOccasionStyle(occasion='university', style='تورّد طبيعي',
                                       product='صبغة شفاه أو أحمر شفاه مطفأ فاتح جداً',
                                       texture='مطفأ — يمنح مظهراً صحياً ونابضاً بالحياة'))

    @Rule(OccasionContext(occasion='evening'))
    def evening_lip_style(self):
        self.declare(LipOccasionStyle(occasion='evening', style='إطلالة متوازنة',
                                       product='أحمر شفاه بصبغة قوية، متوازن مع مكياج العين',
                                       texture='ساتان أو كريمي — يمنح عمقاً ثلاثي الأبعاد'))

    @Rule(OccasionContext(occasion='party'))
    def party_lip_style(self):
        self.declare(LipOccasionStyle(occasion='party', style='إطلالة متوازنة',
                                       product='أحمر شفاه بصبغة قوية، متوازن مع مكياج العين',
                                       texture='ساتان أو كريمي — يمنح عمقاً ثلاثي الأبعاد'))

    @Rule(OccasionContext(occasion='photo'))
    def photo_lip_style(self):
        self.declare(LipOccasionStyle(occasion='photo', style='تعريف حاد عالي الدقة',
                                       product='أحمر شفاه مطفأ مع تحديد حاد جداً للحواف',
                                       texture='مطفأ بالكامل — يمنع تشتت انعكاس الفلاش'))

    @Rule(OccasionContext(occasion='wedding'))
    def wedding_lip_style(self):
        self.declare(LipOccasionStyle(occasion='wedding', style='شفاه فاخرة وممتلئة',
                                       product='أحمر شفاه غني مع طبقة لمعان توضع عمودياً بمنتصف الشفة فقط',
                                       texture='لامع (بالمنتصف فقط، فوق طبقة أساس غنية)'))

    # ──── Rule 4: التوصية النهائية ────

    @Rule(LipShapeCategory(category=MATCH.category),
          LipColorMatch(colors=MATCH.colors),
          LipOccasionStyle(occasion=MATCH.occasion))
    def final_lip_recommendation(self, category, colors, occasion):
        self.declare(LipRecommendation(shape_category=category, lip_colors=colors, occasion=occasion, complete=True))


# ══════════════════════════════════════════════════════
# ENGINE
# ══════════════════════════════════════════════════════

class LipMakeupEngine(LipRulesKB):
    """محرك مكياج الشفاه"""

    def __init__(self):
        super().__init__()

    def analyze_lips(self, lip_data):
        self.reset()
        self.declare(
            LipAnalysis(
                volume=lip_data.get('volume', 'Medium'),
                balance=lip_data.get('balance', 'Balanced'),
                width=lip_data.get('width', 'Average'),
                symmetry=lip_data.get('symmetry', 'Symmetrical'),
                cupid_bow=lip_data.get('cupid_bow', 'Soft'),
                corners=lip_data.get('corners', 'Neutral')
            ),
            SkinProfile(undertone=lip_data.get('undertone', 'Warm'), depth=lip_data.get('depth', 'Medium')),
            OccasionContext(occasion=lip_data.get('occasion', 'work'))
        )
        self.run()
        return self._extract_results()

    def _extract_results(self):
        results = {'shape': None, 'color': None, 'occasion': None, 'recommendation': None}

        for fact in self.facts.values():
            if isinstance(fact, LipShapeCategory):
                results['shape'] = {
                    'category': fact.get('category'),
                    'name_ar': fact.get('name_ar'),
                    'correction': fact.get('correction_style'),
                    'technique': fact.get('technique'),
                    'reason': fact.get('reason'),
                    'arrow_target': 'lip_border'
                }
            elif isinstance(fact, LipColorMatch):
                results['color'] = {'undertone': fact.get('undertone'), 'palette': fact.get('palette'),
                                     'colors': fact.get('colors'),'arrow_target': 'lips'}
            elif isinstance(fact, LipOccasionStyle):
                results['occasion'] = {'occasion': fact.get('occasion'), 'style': fact.get('style'),
                                        'product': fact.get('product'), 'texture': fact.get('texture')}
            elif isinstance(fact, LipRecommendation):
                results['recommendation'] = {'shape': fact.get('shape_category'), 'colors': fact.get('lip_colors'),
                                              'occasion': fact.get('occasion'), 'complete': fact.get('complete')}

        return results


if __name__ == "__main__":
    engine = LipMakeupEngine()
    example = {'volume': 'Medium', 'balance': 'Lower Fuller', 'width': 'Average', 'undertone': 'Cool',
               'depth': 'Medium', 'occasion': 'wedding'}
    result = engine.analyze_lips(example)
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))