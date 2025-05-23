from flask import Flask, request, render_template, jsonify # Added jsonify
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

app = Flask(__name__) 

# --- APScheduler Configuration ---
class Config:
    SCHEDULER_API_ENABLED = True

app.config.from_object(Config())
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()
# --- End APScheduler Configuration ---

init_db() # Initialize DB schema if it doesn't exist



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
    scheduler.add_job(id='periodic_scrape_job', func=scheduled_scrape_task, trigger='interval', minutes=5)


# --- Flask Routes ---
@app.route('/')
def home():
    default_product_info = {
        "name": "Product Name",
        "price": "N/A",
        "image_url": None
    }
    # Use render_template to serve the HTML file from the 'templates' folder
    return render_template('index.html',
                           product_info=default_product_info,
                           message=None,
                           message_type=None, # Added message_type for consistency
                           submitted_url="") # Pass empty submitted_url

@app.route('/track', methods=['POST'])
def track():
    url = request.form['url']
    message = None
    message_type = None
    product_display_info = { "name": "Product Not Found", "price": "N/A", "image_url": None }

    ua_string = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36" # Example
    HEADERS_FOR_IMAGE = {
        "User-Agent": ua_string, # Make sure you have a User-Agent here
        "Accept-Language": "en-US,en;q=0.9"
    }

    scraped_data = fetch_amazon_data(url)

    if scraped_data:
        image_url = get_amazon_image(url, HEADERS_FOR_IMAGE)
        product_display_info = {
            "name": scraped_data['title'],
            "price": scraped_data['price'],
            "image_url": image_url
        }

        product_id = add_or_update_tracked_product(url, scraped_data['title'], image_url)
        if product_id:
            if scraped_data['price'] != "Price not found" and scraped_data['price'] is not None: # Check for None too
                save_price_history(url, scraped_data['price'], scraped_data['timestamp'])
            message = f"Product '{scraped_data['title']}' is now being tracked! History will appear below."
            message_type = "success"
            logging.info(f"Tracking new product: {url} - {scraped_data['title']}")
        else:
            message = "Error adding product to tracking database."
            message_type = "error"
            logging.error(f"Failed to add/update tracked product: {url}")
    else:
        message = "Could not fetch product data. Please check the URL or try again later."
        message_type = "error"
        logging.warning(f"Failed to fetch data for user-submitted URL: {url}")

    # Use render_template and pass the submitted_url so the graph can fetch its data
    return render_template('index.html',
                           product_info=product_display_info,
                           message=message,
                           message_type=message_type,
                           submitted_url=url) # Pass the URL back to the template


# --- API Endpoint for Historical Data ---
@app.route('/api/history/<path:product_url>')
def api_product_history(product_url):
    logging.info(f"API request for history of: {product_url}")
    history_data = get_product_price_history(product_url)
    product_details = get_tracked_product_details(product_url)

    if not product_details:
        return jsonify({"error": "Product not tracked or not found"}), 404

    return jsonify({
        "product_title": product_details.get("title", "N/A"),        # Ensure this is sent
        "product_image_url": product_details.get("image_url"),      # Ensure this is sent
        "history": history_data if history_data is not None else [] # Ensure history is always a list
    })

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)