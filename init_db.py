import sqlite3
import os
import bcrypt

DATABASE_URL = os.environ.get('POSTGRES_URL') or os.environ.get('DATABASE_URL')

def get_db_connection():
    if DATABASE_URL:
        import psycopg2
        url = DATABASE_URL
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return psycopg2.connect(url)
    else:
        return sqlite3.connect("database.db")

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Drop tables if they exist for a clean start (careful in production!)
    if DATABASE_URL:
        cursor.execute("DROP TABLE IF EXISTS users CASCADE")
        cursor.execute("DROP TABLE IF EXISTS products CASCADE")
    else:
        cursor.execute("DROP TABLE IF EXISTS users")
        cursor.execute("DROP TABLE IF EXISTS products")

    # Create Users Table
    user_table_query = '''
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    '''
    if not DATABASE_URL:
        user_table_query = user_table_query.replace('SERIAL', 'INTEGER').replace('PRIMARY KEY', 'PRIMARY KEY AUTOINCREMENT')
    
    cursor.execute(user_table_query)

    # Create Products Table
    product_table_query = '''
        CREATE TABLE products (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price TEXT NOT NULL,
            image_url TEXT NOT NULL,
            is_premium BOOLEAN NOT NULL DEFAULT FALSE,
            description TEXT
        )
    '''
    if not DATABASE_URL:
        product_table_query = product_table_query.replace('SERIAL', 'INTEGER').replace('PRIMARY KEY', 'PRIMARY KEY AUTOINCREMENT').replace('FALSE', '0')
    
    cursor.execute(product_table_query)

    # Seed Admin User (password: admin123)
    admin_pw = bcrypt.hashpw(b"admin123", bcrypt.gensalt()).decode('utf-8')
    placeholder = '%s' if DATABASE_URL else '?'
    cursor.execute(f"INSERT INTO users (username, password, role) VALUES ({placeholder}, {placeholder}, {placeholder})", 
                   ("admin", admin_pw, "admin"))
    
    # Seed Client User (password: client123)
    client_pw = bcrypt.hashpw(b"client123", bcrypt.gensalt()).decode('utf-8')
    cursor.execute(f"INSERT INTO users (username, password, role) VALUES ({placeholder}, {placeholder}, {placeholder})", 
                   ("client", client_pw, "client"))

    # Seed Initial Products
    products = [
        ('Mini brochette de poulet', 'tapas', '2000,00 CFA', 'https://loremflickr.com/320/320/tapas,snack?lock=1', False, 'Mini brochettes'),
        ('Mini brochette de viande', 'tapas', '3000,00 CFA', 'https://loremflickr.com/320/320/tapas,snack?lock=1', False, 'Mini brochettes'),
        ('Mini brochette de crevettes', 'tapas', '4500,00 CFA', 'https://loremflickr.com/320/320/tapas,snack?lock=1', False, 'Mini brochettes'),
        ('Calamar frit', 'tapas', '4000,00 CFA', 'https://loremflickr.com/320/320/tapas,snack?lock=1', False, 'Mini brochettes'),
        ('Ardoise du chef', 'tapas', '19000,00 CFA', 'https://loremflickr.com/320/320/tapas,snack?lock=1', False, 'Ardoises'),
        ('Ardoise de l’océan', 'tapas', '20000,00 CFA', 'https://loremflickr.com/320/320/tapas,snack?lock=1', False, 'Ardoises - Calamar, crevette, tartare a la tahitienne, fish crunch'),
        ('Ardoise Mix Grill', 'tapas', '23000,00 CFA', 'https://loremflickr.com/320/320/tapas,snack?lock=1', False, 'Ardoises - Poitrine fumée, toulouse, viande, poulet, wings, ribs'),
        ('Wings', 'tapas', '2500,00 CFA', 'https://loremflickr.com/320/320/tapas,snack?lock=1', False, 'Frying'),
        ('Pilons', 'tapas', '3000,00 CFA', 'https://loremflickr.com/320/320/tapas,snack?lock=1', False, 'Frying'),
        ('Boulettes de porcs pimentées', 'tapas', '3500,00 CFA', 'https://loremflickr.com/320/320/tapas,snack?lock=1', False, 'Frying'),
        ('Hot dog', 'tapas', '4000,00 CFA', 'https://loremflickr.com/320/320/tapas,snack?lock=1', False, 'Burgers'),
        ('Hamburger frite', 'tapas', '5500,00 CFA', 'https://loremflickr.com/320/320/tapas,snack?lock=1', False, 'Burgers'),
        ('Cheeseburger frite', 'tapas', '6500,00 CFA', 'https://loremflickr.com/320/320/tapas,snack?lock=1', False, 'Burgers'),
        ('Regab', 'biere', '1500,00 CFA', 'https://loremflickr.com/320/320/beer,glass?lock=1', False, 'Bières'),
        ('Chill', 'biere', '1000,00 CFA', 'https://loremflickr.com/320/320/beer,glass?lock=1', False, 'Bières'),
        ('Castel', 'biere', '1000,00 CFA', 'https://loremflickr.com/320/320/beer,glass?lock=1', False, 'Bières'),
        ('Beaufort', 'biere', '1500,00 CFA', 'https://loremflickr.com/320/320/beer,glass?lock=1', False, 'Bières'),
        ('33 Export', 'biere', '1500,00 CFA', 'https://loremflickr.com/320/320/beer,glass?lock=1', False, 'Bières'),
        ('Booster', 'biere', '1500,00 CFA', 'https://loremflickr.com/320/320/beer,glass?lock=1', False, 'Bières'),
        ('1664', 'biere', '2000,00 CFA', 'https://loremflickr.com/320/320/beer,glass?lock=1', False, 'Bières'),
        ('Guiness', 'biere', '2000,00 CFA', 'https://loremflickr.com/320/320/beer,glass?lock=1', False, 'Bières'),
        ('Dopel', 'biere', '1000,00 CFA', 'https://loremflickr.com/320/320/beer,glass?lock=1', False, 'Bières'),
        ('Heineken', 'biere', '2000,00 CFA', 'https://loremflickr.com/320/320/beer,glass?lock=1', False, 'Bières'),
        ('Desperados', 'biere', '2000,00 CFA', 'https://loremflickr.com/320/320/beer,glass?lock=1', False, 'Bières'),
        ('Smirnoff Ice', 'biere', '2000,00 CFA', 'https://loremflickr.com/320/320/beer,glass?lock=1', False, 'Bières'),
        ('Mojito classique', 'cocktails', '4500,00 CFA', 'https://loremflickr.com/320/320/cocktail,glass?lock=1', False, 'Rhum, feuilles de menthe.\nsirop de sucre de canne, citron, soda'),
        ('Mojito Aromatisé', 'cocktails', '5500,00 CFA', 'https://loremflickr.com/320/320/cocktail,glass?lock=1', False, 'Saveur au choix (fraise, passion, mangue,)'),
        ('Pina Colada', 'cocktails', '6000,00 CFA', 'https://loremflickr.com/320/320/cocktail,glass?lock=1', False, "Rhum, Malibu, jus d'ananas,\npurée de coco"),
        ('Caipirinha', 'cocktails', '4500,00 CFA', 'https://loremflickr.com/320/320/cocktail,glass?lock=1', False, 'Rhum, cachaca, citron, sucre en poudre'),
        ('Ti-Punch', 'cocktails', '3500,00 CFA', 'https://loremflickr.com/320/320/cocktail,glass?lock=1', False, 'Rhum. citron, sirop de sucre de canne'),
        ('Ti-Punch aromatisé', 'cocktails', '5000,00 CFA', 'https://loremflickr.com/320/320/cocktail,glass?lock=1', False, 'Saveur au choix (fraise, passion,\nmangue, coco)'),
        ('Margarita', 'cocktails', '4500,00 CFA', 'https://loremflickr.com/320/320/cocktail,glass?lock=1', False, 'Tequila, citron, sucre de canne,\ntriple sec,)'),
        ('Sunrise', 'cocktails', '5000,00 CFA', 'https://loremflickr.com/320/320/cocktail,glass?lock=1', False, "Tequila, jus d'orange, jus de citron, grenadine"),
        ('Cosmopolitan', 'cocktails', '5000,00 CFA', 'https://loremflickr.com/320/320/cocktail,glass?lock=1', False, 'Vodka, Jus de cranberry, citron,\ntriple sec, sucre de canne'),
        ('Vesper 007', 'cocktails', '5000,00 CFA', 'https://loremflickr.com/320/320/cocktail,glass?lock=1', False, 'Vodka , martini, gin, jus de citron'),
        ('Mai Tai', 'cocktails', '5000,00 CFA', 'https://loremflickr.com/320/320/cocktail,glass?lock=1', False, 'Rhum, sirop d orgeat, triple sec, jus de citron'),
        ("Parad'ice", 'cocktails', '6000,00 CFA', 'https://loremflickr.com/320/320/cocktail,glass?lock=1', True, "Cocktails signature - Vodka, malibu ,purée de passion ,\njus d'ananas"),
        ('Amaretto sour', 'cocktails', '6500,00 CFA', 'https://loremflickr.com/320/320/cocktail,glass?lock=1', True, 'Cocktails signature - Jack Daniel, amaretto, jus de citron'),
        ('Gin basil', 'cocktails', '6000,00 CFA', 'https://loremflickr.com/320/320/cocktail,glass?lock=1', True, 'Cocktails signature - Gin, jus de citron , sucre de canne ,\nbasilic'),
        ('La prefé', 'cocktails', '6000,00 CFA', 'https://loremflickr.com/320/320/cocktail,glass?lock=1', True, 'Cocktails signature - Porto blanc, malibu, litchi'),
        ('Old fashion', 'cocktails', '6000,00 CFA', 'https://loremflickr.com/320/320/cocktail,glass?lock=1', True, "Cocktails signature - Agoustura , whisky bourbon, zeste d'orange"),
        ('Oxygene', 'cocktails', '13000,00 CFA', 'https://loremflickr.com/320/320/cocktail,glass?lock=1', False, 'Stunning cocktails - Champagne, crème de pêche ,fruits\nde la passion'),
        ('Cosmos', 'cocktails', '14000,00 CFA', 'https://loremflickr.com/320/320/cocktail,glass?lock=1', False, 'Stunning cocktails - Champagne, purée de fruits rouge,\nmyrtille et fruits rouge'),
        ('Chantaco', 'mocktails', '4000,00 CFA', 'https://loremflickr.com/320/320/mocktail,juice?lock=1', False, "Mocktails - Jus d'orange, jus de pamplemousse,\ncitron, sirop do grenadine"),
        ('Florida', 'mocktails', '4000,00 CFA', 'https://loremflickr.com/320/320/mocktail,juice?lock=1', False, "Mocktails - Jus d'orange, citron, sirop de grenadine"),
        ('Dei Passion', 'mocktails', '4500,00 CFA', 'https://loremflickr.com/320/320/mocktail,juice?lock=1', False, "Mocktails - Jus d'ananas, fruit de le passion,\ncitron, sirop de grenadine"),
        ('Virgin Mojito', 'mocktails', '4000,00 CFA', 'https://loremflickr.com/320/320/mocktail,juice?lock=1', False, 'Mocktails - Perrier, sirop de sucre de canne,\ncitron, menthe'),
        ('Virgin Mojito Aromatisé', 'mocktails', '5000,00 CFA', 'https://loremflickr.com/320/320/mocktail,juice?lock=1', False, 'Mocktails - Saveur aux choix (fraise, passion, mangue,)'),
        ('Mango Sparkle', 'mocktails', '4000,00 CFA', 'https://loremflickr.com/320/320/mocktail,juice?lock=1', False, 'Mocktails - Purée da mangue, jus de pomme, citron'),
        ('Baby Breeze', 'mocktails', '6000,00 CFA', 'https://loremflickr.com/320/320/mocktail,juice?lock=1', False, "Mocktails - Jus d'ananas, jus de cranberry, citron"),
        ('Johnnie Walker Red Label', 'whisky', '4000,00 CFA', 'https://loremflickr.com/320/320/whisky?lock=1', False, 'Les assemblages'),
        ('Johnnie Walker Black Label', 'whisky', '7000,00 CFA', 'https://loremflickr.com/320/320/whisky?lock=1', False, 'Les assemblages'),
        ('Johnnie Walker Blue Label', 'whisky', '25000,00 CFA', 'https://loremflickr.com/320/320/whisky?lock=1', True, 'Les assemblages'),
        ('Johnnie Walker Green Label', 'whisky', '25000,00 CFA', 'https://loremflickr.com/320/320/whisky?lock=1', False, 'Les assemblages'),
        ('Chivas Regal 12 ans', 'whisky', '7500,00 CFA', 'https://loremflickr.com/320/320/whisky?lock=1', False, 'Les assemblages'),
        ('Chivas Regal 18 ans', 'whisky', '15000,00 CFA', 'https://loremflickr.com/320/320/whisky?lock=1', False, 'Les assemblages'),
        ('Chivas Regal 21 ans Royal Salute', 'whisky', '20000,00 CFA', 'https://loremflickr.com/320/320/whisky?lock=1', False, 'Les assemblages'),
        ("Jack Daniel's N07", 'whisky', '4000,00 CFA', 'https://loremflickr.com/320/320/whisky?lock=1', False, 'Les assemblages'),
        ("Jack Daniel's Honey", 'whisky', '5000,00 CFA', 'https://loremflickr.com/320/320/whisky?lock=1', False, 'Les assemblages'),
        ("Jack Daniel's Fire", 'whisky', '5000,00 CFA', 'https://loremflickr.com/320/320/whisky?lock=1', False, 'Les assemblages'),
        ("Jack Daniel's gentleman", 'whisky', '8000,00 CFA', 'https://loremflickr.com/320/320/whisky?lock=1', False, 'Les assemblages'),
        ("Jack Daniel's silver", 'whisky', '7000,00 CFA', 'https://loremflickr.com/320/320/whisky?lock=1', False, 'Les assemblages'),
        ('Don papa', 'rhum', '7000,00 CFA', 'https://loremflickr.com/320/320/rum,glass?lock=1', False, 'Rhum sélection'),
        ('Kraken', 'rhum', '6000,00 CFA', 'https://loremflickr.com/320/320/rum,glass?lock=1', False, 'Rhum sélection'),
        ('Diplomatico', 'rhum', '7000,00 CFA', 'https://loremflickr.com/320/320/rum,glass?lock=1', False, 'Rhum sélection'),
        ('Clement', 'rhum', '5500,00 CFA', 'https://loremflickr.com/320/320/rum,glass?lock=1', False, 'Rhum sélection'),
        ('Rhum Havana', 'rhum', '5000,00 CFA', 'https://loremflickr.com/320/320/rum,glass?lock=1', False, 'Rhum sélection'),
        ('Rhum mangoustan', 'rhum', '3500,00 CFA', 'https://loremflickr.com/320/320/rum,glass?lock=1', False, 'Rhum sélection'),
        ('Hennessy VS', 'cognac', '5000,00 CFA', 'https://loremflickr.com/320/320/cognac,glass?lock=1', False, 'Cognac & armagnac sélection'),
        ('Hennessy VSOP', 'cognac', '7000,00 CFA', 'https://loremflickr.com/320/320/cognac,glass?lock=1', False, 'Cognac & armagnac sélection'),
        ('Hennessy X.O', 'cognac', '15000,00 CFA', 'https://loremflickr.com/320/320/cognac,glass?lock=1', False, 'Cognac & armagnac sélection'),
        ('Armagnac VS', 'cognac', '5000,00 CFA', 'https://loremflickr.com/320/320/cognac,glass?lock=1', False, 'Cognac & armagnac sélection'),
        ('Armagnac X.O', 'cognac', '7000,00 CFA', 'https://loremflickr.com/320/320/cognac,glass?lock=1', False, 'Cognac & armagnac sélection'),
        ('Gin Gordon', 'gin', '3500,00 CFA', 'https://loremflickr.com/320/320/gin,tonic?lock=1', False, 'Gin sélection'),
        ('Bombay Saphir', 'gin', '5000,00 CFA', 'https://loremflickr.com/320/320/gin,tonic?lock=1', False, 'Gin sélection'),
        ('Bulldog', 'gin', '6500,00 CFA', 'https://loremflickr.com/320/320/gin,tonic?lock=1', False, 'Gin sélection'),
        ('Tanqueray', 'gin', '6000,00 CFA', 'https://loremflickr.com/320/320/gin,tonic?lock=1', False, 'Gin sélection'),
        ('Gin Hendricks', 'gin', '7000,00 CFA', 'https://loremflickr.com/320/320/gin,tonic?lock=1', False, 'Gin sélection'),
        ('Vodka Absolut', 'vodka', '4000,00 CFA', 'https://loremflickr.com/320/320/vodka,glass?lock=1', False, 'Vodka sélection'),
        ('Vodka Belvedere', 'vodka', '5000,00 CFA', 'https://loremflickr.com/320/320/vodka,glass?lock=1', False, 'Vodka sélection'),
        ('Vodka Elixir', 'vodka', '6000,00 CFA', 'https://loremflickr.com/320/320/vodka,glass?lock=1', False, 'Vodka sélection'),
        ('Vodka Sky', 'vodka', '5500,00 CFA', 'https://loremflickr.com/320/320/vodka,glass?lock=1', False, 'Vodka sélection'),
        ('Glenfiddich 12 ans', 'whisky', '7000,00 CFA', 'https://loremflickr.com/320/320/whisky?lock=1', False, 'Glen sélection'),
        ('Glenfiddich 15 ans', 'whisky', '8000,00 CFA', 'https://loremflickr.com/320/320/whisky?lock=1', False, 'Glen sélection'),
        ('Glenlivet 12 ans', 'whisky', '6000,00 CFA', 'https://loremflickr.com/320/320/whisky?lock=1', False, 'Glen sélection'),
        ('Glenmorangie 12 ans', 'whisky', '6000,00 CFA', 'https://loremflickr.com/320/320/whisky?lock=1', False, 'Glen sélection'),
        ('Campari', 'aperitifs', '3500,00 CFA', 'https://loremflickr.com/320/320/aperitif,glass?lock=1', False, 'Apéritifs'),
        ('Martini', 'aperitifs', '3500,00 CFA', 'https://loremflickr.com/320/320/aperitif,glass?lock=1', False, 'Apéritifs - Rouge, blanc'),
        ('Suze', 'aperitifs', '3500,00 CFA', 'https://loremflickr.com/320/320/aperitif,glass?lock=1', False, 'Apéritifs'),
        ('Porto', 'aperitifs', '3500,00 CFA', 'https://loremflickr.com/320/320/aperitif,glass?lock=1', False, 'Apéritifs - Rouge, blanc'),
        ('Ricard', 'aperitifs', '3500,00 CFA', 'https://loremflickr.com/320/320/aperitif,glass?lock=1', False, 'Apéritifs'),
        ('Safari', 'aperitifs', '4000,00 CFA', 'https://loremflickr.com/320/320/aperitif,glass?lock=1', False, 'Apéritifs'),
        ('Tequila', 'aperitifs', '4000,00 CFA', 'https://loremflickr.com/320/320/aperitif,glass?lock=1', False, 'Apéritifs'),
        ('Malibu', 'aperitifs', '3000,00 CFA', 'https://loremflickr.com/320/320/aperitif,glass?lock=1', False, 'Apéritifs'),
        ('Ballantlnes', 'aperitifs', '3000,00 CFA', 'https://loremflickr.com/320/320/aperitif,glass?lock=1', False, 'Apéritifs'),
        ('J&B', 'aperitifs', '3500,00 CFA', 'https://loremflickr.com/320/320/aperitif,glass?lock=1', False, 'Apéritifs'),
        ('White-horse', 'aperitifs', '3000,00 CFA', 'https://loremflickr.com/320/320/aperitif,glass?lock=1', False, 'Apéritifs'),
        ('Get 27 & Get 31', 'digestifs', '5000,00 CFA', 'https://loremflickr.com/320/320/digestif,glass?lock=1', False, 'Digestifs'),
        ('Baileys', 'digestifs', '5000,00 CFA', 'https://loremflickr.com/320/320/digestif,glass?lock=1', False, 'Digestifs'),
        ('Grand marinier', 'digestifs', '7000,00 CFA', 'https://loremflickr.com/320/320/digestif,glass?lock=1', False, 'Digestifs'),
        ('Cointreau', 'digestifs', '7000,00 CFA', 'https://loremflickr.com/320/320/digestif,glass?lock=1', False, 'Digestifs'),
        ('Limoncello', 'digestifs', '', 'https://loremflickr.com/320/320/digestif,glass?lock=1', False, 'Digestifs'),
        ('Amaretto', 'digestifs', '', 'https://loremflickr.com/320/320/digestif,glass?lock=1', False, 'Digestifs'),
        ('Eau de vie mirabelle', 'digestifs', '', 'https://loremflickr.com/320/320/digestif,glass?lock=1', False, 'Digestifs'),
        ('½ Andza', 'softs', '750,00 CFA', 'https://loremflickr.com/320/320/soda,glass?lock=1', False, 'Boissons non alcoolisées'),
        ("Sirop à l'eau", 'softs', '1000,00 CFA', 'https://loremflickr.com/320/320/soda,glass?lock=1', False, 'Boissons non alcoolisées'),
        ('Andza', 'softs', '2000,00 CFA', 'https://loremflickr.com/320/320/soda,glass?lock=1', False, 'Boissons non alcoolisées'),
        ('Coca-cola', 'softs', '1500,00 CFA', 'https://loremflickr.com/320/320/soda,glass?lock=1', False, 'Boissons non alcoolisées'),
        ('Fanta', 'softs', '1000,00 CFA', 'https://loremflickr.com/320/320/soda,glass?lock=1', False, 'Boissons non alcoolisées'),
        ('Djino pamplemousse', 'softs', '1000,00 CFA', 'https://loremflickr.com/320/320/soda,glass?lock=1', False, 'Boissons non alcoolisées'),
        ('Orangina', 'softs', '1500,00 CFA', 'https://loremflickr.com/320/320/soda,glass?lock=1', False, 'Boissons non alcoolisées'),
        ('Imperiale tonic', 'softs', '1500,00 CFA', 'https://loremflickr.com/320/320/soda,glass?lock=1', False, 'Boissons non alcoolisées'),
        ('Schweppes soda water', 'softs', '1500,00 CFA', 'https://loremflickr.com/320/320/soda,glass?lock=1', False, 'Boissons non alcoolisées'),
        ('Sprite', 'softs', '1000,00 CFA', 'https://loremflickr.com/320/320/soda,glass?lock=1', False, 'Boissons non alcoolisées'),
        ('Redbull', 'softs', '2000,00 CFA', 'https://loremflickr.com/320/320/soda,glass?lock=1', False, 'Boissons non alcoolisées'),
        ('Perrier', 'softs', '2500,00 CFA', 'https://loremflickr.com/320/320/soda,glass?lock=1', False, 'Boissons non alcoolisées'),
        ('Jus de fruits', 'softs', '2000,00 CFA', 'https://loremflickr.com/320/320/soda,glass?lock=1', False, 'Boissons non alcoolisées - Orange, mangue, pomme, goyave, cranberry, ananas, fruits de la passion'),
        ('Jus de fruits pressé', 'softs', '3000,00 CFA', 'https://loremflickr.com/320/320/soda,glass?lock=1', False, 'Boissons non alcoolisées'),
        ('Amiral de Beychevelle, Saint Julien', 'vins', '65000,00 CFA', 'https://loremflickr.com/320/320/wine,glass?lock=1', False, 'Castel France'),
        ('Château Barreyres, Haut Médoc', 'vins', '25000,00 CFA', 'https://loremflickr.com/320/320/wine,glass?lock=1', False, 'Castel France'),
        ("Château d'arcins", 'vins', '27000,00 CFA', 'https://loremflickr.com/320/320/wine,glass?lock=1', False, 'Castel France'),
        ('Chianti', 'vins', '16000,00 CFA', 'https://loremflickr.com/320/320/wine,glass?lock=1', False, 'Italy'),
        ('Doppio', 'vins', '18000,00 CFA', 'https://loremflickr.com/320/320/wine,glass?lock=1', False, 'Italy'),
        ('Appassimento', 'vins', '14000,00 CFA', 'https://loremflickr.com/320/320/wine,glass?lock=1', False, 'Italy'),
        ('Nederburg', 'vins', '15000,00 CFA', 'https://loremflickr.com/320/320/wine,glass?lock=1', False, 'South africa'),
        ('Beyerskloof', 'vins', '20000,00 CFA', 'https://loremflickr.com/320/320/wine,glass?lock=1', False, 'South africa'),
        ('Cape spring', 'vins', '12000,00 CFA', 'https://loremflickr.com/320/320/wine,glass?lock=1', False, 'South africa'),
        ('Chablis, Louis Jadot', 'vins', '30000,00 CFA', 'https://loremflickr.com/320/320/wine,glass?lock=1', False, 'Blanc'),
        ('Château du Levant Sauternes', 'vins', '35000,00 CFA', 'https://loremflickr.com/320/320/wine,glass?lock=1', False, 'Blanc'),
        ('Calvet', 'vins', '14000,00 CFA', 'https://loremflickr.com/320/320/wine,glass?lock=1', False, 'Blanc'),
        ('Gewurztraminer, Laugel', 'vins', '25000,00 CFA', 'https://loremflickr.com/320/320/wine,glass?lock=1', False, 'Blanc'),
        ('Sancere', 'vins', '30000,00 CFA', 'https://loremflickr.com/320/320/wine,glass?lock=1', False, 'Blanc'),
        ('Jurancon', 'vins', '18000,00 CFA', 'https://loremflickr.com/320/320/wine,glass?lock=1', False, 'Blanc'),
        ('M de Minuty', 'vins', '30000,00 CFA', 'https://loremflickr.com/320/320/wine,glass?lock=1', False, 'Rosés'),
        ('Trouillard', 'vins', '50000,00 CFA', 'https://loremflickr.com/320/320/wine,glass?lock=1', True, 'Champagnes'),
        ('Veuve Cliquot, Brut', 'vins', '80000,00 CFA', 'https://loremflickr.com/320/320/wine,glass?lock=1', True, 'Champagnes'),
        ('Moët et Chandon, Brut Imperial', 'vins', '90000,00 CFA', 'https://loremflickr.com/320/320/wine,glass?lock=1', True, 'Champagnes'),
        ('Laurent Perrier Rosé', 'vins', '120000,00 CFA', 'https://loremflickr.com/320/320/wine,glass?lock=1', True, 'Champagnes'),
        ('Ruinart', 'vins', '150000,00 CFA', 'https://loremflickr.com/320/320/wine,glass?lock=1', True, 'Champagnes'),
        ('Chianti', 'vins', '4500,00 CFA', 'https://loremflickr.com/320/320/wine,glass?lock=1', False, 'Rouges'),
        ('Chatt Carbonac', 'vins', '5000,00 CFA', 'https://loremflickr.com/320/320/wine,glass?lock=1', False, 'Rouges'),
        ('Château du Levant Sauternes', 'vins', '8000,00 CFA', 'https://loremflickr.com/320/320/wine,glass?lock=1', False, 'Blancs'),
        ('Les Fondettes, Sancerre', 'vins', '6000,00 CFA', 'https://loremflickr.com/320/320/wine,glass?lock=1', False, 'Blancs'),
        ('Calvet', 'vins', '4500,00 CFA', 'https://loremflickr.com/320/320/wine,glass?lock=1', False, 'Blancs'),
        ('Jurancon', 'vins', '5000,00 CFA', 'https://loremflickr.com/320/320/wine,glass?lock=1', False, 'Blancs'),
        ('Kir au vin blanc', 'vins', '6000,00 CFA', 'https://loremflickr.com/320/320/wine,glass?lock=1', False, 'Blancs - Pêche, cassis, framboise, litchi'),
        ('Fleurs de Prairie, Côtes de Provences', 'vins', '4000,00 CFA', 'https://loremflickr.com/320/320/wine,glass?lock=1', False, 'Rosés'),
        ('Trouillard', 'vins', '10000,00 CFA', 'https://loremflickr.com/320/320/wine,glass?lock=1', False, 'Coupe ou piscine'),
        ('Veuve Cliquot Brut', 'vins', '13000,00 CFA', 'https://loremflickr.com/320/320/wine,glass?lock=1', False, 'Coupe ou piscine'),
        ('Moët et Chandon Brut', 'vins', '15000,00 CFA', 'https://loremflickr.com/320/320/wine,glass?lock=1', False, 'Coupe ou piscine'),
        ('Philip', 'vins', '8500,00 CFA', 'https://loremflickr.com/320/320/wine,glass?lock=1', False, 'Coupe ou piscine'),
        ('Trouillard', 'vins', '13000,00 CFA', 'https://loremflickr.com/320/320/wine,glass?lock=1', False, 'Kir ou piscine Royale'),
        ('Veuve Cliquot Brut', 'vins', '16000,00 CFA', 'https://loremflickr.com/320/320/wine,glass?lock=1', False, 'Kir ou piscine Royale'),
        ('Moët et Chandon Brut', 'vins', '17000,00 CFA', 'https://loremflickr.com/320/320/wine,glass?lock=1', False, 'Kir ou piscine Royale'),
    ]

    for p in products:
        cursor.execute(f"INSERT INTO products (name, category, price, image_url, is_premium, description) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})", p)

    conn.commit()
    conn.close()
    print("Database initialized successfully.")

if __name__ == "__main__":
    init_db()
)
    print("Database initialized successfully.")

if __name__ == "__main__":
    init_db()
