from flask import Flask, request, jsonify, send_from_directory
import os
from Posting import post_to_unipile

app = Flask(__name__)

# Base directory for static files
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Serve static files for the root directory
@app.route('/')
def serve_index():
    return send_from_directory(ROOT_DIR, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    # Ensure the file exists before attempting to serve
    if os.path.isfile(os.path.join(ROOT_DIR, path)):
        return send_from_directory(ROOT_DIR, path)
    return jsonify({"error": "File Not Found", "path": path}), 404

# API Endpoint for LinkedIn Automation
@app.route('/api/post', methods=['POST'])
def handle_post():
    data = request.json
    if not data:
        return jsonify({"success": False, "message": "No data received"}), 400
    
    account_id = data.get('account_id')
    text = data.get('text')
    
    if not account_id or not text:
        return jsonify({"success": False, "message": "Missing account_id or text"}), 400
    
    print(f"Triggering automation for account: {account_id}")
    
    # Trigger the posting logic in Posting.py
    result = post_to_unipile(account_id, text)
    
    if result.get("success"):
        return jsonify({
            "success": True, 
            "message": "Post successfully scheduled via Unipile",
            "data": result.get("data")
        })
    else:
        return jsonify({
            "success": False, 
            "message": f"Automation failed: {result.get('message')}"
        }), 500

if __name__ == '__main__':
    print("--------------------------------------------------")
    print(f"LinkedIn AI Agent Backend Running from: {ROOT_DIR}")
    print("Accessible at http://localhost:8000")
    print("--------------------------------------------------")
    # Listen on 0.0.0.0 for broader accessibility
    app.run(debug=True, host='0.0.0.0', port=8000)
