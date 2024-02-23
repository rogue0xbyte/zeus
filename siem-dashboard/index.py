from flask import *
from Aadhar_OCR import Aadhar_OCR
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import ssl, smtplib, hashlib, uuid
from werkzeug.utils import secure_filename
import os
import psycopg2
import sys
sys.path.append(f"{os.path.dirname(os.getcwd())}/elements/src")
import pandas as pd
import joblib
import datetime, json
import email
from io import BytesIO
import cv2 as cv
import torch
from torchvision import transforms
from Model import DeePixBiS
import time
import base64
app = Flask(__name__)
app.jinja_env.auto_reload = True
app.config["TEMPLATES_AUTO_RELOAD"] = True

def predict_single_transaction(transaction, preprocessor, svd, classifier):
    features = ['step', 'customer', 'age', 'gender', 'merchant', 'category', 'amount']
    transaction_df = pd.DataFrame([transaction], columns=features)
    transaction_processed = preprocessor.transform(transaction_df)
    transaction_svd = svd.transform(transaction_processed)
    prediction = classifier.predict(transaction_svd)
    return "Fraud Transaction" if prediction[0] == 1 else "Valid Transaction"

DATABASE_URL = "postgresql://postgres:inr_db@db.inr.intellx.in/zeus"
CONNECTION = psycopg2.connect(DATABASE_URL)

@app.route('/')
def main():
    return redirect(url_for("dashboard"))

@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")
    
@app.route('/dashboard/matrix', methods=['GET', 'POST'])
def dashboard_matrix():

    return render_template("crcf.html")

@app.route('/dashboard/SIEM/ongoing')
def dashboard_siem():

    cursor = CONNECTION.cursor()

    cursor.execute('SELECT * FROM events WHERE NOT RESOLVED;')

    headings = [desc[0] for desc in cursor.description]
    data_values = list(cursor.fetchall())

    data = [{heading: value for heading, value in zip(headings, data)} for data in data_values]

    return render_template("SIEM/ongoing.html", data = data)

@app.route('/dashboard/SIEM/all')
def dashboard_siem_all():

    cursor = CONNECTION.cursor()

    cursor.execute('SELECT * FROM events;')

    headings = [desc[0] for desc in cursor.description]
    data_values = list(cursor.fetchall())

    data = [{heading: value for heading, value in zip(headings, data)} for data in data_values]

    return render_template("SIEM/all.html", data=data)

@app.route('/dashboard/SIEM/event/<id>', methods=['GET', 'POST'])
def event_view(id):

    if request.method == "POST":

        cursor = CONNECTION.cursor()

        cursor.execute('''
                INSERT INTO event_comments (
                        id,
                        user_id,
                        comment
                    )
                VALUES (
                        %s,
                        1,
                        %s
                    )
            ''', (id, request.form.get("desc")))

        CONNECTION.commit()

        return redirect(url_for('event_view', id=id))

    cursor = CONNECTION.cursor()

    cursor.execute('SELECT * FROM events WHERE id=%s;', (id,))

    headings = [desc[0] for desc in cursor.description]
    data_values = list(cursor.fetchall())

    data = [{heading: value for heading, value in zip(headings, data)} for data in data_values]

    event = data[0]

    days_passed = ((event["timestamp"] - datetime.datetime.now()).days) + 1

    event["days"] = abs(days_passed)
    event["timestamp"] = event["timestamp"].strftime('%b %d, %Y %I:%M %p')

    cursor.execute('SELECT * FROM event_comments WHERE event_id=%s;', (id,))

    headings = [desc[0] for desc in cursor.description]
    data_values = list(cursor.fetchall())

    event["comments"] = [{heading: value for heading, value in zip(headings, data)} for data in data_values]

    return render_template("SIEM/event.html", event = event)

@app.route('/dashboard/SIEM/create', methods=['GET', 'POST'])
def dashboard_siem_create():
    if request.method == "POST":

            cursor = CONNECTION.cursor()

            cursor.execute('''
                INSERT INTO events (
                        event_type,
                        description,
                        source_device,
                        man_interv
                    )
                VALUES (
                        %s,
                        %s,
                        %s,
                        True
                    )
            ''', (request.form.get("type"), request.form.get("desc"), request.form.get("name")))

            CONNECTION.commit()

            return redirect(url_for('dashboard_siem'))

    return render_template("SIEM/create.html")

@app.route('/dashboard/resolve/<id>')
def dashboard_siem_resolve(id):

    cursor = CONNECTION.cursor()

    cursor.execute('UPDATE events SET resolved = true, resolution_timestamp = %s WHERE id=%s;', (datetime.datetime.now(),id,))

    CONNECTION.commit()

    return redirect(url_for("event_view", id=id))

@app.route('/dashboard/faces')
def dashboard_facedb():
    cursor = CONNECTION.cursor()

    cursor.execute('SELECT * FROM faces;')

    headings = [desc[0] for desc in cursor.description]
    data_values = list(cursor.fetchall())

    data = [{heading: value for heading, value in zip(headings, data)} for data in data_values]


    return render_template("faces.html", data=data)

app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit upload size to 16MB

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
@app.route('/validate/id', methods=['GET', 'POST'])
def validate_id():
    if request.method == 'POST':
        file = request.files.get('id_card')
        if file and file.filename:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            aadhar_ocr = Aadhar_OCR(file_path)
            details = aadhar_ocr.extract_data()
            if details:
                return render_template('validate_id.html', details=details, valid=True)
            else:
                return render_template('validate_id.html', valid=False)
        else:
            return redirect(request.url)
    return render_template('validate_id.html')

from cam import verify_image_with_model

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Flask route for image validation
@app.route('/validate/photo', methods=['GET', 'POST'])
def validate_photo():
    if request.method == 'POST':
        file = request.files.get('image_file')
        if file and file.filename:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            # Proceed to verify the image using your model
            verification_result = verify_image_with_model(file_path)
            # Render the verification result template with the result
            return render_template('upload_image_for_verification.html', verification_result=verification_result)
        else:
            return redirect(request.url)
    return render_template('upload_image_for_verification.html')

def load_models():
    # Load the saved models from disk
    rf_classifier = joblib.load('models/email_phish/rf_classifier.joblib')
    svm_classifier = joblib.load('models/email_phish/svm_classifier.joblib')
    return rf_classifier, svm_classifier

def predict_email(email_text, rf_classifier, svm_classifier):
    # Use the loaded models to predict the class of the email text
    pred_rf = rf_classifier.predict([email_text])[0]
    pred_svm = svm_classifier.predict([email_text])[0]
    return pred_rf, pred_svm

@app.route('/phish/mail', methods=['GET', 'POST'])
def phish_mail():
    if request.method == 'POST':
        try:
            email_text = request.form['emailText'].strip()
            if email_text == '':
                print(yamborghini)
            src = "txt"
        except:
            # try:
            email_text = email.message_from_binary_file(BytesIO(request.files['file'].read()))
            body = ""

            if email_text.is_multipart():
                for part in email_text.walk():
                    ctype = part.get_content_type()
                    cdispo = str(part.get('Content-Disposition'))

                    # skip any text/plain (txt) attachments
                    if ctype == 'text/plain' and 'attachment' not in cdispo:
                        body = part.get_payload(decode=True)  # decode
                        break
            # not multipart - i.e. plain text, no attachments, keeping fingers crossed
            else:
                body = email_text.get_payload(decode=True)
            email_text = body.decode()
            src = "file"
            # except Exception as e:
            #     return str(e)
            #     return redirect(url_for("phish_mail"))
        rf_classifier, svm_classifier = load_models()
        prediction_rf, prediction_svm = predict_email(email_text, rf_classifier, svm_classifier)
        return render_template('phish.html', prediction_rf=prediction_rf, prediction_svm=prediction_svm)
    return render_template('phish.html')

@app.route('/credit/fraud', methods=['GET', 'POST'])
def fraud():
    prediction = None
    if request.method == 'POST':
        transaction = {
            'step': int(request.form['step']),
            'customer': f"C{request.form['customer']}",
            'age': request.form['age'],
            'gender': request.form['gender'],
            'merchant': f"M{request.form['merchant']}",
            'category': request.form['category'],
            'amount': float(request.form['amount'])
        }
        # Load the saved components
        preprocessor = joblib.load('models/card_fraud/preprocessor.joblib')
        svd = joblib.load('models/card_fraud/svd_transformer.joblib')
        rf_classifier = joblib.load('models/card_fraud/rf_classifier.joblib')

        prediction = predict_single_transaction(transaction, preprocessor, svd, rf_classifier)
        print("\nPrediction for the transaction:", prediction)

    return render_template('trans_fraud.html', prediction=prediction)

@app.route('/real', methods=['GET', 'POST'])
def real():
    import cv2 as cv
    import torch
    from torchvision import transforms
    from Model import DeePixBiS

    model = DeePixBiS()
    model.load_state_dict(torch.load('./DeePixBiS.pth'))
    model.eval()

    tfms = transforms.Compose([
        transforms.ToPILImage(),
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    ])

    faceClassifier = cv.CascadeClassifier('Classifiers/haarface.xml')

    camera = cv.VideoCapture(0)

    result = []

    def generate_frames():
        while True:
            _, img = camera.read()
            grey = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
            faces = faceClassifier.detectMultiScale(grey, scaleFactor=1.1, minNeighbors=4)

            for x, y, w, h in faces:
                faceRegion = img[y:y + h, x:x + w]
                faceRegion = cv.cvtColor(faceRegion, cv.COLOR_BGR2RGB)

                faceRegion = tfms(faceRegion)
                faceRegion = faceRegion.unsqueeze(0)

                mask, binary = model.forward(faceRegion)
                res = torch.mean(mask).item()

                if res < 0.5:
                    cv.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    cv.putText(img, 'Fake', (x, y + h + 30), cv.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255))
                    
                else:
                    cv.rectangle(img, (x, y), (x + w, y + h), (0, 255,0), 2)
                    cv.putText(img, 'Real', (x, y + h + 30), cv.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0))

            _, frame = cv.imencode('.jpg', img)
            frame = frame.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/real_page', methods=['GET', 'POST'])
def real_page():
    return render_template('realtime.html')


if __name__ == '__main__':    
    app.run(debug=True)
