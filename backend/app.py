from flask import Flask, request, render_template_string, jsonify # Added jsonify
from flask_apscheduler import APScheduler # Added APScheduler
from amazon_scraper import fetch_amazon_data
from amazon_image_scraper import get_amazon_image
# Updated database import
from database import (
    init_db,
    add_or_update_tracked_product,
    save_price_history,
    get_all_tracked_product_urls,
    get_product_price_history,
    get_tracked_product_details # Added
)
import logging # For better logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__) # Corrected: app = Flask(__name__)

# --- APScheduler Configuration ---
class Config:
    SCHEDULER_API_ENABLED = True

app.config.from_object(Config())
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()
# --- End APScheduler Configuration ---

init_db() # Initialize DB schema if it doesn't exist

# --- Your HTML Template (keep as is or move to a file) ---
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PricePulse - E-Commerce Price Tracker</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; background-color: #f0f2f5; display: flex; justify-content: center; align-items: flex-start; min-height: 100vh; padding-top: 50px; }
        .container { background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); width: 800px; padding-bottom: 30px; margin-bottom: 50px; }
        .header { background-color: #3498db; color: white; padding: 20px 0; text-align: center; font-size: 24px; border-top-left-radius: 8px; border-top-right-radius: 8px; margin-bottom: 20px; }
        .section { margin: 0 40px 20px 40px; }
        .input-section { display: flex; align-items: center; margin-bottom: 20px; }
        .input-section label { margin-right: 10px; font-weight: bold; }
        .input-section input[type="text"] { flex-grow: 1; padding: 10px; border: 1px solid #ccc; border-radius: 4px; font-size: 16px; }
        .input-section button { background-color: #2ecc71; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; margin-left: 10px; }
        .input-section button:hover { background-color: #27ae60; }
        .product-preview, .price-history-graph, .other-platforms { border: 1px solid #e0e0e0; border-radius: 4px; padding: 15px; margin-bottom: 20px; min-height: 80px; box-sizing: border-box; }
        .product-preview { display: flex; align-items: center; }
        .product-preview-image { width: 100px; height: 80px; border: 1px solid #ccc; background-color: #f9f9f9; margin-right: 15px; display: flex; justify-content: center; align-items: center; color: #888; font-size: 12px; }
        .product-info p { margin: 5px 0; }
        .price-info { font-weight: bold; }
        .price-history-graph { height: 250px; display: flex; justify-content: center; align-items: center; color: #888; }
        .other-platforms ul { list-style: none; padding: 0; margin: 0; }
        .other-platforms li { margin-bottom: 5px; }
        .section-title { font-weight: bold; margin-bottom: 10px; font-size: 18px; }
        .message { padding: 10px; margin-bottom: 15px; border-radius: 4px; text-align: center; }
        .message.success { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb;}
        .message.error { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb;}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">PricePulse - E-Commerce Price Tracker</div>
        {% if message %}
            <div class="section">
                <div class="message {{ message_type }}">{{ message }}</div>
            </div>
        {% endif %}
        <div class="section">
            <form method="POST" action="/track" class="input-section">
                <label for="url">Enter Amazon Product URL:</label>
                <input type="text" name="url" id="url" placeholder="Enter Amazon Product URL" required value="{{ submitted_url }}">
                <button type="submit">Track Product</button>
            </form>
        </div>
        <div class="section">
            <div class="section-title">Product Preview:</div>
            <div class="product-preview">
                <div class="product-preview-image">
                    {% if product_info.image_url %}
                        <img src="{{ product_info.image_url }}" alt="Product Image" style="width: 100%; height: 100%; object-fit: contain;">
                    {% else %}
                        [Image Not Available]
                    {% endif %}
                </div>
                <div class="product-info">
                    <p><strong>{{ product_info.name }}</strong></p>
                    <p class="price-info">Current Price: {{ product_info.price }}</p>
                </div>
            </div>
        </div>
        <div class="section">
            <div class="section-title">Price History Graph:</div>
            <div class="price-history-graph" id="priceChartContainer">
                [Graph Placeholder - Will be implemented with Chart.js later]
                <!-- We will populate this using JavaScript and the /api/history endpoint -->
            </div>
        </div>
        <!-- Other platforms section can remain as is for now -->
    </div>
</body>
</html>
'''

# --- Scheduled Job ---
def scheduled_scrape_task():
    """
    Fetches all tracked product URLs and scrapes data for each.
    This function is run by the APScheduler.
    """
    with app.app_context(): # Important for scheduler tasks needing app context
        logging.info("Starting scheduled scrape task...")
        urls_to_scrape = get_all_tracked_product_urls()
        if not urls_to_scrape:
            logging.info("No products to track. Scheduled task finished.")
            return

        for url in urls_to_scrape:
            logging.info(f"Scheduled scraping for: {url}")
            product_data = fetch_amazon_data(url)
            if product_data and product_data['price'] != "Price not found":
                save_price_history(url, product_data['price'], product_data['timestamp'])
                # Optionally update the title/image in tracked_products if they change
                # For now, we only update them when user manually adds/tracks via UI
                # add_or_update_tracked_product(url, product_data['title'], get_amazon_image(url, HEADERS)) # If you want to auto-update image too
                logging.info(f"Successfully scraped and saved price for: {product_data['title']}")
            elif product_data:
                logging.warning(f"Price not found for {url}. Title: {product_data['title']}")
            else:
                logging.warning(f"Failed to fetch data for: {url}")
        logging.info("Scheduled scrape task finished.")

# Register the job with APScheduler
# Runs every 1 hour. For testing, you can use minutes=1 or seconds=30
if not scheduler.get_job('periodic_scrape_job'): # Avoid adding duplicate jobs on reload with debug=True
    scheduler.add_job(id='periodic_scrape_job', func=scheduled_scrape_task, trigger='interval', hours=1)


# --- Flask Routes ---
@app.route('/')
def home():
    default_product_info = {
        "name": "Product Name",
        "price": "N/A",
        "image_url": None
    }
    return render_template_string(HTML_TEMPLATE,
                                  product_info=default_product_info,
                                  message=None,
                                  submitted_url="")

@app.route('/track', methods=['POST'])
def track():
    url = request.form['url']
    message = None
    message_type = None
    product_display_info = { "name": "Product Not Found", "price": "N/A", "image_url": None }

    # Perform an initial scrape to get details and first price point
    scraped_data = fetch_amazon_data(url)
    HEADERS_FOR_IMAGE = { # Define headers for image scraper if not globally defined
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }

    if scraped_data:
        image_url = get_amazon_image(url, HEADERS_FOR_IMAGE) # Assuming headers are defined
        product_display_info = {
            "name": scraped_data['title'],
            "price": scraped_data['price'],
            "image_url": image_url
        }

        # Add to tracked_products and save initial price
        product_id = add_or_update_tracked_product(url, scraped_data['title'], image_url)
        if product_id:
            if scraped_data['price'] != "Price not found":
                save_price_history(url, scraped_data['price'], scraped_data['timestamp'])
            message = f"Product '{scraped_data['title']}' is now being tracked!"
            message_type = "success"
            logging.info(f"Tracking new product: {url} - {scraped_data['title']}")
        else:
            message = "Error adding product to tracking database."
            message_type = "error"
            logging.error(f"Failed to add/update tracked product: {url}")
    else:
        message = "Could not fetch product data. Please check the URL."
        message_type = "error"
        logging.warning(f"Failed to fetch data for user-submitted URL: {url}")

    return render_template_string(HTML_TEMPLATE,
                                  product_info=product_display_info,
                                  message=message,
                                  message_type=message_type,
                                  submitted_url=url)

# --- API Endpoint for Historical Data ---
@app.route('/api/history/<path:product_url>') # <path:..> allows URLs in path
def api_product_history(product_url):
    # The product_url will be URL-encoded by the browser/client,
    # Flask automatically decodes it.
    logging.info(f"API request for history of: {product_url}")
    history_data = get_product_price_history(product_url)
    product_details = get_tracked_product_details(product_url)

    if not product_details:
        return jsonify({"error": "Product not tracked or not found"}), 404

    return jsonify({
        "product_title": product_details.get("title", "N/A"),
        "product_image_url": product_details.get("image_url"),
        "history": history_data
    })

if __name__ == '__main__':
    # Ensure init_db is called before starting the app if you cleared the DB
    # init_db() # Usually done once globally, as above.
    app.run(debug=True, use_reloader=False) # use_reloader=False is important for APScheduler in debug mode
                                           # to prevent scheduler from running twice.