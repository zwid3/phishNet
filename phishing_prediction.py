from flask import Flask, request, jsonify, render_template
import pickle
import re  # For URL validation

app = Flask(__name__)

# Load model once when the app starts
model = pickle.load(open('/home/revelator/phishing_app/phishing_model.pkl', 'rb'))

# Preprocessing function for URLs
def extract_features(url):
    """Extracts basic numerical features from a URL."""
    return [
        len(url),          # Length of URL
        url.count('.'),    # Number of dots in the domain
        url.count('/'),    # Number of slashes in the URL path
        url.count('-'),    # Number of hyphens in the URL
        url.count('_')     # Number of underscores in the URL
    ]

def is_valid_url(url):
    """Validates whether a given string is a valid URL."""
    pattern = re.compile(
        r'^(https?://)?'  # Optional http or https
        r'([a-zA-Z0-9.-]+)'  # Domain name
        r'(\.[a-zA-Z]{2,})'  # Top-level domain
        r'(/.*)?$'  # Optional path
    )
    return re.match(pattern, url) is not None

@app.route('/')
def home():
    return render_template('index.html')  # Render an HTML form for user input

@app.route('/url-predict', methods=['POST'])
def url_predict():
    try:
        url = request.form.get('url')
        if not url:
            return render_template('index.html', error="No URL provided", response_color="orange")

        # Validate the URL format
        if not is_valid_url(url):
            return render_template('index.html', error="Invalid URL format", response_color="orange")

        # Preprocess the URL into numerical features
        features = extract_features(url)

        # Predict using the model
        prediction = model.predict([features])
        result = 'phishing' if prediction[0] == 1 else 'legitimate'

        # Set response color based on prediction
        response_color = "red" if result == "phishing" else "green"

        return render_template('index.html', prediction=result, response_color=response_color)
    except Exception as e:
        return render_template('index.html', error=f"An error occurred: {str(e)}", response_color="orange")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005)
