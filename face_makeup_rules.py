# -*- coding: utf-8 -*-
"""
face_makeup_rules.py — Experta-based Expert System (Face Contour / Blush / Highlight)
======================================================================================
مبني على "الخبرة النهائية": يحدد شكل الوجه، ثم يبني توصية النحت والبلاشر والهاياليت،
ثم يلوّن البلاشر حسب البشرة، ثم يضبط الشفافية حسب المناسبة واستراتيجية العين.
"""

# ✅ MUST BE FIRST: Python 3.10+ Compatibility Fix
import compat_fix

from experta import *
import json


# ══════════════════════════════════════════════════════
# FACTS
# ══════════════════════════════════════════════════════

class FaceShapeAnalysis(Fact):
    shape = Field(str)
    votes = Field(dict)


class SkinProfile(Fact):
    undertone = Field(str)
    depth = Field(str)


class FaceFullness(Fact):
    fullness = Field(str, default='Full')


class EyeMakeupStrategy(Fact):
    strategy = Field(str, default='Monochromatic')


class OccasionContext(Fact):
    occasion = Field(str)


class FaceShapeCategory(Fact):
    shape = Field(str)
    name_ar = Field(str)
    goal = Field(str)
    priority = Field(int, default=0)


class SculptRule(Fact):
    placement = Field(str)
    purpose = Field(str)


class BlushRule(Fact):
    placement = Field(str)
    purpose = Field(str)


class HighlightRule(Fact):
    placement = Field(str)
    purpose = Field(str)


class BlushColorMatch(Fact):
    undertone = Field(str)
    depth = Field(str)
    base_color = Field(str)
    palette = Field(str)


class BlushAdjustment(Fact):
    strategy = Field(str)
    rule = Field(str)
    opacity = Field(int)


class BlushTexture(Fact):
    occasion = Field(str)
    finish = Field(str)
    transparency = Field(str)
    description = Field(str)


class FaceContourBlushRecommendation(Fact):
    shape = Field(str)
    base_color = Field(str)
    occasion = Field(str)
    complete = Field(bool, default=False)


# ══════════════════════════════════════════════════════
# RULES
# ══════════════════════════════════════════════════════

class FaceContourRulesKB(KnowledgeEngine):

    # ──── الوجه البيضاوي ────

    @Rule(FaceShapeAnalysis(shape='Oval'), FaceFullness(fullness='Full'))
    def oval_full_face(self):
        self.declare(
            FaceShapeCategory(shape='Oval', name_ar='الوجه البيضاوي (Face Oval)',
                               goal='الحفاظ على التوازن المثالي وتعريف الملامح', priority=1),
            SculptRule(placement='نحت خفيف جداً فوق البلاشر مباشرة، على عظمة الخد',
                       purpose='زيادة البعد ثلاثي الأبعاد دون كسر توازن الوجه'),
            BlushRule(placement='على تفاحتي الخد فقط، بدمج مسحوب للأعلى باتجاه الأذن',
                      purpose='الحفاظ على النضارة الطبيعية ورفع ملامح الوجه'),
            HighlightRule(placement='تحت عظمة الخد مباشرة فوق خط الكونتور',
                          purpose='تعريف الملامح وإبراز عظمة الخد')
        )

    @Rule(FaceShapeAnalysis(shape='Oval'), FaceFullness(fullness='Thin'))
    def oval_thin_face(self):
        self.declare(
            FaceShapeCategory(shape='Oval', name_ar='الوجه البيضاوي (Face Oval)',
                               goal='الحفاظ على التوازن المثالي مع تفادي مظهر الوجه الغارق', priority=1),
            SculptRule(placement='استبدال الكونتور الداكن ببرونز دافئ خفيف جداً، بدمج دائري في مركز الخد',
                       purpose='منع ظهور "الوجه الغارق" وإعطاء حيوية بدل النحت الحاد'),
            BlushRule(placement='في مركز الخد بدمج ناعم جداً باتجاه الأذن',
                      purpose='إعطاء حجم حيوي للخدود النحيفة'),
            HighlightRule(placement='لمسة بسيطة جداً على جسر الأنف بنفس لون البلاشر',
                          purpose='توحيد الإضاءة وتفادي مظهر النحول الزائد')
        )

    # ──── الوجه الدائري ────

    @Rule(FaceShapeAnalysis(shape='Round'), FaceFullness(fullness='Full'))
    def round_full_face(self):
        self.declare(
            FaceShapeCategory(shape='Round', name_ar='الوجه الدائري (Face Round)',
                               goal='كسر الاستدارة، تقليل العرض، وإعطاء إيحاء بالطول والحدة', priority=2),
            SculptRule(placement='نحت نازل وحاد من الأذن للزاوية تحت الفم، مع تحديد خط الفك لتعريف العظم',
                       purpose='كسر استدارة الخدين وتعريف عظمة الفك'),
            BlushRule(placement='تحت العين مباشرة، مسحوب للأعلى ومدمج مع ظل العين',
                      purpose='رفع ملامح الوجه بصرياً'),
            HighlightRule(placement='على رأس الخدين (أعلى نقطة) والذقن',
                          purpose='زيادة المدى الطولي الظاهر للوجه')
        )

    @Rule(FaceShapeAnalysis(shape='Round'), FaceFullness(fullness='Thin'))
    def round_thin_face(self):
        self.declare(
            FaceShapeCategory(shape='Round', name_ar='الوجه الدائري (Face Round)',
                               goal='كسر الاستدارة بلطف مع الحفاظ على حيوية الخدود', priority=2),
            SculptRule(placement='كونتور عادي من منتصف الأذن إلى منتصف الخد',
                       purpose='تعريف الهيكل الطبيعي دون حدة زائدة'),
            BlushRule(placement='من جانب الأنف مسحوب باتجاه الزاوية الخارجية للعين',
                      purpose='تعزيز الحدة والإطالة البصرية'),
            HighlightRule(placement='فوق عظمة الخد مباشرة',
                          purpose='تعزيز البروز الطبيعي للخد')
        )

    # ──── الوجه المستطيل ────

    @Rule(FaceShapeAnalysis(shape='Rectangular'), FaceFullness(fullness='Full'))
    def rectangular_full_face(self):
        self.declare(
            FaceShapeCategory(shape='Rectangular', name_ar='الوجه المستطيل (Face Rectangular)',
                               goal='تقصير المدى العمودي وزيادة العرض الوهمي لمقاربته من الشكل البيضاوي', priority=3),
            SculptRule(placement='خط أفقي صريح من منتصف الأذن إلى منتصف الخد لكسر طول الوجه',
                       purpose='كسر الخط العمودي المستمر'),
            BlushRule(placement='يوضع بشكل عرضي بجانب الكونتور',
                      purpose='زيادة عرض الوجه بصرياً'),
            HighlightRule(placement='وسط الجبهة والذقن فقط',
                          purpose='جذب الانتباه للمركز وتجنب إطالة الأطراف')
        )

    @Rule(FaceShapeAnalysis(shape='Rectangular'), FaceFullness(fullness='Thin'))
    def rectangular_thin_face(self):
        self.declare(
            FaceShapeCategory(shape='Rectangular', name_ar='الوجه المستطيل (Face Rectangular)',
                               goal='تقصير الوجه بصرياً وتخفيف حدة الفك الطويل', priority=3),
            SculptRule(placement='تظليل ناعم عند منبت الشعر (أعلى الجبهة) وأسفل الذقن فقط',
                       purpose='تقصير الوجه بصرياً'),
            BlushRule(placement='على الصدغين وجوانب الجبهة',
                      purpose='زيادة عرض الوجه في المنطقة العلوية'),
            HighlightRule(placement='وسط الجبهة والذقن فقط',
                          purpose='جذب الانتباه للمركز')
        )

    # ──── الوجه المربع ────

    @Rule(FaceShapeAnalysis(shape='Square'))
    def square_face(self):
        self.declare(
            FaceShapeCategory(shape='Square', name_ar='الوجه المربع (Face Square)',
                               goal='تليين حدة زوايا الفك وإضافة انسيابية للملامح', priority=4),
            SculptRule(placement='نحت خفيف على زوايا الفك مع تدوير خط الكونتور',
                       purpose='تليين حدة الزوايا'),
            BlushRule(placement='على تفاحتي الخد بشكل دائري ناعم',
                      purpose='إضافة انسيابية بصرية للوجه'),
            HighlightRule(placement='وسط الجبهة وأعلى الخدين',
                          purpose='دعم التصحيح البصري لشكل الوجه')
        )

    # ──── الوجه القلب ────

    @Rule(FaceShapeAnalysis(shape='Heart'))
    def heart_face(self):
        self.declare(
            FaceShapeCategory(shape='Heart', name_ar='الوجه القلب (Face Heart)',
                               goal='موازنة عرض الجبهة مع تخفيف الثقل البصري في منطقة الفك', priority=4),
            SculptRule(placement='نحت خفيف على جانبي الجبهة وزاويتيها',
                       purpose='تصغير عرض الجبهة بصرياً'),
            BlushRule(placement='تحت عظمة الخد باتجاه منتصف الوجه',
                      purpose='إضافة عرض بصري لمنطقة الفك والذقن'),
            HighlightRule(placement='على الذقن ومنتصف الجبهة',
                          purpose='موازنة أبعاد الوجه')
        )

    # ──── الوجه الماسي ────

    @Rule(FaceShapeAnalysis(shape='Diamond'))
    def diamond_face(self):
        self.declare(
            FaceShapeCategory(shape='Diamond', name_ar='الوجه الماسي (Face Diamond)',
                               goal='توسيع الجبهة والفك بصرياً وتليين بروز عظام الخد', priority=4),
            SculptRule(placement='نحت خفيف جداً على عظمة الخد البارزة فقط',
                       purpose='تليين حدة بروز عظام الخد'),
            BlushRule(placement='على تفاحتي الخد بامتداد أفقي خفيف',
                      purpose='توسيع منطقة الخد بصرياً'),
            HighlightRule(placement='وسط الجبهة والذقن',
                          purpose='توسيع الجبهة والفك بصرياً')
        )

    # ──── Rule: مصفوفة لون البلاشر حسب البشرة (٦ حالات) ────

    @Rule(SkinProfile(undertone='Warm', depth='Fair'))
    def warm_fair_blush(self):
        self.declare(BlushColorMatch(undertone='Warm', depth='Fair', base_color='خوخي ذهبي', palette='أساس دافئ'))

    @Rule(SkinProfile(undertone='Warm', depth='Medium'))
    def warm_medium_blush(self):
        self.declare(BlushColorMatch(undertone='Warm', depth='Medium', base_color='مرجاني', palette='أساس دافئ'))

    @Rule(SkinProfile(undertone='Warm', depth='Dark'))
    def warm_dark_blush(self):
        self.declare(BlushColorMatch(undertone='Warm', depth='Dark', base_color='برتقالي محروق', palette='أساس دافئ'))

    @Rule(SkinProfile(undertone='Cool', depth='Fair'))
    def cool_fair_blush(self):
        self.declare(BlushColorMatch(undertone='Cool', depth='Fair', base_color='موف فاتح', palette='أساس بارد'))

    @Rule(SkinProfile(undertone='Cool', depth='Medium'))
    def cool_medium_blush(self):
        self.declare(BlushColorMatch(undertone='Cool', depth='Medium', base_color='وردي ترابي', palette='أساس بارد'))

    @Rule(SkinProfile(undertone='Cool', depth='Dark'))
    def cool_dark_blush(self):
        self.declare(BlushColorMatch(undertone='Cool', depth='Dark', base_color='وردي توتي غامق', palette='أساس بارد'))

    # ──── Rule: تعديل اللون حسب استراتيجية مكياج العين ────

    @Rule(EyeMakeupStrategy(strategy='Monochromatic'))
    def monochromatic_blush_adjustment(self):
        self.declare(BlushAdjustment(strategy='Monochromatic',
                                      rule='يُختار اللون من المصفوفة بنفس درجة "حرارة" ظل العين ولون البشرة',
                                      opacity=100))

    @Rule(EyeMakeupStrategy(strategy='Contrast'))
    def contrast_blush_adjustment(self):
        self.declare(BlushAdjustment(strategy='Contrast',
                                      rule='يُحيَّد اللون ويُجعل باهتاً وشفافاً جداً (شفاف بنسبة 80%) كي تبقى العين هي "البطل"',
                                      opacity=20))

    @Rule(EyeMakeupStrategy(strategy='Triadic'))
    def triadic_blush_adjustment(self):
        self.declare(BlushAdjustment(strategy='Triadic',
                                      rule='يُحيَّد اللون ويُجعل باهتاً وشفافاً جداً (شفاف بنسبة 80%) كي تبقى العين هي "البطل"',
                                      opacity=20))

    @Rule(EyeMakeupStrategy(strategy='Earthy'))
    def earthy_blush_adjustment(self):
        self.declare(BlushAdjustment(strategy='Earthy',
                                      rule='يُختار اللون من المصفوفة بأقصى حيوية لكسر رتابة الألوان الترابية',
                                      opacity=100))

    # ──── Rule: القوام والشفافية حسب المناسبة ────

    @Rule(OccasionContext(occasion='work'))
    def work_blush_texture(self):
        self.declare(BlushTexture(occasion='work', finish='مطفأ', transparency='شفاف بنسبة 80%',
                                   description='تورّد طبيعي نابع من الجلد'))

    @Rule(OccasionContext(occasion='university'))
    def university_blush_texture(self):
        self.declare(BlushTexture(occasion='university', finish='مطفأ', transparency='شفاف بنسبة 80%',
                                   description='تورّد طبيعي نابع من الجلد'))

    @Rule(OccasionContext(occasion='evening'))
    def evening_blush_texture(self):
        self.declare(BlushTexture(occasion='evening', finish='ساتان / لامع', transparency='صبغة كاملة',
                                   description='لون قوي يبرز تحت أضواء السهرة'))

    @Rule(OccasionContext(occasion='wedding'))
    def wedding_blush_texture(self):
        self.declare(BlushTexture(occasion='wedding', finish='ساتان / لامع', transparency='صبغة كاملة',
                                   description='لون قوي يبرز تحت أضواء السهرة'))

    @Rule(OccasionContext(occasion='party'))
    def party_blush_texture(self):
        self.declare(BlushTexture(occasion='party', finish='ساتان / لامع', transparency='صبغة كاملة',
                                   description='لون قوي يبرز تحت الإضاءة'))

    @Rule(OccasionContext(occasion='photo'))
    def photo_blush_texture(self):
        self.declare(BlushTexture(occasion='photo', finish='مطفأ', transparency='صبغة كاملة بلا لمعان',
                                   description='مطفأ تماماً لتفادي انعكاس الفلاش'))

    # ──── Rule: التوصية النهائية ────

    @Rule(FaceShapeCategory(shape=MATCH.shape),
          BlushColorMatch(base_color=MATCH.base_color),
          OccasionContext(occasion=MATCH.occasion))
    def final_face_recommendation(self, shape, base_color, occasion):
        self.declare(FaceContourBlushRecommendation(shape=shape, base_color=base_color, occasion=occasion, complete=True))


# ══════════════════════════════════════════════════════
# ENGINE
# ══════════════════════════════════════════════════════

class FaceContourEngine(FaceContourRulesKB):
    """محرك الكونتور والبلاشر والهاياليت"""

    def __init__(self):
        super().__init__()

    def analyze_face(self, face_data):
        """
        input: dict {
            'shape': 'Oval', 'votes': {...},
            'undertone': 'Warm', 'depth': 'Medium',
            'fullness': 'Full',
            'eye_strategy': 'Monochromatic',
            'occasion': 'evening'
        }
        """
        self.reset()
        self.declare(
            FaceShapeAnalysis(shape=face_data.get('shape', 'Oval'), votes=face_data.get('votes', {})),
            SkinProfile(undertone=face_data.get('undertone', 'Warm'), depth=face_data.get('depth', 'Medium')),
            FaceFullness(fullness=face_data.get('fullness', 'Full')),
            EyeMakeupStrategy(strategy=face_data.get('eye_strategy', 'Monochromatic')),
            OccasionContext(occasion=face_data.get('occasion', 'work'))
        )
        self.run()
        return self._extract_results()

    def _extract_results(self):
        results = {'shape': None, 'sculpt': None, 'blush': None, 'highlight': None,
                   'color': None, 'adjustment': None, 'texture': None, 'recommendation': None}

        for fact in self.facts.values():
            if isinstance(fact, FaceShapeCategory):
                results['shape'] = {'shape': fact.get('shape'), 'name_ar': fact.get('name_ar'), 'goal': fact.get('goal')}
            elif isinstance(fact, SculptRule):
                results['sculpt'] = {'placement': fact.get('placement'), 'purpose': fact.get('purpose')}
            elif isinstance(fact, BlushRule):
                results['blush'] = {'placement': fact.get('placement'), 'purpose': fact.get('purpose')}
            elif isinstance(fact, HighlightRule):
                results['highlight'] = {'placement': fact.get('placement'), 'purpose': fact.get('purpose')}
            elif isinstance(fact, BlushColorMatch):
                results['color'] = {'base_color': fact.get('base_color'), 'palette': fact.get('palette')}
            elif isinstance(fact, BlushAdjustment):
                results['adjustment'] = {'rule': fact.get('rule'), 'opacity': fact.get('opacity')}
            elif isinstance(fact, BlushTexture):
                results['texture'] = {'finish': fact.get('finish'), 'transparency': fact.get('transparency'),
                                       'description': fact.get('description')}
            elif isinstance(fact, FaceContourBlushRecommendation):
                results['recommendation'] = {'shape': fact.get('shape'), 'color': fact.get('base_color'),
                                              'occasion': fact.get('occasion'), 'complete': fact.get('complete')}

        return results


if __name__ == "__main__":
    engine = FaceContourEngine()
    result = engine.analyze_face({'shape': 'Oval', 'undertone': 'Warm', 'depth': 'Medium', 'occasion': 'evening'})
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))