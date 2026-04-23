import sys
import json
from bs4 import BeautifulSoup

def parse_menu(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    menu_data = []

    # Find the main sections
    menus = soup.find_all('div', class_='menu-wrap')
    
    for menu in menus:
        # Get section title (Tapas, The Peat Bar, etc.)
        section_title_elem = menu.find('h2', class_='menu__title')
        if not section_title_elem:
            continue
        section_title = section_title_elem.get_text(strip=True)
        
        # Find categories within the section
        categories = menu.find_all('div', class_='category-wrap')
        for cat in categories:
            cat_title_elem = cat.find('h3', class_='category__title')
            cat_title = cat_title_elem.get_text(strip=True) if cat_title_elem else "General"
            
            # Find subcategories if any
            sub_cats = cat.find_all('div', class_='subcategory-wrap')
            if not sub_cats:
                # Items might be directly under category
                items = cat.find_all('div', class_='dish-wrap')
                for item in items:
                    data = extract_item_info(item, section_title, cat_title)
                    if data:
                        menu_data.append(data)
            else:
                for sub_cat in sub_cats:
                    sub_cat_title_elem = sub_cat.find('h4', class_='subcategory__title')
                    sub_cat_title = sub_cat_title_elem.get_text(strip=True) if sub_cat_title_elem else cat_title
                    
                    items = sub_cat.find_all('div', class_='dish-wrap')
                    for item in items:
                        data = extract_item_info(item, section_title, sub_cat_title)
                        if data:
                            menu_data.append(data)
                            
    return menu_data

def extract_item_info(item, section, category):
    title_elem = item.find('h4', class_='dish__title')
    if not title_elem:
        # Sometimes it's a different structure
        return None
    
    name = title_elem.get_text(strip=True)
    
    descr_elem = item.find('p', class_='dish__descr')
    description = descr_elem.get_text(strip=True) if descr_elem else ""
    
    price_elem = item.find('span', class_='dish__price')
    price = price_elem.get_text(strip=True) if price_elem else ""
    
    # Simple image check
    img_elem = item.find('img')
    image_url = img_elem['src'] if img_elem and 'src' in img_elem.attrs else ""

    return {
        "section": section,
        "category": category,
        "name": name,
        "description": description,
        "price": price,
        "image_url": image_url
    }

if __name__ == "__main__":
    with open('menu_source.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    extracted = parse_menu(content)
    with open('extracted_menu.json', 'w', encoding='utf-8') as f:
        json.dump(extracted, f, indent=4, ensure_ascii=False)
    
    print(f"Extracted {len(extracted)} items.")
