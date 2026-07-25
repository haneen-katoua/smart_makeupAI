# -*- coding: utf-8 -*-
"""
complete_makeup_pipeline.py — End-to-End Makeup Analysis Pipeline
==================================================================
المدخلات (حالياً): صورة الوجه + المناسبة
المخرجات: تقرير موحّد لكل ملمح (الشكل/النوع + المكياج المناسب + السبب)
          + نسخة JSON جاهزة للاستخدام في API/واجهات.

ملاحظة: تحليل لون اللبس (outfit_color_analysis.py) غير مُستخدم حالياً بالنظام،
        وسيُضاف لاحقاً كخطوة مستقلة دون الحاجة لتعديل هذا الملف من جديد
        (يكفي إعادة تفعيل الاستدعاء في process() عند جهوزه).

Flow:
  صورة الوجه → MediaPipe (شكل الوجه/العيون/الحواجب/الشفاه/الأنف) الحقيقي
  صورة الوجه → تحليل لون البشرة (Undertone / Depth / Skin type)
  → Experta Expert System → توصيات كاملة → تقرير موحّد
"""

# ✅ MUST BE FIRST: Python 3.10+ Compatibility Fix
import compat_fix

import argparse
import json
from pathlib import Path
from typing import Dict, Optional

from all_face_analysis import analyze_face_from_image_dict
from skin_analysis import analyze_skin_from_image_dict as analyze_skin
from full_makeup_expert_system import CompleteMakeupExpertSystem


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


# ── قواميس تعريب للعرض فقط (لا تُستخدم في منطق المطابقة) ──

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


# ══════════════════════════════════════════════════════════════════
# PIPELINE
# ══════════════════════════════════════════════════════════════════

class CompleteMakeupPipeline:
    """Pipeline شامل: صورة الوجه + المناسبة → توصيات مكياج كاملة"""

    def __init__(self):
        self.expert_system = CompleteMakeupExpertSystem()
        self.results = {}

    def process(self, face_image_path: str, occasion_raw: str,
                eye_strategy: str = 'Monochromatic',
                output_json: Optional[str] = None) -> Optional[Dict]:

        occasion = normalize_occasion(occasion_raw)

        print("\n" + "=" * 80)
        print("  بدء تحليل الصورة وتوليد توصيات المكياج")
        print("=" * 80)

        # ── تحليل الوجه (حقيقي عبر MediaPipe) ──
        print("\n[1/3] تحليل الوجه (MediaPipe)...")
        face_analysis = self._analyze_face(face_image_path)
        if face_analysis is None:
            return None
        self.results['face_analysis'] = face_analysis
        print("  ✓ تم تحليل شكل الوجه والعينين والحواجب والشفاه والأنف")

        # ── تحليل البشرة ──
        print("\n[2/3] تحليل لون البشرة...")
        skin_analysis = self._analyze_skin(face_image_path)
        self.results['skin_analysis'] = skin_analysis
        print(f"  ✓ العمق: {_ar(DEPTH_AR, skin_analysis.get('skin_depth'))} | الأندرتون: {_ar(UNDERTONE_AR, skin_analysis.get('undertone'))}")

        # ── النظام الخبير (Experta) ──
        print("\n[3/3] تشغيل النظام الخبير وتوليد التوصيات...")
        expert_input = self._prepare_expert_input(face_analysis, skin_analysis, occasion, eye_strategy)
        expert_output = self.expert_system.analyze_complete_face(expert_input)
        self.results['expert_output'] = expert_output
        self.results['occasion'] = occasion

        print("\n✓ اكتمل التحليل\n")

        if output_json:
            self._save_json(output_json)

        return self.results

    # ── تحليل الوجه الحقيقي ──
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
            print(f"  ✓ تم حفظ النتائج في: {output_path}")
        except Exception as e:
            print(f"  ✗ خطأ في حفظ JSON: {e}")

    # ══════════════════════════════════════════════════════════════
    # التقرير الموحّد: لكل ملمح → الشكل + المكياج المناسب + السبب
    # ══════════════════════════════════════════════════════════════

    def build_unified_report(self) -> list:
        """يبني قائمة عناصر: كل عنصر يمثل ملمحاً واحداً بصيغة موحّدة وجاهزة لأي API"""
        eo = self.results.get('expert_output', {}) or {}
        report = []

        # 1) شكل الوجه (كونتور/بلاشر/هاياليت)
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

            # نعتمد التوصية المجمّعة إن وُجدت، وإلا نبني من الحقائق الفردية
            shape_ar = rec.get('category_ar') or category.get('name_ar')
            goal = rec.get('goal') or category.get('goal')
            style = plan.get('style') or rec.get('style')

            if shape_ar or style:
                spacing_text = spacing.get('rule') or 'المسافة بين العينين متوازنة، ولذلك لا حاجة لأي تصحيح لوني في الزاوية الداخلية'
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
        """طباعة التقرير الموحّد على الكونسول بشكل واضح ومنظّم"""
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
            print(f"   السبب       : {item['reason']}")

        print("\n" + "=" * 80 + "\n")
        return report


# ══════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════

def analyze_image(face_image_path: str, occasion: str = 'evening',
                   eye_strategy: str = 'Monochromatic',
                   output_json: Optional[str] = None, print_report: bool = True) -> Optional[Dict]:
    """
    دالة مباشرة للاستخدام كمكتبة (مثلاً من داخل API):

        from complete_makeup_pipline import analyze_image
        data = analyze_image('face.jpg', occasion='wedding')
    """
    pipeline = CompleteMakeupPipeline()
    result = pipeline.process(face_image_path, occasion, eye_strategy, output_json)
    report = None
    if result and print_report:
        report = pipeline.print_report()
    if result is not None:
        result['unified_report'] = report if report is not None else pipeline.build_unified_report()
    return result


def main():
    parser = argparse.ArgumentParser(description='تحليل صورة الوجه وتوليد توصيات مكياج كاملة')
    parser.add_argument('--face', required=True, help='مسار صورة الوجه')
    parser.add_argument('--occasion', required=False, default='evening',
                         help='المناسبة: work / university / evening / party / wedding / photo (أو بالعربي)')
    parser.add_argument('--eye-strategy', required=False, default='Monochromatic',
                         help='استراتيجية مكياج العين: Monochromatic / Contrast / Triadic / Earthy')
    parser.add_argument('--output', required=False, default='makeup_analysis.json', help='مسار حفظ JSON')
    args = parser.parse_args()

    analyze_image(
        face_image_path=args.face,
        occasion=args.occasion,
        eye_strategy=args.eye_strategy,
        output_json=args.output,
        print_report=True
    )


if __name__ == "__main__":
    main()