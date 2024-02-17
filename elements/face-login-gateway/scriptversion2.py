import os
import cv2
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load a pre-trained face recognition model (e.g., OpenCV's LBPH recognizer)
face_recognizer = cv2.face.LBPHFaceRecognizer_create()

# Database of registered users (user_id: name)
user_database = {
    1: "John",
    2: "Alice",
    # Add more users as needed
}

@app.route('/register', methods=['POST'])
def register():
    try:
        user_id = int(request.form['user_id'])
        name = request.form['name']

        # Capture an image from the user
        image_data = request.files['image'].read()
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Convert the image to grayscale
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Train the face recognizer with the new face
        face_recognizer.update([gray_img], np.array([user_id]))

        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/login', methods=['POST'])
def login():
    try:
        # Capture an image from the user
        image_data = request.files['image'].read()
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Convert the image to grayscale
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Perform face recognition
        label, confidence = face_recognizer.predict(gray_img)

        if confidence < 70:  # You can adjust the confidence threshold as needed
            user_id = label
            name = user_database.get(user_id, "Unknown")
            return jsonify({"status": "success", "user_id": user_id, "name": name})
        else:
            return jsonify({"status": "failure", "message": "Face not recognized"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
