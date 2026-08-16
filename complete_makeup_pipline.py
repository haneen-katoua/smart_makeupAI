# # -*- coding: utf-8 -*-
# """
# complete_makeup_pipeline.py — End-to-End Makeup Analysis Pipeline
# ==================================================================
# المدخلات (حالياً): صورة الوجه + المناسبة
# المخرجات: تقرير موحّد لكل ملمح (الشكل/النوع + المكياج المناسب + السبب)
#           + نسخة JSON جاهزة للاستخدام في API/واجهات.

# ملاحظة: تحليل لون اللبس (outfit_color_analysis.py) غير مُستخدم حالياً بالنظام،
#         وسيُضاف لاحقاً كخطوة مستقلة دون الحاجة لتعديل هذا الملف من جديد
#         (يكفي إعادة تفعيل الاستدعاء في process() عند جهوزه).

# Flow:
#   صورة الوجه → MediaPipe (شكل الوجه/العيون/الحواجب/الشفاه/الأنف) الحقيقي
#   صورة الوجه → تحليل لون البشرة (Undertone / Depth / Skin type)
#   → Experta Expert System → توصيات كاملة → تقرير موحّد
# """

# # ✅ MUST BE FIRST: Python 3.10+ Compatibility Fix
# import compat_fix

# import argparse
# import json
# from pathlib import Path
# from typing import Dict, Optional

# from all_face_analysis import analyze_face_from_image_dict
# from skin_analysis import analyze_skin_from_image_dict as analyze_skin
# from full_makeup_expert_system import CompleteMakeupExpertSystem


# # ══════════════════════════════════════════════════════════════════
# # تطبيع مدخلات المستخدم
# # ══════════════════════════════════════════════════════════════════

# OCCASION_MAP = {
#     'work': 'work', 'عمل': 'work', 'دوام': 'work',
#     'university': 'university', 'جامعة': 'university', 'دراسة': 'university',
#     'evening': 'evening', 'سهرة': 'evening', 'مساء': 'evening',
#     'party': 'party', 'حفلة': 'party', 'حفل': 'party',
#     'wedding': 'wedding', 'زفاف': 'wedding', 'عرس': 'wedding',
#     'photo': 'photo', 'تصوير': 'photo', 'فوتوشوت': 'photo',
# }


# def normalize_occasion(raw_occasion: str) -> str:
#     key = (raw_occasion or '').strip().lower()
#     return OCCASION_MAP.get(key, 'evening')


# # ── قواميس تعريب للعرض فقط (لا تُستخدم في منطق المطابقة) ──

# OCCASION_AR = {
#     'work': 'عمل', 'university': 'جامعة', 'evening': 'سهرة',
#     'party': 'حفلة', 'wedding': 'زفاف', 'photo': 'تصوير',
# }

# UNDERTONE_AR = {'warm': 'دافئ', 'cool': 'بارد', 'neutral': 'محايد'}
# DEPTH_AR = {'fair': 'فاتحة', 'medium': 'متوسطة', 'dark': 'داكنة'}
# SKIN_TYPE_AR = {'oily': 'دهنية', 'dry': 'جافة', 'combination': 'مختلطة',
#                 'sensitive': 'حساسة', 'normal': 'عادية'}


# def _ar(mapping: Dict, value: Optional[str]) -> str:
#     if not value:
#         return 'غير محدد'
#     return mapping.get(str(value).strip().lower(), value)


# def _adapt_eyes(eyes_raw: Dict) -> Dict:
#     """تحويل صيغة نتائج all_face_analysis.analyze_eyes لصيغة يفهمها full_makeup_expert_system"""
#     def conv(eye):
#         geo = eye.get('geo_shape', 'Almond')
#         etype = eye.get('eye_type', 'Normal')
#         return {
#             'geo_shape': geo,
#             'eye_type': etype,
#             'combined': f"{geo} {etype}".strip(),
#             'size': eye.get('size', 'Normal'),
#             'corner': eye.get('corner_direction', 'Neutral'),
#         }

#     return {
#         'left': conv(eyes_raw.get('left_eye', {}) or {}),
#         'right': conv(eyes_raw.get('right_eye', {}) or {}),
#         'inter_eye_ratio': eyes_raw.get('inter_eye_ratio', 0.35)
#     }


# def _derive_fullness(face_shape_data: Dict) -> str:
#     """تقدير امتلاء الوجه من نسبة الفك إلى عظمة الخد (تقريبي)"""
#     ratio = (face_shape_data or {}).get('ratios', {}).get('jaw_to_cheekbone_ratio', 0.9)
#     return 'Full' if ratio >= 0.9 else 'Thin'


# # ══════════════════════════════════════════════════════════════════
# # PIPELINE
# # ══════════════════════════════════════════════════════════════════

# class CompleteMakeupPipeline:
#     """Pipeline شامل: صورة الوجه + المناسبة → توصيات مكياج كاملة"""

#     def __init__(self):
#         self.expert_system = CompleteMakeupExpertSystem()
#         self.results = {}

#     def process(self, face_image_path: str, occasion_raw: str,
#                 eye_strategy: str = 'Monochromatic',
#                 output_json: Optional[str] = None) -> Optional[Dict]:

#         occasion = normalize_occasion(occasion_raw)

#         print("\n" + "=" * 80)
#         print("  بدء تحليل الصورة وتوليد توصيات المكياج")
#         print("=" * 80)

#         # ── تحليل الوجه (حقيقي عبر MediaPipe) ──
#         print("\n[1/3] تحليل الوجه (MediaPipe)...")
#         face_analysis = self._analyze_face(face_image_path)
#         if face_analysis is None:
#             return None
#         self.results['face_analysis'] = face_analysis
#         print("  ✓ تم تحليل شكل الوجه والعينين والحواجب والشفاه والأنف")

#         # ── تحليل البشرة ──
#         print("\n[2/3] تحليل لون البشرة...")
#         skin_analysis = self._analyze_skin(face_image_path)
#         self.results['skin_analysis'] = skin_analysis
#         print(f"  ✓ العمق: {_ar(DEPTH_AR, skin_analysis.get('skin_depth'))} | الأندرتون: {_ar(UNDERTONE_AR, skin_analysis.get('undertone'))}")

#         # ── النظام الخبير (Experta) ──
#         print("\n[3/3] تشغيل النظام الخبير وتوليد التوصيات...")
#         expert_input = self._prepare_expert_input(face_analysis, skin_analysis, occasion, eye_strategy)
#         expert_output = self.expert_system.analyze_complete_face(expert_input)
#         self.results['expert_output'] = expert_output
#         self.results['occasion'] = occasion

#         print("\n✓ اكتمل التحليل\n")

#         if output_json:
#             self._save_json(output_json)

#         return self.results

#     # ── تحليل الوجه الحقيقي ──
#     def _analyze_face(self, image_path: str) -> Optional[Dict]:
#         if not Path(image_path).exists():
#             print(f"  ✗ خطأ: الصورة غير موجودة: {image_path}")
#             return None

#         result = analyze_face_from_image_dict(image_path)
#         if not result.get('success') or not result.get('face_detected'):
#             print(f"  ✗ خطأ: لم يتم اكتشاف وجه في الصورة ({result.get('error')})")
#             return None

#         return result

#     def _analyze_skin(self, image_path: str) -> Dict:
#         result = analyze_skin(image_path)
#         if not result or not result.get('success'):
#             print(f"  ⚠ تعذّر تحليل البشرة، تم استخدام قيم افتراضية ({result.get('error') if result else 'unknown'})")
#             return {'skin_depth': 'Medium', 'undertone': 'Warm', 'skin_type': 'Normal'}
#         return result

#     def _prepare_expert_input(self, face_analysis: Dict, skin_analysis: Dict,
#                                occasion: str, eye_strategy: str) -> Dict:
#         eyes_adapted = _adapt_eyes(face_analysis.get('eyes', {}) or {})
#         fullness = _derive_fullness(face_analysis.get('face_shape', {}))

#         return {
#             'eyes': eyes_adapted,
#             'brows': face_analysis.get('brows', {}) or {},
#             'lips': face_analysis.get('lips', {}) or {},
#             'nose': face_analysis.get('nose', {}) or {},
#             'face_shape': face_analysis.get('face_shape', {}) or {},
#             'skin': {
#                 'undertone': skin_analysis.get('undertone', 'Warm'),
#                 'depth': skin_analysis.get('skin_depth', 'Medium'),
#                 'skin_type': skin_analysis.get('skin_type', 'Normal'),
#             },
#             'context': {
#                 'occasion': occasion,
#                 'face_fullness': fullness,
#                 'eye_strategy': eye_strategy,
#             }
#         }

#     def _save_json(self, output_path: str):
#         try:
#             with open(output_path, 'w', encoding='utf-8') as f:
#                 json.dump(self.results, f, indent=2, ensure_ascii=False, default=str)
#             print(f"  ✓ تم حفظ النتائج في: {output_path}")
#         except Exception as e:
#             print(f"  ✗ خطأ في حفظ JSON: {e}")

#     # ══════════════════════════════════════════════════════════════
#     # التقرير الموحّد: لكل ملمح → الشكل + المكياج المناسب + السبب
#     # ══════════════════════════════════════════════════════════════

#     def build_unified_report(self) -> list:
#         """يبني قائمة عناصر: كل عنصر يمثل ملمحاً واحداً بصيغة موحّدة وجاهزة لأي API"""
#         eo = self.results.get('expert_output', {}) or {}
#         report = []

#         # 1) شكل الوجه (كونتور/بلاشر/هاياليت)
#         face = eo.get('face') or {}
#         if face.get('shape'):
#             makeup_parts = []
#             if face.get('sculpt'):
#                 makeup_parts.append(f"كونتور: {face['sculpt']['placement']}")
#             if face.get('blush'):
#                 makeup_parts.append(f"بلاشر: {face['blush']['placement']} (اللون: {(face.get('color') or {}).get('base_color', 'غير محدد')})")
#             if face.get('highlight'):
#                 makeup_parts.append(f"هاياليت: {face['highlight']['placement']}")
#             report.append({
#                 'feature': 'شكل الوجه',
#                 'shape': face['shape'].get('name_ar'),
#                 'makeup': ' | '.join(makeup_parts),
#                 'reason': face['shape'].get('goal'),
#             })

#         # 2) الحواجب
#         brows = eo.get('brows') or {}
#         if brows.get('correction') or brows.get('style'):
#             correction = brows.get('correction') or {}
#             style = brows.get('style') or {}
#             color = brows.get('color') or {}
#             report.append({
#                 'feature': 'الحواجب',
#                 'shape': f"قوس: {correction.get('arch_type', 'غير محدد')} | ذيل: {correction.get('tail_direction', 'غير محدد')}",
#                 'makeup': f"{style.get('style', 'غير محدد')} — {style.get('technique', 'غير محدد')} ({style.get('product', 'غير محدد')}) | اللون: {color.get('tone', 'غير محدد')}",
#                 'reason': correction.get('visual_purpose', 'غير محدد'),
#             })

#         # 3) العينان
#         eyes = eo.get('eyes') or {}
#         for side, label in (('left', 'العين اليسرى'), ('right', 'العين اليمنى')):
#             eye = (eyes.get(side) or {})
#             rec = eye.get('recommendation') or {}
#             category = eye.get('category') or {}
#             plan = eye.get('plan') or {}
#             spacing = eye.get('spacing') or {}

#             # نعتمد التوصية المجمّعة إن وُجدت، وإلا نبني من الحقائق الفردية
#             shape_ar = rec.get('category_ar') or category.get('name_ar')
#             goal = rec.get('goal') or category.get('goal')
#             style = plan.get('style') or rec.get('style')

#             if shape_ar or style:
#                 spacing_text = spacing.get('rule') or 'المسافة بين العينين متوازنة، ولذلك لا حاجة لأي تصحيح لوني في الزاوية الداخلية'
#                 report.append({
#                     'feature': label,
#                     'shape': shape_ar or 'غير محدد',
#                     'makeup': f"{style or 'غير محدد'} | القوام: {plan.get('texture', 'غير محدد')} | الرموش: {plan.get('lashes', 'غير محدد')} | الآيلاينر: {plan.get('eyeliner', 'غير محدد')} | تصحيح المسافة: {spacing_text}",
#                     'reason': goal or 'غير محدد',
#                 })

#         # 4) الشفاه
#         lips = eo.get('lips') or {}
#         if lips.get('shape'):
#             shape = lips['shape']
#             color = lips.get('color') or {}
#             occ = lips.get('occasion') or {}
#             report.append({
#                 'feature': 'الشفاه',
#                 'shape': shape.get('name_ar'),
#                 'makeup': f"{shape.get('correction', 'غير محدد')} — {shape.get('technique', 'غير محدد')} | اللون: {color.get('colors', 'غير محدد')} | المنتج: {occ.get('product', 'غير محدد')} ({occ.get('texture', 'غير محدد')})",
#                 'reason': shape.get('reason'),
#             })

#         # 5) الأنف
#         nose = eo.get('nose') or {}
#         if nose.get('shape'):
#             shape = nose['shape']
#             contour = nose.get('contour') or {}
#             highlight = nose.get('highlight') or {}
#             nmap = nose.get('map') or {}
#             report.append({
#                 'feature': 'الأنف',
#                 'shape': shape.get('name_ar'),
#                 'makeup': f"{shape.get('technique', 'غير محدد')} | منتج الكونتور: {contour.get('product', 'غير محدد')} | الهاياليت: {highlight.get('tone', 'غير محدد')} ({nmap.get('highlight', 'غير محدد')})",
#                 'reason': shape.get('reason'),
#             })

#         # 6) الأساس والكونسيلر
#         foundation = eo.get('foundation') or {}
#         if foundation.get('shade') or foundation.get('formula'):
#             shade = foundation.get('shade') or {}
#             formula = foundation.get('formula') or {}
#             concealer = foundation.get('concealer') or {}
#             primer = foundation.get('primer') or {}
#             setting = foundation.get('setting') or {}
#             report.append({
#                 'feature': 'الأساس والكونسيلر',
#                 'shape': f"{shade.get('descriptor', 'غير محدد')} ({shade.get('range', 'غير محدد')})",
#                 'makeup': f"الأساس: {formula.get('primary', 'غير محدد')} ({formula.get('texture', 'غير محدد')}) | الكونسيلر: {concealer.get('descriptor', 'غير محدد')} | البرايمر: {primer.get('type', 'غير محدد')} | التثبيت: {setting.get('method', 'غير محدد')}",
#                 'reason': formula.get('reason', 'غير محدد'),
#             })

#         return report

#     def print_report(self):
#         """طباعة التقرير الموحّد على الكونسول بشكل واضح ومنظّم"""
#         print("\n" + "=" * 80)
#         print("  التقرير النهائي — لكل ملمح: الشكل / المكياج المناسب / السبب")
#         print("=" * 80)

#         skin = self.results.get('skin_analysis', {})
#         print(f"\nالبشرة: العمق = {_ar(DEPTH_AR, skin.get('skin_depth'))} | الأندرتون = {_ar(UNDERTONE_AR, skin.get('undertone'))} | النوع = {_ar(SKIN_TYPE_AR, skin.get('skin_type'))}")
#         print(f"المناسبة: {OCCASION_AR.get(self.results.get('occasion'), self.results.get('occasion', 'غير محدد'))}")

#         report = self.build_unified_report()
#         for item in report:
#             print("\n" + "-" * 80)
#             print(f"📍 الملمح: {item['feature']}")
#             print(f"   الشكل/النوع : {item['shape']}")
#             print(f"   المكياج     : {item['makeup']}")
#             print(f"   السبب       : {item['reason']}")

#         print("\n" + "=" * 80 + "\n")
#         return report


# # ══════════════════════════════════════════════════════════════════
# # CLI
# # ══════════════════════════════════════════════════════════════════

# def analyze_image(face_image_path: str, occasion: str = 'evening',
#                    eye_strategy: str = 'Monochromatic',
#                    output_json: Optional[str] = None, print_report: bool = True) -> Optional[Dict]:
#     """
#     دالة مباشرة للاستخدام كمكتبة (مثلاً من داخل API):

#         from complete_makeup_pipline import analyze_image
#         data = analyze_image('face.jpg', occasion='wedding')
#     """
#     pipeline = CompleteMakeupPipeline()
#     result = pipeline.process(face_image_path, occasion, eye_strategy, output_json)
#     report = None
#     if result and print_report:
#         report = pipeline.print_report()
#     if result is not None:
#         result['unified_report'] = report if report is not None else pipeline.build_unified_report()
#     return result


# def main():
#     parser = argparse.ArgumentParser(description='تحليل صورة الوجه وتوليد توصيات مكياج كاملة')
#     parser.add_argument('--face', required=True, help='مسار صورة الوجه')
#     parser.add_argument('--occasion', required=False, default='evening',
#                          help='المناسبة: work / university / evening / party / wedding / photo (أو بالعربي)')
#     parser.add_argument('--eye-strategy', required=False, default='Monochromatic',
#                          help='استراتيجية مكياج العين: Monochromatic / Contrast / Triadic / Earthy')
#     parser.add_argument('--output', required=False, default='makeup_analysis.json', help='مسار حفظ JSON')
#     args = parser.parse_args()

#     analyze_image(
#         face_image_path=args.face,
#         occasion=args.occasion,
#         eye_strategy=args.eye_strategy,
#         output_json=args.output,
#         print_report=True
#     )


# if __name__ == "__main__":
#     main()
# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
# ✅ MUST BE FIRST: Python 3.10+ Compatibility Fix


# import compat_fix

# import argparse
# import json
# import os
# from pathlib import Path
# from typing import Dict, Optional

# from all_face_analysis import analyze_face_from_image_dict
# from skin_analysis import analyze_skin_from_image_dict as analyze_skin
# from full_makeup_expert_system import CompleteMakeupExpertSystem


# # ══════════════════════════════════════════════════════════════════
# # تطبيع مدخلات المستخدم
# # ══════════════════════════════════════════════════════════════════

# OCCASION_MAP = {
#     'work': 'work', 'عمل': 'work', 'دوام': 'work',
#     'university': 'university', 'جامعة': 'university', 'دراسة': 'university',
#     'evening': 'evening', 'سهرة': 'evening', 'مساء': 'evening',
#     'party': 'party', 'حفلة': 'party', 'حفل': 'party',
#     'wedding': 'wedding', 'زفاف': 'wedding', 'عرس': 'wedding',
#     'photo': 'photo', 'تصوير': 'photo', 'فوتوشوت': 'photo',
# }


# def normalize_occasion(raw_occasion: str) -> str:
#     key = (raw_occasion or '').strip().lower()
#     return OCCASION_MAP.get(key, 'evening')


# # ── قواميس تعريب للعرض فقط (لا تُستخدم في منطق المطابقة) ──

# OCCASION_AR = {
#     'work': 'عمل', 'university': 'جامعة', 'evening': 'سهرة',
#     'party': 'حفلة', 'wedding': 'زفاف', 'photo': 'تصوير',
# }

# UNDERTONE_AR = {'warm': 'دافئ', 'cool': 'بارد', 'neutral': 'محايد'}
# DEPTH_AR = {'fair': 'فاتحة', 'medium': 'متوسطة', 'dark': 'داكنة'}
# SKIN_TYPE_AR = {'oily': 'دهنية', 'dry': 'جافة', 'combination': 'مختلطة',
#                 'sensitive': 'حساسة', 'normal': 'عادية'}


# def _ar(mapping: Dict, value: Optional[str]) -> str:
#     if not value:
#         return 'غير محدد'
#     return mapping.get(str(value).strip().lower(), value)


# def _adapt_eyes(eyes_raw: Dict) -> Dict:
#     """تحويل صيغة نتائج all_face_analysis.analyze_eyes لصيغة يفهمها full_makeup_expert_system"""
#     def conv(eye):
#         geo = eye.get('geo_shape', 'Almond')
#         etype = eye.get('eye_type', 'Normal')
#         return {
#             'geo_shape': geo,
#             'eye_type': etype,
#             'combined': f"{geo} {etype}".strip(),
#             'size': eye.get('size', 'Normal'),
#             'corner': eye.get('corner_direction', 'Neutral'),
#         }

#     return {
#         'left': conv(eyes_raw.get('left_eye', {}) or {}),
#         'right': conv(eyes_raw.get('right_eye', {}) or {}),
#         'inter_eye_ratio': eyes_raw.get('inter_eye_ratio', 0.35)
#     }


# def _derive_fullness(face_shape_data: Dict) -> str:
#     """تقدير امتلاء الوجه من نسبة الفك إلى عظمة الخد (تقريبي)"""
#     ratio = (face_shape_data or {}).get('ratios', {}).get('jaw_to_cheekbone_ratio', 0.9)
#     return 'Full' if ratio >= 0.9 else 'Thin'


# def _to_clean_abs_path(path_str: str) -> str:
#     """تحويل المسار إلى مسار مطلق ونظيف مخصص لبيئة Windows لتفادي خطأ MediaPipe errno=22"""
#     p = Path(path_str).resolve()
#     return str(p)


# # ══════════════════════════════════════════════════════════════════
# # PIPELINE
# # ══════════════════════════════════════════════════════════════════

# class CompleteMakeupPipeline:
#     """Pipeline شامل: صورة الوجه + المناسبة ← توصيات مكياج كاملة"""

#     def __init__(self):
#         self.expert_system = CompleteMakeupExpertSystem()
#         self.results = {}

#     def process(self, face_image_path: str, occasion_raw: str,
#                 eye_strategy: str = 'Monochromatic',
#                 output_json: Optional[str] = None) -> Optional[Dict]:

#         occasion = normalize_occasion(occasion_raw)

#         print("\n" + "=" * 80)
#         print("  بدء تحليل الصورة وتوليد توصيات المكياج")
#         print("=" * 80)

#         # تحويل المسار إلى مسار Windows مطلق ونظيف
#         clean_image_path = _to_clean_abs_path(face_image_path)

#         # ── تحليل الوجه (حقيقي عبر MediaPipe) ──
#         print("\n[1/3] تحليل الوجه (MediaPipe)...")
#         face_analysis = self._analyze_face(clean_image_path)
#         if face_analysis is None:
#             return None
#         self.results['face_analysis'] = face_analysis
#         print("  ✓ تم تحليل شكل الوجه والعينين والحواجب والشفاه والأنف")

#         # ── تحليل البشرة ──
#         print("\n[2/3] تحليل لون البشرة...")
#         skin_analysis = self._analyze_skin(clean_image_path)
#         self.results['skin_analysis'] = skin_analysis
#         print(f"  ✓ العمق: {_ar(DEPTH_AR, skin_analysis.get('skin_depth'))} | الأندرتون: {_ar(UNDERTONE_AR, skin_analysis.get('undertone'))}")

#         # ── النظام الخبير (Experta) ──
#         print("\n[3/3] تشغيل النظام الخبير وتوليد التوصيات...")
#         expert_input = self._prepare_expert_input(face_analysis, skin_analysis, occasion, eye_strategy)
#         expert_output = self.expert_system.analyze_complete_face(expert_input)
#         self.results['expert_output'] = expert_output
#         self.results['occasion'] = occasion

#         print("\n✓ اكتمل التحليل\n")

#         if output_json:
#             self._save_json(output_json)

#         return self.results

#     # ── تحليل الوجه الحقيقي ──
#     def _analyze_face(self, image_path: str) -> Optional[Dict]:
#         if not os.path.exists(image_path):
#             print(f"  ✗ خطأ: الصورة غير موجودة: {image_path}")
#             return None

#         result = analyze_face_from_image_dict(image_path)
#         if not result.get('success') or not result.get('face_detected'):
#             print(f"  ✗ خطأ: لم يتم اكتشاف وجه في الصورة ({result.get('error')})")
#             return None

#         return result

#     def _analyze_skin(self, image_path: str) -> Dict:
#         """تحليل البشرة بعد التأكد المطلق من وجود المسارات وتفادي القيم الافتراضية"""
#         try:
#             if not os.path.exists(image_path):
#                 raise FileNotFoundError(f"Image not found at {image_path}")
                
#             result = analyze_skin(image_path)
#         except Exception as e:
#             result = {'success': False, 'error': str(e)}

#         if not result or not result.get('success'):
#             err_msg = result.get('error') if result else 'unknown'
#             print(f"  ⚠ تعذّر تحليل البشرة، تم استخدام قيم افتراضية ({err_msg})")
#             return {
#                 'success': False,
#                 'skin_depth': 'Medium',
#                 'undertone': 'Warm',
#                 'skin_type': 'Normal',
#                 'color_hex': '#D8A7B1',
#                 'color_rgb': (216, 167, 177),
#                 'color_lab': {'L': 60.0, 'a': 15.0, 'b': 20.0}
#             }

#         return {
#             'success': True,
#             'skin_depth': result.get('skin_depth') or 'Medium',
#             'undertone': result.get('undertone') or 'Warm',
#             'skin_type': result.get('skin_type') or 'Normal',
#             'color_hex': result.get('color_hex') or '#D8A7B1',
#             'color_rgb': result.get('color_rgb') or (216, 167, 177),
#             'color_lab': result.get('color_lab') or {'L': 60.0, 'a': 15.0, 'b': 20.0},
#             'confidence': result.get('confidence', 0.8)
#         }

#     def _prepare_expert_input(self, face_analysis: Dict, skin_analysis: Dict,
#                                occasion: str, eye_strategy: str) -> Dict:
#         eyes_adapted = _adapt_eyes(face_analysis.get('eyes', {}) or {})
#         fullness = _derive_fullness(face_analysis.get('face_shape', {}))

#         return {
#             'eyes': eyes_adapted,
#             'brows': face_analysis.get('brows', {}) or {},
#             'lips': face_analysis.get('lips', {}) or {},
#             'nose': face_analysis.get('nose', {}) or {},
#             'face_shape': face_analysis.get('face_shape', {}) or {},
#             'skin': {
#                 'undertone': skin_analysis.get('undertone', 'Warm'),
#                 'depth': skin_analysis.get('skin_depth', 'Medium'),
#                 'skin_type': skin_analysis.get('skin_type', 'Normal'),
#                 'color_hex': skin_analysis.get('color_hex', '#D8A7B1'),
#                 'color_rgb': skin_analysis.get('color_rgb', (216, 167, 177)),
#             },
#             'context': {
#                 'occasion': occasion,
#                 'face_fullness': fullness,
#                 'eye_strategy': eye_strategy,
#             }
#         }

#     def _save_json(self, output_path: str):
#         try:
#             with open(output_path, 'w', encoding='utf-8') as f:
#                 json.dump(self.results, f, indent=2, ensure_ascii=False, default=str)
#             print(f"  ✓ تم حفظ النتائج في: {output_path}")
#         except Exception as e:
#             print(f"  ✗ خطأ في حفظ JSON: {e}")

#     # ══════════════════════════════════════════════════════════════
#     # التقرير الموحّد: لكل ملمح ← الشكل + المكياج المناسب + السبب
#     # ══════════════════════════════════════════════════════════════

#     def build_unified_report(self) -> list:
#         eo = self.results.get('expert_output', {}) or {}
#         report = []

#         # 1) شكل الوجه (كونتور/بلاشر/هاياليت)
#         face = eo.get('face') or {}
#         if face.get('shape'):
#             makeup_parts = []
            
#             if face.get('sculpt'):
#                 sculpt_info = face['sculpt']
#                 hex_code = sculpt_info.get('hex', '')
#                 opacity = sculpt_info.get('opacity', '')
#                 makeup_parts.append(f"كونتور: {sculpt_info['placement']} [الدرجة: {sculpt_info.get('shade_descriptor', '')} | HEX: {hex_code} | الشفافية: {opacity}%]")
            
#             if face.get('blush'):
#                 blush_info = face['blush']
#                 color_info = face.get('color', {})
#                 shades = color_info.get('shades_details', {}).get('primary', {})
#                 blush_hex = shades.get('hex', '')
#                 blush_name = shades.get('name', color_info.get('base_color', 'غير محدد'))
#                 makeup_parts.append(f"بلاشر: {blush_info['placement']} [اللون: {blush_name} | HEX: {blush_hex} | الشفافية: {blush_info.get('opacity', '')}%]")
            
#             if face.get('highlight'):
#                 hl_info = face['highlight']
#                 makeup_parts.append(f"هاياليت: {hl_info['placement']} [الدرجة: {hl_info.get('shade_descriptor', '')} | HEX: {hl_info.get('hex', '')} | الشفافية: {hl_info.get('opacity', '')}%]")
                
#             report.append({
#                 'feature': 'شكل الوجه',
#                 'shape': face['shape'].get('name_ar'),
#                 'makeup': ' | '.join(makeup_parts),
#                 'reason': face['shape'].get('goal'),
#             })

#         # 2) الحواجب
#         brows = eo.get('brows') or {}
#         if brows.get('correction') or brows.get('style'):
#             correction = brows.get('correction') or {}
#             style = brows.get('style') or {}
#             color = brows.get('color') or {}
#             report.append({
#                 'feature': 'الحواجب',
#                 'shape': f"قوس: {correction.get('arch_type', 'غير محدد')} | ذيل: {correction.get('tail_direction', 'غير محدد')}",
#                 'makeup': f"{style.get('style', 'غير محدد')} — {style.get('technique', 'غير محدد')} ({style.get('product', 'غير محدد')}) | اللون: {color.get('tone', 'غير محدد')}",
#                 'reason': correction.get('visual_purpose', 'غير محدد'),
#             })

#         # 3) العينان
#         eyes = eo.get('eyes') or {}
#         for side, label in (('left', 'العين اليسرى'), ('right', 'العين اليمنى')):
#             eye = (eyes.get(side) or {})
#             rec = eye.get('recommendation') or {}
#             category = eye.get('category') or {}
#             plan = eye.get('plan') or {}
#             spacing = eye.get('spacing') or {}

#             shape_ar = rec.get('category_ar') or category.get('name_ar')
#             goal = rec.get('goal') or category.get('goal')
#             style = plan.get('style') or rec.get('style')

#             if shape_ar or style:
#                 spacing_text = spacing.get('rule') or 'المسافة بين العينين متوازنة، ولذلك لا حاجة لأي تصحيح لوني في الزاوية الداخلية'
#                 report.append({
#                     'feature': label,
#                     'shape': shape_ar or 'غير محدد',
#                     'makeup': f"{style or 'غير محدد'} | القوام: {plan.get('texture', 'غير محدد')} | الرموش: {plan.get('lashes', 'غير محدد')} | الآيلاينر: {plan.get('eyeliner', 'غير محدد')} | تصحيح المسافة: {spacing_text}",
#                     'reason': goal or 'غير محدد',
#                 })

#         # 4) الشفاه
#         lips = eo.get('lips') or {}
#         if lips.get('shape'):
#             shape = lips['shape']
#             color = lips.get('color') or {}
#             occ = lips.get('occasion') or {}
            
#             lipsticks = [f"{s['name']} ({s['hex']})" for s in color.get('lipstick_shades', [])]
#             liners = [f"{l['name']} ({l['hex']})" for l in color.get('lip_liners', [])]
            
#             shades_text = ", ".join(lipsticks) if lipsticks else color.get('colors_summary', 'غير محدد')
#             liners_text = ", ".join(liners) if liners else 'غير محدد'
#             opacity_text = f" | الشفافية: {occ.get('opacity')}%" if occ.get('opacity') is not None else ""

#             report.append({
#                 'feature': 'الشفاه',
#                 'shape': shape.get('name_ar'),
#                 'makeup': f"{shape.get('correction', 'غير محدد')} — {shape.get('technique', 'غير محدد')} | "
#                           f"الدرجات المقترحة: [{shades_text}] | "
#                           f"المحددات: [{liners_text}] | "
#                           f"المنتج: {occ.get('product', 'غير محدد')} ({occ.get('texture', 'غير محدد')}){opacity_text}",
#                 'reason': shape.get('reason'),
#             })

#         # 5) الأنف
#         nose = eo.get('nose') or {}
#         if nose.get('shape'):
#             shape = nose['shape']
#             contour = nose.get('contour') or {}
#             highlight = nose.get('highlight') or {}
#             nmap = nose.get('map') or {}
#             report.append({
#                 'feature': 'الأنف',
#                 'shape': shape.get('name_ar'),
#                 'makeup': f"{shape.get('technique', 'غير محدد')} | منتج الكونتور: {contour.get('product', 'غير محدد')} | الهاياليت: {highlight.get('tone', 'غير محدد')} ({nmap.get('highlight', 'غير محدد')})",
#                 'reason': shape.get('reason'),
#             })

#         # 6) الأساس والكونسيلر
#         foundation = eo.get('foundation') or {}
#         if foundation.get('shade') or foundation.get('formula'):
#             shade = foundation.get('shade') or {}
#             formula = foundation.get('formula') or {}
#             concealer = foundation.get('concealer') or {}
#             primer = foundation.get('primer') or {}
#             setting = foundation.get('setting') or {}
            
#             f_hex = shade.get('hex', '')
#             f_color_str = f" [HEX: {f_hex}]" if f_hex else ""
            
#             c_hex = concealer.get('hex', '')
#             c_color_str = f" [HEX: {c_hex}]" if c_hex else ""

#             report.append({
#                 'feature': 'الأساس والكونسيلر',
#                 'shape': f"{shade.get('descriptor', 'غير محدد')} ({shade.get('range', 'غير محدد')}){f_color_str}",
#                 'makeup': f"الأساس: {formula.get('primary', 'غير محدد')} ({formula.get('texture', 'غير محدد')}) | "
#                           f"الكونسيلر: {concealer.get('descriptor', 'غير محدد')}{c_color_str} | "
#                           f"البرايمر: {primer.get('type', 'غير محدد')} | "
#                           f"التثبيت: {setting.get('method', 'غير محدد')}",
#                 'reason': formula.get('reason', 'غير محدد'),
#             })

#         return report

#     def print_report(self):
#         """طباعة التقرير الموحّد على الكونسول بشكل واضح ومنظّم"""
#         print("\n" + "=" * 80)
#         print("  التقرير النهائي — لكل ملمح: الشكل / المكياج المناسب / السبب")
#         print("=" * 80)

#         skin = self.results.get('skin_analysis', {})
#         print(f"\nالبشرة: العمق = {_ar(DEPTH_AR, skin.get('skin_depth'))} | الأندرتون = {_ar(UNDERTONE_AR, skin.get('undertone'))} | النوع = {_ar(SKIN_TYPE_AR, skin.get('skin_type'))}")
#         print(f"المناسبة: {OCCASION_AR.get(self.results.get('occasion'), self.results.get('occasion', 'غير محدد'))}")

#         report = self.build_unified_report()
#         for item in report:
#             print("\n" + "-" * 80)
#             print(f"📍 الملمح: {item['feature']}")
#             print(f"   الشكل/النوع : {item['shape']}")
#             print(f"   المكياج     : {item['makeup']}")
#             print(f"   السبب       : {item['reason']}")

#         print("\n" + "=" * 80 + "\n")
#         return report


# # ══════════════════════════════════════════════════════════════════
# # CLI
# # ══════════════════════════════════════════════════════════════════

# def analyze_image(face_image_path: str, occasion: str = 'evening',
#                   eye_strategy: str = 'Monochromatic',
#                   output_json: Optional[str] = None, print_report: bool = True) -> Optional[Dict]:
#     pipeline = CompleteMakeupPipeline()
#     result = pipeline.process(face_image_path, occasion, eye_strategy, output_json)
#     report = None
#     if result and print_report:
#         report = pipeline.print_report()
#     if result is not None:
#         result['unified_report'] = report if report is not None else pipeline.build_unified_report()
#     return result


# def main():
#     parser = argparse.ArgumentParser(description='تحليل صورة الوجه وتوليد توصيات مكياج كاملة')
#     parser.add_argument('--face', required=True, help='مسار صورة الوجه')
#     parser.add_argument('--occasion', required=False, default='evening',
#                         help='المناسبة: work / university / evening / party / wedding / photo (أو بالعربي)')
#     parser.add_argument('--eye-strategy', required=False, default='Monochromatic',
#                         help='استراتيجية مكياج العين: Monochromatic / Contrast / Triadic / Earthy')
#     parser.add_argument('--output', required=False, default='makeup_analysis.json', help='مسار حفظ JSON')
#     args = parser.parse_args()

#     analyze_image(
#         face_image_path=args.face,
#         occasion=args.occasion,
#         eye_strategy=args.eye_strategy,
#         output_json=args.output,
#         print_report=True
#     )


# if __name__ == "__main__":
#     main()


# # ✅ 1. إجبار Matplotlib على العمل بدون واجهة رسومية لمنع فتح أي نوافذ صور
# import matplotlib
# matplotlib.use('Agg')
# import matplotlib.pyplot as plt

# # ✅ 2. إصلاح توافقية Python 3.10+ مع Experta
# import compat_fix

# import argparse
# import json
# import os
# from pathlib import Path
# from typing import Dict, Optional, List
# import cv2
# import numpy as np

# # استدعاء ملفات التحليل والنظام الخبير
# from all_face_analysis import analyze_face_from_image_dict
# from skin_analysis import analyze_skin_from_image_dict as analyze_skin
# from full_makeup_expert_system import CompleteMakeupExpertSystem
# from clothing_hue_extractor import analyze_clothing_color
# from experta import KnowledgeEngine, Fact, Rule, MATCH, TEST


# # ══════════════════════════════════════════════════════════════════
# # 1. قواعد وبيانات باليتات ظلال العيون (القيم المحايدة)
# # ══════════════════════════════════════════════════════════════════

# NEUTRAL_12_WARM = {
#     "Highlight": [(18, 20, 255), (22, 25, 240), (15, 15, 255)],
#     "Base":      [(20, 60, 200), (25, 70, 180), (30, 55, 190)],
#     "Sculpt":    [(15, 95, 90), (12, 110, 80), (10, 120, 70)],
#     "Accent":    [(25, 80, 230), (18, 90, 210), (30, 70, 220)],
# }

# NEUTRAL_12_COOL = {
#     "Highlight": [(160, 15, 255), (170, 20, 240), (155, 10, 255)],
#     "Base":      [(165, 50, 200), (160, 40, 190), (170, 45, 180)],
#     "Sculpt":    [(170, 90, 90), (160, 100, 80), (175, 110, 70)],
#     "Accent":    [(165, 70, 230), (170, 80, 210), (160, 60, 220)],
# }

# def hsv_to_rgb(hsv):
#     hsv_img = np.uint8([[[hsv[0], hsv[1], hsv[2]]]])
#     return cv2.cvtColor(hsv_img, cv2.COLOR_HSV2RGB)[0][0]

# def rgb_hex_hue(rgb):
#     hex_color = "#{:02X}{:02X}{:02X}".format(rgb[0], rgb[1], rgb[2])
#     hsv_back = cv2.cvtColor(np.uint8([[rgb]]), cv2.COLOR_RGB2HSV)[0][0]
#     return hex_color, hsv_back[0]

# def dedupe_hsv(hsv, seen, step=6, guard=30):
#     rgb = hsv_to_rgb(hsv)
#     rgb_key = tuple(int(x) for x in rgb)
#     is_acceptable = (rgb_key not in seen) or guard <= 0
#     return (hsv, rgb) if is_acceptable else dedupe_hsv(
#         ((hsv[0] + step) % 180, hsv[1], hsv[2]), seen, step, guard - 1
#     )

# def extract_color_data(hsv, seen):
#     _, rgb = dedupe_hsv(hsv, seen)
#     seen.add(tuple(int(x) for x in rgb))
#     hex_color, final_hue = rgb_hex_hue(rgb)
#     return {"hex": hex_color, "rgb": tuple(int(x) for x in rgb), "hue": int(final_hue)}

# UNDERTONE_TRANSFORMS = {
#     "warm": lambda h, s, v: ((h + 8) % 180, min(s + 25, 255), min(v + 15, 255)),
#     "cool": lambda h, s, v: ((h - 12) % 180, min(s + 35, 255), max(v - 20, 0)),
# }

# def apply_undertone(hsv, transform_name):
#     h, s, v = hsv
#     transform = UNDERTONE_TRANSFORMS.get(transform_name, lambda h, s, v: (h, s, v))
#     return transform(h, s, v)

# PALETTE_BASE_RULES = {
#     "Monochromatic": lambda H, t: {"Highlight": apply_undertone((H, 30, 255), t), "Base": apply_undertone((H, 70, 180), t), "Sculpt": apply_undertone((H, 95, 90), t)},
#     "Analogous": lambda H, t: {"Highlight": apply_undertone(((H - 10) % 180, 35, 255), t), "Base": apply_undertone(((H + 15) % 180, 65, 185), t), "Sculpt": apply_undertone(((H + 35) % 180, 85, 80), t)},
#     "Split-Complementary": lambda H, t: {"Highlight": apply_undertone((H, 25, 255), t), "Base": apply_undertone(((H + 75) % 180, 60, 190), t), "Sculpt": apply_undertone(((H + 105) % 180, 90, 70), t)},
#     "Triadic": lambda H, t: {"Highlight": apply_undertone((20, 20, 255), t), "Base": apply_undertone(((H + 60) % 180, 55, 175), t), "Sculpt": apply_undertone(((H - 60) % 180, 85, 75), t)},
#     "Earth Colors": lambda H, t: {"Highlight": apply_undertone((20, 25, 245), t), "Base": apply_undertone((15, 65, 160), t), "Sculpt": apply_undertone((12, 95, 60), t)},
# }

# def generate_neutral_palette_data(palette):
#     seen = set()
#     collected_colors = []
#     for group in ["Highlight", "Base", "Sculpt", "Accent"]:
#         for hsv in palette[group]:
#             color_info = extract_color_data(hsv, seen)
#             color_info["role"] = group
#             collected_colors.append(color_info)
#     return {"Neutral Palette": collected_colors}

# def generate_all_palettes_data(H, transform_name):
#     seen = set()
#     collected_dict = {}
#     for strat, rule_func in PALETTE_BASE_RULES.items():
#         palette = rule_func(H, transform_name)
#         strat_colors = []
#         for role, hsv in palette.items():
#             color_info = extract_color_data(hsv, seen)
#             color_info["role"] = role
#             strat_colors.append(color_info)
#         collected_dict[strat] = strat_colors
#     return collected_dict


# # ══════════════════════════════════════════════════════════════════
# # 2. النظام الخبير للملابس والظلال
# # ══════════════════════════════════════════════════════════════════

# class ClothColor(Fact): pass
# class SkinInfo(Fact): pass

# class MakeupExpert(KnowledgeEngine):
#     def __init__(self):
#         super().__init__()
#         self.path, self.reason, self.hue, self.transform = None, None, None, None

#     @Rule(ClothColor(bgr=None))
#     def rule_missing(self): self.path, self.reason = "neutral", "missing"

#     @Rule(ClothColor(bgr=MATCH.bgr), TEST(lambda bgr: bgr is not None and bgr[0] < 40 and bgr[1] < 40 and bgr[2] < 40))
#     def rule_black(self, bgr): self.path, self.reason = "neutral", "black"

#     @Rule(ClothColor(bgr=MATCH.bgr), TEST(lambda bgr: bgr is not None and bgr[0] > 220 and bgr[1] > 220 and bgr[2] > 220))
#     def rule_white(self, bgr): self.path, self.reason = "neutral", "white"

#     @Rule(ClothColor(bgr=MATCH.bgr, hue=MATCH.hue), TEST(lambda bgr: bgr is not None and not (bgr[0]<40 and bgr[1]<40 and bgr[2]<40) and not (bgr[0]>220 and bgr[1]>220 and bgr[2]>220)))
#     def rule_colored(self, bgr, hue): self.path, self.reason, self.hue = "colored", "colored", hue

#     @Rule(SkinInfo(undertone="Warm"))
#     def rule_warm(self): self.transform = "warm"

#     @Rule(SkinInfo(undertone="Cool"))
#     def rule_cool(self): self.transform = "cool"


# # ══════════════════════════════════════════════════════════════════
# # 3. البايپلاين الرئيسي للمكياج
# # ══════════════════════════════════════════════════════════════════

# def run_pipeline(face_image_path: str, clothing_image_path: Optional[str] = None, occasion: str = 'wedding'):
#     print("\n================================================================================")
#     print("  بدء تحليل الصورة وتوليد توصيات المكياج")
#     print("================================================================================")

#     # 1. تحليل ملامح الوجه
#     print("\n[1/3] تحليل الوجه (MediaPipe)...")
#     face_res = analyze_face_from_image_dict(face_image_path)
#     print("  ✓ تم تحليل شكل الوجه والعينين والحواجب والشفاه والأنف")

#     # 2. تحليل أندرتون وعمق البشرة
#     print("\n[2/3] تحليل لون البشرة...")
#     skin_res = analyze_skin(face_image_path)
#     undertone = skin_res.get('undertone', 'Warm')
#     depth = skin_res.get('skin_depth', 'Medium')
#     print(f"  ✓ العمق: {depth} | الأندرتون: {undertone}")

#     # 3. تحليل لون الملابس إذا وُجدت
#     cloth_bgr, cloth_hue = None, None
#     if clothing_image_path and os.path.exists(clothing_image_path):
#         print("\n[3/3] تحليل لون الملابس...")
#         cloth_data = analyze_clothing_color(clothing_image_path)
#         cloth_bgr = cloth_data.get("dominant_bgr")
#         cloth_hue = cloth_data.get("Input_Hue")

#     # 4. تشغيل النظام الخبير الشامل للمكياج
#     print("\n[3/3] تشغيل النظام الخبير وتوليد التوصيات...")
#     expert = CompleteMakeupExpertSystem()
#     expert_input = {
#         'eyes': face_res.get('eyes', {}),
#         'brows': face_res.get('brows', {}),
#         'lips': face_res.get('lips', {}),
#         'nose': face_res.get('nose', {}),
#         'face_shape': face_res.get('face_shape', {}),
#         'skin': {'undertone': undertone, 'depth': depth},
#         'context': {'occasion': occasion, 'face_fullness': 'Full', 'eye_strategy': 'Monochromatic'}
#     }
#     expert_output = expert.analyze_complete_face(expert_input)

#     # 5. استخراج باليتات ألوان الظلال
#     shadow_expert = MakeupExpert()
#     shadow_expert.reset()
#     shadow_expert.declare(ClothColor(bgr=cloth_bgr, hue=cloth_hue))
#     shadow_expert.declare(SkinInfo(undertone=undertone))
#     shadow_expert.run()

#     if shadow_expert.path == "neutral":
#         palette12 = NEUTRAL_12_WARM if undertone == "Warm" else NEUTRAL_12_COOL
#         palettes_data = generate_neutral_palette_data(palette12)
#     else:
#         palettes_data = generate_all_palettes_data(shadow_expert.hue, shadow_expert.transform)

#     print("\n✓ اكتمل التحليل")

#     # 💾 6. حفظ النتائج والباليتات بالكامل في ملف JSON
#     final_output_dict = {
#         "skin": {"depth": depth, "undertone": undertone},
#         "occasion": occasion,
#         "expert_recommendations": expert_output,
#         "eyeshadow_palettes": palettes_data
#     }
    
#     json_filename = "makeup_analysis.json"
#     with open(json_filename, "w", encoding="utf-8") as f:
#         json.dump(final_output_dict, f, ensure_ascii=False, indent=4)
        
#     print(f"\n  ✓ تم حفظ النتائج بالكامل في ملف: {json_filename}")

#     # 7. طباعة التقرير النهائي النصي كاملاً مع الباليتات
#     print("\n================================================================================")
#     print("  التقرير النهائي — لكل ملمح: الشكل / المكياج المناسب / السبب")
#     print("================================================================================")
#     print(f"\nالبشرة: العمق = {depth} | الأندرتون = {undertone}")
#     print(f"المناسبة: {occasion}\n")

#     # طباعة التوصيات الحالية لكل ملمح
#     for feature_key, info in expert_output.items():
#         title = info.get('title', feature_key)
#         shape = info.get('shape_type', 'غير محدد')
#         rec = info.get('recommendation', '')
#         reason = info.get('reason', '')
#         print("-" * 80)
#         print(f"📍 الملمح: {feature_key}")
#         print(f"   الشكل/النوع : {shape}")
#         print(f"   المكياج     : {rec}")
#         print(f"   السبب       : {reason}")

#     # طباعة فقرة باليتات الظلال نصياً بدون صور
#     print("-" * 80)
#     print("📍 الملمح: ظلال العيون (Eyesshadow Palettes)")
#     print("-" * 80)
#     for strategy_name, colors in palettes_data.items():
#         print(f"\n🎨 استراتيجية: {strategy_name}")
#         for c in colors:
#             role = c.get('role', 'Color')
#             hex_val = c.get('hex', '')
#             rgb_val = c.get('rgb', '')
#             print(f"   • {role:<10} | HEX: {hex_val} | RGB: {rgb_val}")

#     print("\n================================================================================\n")


# # ══════════════════════════════════════════════════════════════════
# # 4. نقطة التشغيل الرئيسية (Main)
# # ══════════════════════════════════════════════════════════════════

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description="Complete Makeup Pipeline")
#     parser.add_argument('--face', required=True, help='مسار صورة الوجه')
#     parser.add_argument('--cloth', default=None, help='مسار صورة الملابس (اختياري)')
#     parser.add_argument('--occasion', default='wedding', help='المناسبة (مثل: wedding, evening, work)')
    
#     args = parser.parse_args()
    
#     run_pipeline(
#         face_image_path=args.face,
#         clothing_image_path=args.cloth,
#         occasion=args.occasion
#     )


import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import compat_fix

import argparse
import json
import os
from pathlib import Path
from typing import Dict, Optional, List
import cv2
import numpy as np

# استدعاء ملفات التحليل والنظام الخبير الأساسي
from all_face_analysis import analyze_face_from_image_dict
from skin_analysis import analyze_skin_from_image_dict as analyze_skin
from full_makeup_expert_system import CompleteMakeupExpertSystem
from clothing_hue_extractor import analyze_clothing_color

# الاستيراد المباشر والصحيح من ملف الظل
from shadow_palette_rules import (
    PALETTES_DICT, 
    generate_strategy_palettes, 
    dedupe_hsv, 
    hsv_to_rgb
)

# ══════════════════════════════════════════════════════════════════
# تطبيع مدخلات المستخدم
# ══════════════════════════════════════════════════════════════════

OCCASION_MAP = {
    'work': 'work', 'عمل': 'work', 'دوام': 'work',
    'university': 'university', 'جامعة': 'university', 'دراسة': 'university',
    'evening': 'evening', 'سهرة': 'evening', 'مساء': 'evening',
    'party': 'party', 'حفلة': 'party', 'حفل': 'party',
    'wedding': 'wedding', 'زفاف': 'wedding', 'عرس': 'wedding',
    'photo': 'photo', 'تصوير': 'photo', 'فوتوشوت': 'photo',
}

def normalize_occasion(raw_occasion: str) -> str:
    key = (raw_occasion or '').strip().lower()
    return OCCASION_MAP.get(key, 'evening')

# ── قواميس تعريب للعرض فقط ──

OCCASION_AR = {
    'work': 'عمل', 'university': 'جامعة', 'evening': 'سهرة',
    'party': 'حفلة', 'wedding': 'زفاف', 'photo': 'تصوير',
}

UNDERTONE_AR = {'warm': 'دافئ', 'cool': 'بارد', 'neutral': 'محايد'}
DEPTH_AR = {'fair': 'فاتحة', 'medium': 'متوسطة', 'dark': 'داكنة'}
SKIN_TYPE_AR = {'oily': 'دهنية', 'dry': 'جافة', 'combination': 'مختلطة',
                 'sensitive': 'حساسة', 'normal': 'عادية'}

def _ar(mapping: Dict, value: Optional[str]) -> str:
    if not value:
        return 'غير محدد'
    return mapping.get(str(value).strip().lower(), value)

def _adapt_eyes(eyes_raw: Dict) -> Dict:
    """تحويل صيغة نتائج all_face_analysis.analyze_eyes لصيغة يفهمها full_makeup_expert_system"""
    def conv(eye):
        geo = eye.get('geo_shape', 'Almond')
        etype = eye.get('eye_type', 'Normal')
        return {
            'geo_shape': geo,
            'eye_type': etype,
            'combined': f"{geo} {etype}".strip(),
            'size': eye.get('size', 'Normal'),
            'corner': eye.get('corner_direction', 'Neutral'),
        }

    return {
        'left': conv(eyes_raw.get('left_eye', {}) or {}),
        'right': conv(eyes_raw.get('right_eye', {}) or {}),
        'inter_eye_ratio': eyes_raw.get('inter_eye_ratio', 0.35)
    }

def _derive_fullness(face_shape_data: Dict) -> str:
    """تقدير امتلاء الوجه من نسبة الفك إلى عظمة الخد (تقريبي)"""
    ratio = (face_shape_data or {}).get('ratios', {}).get('jaw_to_cheekbone_ratio', 0.9)
    return 'Full' if ratio >= 0.9 else 'Thin'

def extract_palette_json_data(palette_dict, is_neutral=True, skin_undertone="Warm", clothing_hue=0):
    seen = set()
    collected_dict = {}

    if is_neutral:
        palette = PALETTES_DICT.get(skin_undertone, PALETTES_DICT["Cool"])
        groups = ["Highlight", "Base", "Sculpt", "Accent"]
        neutral_colors = []
        for group in groups:
            for hsv in palette[group]:
                _, rgb = dedupe_hsv(hsv, seen, min_distance=30)
                seen.add(tuple(map(int, rgb)))
                hex_color = "#{:02X}{:02X}{:02X}".format(rgb[0], rgb[1], rgb[2])
                neutral_colors.append({
                    "role": group,
                    "hex": hex_color,
                    "rgb": tuple(map(int, rgb)),
                    "hue": int(hsv[0])
                })
        collected_dict["Neutral Palette"] = neutral_colors
    else:
        strategies = generate_strategy_palettes(clothing_hue, skin_undertone)
        for strategy_name, palette in strategies.items():
            strat_colors = []
            for role, hsv in palette.items():
                _, rgb_p = dedupe_hsv(hsv, seen, min_distance=30)
                seen.add(tuple(map(int, rgb_p)))
                hex_color = "#{:02X}{:02X}{:02X}".format(rgb_p[0], rgb_p[1], rgb_p[2])
                strat_colors.append({
                    "role": role,
                    "hex": hex_color,
                    "rgb": tuple(map(int, rgb_p)),
                    "hue": int(hsv[0])
                })
            collected_dict[strategy_name] = strat_colors

    return collected_dict


# ══════════════════════════════════════════════════════════════════
# PIPELINE
# ══════════════════════════════════════════════════════════════════

class CompleteMakeupPipeline:
    """Pipeline شامل: صورة الوجه + الملابس + المناسبة → توصيات مكياج كاملة وباليتات ظلال"""

    def __init__(self):
        self.expert_system = CompleteMakeupExpertSystem()
        self.results = {}

    def process(self, face_image_path: str, occasion_raw: str, 
            clothing_image_path: Optional[str] = None, 
            eye_strategy: str = 'Monochromatic', 
            output_json: Optional[str] = None) -> Optional[Dict]:

        occasion = normalize_occasion(occasion_raw)

        print("\n" + "=" * 80)
        print("  بدء تحليل الصورة وتوليد توصيات المكياج والباليتات")
        print("=" * 80)

        # ── 1. تحليل الوجه (حقيقي عبر MediaPipe) ──
        print("\n[1/4] تحليل الوجه (MediaPipe)...")
        face_analysis = self._analyze_face(face_image_path)
        if face_analysis is None:
            return None
        self.results['face_analysis'] = face_analysis
        print("  ✓ تم تحليل شكل الوجه والعينين والحواجب والشفاه والأنف")

        # ── 2. تحليل البشرة ──
        print("\n[2/4] تحليل لون البشرة...")
        skin_analysis = self._analyze_skin(face_image_path)
        self.results['skin_analysis'] = skin_analysis
        undertone = skin_analysis.get('undertone', 'Warm')
        depth = skin_analysis.get('skin_depth', 'Medium')
        print(f"  ✓ العمق: {_ar(DEPTH_AR, depth)} | الأندرتون: {_ar(UNDERTONE_AR, undertone)}")

        # ── 3. تحليل الملابس (إن وُجدت) ──
        cloth_bgr, cloth_hue = None, 0
        if clothing_image_path and os.path.exists(clothing_image_path):
            print("\n[3/4] تحليل لون الملابس...")
            cloth_data = analyze_clothing_color(clothing_image_path)
            cloth_bgr = cloth_data.get("dominant_bgr")
            cloth_hue = cloth_data.get("Input_Hue", 0)
            print("  ✓ تم استخراج لون الملابس بنجاح")
        else:
            print("\n[3/4] تخطي تحليل الملابس (لم يتم إرفاق صفتها أو مسارها غير صحيح)")

        # ── 4. النظام الخبير (Experta) ──
        print("\n[4/4] تشغيل النظام الخبير وتوليد التوصيات والباليتات...")
        expert_input = self._prepare_expert_input(face_analysis, skin_analysis, occasion, eye_strategy)
        expert_output = self.expert_system.analyze_complete_face(expert_input)
        self.results['expert_output'] = expert_output
        self.results['occasion'] = occasion

        # تحديد ما إذا كان اللون محايداً أم لا لتوليد الباليتات الصحيحة
        is_neutral = (
            cloth_bgr is None or 
            (cloth_bgr[0] < 40 and cloth_bgr[1] < 40 and cloth_bgr[2] < 40) or 
            (cloth_bgr[0] > 220 and cloth_bgr[1] > 220 and cloth_bgr[2] > 220)
        )

        palettes_data = extract_palette_json_data(
            palette_dict=PALETTES_DICT, 
            is_neutral=is_neutral, 
            skin_undertone=undertone, 
            clothing_hue=cloth_hue
        )
        self.results['eyeshadow_palettes'] = palettes_data

        print("\n✓ اكتمل التحليل بنجاح\n")

        if output_json:
            self._save_json(output_json)

        return self.results

    def _analyze_face(self, image_path: str) -> Optional[Dict]:
        if not Path(image_path).exists():
            print(f"  ✗ خطأ: الصورة غير موجودة: {image_path}")
            return None

        result = analyze_face_from_image_dict(image_path)
        if not result.get('success') or not result.get('face_detected'):
            print(f"  ✗ خطأ: لم يتم اكتشاف وجه في الصورة ({result.get('error')})")
            return None

        return result

    def _analyze_skin(self, image_path: str) -> Dict:
        result = analyze_skin(image_path)
        if not result or not result.get('success'):
            print(f"  ⚠ تعذّر تحليل البشرة، تم استخدام قيم افتراضية ({result.get('error') if result else 'unknown'})")
            return {'skin_depth': 'Medium', 'undertone': 'Warm', 'skin_type': 'Normal'}
        return result

    def _prepare_expert_input(self, face_analysis: Dict, skin_analysis: Dict,
                               occasion: str, eye_strategy: str) -> Dict:
        eyes_adapted = _adapt_eyes(face_analysis.get('eyes', {}) or {})
        fullness = _derive_fullness(face_analysis.get('face_shape', {}))

        return {
            'eyes': eyes_adapted,
            'brows': face_analysis.get('brows', {}) or {},
            'lips': face_analysis.get('lips', {}) or {},
            'nose': face_analysis.get('nose', {}) or {},
            'face_shape': face_analysis.get('face_shape', {}) or {},
            'skin': {
                'undertone': skin_analysis.get('undertone', 'Warm'),
                'depth': skin_analysis.get('skin_depth', 'Medium'),
                'skin_type': skin_analysis.get('skin_type', 'Normal'),
            },
            'context': {
                'occasion': occasion,
                'face_fullness': fullness,
                'eye_strategy': eye_strategy,
            }
        }

    def _save_json(self, output_path: str):
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False, default=str)
            print(f"  ✓ تم حفظ النتائج بالكامل في: {output_path}")
        except Exception as e:
            print(f"  ✗ خطأ في حفظ JSON: {e}")

    # ══════════════════════════════════════════════════════════════
    # التقرير الموحّد (هيكل طريقتك الأساسي + قسم باليتات الظلال الإضافي)
    # ══════════════════════════════════════════════════════════════

    def build_unified_report(self) -> list:
        eo = self.results.get('expert_output', {}) or {}
        report = []

        # 1) شكل الوجه
        face = eo.get('face') or {}
        if face.get('shape'):
            makeup_parts = []
            if face.get('sculpt'):
                makeup_parts.append(f"كونتور: {face['sculpt']['placement']}")
            if face.get('blush'):
                makeup_parts.append(f"بلاشر: {face['blush']['placement']} (اللون: {(face.get('color') or {}).get('base_color', 'غير محدد')})")
            if face.get('highlight'):
                makeup_parts.append(f"هاياليت: {face['highlight']['placement']}")
            report.append({
                'feature': 'شكل الوجه',
                'shape': face['shape'].get('name_ar'),
                'makeup': ' | '.join(makeup_parts),
                'reason': face['shape'].get('goal'),
            })

        # 2) الحواجب
        brows = eo.get('brows') or {}
        if brows.get('correction') or brows.get('style'):
            correction = brows.get('correction') or {}
            style = brows.get('style') or {}
            color = brows.get('color') or {}
            report.append({
                'feature': 'الحواجب',
                'shape': f"قوس: {correction.get('arch_type', 'غير محدد')} | ذيل: {correction.get('tail_direction', 'غير محدد')}",
                'makeup': f"{style.get('style', 'غير محدد')} — {style.get('technique', 'غير محدد')} ({style.get('product', 'غير محدد')}) | اللون: {color.get('tone', 'غير محدد')}",
                'reason': correction.get('visual_purpose', 'غير محدد'),
            })

        # 3) العينان
        eyes = eo.get('eyes') or {}
        for side, label in (('left', 'العين اليسرى'), ('right', 'العين اليمنى')):
            eye = (eyes.get(side) or {})
            rec = eye.get('recommendation') or {}
            category = eye.get('category') or {}
            plan = eye.get('plan') or {}
            spacing = eye.get('spacing') or {}

            shape_ar = rec.get('category_ar') or category.get('name_ar')
            goal = rec.get('goal') or category.get('goal')
            style = plan.get('style') or rec.get('style')

            if shape_ar or style:
                spacing_text = spacing.get('rule') or 'المسافة بين العينين متوازنة'
                report.append({
                    'feature': label,
                    'shape': shape_ar or 'غير محدد',
                    'makeup': f"{style or 'غير محدد'} | القوام: {plan.get('texture', 'غير محدد')} | الرموش: {plan.get('lashes', 'غير محدد')} | الآيلاينر: {plan.get('eyeliner', 'غير محدد')} | تصحيح المسافة: {spacing_text}",
                    'reason': goal or 'غير محدد',
                })

        # 4) الشفاه
        lips = eo.get('lips') or {}
        if lips.get('shape'):
            shape = lips['shape']
            color = lips.get('color') or {}
            occ = lips.get('occasion') or {}
            report.append({
                'feature': 'الشفاه',
                'shape': shape.get('name_ar'),
                'makeup': f"{shape.get('correction', 'غير محدد')} — {shape.get('technique', 'غير محدد')} | اللون: {color.get('colors', 'غير محدد')} | المنتج: {occ.get('product', 'غير محدد')} ({occ.get('texture', 'غير محدد')})",
                'reason': shape.get('reason'),
            })

        # 5) الأنف
        nose = eo.get('nose') or {}
        if nose.get('shape'):
            shape = nose['shape']
            contour = nose.get('contour') or {}
            highlight = nose.get('highlight') or {}
            nmap = nose.get('map') or {}
            report.append({
                'feature': 'الأنف',
                'shape': shape.get('name_ar'),
                'makeup': f"{shape.get('technique', 'غير محدد')} | منتج الكونتور: {contour.get('product', 'غير محدد')} | الهاياليت: {highlight.get('tone', 'غير محدد')} ({nmap.get('highlight', 'غير محدد')})",
                'reason': shape.get('reason'),
            })

        # 6) الأساس والكونسيلر
        foundation = eo.get('foundation') or {}
        if foundation.get('shade') or foundation.get('formula'):
            shade = foundation.get('shade') or {}
            formula = foundation.get('formula') or {}
            concealer = foundation.get('concealer') or {}
            primer = foundation.get('primer') or {}
            setting = foundation.get('setting') or {}
            report.append({
                'feature': 'الأساس والكونسيلر',
                'shape': f"{shade.get('descriptor', 'غير محدد')} ({shade.get('range', 'غير محدد')})",
                'makeup': f"الأساس: {formula.get('primary', 'غير محدد')} ({formula.get('texture', 'غير محدد')}) | الكونسيلر: {concealer.get('descriptor', 'غير محدد')} | البرايمر: {primer.get('type', 'غير محدد')} | التثبيت: {setting.get('method', 'غير محدد')}",
                'reason': formula.get('reason', 'غير محدد'),
            })

        return report

    def print_report(self):
        print("\n" + "=" * 80)
        print("  التقرير النهائي — لكل ملمح: الشكل / المكياج المناسب / السبب")
        print("=" * 80)

        skin = self.results.get('skin_analysis', {})
        print(f"\nالبشرة: العمق = {_ar(DEPTH_AR, skin.get('skin_depth'))} | الأندرتون = {_ar(UNDERTONE_AR, skin.get('undertone'))} | النوع = {_ar(SKIN_TYPE_AR, skin.get('skin_type'))}")
        print(f"المناسبة: {OCCASION_AR.get(self.results.get('occasion'), self.results.get('occasion', 'غير محدد'))}")

        report = self.build_unified_report()
        for item in report:
            print("\n" + "-" * 80)
            print(f"📍 الملمح: {item['feature']}")
            print(f"   الشكل/النوع : {item['shape']}")
            print(f"   المكياج     : {item['makeup']}")
            print(f"   سبب         : {item['reason']}")

        # طباعة باليتات الظلال الإضافية بتنسيق نظيف متطابق
        palettes_data = self.results.get('eyeshadow_palettes', {})
        if palettes_data:
            print("\n" + "-" * 80)
            print("📍 الملمح: ظلال العيون (Eyeshadow Palettes)")
            print("-" * 80)
            for strategy_name, colors in palettes_data.items():
                print(f"\n🎨 استراتيجية: {strategy_name}")
                for c in colors:
                    role = c.get('role', 'Color')
                    hex_val = c.get('hex', '')
                    rgb_val = c.get('rgb', '')
                    print(f"   • {role:<10} | HEX: {hex_val} | RGB: {rgb_val}")

        print("\n" + "=" * 80 + "\n")
        return report


# ══════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════

def analyze_image(
    face_image_path: str,
    occasion: str = 'evening',
    clothing_image_path: Optional[str] = None,  # 👈 توحيد الاسم هنا
    eye_strategy: str = 'Monochromatic',
    output_json: Optional[str] = None,
    print_report: bool = True
) -> Optional[Dict]:
    
    pipeline = CompleteMakeupPipeline()
    result = pipeline.process(
        face_image_path=face_image_path,
        occasion_raw=occasion,                  # 👈 انتبهي: المعامل في process اسمه occasion_raw
        clothing_image_path=clothing_image_path, # 👈 تمرير الاسم الصحيح
        eye_strategy=eye_strategy,
        output_json=output_json
    )
    
    report = None
    if result and print_report:
        report = pipeline.print_report()
        
    if result is not None:
        result['unified_report'] = report if report is not None else pipeline.build_unified_report()
        
    return result


def main():
    parser = argparse.ArgumentParser(description='تحليل صورة الوجه والملابس وتوليد توصيات مكياج كاملة')
    parser.add_argument('--face', required=True, help='مسار صورة الوجه')
    parser.add_argument('--cloth', default=None, help='مسار صورة الملابس (اختياري)')
    parser.add_argument('--occasion', required=False, default='evening',
                         help='المناسبة: work / university / evening / party / wedding / photo')
    parser.add_argument('--eye-strategy', required=False, default='Monochromatic',
                         help='استراتيجية مكياج العين: Monochromatic / Contrast / Triadic / Earthy')
    parser.add_argument('--output', required=False, default='makeup_analysis.json', help='مسار حفظ JSON')
    args = parser.parse_args()

    analyze_image(
        face_image_path=args.face,
        clothing_image_path=args.cloth,
        occasion=args.occasion,
        eye_strategy=args.eye_strategy,
        output_json=args.output,
        print_report=True
    )

if __name__ == "__main__":
    main()