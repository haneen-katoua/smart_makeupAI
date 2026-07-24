# -*- coding: utf-8 -*-
"""
eye_makeup_rules.py — Experta-based Expert System (كامل بالعربي)
===========================================================
نظام خبير قائم على Experta بدون أي if/else في القواعس
"""

# ✅ MUST BE FIRST: Python 3.10+ Compatibility Fix
import compat_fix

from experta import *
import json


# ══════════════════════════════════════════════════════
# FACTS
# ══════════════════════════════════════════════════════

class EyeAnalysis(Fact):
    geo_shape = Field(str, default='Almond')
    eye_type = Field(str, default='Normal')
    combined = Field(str)
    size = Field(str, default='Normal')
    corner = Field(str, default='Neutral')
    side = Field(str, default='Both')


class EyeSpacing(Fact):
    inter_eye_ratio = Field(float, default=0.35)
    classification = Field(str, default='Normal')


class OccasionContext(Fact):
    occasion = Field(str)


class SkinProfile(Fact):
    undertone = Field(str)
    depth = Field(str)


class EyeMakeupCategory(Fact):
    """فئة مكياج العين المختارة"""
    category = Field(str)
    name_ar = Field(str)
    goal = Field(str)
    priority = Field(int, default=0)


class EyeSpacingCorrection(Fact):
    classification = Field(str)
    name_ar = Field(str)
    rule = Field(str)


class OccasionPlan(Fact):
    style = Field(str)
    texture = Field(str)
    lashes = Field(str)
    eyeliner = Field(str)


class EyeMakeupRecommendation(Fact):
    rule_category = Field(str)
    rule_category_ar = Field(str)
    goal = Field(str)
    style = Field(str)
    spacing_correction = Field(str)
    complete = Field(bool, default=False)


# ══════════════════════════════════════════════════════
# التفسيرات الحقيقية لكل شكل عين (منقولة من ملف "الخبرة النهائية")
# تُستخدم كمصدر واحد للحقيقة حتى لا تختلف القاعدة المخصّصة عن
# القاعدة الاحتياطية (normal_eye_detected) في نفس الشكل
# ══════════════════════════════════════════════════════

EYE_SHAPE_INFO = {
    'Hooded': {
        'name_ar': 'العين المبطّنة (Hooded)',
        'goal': ('تم اختيار تقنية الكات كريز الوهمي (Floating/Illusion Crease) برسم ظل اصطناعي فوق '
                 'الطية الطبيعية للجفن، لخلق عمق بصري يقلل من بروز التبطينة ويجعل الجفن الثابت يبدو '
                 'كجفن متحرك واسع، مع استبعاد الآيلاينر الكلاسيكي لأنه ينكسر تحت الجلد المترهل'),
    },
    'Protruding': {
        'name_ar': 'العين الجاحظة (Protruding)',
        'goal': ('تم اعتماد تقنية الدمج العمودي (Smoky) أو تحديد المحجر (Banana) بوضع ألوان داكنة '
                 'ومطفأة على الجفن المتحرك وكسرة العين، لتقليل المساحة البارزة وجعل العين تبدو أكثر '
                 'تراجعاً بصرياً، مع منع الألوان الفاتحة أو اللامعة في منتصف الجفن لأنها تزيد من مظهر الجحوظ'),
    },
    'Droopy': {
        'name_ar': 'العين الناعسة (Droopy)',
        'goal': ('تم اعتماد تقنية الرفع البصري (Illusion Lifting) بتوجيه كل الخطوط (ظلال وآيلاينر) '
                 'نحو الأعلى قبل نهاية الرموش الطبيعية، لرفع الزاوية الخارجية للعين ومنع ظهورها بمظهر '
                 'حزين أو هابط، مع تجنب اللون الداكن أسفل الزاوية الخارجية لأنه يسحب العين للأسفل ويبرز نعاسها'),
    },
    'Deep-set': {
        'name_ar': 'العين الغائرة (Deep-set)',
        'goal': ('تم اعتماد تقنية التقديم البصري (Advancing) بوضع ألوان فاتحة ومشرقة على كامل الجفن '
                 'المتحرك لسحب العين للخارج بصرياً، مع استخدام ألوان متوسطة (وليست داكنة) في الكسرة، '
                 'ومنع الألوان الداكنة جداً لأنها تزيد من عمق التجويف وتجعل العين تبدو غارقة'),
    },
    'Almond': {
        'name_ar': 'العين اللوزية (Almond)',
        'goal': ('تم اختيار هذا الستايل لأن العين لوزية ومتوازنة تشريحياً، مما يجعلها القالب المثالي '
                 'لأي تصميم مكياج دون الحاجة لتقنيات تصحيحية، مع تعزيز السحبة الطبيعية الجذابة للعين '
                 'وإبراز توازن زواياها'),
    },
    'Round': {
        'name_ar': 'العين الدائرية (Round)',
        'goal': ('تم اعتماد تقنية البنانا (Banana) أو الكسرة المقطوعة جزئياً (Half Cut Crease) بدمج '
                 'الظلال للأعلى وللخارج عند الزوايا الخارجية، لكسر حدة التدوير ومنح العين سحبة أفقية '
                 'توحي بالطول، مع فرض آيلاينر يبدأ رفيعاً من الداخل ويزداد سمكاً تدريجياً نحو الخارج'),
    },
}


# ══════════════════════════════════════════════════════
# RULES
# ══════════════════════════════════════════════════════

class EyeMakeupRulesKB(KnowledgeEngine):

    # ──── Rule 1: تصنيف نوع العين الوظيفي ────

    @Rule(EyeAnalysis(eye_type='Hooded'))
    def hooded_eye_detected(self):
        info = EYE_SHAPE_INFO['Hooded']
        self.declare(EyeMakeupCategory(category='Hooded', name_ar=info['name_ar'],
                                        goal=info['goal'], priority=1))

    @Rule(EyeAnalysis(eye_type='Protruding'))
    def protruding_eye_detected(self):
        info = EYE_SHAPE_INFO['Protruding']
        self.declare(EyeMakeupCategory(category='Protruding', name_ar=info['name_ar'],
                                        goal=info['goal'], priority=2))

    @Rule(EyeAnalysis(eye_type='Droopy'))
    def droopy_eye_detected(self):
        info = EYE_SHAPE_INFO['Droopy']
        self.declare(EyeMakeupCategory(category='Droopy', name_ar=info['name_ar'],
                                        goal=info['goal'], priority=3))

    @Rule(EyeAnalysis(eye_type='Deep-set'))
    def deep_set_eye_detected(self):
        info = EYE_SHAPE_INFO['Deep-set']
        self.declare(EyeMakeupCategory(category='Deep-set', name_ar=info['name_ar'],
                                        goal=info['goal'], priority=4))

    @Rule(EyeAnalysis(eye_type='Almond'))
    def almond_eye_detected(self):
        info = EYE_SHAPE_INFO['Almond']
        self.declare(EyeMakeupCategory(category='Almond', name_ar=info['name_ar'],
                                        goal=info['goal'], priority=5))

    @Rule(EyeAnalysis(eye_type='Round'))
    def round_eye_detected(self):
        info = EYE_SHAPE_INFO['Round']
        self.declare(EyeMakeupCategory(category='Round', name_ar=info['name_ar'],
                                        goal=info['goal'], priority=6))

    @Rule(EyeAnalysis(eye_type='Normal', geo_shape=MATCH.geo_shape))
    def normal_eye_detected(self, geo_shape):
        # عند عدم توفّر تصنيف وظيفي دقيق (Hooded/Protruding/...)، نعتمد على
        # الشكل الهندسي (geo_shape) ونستخدم نفس التفسير الحقيقي من ملف
        # الخبرة النهائية بدل نص عام لا معنى له
        category_key = {'Round': 'Round', 'Almond': 'Almond', 'Average': 'Almond'}.get(geo_shape, 'Almond')
        info = EYE_SHAPE_INFO[category_key]
        self.declare(EyeMakeupCategory(category=category_key, name_ar=info['name_ar'],
                                        goal=info['goal'], priority=7))

    # ──── Rule 2: تصنيف مسافة العينين ────

    @Rule(EyeSpacing(inter_eye_ratio=lambda x: x is not None and x < 0.32))
    def close_set_eyes(self):
        self.declare(EyeSpacingCorrection(
            classification='Close-set', name_ar='عيون متقاربة (Close-set)',
            rule='يتم فرض لون الإضاءة (Highlight) في الزاوية الداخلية (مدمع العين) لتوسيع المسافة بين العينين بصرياً'))

    @Rule(EyeSpacing(inter_eye_ratio=lambda x: x is not None and x > 0.42))
    def wide_set_eyes(self):
        self.declare(EyeSpacingCorrection(
            classification='Wide-set', name_ar='عيون متباعدة (Wide-set)',
            rule='يتم فرض ظل متوسط إلى داكن (من لون النحت أو الأساس) في الزاوية الداخلية لتقريب المسافة بين العينين بصرياً'))

    @Rule(EyeSpacing(inter_eye_ratio=lambda x: x is None or (0.32 <= x <= 0.42)))
    def normal_set_eyes(self):
        self.declare(EyeSpacingCorrection(
            classification='Normal', name_ar='مسافة طبيعية بين العينين',
            rule='المسافة بين العينين متوازنة، ولذلك لا حاجة لأي تصحيح لوني في الزاوية الداخلية'))

    # ──── Rule 3: أسلوب المناسبة ────

    @Rule(EyeMakeupCategory(category=MATCH.category), OccasionContext(occasion='work'))
    def work_occasion_style(self, category):
        styles = {'Hooded': 'مطفأ طبيعي دقيق بتقنية الجناح المصغّر',
                  'Protruding': 'سموكي ناعم',
                  'Almond': 'تعريف طبيعي',
                  'Round': 'بنانا ناعمة',
                  'Droopy': 'رفع طبيعي خفيف',
                  'Deep-set': 'إضاءة طبيعية'}
        style = styles.get(category, 'مكياج طبيعي')
        self.declare(OccasionPlan(style=style, texture='مطفأ بالكامل (ألوان محايدة/ترابية)',
                                   lashes='ماسكرا تكثيف عند الزاوية الخارجية', eyeliner='آيلاينر بني جاف'))

    @Rule(EyeMakeupCategory(category=MATCH.category), OccasionContext(occasion='university'))
    def university_occasion_style(self, category):
        styles = {'Hooded': 'مطفأ طبيعي دقيق بتقنية الجناح المصغّر',
                  'Protruding': 'سموكي ناعم',
                  'Almond': 'تعريف طبيعي',
                  'Round': 'بنانا ناعمة',
                  'Droopy': 'رفع طبيعي خفيف',
                  'Deep-set': 'إضاءة طبيعية'}
        style = styles.get(category, 'مكياج طبيعي')
        self.declare(OccasionPlan(style=style, texture='مطفأ بالكامل (ألوان محايدة/ترابية)',
                                   lashes='ماسكرا تكثيف عند الزاوية الخارجية', eyeliner='آيلاينر بني جاف'))

    @Rule(EyeMakeupCategory(category=MATCH.category), OccasionContext(occasion='evening'))
    def evening_occasion_style(self, category):
        styles = {'Hooded': 'سموكي درامي حاد بتقنية الجناح',
                  'Protruding': 'سموكي كثيف بجناح سميك',
                  'Almond': 'سموكي درامي',
                  'Round': 'بنانا جريئة',
                  'Droopy': 'جناح جريء مع سموكي',
                  'Deep-set': 'سموكي متدرّج ناعم'}
        style = styles.get(category, 'سموكي')
        self.declare(OccasionPlan(style=style, texture='شيمر على الجفن المتحرك / غليتر',
                                   lashes='رموش كثيفة 3D', eyeliner='آيلاينر سائل'))

    @Rule(EyeMakeupCategory(category=MATCH.category), OccasionContext(occasion='party'))
    def party_occasion_style(self, category):
        styles = {'Hooded': 'سموكي درامي حاد بتقنية الجناح',
                  'Protruding': 'سموكي كثيف بجناح سميك',
                  'Almond': 'سموكي درامي',
                  'Round': 'بنانا جريئة',
                  'Droopy': 'جناح جريء مع سموكي',
                  'Deep-set': 'سموكي متدرّج ناعم'}
        style = styles.get(category, 'سموكي')
        self.declare(OccasionPlan(style=style, texture='شيمر على الجفن المتحرك / غليتر',
                                   lashes='رموش كثيفة 3D', eyeliner='آيلاينر سائل'))

    @Rule(EyeMakeupCategory(category=MATCH.category), OccasionContext(occasion='photo'))
    def photo_occasion_style(self, category):
        styles = {'Hooded': 'كت كريز مطفأ مع تعتيم بتقنية الجناح',
                  'Protruding': 'بنانا مطفأة مع تعتيم',
                  'Almond': 'نص كت كريز',
                  'Round': 'نص كت كريز مطفأ',
                  'Droopy': 'V خارجي منحوت',
                  'Deep-set': 'نص كت كريز مطفأ'}
        style = styles.get(category, 'مطفأ')
        self.declare(OccasionPlan(style=style, texture='مطفأ بالكامل (لتفادي انعكاس الفلاش)',
                                   lashes='رموش قطة متوسطة / رموش طبيعية', eyeliner='آيلاينر مدمج'))

    @Rule(EyeMakeupCategory(category=MATCH.category), OccasionContext(occasion='wedding'))
    def wedding_occasion_style(self, category):
        styles = {'Hooded': 'كت كريز فاخر بتقنية جناح حريري دقيق',
                  'Protruding': 'سموكي فاخر / بنانا',
                  'Almond': 'سبوت لايت / بنانا',
                  'Round': 'نص كت كريز فاخر',
                  'Droopy': 'أسلوب جناح فاخر',
                  'Deep-set': 'نص كت كريز فاخر'}
        style = styles.get(category, 'سبوت لايت')
        self.declare(OccasionPlan(style=style, texture='لمسة ساتان / لامعة',
                                   lashes='رموش طويلة وكثيفة فاخرة', eyeliner='آيلاينر حريري'))

    # ──── Rule 4: التوصية النهائية ────

    @Rule(EyeMakeupCategory(category=MATCH.category, name_ar=MATCH.name_ar, goal=MATCH.goal),
          OccasionPlan(style=MATCH.style),
          EyeSpacingCorrection(classification=MATCH.spacing_class))
    def final_recommendation(self, category, name_ar, goal, style, spacing_class):
        self.declare(EyeMakeupRecommendation(rule_category=category, rule_category_ar=name_ar,
                                              goal=goal, style=style, spacing_correction=spacing_class, complete=True))


# ══════════════════════════════════════════════════════
# ENGINE
# ══════════════════════════════════════════════════════

class EyeMakeupEngine(EyeMakeupRulesKB):
    """محرك مكياج العيون بـ Forward Chaining"""

    def __init__(self):
        super().__init__()

    def analyze_eye(self, eye_data):
        self.reset()
        self.declare(
            EyeAnalysis(
                geo_shape=eye_data.get('geo_shape', 'Almond'),
                eye_type=eye_data.get('eye_type', 'Normal'),
                combined=eye_data.get('combined', ''),
                size=eye_data.get('size', 'Normal'),
                corner=eye_data.get('corner', 'Neutral'),
                side=eye_data.get('side', 'Both')
            ),
            EyeSpacing(
                inter_eye_ratio=eye_data.get('inter_eye_ratio'),
                classification=eye_data.get('classification', 'Normal')
            ),
            OccasionContext(occasion=eye_data.get('occasion', 'work'))
        )
        self.run()
        return self._extract_results()

    def _extract_results(self):
        """
        استخراج النتائج — لا يعتمد فقط على التوصية النهائية المجمّعة،
        بل يخزّن كل فئة على حدة كي لا تختفي نتيجة العين إذا لم تكتمل
        سلسلة المطابقة الكاملة لأي سبب.
        """
        facts_dict = {}
        for fact in self.facts.values():
            if isinstance(fact, EyeMakeupCategory):
                facts_dict['category'] = {
                    'category': fact['category'],
                    'name_ar': fact['name_ar'],
                    'goal': fact['goal'],
                }
            elif isinstance(fact, EyeMakeupRecommendation):
                facts_dict['recommendation'] = {
                    'category': fact['rule_category'],
                    'category_ar': fact['rule_category_ar'],
                    'goal': fact['goal'],
                    'style': fact['style'],
                    'spacing': fact['spacing_correction'],
                }
            elif isinstance(fact, OccasionPlan):
                facts_dict['plan'] = {
                    'style': fact['style'],
                    'texture': fact['texture'],
                    'lashes': fact['lashes'],
                    'eyeliner': fact['eyeliner'],
                }
            elif isinstance(fact, EyeSpacingCorrection):
                facts_dict['spacing'] = {
                    'classification': fact['classification'],
                    'name_ar': fact['name_ar'],
                    'rule': fact['rule'],
                }

        return facts_dict if facts_dict else None


if __name__ == "__main__":
    engine = EyeMakeupEngine()
    example = {'geo_shape': 'Almond', 'eye_type': 'Normal', 'inter_eye_ratio': 0.35, 'occasion': 'evening'}
    result = engine.analyze_eye(example)
    print(json.dumps(result, indent=2, ensure_ascii=False))