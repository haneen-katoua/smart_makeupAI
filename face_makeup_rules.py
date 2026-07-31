# # -*- coding: utf-8 -*-
# """
# face_makeup_rules.py — Experta-based Expert System (Face Contour / Blush / Highlight)
# ======================================================================================
# مبني على "الخبرة النهائية": يحدد شكل الوجه، ثم يبني توصية النحت والبلاشر والهاياليت،
# ثم يلوّن البلاشر حسب البشرة، ثم يضبط الشفافية حسب المناسبة واستراتيجية العين.
# """

# # ✅ MUST BE FIRST: Python 3.10+ Compatibility Fix
# import compat_fix

# from experta import *
# import json


# # ══════════════════════════════════════════════════════
# # FACTS
# # ══════════════════════════════════════════════════════

# class FaceShapeAnalysis(Fact):
#     shape = Field(str)
#     votes = Field(dict)


# class SkinProfile(Fact):
#     undertone = Field(str)
#     depth = Field(str)


# class FaceFullness(Fact):
#     fullness = Field(str, default='Full')


# class EyeMakeupStrategy(Fact):
#     strategy = Field(str, default='Monochromatic')


# class OccasionContext(Fact):
#     occasion = Field(str)


# class FaceShapeCategory(Fact):
#     shape = Field(str)
#     name_ar = Field(str)
#     goal = Field(str)
#     priority = Field(int, default=0)


# class SculptRule(Fact):
#     placement = Field(str)
#     purpose = Field(str)


# class BlushRule(Fact):
#     placement = Field(str)
#     purpose = Field(str)


# class HighlightRule(Fact):
#     placement = Field(str)
#     purpose = Field(str)


# class BlushColorMatch(Fact):
#     undertone = Field(str)
#     depth = Field(str)
#     base_color = Field(str)
#     palette = Field(str)


# class BlushAdjustment(Fact):
#     strategy = Field(str)
#     rule = Field(str)
#     opacity = Field(int)


# class BlushTexture(Fact):
#     occasion = Field(str)
#     finish = Field(str)
#     transparency = Field(str)
#     description = Field(str)


# class FaceContourBlushRecommendation(Fact):
#     shape = Field(str)
#     base_color = Field(str)
#     occasion = Field(str)
#     complete = Field(bool, default=False)


# # ══════════════════════════════════════════════════════
# # RULES
# # ══════════════════════════════════════════════════════

# class FaceContourRulesKB(KnowledgeEngine):

#     # ──── الوجه البيضاوي ────

#     @Rule(FaceShapeAnalysis(shape='Oval'), FaceFullness(fullness='Full'))
#     def oval_full_face(self):
#         self.declare(
#             FaceShapeCategory(shape='Oval', name_ar='الوجه البيضاوي (Face Oval)',
#                                goal='الحفاظ على التوازن المثالي وتعريف الملامح', priority=1),
#             SculptRule(placement='نحت خفيف جداً فوق البلاشر مباشرة، على عظمة الخد',
#                        purpose='زيادة البعد ثلاثي الأبعاد دون كسر توازن الوجه'),
#             BlushRule(placement='على تفاحتي الخد فقط، بدمج مسحوب للأعلى باتجاه الأذن',
#                       purpose='الحفاظ على النضارة الطبيعية ورفع ملامح الوجه'),
#             HighlightRule(placement='تحت عظمة الخد مباشرة فوق خط الكونتور',
#                           purpose='تعريف الملامح وإبراز عظمة الخد')
#         )

#     @Rule(FaceShapeAnalysis(shape='Oval'), FaceFullness(fullness='Thin'))
#     def oval_thin_face(self):
#         self.declare(
#             FaceShapeCategory(shape='Oval', name_ar='الوجه البيضاوي (Face Oval)',
#                                goal='الحفاظ على التوازن المثالي مع تفادي مظهر الوجه الغارق', priority=1),
#             SculptRule(placement='استبدال الكونتور الداكن ببرونز دافئ خفيف جداً، بدمج دائري في مركز الخد',
#                        purpose='منع ظهور "الوجه الغارق" وإعطاء حيوية بدل النحت الحاد'),
#             BlushRule(placement='في مركز الخد بدمج ناعم جداً باتجاه الأذن',
#                       purpose='إعطاء حجم حيوي للخدود النحيفة'),
#             HighlightRule(placement='لمسة بسيطة جداً على جسر الأنف بنفس لون البلاشر',
#                           purpose='توحيد الإضاءة وتفادي مظهر النحول الزائد')
#         )

#     # ──── الوجه الدائري ────

#     @Rule(FaceShapeAnalysis(shape='Round'), FaceFullness(fullness='Full'))
#     def round_full_face(self):
#         self.declare(
#             FaceShapeCategory(shape='Round', name_ar='الوجه الدائري (Face Round)',
#                                goal='كسر الاستدارة، تقليل العرض، وإعطاء إيحاء بالطول والحدة', priority=2),
#             SculptRule(placement='نحت نازل وحاد من الأذن للزاوية تحت الفم، مع تحديد خط الفك لتعريف العظم',
#                        purpose='كسر استدارة الخدين وتعريف عظمة الفك'),
#             BlushRule(placement='تحت العين مباشرة، مسحوب للأعلى ومدمج مع ظل العين',
#                       purpose='رفع ملامح الوجه بصرياً'),
#             HighlightRule(placement='على رأس الخدين (أعلى نقطة) والذقن',
#                           purpose='زيادة المدى الطولي الظاهر للوجه')
#         )

#     @Rule(FaceShapeAnalysis(shape='Round'), FaceFullness(fullness='Thin'))
#     def round_thin_face(self):
#         self.declare(
#             FaceShapeCategory(shape='Round', name_ar='الوجه الدائري (Face Round)',
#                                goal='كسر الاستدارة بلطف مع الحفاظ على حيوية الخدود', priority=2),
#             SculptRule(placement='كونتور عادي من منتصف الأذن إلى منتصف الخد',
#                        purpose='تعريف الهيكل الطبيعي دون حدة زائدة'),
#             BlushRule(placement='من جانب الأنف مسحوب باتجاه الزاوية الخارجية للعين',
#                       purpose='تعزيز الحدة والإطالة البصرية'),
#             HighlightRule(placement='فوق عظمة الخد مباشرة',
#                           purpose='تعزيز البروز الطبيعي للخد')
#         )

#     # ──── الوجه المستطيل ────

#     @Rule(FaceShapeAnalysis(shape='Rectangular'), FaceFullness(fullness='Full'))
#     def rectangular_full_face(self):
#         self.declare(
#             FaceShapeCategory(shape='Rectangular', name_ar='الوجه المستطيل (Face Rectangular)',
#                                goal='تقصير المدى العمودي وزيادة العرض الوهمي لمقاربته من الشكل البيضاوي', priority=3),
#             SculptRule(placement='خط أفقي صريح من منتصف الأذن إلى منتصف الخد لكسر طول الوجه',
#                        purpose='كسر الخط العمودي المستمر'),
#             BlushRule(placement='يوضع بشكل عرضي بجانب الكونتور',
#                       purpose='زيادة عرض الوجه بصرياً'),
#             HighlightRule(placement='وسط الجبهة والذقن فقط',
#                           purpose='جذب الانتباه للمركز وتجنب إطالة الأطراف')
#         )

#     @Rule(FaceShapeAnalysis(shape='Rectangular'), FaceFullness(fullness='Thin'))
#     def rectangular_thin_face(self):
#         self.declare(
#             FaceShapeCategory(shape='Rectangular', name_ar='الوجه المستطيل (Face Rectangular)',
#                                goal='تقصير الوجه بصرياً وتخفيف حدة الفك الطويل', priority=3),
#             SculptRule(placement='تظليل ناعم عند منبت الشعر (أعلى الجبهة) وأسفل الذقن فقط',
#                        purpose='تقصير الوجه بصرياً'),
#             BlushRule(placement='على الصدغين وجوانب الجبهة',
#                       purpose='زيادة عرض الوجه في المنطقة العلوية'),
#             HighlightRule(placement='وسط الجبهة والذقن فقط',
#                           purpose='جذب الانتباه للمركز')
#         )

#     # ──── الوجه المربع ────

#     @Rule(FaceShapeAnalysis(shape='Square'))
#     def square_face(self):
#         self.declare(
#             FaceShapeCategory(shape='Square', name_ar='الوجه المربع (Face Square)',
#                                goal='تليين حدة زوايا الفك وإضافة انسيابية للملامح', priority=4),
#             SculptRule(placement='نحت خفيف على زوايا الفك مع تدوير خط الكونتور',
#                        purpose='تليين حدة الزوايا'),
#             BlushRule(placement='على تفاحتي الخد بشكل دائري ناعم',
#                       purpose='إضافة انسيابية بصرية للوجه'),
#             HighlightRule(placement='وسط الجبهة وأعلى الخدين',
#                           purpose='دعم التصحيح البصري لشكل الوجه')
#         )

#     # ──── الوجه القلب ────

#     @Rule(FaceShapeAnalysis(shape='Heart'))
#     def heart_face(self):
#         self.declare(
#             FaceShapeCategory(shape='Heart', name_ar='الوجه القلب (Face Heart)',
#                                goal='موازنة عرض الجبهة مع تخفيف الثقل البصري في منطقة الفك', priority=4),
#             SculptRule(placement='نحت خفيف على جانبي الجبهة وزاويتيها',
#                        purpose='تصغير عرض الجبهة بصرياً'),
#             BlushRule(placement='تحت عظمة الخد باتجاه منتصف الوجه',
#                       purpose='إضافة عرض بصري لمنطقة الفك والذقن'),
#             HighlightRule(placement='على الذقن ومنتصف الجبهة',
#                           purpose='موازنة أبعاد الوجه')
#         )

#     # ──── الوجه الماسي ────

#     @Rule(FaceShapeAnalysis(shape='Diamond'))
#     def diamond_face(self):
#         self.declare(
#             FaceShapeCategory(shape='Diamond', name_ar='الوجه الماسي (Face Diamond)',
#                                goal='توسيع الجبهة والفك بصرياً وتليين بروز عظام الخد', priority=4),
#             SculptRule(placement='نحت خفيف جداً على عظمة الخد البارزة فقط',
#                        purpose='تليين حدة بروز عظام الخد'),
#             BlushRule(placement='على تفاحتي الخد بامتداد أفقي خفيف',
#                       purpose='توسيع منطقة الخد بصرياً'),
#             HighlightRule(placement='وسط الجبهة والذقن',
#                           purpose='توسيع الجبهة والفك بصرياً')
#         )

#     # ──── Rule: مصفوفة لون البلاشر حسب البشرة (٦ حالات) ────

#     @Rule(SkinProfile(undertone='Warm', depth='Fair'))
#     def warm_fair_blush(self):
#         self.declare(BlushColorMatch(undertone='Warm', depth='Fair', base_color='خوخي ذهبي', palette='أساس دافئ'))

#     @Rule(SkinProfile(undertone='Warm', depth='Medium'))
#     def warm_medium_blush(self):
#         self.declare(BlushColorMatch(undertone='Warm', depth='Medium', base_color='مرجاني', palette='أساس دافئ'))

#     @Rule(SkinProfile(undertone='Warm', depth='Dark'))
#     def warm_dark_blush(self):
#         self.declare(BlushColorMatch(undertone='Warm', depth='Dark', base_color='برتقالي محروق', palette='أساس دافئ'))

#     @Rule(SkinProfile(undertone='Cool', depth='Fair'))
#     def cool_fair_blush(self):
#         self.declare(BlushColorMatch(undertone='Cool', depth='Fair', base_color='موف فاتح', palette='أساس بارد'))

#     @Rule(SkinProfile(undertone='Cool', depth='Medium'))
#     def cool_medium_blush(self):
#         self.declare(BlushColorMatch(undertone='Cool', depth='Medium', base_color='وردي ترابي', palette='أساس بارد'))

#     @Rule(SkinProfile(undertone='Cool', depth='Dark'))
#     def cool_dark_blush(self):
#         self.declare(BlushColorMatch(undertone='Cool', depth='Dark', base_color='وردي توتي غامق', palette='أساس بارد'))

#     # ──── Rule: تعديل اللون حسب استراتيجية مكياج العين ────

#     @Rule(EyeMakeupStrategy(strategy='Monochromatic'))
#     def monochromatic_blush_adjustment(self):
#         self.declare(BlushAdjustment(strategy='Monochromatic',
#                                       rule='يُختار اللون من المصفوفة بنفس درجة "حرارة" ظل العين ولون البشرة',
#                                       opacity=100))

#     @Rule(EyeMakeupStrategy(strategy='Contrast'))
#     def contrast_blush_adjustment(self):
#         self.declare(BlushAdjustment(strategy='Contrast',
#                                       rule='يُحيَّد اللون ويُجعل باهتاً وشفافاً جداً (شفاف بنسبة 80%) كي تبقى العين هي "البطل"',
#                                       opacity=20))

#     @Rule(EyeMakeupStrategy(strategy='Triadic'))
#     def triadic_blush_adjustment(self):
#         self.declare(BlushAdjustment(strategy='Triadic',
#                                       rule='يُحيَّد اللون ويُجعل باهتاً وشفافاً جداً (شفاف بنسبة 80%) كي تبقى العين هي "البطل"',
#                                       opacity=20))

#     @Rule(EyeMakeupStrategy(strategy='Earthy'))
#     def earthy_blush_adjustment(self):
#         self.declare(BlushAdjustment(strategy='Earthy',
#                                       rule='يُختار اللون من المصفوفة بأقصى حيوية لكسر رتابة الألوان الترابية',
#                                       opacity=100))

#     # ──── Rule: القوام والشفافية حسب المناسبة ────

#     @Rule(OccasionContext(occasion='work'))
#     def work_blush_texture(self):
#         self.declare(BlushTexture(occasion='work', finish='مطفأ', transparency='شفاف بنسبة 80%',
#                                    description='تورّد طبيعي نابع من الجلد'))

#     @Rule(OccasionContext(occasion='university'))
#     def university_blush_texture(self):
#         self.declare(BlushTexture(occasion='university', finish='مطفأ', transparency='شفاف بنسبة 80%',
#                                    description='تورّد طبيعي نابع من الجلد'))

#     @Rule(OccasionContext(occasion='evening'))
#     def evening_blush_texture(self):
#         self.declare(BlushTexture(occasion='evening', finish='ساتان / لامع', transparency='صبغة كاملة',
#                                    description='لون قوي يبرز تحت أضواء السهرة'))

#     @Rule(OccasionContext(occasion='wedding'))
#     def wedding_blush_texture(self):
#         self.declare(BlushTexture(occasion='wedding', finish='ساتان / لامع', transparency='صبغة كاملة',
#                                    description='لون قوي يبرز تحت أضواء السهرة'))

#     @Rule(OccasionContext(occasion='party'))
#     def party_blush_texture(self):
#         self.declare(BlushTexture(occasion='party', finish='ساتان / لامع', transparency='صبغة كاملة',
#                                    description='لون قوي يبرز تحت الإضاءة'))

#     @Rule(OccasionContext(occasion='photo'))
#     def photo_blush_texture(self):
#         self.declare(BlushTexture(occasion='photo', finish='مطفأ', transparency='صبغة كاملة بلا لمعان',
#                                    description='مطفأ تماماً لتفادي انعكاس الفلاش'))

#     # ──── Rule: التوصية النهائية ────

#     @Rule(FaceShapeCategory(shape=MATCH.shape),
#           BlushColorMatch(base_color=MATCH.base_color),
#           OccasionContext(occasion=MATCH.occasion))
#     def final_face_recommendation(self, shape, base_color, occasion):
#         self.declare(FaceContourBlushRecommendation(shape=shape, base_color=base_color, occasion=occasion, complete=True))


# # ══════════════════════════════════════════════════════
# # ENGINE
# # ══════════════════════════════════════════════════════

# class FaceContourEngine(FaceContourRulesKB):
#     """محرك الكونتور والبلاشر والهاياليت"""

#     def __init__(self):
#         super().__init__()

#     def analyze_face(self, face_data):
#         """
#         input: dict {
#             'shape': 'Oval', 'votes': {...},
#             'undertone': 'Warm', 'depth': 'Medium',
#             'fullness': 'Full',
#             'eye_strategy': 'Monochromatic',
#             'occasion': 'evening'
#         }
#         """
#         self.reset()
#         self.declare(
#             FaceShapeAnalysis(shape=face_data.get('shape', 'Oval'), votes=face_data.get('votes', {})),
#             SkinProfile(undertone=face_data.get('undertone', 'Warm'), depth=face_data.get('depth', 'Medium')),
#             FaceFullness(fullness=face_data.get('fullness', 'Full')),
#             EyeMakeupStrategy(strategy=face_data.get('eye_strategy', 'Monochromatic')),
#             OccasionContext(occasion=face_data.get('occasion', 'work'))
#         )
#         self.run()
#         return self._extract_results()

#     def _extract_results(self):
#         results = {'shape': None, 'sculpt': None, 'blush': None, 'highlight': None,
#                    'color': None, 'adjustment': None, 'texture': None, 'recommendation': None}

#         for fact in self.facts.values():
#             if isinstance(fact, FaceShapeCategory):
#                 results['shape'] = {'shape': fact.get('shape'), 'name_ar': fact.get('name_ar'), 'goal': fact.get('goal')}
#             elif isinstance(fact, SculptRule):
#                 results['sculpt'] = {'placement': fact.get('placement'), 'purpose': fact.get('purpose')}
#             elif isinstance(fact, BlushRule):
#                 results['blush'] = {'placement': fact.get('placement'), 'purpose': fact.get('purpose')}
#             elif isinstance(fact, HighlightRule):
#                 results['highlight'] = {'placement': fact.get('placement'), 'purpose': fact.get('purpose')}
#             elif isinstance(fact, BlushColorMatch):
#                 results['color'] = {'base_color': fact.get('base_color'), 'palette': fact.get('palette')}
#             elif isinstance(fact, BlushAdjustment):
#                 results['adjustment'] = {'rule': fact.get('rule'), 'opacity': fact.get('opacity')}
#             elif isinstance(fact, BlushTexture):
#                 results['texture'] = {'finish': fact.get('finish'), 'transparency': fact.get('transparency'),
#                                        'description': fact.get('description')}
#             elif isinstance(fact, FaceContourBlushRecommendation):
#                 results['recommendation'] = {'shape': fact.get('shape'), 'color': fact.get('base_color'),
#                                               'occasion': fact.get('occasion'), 'complete': fact.get('complete')}

#         return results


# if __name__ == "__main__":
#     engine = FaceContourEngine()
#     result = engine.analyze_face({'shape': 'Oval', 'undertone': 'Warm', 'depth': 'Medium', 'occasion': 'evening'})
#     print(json.dumps(result, indent=2, ensure_ascii=False, default=str))

# -*- coding: utf-8 -*-
"""
face_makeup_rules.py — Experta-based Expert System (Face Contour / Blush / Highlight)
======================================================================================
مبني على "الخبرة النهائية": يحدد شكل الوجه، ثم يبني توصية النحت والبلاشر والهاياليت،
ثم يلوّن البلاشر حسب البشرة، ويحدد درجات الكونتور والهايلايتر،
ثم يضبط الشفافية (Opacity) والملمس لكل المنتجات حسب المناسبة.
"""

# ✅ MUST BE FIRST: Python 3.10+ Compatibility Fix
import compat_fix

from experta import *
import json


# ══════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ══════════════════════════════════════════════════════

def clean_experta_types(obj):
    """تحويل كائنات frozendict و frozenlist الخاصة بـ experta إلى dict و list لطباعة JSON نظيفة"""
    if type(obj).__name__ == 'frozendict':
        return dict(obj)
    elif type(obj).__name__ == 'frozenlist':
        return list(obj)
    return str(obj)


def get_blush_palette_shades(base_color):
    """توليد مجموعة درجات متنوعة وأكواد HEX/RGB بناءً على اللون الأساسي للبلاشر"""
    if base_color == 'برتقالي محروق':
        return {
            'primary': {'name': 'برتقالي محروق رئيسي (Burnt Orange)', 'hex': '#CC5500', 'rgb': (204, 85, 0)},
            'shades': [
                {'name': 'تراكوتا دافئ (Warm Terracotta)', 'hex': '#E07A5F', 'rgb': (224, 122, 95)},
                {'name': 'قرفة دافئة (Spiced Cinnamon)', 'hex': '#D2691E', 'rgb': (210, 105, 30)},
                {'name': 'برتقالي نحاسي غامق (Deep Copper)', 'hex': '#B85042', 'rgb': (184, 80, 66)}
            ]
        }
    elif base_color == 'وردي توتي غامق':
        return {
            'primary': {'name': 'وردي توتي غامق رئيسي (Deep Berry Rose)', 'hex': '#8E2A59', 'rgb': (142, 42, 89)},
            'shades': [
                {'name': 'توتي plum ناعم (Soft Plum)', 'hex': '#9B51E0', 'rgb': (155, 81, 224)},
                {'name': 'وردي عنابي (Burgundy Rose)', 'hex': '#800020', 'rgb': (128, 0, 32)},
                {'name': 'توتي خمر يافع (Muted Berry)', 'hex': '#A0522D', 'rgb': (160, 82, 45)}
            ]
        }
    elif base_color == 'مرجاني':
        return {
            'primary': {'name': 'مرجاني دافئ (Warm Coral)', 'hex': '#E07A5F', 'rgb': (224, 122, 95)},
            'shades': [
                {'name': 'مرجاني وردي (Pink Coral)', 'hex': '#F4A261', 'rgb': (244, 162, 97)},
                {'name': 'خوخي مشرق (Bright Peach)', 'hex': '#E76F51', 'rgb': (231, 111, 81)}
            ]
        }
    elif base_color == 'وردي ترابي':
        return {
            'primary': {'name': 'وردي ترابي (Dusty Rose)', 'hex': '#C87D85', 'rgb': (200, 125, 133)},
            'shades': [
                {'name': 'موف ترابي (Dusty Mauve)', 'hex': '#B5718E', 'rgb': (181, 113, 142)},
                {'name': 'وردي بيج (Rose Beige)', 'hex': '#D8A7B1', 'rgb': (216, 167, 177)}
            ]
        }
    elif base_color == 'خوخي ذهبي':
        return {
            'primary': {'name': 'خوخي ذهبي (Golden Peach)', 'hex': '#F2A68D', 'rgb': (242, 166, 141)},
            'shades': [
                {'name': 'خوخي مشرق (Soft Peach)', 'hex': '#F7C59F', 'rgb': (247, 197, 159)}
            ]
        }
    else:  # موف فاتح
        return {
            'primary': {'name': 'موف فاتح (Soft Mauve)', 'hex': '#E0B0FF', 'rgb': (224, 176, 255)},
            'shades': [
                {'name': 'وردي بارد (Cool Pink)', 'hex': '#F8C8DC', 'rgb': (248, 200, 220)}
            ]
        }


def get_contour_highlight_shades(undertone, depth):
    """تحديد درجات الكونتور والهايلايتر مع أكواد HEX و RGB بناءً على لون البشرة"""
    if undertone == 'Warm':
        contour = {'descriptor': 'برونزي دافئ غني', 'hex': '#8B5A2B', 'rgb': (139, 90, 43)} if depth == 'Dark' else \
                  {'descriptor': 'برونزي دافئ متوسط', 'hex': '#A67B5B', 'rgb': (166, 123, 91)} if depth == 'Medium' else \
                  {'descriptor': 'برونزي دافئ فاتح', 'hex': '#C49A45', 'rgb': (196, 154, 69)}
        
        highlight = {'descriptor': 'ذهبي غني/نحاسي', 'hex': '#D4AF37', 'rgb': (212, 175, 55)} if depth == 'Dark' else \
                    {'descriptor': 'ذهبي عسلي/شامبانيا دافئ', 'hex': '#F3E5AB', 'rgb': (243, 229, 171)} if depth == 'Medium' else \
                    {'descriptor': 'عاجي/شامبانيا ذهبي فاتح', 'hex': '#FFF8DC', 'rgb': (255, 248, 220)}
    else:  # Cool
        contour = {'descriptor': 'بني بارد شوكولاتة غامق', 'hex': '#4A2C2A', 'rgb': (74, 44, 42)} if depth == 'Dark' else \
                  {'descriptor': 'رمادي بيج محايد (Taupe)', 'hex': '#8B7D7B', 'rgb': (139, 125, 123)} if depth == 'Medium' else \
                  {'descriptor': 'كونتور رمادي بارد فاتح', 'hex': '#B0A8A6', 'rgb': (176, 168, 166)}
        
        highlight = {'descriptor': 'برونزي لؤلؤي وردي غامق', 'hex': '#C5A059', 'rgb': (197, 160, 89)} if depth == 'Dark' else \
                    {'descriptor': 'لؤلؤي وردي متوسط', 'hex': '#F4C2C2', 'rgb': (244, 194, 194)} if depth == 'Medium' else \
                    {'descriptor': 'فضي لؤلؤي/ثلجي', 'hex': '#F8F8FF', 'rgb': (248, 248, 255)}

    return contour, highlight


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

class OccasionIntensity(Fact):
    """حقيقة خاصة بتشبع الألوان والشفافية لكل من البلاشر والكونتور والهايلايتر"""
    occasion = Field(str)
    blush_opacity = Field(int)
    contour_opacity = Field(int)
    highlight_opacity = Field(int)
    finish = Field(str)
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

    # ──── Rule: القوام والشفافية لكل الأجزاء حسب المناسبة ────
    @Rule(OccasionContext(occasion='work'))
    def work_intensity(self):
        self.declare(OccasionIntensity(
            occasion='work', blush_opacity=40, contour_opacity=45, highlight_opacity=30,
            finish='مطفأ', description='تورّد طبيعي وتحديد ناعم جداً مدموج بالبشرة'
        ))

    @Rule(OccasionContext(occasion='university'))
    def university_intensity(self):
        self.declare(OccasionIntensity(
            occasion='university', blush_opacity=45, contour_opacity=40, highlight_opacity=35,
            finish='مطفأ', description='إطلالة يومية خفيفة ناعمة'
        ))

    @Rule(OccasionContext(occasion='evening'))
    def evening_intensity(self):
        self.declare(OccasionIntensity(
            occasion='evening', blush_opacity=85, contour_opacity=80, highlight_opacity=85,
            finish='ساتان / لامع', description='لون وتحديد بارز يظهر بقوة تحت أضواء السهرة'
        ))

    @Rule(OccasionContext(occasion='wedding'))
    def wedding_intensity(self):
        self.declare(OccasionIntensity(
            occasion='wedding', blush_opacity=100, contour_opacity=85, highlight_opacity=95,
            finish='مخملي غني / براق', description='تحديد وصبغة كاملة عالية الدقة مناسبة للتصوير والفلاش'
        ))

    @Rule(OccasionContext(occasion='party'))
    def party_intensity(self):
        self.declare(OccasionIntensity(
            occasion='party', blush_opacity=90, contour_opacity=75, highlight_opacity=90,
            finish='ساتان / لامع', description='إطلالة براقة ومتألقة تحت الإضاءة'
        ))

    @Rule(OccasionContext(occasion='photo'))
    def photo_intensity(self):
        self.declare(OccasionIntensity(
            occasion='photo', blush_opacity=95, contour_opacity=90, highlight_opacity=70,
            finish='مطفأ تماماً', description='تحديد وتظليل قوي بدون لمعة لتفادي انعكاس الفلاش'
        ))

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
        self.face_data = {}

    def analyze_face(self, face_data):
        self.face_data = face_data
        self.reset()
        self.declare(
            FaceShapeAnalysis(shape=face_data.get('shape', 'Oval'), votes=face_data.get('votes', {})),
            SkinProfile(undertone=face_data.get('undertone', 'Warm'), depth=face_data.get('depth', 'Medium')),
            FaceFullness(fullness=face_data.get('fullness', 'Full')),
            OccasionContext(occasion=face_data.get('occasion', 'work'))
        )
        self.run()
        return self._extract_results()

    def _extract_results(self):
        results = {'shape': None, 'sculpt': None, 'blush': None, 'highlight': None,
                   'color': None, 'texture': None, 'recommendation': None}

        # جلب درجات الألوان بناءً على لون البشرة
        undertone = self.face_data.get('undertone', 'Warm')
        depth = self.face_data.get('depth', 'Medium')
        contour_info, highlight_info = get_contour_highlight_shades(undertone, depth)

        # استخراج قيم الشفافية والمظهر النهائي
        intensity_data = {}
        for fact in self.facts.values():
            if isinstance(fact, OccasionIntensity):
                intensity_data = {
                    'blush_opacity': fact.get('blush_opacity'),
                    'contour_opacity': fact.get('contour_opacity'),
                    'highlight_opacity': fact.get('highlight_opacity'),
                    'finish': fact.get('finish'),
                    'description': fact.get('description')
                }

        for fact in self.facts.values():
            if isinstance(fact, FaceShapeCategory):
                results['shape'] = {'shape': fact.get('shape'), 'name_ar': fact.get('name_ar'), 'goal': fact.get('goal')}
            elif isinstance(fact, SculptRule):
                results['sculpt'] = {
                    'placement': fact.get('placement'), 
                    'purpose': fact.get('purpose'),
                    'shade_descriptor': contour_info['descriptor'],
                    'hex': contour_info['hex'],
                    'rgb': contour_info['rgb'],
                    'opacity': intensity_data.get('contour_opacity', 70)  # 👈 إضافة شفافية الكونتور
                }
            elif isinstance(fact, BlushRule):
                results['blush'] = {
                    'placement': fact.get('placement'), 
                    'purpose': fact.get('purpose'),
                    'opacity': intensity_data.get('blush_opacity', 80)     # 👈 إضافة شفافية البلاشر
                }
            elif isinstance(fact, HighlightRule):
                results['highlight'] = {
                    'placement': fact.get('placement'), 
                    'purpose': fact.get('purpose'),
                    'shade_descriptor': highlight_info['descriptor'],
                    'hex': highlight_info['hex'],
                    'rgb': highlight_info['rgb'],
                    'opacity': intensity_data.get('highlight_opacity', 80) # 👈 إضافة شفافية الهايلايتر
                }
            elif isinstance(fact, BlushColorMatch):
                base_color = fact.get('base_color')
                results['color'] = {
                    'base_color': base_color, 
                    'palette': fact.get('palette'),
                    'shades_details': get_blush_palette_shades(base_color)
                }
            elif isinstance(fact, OccasionIntensity):
                results['texture'] = {
                    'finish': fact.get('finish'),
                    'description': fact.get('description')
                }
            elif isinstance(fact, FaceContourBlushRecommendation):
                results['recommendation'] = {'shape': fact.get('shape'), 'color': fact.get('base_color'),
                                              'occasion': fact.get('occasion'), 'complete': fact.get('complete')}

        return results


if __name__ == "__main__":
    engine = FaceContourEngine()
    result = engine.analyze_face({'shape': 'Oval', 'undertone': 'Warm', 'depth': 'Medium', 'occasion': 'evening'})
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))