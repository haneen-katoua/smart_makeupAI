import json
import math
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def hex_to_rgb(hex_str):
    """تحويل كود HEX إلى كود RGB"""
    if not hex_str:
        return None
    hex_str = hex_str.lstrip('#')
    if len(hex_str) != 6:
        return None
    try:
        return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))
    except ValueError:
        return None

def calculate_color_distance(hex1, hex2):
    """حساب التقارب البصري بين لونين باستخدام Euclidean Distance على RGB"""
    rgb1 = hex_to_rgb(hex1)
    rgb2 = hex_to_rgb(hex2)
    if not rgb1 or not rgb2:
        return float('inf')
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(rgb1, rgb2)))


class DynamicMakeupMatcher:
    def __init__(self,
                 analysis_json_path=os.path.join(BASE_DIR, "makeup_analysis.json"),
                 dataset_json_path=os.path.join(BASE_DIR, "makeup_data.json")):
        # تحميل ملفات التحليل والداتا
        with open(analysis_json_path, 'r', encoding='utf-8') as f:
            self.analysis = json.load(f)

        with open(dataset_json_path, 'r', encoding='utf-8') as f:
            self.dataset = json.load(f)

        # خريطة ربط بين الفئات الداخلية وأنواع المنتجات في الداتا
        self.category_type_map = {
            "lipstick": ["lipstick", "lip", "lipstick_creme", "lipstick_matte"],
            "lip_liner": ["lip_liner", "lip liner", "liner", "lip_pencil"],
            "blush": ["blush"],
            "foundation": ["foundation"],
            "bronzer": ["bronzer", "contour"]
        }

    def extract_target_recommendations(self):
        targets = {
        'lipstick': [],
        'lip_liner': [],
        'blush': [],
        'foundation': [],
        'bronzer': []
    }

        analysis = self.analysis or {}
        expert = analysis.get('expert_output') or {}

        lips_section = expert.get('lips') or {}
        lips_color = lips_section.get('color') or {}
        for shade in lips_color.get('lipstick_shades') or []:
            if isinstance(shade, dict) and shade.get('hex'):
                targets['lipstick'].append({
                    'target_name': shade.get('name'),
                    'hex': shade.get('hex')
                })
        for liner in lips_color.get('lip_liners') or []:
            if isinstance(liner, dict) and liner.get('hex'):
                targets['lip_liner'].append({
                    'target_name': liner.get('name'),
                    'hex': liner.get('hex')
                })

        face_section = expert.get('face') or {}
        blush_info = face_section.get('blush') or {}
        color_details = blush_info.get('color_details') or {}
        
        primary = color_details.get('primary') or {}
        if primary.get('hex'):
            targets['blush'].append({
                'target_name': primary.get('name'),
                'hex': primary.get('hex')
            })
            
        for shade in color_details.get('shades') or []:
            if isinstance(shade, dict) and shade.get('hex'):
                targets['blush'].append({
                    'target_name': shade.get('name'),
                    'hex': shade.get('hex')
                })

        sculpt_info = face_section.get('sculpt') or {}
        if sculpt_info.get('hex'):
            targets['bronzer'].append({
                'target_name': sculpt_info.get('shade_descriptor', 'Sculpt Shade'),
                'hex': sculpt_info.get('hex')
            })

        foundation_section = expert.get('foundation') or {}
        found_shade = foundation_section.get('shade') or {}
        if found_shade.get('hex'):
            targets['foundation'].append({
                'target_name': found_shade.get('descriptor', 'Foundation Shade'),
                'hex': found_shade.get('hex')
            })

        return targets

    def _product_matches_category(self, product, category):
        """فلترة ذكية لربط المنتج بالفئة المطلوبة"""
        product_type = (product.get('product_type') or "").lower()
        name = (product.get('name') or "").lower()
        tags = [t.lower() for t in product.get('tag_list', [])]

        allowed_types = self.category_type_map.get(category, [])

        # لو النوع موجود ومطابق
        if any(t in product_type for t in allowed_types):
            return True

        # لو الاسم فيه كلمة من الفئة
        if any(t in name for t in allowed_types):
            return True

        # لو التاجز فيها كلمة من الفئة
        if any(any(t in tag for t in allowed_types) for tag in tags):
            return True

        return False

    def get_recommendations(self, top_n_per_category=3):
        """مطابقة المنتجات مع الألوان وترتيب أفضل النتائج لكل فئة"""
        targets = self.extract_target_recommendations()
        matched_results = {}

        for category, target_colors in targets.items():
            if not target_colors:
                continue

            category_matches = []

            # فلترة الداتا حسب الفئة بشكل ذكي
            filtered_dataset = [
                p for p in self.dataset
                if self._product_matches_category(p, category)
            ]

            for product in filtered_dataset:
                product_colors = product.get('product_colors', [])
                if not product_colors:
                    continue

                for target in target_colors:
                    target_hex = target['hex']
                    if not target_hex:
                        continue

                    for color in product_colors:
                        prod_hex = color.get('hex_value')
                        if not prod_hex:
                            continue

                        distance = calculate_color_distance(target_hex, prod_hex)

                        category_matches.append({
                            'product_id': product.get('id'),
                            'brand': product.get('brand'),
                            'name': product.get('name'),
                            'price': f"{product.get('price', '')} {product.get('price_sign', '$')}".strip(),
                            'matched_shade_name': color.get('colour_name'),
                            'matched_shade_hex': prod_hex,
                            'recommended_shade_target': target['target_name'],
                            'recommended_target_hex': target_hex,
                            'match_score_distance': round(distance, 2),
                            'image_link': product.get('image_link'),
                            'product_link': product.get('product_link'),
                            'tags': product.get('tag_list', [])
                        })

            # ترتيب النتائج من الأقرب للأبعد
            category_matches.sort(key=lambda x: x['match_score_distance'])

            # إزالة التكرار مع الاحتفاظ بأفضل نتيجة لكل منتج
            unique_products = []
            seen_ids = set()
            for item in category_matches:
                if item['product_id'] not in seen_ids:
                    seen_ids.add(item['product_id'])
                    unique_products.append(item)
                if len(unique_products) >= top_n_per_category:
                    break

            matched_results[category] = unique_products

        return matched_results


if __name__ == "__main__":
    matcher = DynamicMakeupMatcher()
    results = matcher.get_recommendations(top_n_per_category=3)
    print(json.dumps(results, indent=4, ensure_ascii=False))
