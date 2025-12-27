"""
Minimal Test Server - Use this if api.py keeps crashing

To test on Zeabur:
1. Update Zbfile to: default: python test_server.py
2. Git commit and push
3. If this works, the problem is in api.py
4. If this fails, the problem is Zeabur configuration

To test locally:
python test_server.py
"""

from flask import Flask, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def index():
    return jsonify({
        'status': 'ok',
        'message': 'Minimal test server is running!',
        'version': 'test-v1.0',
        'port': os.environ.get('PORT', '8080'),
        'env_check': {
            'REPLICATE_API_TOKEN': 'set' if os.getenv('REPLICATE_API_TOKEN') else 'missing',
            'MESHY_API_KEY': 'set' if os.getenv('MESHY_API_KEY') else 'missing'
        }
    })

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'healthy',
        'message': 'Test server is working perfectly'
    })

@app.route('/test')
def test():
    return jsonify({
        'test': 'passed',
        'message': 'All routes are responding correctly'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print("=" * 60)
    print(f"[TEST SERVER] Starting minimal test server")
    print(f"[PORT] {port}")
    print(f"[STATUS] If you see this, the server started successfully")
    print("=" * 60)
    app.run(host='0.0.0.0', port=port, debug=False)
