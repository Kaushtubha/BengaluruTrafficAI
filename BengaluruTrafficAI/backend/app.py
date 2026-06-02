from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({
        "status": "online",
        "junction": "Silk Board",
        "active_lane": "North"
    })

if __name__ == '__main__':
    app.run(port=5000, debug=True)