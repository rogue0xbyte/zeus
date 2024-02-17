from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np

app = Flask(__name__)
CORS(app)

# Database of registered users (user_id: name, histogram)
user_database = {
    1: {"name": "John", "histogram": None},
    2: {"name": "Alice", "histogram": None},
    # Add more users as needed
}

def get_histogram(image):
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Calculate histogram
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256])

    # Normalize histogram
    hist = cv2.normalize(hist, hist).flatten()

    return hist

def compare_histograms(hist1, hist2):
    # Calculate histogram intersection
    return cv2.compareHist(hist1, hist2, cv2.HISTCMP_INTERSECT)

def authenticate_user(user_id, name, query_hist):
    for stored_user_id, user_data in user_database.items():
        if user_id == stored_user_id and name == user_data['name']:
            known_hist = np.array(user_data['histogram'])
            similarity = compare_histograms(query_hist, known_hist)

            if similarity > 0.5:  # You can adjust the similarity threshold as needed
                return True

    return False

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        try:
            # Get user credentials and captured image
            user_id = int(request.form['user_id'])
            name = request.form['name']
            captured_image_data = request.files['image'].read()
            captured_nparr = np.frombuffer(captured_image_data, np.uint8)
            captured_img = cv2.imdecode(captured_nparr, cv2.IMREAD_COLOR)
            query_hist = get_histogram(captured_img)

            if query_hist is not None:
                # Authenticate user
                if authenticate_user(user_id, name, query_hist):
                    return render_template('login.html', user_id=user_id, name=name, status="success")
                else:
                    return render_template('login.html', status="failure", message="Authentication failed")
            else:
                return render_template('login.html', status="error", message="Unable to generate histogram for login")

        except Exception as e:
            return render_template('login.html', status="error", message=str(e))

    else:
        return render_template('login.html')

@app.route('/register', methods=['POST','GET'])
def register_user():
    if request.method == 'POST':
        try:
            user_id = int(request.form['user_id'])
            name = request.form['name']
            captured_image_data = request.files['image'].read()
            captured_nparr = np.frombuffer(captured_image_data, np.uint8)
            captured_img = cv2.imdecode(captured_nparr, cv2.IMREAD_COLOR)
            hist = get_histogram(captured_img)

            if hist is not None:
                user_database[user_id] = {"name": name, "histogram": hist.tolist()}
                return render_template('login.html', user_id=user_id, name=name, status="success")
            else:
                return render_template('register.html', status="error", message="Unable to generate histogram for registration")

        except Exception as e:
            return render_template('register.html', status="error", message=str(e))

    else:
        return render_template('register.html')

if __name__ == "__main__":
    app.run(debug=True)
