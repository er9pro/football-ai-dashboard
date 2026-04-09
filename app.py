from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__, static_folder='.')
CORS(app)

DATA_DIR = 'data'

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
                'error': 'No predictions available. Run predictor.py first.'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/fixtures')
def get_fixtures():
    try:
        fix_file = os.path.join(DATA_DIR, 'fixtures.json')
        if os.path.exists(fix_file):
            with open(fix_file, 'r') as f:
                fixtures = json.load(f)
            return jsonify({
                'success': True,
                'data': fixtures,
                'count': len(fixtures)
            })
        else:
            return jsonify({'success': False, 'error': 'No fixtures found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stats')
def get_stats():
    try:
        stats = {}
        for fname in ['xg_stats.json', 'odds.json', 'injuries.json']:
            fpath = os.path.join(DATA_DIR, fname)
            if os.path.exists(fpath):
                with open(fpath, 'r') as f:
                    stats[fname.replace('.json', '')] = json.load(f)
        return jsonify({'success': True, 'data': stats})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    print('Starting Football AI Dashboard...')
    print('Open http://localhost:5000 in your browser')
    app.run(debug=True, host='0.0.0.0', port=5000)
