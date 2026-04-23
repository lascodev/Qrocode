import re
import json

def parse_menu(html_content):
    all_items = []
    current_section = "Unknown"
    current_category = "General"
    
    # Use re.finditer to find all relevant tags in order
    pattern = re.compile(r'<(h2 class="menu__title"|h3 class="menu-category__title"|h4 class="menu-subcategory__title"|h4 class="dish__title"|p class="dish__descr"|span class="dish__price")>(.*?)</', re.DOTALL)
    
    current_item = None
    
    for match in pattern.finditer(html_content):
        tag_type = match.group(1)
        content = match.group(2).replace('">', '').strip()
        
        if 'menu__title' in tag_type:
            current_section = content
            current_category = "General"
        elif 'category__title' in tag_type or 'subcategory__title' in tag_type:
            current_category = content
        elif 'dish__title' in tag_type:
            # Save previous item if it exists
            if current_item:
                all_items.append(current_item)
            current_item = {
                "section": current_section,
                "category": current_category,
                "name": content,
                "description": "",
                "price": ""
            }
        elif 'dish__descr' in tag_type:
            if current_item:
                current_item["description"] = content
        elif 'dish__price' in tag_type:
            if current_item:
                current_item["price"] = content
                # We can save it now or wait for next title. Saving now is safer if price is always last.
                all_items.append(current_item)
                current_item = None
                
    # Final cleanup if an item was left open
    if current_item:
        all_items.append(current_item)
        
    return all_items

if __name__ == "__main__":
    with open('menu_source.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    extracted = parse_menu(content)
    with open('extracted_menu.json', 'w', encoding='utf-8') as f:
        json.dump(extracted, f, indent=4, ensure_ascii=False)
    
    print(f"Extracted {len(extracted)} items.")
