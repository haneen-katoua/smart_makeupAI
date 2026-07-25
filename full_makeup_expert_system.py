# ✅ MUST BE FIRST: Python 3.10+ Compatibility Fix
import compat_fix

import json
from eye_makeup_rules import EyeMakeupEngine
from brow_makeup_rules import BrowMakeupEngine
from lip_makeup_rules import LipMakeupEngine
from nose_makeup_rules import NoseMakeupEngine
from face_makeup_rules import FaceContourEngine
from foundation_makeup_rules import FoundationEngine


class CompleteMakeupExpertSystem:
    """نظام خبير متكامل لتحليل وصياغة توصيات مكياج العميل بالكامل"""
    
    def __init__(self):
        self.eye_engine = EyeMakeupEngine()
        self.brow_engine = BrowMakeupEngine()
        self.lip_engine = LipMakeupEngine()
        self.nose_engine = NoseMakeupEngine()
        self.face_engine = FaceContourEngine()
        self.foundation_engine = FoundationEngine()
        
        self.complete_analysis = {}
    
    def analyze_complete_face(self, analysis_data):
        """
        تحليل الوجه بالكامل وتوليد توصيات مكياج شاملة
        
        input: dict {
            # تحليل العيون
            'eyes': {
                'left': {
                    'geo_shape': 'Round',
                    'eye_type': 'Hooded',
                    'combined': 'Round Hooded',
                    'size': 'Normal',
                    'corner': 'Neutral'
                },
                'right': {...},
                'inter_eye_ratio': 0.30
            },
            
            # تحليل الحواجب
            'brows': {
                'thickness': 'Medium',
                'length': 'Medium',
                'shape': 'Soft Arch',
                'position': 'Normal',
                'spacing': 'Normal',
                'symmetry': 'Symmetrical'
            },
            
            # تحليل الشفاه
            'lips': {
                'volume': 'Medium',
                'balance': 'Lower Fuller',
                'width': 'Average',
                'symmetry': 'Symmetrical'
            },
            
            # تحليل الأنف
            'nose': {
                'shape': 'Balanced'
            },
            
            # تحليل شكل الوجه
            'face_shape': {
                'shape': 'Oval',
                'votes': {'Oval': 10, 'Round': 2}
            },
            
            # معلومات البشرة
            'skin': {
                'undertone': 'Warm',
                'depth': 'Medium',
                'skin_type': 'Combination'
            },
            
            # السياق
            'context': {
                'occasion': 'evening',
                'face_fullness': 'Full',
                'eye_strategy': 'Monochromatic'
            }
        }
        """
        
        print("\n" + "="*80)
        print("  COMPLETE MAKEUP EXPERT SYSTEM — INTEGRATED ANALYSIS")
        print("="*80)
        
        # ── تحليل العيون ──
        print("\n[1/6] ANALYZING EYES...")
        eye_results = self._analyze_eyes(analysis_data)
        self.complete_analysis['eyes'] = eye_results
        
        # ── تحليل الحواجب ──
        print("[2/6] ANALYZING BROWS...")
        brow_results = self._analyze_brows(analysis_data)
        self.complete_analysis['brows'] = brow_results
        
        # ── تحليل الشفاه ──
        print("[3/6] ANALYZING LIPS...")
        lip_results = self._analyze_lips(analysis_data)
        self.complete_analysis['lips'] = lip_results
        
        # ── تحليل الأنف ──
        print("[4/6] ANALYZING NOSE...")
        nose_results = self._analyze_nose(analysis_data)
        self.complete_analysis['nose'] = nose_results
        
        # ── تحليل الوجه (الكونتور/البلاشر) ──
        print("[5/6] ANALYZING FACE SHAPE (Contour/Blush)...")
        face_results = self._analyze_face_contour(analysis_data)
        self.complete_analysis['face'] = face_results
        
        # ── تحليل الأساس والكونسيلر ──
        print("[6/6] ANALYZING FOUNDATION & CONCEALER...")
        foundation_results = self._analyze_foundation(analysis_data)
        self.complete_analysis['foundation'] = foundation_results
        
        print("\n✓ ANALYSIS COMPLETE\n")
        
        return self.complete_analysis
    
    def _analyze_eyes(self, data):
        """تحليل العيون"""
        if 'eyes' not in data:
            return None
        
        results = {}
        eyes_data = data['eyes']
        
        # Left eye
        if 'left' in eyes_data:
            left_data = eyes_data['left'].copy()
            left_data['inter_eye_ratio'] = eyes_data.get('inter_eye_ratio')
            left_data['occasion'] = data.get('context', {}).get('occasion', 'work')
            left_data['side'] = 'Left'
            results['left'] = self.eye_engine.analyze_eye(left_data)
        
        # Right eye
        if 'right' in eyes_data:
            right_data = eyes_data['right'].copy()
            right_data['inter_eye_ratio'] = eyes_data.get('inter_eye_ratio')
            right_data['occasion'] = data.get('context', {}).get('occasion', 'work')
            right_data['side'] = 'Right'
            results['right'] = self.eye_engine.analyze_eye(right_data)
        
        return results
    
    def _analyze_brows(self, data):
        """تحليل الحواجب"""
        if 'brows' not in data:
            return None
        
        brow_data = data['brows'].copy()
        brow_data['face_shape'] = data.get('face_shape', {}).get('shape', 'Oval')
        brow_data['occasion'] = data.get('context', {}).get('occasion', 'work')
        brow_data['undertone'] = data.get('skin', {}).get('undertone', 'warm')
        brow_data['depth'] = data.get('skin', {}).get('depth', 'medium')
        
        return self.brow_engine.analyze_brows(brow_data)
    
    def _analyze_lips(self, data):
        """تحليل الشفاه"""
        if 'lips' not in data:
            return None
        
        lip_data = data['lips'].copy()
        lip_data['undertone'] = data.get('skin', {}).get('undertone', 'Warm')
        lip_data['depth'] = data.get('skin', {}).get('depth', 'Medium')
        lip_data['occasion'] = data.get('context', {}).get('occasion', 'work')
        
        return self.lip_engine.analyze_lips(lip_data)
    
    def _analyze_nose(self, data):
        """تحليل الأنف"""
        if 'nose' not in data:
            return None
        
        nose_data = data['nose'].copy()
        nose_data['undertone'] = data.get('skin', {}).get('undertone', 'Warm')
        nose_data['depth'] = data.get('skin', {}).get('depth', 'Medium')
        
        return self.nose_engine.analyze_nose(nose_data)
    
    def _analyze_face_contour(self, data):
        """تحليل الوجه (الكونتور/البلاشر)"""
        if 'face_shape' not in data:
            return None
        
        face_data = data['face_shape'].copy()
        face_data['undertone'] = data.get('skin', {}).get('undertone', 'Warm')
        face_data['depth'] = data.get('skin', {}).get('depth', 'Medium')
        face_data['fullness'] = data.get('context', {}).get('face_fullness', 'Full')
        face_data['eye_strategy'] = data.get('context', {}).get('eye_strategy', 'Monochromatic')
        face_data['occasion'] = data.get('context', {}).get('occasion', 'work')
        
        return self.face_engine.analyze_face(face_data)
    
    def _analyze_foundation(self, data):
        """تحليل الأساس والكونسيلر"""
        if 'skin' not in data:
            return None
        
        foundation_data = data['skin'].copy()
        
        return self.foundation_engine.analyze_foundation(foundation_data)
    
    def print_summary(self):
        """طباعة ملخص شامل للتوصيات"""
        print("\n" + "="*80)
        print("  MAKEUP RECOMMENDATIONS SUMMARY")
        print("="*80)
        
        # العيون
        if 'eyes' in self.complete_analysis and self.complete_analysis['eyes']:
            print("\n📍 EYES")
            print("-" * 80)
            eyes = self.complete_analysis['eyes']
            if isinstance(eyes, dict):
                if 'left' in eyes and eyes['left'] and 'recommendation' in eyes['left']:
                    rec = eyes['left'].get('recommendation', {})
                    if rec:
                        print(f"  Category: {rec.get('category_ar', 'N/A')} — {rec.get('style', 'N/A')}")
                if 'right' in eyes and eyes['right'] and 'recommendation' in eyes['right']:
                    rec = eyes['right'].get('recommendation', {})
                    if rec:
                        print(f"  Right Eye: {rec.get('style', 'N/A')}")
        
        # الحواجب
        if 'brows' in self.complete_analysis and self.complete_analysis['brows']:
            print("\n📍 BROWS")
            print("-" * 80)
            brows = self.complete_analysis['brows']
            if isinstance(brows, dict):
                if 'correction' in brows and brows['correction']:
                    print(f"  Arch Type:    {brows['correction'].get('arch_type', 'N/A')}")
                    print(f"  Tail:         {brows['correction'].get('tail_direction', 'N/A')}")
                if 'style' in brows and brows['style']:
                    print(f"  Style:        {brows['style'].get('style', 'N/A')}")
                if 'color' in brows and brows['color']:
                    print(f"  Color:        {brows['color'].get('tone', 'N/A')}")
        
        # الشفاه
        if 'lips' in self.complete_analysis and self.complete_analysis['lips']:
            print("\n📍 LIPS")
            print("-" * 80)
            lips = self.complete_analysis['lips']
            if isinstance(lips, dict):
                if 'shape' in lips and lips['shape']:
                    print(f"  Category:     {lips['shape'].get('name_ar', 'N/A')}")
                    print(f"  Correction:   {lips['shape'].get('correction', 'N/A')}")
                if 'color' in lips and lips['color']:
                    print(f"  Color Tone:   {lips['color'].get('colors', 'N/A')}")
                if 'occasion' in lips and lips['occasion']:
                    print(f"  Product:      {lips['occasion'].get('product', 'N/A')}")
        
        # الأنف
        if 'nose' in self.complete_analysis and self.complete_analysis['nose']:
            print("\n📍 NOSE")
            print("-" * 80)
            nose = self.complete_analysis['nose']
            if isinstance(nose, dict):
                if 'shape' in nose and nose['shape']:
                    print(f"  Shape:        {nose['shape'].get('name_ar', 'N/A')}")
                    print(f"  Technique:    {nose['shape'].get('technique', 'N/A')}")
                if 'contour' in nose and nose['contour']:
                    print(f"  Contour:      {nose['contour'].get('product', 'N/A')}")
        
        # الوجه
        if 'face' in self.complete_analysis and self.complete_analysis['face']:
            print("\n📍 FACE (Contour / Blush / Highlight)")
            print("-" * 80)
            face = self.complete_analysis['face']
            if isinstance(face, dict):
                if 'shape' in face and face['shape']:
                    shape_info = face['shape']
                    if isinstance(shape_info, dict):
                        print(f"  Face Shape:   {shape_info.get('name_ar', 'N/A')}")
                if 'sculpt' in face and face['sculpt']:
                    print(f"  Sculpt:       {face['sculpt'].get('placement', 'N/A')}")
                if 'blush' in face and face['blush']:
                    print(f"  Blush:        {face['blush'].get('placement', 'N/A')}")
                if 'color' in face and face['color']:
                    print(f"  Blush Color:  {face['color'].get('base_color', 'N/A')}")
        
        # الأساس
        if 'foundation' in self.complete_analysis and self.complete_analysis['foundation']:
            print("\n📍 FOUNDATION & CONCEALER")
            print("-" * 80)
            foundation = self.complete_analysis['foundation']
            if isinstance(foundation, dict):
                if 'shade' in foundation and foundation['shade']:
                    shade = foundation['shade']
                    if isinstance(shade, dict):
                        print(f"  Shade Range:  {shade.get('range', 'N/A')}")
                        print(f"  Descriptor:   {shade.get('descriptor', 'N/A')}")
                if 'formula' in foundation and foundation['formula']:
                    formula = foundation['formula']
                    if isinstance(formula, dict):
                        print(f"  Formula:      {formula.get('primary', 'N/A')}")
                if 'primer' in foundation and foundation['primer']:
                    primer = foundation['primer']
                    if isinstance(primer, dict):
                        print(f"  Primer:       {primer.get('type', 'N/A')}")
                if 'setting' in foundation and foundation['setting']:
                    setting = foundation['setting']
                    if isinstance(setting, dict):
                        print(f"  Setting:      {setting.get('method', 'N/A')}")
        
        print("\n" + "="*80 + "\n")
    
    def export_json(self, filepath):
        """تصدير التحليل الكامل إلى JSON"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.complete_analysis, f, indent=2, ensure_ascii=False, default=str)
        print(f"✓ Analysis exported to {filepath}")


# ══════════════════════════════════════════════════════
# EXAMPLE USAGE
# ══════════════════════════════════════════════════════

if __name__ == "__main__":
    
    # بيانات تحليل شاملة للعميل
    client_analysis = {
        'eyes': {
            'left': {
                'geo_shape': 'Round',
                'eye_type': 'Hooded',
                'combined': 'Round Hooded',
                'size': 'Normal',
                'corner': 'Neutral'
            },
            'right': {
                'geo_shape': 'Round',
                'eye_type': 'Normal',
                'combined': 'Round',
                'size': 'Normal',
                'corner': 'Neutral'
            },
            'inter_eye_ratio': 0.30
        },
        
        'brows': {
            'thickness': 'Medium',
            'length': 'Medium',
            'shape': 'Soft Arch',
            'position': 'Normal',
            'spacing': 'Normal',
            'symmetry': 'Symmetrical'
        },
        
        'lips': {
            'volume': 'Medium',
            'balance': 'Lower Fuller',
            'width': 'Average',
            'symmetry': 'Symmetrical',
            'cupid_bow': 'Soft',
            'corners': 'Neutral'
        },
        
        'nose': {
            'shape': 'Balanced'
        },
        
        'face_shape': {
            'shape': 'Oval',
            'votes': {'Oval': 10, 'Round': 2, 'Rectangular': 0}
        },
        
        'skin': {
            'undertone': 'Warm',
            'depth': 'Medium',
            'skin_type': 'Combination'
        },
        
        'context': {
            'occasion': 'evening',
            'face_fullness': 'Full',
            'eye_strategy': 'Monochromatic'
        }
    }
    
    # شغّل النظام الخبير
    expert_system = CompleteMakeupExpertSystem()
    results = expert_system.analyze_complete_face(client_analysis)
    
    # اطبع الملخص
    expert_system.print_summary()
    
    # صدّر النتائج
    expert_system.export_json('makeup_analysis_result.json')
    
    # اطبع النتائج الكاملة
    print("\nFULL ANALYSIS (JSON):")
    print(json.dumps(results, indent=2, ensure_ascii=False, default=str))