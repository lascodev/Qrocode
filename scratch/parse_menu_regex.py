import re
import json

def parse_menu(html_content):
    # This is a rough parser using regex
    sections = re.split(r'<h2 class="menu__title">', html_content)
    all_items = []
    
    for section_block in sections[1:]:
        section_name_match = re.search(r'^(.*?)</h2>', section_block, re.DOTALL)
        if not section_name_match: continue
        section_name = section_name_match.group(1).strip()
        
        # Split by categories
        categories = re.split(r'<h[34] class="category__title|subcategory__title">', section_block)
        for cat_block in categories[1:]:
            cat_name_match = re.search(r'^(.*?)<', cat_block, re.DOTALL)
            cat_name = cat_name_match.group(1).replace('">', '').strip() if cat_name_match else "General"
            
            # Find items in this category
            items = re.findall(r'<div id="dish-\d+"(.*?)</div>\s*</div>\s*</div>', cat_block, re.DOTALL)
            for item_html in items:
                name_match = re.search(r'<h4 class="dish__title">\s*(.*?)\s*</h4>', item_html, re.DOTALL)
                if not name_match: continue
                name = name_match.group(1).strip()
                
                descr_match = re.search(r'<p class="dish__descr">(.*?)</p>', item_html, re.DOTALL)
                description = descr_match.group(1).strip() if descr_match else ""
                
                price_match = re.search(r'<span class="dish__price">(.*?)</span>', item_html, re.DOTALL)
                price = price_match.group(1).strip() if price_match else ""
                
                all_items.append({
                    "section": section_name,
                    "category": cat_name,
                    "name": name,
                    "description": description,
                    "price": price
                })
                
    return all_items

if __name__ == "__main__":
    with open('menu_source.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    extracted = parse_menu(content)
    with open('extracted_menu.json', 'w', encoding='utf-8') as f:
        json.dump(extracted, f, indent=4, ensure_ascii=False)
    
    print(f"Extracted {len(extracted)} items.")
