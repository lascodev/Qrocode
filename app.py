import os
import sqlite3
import jwt
import datetime
import bcrypt
import urllib.parse as urlparse
from functools import wraps
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Use environment variable for production, fallback for local
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'the_peat_secret_key_12345')
app.config['UPLOAD_FOLDER'] = 'assets/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# --- Database Setup ---
DATABASE_URL = os.environ.get('POSTGRES_URL') or os.environ.get('DATABASE_URL')

def get_db_connection():
    if DATABASE_URL:
        # PostgreSQL Connection (Vercel / Production)
        import psycopg2
        import psycopg2.extras
        # Fix for some providers that use postgres:// instead of postgresql://
        url = DATABASE_URL
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        
        conn = psycopg2.connect(url)
        # Use DictCursor to mimic sqlite3.Row behavior
        return conn
    else:
        # SQLite Connection (Local)
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        return conn

def execute_query(query, params=(), fetchone=False, fetchall=False, commit=False):
    conn = get_db_connection()
    try:
        if DATABASE_URL:
            import psycopg2.extras
            # For Postgres, we use a cursor
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            # Convert ? placeholders to %s for Postgres
            query = query.replace('?', '%s')
            cur.execute(query, params)
            if commit:
                conn.commit()
            
            result = None
            if fetchone:
                result = cur.fetchone()
            elif fetchall:
                result = cur.fetchall()
            
            if commit and DATABASE_URL: # If it was an INSERT and we need ID
                if 'INSERT' in query.upper() and 'RETURNING id' not in query.upper():
                    # This is simplified; real logic might need RETURNING
                    pass
                    
            return result
        else:
            # For SQLite
            cur = conn.execute(query, params)
            if commit:
                conn.commit()
            
            if fetchone:
                return cur.fetchone()
            if fetchall:
                return cur.fetchall()
            return cur
    finally:
        if not commit or DATABASE_URL:
            conn.close()

# --- Middleware for Auth ---
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            token = token.split(" ")[1] # Bearer TOKEN
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = data
        except Exception as e:
            return jsonify({'message': 'Token is invalid!', 'error': str(e)}), 401
        return f(current_user, *args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user.get('role') != 'admin':
            return jsonify({'message': 'Admin privilege required!'}), 403
        return f(current_user, *args, **kwargs)
    return decorated

# --- Routes for HTML Pages ---
@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/admin')
def admin():
    return app.send_static_file('admin.html')

# --- API Routes ---

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'message': 'Username and password required'}), 400
        
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    try:
        execute_query("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                     (username, hashed_password, 'client'), commit=True)
    except Exception as e:
        return jsonify({'message': 'Username already exists or database error'}), 409
    
    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = execute_query("SELECT * FROM users WHERE username = ?", (username,), fetchone=True)
    
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        token = jwt.encode({
            'username': user['username'],
            'role': user['role'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm="HS256")
        
        return jsonify({'token': token, 'role': user['role']}), 200
        
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/api/products', methods=['GET'])
@token_required
def get_products(current_user):
    products = execute_query("SELECT * FROM products", fetchall=True)
    return jsonify([dict(ix) for ix in products]), 200

@app.route('/api/products', methods=['POST'])
@token_required
@admin_required
def add_product(current_user):
    data = request.get_json()
    # For Postgres we handle the ID slightly differently if needed, 
    # but let's keep it simple for now.
    query = '''
        INSERT INTO products (name, category, price, image_url, is_premium, description) 
        VALUES (?, ?, ?, ?, ?, ?)
    '''
    params = (data['name'], data['category'], data['price'], data['image_url'], data.get('is_premium', 0), data.get('description', ''))
    
    execute_query(query, params, commit=True)
    return jsonify({'message': 'Product added successfully'}), 201

@app.route('/api/products/<int:id>', methods=['PUT'])
@token_required
@admin_required
def update_product(current_user, id):
    data = request.get_json()
    query = '''
        UPDATE products 
        SET name = ?, category = ?, price = ?, image_url = ?, is_premium = ?, description = ?
        WHERE id = ?
    '''
    params = (data['name'], data['category'], data['price'], data['image_url'], data.get('is_premium', 0), data.get('description', ''), id)
    execute_query(query, params, commit=True)
    return jsonify({'message': 'Product updated successfully'}), 200

@app.route('/api/products/<int:id>', methods=['DELETE'])
@token_required
@admin_required
def delete_product(current_user, id):
    execute_query('DELETE FROM products WHERE id = ?', (id,), commit=True)
    return jsonify({'message': 'Product deleted successfully'}), 200

@app.route('/api/upload', methods=['POST'])
@token_required
@admin_required
def upload_file(current_user):
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
    if file:
        filename = secure_filename(file.filename)
        filename = f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
        
        # Check if running on Vercel
        if os.environ.get('VERCEL'):
            return jsonify({'message': 'Local uploads not supported on Vercel. Please use Cloudinary or S3.'}), 501
            
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
            
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return jsonify({'url': f'assets/uploads/{filename}'}), 200

@app.route('/api/users', methods=['GET'])
@token_required
@admin_required
def get_users(current_user):
    users = execute_query("SELECT id, username, role FROM users", fetchall=True)
    return jsonify([dict(ix) for ix in users]), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=not os.environ.get('VERCEL'))
