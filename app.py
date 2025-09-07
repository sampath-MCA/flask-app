from flask import Flask, request, jsonify

app = Flask(__name__)

# Home route
@app.route('/')
def home():
    return jsonify({"message": "Welcome to my Flask API!"})

if __name__ == '__main__':
     app.run(host='0.0.0.0', port=8000)

