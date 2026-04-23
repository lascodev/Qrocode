import json
import re

def slugify(text):
    text = text.lower()
    text = re.sub(r'[àáâãäå]', 'a', text)
    text = re.sub(r'[èéêë]', 'e', text)
    text = re.sub(r'[ìíîï]', 'i', text)
    text = re.sub(r'[òóôõö]', 'o', text)
    text = re.sub(r'[ùúûü]', 'u', text)
    text = re.sub(r'[ç]', 'c', text)
    text = re.sub(r'[^a-z0-9]', '_', text)
    return re.sub(r'_+', '_', text).strip('_')

def map_category(cat_name, section_name):
    cat_lower = cat_name.lower()
    if section_name == "Tapas":
        return "tapas"
    if "bière" in cat_lower:
        return "biere"
    if "cocktail" in cat_lower:
        return "cocktails"
    if "mocktail" in cat_lower:
        return "mocktails"
    if "whisky" in cat_lower or "glen" in cat_lower:
        return "whisky"
    if "rhum" in cat_lower:
        return "rhum"
    if "gin" in cat_lower:
        return "gin"
    if "vodka" in cat_lower:
        return "vodka"
    if "cognac" in cat_lower or "armagnac" in cat_lower:
        return "cognac"
    if "vin" in cat_lower or "rouge" in cat_lower or "blanc" in cat_lower or "rosé" in cat_lower or "champagne" in cat_lower or "piscine" in cat_lower or "coupe" in cat_lower or "chateau" in cat_lower or "chianti" in cat_lower or "castel" in cat_lower or "nederburg" in cat_lower or "beyerskloof" in cat_lower:
        return "vins"
    if "apéritif" in cat_lower:
        return "aperitifs"
    if "digestif" in cat_lower:
        return "digestifs"
    if "boissons non alcoolisées" in cat_lower:
        return "softs"
    return "softs"

def get_image(cat_slug):
    images = {
        "tapas": "https://loremflickr.com/320/320/tapas,snack?lock=1",
        "biere": "https://loremflickr.com/320/320/beer,glass?lock=1",
        "cocktails": "https://loremflickr.com/320/320/cocktail,glass?lock=1",
        "mocktails": "https://loremflickr.com/320/320/mocktail,juice?lock=1",
        "whisky": "https://loremflickr.com/320/320/whisky?lock=1",
        "rhum": "https://loremflickr.com/320/320/rum,glass?lock=1",
        "gin": "https://loremflickr.com/320/320/gin,tonic?lock=1",
        "vodka": "https://loremflickr.com/320/320/vodka,glass?lock=1",
        "cognac": "https://loremflickr.com/320/320/cognac,glass?lock=1",
        "vins": "https://loremflickr.com/320/320/wine,glass?lock=1",
        "softs": "https://loremflickr.com/320/320/soda,glass?lock=1",
        "aperitifs": "https://loremflickr.com/320/320/aperitif,glass?lock=1",
        "digestifs": "https://loremflickr.com/320/320/digestif,glass?lock=1"
    }
    return images.get(cat_slug, "https://loremflickr.com/320/320/drink?lock=1")

if __name__ == "__main__":
    with open('extracted_menu.json', 'r', encoding='utf-8') as f:
        items = json.load(f)
    
    products = []
    for i in items:
        cat_slug = map_category(i['category'], i['section'])
        # If it's a signature cocktail or champagne, mark as premium
        is_premium = 1 if ("signature" in i['category'].lower() or "champagne" in i['category'].lower() or "blue label" in i['name'].lower()) else 0
        
        # Format description: concatenate category and description if they are different
        full_desc = i['description']
        if i['category'] != "General" and i['category'] not in ["Tapas", "Cocktails"]:
            if full_desc:
                full_desc = f"{i['category']} - {full_desc}"
            else:
                full_desc = i['category']
        
        products.append((
            i['name'],
            cat_slug,
            i['price'],
            get_image(cat_slug),
            is_premium,
            full_desc
        ))
    
    # Generate the init_db.py content or at least the products list
    print("products = [")
    for p in products:
        print(f"    {p},")
    print("]")
