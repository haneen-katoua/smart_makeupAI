# -*- coding: utf-8 -*-
"""
data_transformer.py — تحويل البيانات من الهيكل الحالي إلى makeup_analysis.json
===============================================================================

هذا الملف يحتوي على دالة تحويل البيانات بحيث تطابق هيكل makeup_analysis.json
المطلوب من الزملاء (مع hex و rgb في كل مكان و eyeshadow_palettes منظمة).
"""

import json
from typing import Dict, List, Any, Optional
from colorsys import rgb_to_hsv


class MakeupDataTransformer:
    """تحويل بيانات المكياج إلى الصيغة المطلوبة"""
    
    def __init__(self):
        self.result = {}
        self.skin_analysis = {}
    
    def transform(self, current_data: Dict) -> Dict:
        """تحويل البيانات الحالية إلى الهيكل المطلوب"""
        try:
            # حفظ skin_analysis للاستخدام لاحقاً
            self.skin_analysis = current_data.get('skin_analysis', {})
            
            # نسخ face_analysis و skin_analysis كما هي
            self.result['face_analysis'] = current_data.get('face_analysis', {})
            self.result['skin_analysis'] = self.skin_analysis
            
            # تحويل expert_output إلى الهيكل المطلوب
            expert_output = current_data.get('expert_output', {})
            self.result['expert_output'] = self._transform_expert_output(expert_output)
            
            # نسخ الحقول الإضافية
            self.result['occasion'] = current_data.get('occasion', 'evening')
            
            # معالجة eyeshadow_palettes
            eyeshadow = current_data.get('eyeshadow_palettes', {})
            if eyeshadow and isinstance(eyeshadow, dict) and len(eyeshadow) > 0:
                # إذا كانت موجودة وليست فاضية، استخدمها
                self.result['eyeshadow_palettes'] = self._ensure_eyeshadow_structure(eyeshadow)
            else:
                # إذا كانت فاضية أو غير موجودة، وليد لوحات جديدة
                self.result['eyeshadow_palettes'] = self._generate_eyeshadow_palettes()
            
            return self.result
        except Exception as e:
            print(f"❌ خطأ في تحويل البيانات: {e}")
            return current_data
    
    def _transform_expert_output(self, expert_output: Dict) -> Dict:
        """تحويل expert_output إلى الهيكل المطلوب"""
        transformed = {}
        
        # تحويل كل قسم
        transformed['eyes'] = self._ensure_eyes_structure(expert_output.get('eyes', {}))
        transformed['brows'] = self._ensure_brows_structure(expert_output.get('brows', {}))
        transformed['lips'] = self._ensure_lips_structure(expert_output.get('lips', {}))
        transformed['nose'] = self._ensure_nose_structure(expert_output.get('nose', {}))
        transformed['face'] = self._ensure_face_structure(expert_output.get('face', {}))
        transformed['foundation'] = self._ensure_foundation_structure(expert_output.get('foundation', {}))
        
        return transformed
    
    def _ensure_eyes_structure(self, eyes: Dict) -> Dict:
        """التأكد من أن eyes يتبع الهيكل الصحيح"""
        if not eyes:
            return {"left": {}, "right": {}}
        
        result = {}
        
        if 'left_eye' in eyes:
            result['left'] = eyes['left_eye']
        elif 'left' in eyes:
            result['left'] = eyes['left']
        else:
            result['left'] = {}
        
        if 'right_eye' in eyes:
            result['right'] = eyes['right_eye']
        elif 'right' in eyes:
            result['right'] = eyes['right']
        else:
            result['right'] = {}
        
        return result
    
    def _ensure_brows_structure(self, brows: Dict) -> Dict:
        """التأكد من أن brows يتبع الهيكل الصحيح"""
        if not brows:
            return {
                "correction": {},
                "style": {},
                "color": None,
                "recommendation": None
            }
        
        result = {
            "correction": brows.get('correction', {}),
            "style": brows.get('style', {}),
            "color": brows.get('color'),
            "recommendation": brows.get('recommendation')
        }
        
        return result
    
    def _ensure_lips_structure(self, lips: Dict) -> Dict:
        """التأكد من أن lips يتبع الهيكل الصحيح"""
        if not lips:
            return {
                "shape": {},
                "color": None,
                "occasion": None,
                "recommendation": None
            }
        
        result = {
            "shape": lips.get('shape', {}),
            "color": self._ensure_color_has_hex_rgb(lips.get('color')),
            "occasion": lips.get('occasion'),
            "recommendation": lips.get('recommendation')
        }
        
        return result
    
    def _ensure_nose_structure(self, nose: Dict) -> Dict:
        """التأكد من أن nose يتبع الهيكل الصحيح"""
        if not nose:
            return {
                "shape": {},
                "map": None,
                "contour": None,
                "highlight": None,
                "recommendation": None
            }
        
        result = {
            "shape": nose.get('shape', {}),
            "map": nose.get('map'),
            "contour": self._ensure_color_has_hex_rgb(nose.get('contour')),
            "highlight": self._ensure_color_has_hex_rgb(nose.get('highlight')),
            "recommendation": nose.get('recommendation')
        }
        
        return result
    
    def _ensure_face_structure(self, face: Dict) -> Dict:
        """التأكد من أن face يتبع الهيكل الصحيح"""
        if not face:
            return {
                "shape": {},
                "sculpt": None,
                "blush": None,
                "highlight": None,
                "color": None,
                "texture": None,
                "recommendation": None
            }
        
        result = {
            "shape": face.get('shape', {}),
            "sculpt": self._ensure_color_has_hex_rgb(face.get('sculpt')),
            "blush": self._ensure_color_has_hex_rgb(face.get('blush')),
            "highlight": self._ensure_color_has_hex_rgb(face.get('highlight')),
            "color": face.get('color'),
            "texture": face.get('texture'),
            "recommendation": face.get('recommendation')
        }
        
        return result
    
    def _ensure_foundation_structure(self, foundation: Dict) -> Dict:
        """التأكد من أن foundation يتبع الهيكل الصحيح"""
        if not foundation:
            return {
                "shade": None,
                "formula": None,
                "concealer": None,
                "primer": None,
                "setting": None,
                "recommendation": None
            }
        
        result = {
            "shade": self._ensure_color_has_hex_rgb(foundation.get('shade')),
            "formula": foundation.get('formula'),
            "concealer": self._ensure_color_has_hex_rgb(foundation.get('concealer')),
            "primer": foundation.get('primer'),
            "setting": foundation.get('setting'),
            "recommendation": foundation.get('recommendation')
        }
        
        return result
    
    def _ensure_color_has_hex_rgb(self, color_obj: Optional[Dict]) -> Optional[Dict]:
        """التأكد من أن كل كائن لون يحتوي على hex و rgb"""
        if not color_obj or not isinstance(color_obj, dict):
            return color_obj
        
        result = color_obj.copy()
        
        # تحويل rgb من string إلى list إذا لزم
        if 'rgb' in result:
            if isinstance(result['rgb'], str):
                try:
                    result['rgb'] = json.loads(result['rgb'])
                except:
                    pass
        
        # التأكد من وجود hex
        if 'hex' not in result and 'color_hex' in result:
            result['hex'] = result.pop('color_hex')
        
        # معالجة lipstick_shades و lip_liners
        if 'lipstick_shades' in result and result['lipstick_shades']:
            result['lipstick_shades'] = [
                self._ensure_shade_has_hex_rgb(shade) 
                for shade in result['lipstick_shades']
            ]
        
        if 'lip_liners' in result and result['lip_liners']:
            result['lip_liners'] = [
                self._ensure_shade_has_hex_rgb(liner) 
                for liner in result['lip_liners']
            ]
        
        return result
    
    def _ensure_shade_has_hex_rgb(self, shade: Dict) -> Dict:
        """التأكد من أن كل shade يحتوي على hex و rgb"""
        if not shade:
            return shade
        
        result = shade.copy()
        
        # تحويل rgb من string إلى list إذا لزم
        if 'rgb' in result and isinstance(result['rgb'], str):
            try:
                result['rgb'] = json.loads(result['rgb'])
            except:
                pass
        
        return result
    
    def _ensure_eyeshadow_structure(self, eyeshadow: Dict) -> Dict:
        """التأكد من أن eyeshadow_palettes يحتوي على البيانات الصحيحة"""
        if not eyeshadow or not isinstance(eyeshadow, dict):
            return {}
        
        result = {}
        
        # معالجة كل لوحة
        for palette_name, shades in eyeshadow.items():
            if isinstance(shades, list) and len(shades) > 0:
                result[palette_name] = [
                    self._ensure_shade_has_hex_rgb_hue(shade)
                    for shade in shades
                ]
            else:
                result[palette_name] = shades
        
        return result
    
    def _ensure_shade_has_hex_rgb_hue(self, shade: Dict) -> Dict:
        """التأكد من أن كل shade يحتوي على hex، rgb و hue"""
        if not shade or not isinstance(shade, dict):
            return shade
        
        result = shade.copy()
        
        # تحويل rgb من string إلى list
        if 'rgb' in result and isinstance(result['rgb'], str):
            try:
                result['rgb'] = json.loads(result['rgb'])
            except:
                pass
        
        # إضافة hue إذا لم يكن موجوداً
        if 'hue' not in result and 'rgb' in result and isinstance(result['rgb'], list):
            try:
                r, g, b = result['rgb']
                h, s, v = rgb_to_hsv(r/255, g/255, b/255)
                result['hue'] = int(h * 360)
            except:
                result['hue'] = 0
        
        return result
    
    def _generate_eyeshadow_palettes(self) -> Dict:
        """
        توليد لوحات ظلال عيون بناءً على تحليل البشرة
        إذا لم تكن موجودة
        """
        # استخرج معلومات البشرة
        skin_depth = self.skin_analysis.get('skin_depth', 'Medium')
        undertone = self.skin_analysis.get('undertone', 'Neutral')
        
        # حدد المجموعات اللونية بناءً على البشرة
        palettes = {}
        
        # Neutral Palette (محايد)
        if undertone in ['Warm', 'Neutral']:
            palettes['Neutral Palette'] = [
                {
                    "role": "Highlight",
                    "hex": "#FFF7EB",
                    "rgb": [255, 247, 235],
                    "hue": 18
                },
                {
                    "role": "Highlight",
                    "hex": "#D2C8AD",
                    "rgb": [210, 200, 173],
                    "hue": 22
                },
                {
                    "role": "Highlight",
                    "hex": "#C3AE99",
                    "rgb": [195, 174, 153],
                    "hue": 15
                },
                {
                    "role": "Base",
                    "hex": "#C8AE7A",
                    "rgb": [200, 174, 122],
                    "hue": 20
                },
                {
                    "role": "Base",
                    "hex": "#B4A24A",
                    "rgb": [180, 162, 74],
                    "hue": 25
                },
                {
                    "role": "Base",
                    "hex": "#DCDC79",
                    "rgb": [220, 220, 121],
                    "hue": 30
                },
                {
                    "role": "Sculpt",
                    "hex": "#5A4938",
                    "rgb": [90, 73, 56],
                    "hue": 15
                },
                {
                    "role": "Sculpt",
                    "hex": "#8C5B3A",
                    "rgb": [140, 91, 58],
                    "hue": 12
                },
                {
                    "role": "Sculpt",
                    "hex": "#463025",
                    "rgb": [70, 48, 37],
                    "hue": 10
                },
                {
                    "role": "Accent",
                    "hex": "#E6DA9E",
                    "rgb": [230, 218, 158],
                    "hue": 25
                },
                {
                    "role": "Accent",
                    "hex": "#B49566",
                    "rgb": [180, 149, 102],
                    "hue": 18
                },
                {
                    "role": "Accent",
                    "hex": "#BEBE5D",
                    "rgb": [190, 190, 93],
                    "hue": 30
                }
            ]
        
        # Cool Palette (بارد)
        if undertone in ['Cool', 'Pink']:
            palettes['Cool Palette'] = [
                {
                    "role": "Highlight",
                    "hex": "#FFF3FF",
                    "rgb": [255, 243, 255],
                    "hue": 300
                },
                {
                    "role": "Highlight",
                    "hex": "#E8D5E8",
                    "rgb": [232, 213, 232],
                    "hue": 300
                },
                {
                    "role": "Highlight",
                    "hex": "#D5C8E0",
                    "rgb": [213, 200, 224],
                    "hue": 270
                },
                {
                    "role": "Base",
                    "hex": "#C8B5D1",
                    "rgb": [200, 181, 209],
                    "hue": 280
                },
                {
                    "role": "Base",
                    "hex": "#B5A5C0",
                    "rgb": [181, 165, 192],
                    "hue": 270
                },
                {
                    "role": "Base",
                    "hex": "#D0B8D5",
                    "rgb": [208, 184, 213],
                    "hue": 290
                },
                {
                    "role": "Sculpt",
                    "hex": "#5A4861",
                    "rgb": [90, 72, 97],
                    "hue": 280
                },
                {
                    "role": "Sculpt",
                    "hex": "#6B5B7A",
                    "rgb": [107, 91, 122],
                    "hue": 270
                },
                {
                    "role": "Sculpt",
                    "hex": "#453850",
                    "rgb": [69, 56, 80],
                    "hue": 280
                },
                {
                    "role": "Accent",
                    "hex": "#E0D5E8",
                    "rgb": [224, 213, 232],
                    "hue": 290
                },
                {
                    "role": "Accent",
                    "hex": "#C0A8D0",
                    "rgb": [192, 168, 208],
                    "hue": 280
                },
                {
                    "role": "Accent",
                    "hex": "#B5A5C5",
                    "rgb": [181, 165, 197],
                    "hue": 270
                }
            ]
        
        # Bronze/Warm Palette (دافئ)
        if undertone == 'Warm' or len(palettes) == 0:
            if 'Neutral Palette' not in palettes:  # تجنب التكرار
                palettes['Warm Palette'] = [
                    {
                        "role": "Highlight",
                        "hex": "#FFF8E7",
                        "rgb": [255, 248, 231],
                        "hue": 35
                    },
                    {
                        "role": "Highlight",
                        "hex": "#FFD9B3",
                        "rgb": [255, 217, 179],
                        "hue": 20
                    },
                    {
                        "role": "Base",
                        "hex": "#E8B88A",
                        "rgb": [232, 184, 138],
                        "hue": 25
                    },
                    {
                        "role": "Base",
                        "hex": "#D4A574",
                        "rgb": [212, 165, 116],
                        "hue": 28
                    },
                    {
                        "role": "Sculpt",
                        "hex": "#8B5A3C",
                        "rgb": [139, 90, 60],
                        "hue": 15
                    },
                    {
                        "role": "Sculpt",
                        "hex": "#A0522D",
                        "rgb": [160, 82, 45],
                        "hue": 12
                    },
                    {
                        "role": "Accent",
                        "hex": "#FF9F43",
                        "rgb": [255, 159, 67],
                        "hue": 32
                    }
                ]
        
        return palettes if palettes else {}


def apply_transformation_to_results(results: Dict) -> Dict:
    """
    تطبيق التحويل على النتائج قبل الحفظ
    هذه الدالة تُستخدم في complete_makeup_pipeline.py
    """
    try:
        transformer = MakeupDataTransformer()
        return transformer.transform(results)
    except Exception as e:
        print(f"⚠️ تحذير: فشل التحويل: {e}")
        return results


if __name__ == "__main__":
    # مثال على الاستخدام
    sample = {
        "face_analysis": {"success": True},
        "skin_analysis": {
            "skin_depth": "Fair",
            "undertone": "Warm"
        },
        "expert_output": {},
        "occasion": "wedding",
        "eyeshadow_palettes": {}
    }
    
    transformer = MakeupDataTransformer()
    result = transformer.transform(sample)
    
    print("✅ تم التحويل!")
    print(f"✓ eyeshadow_palettes الآن يحتوي على {len(result['eyeshadow_palettes'])} لوحات")
