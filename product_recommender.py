import json
import math
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def hex_to_rgb(hex_str):
    if not hex_str:
        return None
    hex_str = str(hex_str).lstrip('#')
    if len(hex_str) == 3:
        hex_str = ''.join([c*2 for c in hex_str])
    if len(hex_str) != 6:
        return None
    try:
        return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))
    except ValueError:
        return None

def calculate_color_distance(hex1, hex2):
    rgb1 = hex_to_rgb(hex1)
    rgb2 = hex_to_rgb(hex2)
    if not rgb1 or not rgb2:
        return float('inf')
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(rgb1, rgb2)))

class DynamicMakeupMatcher:
    def __init__(self,
                 analysis_json_path=os.path.join(BASE_DIR, "makeup_analysis.json"),
                 dataset_json_path=os.path.join(BASE_DIR, "makeup_data.json")):
        with open(analysis_json_path, 'r', encoding='utf-8') as f:
            self.analysis = json.load(f)

        with open(dataset_json_path, 'r', encoding='utf-8') as f:
            self.dataset = json.load(f)

        self.category_type_map = {
            "lipstick": ["lipstick", "lip", "lipstick_creme", "lipstick_matte"],
            "lip_liner": ["lip_liner", "lip liner", "liner", "lip_pencil"],
            "blush": ["blush"],
            "foundation": ["foundation"],
            "bronzer": ["bronzer", "contour"]
        }

    def extract_target_recommendations(self):
        targets = {'lipstick': [], 'lip_liner': [], 'blush': [], 'foundation': [], 'bronzer': []}
        analysis = self.analysis or {}
        expert = analysis.get('expert_output') or {}

        lips_section = expert.get('lips') or {}
        lips_color = lips_section.get('color') or {}
        for shade in lips_color.get('lipstick_shades') or []:
            if isinstance(shade, dict) and shade.get('hex'):
                targets['lipstick'].append({'target_name': shade.get('name'), 'hex': shade.get('hex')})
        for liner in lips_color.get('lip_liners') or []:
            if isinstance(liner, dict) and liner.get('hex'):
                targets['lip_liner'].append({'target_name': liner.get('name'), 'hex': liner.get('hex')})

        face_section = expert.get('face') or {}
        blush_info = face_section.get('blush') or {}
        color_details = blush_info.get('color_details') or {}
        
        primary = color_details.get('primary') or {}
        if primary.get('hex'):
            targets['blush'].append({'target_name': primary.get('name'), 'hex': primary.get('hex')})
            
        for shade in color_details.get('shades') or []:
            if isinstance(shade, dict) and shade.get('hex'):
                targets['blush'].append({'target_name': shade.get('name'), 'hex': shade.get('hex')})

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
        product_type = (product.get('product_type') or "").lower()
        name = (product.get('name') or "").lower()
        tags = [t.lower() for t in product.get('tag_list', []) if isinstance(t, str)]
        allowed_types = self.category_type_map.get(category, [])

        return (any(t in product_type for t in allowed_types) or
                any(t in name for t in allowed_types) or
                any(any(t in tag for t in allowed_types) for tag in tags))

    def get_recommendations(self, top_n_per_category=3):
        targets = self.extract_target_recommendations()
        matched_results = {}

        for category, target_colors in targets.items():
            if not target_colors:
                continue

            category_matches = []
            filtered_dataset = [p for p in self.dataset if self._product_matches_category(p, category)]

            for product in filtered_dataset:
                product_colors = product.get('product_colors', [])
                if not product_colors:
                    continue

                # معالجة تنسيق السعر بدقة
                price_val = product.get('price')
                price_sign = product.get('price_sign') or '$'
                
                if price_val in [None, '', 0, '0', '0.0', 0.0]:
                    formatted_price = "Not available"
                else:
                    formatted_price = f"{price_val} {price_sign}".strip()

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
                            'price': formatted_price,
                            'matched_shade_name': color.get('colour_name'),
                            'matched_shade_hex': prod_hex,
                            'recommended_shade_target': target['target_name'],
                            'recommended_target_hex': target_hex,
                            'match_score_distance': round(distance, 2),
                            'image_link': product.get('image_link'),
                            'product_link': product.get('product_link'),
                            'tags': product.get('tag_list', [])
                        })

            category_matches.sort(key=lambda x: x['match_score_distance'])

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