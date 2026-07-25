# -*- coding: utf-8 -*-
"""
brow_makeup_rules.py — Experta-based Expert System (كامل بالعربي)
===========================================================
نظام خبير لقواعد الحواجب — Forward Chaining تلقائي، بلا if/else في القواعد
"""

# ✅ MUST BE FIRST: Python 3.10+ Compatibility Fix
import compat_fix

from experta import *
import json


# ══════════════════════════════════════════════════════
# FACTS
# ══════════════════════════════════════════════════════

class BrowAnalysis(Fact):
    """نتائج تحليل الحاجب"""
    thickness = Field(str)
    length = Field(str)
    shape = Field(str)
    position = Field(str)
    spacing = Field(str)
    symmetry = Field(str)


class FaceShape(Fact):
    """شكل الوجه"""
    shape = Field(str)  # Oval / Round / Rectangular / Triangle / Square / Heart / Diamond


class OccasionContext(Fact):
    """سياق المناسبة"""
    occasion = Field(str)  # work / university / evening / party / wedding / photo


class SkinTone(Fact):
    """لون البشرة"""
    undertone = Field(str)  # warm / cool
    depth = Field(str)      # fair / medium / dark


class BrowCorrectionRule(Fact):
    """قاعدة تصحيح الحاجب حسب شكل الوجه"""
    face_shape = Field(str)
    arch_type = Field(str)
    arch_position = Field(str)
    tail_direction = Field(str)
    tail_weight = Field(str)
    visual_purpose = Field(str)


class BrowStyleRule(Fact):
    """قاعدة أسلوب الحاجب حسب المناسبة"""
    occasion = Field(str)
    style = Field(str)
    technique = Field(str)
    product = Field(str)
    color_intensity = Field(str)
    description = Field(str)
    appearance = Field(str)


class BrowColorRule(Fact):
    """قاعدة لون الحاجب حسب البشرة"""
    undertone = Field(str)
    depth = Field(str)
    tone = Field(str)
    palette = Field(str)


class BrowRecommendation(Fact):
    """التوصية النهائية الكاملة"""
    face_shape = Field(str)
    occasion = Field(str)
    color_tone = Field(str)
    complete = Field(bool, default=False)


# ══════════════════════════════════════════════════════
# RULES
# ══════════════════════════════════════════════════════

class BrowRulesKB(KnowledgeEngine):

    # ──── Rule 1: تصحيحات الحاجب حسب شكل الوجه ────

    @Rule(FaceShape(shape='Oval'))
    def oval_face_brow(self):
        self.declare(BrowCorrectionRule(
            face_shape='Oval', arch_type='قوس طبيعي', arch_position='وضعية طبيعية',
            tail_direction='طبيعي', tail_weight='طبيعي',
            visual_purpose='متوازن تشريحياً ولا يحتاج تصحيح'))

    @Rule(FaceShape(shape='Round'))
    def round_face_brow(self):
        self.declare(BrowCorrectionRule(
            face_shape='Round', arch_type='قوس مرتفع', arch_position='مرفوع',
            tail_direction='ممتد للخارج', tail_weight='ثقيل',
            visual_purpose='كسر الاستدارة وإعطاء إيحاء بالطول والحدة'))

    @Rule(FaceShape(shape='Rectangular'))
    def rectangular_face_brow(self):
        self.declare(BrowCorrectionRule(
            face_shape='Rectangular', arch_type='قوس ناعم أو شبه مسطح', arch_position='معتدل إلى منخفض',
            tail_direction='ممتد وطويل', tail_weight='خفيف ومدبب',
            visual_purpose='كسر الخط العمودي وإضافة عرض وهمي'))

    @Rule(FaceShape(shape='Triangle'))
    def triangle_face_brow(self):
        self.declare(BrowCorrectionRule(
            face_shape='Triangle', arch_type='قوس محايد', arch_position='معتدل',
            tail_direction='ممتد وثقيل', tail_weight='ثقيل نسبياً',
            visual_purpose='موازنة عرض الفك بإضافة ثقل بصري أعلى'))

    @Rule(FaceShape(shape='Square'))
    def square_face_brow(self):
        self.declare(BrowCorrectionRule(
            face_shape='Square', arch_type='قوس ناعم', arch_position='مرتفع قليلاً وناعم',
            tail_direction='مدبب', tail_weight='خفيف',
            visual_purpose='كسر حدة الزوايا وإضافة منحنى لتليين الملامح'))

    @Rule(FaceShape(shape='Heart'))
    def heart_face_brow(self):
        self.declare(BrowCorrectionRule(
            face_shape='Heart', arch_type='قوس ناعم منخفض', arch_position='منخفض وناعم',
            tail_direction='مدبب ورفيع', tail_weight='رفيع',
            visual_purpose='موازنة عرض الجبهة وتخفيف الثقل البصري'))

    @Rule(FaceShape(shape='Diamond'))
    def diamond_face_brow(self):
        self.declare(BrowCorrectionRule(
            face_shape='Diamond', arch_type='قوس ناعم', arch_position='دائري ناعم',
            tail_direction='مدبب وخفيف', tail_weight='خفيف',
            visual_purpose='توسيع الجبهة وتليين حدة عظام الخد البارزة'))

    # ──── Rule 2: أسلوب الحاجب حسب المناسبة ────

    @Rule(OccasionContext(occasion='work'))
    def work_brow_style(self):
        self.declare(BrowStyleRule(
            occasion='work', style='تهذيب طبيعي', technique='تمشيط وتهذيب',
            product='جل شفاف أو ملوّن خفيف', color_intensity='شفاف جداً',
            description='تمشيط شفاف أو لون خفيف جداً على الشعر', appearance='مظهر نظيف بلا رسم واضح'))

    @Rule(OccasionContext(occasion='university'))
    def university_brow_style(self):
        self.declare(BrowStyleRule(
            occasion='university', style='تهذيب طبيعي', technique='تمشيط وتهذيب',
            product='جل شفاف أو ملوّن خفيف', color_intensity='شفاف جداً',
            description='تمشيط شفاف أو لون خفيف جداً على الشعر', appearance='مظهر نظيف بلا رسم واضح'))

    @Rule(OccasionContext(occasion='evening'))
    def evening_brow_style(self):
        self.declare(BrowStyleRule(
            occasion='evening', style='تحديد بقوس واضح', technique='تحديد',
            product='بودرة أو قلم حواجب', color_intensity='طبيعي إلى قوي',
            description='تحديد نقاط الارتكاز مع تكثيف بسيط للمظهر المسائي', appearance='تناسق محدد وأنيق'))

    @Rule(OccasionContext(occasion='party'))
    def party_brow_style(self):
        self.declare(BrowStyleRule(
            occasion='party', style='تحديد بقوس واضح', technique='تحديد',
            product='بودرة أو قلم حواجب', color_intensity='طبيعي',
            description='تحديد نقاط الارتكاز (البداية، القمة، النهاية)', appearance='تناسق محدد'))

    @Rule(OccasionContext(occasion='photo'))
    def photography_brow_style(self):
        self.declare(BrowStyleRule(
            occasion='photo', style='نحت الحاجب', technique='نحت وتعبئة',
            product='قلم أو بودرة بضربات ريشة', color_intensity='قوي (جاهز للتصوير عالي الدقة)',
            description='تعبئة الفراغات بضربات ريشة بزاوية 45 درجة تحاكي نمو الشعر', appearance='كثافة طبيعية'))

    @Rule(OccasionContext(occasion='wedding'))
    def wedding_brow_style(self):
        self.declare(BrowStyleRule(
            occasion='wedding', style='فخامة وجرأة', technique='دقة وجرأة في الرسم',
            product='لاينر ومحدد حواجب', color_intensity='قوي وجريء',
            description='رسم حاد ومحدد مع رفع القمة لخلق طاقة رفع قصوى', appearance='رفع درامي فاخر'))

    # ──── Rule 3: لون الحاجب حسب البشرة ────

    @Rule(SkinTone(undertone='warm', depth='fair'))
    def warm_fair_brow_color(self):
        self.declare(BrowColorRule(undertone='warm', depth='fair', tone='بني دافئ / أشقر محمر',
                                    palette='أساس ذهبي دافئ'))

    @Rule(SkinTone(undertone='warm', depth='medium'))
    def warm_medium_brow_color(self):
        self.declare(BrowColorRule(undertone='warm', depth='medium', tone='بني متوسط',
                                    palette='أساس ذهبي دافئ'))

    @Rule(SkinTone(undertone='warm', depth='dark'))
    def warm_dark_brow_color(self):
        self.declare(BrowColorRule(undertone='warm', depth='dark', tone='بني غني / أشقر داكن',
                                    palette='أساس ذهبي دافئ'))

    @Rule(SkinTone(undertone='cool', depth='fair'))
    def cool_fair_brow_color(self):
        self.declare(BrowColorRule(undertone='cool', depth='fair', tone='تاوب فاتح / بني رمادي',
                                    palette='أساس بارد'))

    @Rule(SkinTone(undertone='cool', depth='medium'))
    def cool_medium_brow_color(self):
        self.declare(BrowColorRule(undertone='cool', depth='medium', tone='بني رمادي (آش براون)',
                                    palette='أساس بارد'))

    @Rule(SkinTone(undertone='cool', depth='dark'))
    def cool_dark_brow_color(self):
        self.declare(BrowColorRule(undertone='cool', depth='dark', tone='بني رمادي داكن',
                                    palette='أساس بارد'))

    # ──── Rule 4: التوصية النهائية ────

    @Rule(BrowCorrectionRule(face_shape=MATCH.shape),
          BrowStyleRule(occasion=MATCH.occasion),
          BrowColorRule(tone=MATCH.tone))
    def final_brow_recommendation(self, shape, occasion, tone):
        self.declare(BrowRecommendation(face_shape=shape, occasion=occasion, color_tone=tone, complete=True))


# ══════════════════════════════════════════════════════
# ENGINE
# ══════════════════════════════════════════════════════

class BrowMakeupEngine(BrowRulesKB):
    """محرك مكياج الحواجب"""

    def __init__(self):
        super().__init__()

    def analyze_brows(self, brow_data):
        self.reset()
        self.declare(
            BrowAnalysis(
                thickness=brow_data.get('thickness', 'Medium'),
                length=brow_data.get('length', 'Medium'),
                shape=brow_data.get('shape', 'Soft Arch'),
                position=brow_data.get('position', 'Normal'),
                spacing=brow_data.get('spacing', 'Normal'),
                symmetry=brow_data.get('symmetry', 'Symmetrical')
            ),
            FaceShape(shape=brow_data.get('face_shape', 'Oval')),
            OccasionContext(occasion=brow_data.get('occasion', 'work')),
            SkinTone(undertone=brow_data.get('undertone', 'warm'), depth=brow_data.get('depth', 'medium'))
        )
        self.run()
        return self._extract_results()

    def _extract_results(self):
        results = {'correction': None, 'style': None, 'color': None, 'recommendation': None}

        for fact in self.facts.values():
            if isinstance(fact, BrowCorrectionRule):
                results['correction'] = {
                    'arch_type': fact.get('arch_type'),
                    'arch_position': fact.get('arch_position'),
                    'tail_direction': fact.get('tail_direction'),
                    'tail_weight': fact.get('tail_weight'),
                    'visual_purpose': fact.get('visual_purpose')
                }
            elif isinstance(fact, BrowStyleRule):
                results['style'] = {
                    'style': fact.get('style'),
                    'technique': fact.get('technique'),
                    'product': fact.get('product'),
                    'color_intensity': fact.get('color_intensity'),
                    'appearance': fact.get('appearance')
                }
            elif isinstance(fact, BrowColorRule):
                results['color'] = {'tone': fact.get('tone'), 'palette': fact.get('palette')}
            elif isinstance(fact, BrowRecommendation):
                results['recommendation'] = {
                    'face_shape': fact.get('face_shape'),
                    'occasion': fact.get('occasion'),
                    'color': fact.get('color_tone'),
                    'complete': fact.get('complete')
                }

        return results


if __name__ == "__main__":
    engine = BrowMakeupEngine()
    example = {'thickness': 'Medium', 'length': 'Medium', 'shape': 'Soft Arch', 'face_shape': 'Round',
               'occasion': 'wedding', 'undertone': 'cool', 'depth': 'medium'}
    result = engine.analyze_brows(example)
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))