from flask import Flask, jsonify, request
from ultralytics import YOLO
import math
import base64
from datetime import datetime
import os
import uuid
# Initialize Flask app
app = Flask(__name__)

# Load YOLOv8 pose model
model = YOLO("yolov8n-pose.pt")
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
def distance(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

def detect_head(image_path):
    results = model(image_path)
    for r in results:
        if r.boxes is None or r.keypoints is None or r.keypoints.xy is None:
            continue
        for box, kp in zip(r.boxes, r.keypoints.xy):
            cls_id = int(box.cls[0])
            label = r.names[cls_id]
            if label != "person":
                continue

            # Head keypoints: nose (0), left eye (1), right eye (2), left ear (3), right ear (4)
            head_points = [kp[i] for i in range(5)]
            visible = [p for p in head_points if p[0] > 0 and p[1] > 0]

            # Require at least 2 visible head keypoints
            if len(visible) >= 2:
                return True
    return False

# GET API → Detect from static image
@app.route("/detect", methods=["GET"])
def detect():
    image_path = "human.jpg"   # Static image path
    detected = detect_head(image_path)
    return jsonify({
        "image": image_path,
        "head_detected": detected
    })

@app.route("/upload", methods=["POST"])
def upload_image():
    print('hi')
    return jsonify({
           "mage": 's',
           "head_detected": 'ss'
           })


    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
