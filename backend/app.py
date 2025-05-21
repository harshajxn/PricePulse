from flask import Flask, request, render_template_string

app = Flask(__name__)

# Basic HTML and CSS template to mimic the image
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PricePulse - E-Commerce Price Tracker</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            background-color: #f0f2f5;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            min-height: 100vh;
            padding-top: 50px;
        }
        .container {
            background-color: #ffffff;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            width: 800px;
            padding-bottom: 30px;
            margin-bottom: 50px;
        }
        .header {
            background-color: #3498db;
            color: white;
            padding: 20px 0;
            text-align: center;
            font-size: 24px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            margin-bottom: 20px;
        }
        .section {
            margin: 0 40px 20px 40px;
        }
        .input-section {
            display: flex;
            align-items: center;
            margin-bottom: 20px;
        }
        .input-section label {
            margin-right: 10px;
            font-weight: bold;
        }
        .input-section input[type="text"] {
            flex-grow: 1;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 4px;
            font-size: 16px;
        }
        .input-section button {
            background-color: #2ecc71;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            margin-left: 10px;
        }
        .input-section button:hover {
            background-color: #27ae60;
        }
        .product-preview, .price-history-graph, .other-platforms {
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            padding: 15px;
            margin-bottom: 20px;
            min-height: 80px; /* Adjust as needed */
            box-sizing: border-box;
        }
        .product-preview {
            display: flex;
            align-items: center;
        }
        .product-preview-image {
            width: 100px;
            height: 80px;
            border: 1px solid #ccc;
            background-color: #f9f9f9;
            margin-right: 15px;
            display: flex;
            justify-content: center;
            align-items: center;
            color: #888;
            font-size: 12px;
        }
        .product-info p {
            margin: 5px 0;
        }
        .price-info {
            font-weight: bold;
        }
        .price-history-graph {
            height: 250px; /* Height for the graph placeholder */
            display: flex;
            justify-content: center;
            align-items: center;
            color: #888;
        }
        .other-platforms ul {
            list-style: none;
            padding: 0;
            margin: 0;
        }
        .other-platforms li {
            margin-bottom: 5px;
        }
        .section-title {
            font-weight: bold;
            margin-bottom: 10px;
            font-size: 18px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            PricePulse - E-Commerce Price Tracker
        </div>

        <div class="section">
            <form method="POST" action="/track" class="input-section">
                <label for="url">Enter Amazon Product URL:</label>
                <input type="text" name="url" id="url" placeholder="Enter Amazon Product URL" required>
                <button type="submit">Track</button>
            </form>
        </div>

        <div class="section">
            <div class="section-title">Product Preview:</div>
            <div class="product-preview">
                <div class="product-preview-image">
                    {% if product_info.image_placeholder %}
                        {{ product_info.image_placeholder }}
                    {% else %}
                        [Image Placeholder]
                    {% endif %}
                </div>
                <div class="product-info">
                    <p><strong>{{ product_info.name }}</strong></p>
                    <p class="price-info">Current Price: ₹{{ product_info.price }}</p>
                </div>
            </div>
        </div>

        <div class="section">
            <div class="section-title">Price History Graph:</div>
            <div class="price-history-graph">
                [Graph Placeholder]
            </div>
        </div>

        <div class="section">
            <div class="section-title">Available on Other Platforms (Bonus):</div>
            <div class="other-platforms">
                <ul>
                    {% for platform, price in other_platforms.items() %}
                        <li>- {{ platform }}: {% if price != 'Not Available' %}₹{{ price }}{% else %}{{ price }}{% endif %}</li>
                    {% endfor %}
                </ul>
            </div>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    # Initialize with default/empty data for initial load
    default_product_info = {
        "name": "Product Name (e.g., Samsung Galaxy M14)",
        "price": "N/A",
        "image_placeholder": "Product Image"
    }
    default_other_platforms = {
        "Flipkart": "N/A",
        "Meesho": "N/A",
        "BigBasket": "N/A"
    }
    return render_template_string(HTML_TEMPLATE, 
                                  product_info=default_product_info, 
                                  other_platforms=default_other_platforms)

@app.route('/track', methods=['POST'])
def track():
    url = request.form['url']
    
    # --- Mock data for demonstration ---
    # In a real application, you would scrape the product details from the URL
    # and fetch prices from other platforms.
    if "samsung-galaxy-m14" in url.lower():
        product_info = {
            "name": "Samsung Galaxy M14",
            "price": "13,499",
            "image_placeholder": "" # Empty for now, would be an actual image in a real app
        }
        other_platforms = {
            "Flipkart": "13,299",
            "Meesho": "13,499",
            "BigBasket": "Not Available"
        }
    else:
        # Default or error case
        product_info = {
            "name": "Product Not Found (Mock)",
            "price": "N/A",
            "image_placeholder": "No Image"
        }
        other_platforms = {
            "Flipkart": "N/A",
            "Meesho": "N/A",
            "BigBasket": "N/A"
        }
    # --- End Mock data ---

    return render_template_string(HTML_TEMPLATE, product_info=product_info, other_platforms=other_platforms)

if __name__ == '__main__':
    app.run(debug=True)