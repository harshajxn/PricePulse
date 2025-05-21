from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <h1>PricePulse Amazon Tracker</h1>
    <form method="POST" action="/track">
      <input type="text" name="url" placeholder="Enter Amazon Product URL" size="50" required>
      <button type="submit">Track</button>
    </form>
    '''

@app.route('/track', methods=['POST'])
def track():
    url = request.form['url']
    return f'You entered: {url}'

if __name__ == '__main__':
    app.run(debug=True) 
