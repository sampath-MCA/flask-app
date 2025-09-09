from flask import Flask, jsonify
from ultralytics import YOLO
import math

# Initialize Flask app
app = Flask(__name__)

# Load YOLOv8 pose model
model = YOLO("yolov8n-pose.pt")

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

@app.route("/upload", methods=["GET"])
def image_uplaod():
     return jsonify({
        "image": request,
        "head_detected": 'ss'
    }) 
    # image_data = request.data  # Get Base64 string from POST
    # if not image_data:
    #     return "No image data received", 400

    # try:
    #     # Decode and save image
    #     with open("upload.jpg", "wb") as f:
    #         f.write(base64.b64decode(image_data))
    #     return "Image received", 200
    # except Exception as e:
    #     return f"Error: {str(e)}", 500
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
