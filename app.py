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

def mergeFile(newFolder,user):
    folder_path = f"uploads/{newFolder}"
    combined_base64 = ''
    
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for file in sorted(filenames, key=lambda x: int(x.split("_")[0])):
            full_path = os.path.join(dirpath, file)
            print(full_path)
            try:
                with open(full_path, "r") as f:
                    data = json.load(f)
                    #print(data)
                    #print(f"{full_path}")
                    combined_base64 += data["base"]["image"]
            except FileNotFoundError:
                print(f"File not found: {full_path}")
   
    return creatImage(combined_base64, newFolder,user,folder_path)


def creatImage(base64_string, state,user,folder_path):
    #print( base64_string)  # Print first 50 chars for preview
    image_data = base64.b64decode(base64_string)
    path = f"uploads/{user}/{state}.jpg"
    
    with open(path, "wb") as f:
        f.write(image_data)
        #shutil.rmtree(folder_path)


    return 'hi'

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

@app.route('/upload', methods=['POST'])
def upload_image():
    data = request.get_json(silent=True) or {}
    print(data)
    user = request.args.get('user')
    id = request.args.get('id')
    chunkNo = request.args.get('chunkNo')
    index = request.args.get('index')

    print(chunkNo)

    data = {
        "base": data
    }

    newFolder = f"{user}_{id}"
    path = os.path.join(UPLOAD_FOLDER, newFolder)
    os.makedirs(path, exist_ok=True)

    userPath = os.path.join(UPLOAD_FOLDER, user)
    os.makedirs(userPath, exist_ok=True)
   
    # Save JSON file inside the folder
    filename = f"{index}_{user}_{id}_chunk{chunkNo}.json"
    #print(filename)
    filepath = os.path.join(path, filename)
  
    
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)
    if(chunkNo == 'last'):
       return mergeFile(newFolder,user)
    return 'hi'


    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
