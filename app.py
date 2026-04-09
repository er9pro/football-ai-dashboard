from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
import subprocess
import threading
from datetime import datetime

app = Flask(__name__, static_folder='.')
CORS(app)

DATA_DIR = 'data'

def generate_predictions_background():
    """Run predictor in background thread so Flask starts immediately"""
    try:
        print("Generating predictions in background...")
        result = subprocess.run(['python', 'predictor.py'],
                                capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print("Predictions generated successfully")
        else:
            print(f"Warning: predictor.py failed: {result.stderr}")
    except Exception as e:
        print(f"Warning: Could not run predictor.py: {e}")

# Start prediction generation in background (don't block Flask startup)
threading.Thread(target=generate_predictions_background, daemon=True).start()

@app.route('/')
def index():
    return send_from_directory('.', 'dashboard.html')

@app.route('/api/predictions')
def get_predictions():
    try:
        pred_file = os.path.join(DATA_DIR, 'predictions.json')
        if os.path.exists(pred_file):
            with open(pred_file, 'r') as f:
                predictions = json.load(f)
            return jsonify({
                'success': True,
                'data': predictions,
                'updated': datetime.fromtimestamp(os.path.getmtime(pred_file)).isoformat(),
                'count': len(predictions)
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No predictions available. Generating now...'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
