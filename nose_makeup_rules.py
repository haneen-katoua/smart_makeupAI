# -*- coding: utf-8 -*-
"""
nose_makeup_rules.py — Experta-based Expert System (كامل بالعربي)
===========================================================
نظام خبير لقواعد مكياج الأنف
"""

# ✅ MUST BE FIRST: Python 3.10+ Compatibility Fix
import compat_fix

from experta import *
import json


# ══════════════════════════════════════════════════════
# FACTS
# ══════════════════════════════════════════════════════

class NoseAnalysis(Fact):
    shape = Field(str)


class SkinProfile(Fact):
    undertone = Field(str)
    depth = Field(str)


class NoseShapeCategory(Fact):
    shape = Field(str)
    name_ar = Field(str)
    goal = Field(str)
    technique = Field(str)
    reason = Field(str)


class NoseMap(Fact):
    shape = Field(str)
    contour = Field(str)
    highlight = Field(str)
    tip_shading = Field(str)


class ContourProductMatch(Fact):
    undertone = Field(str)
    depth = Field(str)
    product = Field(str)
    reason_ar = Field(str)


class HighlightTone(Fact):
    undertone = Field(str)
    tone = Field(str)
    method = Field(str)


class NoseRecommendation(Fact):
    shape = Field(str)
    contour_product = Field(str)
    highlight_tone = Field(str)
    complete = Field(bool, default=False)


# ══════════════════════════════════════════════════════
# RULES
# ══════════════════════════════════════════════════════

class NoseRulesKB(KnowledgeEngine):

    # ──── Rule 1: تصنيف شكل الأنف والتقنيات ────

    @Rule(NoseAnalysis(shape='Long'))
    def long_nose_detected(self):
        self.declare(
            NoseShapeCategory(
                shape='Long', name_ar='الأنف الطويل',
                goal='كسر الخط العمودي المستمر وتقصير الطول الظاهر',
                technique='يوضع الكونتور بدءاً من منتصف جسر الأنف فقط (وليس من الحاجب)، مع رسم دائرة تظليل ناعمة حول طرف الأنف',
                reason='بما أن الأنف طويل، يوضع الكونتور من منتصف الجسر فقط لكسر الخط العمودي المستمر'),
            NoseMap(shape='Long',
                    contour='يبدأ من منتصف جسر الأنف، ويُدمج للأسفل على الجانبين',
                    highlight='خط رفيع في منتصف الجسر يتوقف قبل الطرف',
                    tip_shading='ظل دائري ناعم حول طرف الأنف'))

    @Rule(NoseAnalysis(shape='Short'))
    def short_nose_detected(self):
        self.declare(
            NoseShapeCategory(
                shape='Short', name_ar='الأنف القصير',
                goal='خلق إيحاء بالطول عبر تعريف هيكل العظم',
                technique='يوضع كونتور كامل على جانبي الأنف من الحاجب حتى الطرف، مع هاياليت على طرف الأنف تماماً',
                reason='لإعطاء إيحاء بالطول، يُستخدم كونتور بطول كامل لتعريف الهيكل العظمي'),
            NoseMap(shape='Short',
                    contour='بطول كامل، من بداية الحاجب حتى الطرف على الجانبين',
                    highlight='يوضع مباشرة على طرف الأنف (تقنية الإظهار للأمام)',
                    tip_shading='لا يوجد — الطرف يُبرَز بالهاياليت وليس بالتظليل'))

    @Rule(NoseAnalysis(shape='Balanced'))
    def balanced_nose_detected(self):
        self.declare(
            NoseShapeCategory(
                shape='Balanced', name_ar='الأنف المتوازن',
                goal='تأطير الأنف بشكل مثالي مع إبراز قوة الملامح',
                technique='يوضع كونتور كامل على الجانبين مع تظليل خفيف على الطرف، بالإضافة إلى هاياليت على الطرف',
                reason='الأنف متوازن أصلاً، لذلك تُستخدم تقنية التعريف الكامل لإبراز قوة الملامح'),
            NoseMap(shape='Balanced',
                    contour='بطول كامل على الجانبين وبكثافة معتدلة',
                    highlight='على طرف الأنف',
                    tip_shading='تظليل خفيف على الطرف مدموج مع الهاياليت لإعطاء بعد ثلاثي الأبعاد'))

    # ──── Rule 2: منتج الكونتور حسب البشرة ────

    @Rule(SkinProfile(undertone='Warm', depth='Fair'))
    def warm_fair_contour(self):
        self.declare(ContourProductMatch(undertone='Warm', depth='Fair', product='بيج ذهبي فاتح',
                                          reason_ar='يميل للذهبي الفاتح، يمنح نحتاً طبيعياً'))

    @Rule(SkinProfile(undertone='Warm', depth='Medium'))
    def warm_medium_contour(self):
        self.declare(ContourProductMatch(undertone='Warm', depth='Medium', product='بني دافئ (Warm Brown)',
                                          reason_ar='لموازنة تدرجات البيج الدافئ'))

    @Rule(SkinProfile(undertone='Warm', depth='Dark'))
    def warm_dark_contour(self):
        self.declare(ContourProductMatch(undertone='Warm', depth='Dark', product='برونزي',
                                          reason_ar='يحتاج صبغة قوية لإظهار التراجع البصري'))

    @Rule(SkinProfile(undertone='Cool', depth='Fair'))
    def cool_fair_contour(self):
        self.declare(ContourProductMatch(undertone='Cool', depth='Fair', product='بني تاوب رمادي فاتح',
                                          reason_ar='بني مائل للرمادي الفاتح جداً، يحاكي الظل الطبيعي'))

    @Rule(SkinProfile(undertone='Cool', depth='Medium'))
    def cool_medium_contour(self):
        self.declare(ContourProductMatch(undertone='Cool', depth='Medium', product='موف',
                                          reason_ar='يضيف مسحة وردية/زرقاء تتناغم مع العروق الباردة'))

    @Rule(SkinProfile(undertone='Cool', depth='Dark'))
    def cool_dark_contour(self):
        self.declare(ContourProductMatch(undertone='Cool', depth='Dark', product='بني رمادي غامق',
                                          reason_ar='يضمن عدم تحول الكونتور إلى لون برتقالي'))

    # ──── Rule 3: لون الهاياليت ────

    @Rule(SkinProfile(undertone='Warm'))
    def warm_highlight_tone(self):
        self.declare(HighlightTone(undertone='Warm', tone='عاجي',
                                    method='يُنتج بالمزج بين لون البشرة الأساسي والأبيض'))

    @Rule(SkinProfile(undertone='Cool'))
    def cool_highlight_tone(self):
        self.declare(HighlightTone(undertone='Cool', tone='وردي لؤلؤي',
                                    method='يُنتج بالمزج بين لون البشرة الأساسي والأبيض'))

    # ──── Rule 4: التوصية النهائية ────

    @Rule(NoseShapeCategory(shape=MATCH.shape),
          NoseMap(shape=MATCH.shape_map),
          ContourProductMatch(product=MATCH.product),
          HighlightTone(tone=MATCH.highlight))
    def final_nose_recommendation(self, shape, shape_map, product, highlight):
        self.declare(NoseRecommendation(shape=shape, contour_product=product, highlight_tone=highlight, complete=True))


# ══════════════════════════════════════════════════════
# ENGINE
# ══════════════════════════════════════════════════════

class NoseMakeupEngine(NoseRulesKB):
    """محرك مكياج الأنف"""

    def __init__(self):
        super().__init__()

    def analyze_nose(self, nose_data):
        self.reset()
        self.declare(
            NoseAnalysis(shape=nose_data.get('shape', 'Balanced')),
            SkinProfile(undertone=nose_data.get('undertone', 'Warm'), depth=nose_data.get('depth', 'Medium'))
        )
        self.run()
        return self._extract_results()

    def _extract_results(self):
        results = {'shape': None, 'map': None, 'contour': None, 'highlight': None, 'recommendation': None}

        for fact in self.facts.values():
            if isinstance(fact, NoseShapeCategory):
                results['shape'] = {'shape': fact.get('shape'), 'name_ar': fact.get('name_ar'),
                                     'goal': fact.get('goal'), 'technique': fact.get('technique'),
                                     'reason': fact.get('reason')}
            elif isinstance(fact, NoseMap):
                results['map'] = {
                        'contour': fact.get('contour'),
                        'contour_arrow_target': [
                            'nose_contour_left',
                            'nose_contour_right'
                        ],

                        'highlight': fact.get('highlight'),
                        'highlight_arrow_target': 'nose_bridge',

                        'tip_shading': fact.get('tip_shading'),
                        'tip_arrow_target': 'nose_tip'
                    }
            elif isinstance(fact, ContourProductMatch):
                results['contour'] = {'product': fact.get('product'), 'reason': fact.get('reason_ar')}
            elif isinstance(fact, HighlightTone):
                results['highlight'] = {'tone': fact.get('tone'), 'method': fact.get('method')}
            elif isinstance(fact, NoseRecommendation):
                results['recommendation'] = {'shape': fact.get('shape'), 'product': fact.get('contour_product'),
                                              'highlight': fact.get('highlight_tone'), 'complete': fact.get('complete')}

        return results


if __name__ == "__main__":
    engine = NoseMakeupEngine()
    example = {'shape': 'Long', 'undertone': 'Warm', 'depth': 'Medium'}
    result = engine.analyze_nose(example)
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))