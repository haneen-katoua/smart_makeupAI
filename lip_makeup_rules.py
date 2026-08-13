

# # ✅ MUST BE FIRST: Python 3.10+ Compatibility Fix
# import compat_fix

# from experta import *
# import json


# # ══════════════════════════════════════════════════════
# # FACTS
# # ══════════════════════════════════════════════════════

# class LipAnalysis(Fact):
#     volume = Field(str)
#     balance = Field(str)
#     width = Field(str)
#     symmetry = Field(str)
#     cupid_bow = Field(str)
#     corners = Field(str)


# class SkinProfile(Fact):
#     undertone = Field(str)
#     depth = Field(str)


# class OccasionContext(Fact):
#     occasion = Field(str)


# class LipShapeCategory(Fact):
#     category = Field(str)
#     name_ar = Field(str)
#     correction_style = Field(str)
#     technique = Field(str)
#     reason = Field(str)


# class LipColorMatch(Fact):
#     undertone = Field(str)
#     palette = Field(str)
#     colors = Field(str)


# class LipOccasionStyle(Fact):
#     occasion = Field(str)
#     style = Field(str)
#     product = Field(str)
#     texture = Field(str)


# class LipRecommendation(Fact):
#     shape_category = Field(str)
#     lip_colors = Field(str)
#     occasion = Field(str)
#     complete = Field(bool, default=False)


# # ══════════════════════════════════════════════════════
# # RULES
# # ══════════════════════════════════════════════════════

# class LipRulesKB(KnowledgeEngine):

#     # ──── Rule 1: تصنيف حالة الشفاه ────

#     @Rule(LipAnalysis(volume='Thin', balance='Balanced'))
#     def thin_lips_detected(self):
#         self.declare(LipShapeCategory(
#             category='Thin', name_ar='شفاه رقيقة',
#             correction_style='تكبير للخارج (Overline)',
#             technique='رسم لاينر الشفاه خارج الحد الطبيعي للشفة',
#             reason='لخلق إيحاء بامتلاء أكبر'))

#     @Rule(LipAnalysis(volume='Thin', balance='Upper Fuller'))
#     def thin_upper_lip_detected(self):
#         self.declare(LipShapeCategory(
#             category='Upper Thin', name_ar='شفة علوية رقيقة',
#             correction_style='موازنة النسبة',
#             technique='رسم الخط أعلى الحد الطبيعي للشفة العلوية',
#             reason='لتحقيق التماثل بين الشفتين العلوية والسفلى'))

#     @Rule(LipAnalysis(volume='Thin', balance='Lower Fuller'))
#     def thin_lower_lip_detected(self):
#         self.declare(LipShapeCategory(
#             category='Lower Thin', name_ar='شفة سفلى رقيقة',
#             correction_style='موازنة النسبة',
#             technique='رسم الخط أسفل الحد الطبيعي للشفة السفلى',
#             reason='لضمان التوازن البصري وتماثل الفم'))

#     @Rule(LipAnalysis(volume='Medium', balance='Upper Fuller'))
#     def medium_upper_fuller(self):
#         self.declare(LipShapeCategory(
#             category='Upper Thin', name_ar='شفة علوية أرق نسبياً',
#             correction_style='موازنة النسبة',
#             technique='رسم الخط أعلى الحد الطبيعي للشفة العلوية',
#             reason='لتحقيق التماثل بين الشفتين'))

#     @Rule(LipAnalysis(volume='Medium', balance='Lower Fuller'))
#     def medium_lower_fuller(self):
#         self.declare(LipShapeCategory(
#             category='Lower Thin', name_ar='شفة سفلى أرق نسبياً',
#             correction_style='موازنة النسبة',
#             technique='رسم الخط أسفل الحد الطبيعي للشفة السفلى',
#             reason='لضمان التماثل بين الشفتين'))

#     @Rule(LipAnalysis(volume='Full', width='Wide'))
#     def very_large_lips(self):
#         self.declare(LipShapeCategory(
#             category='Very Large', name_ar='شفاه كبيرة جداً',
#             correction_style='تصغير بصري',
#             technique='رسم الخط داخل الحد الطبيعي للشفة، مع استخدام ألوان متوسطة إلى داكنة',
#             reason='لتقليل المساحة الظاهرة للشفاه'))

#     @Rule(LipAnalysis(volume='Full', balance='Balanced'))
#     def full_balanced_lips(self):
#         self.declare(LipShapeCategory(
#             category='Full & Balanced', name_ar='شفاه ممتلئة ومتوازنة',
#             correction_style='الحفاظ على الشكل الطبيعي',
#             technique='رسم لاينر الشفاه على الحد الطبيعي للشفة',
#             reason='الشفاه ممتلئة أصلاً وتُعد المعيار الجمالي المثالي'))

#     @Rule(LipAnalysis(volume='Medium', balance='Balanced'))
#     def medium_balanced_lips(self):
#         self.declare(LipShapeCategory(
#             category='Full & Balanced', name_ar='شفاه متوسطة ومتوازنة',
#             correction_style='الحفاظ على الشكل الطبيعي',
#             technique='رسم لاينر الشفاه على الحد الطبيعي للشفة',
#             reason='متوازنة وتحتاج فقط للتحديد'))

#     # ──── Rule 2: لون الروج حسب الأندرتون ────

#     @Rule(SkinProfile(undertone='Warm'))
#     def warm_lip_color(self):
#         self.declare(LipColorMatch(undertone='Warm', palette='أساس ذهبي/خوخي',
#                                     colors='درجات مرجانية وخوخية'))

#     @Rule(SkinProfile(undertone='Cool'))
#     def cool_lip_color(self):
#         self.declare(LipColorMatch(undertone='Cool', palette='أساس بارد',
#                                     colors='درجات التوت والوردي المائل للأزرق (ماوف/راسبيري)'))

#     # ──── Rule 3: المنتج والملمس حسب المناسبة ────

#     @Rule(OccasionContext(occasion='work'))
#     def work_lip_style(self):
#         self.declare(LipOccasionStyle(occasion='work', style='تورّد طبيعي',
#                                        product='صبغة شفاه أو أحمر شفاه مطفأ فاتح جداً',
#                                        texture='مطفأ — يمنح مظهراً صحياً ونابضاً بالحياة'))

#     @Rule(OccasionContext(occasion='university'))
#     def university_lip_style(self):
#         self.declare(LipOccasionStyle(occasion='university', style='تورّد طبيعي',
#                                        product='صبغة شفاه أو أحمر شفاه مطفأ فاتح جداً',
#                                        texture='مطفأ — يمنح مظهراً صحياً ونابضاً بالحياة'))

#     @Rule(OccasionContext(occasion='evening'))
#     def evening_lip_style(self):
#         self.declare(LipOccasionStyle(occasion='evening', style='إطلالة متوازنة',
#                                        product='أحمر شفاه بصبغة قوية، متوازن مع مكياج العين',
#                                        texture='ساتان أو كريمي — يمنح عمقاً ثلاثي الأبعاد'))

#     @Rule(OccasionContext(occasion='party'))
#     def party_lip_style(self):
#         self.declare(LipOccasionStyle(occasion='party', style='إطلالة متوازنة',
#                                        product='أحمر شفاه بصبغة قوية، متوازن مع مكياج العين',
#                                        texture='ساتان أو كريمي — يمنح عمقاً ثلاثي الأبعاد'))

#     @Rule(OccasionContext(occasion='photo'))
#     def photo_lip_style(self):
#         self.declare(LipOccasionStyle(occasion='photo', style='تعريف حاد عالي الدقة',
#                                        product='أحمر شفاه مطفأ مع تحديد حاد جداً للحواف',
#                                        texture='مطفأ بالكامل — يمنع تشتت انعكاس الفلاش'))

#     @Rule(OccasionContext(occasion='wedding'))
#     def wedding_lip_style(self):
#         self.declare(LipOccasionStyle(occasion='wedding', style='شفاه فاخرة وممتلئة',
#                                        product='أحمر شفاه غني مع طبقة لمعان توضع عمودياً بمنتصف الشفة فقط',
#                                        texture='لامع (بالمنتصف فقط، فوق طبقة أساس غنية)'))

#     # ──── Rule 4: التوصية النهائية ────

#     @Rule(LipShapeCategory(category=MATCH.category),
#           LipColorMatch(colors=MATCH.colors),
#           LipOccasionStyle(occasion=MATCH.occasion))
#     def final_lip_recommendation(self, category, colors, occasion):
#         self.declare(LipRecommendation(shape_category=category, lip_colors=colors, occasion=occasion, complete=True))


# # ══════════════════════════════════════════════════════
# # ENGINE
# # ══════════════════════════════════════════════════════

# class LipMakeupEngine(LipRulesKB):
#     """محرك مكياج الشفاه"""

#     def __init__(self):
#         super().__init__()

#     def analyze_lips(self, lip_data):
#         self.reset()
#         self.declare(
#             LipAnalysis(
#                 volume=lip_data.get('volume', 'Medium'),
#                 balance=lip_data.get('balance', 'Balanced'),
#                 width=lip_data.get('width', 'Average'),
#                 symmetry=lip_data.get('symmetry', 'Symmetrical'),
#                 cupid_bow=lip_data.get('cupid_bow', 'Soft'),
#                 corners=lip_data.get('corners', 'Neutral')
#             ),
#             SkinProfile(undertone=lip_data.get('undertone', 'Warm'), depth=lip_data.get('depth', 'Medium')),
#             OccasionContext(occasion=lip_data.get('occasion', 'work'))
#         )
#         self.run()
#         return self._extract_results()

#     def _extract_results(self):
#         results = {'shape': None, 'color': None, 'occasion': None, 'recommendation': None}

#         for fact in self.facts.values():
#             if isinstance(fact, LipShapeCategory):
#                 results['shape'] = {
#                     'category': fact.get('category'),
#                     'name_ar': fact.get('name_ar'),
#                     'correction': fact.get('correction_style'),
#                     'technique': fact.get('technique'),
#                     'reason': fact.get('reason')
#                 }
#             elif isinstance(fact, LipColorMatch):
#                 results['color'] = {'undertone': fact.get('undertone'), 'palette': fact.get('palette'),
#                                      'colors': fact.get('colors')}
#             elif isinstance(fact, LipOccasionStyle):
#                 results['occasion'] = {'occasion': fact.get('occasion'), 'style': fact.get('style'),
#                                         'product': fact.get('product'), 'texture': fact.get('texture')}
#             elif isinstance(fact, LipRecommendation):
#                 results['recommendation'] = {'shape': fact.get('shape_category'), 'colors': fact.get('lip_colors'),
#                                               'occasion': fact.get('occasion'), 'complete': fact.get('complete')}

#         return results


# if __name__ == "__main__":
#     engine = LipMakeupEngine()
#     example = {'volume': 'Medium', 'balance': 'Lower Fuller', 'width': 'Average', 'undertone': 'Cool',
#                'depth': 'Medium', 'occasion': 'wedding'}
#     result = engine.analyze_lips(example)
#     print(json.dumps(result, indent=2, ensure_ascii=False, default=str))

# ✅ MUST BE FIRST: Python 3.10+ Compatibility Fix
import compat_fix

from experta import *
import json

# ══════════════════════════════════════════════════════
# HELPER FUNCTIONS (درجات أحمر الشفاه ومحدد الشفاه)
# ══════════════════════════════════════════════════════

def get_lip_shades_and_liners(undertone, depth):
    """
    إرجاع درجات أحمر الشفاه ومحددات الشفاه (Lip Liner) بناءً على undertone و depth
    """
    if undertone == 'Warm':
        if depth == 'Fair':
            return {
                'lipstick_shades': [
                    {'name': 'خوخي ناعم (Soft Peach)', 'hex': '#FFB7B2', 'rgb': (255, 183, 178)},
                    {'name': 'مرجاني مشرق (Bright Coral)', 'hex': '#FF7F50', 'rgb': (255, 127, 80)},
                    {'name': 'مشمشي دافئ (Warm Apricot)', 'hex': '#FBCEB1', 'rgb': (251, 206, 177)}
                ],
                'lip_liners': [
                    {'name': 'محدد خوخي بني (Peach Nude Liner)', 'hex': '#D18B70', 'rgb': (209, 139, 112)},
                    {'name': 'محدد مرجاني غامق (Deep Coral Liner)', 'hex': '#C85A32', 'rgb': (200, 90, 50)}
                ]
            }
        elif depth == 'Medium':
            return {
                'lipstick_shades': [
                    {'name': 'مرجاني دافئ (Warm Coral)', 'hex': '#E07A5F', 'rgb': (224, 122, 95)},
                    {'name': 'خوخي بني (Warm Nude Peach)', 'hex': '#C87D55', 'rgb': (200, 125, 85)},
                    {'name': 'برتقالي تراكوتا (Terracotta)', 'hex': '#D2691E', 'rgb': (210, 105, 30)}
                ],
                'lip_liners': [
                    {'name': 'محدد تراكوتا متوسط (Terracotta Liner)', 'hex': '#A04000', 'rgb': (160, 64, 0)},
                    {'name': 'محدد بني بني دافئ (Warm Brown Liner)', 'hex': '#8B4513', 'rgb': (139, 69, 19)}
                ]
            }
        else:  # Dark
            return {
                'lipstick_shades': [
                    {'name': 'قرفة دافئة (Spiced Cinnamon)', 'hex': '#B85042', 'rgb': (184, 80, 66)},
                    {'name': 'برتقالي محروق غني (Burnt Orange)', 'hex': '#CC5500', 'rgb': (204, 85, 0)},
                    {'name': 'بني نبيذي دافئ (Warm Bronze Brown)', 'hex': '#6E2C00', 'rgb': (110, 44, 0)}
                ],
                'lip_liners': [
                    {'name': 'محدد شوكولاتة غامق (Deep Chocolate Liner)', 'hex': '#4A235A', 'rgb': (74, 35, 90)},
                    {'name': 'محدد بني محروق (Burnt Brown Liner)', 'hex': '#4E1F0D', 'rgb': (78, 31, 13)}
                ]
            }
    else:  # Cool Undertone
        if depth == 'Fair':
            return {
                'lipstick_shades': [
                    {'name': 'وردي بارد ناعم (Cool Soft Pink)', 'hex': '#F8C8DC', 'rgb': (248, 200, 220)},
                    {'name': 'موف فاتح (Light Mauve)', 'hex': '#E0B0FF', 'rgb': (224, 176, 255)},
                    {'name': 'توتي خفيف (Berry Tint)', 'hex': '#C71585', 'rgb': (199, 21, 133)}
                ],
                'lip_liners': [
                    {'name': 'محدد وردي ترابي (Dusty Rose Liner)', 'hex': '#C87D85', 'rgb': (200, 125, 133)},
                    {'name': 'محدد موف متوسط (Medium Mauve Liner)', 'hex': '#9B51E0', 'rgb': (155, 81, 224)}
                ]
            }
        elif depth == 'Medium':
            return {
                'lipstick_shades': [
                    {'name': 'وردي ترابي (Dusty Rose)', 'hex': '#C87D85', 'rgb': (200, 125, 133)},
                    {'name': 'موف متوسط (Medium Mauve)', 'hex': '#A569BD', 'rgb': (165, 105, 189)},
                    {'name': 'توتي رايب (Plum Berry)', 'hex': '#8E2A59', 'rgb': (142, 42, 89)}
                ],
                'lip_liners': [
                    {'name': 'محدد توتي غامق (Deep Berry Liner)', 'hex': '#6C3483', 'rgb': (108, 52, 131)},
                    {'name': 'محدد موف غامق (Dark Mauve Liner)', 'hex': '#7D3C98', 'rgb': (125, 60, 152)}
                ]
            }
        else:  # Dark
            return {
                'lipstick_shades': [
                    {'name': 'وردي توتي غامق (Deep Berry Rose)', 'hex': '#800020', 'rgb': (128, 0, 32)},
                    {'name': 'عنابي فاخر (Deep Burgundy)', 'hex': '#581845', 'rgb': (88, 24, 69)},
                    {'name': 'بنفسجي غامق (Plum Dark)', 'hex': '#4A235A', 'rgb': (74, 35, 90)}
                ],
                'lip_liners': [
                    {'name': 'محدد عنابي أسود (Black Burgundy Liner)', 'hex': '#34111E', 'rgb': (52, 17, 30)},
                    {'name': 'محدد توتي داكن جداً (Dark Plum Liner)', 'hex': '#2C001E', 'rgb': (44, 0, 30)}
                ]
            }


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
    opacity = Field(int)  # 👈 إضافة نسبة الشفافية كرقم مئوي


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

    # ──── Rule 3: المنتج، الملمس، والشفافية حسب المناسبة ────

    @Rule(OccasionContext(occasion='work'))
    def work_lip_style(self):
        self.declare(LipOccasionStyle(occasion='work', style='تورّد طبيعي',
                                       product='صبغة شفاه أو أحمر شفاه مطفأ فاتح جداً',
                                       texture='مطفأ — يمنح مظهراً صحياً ونابضاً بالحياة',
                                       opacity=40))  # 👈 شفافية خفيفة (40%)

    @Rule(OccasionContext(occasion='university'))
    def university_lip_style(self):
        self.declare(LipOccasionStyle(occasion='university', style='تورّد طبيعي',
                                       product='صبغة شفاه أو أحمر شفاه مطفأ فاتح جداً',
                                       texture='مطفأ — يمنح مظهراً صحياً ونابضاً بالحياة',
                                       opacity=50))  # 👈 شفافية (50%)

    @Rule(OccasionContext(occasion='evening'))
    def evening_lip_style(self):
        self.declare(LipOccasionStyle(occasion='evening', style='إطلالة متوازنة',
                                       product='أحمر شفاه بصبغة قوية، متوازن مع مكياج العين',
                                       texture='ساتان أو كريمي — يمنح عمقاً ثلاثي الأبعاد',
                                       opacity=90))  # 👈 صبغة عالية (90%)

    @Rule(OccasionContext(occasion='party'))
    def party_lip_style(self):
        self.declare(LipOccasionStyle(occasion='party', style='إطلالة متوازنة',
                                       product='أحمر شفاه بصبغة قوية، متوازن مع مكياج العين',
                                       texture='ساتان أو كريمي — يمنح عمقاً ثلاثي الأبعاد',
                                       opacity=90))

    @Rule(OccasionContext(occasion='photo'))
    def photo_lip_style(self):
        self.declare(LipOccasionStyle(occasion='photo', style='تعريف حاد عالي الدقة',
                                       product='أحمر شفاه مطفأ مع تحديد حاد جداً للحواف',
                                       texture='مطفأ بالكامل — يمنع تشتت انعكاس الفلاش',
                                       opacity=100))  # 👈 صبغة تامة (100%)

    @Rule(OccasionContext(occasion='wedding'))
    def wedding_lip_style(self):
        self.declare(LipOccasionStyle(occasion='wedding', style='شفاه فاخرة وممتلئة',
                                       product='أحمر شفاه غني مع طبقة لمعان توضع عمودياً بمنتصف الشفة فقط',
                                       texture='لامع (بالمنتصف فقط، فوق طبقة أساس غنية)',
                                       opacity=100))

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
        self.lip_data = {}

    def analyze_lips(self, lip_data):
        self.lip_data = lip_data
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

        # جلب درجات الشفاه والمحددات
        undertone = self.lip_data.get('undertone', 'Warm')
        depth = self.lip_data.get('depth', 'Medium')
        color_details = get_lip_shades_and_liners(undertone, depth)

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
                results['color'] = {
                    'undertone': fact.get('undertone'),
                    'palette': fact.get('palette'),
                    'colors_summary': fact.get('colors'),
                    'lipstick_shades': color_details['lipstick_shades'],
                    'lip_liners': color_details['lip_liners']
                }
            elif isinstance(fact, LipOccasionStyle):
                results['occasion'] = {
                    'occasion': fact.get('occasion'),
                    'style': fact.get('style'),
                    'product': fact.get('product'),
                    'texture': fact.get('texture'),
                    'opacity': fact.get('opacity')  # 👈 نسبة الشفافية (التركيز)
                }
            elif isinstance(fact, LipRecommendation):
                results['recommendation'] = {
                    'shape': fact.get('shape_category'),
                    'colors': fact.get('lip_colors'),
                    'occasion': fact.get('occasion'),
                    'complete': fact.get('complete')
                }

        return results


if __name__ == "__main__":
    engine = LipMakeupEngine()
    example = {
        'volume': 'Medium', 
        'balance': 'Lower Fuller', 
        'width': 'Average', 
        'undertone': 'Cool',
        'depth': 'Fair', 
        'occasion': 'wedding'
    }
    result = engine.analyze_lips(example)
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))