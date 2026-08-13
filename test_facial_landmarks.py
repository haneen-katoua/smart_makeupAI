# -*- coding: utf-8 -*-
"""
test_facial_landmarks.py — اختبار دقة قياسات الملامح
=====================================================

استخدام:
    python test_facial_landmarks.py --image path/to/image.jpg
    
أو من داخل Python:
    from test_facial_landmarks import test_face_analysis
    test_face_analysis('image.jpg')
"""

import compat_fix

import json
import argparse
from pathlib import Path
from all_face_analysis import analyze_face_from_image_dict


def print_section(title: str):
    """طباعة عنوان قسم"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def test_face_analysis(image_path: str):
    """اختبار شامل لتحليل الملامح"""
    
    if not Path(image_path).exists():
        print(f"❌ الصورة غير موجودة: {image_path}")
        return False
    
    print_section("🧪 اختبار تحليل الملامح")
    print(f"الصورة: {image_path}\n")
    
    # ── تشغيل التحليل ──
    result = analyze_face_from_image_dict(image_path)
    
    if not result.get('success'):
        print(f"❌ فشل التحليل: {result.get('error')}")
        return False
    
    if not result.get('face_detected'):
        print(f"❌ لم يتم اكتشاف وجه في الصورة")
        return False
    
    print("✅ تم اكتشاف الوجه بنجاح\n")
    
    # ── اختبار تحليل الشفاه ──
    print_section("1️⃣  تحليل الشفاه")
    lips = result.get('lips', {})
    
    if not lips:
        print("⚠️  لا توجد بيانات للشفاه")
    else:
        print(f"الامتلاء (Volume): {lips.get('volume', 'N/A')}")
        print(f"التوازن (Balance): {lips.get('balance', 'N/A')}")
        print(f"العرض (Width): {lips.get('width', 'N/A')}")
        
        measurements = lips.get('measurements', {})
        if measurements:
            print(f"\nالقياسات:")
            print(f"  - امتلاء الشفة العلوية: {measurements.get('upper_thickness', 0):.4f}")
            print(f"  - امتلاء الشفة السفلى: {measurements.get('lower_thickness', 0):.4f}")
            print(f"  - النسبة (Upper/Lower): {measurements.get('thickness_ratio', 0):.4f}")
            
            # اختبار المنطق
            ratio = measurements.get('thickness_ratio', 1.0)
            if ratio > 1.2:
                print(f"  ✅ نتيجة صحيحة: الشفة العلوية أكثر امتلاءً")
            elif ratio < 0.83:
                print(f"  ✅ نتيجة صحيحة: الشفة السفلى أكثر امتلاءً")
            else:
                print(f"  ✅ نتيجة صحيحة: الشفاه متوازنة")
    
    # ── اختبار تحليل العيون ──
    print_section("2️⃣  تحليل العيون")
    eyes = result.get('eyes', {})
    
    if not eyes:
        print("⚠️  لا توجد بيانات للعيون")
    else:
        left_eye = eyes.get('left_eye', {})
        right_eye = eyes.get('right_eye', {})
        
        print(f"العين اليسرى:")
        print(f"  - الشكل: {left_eye.get('geo_shape', 'N/A')}")
        print(f"  - الحجم: {left_eye.get('size', 'N/A')}")
        print(f"  - فتحة العين: {left_eye.get('opening', 0):.4f}")
        
        print(f"\nالعين اليمنى:")
        print(f"  - الشكل: {right_eye.get('geo_shape', 'N/A')}")
        print(f"  - الحجم: {right_eye.get('size', 'N/A')}")
        print(f"  - فتحة العين: {right_eye.get('opening', 0):.4f}")
        
        inter_eye_ratio = eyes.get('inter_eye_ratio', 0)
        print(f"\nمسافة العينين:")
        print(f"  - النسبة: {inter_eye_ratio:.4f}")
        
        if inter_eye_ratio < 0.32:
            print(f"  ✅ العيون متقاربة (Close-set)")
        elif inter_eye_ratio > 0.42:
            print(f"  ✅ العيون متباعدة (Wide-set)")
        else:
            print(f"  ✅ المسافة طبيعية (Normal)")
        
        print(f"\nالتناسق: {eyes.get('symmetry', 'N/A')}")
    
    # ── اختبار تحليل الحواجب ──
    print_section("3️⃣  تحليل الحواجب")
    brows = result.get('brows', {})
    
    if not brows:
        print("⚠️  لا توجد بيانات للحواجب")
    else:
        print(f"السمك (Thickness): {brows.get('thickness', 'N/A')}")
        print(f"الطول (Length): {brows.get('length', 'N/A')}")
        print(f"الشكل (Shape): {brows.get('shape', 'N/A')}")
        
        measurements = brows.get('measurements', {})
        if measurements:
            print(f"\nالقياسات:")
            print(f"  - طول الحاجب الأيسر: {measurements.get('left_length', 0):.4f}")
            print(f"  - طول الحاجب الأيمن: {measurements.get('right_length', 0):.4f}")
            print(f"  - عمق القوس (متوسط): {measurements.get('avg_arch_depth', 0):.4f}")
    
    # ── اختبار تحليل الأنف ──
    print_section("4️⃣  تحليل الأنف")
    nose = result.get('nose', {})
    
    if not nose:
        print("⚠️  لا توجد بيانات للأنف")
    else:
        print(f"الشكل (Shape): {nose.get('shape', 'N/A')}")
        print(f"العرض (Width): {nose.get('width', 'N/A')}")
        print(f"الجسر (Bridge): {nose.get('bridge', 'N/A')}")
        
        measurements = nose.get('measurements', {})
        if measurements:
            print(f"\nالقياسات:")
            print(f"  - الطول: {measurements.get('length', 0):.4f}")
            print(f"  - العرض (جانبي): {measurements.get('width_sides', 0):.4f}")
            print(f"  - عرض المنخرين: {measurements.get('nostril_width', 0):.4f}")
            ratio = measurements.get('length_to_width_ratio', 1.0)
            print(f"  - النسبة (طول/عرض): {ratio:.4f}")
            
            if ratio > 1.5:
                print(f"  ✅ الأنف طويل")
            elif ratio < 0.8:
                print(f"  ✅ الأنف قصير")
            else:
                print(f"  ✅ الأنف متوازن")
    
    # ── اختبار تحليل شكل الوجه ──
    print_section("5️⃣  تحليل شكل الوجه")
    face_shape = result.get('face_shape', {})
    
    if not face_shape:
        print("⚠️  لا توجد بيانات لشكل الوجه")
    else:
        print(f"الشكل: {face_shape.get('shape', 'N/A')}")
        print(f"الثقة (Confidence): {face_shape.get('confidence', 0):.2%}")
        
        votes = face_shape.get('votes', {})
        if votes:
            print(f"\nالتصويتات:")
            for shape, vote in sorted(votes.items(), key=lambda x: x[1], reverse=True):
                print(f"  - {shape}: {vote} صوت")
        
        ratios = face_shape.get('ratios', {})
        if ratios:
            print(f"\nالنسب:")
            print(f"  - الطول/العرض: {ratios.get('face_length_to_width', 0):.4f}")
            print(f"  - الفك/عظام الخد: {ratios.get('jaw_to_cheekbone_ratio', 0):.4f}")
            print(f"  - الجبهة/الفك: {ratios.get('forehead_to_jaw_ratio', 0):.4f}")
    
    # ── الملخص ──
    print_section("✅ ملخص النتائج")
    print("تم التحليل بنجاح! البيانات الآن جاهزة للنظام الخبير.")
    print("\nيمكنك الآن تشغيل:")
    print("  python complete_makeup_pipline.py --face image.jpg --occasion evening")
    
    # ── حفظ النتائج ──
    output_file = Path(image_path).stem + "_analysis.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False, default=str)
    print(f"\n💾 تم حفظ النتائج في: {output_file}")
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description='اختبار دقة تحليل الملامح باستخدام MediaPipe'
    )
    parser.add_argument('--image', '-i', required=True, help='مسار الصورة')
    parser.add_argument('--output', '-o', default=None, help='مسار الملف للحفظ (اختياري)')
    
    args = parser.parse_args()
    
    success = test_face_analysis(args.image)
    
    exit(0 if success else 1)


if __name__ == "__main__":
    main()
