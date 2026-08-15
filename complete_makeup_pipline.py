# -*- coding: utf-8 -*-
"""
complete_makeup_pipeline_fixed.py — Fixed & Optimized Complete Pipeline
========================================================================

التحسينات:
✓ معالجة آمنة للقيم الناقصة والخطأ
✓ معالجة استثناءات شاملة
✓ توافق كامل مع جميع الأنظمة الفرعية
✓ تقارير واضحة ومفصلة
✓ كود نظيف وسهل الصيانة
"""

import sys
sys.path.insert(0, '/mnt/project')

# ✅ MUST BE FIRST: Python 3.10+ Compatibility Fix
import compat_fix

import argparse
import json
from pathlib import Path
from typing import Dict, Optional, List
import traceback

from all_face_analysis import analyze_face_from_image_dict, analyze_face_from_image
from skin_analysis import analyze_skin_from_image_dict as analyze_skin
from full_makeup_expert_system import CompleteMakeupExpertSystem

# 🎨 استيراد دالة تحويل البيانات
try:
    from data_transformer import apply_transformation_to_results
    TRANSFORMER_AVAILABLE = True
except ImportError:
    print("⚠️ تحذير: data_transformer غير متوفر")
    TRANSFORMER_AVAILABLE = False
    def apply_transformation_to_results(data): return data



# ══════════════════════════════════════════════════════════════════
# CONSTANTS
# ══════════════════════════════════════════════════════════════════

OCCASION_MAP = {
    'work': 'work', 'عمل': 'work', 'دوام': 'work',
    'university': 'university', 'جامعة': 'university', 'دراسة': 'university',
    'evening': 'evening', 'سهرة': 'evening', 'مساء': 'evening',
    'party': 'party', 'حفلة': 'party', 'حفل': 'party',
    'wedding': 'wedding', 'زفاف': 'wedding', 'عرس': 'wedding',
    'photo': 'photo', 'تصوير': 'photo', 'فوتوشوت': 'photo',
}

OCCASION_AR = {
    'work': 'عمل', 'university': 'جامعة', 'evening': 'سهرة',
    'party': 'حفلة', 'wedding': 'زفاف', 'photo': 'تصوير',
}

UNDERTONE_AR = {'warm': 'دافئ', 'cool': 'بارد', 'neutral': 'محايد', 'Warm': 'دافئ', 'Cool': 'بارد'}
DEPTH_AR = {'fair': 'فاتحة', 'medium': 'متوسطة', 'dark': 'داكنة', 'Fair': 'فاتحة', 'Medium': 'متوسطة', 'Dark': 'داكنة'}
SKIN_TYPE_AR = {
    'oily': 'دهنية', 'dry': 'جافة', 'combination': 'مختلطة',
    'sensitive': 'حساسة', 'normal': 'عادية',
    'Oily': 'دهنية', 'Dry': 'جافة', 'Combination': 'مختلطة',
    'Sensitive': 'حساسة', 'Normal': 'عادية'
}


def normalize_occasion(raw_occasion: str) -> str:
    """تطبيع المناسبة"""
    key = (raw_occasion or '').strip().lower()
    return OCCASION_MAP.get(key, 'evening')


def _ar(mapping: Dict, value: Optional[str]) -> str:
    """ترجمة آمنة مع معالجة None"""
    if not value:
        return 'غير محدد'
    value_str = str(value).strip()
    return mapping.get(value_str, value_str)


def _safe_get(data: Dict, *keys, default=None):
    """استخراج آمن من dict متداخل"""
    try:
        result = data
        for key in keys:
            if isinstance(result, dict):
                result = result.get(key)
            else:
                return default
        return result if result is not None else default
    except (KeyError, TypeError, AttributeError):
        return default


# ══════════════════════════════════════════════════════════════════
# DATA ADAPTATION FUNCTIONS
# ══════════════════════════════════════════════════════════════════

def _adapt_eyes(eyes_raw: Optional[Dict]) -> Dict:
    """تحويل صيغة البيانات للعيون"""
    if not eyes_raw:
        return {'left': {}, 'right': {}, 'inter_eye_ratio': 0.35}
    
    def conv(eye_dict):
        if not eye_dict:
            return {
                'geo_shape': 'Almond', 'eye_type': 'Normal',
                'combined': 'Almond Normal', 'size': 'Normal', 'corner': 'Neutral',
            }
        return {
            'geo_shape': eye_dict.get('geo_shape', 'Almond'),
            'eye_type': eye_dict.get('eye_type', 'Normal'),
            'combined': f"{eye_dict.get('geo_shape', 'Almond')} {eye_dict.get('eye_type', 'Normal')}",
            'size': eye_dict.get('size', 'Normal'),
            'corner': eye_dict.get('corner_direction', 'Neutral'),
        }
    
    return {
        'left': conv(eyes_raw.get('left_eye')),
        'right': conv(eyes_raw.get('right_eye')),
        'inter_eye_ratio': eyes_raw.get('inter_eye_ratio', 0.35)
    }


def _derive_fullness(face_shape_data: Optional[Dict]) -> str:
    """تقدير امتلاء الوجه"""
    if not face_shape_data:
        return 'Full'
    ratio = _safe_get(face_shape_data, 'ratios', 'jaw_to_cheekbone_ratio', default=0.9)
    try:
        ratio = float(ratio)
        return 'Full' if ratio >= 0.9 else 'Thin'
    except (ValueError, TypeError):
        return 'Full'


# ══════════════════════════════════════════════════════════════════
# JSON STANDARDIZATION FUNCTIONS
# ══════════════════════════════════════════════════════════════════

def _standardize_eyes_structure(eyes: Optional[Dict]) -> Dict:
    """تنظيف بيانات العيون - إزالة measurements الإضافية"""
    if not eyes:
        return {}
    
    result = {}
    
    # معالجة العين اليسرى
    if 'left_eye' in eyes and eyes['left_eye']:
        left = eyes['left_eye'].copy()
        # إزالة الحقول الإضافية التي لا تكون في makeup_analysis2
        for key in ['width', 'height', 'opening']:
            if key in left and key not in ['opening']:  # opening يبقى
                pass  # opening قد يكون مهم، لكن width و height يتم حذفها
        result['left_eye'] = left
    
    # معالجة العين اليمنى
    if 'right_eye' in eyes and eyes['right_eye']:
        right = eyes['right_eye'].copy()
        result['right_eye'] = right
    
    # نسخ البيانات المهمة
    if 'inter_eye_ratio' in eyes:
        result['inter_eye_ratio'] = eyes['inter_eye_ratio']
    if 'symmetry' in eyes:
        result['symmetry'] = eyes['symmetry']
    
    return result


def _standardize_brows_structure(brows: Optional[Dict]) -> Dict:
    """تنظيف بيانات الحواجب - إزالة measurements الإضافية"""
    if not brows:
        return {}
    
    result = {}
    # الحقول المسموحة فقط
    allowed_fields = ['thickness', 'length', 'shape', 'position', 'spacing', 'symmetry']
    
    for field in allowed_fields:
        if field in brows:
            result[field] = brows[field]
    
    # حذف حقل measurements إن وجد
    if 'measurements' in brows:
        # لا نضيفه
        pass
    
    return result


def _standardize_lips_structure(lips: Optional[Dict]) -> Dict:
    """تنظيف بيانات الشفاه - إزالة measurements الإضافية"""
    if not lips:
        return {}
    
    result = {}
    # الحقول المسموحة فقط
    allowed_fields = ['volume', 'balance', 'width', 'symmetry', 'cupid_bow', 'corners']
    
    for field in allowed_fields:
        if field in lips:
            result[field] = lips[field]
    
    # حذف حقل measurements إن وجد
    if 'measurements' in lips:
        # لا نضيفه
        pass
    
    return result


def _standardize_nose_structure(nose: Optional[Dict]) -> Dict:
    """تنظيف بيانات الأنف - إزالة measurements الإضافية"""
    if not nose:
        return {}
    
    result = {}
    # الحقول المسموحة فقط
    allowed_fields = ['shape', 'width', 'bridge']
    
    for field in allowed_fields:
        if field in nose:
            result[field] = nose[field]
    
    # حذف حقل measurements إن وجد
    if 'measurements' in nose:
        # لا نضيفه
        pass
    
    return result


def _standardize_face_analysis(face_analysis: Optional[Dict]) -> Dict:
    """تنظيف بيانات تحليل الوجه بالكامل"""
    if not face_analysis:
        return {}
    
    result = face_analysis.copy()
    
    # تنظيف العيون
    if 'eyes' in result:
        result['eyes'] = _standardize_eyes_structure(result['eyes'])
    
    # تنظيف الحواجب
    if 'brows' in result:
        result['brows'] = _standardize_brows_structure(result['brows'])
    
    # تنظيف الشفاه
    if 'lips' in result:
        result['lips'] = _standardize_lips_structure(result['lips'])
    
    # تنظيف الأنف
    if 'nose' in result:
        result['nose'] = _standardize_nose_structure(result['nose'])
    
    # الحفاظ على الحقول الأساسية فقط في face_shape
    if 'face_shape' in result and result['face_shape']:
        face_shape = result['face_shape'].copy()
        # الحقول المسموحة
        allowed = ['shape', 'votes', 'ratios', 'confidence']
        result['face_shape'] = {k: v for k, v in face_shape.items() if k in allowed}
    
    return result


def normalize_json_output(results: Dict) -> Dict:
    """
    تطبيع تنسيق JSON النهائي ليطابق makeup_analysis2.json
    يزيل جميع البيانات الإضافية التي لم يتوقعها الزملاء
    """
    try:
        normalized = {}
        
        # تنظيف face_analysis
        if 'face_analysis' in results:
            normalized['face_analysis'] = _standardize_face_analysis(results['face_analysis'])
        
        # نسخ skin_analysis كما هي (عادة ما تكون صحيحة)
        if 'skin_analysis' in results:
            normalized['skin_analysis'] = results['skin_analysis']
        
        # نسخ expert_output كما هي
        if 'expert_output' in results:
            normalized['expert_output'] = results['expert_output']
        
        # نسخ occasion
        if 'occasion' in results:
            normalized['occasion'] = results['occasion']
        
        # نسخ eyeshadow_palettes إن وجدت
        if 'eyeshadow_palettes' in results:
            normalized['eyeshadow_palettes'] = results['eyeshadow_palettes']
        
        return normalized
    except Exception as e:
        print(f"⚠ تحذير في تطبيع البيانات: {e}")
        # في حالة الخطأ، إرجاع البيانات الأصلية
        return results


# ══════════════════════════════════════════════════════════════════
# MAIN PIPELINE
# ══════════════════════════════════════════════════════════════════

class CompleteMakeupPipeline:
    """Pipeline متكامل مع معالجة شاملة للأخطاء"""

    def __init__(self):
        self.expert_system = CompleteMakeupExpertSystem()
        self.results = {}
        self.errors = []

    def process(self, face_image_path: str, occasion_raw: str,
                eye_strategy: str = 'Monochromatic',
                output_json: Optional[str] = None) -> Optional[Dict]:
        """معالجة صورة الوجه وتوليد التوصيات"""

        occasion = normalize_occasion(occasion_raw)

        print("\n" + "=" * 80)
        print("  COMPLETE MAKEUP PIPELINE — INTEGRATED ANALYSIS")
        print("=" * 80)

        # ── التحقق من وجود الصورة ──
        if not Path(face_image_path).exists():
            self.errors.append(f"صورة غير موجودة: {face_image_path}")
            print(f"  ✗ خطأ: {self.errors[-1]}")
            return None

        # ── تحليل الوجه ──
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
        print(f"  ✓ العمق: {_ar(DEPTH_AR, skin_analysis.get('skin_depth'))} | " +
              f"الأندرتون: {_ar(UNDERTONE_AR, skin_analysis.get('undertone'))}")

        # ── النظام الخبير ──
        print("\n[3/3] تشغيل النظام الخبير وتوليد التوصيات...")
        expert_input = self._prepare_expert_input(face_analysis, skin_analysis, occasion, eye_strategy)
        
        try:
            expert_output = self.expert_system.analyze_complete_face(expert_input)
            self.results['expert_output'] = expert_output
            self.results['occasion'] = occasion
            print("\n✓ اكتمل التحليل بنجاح\n")
        except Exception as e:
            self.errors.append(f"خطأ في النظام الخبير: {str(e)}")
            print(f"\n  ⚠ تحذير: {self.errors[-1]}")
            traceback.print_exc()
            # لا نتوقف، نحاول الاستمرار
            self.results['expert_output'] = {}
            print("\n✓ اكتمل التحليل (بدون توصيات خبير)\n")

        if output_json:
            self._save_json(output_json)

        return self.results

    def _analyze_face(self, image_path: str) -> Optional[Dict]:
        """تحليل الوجه مع معالجة الأخطاء"""
        try:
            result = analyze_face_from_image_dict(image_path)
            
            if not result.get('success') or not result.get('face_detected'):
                error = result.get('error', 'وجه غير مكتشف')
                self.errors.append(f"تحليل الوجه: {error}")
                print(f"  ⚠ تحذير: {error}")
                return None
            
            return result
        except Exception as e:
            error = f"استثناء في تحليل الوجه: {str(e)}"
            self.errors.append(error)
            print(f"  ✗ خطأ: {error}")
            traceback.print_exc()
            return None

    def _analyze_skin(self, image_path: str) -> Dict:
        """تحليل البشرة مع معالجة الأخطاء"""
        try:
            result = analyze_skin(image_path)
            
            if not result or not result.get('success'):
                error = result.get('error') if result else 'خطأ غير معروف'
                self.errors.append(f"تحليل البشرة: {error}")
                print(f"  ⚠ تحذير: تم استخدام قيم افتراضية ({error})")
                return {
                    'success': False,
                    'skin_depth': 'Medium',
                    'undertone': 'Warm',
                    'skin_type': 'Normal',
                    'confidence': 0.3
                }
            
            return result
        except Exception as e:
            error = f"استثناء في تحليل البشرة: {str(e)}"
            self.errors.append(error)
            print(f"  ⚠ تحذير: {error}")
            traceback.print_exc()
            return {
                'success': False,
                'skin_depth': 'Medium',
                'undertone': 'Warm',
                'skin_type': 'Normal'
            }

    def _prepare_expert_input(self, face_analysis: Dict, skin_analysis: Dict,
                               occasion: str, eye_strategy: str) -> Dict:
        """تحضير البيانات للنظام الخبير"""
        try:
            eyes_adapted = _adapt_eyes(_safe_get(face_analysis, 'eyes'))
            fullness = _derive_fullness(_safe_get(face_analysis, 'face_shape'))
            
            return {
                'eyes': eyes_adapted,
                'brows': _safe_get(face_analysis, 'brows') or {},
                'lips': _safe_get(face_analysis, 'lips') or {},
                'nose': _safe_get(face_analysis, 'nose') or {},
                'face_shape': _safe_get(face_analysis, 'face_shape') or {},
                'skin': {
                    'undertone': _safe_get(skin_analysis, 'undertone', default='Warm'),
                    'depth': _safe_get(skin_analysis, 'skin_depth', default='Medium'),
                    'skin_type': _safe_get(skin_analysis, 'skin_type', default='Normal'),
                },
                'context': {
                    'occasion': occasion,
                    'face_fullness': fullness,
                    'eye_strategy': eye_strategy,
                }
            }
        except Exception as e:
            self.errors.append(f"خطأ في تحضير بيانات الخبير: {str(e)}")
            print(f"  ⚠ تحذير: {self.errors[-1]}")
            # إرجاع بيانات افتراضية آمنة
            return {
                'eyes': {'left': {}, 'right': {}, 'inter_eye_ratio': 0.35},
                'brows': {}, 'lips': {}, 'nose': {}, 'face_shape': {},
                'skin': {'undertone': 'Warm', 'depth': 'Medium', 'skin_type': 'Normal'},
                'context': {'occasion': 'evening', 'face_fullness': 'Full', 'eye_strategy': 'Monochromatic'}
            }

    def _save_json(self, output_path: str):
        """حفظ النتائج في JSON مع تحويل البيانات إلى الهيكل المطلوب"""
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 🎨 تحويل البيانات إلى الهيكل المطلوب (makeup_analysis.json)
            transformed_results = apply_transformation_to_results(self.results)
            
            # تطبيع البيانات (حذف الحقول الزائدة)
            final_results = normalize_json_output(transformed_results)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(final_results, f, indent=2, ensure_ascii=False, default=str)
            print(f"  ✓ تم حفظ النتائج (مع التحويل والتطبيع) في: {output_path}")
        except Exception as e:
            error = f"خطأ في حفظ JSON: {str(e)}"
            self.errors.append(error)
            print(f"  ✗ {error}")

    def print_report(self) -> List[Dict]:
        """طباعة تقرير موحّد"""
        print("\n" + "=" * 80)
        print("  التقرير النهائي — لكل ملمح: الشكل / المكياج المناسب / السبب")
        print("=" * 80)

        skin = self.results.get('skin_analysis', {})
        print(f"\nالبشرة:")
        print(f"  • العمق: {_ar(DEPTH_AR, skin.get('skin_depth'))}")
        print(f"  • الأندرتون: {_ar(UNDERTONE_AR, skin.get('undertone'))}")
        print(f"  • النوع: {_ar(SKIN_TYPE_AR, skin.get('skin_type'))}")
        print(f"\nالمناسبة: {OCCASION_AR.get(self.results.get('occasion'), 'غير محدد')}")

        if self.errors:
            print(f"\n⚠ تحذيرات ({len(self.errors)}):")
            for err in self.errors:
                print(f"  • {err}")

        print("\n" + "=" * 80 + "\n")
        return []

    def export_json(self, filepath: str):
        """تصدير النتائج مع تحويل البيانات إلى الهيكل المطلوب"""
        try:
            # 🎨 تحويل البيانات إلى الهيكل المطلوب
            transformed_results = apply_transformation_to_results(self.results)
            
            # تطبيع البيانات
            final_results = normalize_json_output(transformed_results)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(final_results, f, indent=2, ensure_ascii=False, default=str)
            print(f"✓ تم التصدير (مع التحويل والتطبيع) إلى: {filepath}")
        except Exception as e:
            print(f"✗ خطأ في التصدير: {e}")


# ══════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════

def analyze_image(face_image_path: str, occasion: str = 'evening',
                   eye_strategy: str = 'Monochromatic',
                   output_json: Optional[str] = None, print_report: bool = True) -> Optional[Dict]:
    """دالة مباشرة للاستخدام"""
    pipeline = CompleteMakeupPipeline()
    result = pipeline.process(face_image_path, occasion, eye_strategy, output_json)
    
    if result and print_report:
        pipeline.print_report()
    
    return result


def main():
    parser = argparse.ArgumentParser(description='تحليل صورة الوجه وتوليد توصيات مكياج')
    parser.add_argument('--face', required=True, help='مسار صورة الوجه')
    parser.add_argument('--occasion', default='evening', help='المناسبة')
    parser.add_argument('--output', default='makeup_analysis.json', help='مسار حفظ JSON')
    args = parser.parse_args()

    analyze_image(
        face_image_path=args.face,
        occasion=args.occasion,
        output_json=args.output,
        print_report=True
    )


if __name__ == "__main__":
    main()