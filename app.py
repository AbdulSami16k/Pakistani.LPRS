import base64
import cv2
import os
import numpy as np
import requests
import keyboard
from flask import Flask, jsonify, render_template, request

app = Flask(__name__, template_folder="C:/Users/Abdul Sami/PycharmProjects/pythonProject2/templates/")
save_path = "C:/Users/Abdul Sami/PycharmProjects/pythonProject2/templates/image/binary_image.jpg"
min_area = 5001
plate_cascade = cv2.CascadeClassifier("C:/Users/Abdul Sami/PycharmProjects/pythonProject2/templates/pak.xml")

# Set the API key and URL for OCR
api_key = '583946f98288957'
api_url = 'https://api.ocr.space/parse/image'

def detect_license_plate(frame):
    img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    numberplate = plate_cascade.detectMultiScale(img_gray, 1.1, 4)
    for (x, y, w, h) in numberplate:
        area = w * h
        if area > min_area:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cv2.putText(frame, "Number Plate ", (x, y - 5), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
            gray_roi = img_gray[y:y + h, x:x + w]
            binary_roi = cv2.adaptiveThreshold(gray_roi, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                               cv2.THRESH_BINARY_INV, 11, 2)
            return binary_roi, frame

    return None, frame


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/detect_license_plate', methods=['POST'])
def detect_license_plate_route():
    # Ensure that the 'image_data_url' key is present in the request JSON
    if 'image_data_url' not in request.json:
        return jsonify({'error': 'Invalid request'}), 400

    # Get the image data URL from the request
    image_data_url = request.json['image_data_url']

    # Decode the image data from base64
    _, encoded_image = image_data_url.split(',', 1)
    decoded_image = base64.b64decode(encoded_image)

    # Convert the image data to a numpy array
    nparr = np.frombuffer(decoded_image, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Perform license plate detection on the frame
    binary_image, detected_frame = detect_license_plate(frame)

    if binary_image is not None:
        # Encode the binary image and convert to base64
        _, buffer = cv2.imencode('.jpg', binary_image)
        binary_image_data = base64.b64encode(buffer).decode('utf-8')

        # Save the binary image to the specified path
        with open(save_path, 'wb') as file:
            file.write(buffer)
    else:
        binary_image_data = ''

    # Encode the detected frame and convert to base64
    _, buffer = cv2.imencode('.jpg', detected_frame)
    detected_frame_data = base64.b64encode(buffer).decode('utf-8')

    # Convert the binary image to text using OCR
    if keyboard.is_pressed('d'):
        images = os.listdir(os.path.dirname(save_path))
        images.sort(key=lambda x: os.path.getmtime(os.path.join(os.path.dirname(save_path), x)))
        if len(images) > 0:
            image_path = os.path.join(os.path.dirname(save_path), images[-1])
            with open(image_path, 'rb') as f:
                payload = {
                    'apikey': api_key,
                    'OCREngine': 3,
                    'language': 'eng',
                    'isOverlayRequired': False
                }
                response = requests.post(api_url, data=payload, files={'image': f})
                result = response.json()
                detected_text = result["ParsedResults"][0]["ParsedText"]
                print(detected_text)
        else:
            detected_text = ''
    else:
        detected_text = ''

    return jsonify({
        'detected_frame_data': detected_frame_data,
        'binary_image_data': binary_image_data,
        'detected_text': detected_text
    })


@app.route('/get_binary_image')
def get_binary_image():
    # Read the saved binary image
    filename = os.path.join(os.path.dirname(save_path), "binary_image.jpg")
    with open(filename, "rb") as f:
        image_data = f.read()

    # Convert the binary image to a base64-encoded string and return as JSON
    image_data_base64 = base64.b64encode(image_data).decode("utf-8")
    return jsonify({"image_data": image_data_base64})


if __name__ == '__main__':
    # Ensure that the directory to save the image exists
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    app.run(debug=True, port=5001)
