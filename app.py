from flask import Flask, render_template, request, redirect, url_for, flash
import os
import json
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'upload')
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Path to the JSON file
PRODUCTS_FILE = 'products.json'

# Dictionary to store product data
products = {}

@app.route('/produk_detail/<int:product_id>')
def produk_detail(product_id):
    product_id = str(product_id)  # Convert to string since dictionary keys are strings
    load_products()  # Ensure products are loaded
    product = products.get(product_id)

    if product:
        return render_template('produk_detail.html', product=product)
    else:
        flash('Product not found.')
        return redirect(url_for('produk'))


# Load products from JSON file
def load_products():
    global products
    products.clear()  # Clear the dictionary before updating
    try:
        if os.path.exists(PRODUCTS_FILE):
            with open(PRODUCTS_FILE, 'r') as f:
                products.update(json.load(f))
        else:
            products = {}
    except json.JSONDecodeError:
        print('Failed to load products data. The file might be corrupted.')
        products = {}

# Save products to JSON file
def save_products():
    try:
        with open(PRODUCTS_FILE, 'w') as f:
            json.dump(products, f, indent=4)
        print(f"Products saved to {PRODUCTS_FILE}")
    except IOError:
        flash('Failed to save products data. Please try again.')
        print("Error saving products to file")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/produk')
def produk():
    load_products()  # Load products before rendering the produk page
    return render_template('produk.html', products=products)

@app.route('/tambah', methods=['GET', 'POST'])
def tambah():
    if request.method == 'POST':
        product_name = request.form['productName']
        price = request.form['price']
        description = request.form['description']
        whatsapp = request.form['whatsapp']
        file = request.files['productImage']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Save product details to the dictionary
            product_id = str(len(products) + 1)  # Ensure product_id is a string
            products[product_id] = {
                'name': product_name,
                'price': price,
                'description': description,
                'whatsapp': whatsapp,
                'image': f'upload/{filename}'
            }

            # Save products to JSON file
            save_products()

            flash('Product added successfully!')
            return redirect(url_for('admin'))

    return render_template('tambah.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    load_products()  # Load products data before rendering the admin page
    return render_template('admin.html', products=products)

@app.route('/delete/<int:product_id>', methods=['POST'])
def delete(product_id):
    product_id = str(product_id)  # Convert product_id to string since dictionary keys are strings
    if product_id in products:
        # Get the image path of the product to be deleted
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(products[product_id]['image']))
        
        # Delete image file if it exists
        if os.path.exists(image_path):
            os.remove(image_path)
        else:
            print(f"Image not found at path: {image_path}")

        # Delete the product from the dictionary
        del products[product_id]

        # Re-index the remaining products to maintain sequential product IDs
        products_reindexed = {str(i+1): prod for i, prod in enumerate(products.values())}
        products.clear()
        products.update(products_reindexed)

        # Save the updated products to the JSON file
        save_products()
        flash('Product deleted successfully!')
    else:
        flash('Product not found.')
    
    return redirect(url_for('admin'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'dermaji' and password == 'dermajiumkm69':
            flash('Login successful!')
            return redirect(url_for('admin'))
        else:
            flash('Invalid credentials, please try again.')
            return redirect(url_for('login'))
    return render_template('login.html')

if __name__ == '__main__':
    load_products()
    app.run(host='0.0.0.0', port=5000, debug=True)
