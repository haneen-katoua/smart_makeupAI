# # -*- coding: utf-8 -*-
# """
# foundation_makeup_rules.py — Experta-based Expert System (Foundation / Concealer / Primer / Setting)
# """

# # ✅ MUST BE FIRST: Python 3.10+ Compatibility Fix
# import compat_fix

# from experta import *
# import json


# # ══════════════════════════════════════════════════════
# # FACTS
# # ══════════════════════════════════════════════════════

# class SkinProfile(Fact):
#     depth = Field(str)
#     undertone = Field(str)
#     skin_type = Field(str, default='Normal')


# class FoundationShade(Fact):
#     depth = Field(str)
#     undertone = Field(str)
#     shade_range = Field(str)
#     color_descriptor = Field(str)


# class FoundationFormula(Fact):
#     skin_type = Field(str)
#     name_ar = Field(str)
#     primary = Field(str)
#     texture = Field(str)
#     coverage = Field(str)
#     reason = Field(str)


# class ConcealerShade(Fact):
#     depth = Field(str)
#     concealer_descriptor = Field(str)
#     reason = Field(str)


# class PrimerMatch(Fact):
#     skin_type = Field(str)
#     name_ar = Field(str)
#     primer_type = Field(str)
#     function = Field(str)


# class SettingProtocol(Fact):
#     skin_type = Field(str)
#     setting_method = Field(str)
#     technique = Field(str)
#     reason = Field(str)


# class FoundationRecommendation(Fact):
#     depth = Field(str)
#     undertone = Field(str)
#     skin_type = Field(str)
#     shade_range = Field(str)
#     formula = Field(str)
#     complete = Field(bool, default=False)


# # ══════════════════════════════════════════════════════
# # RULES
# # ══════════════════════════════════════════════════════

# class FoundationRulesKB(KnowledgeEngine):

#     # ──── درجة الأساس (٦ حالات: عمق × أندرتون) ────

#     @Rule(SkinProfile(depth='Fair', undertone='Warm'))
#     def fair_warm_shade(self):
#         self.declare(FoundationShade(depth='Fair', undertone='Warm', shade_range='فاتحة ذهبية',
#                                       color_descriptor='درجة فاتحة ذهبية الميل'))

#     @Rule(SkinProfile(depth='Medium', undertone='Warm'))
#     def medium_warm_shade(self):
#         self.declare(FoundationShade(depth='Medium', undertone='Warm', shade_range='متوسطة عسلية/ذهبية',
#                                       color_descriptor='درجة متوسطة عسلية/ذهبية'))

#     @Rule(SkinProfile(depth='Dark', undertone='Warm'))
#     def dark_warm_shade(self):
#         self.declare(FoundationShade(depth='Dark', undertone='Warm', shade_range='داكنة كراميلية دافئة',
#                                       color_descriptor='درجة داكنة دافئة كراميلية'))

#     @Rule(SkinProfile(depth='Fair', undertone='Cool'))
#     def fair_cool_shade(self):
#         self.declare(FoundationShade(depth='Fair', undertone='Cool', shade_range='فاتحة وردية/محايدة',
#                                       color_descriptor='درجة فاتحة وردية/محايدة'))

#     @Rule(SkinProfile(depth='Medium', undertone='Cool'))
#     def medium_cool_shade(self):
#         self.declare(FoundationShade(depth='Medium', undertone='Cool', shade_range='متوسطة بيج ورديّة',
#                                       color_descriptor='درجة متوسطة بيج ورديّة'))

#     @Rule(SkinProfile(depth='Dark', undertone='Cool'))
#     def dark_cool_shade(self):
#         self.declare(FoundationShade(depth='Dark', undertone='Cool', shade_range='داكنة باردة (إسبريسو)',
#                                       color_descriptor='درجة داكنة باردة (إسبريسو)'))

#     # ──── نوع/تركيبة الأساس حسب نوع البشرة ────

#     @Rule(SkinProfile(skin_type='Oily'))
#     def oily_foundation(self):
#         self.declare(FoundationFormula(skin_type='Oily', name_ar='البشرة الدهنية', primary='أساس بودرة / سائل مطفأ',
#                                         texture='مطفأ', coverage='متوسطة إلى كاملة',
#                                         reason='تمتص الدهون الزائدة وتثبت لفترة أطول'))

#     @Rule(SkinProfile(skin_type='Dry'))
#     def dry_foundation(self):
#         self.declare(FoundationFormula(skin_type='Dry', name_ar='البشرة الجافة', primary='أساس سائل مرطّب / كريمي',
#                                         texture='نضر ولامع بلطف', coverage='خفيفة إلى متوسطة',
#                                         reason='يمنح ترطيباً ويتفادى إبراز مناطق التقشر'))

#     @Rule(SkinProfile(skin_type='Combination'))
#     def combination_foundation(self):
#         self.declare(FoundationFormula(skin_type='Combination', name_ar='البشرة المختلطة', primary='أساس سائل شبه مطفأ',
#                                         texture='شبه مطفأ', coverage='متوسطة',
#                                         reason='يوازن بين تثبيت منطقة T وترطيب باقي الوجه'))

#     @Rule(SkinProfile(skin_type='Sensitive'))
#     def sensitive_foundation(self):
#         self.declare(FoundationFormula(skin_type='Sensitive', name_ar='البشرة الحساسة', primary='أساس معدني خالٍ من العطور',
#                                         texture='ساتان طبيعي', coverage='خفيفة إلى متوسطة',
#                                         reason='يقلل خطر التهيج ويحافظ على راحة البشرة'))

#     @Rule(SkinProfile(skin_type='Normal'))
#     def normal_foundation(self):
#         self.declare(FoundationFormula(skin_type='Normal', name_ar='البشرة العادية', primary='أساس سائل بلمسة ساتان',
#                                         texture='ساتان', coverage='متوسطة',
#                                         reason='يمنح مظهراً طبيعياً متوازناً دون الحاجة لتصحيح كبير'))

#     # ──── الكونسيلر حسب العمق ────

#     @Rule(SkinProfile(depth='Fair'))
#     def fair_concealer(self):
#         self.declare(ConcealerShade(depth='Fair', concealer_descriptor='درجة أفتح من الأساس بدرجة واحدة',
#                                      reason='لتفتيح منطقة تحت العين وتصحيح الهالات'))

#     @Rule(SkinProfile(depth='Medium'))
#     def medium_concealer(self):
#         self.declare(ConcealerShade(depth='Medium', concealer_descriptor='درجة أفتح بدرجة إلى درجة ونصف من الأساس',
#                                      reason='لتفتيح متوازن دون ظهور طبقة رمادية تحت العين'))

#     @Rule(SkinProfile(depth='Dark'))
#     def dark_concealer(self):
#         self.declare(ConcealerShade(depth='Dark', concealer_descriptor='درجة أفتح مع أندرتون دافئ برتقالي خفيف',
#                                      reason='لتحييد الهالات الداكنة دون ترك أثر رمادي'))

#     # ──── البرايمر حسب نوع البشرة ────

#     @Rule(SkinProfile(skin_type='Oily'))
#     def oily_primer(self):
#         self.declare(PrimerMatch(skin_type='Oily', name_ar='البشرة الدهنية', primer_type='برايمر مطفئ للمعان (أساسه سيليكا)',
#                                   function='تقليل لمعان الدهون وتوسيع ثبات المكياج'))

#     @Rule(SkinProfile(skin_type='Dry'))
#     def dry_primer(self):
#         self.declare(PrimerMatch(skin_type='Dry', name_ar='البشرة الجافة', primer_type='برايمر مرطّب ومضيء',
#                                   function='ترطيب البشرة وتحضيرها لامتصاص أفضل للأساس'))

#     @Rule(SkinProfile(skin_type='Combination'))
#     def combination_primer(self):
#         self.declare(PrimerMatch(skin_type='Combination', name_ar='البشرة المختلطة', primer_type='برايمر موازن ومقلّص للمسام',
#                                   function='تنظيم إفراز الدهون في منطقة T مع ترطيب الأطراف'))

#     @Rule(SkinProfile(skin_type='Sensitive'))
#     def sensitive_primer(self):
#         self.declare(PrimerMatch(skin_type='Sensitive', name_ar='البشرة الحساسة', primer_type='برايمر مهدّئ خالٍ من العطور',
#                                   function='تهدئة البشرة وتقليل احتمال التهيج'))

#     @Rule(SkinProfile(skin_type='Normal'))
#     def normal_primer(self):
#         self.declare(PrimerMatch(skin_type='Normal', name_ar='البشرة العادية', primer_type='برايمر منعّم ومقلّص للمسام',
#                                   function='تنعيم الملمس وتحضير سطح موحد للأساس'))

#     # ──── بروتوكول التثبيت ────

#     @Rule(SkinProfile(skin_type='Oily'))
#     def oily_setting(self):
#         self.declare(SettingProtocol(skin_type='Oily', setting_method='بودرة تثبيت + رذاذ تثبيت مطفئ للمعان',
#                                       technique='تثبيت كامل الوجه ببودرة شفافة مع التركيز على منطقة T',
#                                       reason='لإطالة مدة الثبات ومنع ظهور اللمعان خلال اليوم'))

#     @Rule(SkinProfile(skin_type='Dry'))
#     def dry_setting(self):
#         self.declare(SettingProtocol(skin_type='Dry', setting_method='رذاذ تثبيت مرطّب ومضيء فقط',
#                                       technique='تفادي البودرة الكثيفة والاكتفاء برذاذ التثبيت',
#                                       reason='للحفاظ على النضارة وتجنب إبراز الجفاف'))

#     @Rule(SkinProfile(skin_type='Combination'))
#     def combination_setting(self):
#         self.declare(SettingProtocol(skin_type='Combination', setting_method='بودرة موضعية على منطقة T + رذاذ تثبيت عام',
#                                       technique='تثبيت انتقائي حسب مناطق الوجه',
#                                       reason='لتحقيق توازن بين التثبيت والنضارة'))

#     @Rule(SkinProfile(skin_type='Sensitive'))
#     def sensitive_setting(self):
#         self.declare(SettingProtocol(skin_type='Sensitive', setting_method='رذاذ تثبيت خالٍ من العطور',
#                                       technique='طبقة تثبيت خفيفة جداً',
#                                       reason='لتقليل خطر التهيج مع الحفاظ على الثبات'))

#     @Rule(SkinProfile(skin_type='Normal'))
#     def normal_setting(self):
#         self.declare(SettingProtocol(skin_type='Normal', setting_method='بودرة خفيفة + رذاذ تثبيت',
#                                       technique='تثبيت عام متوازن',
#                                       reason='للحفاظ على المظهر الطبيعي طوال اليوم'))

#     # ──── التوصية النهائية ────

#     @Rule(FoundationShade(depth=MATCH.depth, undertone=MATCH.undertone, shade_range=MATCH.shade_range),
#           FoundationFormula(skin_type=MATCH.skin_type, primary=MATCH.primary))
#     def final_foundation_recommendation(self, depth, undertone, shade_range, skin_type, primary):
#         self.declare(FoundationRecommendation(depth=depth, undertone=undertone, skin_type=skin_type,
#                                                shade_range=shade_range, formula=primary, complete=True))


# # ══════════════════════════════════════════════════════
# # ENGINE
# # ══════════════════════════════════════════════════════

# class FoundationEngine(FoundationRulesKB):
#     """محرك الأساس والكونسيلر"""

#     def __init__(self):
#         super().__init__()

#     def analyze_foundation(self, skin_data):
#         self.reset()
#         self.declare(
#             SkinProfile(
#                 depth=skin_data.get('depth', 'Medium'),
#                 undertone=skin_data.get('undertone', 'Warm'),
#                 skin_type=skin_data.get('skin_type', 'Normal')
#             )
#         )
#         self.run()
#         return self._extract_results()

#     def _extract_results(self):
#         results = {'shade': None, 'formula': None, 'concealer': None, 'primer': None,
#                    'setting': None, 'recommendation': None}
#         for fact in self.facts.values():
#             if isinstance(fact, FoundationShade):
#                 results['shade'] = {'range': fact.get('shade_range'), 'descriptor': fact.get('color_descriptor')}
#             elif isinstance(fact, FoundationFormula):
#                 results['formula'] = {'primary': fact.get('primary'), 'texture': fact.get('texture'),
#                                        'coverage': fact.get('coverage'), 'reason': fact.get('reason')}
#             elif isinstance(fact, ConcealerShade):
#                 results['concealer'] = {'descriptor': fact.get('concealer_descriptor'), 'reason': fact.get('reason')}
#             elif isinstance(fact, PrimerMatch):
#                 results['primer'] = {'type': fact.get('primer_type'), 'function': fact.get('function')}
#             elif isinstance(fact, SettingProtocol):
#                 results['setting'] = {'method': fact.get('setting_method'), 'technique': fact.get('technique'),
#                                        'reason': fact.get('reason')}
#             elif isinstance(fact, FoundationRecommendation):
#                 results['recommendation'] = {'shade_range': fact.get('shade_range'), 'formula': fact.get('formula'),
#                                               'complete': fact.get('complete')}
#         return results


# if __name__ == "__main__":
#     engine = FoundationEngine()
#     result = engine.analyze_foundation({'depth': 'Medium', 'undertone': 'Warm', 'skin_type': 'Combination'})
#     print(json.dumps(result, indent=2, ensure_ascii=False, default=str))

# -*- coding: utf-8 -*-


import compat_fix

from experta import *
import json


# ══════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ══════════════════════════════════════════════════════

def adjust_color(rgb_tuple, brightness_offset=0, warm_offset=0):
    
    r, g, b = rgb_tuple
    r = min(255, max(0, int(r + brightness_offset + warm_offset)))
    g = min(255, max(0, int(g + brightness_offset)))
    b = min(255, max(0, int(b + brightness_offset - warm_offset)))
    
    hex_code = f"#{r:02x}{g:02x}{b:02x}"
    return hex_code, (r, g, b)


# ══════════════════════════════════════════════════════
# FACTS
# ══════════════════════════════════════════════════════

class SkinProfile(Fact):
    depth = Field(str)
    undertone = Field(str)
    skin_type = Field(str, default='Normal')
    color_hex = Field(str, default='#c68c64')
    color_rgb = Field(tuple, default=(198, 140, 100))


class FoundationShade(Fact):
    depth = Field(str)
    undertone = Field(str)
    shade_range = Field(str)
    color_descriptor = Field(str)
    suggested_hex = Field(str)
    suggested_rgb = Field(tuple)


class FoundationFormula(Fact):
    skin_type = Field(str)
    name_ar = Field(str)
    primary = Field(str)
    texture = Field(str)
    coverage = Field(str)
    reason = Field(str)


class ConcealerShade(Fact):
    depth = Field(str)
    concealer_descriptor = Field(str)
    reason = Field(str)
    suggested_hex = Field(str)
    suggested_rgb = Field(tuple)


class PrimerMatch(Fact):
    skin_type = Field(str)
    name_ar = Field(str)
    primer_type = Field(str)
    function = Field(str)


class SettingProtocol(Fact):
    skin_type = Field(str)
    setting_method = Field(str)
    technique = Field(str)
    reason = Field(str)


class FoundationRecommendation(Fact):
    depth = Field(str)
    undertone = Field(str)
    skin_type = Field(str)
    shade_range = Field(str)
    formula = Field(str)
    complete = Field(bool, default=False)


# ══════════════════════════════════════════════════════
# RULES
# ══════════════════════════════════════════════════════

class FoundationRulesKB(KnowledgeEngine):

    # ──── درجة الأساس (٦ حالات: عمق × أندرتون مع حساب الألوان) ────

    @Rule(SkinProfile(depth='Fair', undertone='Warm', color_rgb=MATCH.rgb))
    def fair_warm_shade(self, rgb):
        hex_val, rgb_val = adjust_color(rgb, brightness_offset=5, warm_offset=3)
        self.declare(FoundationShade(depth='Fair', undertone='Warm', shade_range='فاتحة ذهبية',
                                      color_descriptor='درجة فاتحة ذهبية الميل',
                                      suggested_hex=hex_val, suggested_rgb=rgb_val))

    @Rule(SkinProfile(depth='Medium', undertone='Warm', color_rgb=MATCH.rgb))
    def medium_warm_shade(self, rgb):
        hex_val, rgb_val = adjust_color(rgb, brightness_offset=3, warm_offset=4)
        self.declare(FoundationShade(depth='Medium', undertone='Warm', shade_range='متوسطة عسلية/ذهبية',
                                      color_descriptor='درجة متوسطة عسلية/ذهبية',
                                      suggested_hex=hex_val, suggested_rgb=rgb_val))

    @Rule(SkinProfile(depth='Dark', undertone='Warm', color_rgb=MATCH.rgb))
    def dark_warm_shade(self, rgb):
        hex_val, rgb_val = adjust_color(rgb, brightness_offset=2, warm_offset=5)
        self.declare(FoundationShade(depth='Dark', undertone='Warm', shade_range='داكنة كراميلية دافئة',
                                      color_descriptor='درجة داكنة دافئة كراميلية',
                                      suggested_hex=hex_val, suggested_rgb=rgb_val))

    @Rule(SkinProfile(depth='Fair', undertone='Cool', color_rgb=MATCH.rgb))
    def fair_cool_shade(self, rgb):
        hex_val, rgb_val = adjust_color(rgb, brightness_offset=5, warm_offset=-3)
        self.declare(FoundationShade(depth='Fair', undertone='Cool', shade_range='فاتحة وردية/محايدة',
                                      color_descriptor='درجة فاتحة وردية/محايدة',
                                      suggested_hex=hex_val, suggested_rgb=rgb_val))

    @Rule(SkinProfile(depth='Medium', undertone='Cool', color_rgb=MATCH.rgb))
    def medium_cool_shade(self, rgb):
        hex_val, rgb_val = adjust_color(rgb, brightness_offset=3, warm_offset=-3)
        self.declare(FoundationShade(depth='Medium', undertone='Cool', shade_range='متوسطة بيج ورديّة',
                                      color_descriptor='درجة متوسطة بيج ورديّة',
                                      suggested_hex=hex_val, suggested_rgb=rgb_val))

    @Rule(SkinProfile(depth='Dark', undertone='Cool', color_rgb=MATCH.rgb))
    def dark_cool_shade(self, rgb):
        hex_val, rgb_val = adjust_color(rgb, brightness_offset=2, warm_offset=-4)
        self.declare(FoundationShade(depth='Dark', undertone='Cool', shade_range='داكنة باردة (إسبريسو)',
                                      color_descriptor='درجة داكنة باردة (إسبريسو)',
                                      suggested_hex=hex_val, suggested_rgb=rgb_val))

    # ──── نوع/تركيبة الأساس حسب نوع البشرة ────

    @Rule(SkinProfile(skin_type='Oily'))
    def oily_foundation(self):
        self.declare(FoundationFormula(skin_type='Oily', name_ar='البشرة الدهنية', primary='أساس بودرة / سائل مطفأ',
                                        texture='مطفأ', coverage='متوسطة إلى كاملة',
                                        reason='تمتص الدهون الزائدة وتثبت لفترة أطول'))

    @Rule(SkinProfile(skin_type='Dry'))
    def dry_foundation(self):
        self.declare(FoundationFormula(skin_type='Dry', name_ar='البشرة الجافة', primary='أساس سائل مرطّب / كريمي',
                                        texture='نضر ولامع بلطف', coverage='خفيفة إلى متوسطة',
                                        reason='يمنح ترطيباً ويتفادى إبراز مناطق التقشر'))

    @Rule(SkinProfile(skin_type='Combination'))
    def combination_foundation(self):
        self.declare(FoundationFormula(skin_type='Combination', name_ar='البشرة المختلطة', primary='أساس سائل شبه مطفأ',
                                        texture='شبه مطفأ', coverage='متوسطة',
                                        reason='يوازن بين تثبيت منطقة T وترطيب باقي الوجه'))

    @Rule(SkinProfile(skin_type='Sensitive'))
    def sensitive_foundation(self):
        self.declare(FoundationFormula(skin_type='Sensitive', name_ar='البشرة الحساسة', primary='أساس معدني خالٍ من العطور',
                                        texture='ساتان طبيعي', coverage='خفيفة إلى متوسطة',
                                        reason='يقلل خطر التهيج ويحافظ على راحة البشرة'))

    @Rule(SkinProfile(skin_type='Normal'))
    def normal_foundation(self):
        self.declare(FoundationFormula(skin_type='Normal', name_ar='البشرة العادية', primary='أساس سائل بلمسة ساتان',
                                        texture='ساتان', coverage='متوسطة',
                                        reason='يمنح مظهراً طبيعياً متوازناً دون الحاجة لتصحيح كبير'))

    # ──── الكونسيلر حسب العمق وحساب درجة اللون ────

    @Rule(SkinProfile(depth='Fair', color_rgb=MATCH.rgb))
    def fair_concealer(self, rgb):
        hex_val, rgb_val = adjust_color(rgb, brightness_offset=15)
        self.declare(ConcealerShade(depth='Fair', concealer_descriptor='درجة أفتح من الأساس بدرجة واحدة',
                                     reason='لتفتيح منطقة تحت العين وتصحيح الهالات',
                                     suggested_hex=hex_val, suggested_rgb=rgb_val))

    @Rule(SkinProfile(depth='Medium', color_rgb=MATCH.rgb))
    def medium_concealer(self, rgb):
        hex_val, rgb_val = adjust_color(rgb, brightness_offset=20)
        self.declare(ConcealerShade(depth='Medium', concealer_descriptor='درجة أفتح بدرجة إلى درجة ونصف من الأساس',
                                     reason='لتفتيح متوازن دون ظهور طبقة رمادية تحت العين',
                                     suggested_hex=hex_val, suggested_rgb=rgb_val))

    @Rule(SkinProfile(depth='Dark', color_rgb=MATCH.rgb))
    def dark_concealer(self, rgb):
        hex_val, rgb_val = adjust_color(rgb, brightness_offset=15, warm_offset=8)
        self.declare(ConcealerShade(depth='Dark', concealer_descriptor='درجة أفتح مع أندرتون دافئ برتقالي خفيف',
                                     reason='لتحييد الهالات الداكنة دون ترك أثر رمادي',
                                     suggested_hex=hex_val, suggested_rgb=rgb_val))

    # ──── البرايمر حسب نوع البشرة ────

    @Rule(SkinProfile(skin_type='Oily'))
    def oily_primer(self):
        self.declare(PrimerMatch(skin_type='Oily', name_ar='البشرة الدهنية', primer_type='برايمر مطفئ للمعان (أساسه سيليكا)',
                                  function='تقليل لمعان الدهون وتوسيع ثبات المكياج'))

    @Rule(SkinProfile(skin_type='Dry'))
    def dry_primer(self):
        self.declare(PrimerMatch(skin_type='Dry', name_ar='البشرة الجافة', primer_type='برايمر مرطّب ومضيء',
                                  function='ترطيب البشرة وتحضيرها لامتصاص أفضل للأساس'))

    @Rule(SkinProfile(skin_type='Combination'))
    def combination_primer(self):
        self.declare(PrimerMatch(skin_type='Combination', name_ar='البشرة المختلطة', primer_type='برايمر موازن ومقلّص للمسام',
                                  function='تنظيم إفراز الدهون في منطقة T مع ترطيب الأطراف'))

    @Rule(SkinProfile(skin_type='Sensitive'))
    def sensitive_primer(self):
        self.declare(PrimerMatch(skin_type='Sensitive', name_ar='البشرة الحساسة', primer_type='برايمر مهدّئ خالٍ من العطور',
                                  function='تهدئة البشرة وتقليل احتمال التهيج'))

    @Rule(SkinProfile(skin_type='Normal'))
    def normal_primer(self):
        self.declare(PrimerMatch(skin_type='Normal', name_ar='البشرة العادية', primer_type='برايمر منعّم ومقلّص للمسام',
                                  function='تنعيم الملمس وتحضير سطح موحد للأساس'))

    # ──── بروتوكول التثبيت ────

    @Rule(SkinProfile(skin_type='Oily'))
    def oily_setting(self):
        self.declare(SettingProtocol(skin_type='Oily', setting_method='بودرة تثبيت + رذاذ تثبيت مطفئ للمعان',
                                      technique='تثبيت كامل الوجه ببودرة شفافة مع التركيز على منطقة T',
                                      reason='لإطالة مدة الثبات ومنع ظهور اللمعان خلال اليوم'))

    @Rule(SkinProfile(skin_type='Dry'))
    def dry_setting(self):
        self.declare(SettingProtocol(skin_type='Dry', setting_method='رذاذ تثبيت مرطّب ومضيء فقط',
                                      technique='تفادي البودرة الكثيفة والاكتفاء برذاذ التثبيت',
                                      reason='للحفاظ على النضارة وتجنب إبراز الجفاف'))

    @Rule(SkinProfile(skin_type='Combination'))
    def combination_setting(self):
        self.declare(SettingProtocol(skin_type='Combination', setting_method='بودرة موضعية على منطقة T + رذاذ تثبيت عام',
                                      technique='تثبيت انتقائي حسب مناطق الوجه',
                                      reason='لتحقيق توازن بين التثبيت والنضارة'))

    @Rule(SkinProfile(skin_type='Sensitive'))
    def sensitive_setting(self):
        self.declare(SettingProtocol(skin_type='Sensitive', setting_method='رذاذ تثبيت خالٍ من العطور',
                                      technique='طبقة تثبيت خفيفة جداً',
                                      reason='لتقليل خطر التهيج مع الحفاظ على الثبات'))

    @Rule(SkinProfile(skin_type='Normal'))
    def normal_setting(self):
        self.declare(SettingProtocol(skin_type='Normal', setting_method='بودرة خفيفة + رذاذ تثبيت',
                                      technique='تثبيت عام متوازن',
                                      reason='للحفاظ على المظهر الطبيعي طوال اليوم'))

    # ──── التوصية النهائية ────

    @Rule(FoundationShade(depth=MATCH.depth, undertone=MATCH.undertone, shade_range=MATCH.shade_range),
          FoundationFormula(skin_type=MATCH.skin_type, primary=MATCH.primary))
    def final_foundation_recommendation(self, depth, undertone, shade_range, skin_type, primary):
        self.declare(FoundationRecommendation(depth=depth, undertone=undertone, skin_type=skin_type,
                                               shade_range=shade_range, formula=primary, complete=True))


# ══════════════════════════════════════════════════════
# ENGINE
# ══════════════════════════════════════════════════════

class FoundationEngine(FoundationRulesKB):
    """محرك الأساس والكونسيلر المطور"""

    def __init__(self):
        super().__init__()

    def analyze_foundation(self, skin_data):
        self.reset()
        
        # قبول المسميات المستخرجة من skin_analysis سواء skin_depth أو depth
        depth = skin_data.get('skin_depth') or skin_data.get('depth', 'Medium')
        undertone = skin_data.get('undertone', 'Warm')
        skin_type = skin_data.get('skin_type', 'Normal')
        color_hex = skin_data.get('color_hex', '#c68c64')
        
        # التأكد من تحويل RGB إلى tuple
        raw_rgb = skin_data.get('color_rgb', (198, 140, 100))
        color_rgb = tuple(raw_rgb) if isinstance(raw_rgb, (list, tuple)) else (198, 140, 100)

        self.declare(
            SkinProfile(
                depth=depth,
                undertone=undertone,
                skin_type=skin_type,
                color_hex=color_hex,
                color_rgb=color_rgb
            )
        )
        self.run()
        return self._extract_results()

    def _extract_results(self):
        results = {'shade': None, 'formula': None, 'concealer': None, 'primer': None,
                   'setting': None, 'recommendation': None}
        for fact in self.facts.values():
            if isinstance(fact, FoundationShade):
                results['shade'] = {
                    'range': fact.get('shade_range'), 
                    'descriptor': fact.get('color_descriptor'),
                    'hex': fact.get('suggested_hex'),
                    'rgb': fact.get('suggested_rgb')
                }
            elif isinstance(fact, FoundationFormula):
                results['formula'] = {'primary': fact.get('primary'), 'texture': fact.get('texture'),
                                       'coverage': fact.get('coverage'), 'reason': fact.get('reason')}
            elif isinstance(fact, ConcealerShade):
                results['concealer'] = {
                    'descriptor': fact.get('concealer_descriptor'), 
                    'reason': fact.get('reason'),
                    'hex': fact.get('suggested_hex'),
                    'rgb': fact.get('suggested_rgb')
                }
            elif isinstance(fact, PrimerMatch):
                results['primer'] = {'type': fact.get('primer_type'), 'function': fact.get('function')}
            elif isinstance(fact, SettingProtocol):
                results['setting'] = {'method': fact.get('setting_method'), 'technique': fact.get('technique'),
                                       'reason': fact.get('reason')}
            elif isinstance(fact, FoundationRecommendation):
                results['recommendation'] = {'shade_range': fact.get('shade_range'), 'formula': fact.get('formula'),
                                              'complete': fact.get('complete')}
        return results


# ══════════════════════════════════════════════════════
# MAIN TEST (مع نفس مخرجات التحليل لديك)
# ══════════════════════════════════════════════════════

if __name__ == "__main__":
    # محاكاة البيانات القادمة مباشرة من skin_analysis.py
    sample_analysis_output = {
        "success": True,
        "skin_depth": "Medium",
        "undertone": "Warm",
        "skin_type": "Normal",
        "color_lab": {
            "L": 63.137,
            "a": 17.0,
            "b": 30.0
        },
        "color_rgb": [198, 140, 100],
        "color_hex": "#c68c64",
        "confidence": 0.85
    }

    engine = FoundationEngine()
    result = engine.analyze_foundation(sample_analysis_output)
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))